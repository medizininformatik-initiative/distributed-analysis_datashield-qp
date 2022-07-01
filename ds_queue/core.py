"""
  Copyright notice
  ================

  Copyright (C) 2018
      Julian Gruendner     <juliangruendner@googlemail.com>
"""

import queue
import socketserver
import threading
import time
import ssl
import uuid
import os
import json
from ds_http.ds_http import HTTPRequest, HTTPResponse
from logger import Logger
from urllib.parse import urlparse, urlunparse

KEY_FILE = "./cert/queuekey.pem"
CERT_FILE = "./cert/queuecert.pem"
CACERT = "./cert/queuecacert.pem"

proxystate = None

class ProxyHandler(socketserver.StreamRequestHandler):
    def __init__(self, request, client_address, server):

        self.peer = True
        self.target = None

        # Just for debugging
        self._host = None
        self._port = 0

        socketserver.StreamRequestHandler.__init__(self, request, client_address, server)

    def handle(self):

        global proxystate

        try:
            req = HTTPRequest.build(self.rfile)
        except Exception as e:
            proxystate.log.debug(e.__str__() + ": Error on reading request message")
            return

        if req is None:
            return

        proxystate.log.debug(req.serialize())

        req = req.clone()
        self.req = req.clone()
        orig_ip = req.getHeader("X-Real-IP")

        proxystate.log.debug(str(proxystate.api_keys))

        if len(orig_ip) > 0:
            orig_ip = orig_ip[0]

        if proxystate.allowed_ips and orig_ip not in proxystate.allowed_ips:
            print("rejecting ip : " + str(orig_ip))
            return

        self.handleQpRequest(req)

    def extract_site_from_path(self, req):
        req_url = urlparse(req.url)
        path_arr = req_url.path.split("/")
        index = path_arr.index("qprequest") + 1
        site = path_arr[index]
        return site

    def remove_qp_site_from_path(self, req):
        req_url = urlparse(req.url)
        path_arr = req_url.path.split("/")
        index = path_arr.index("qprequest") + 2
        fixed_path = path_arr[index:]
        fixed_path_s = "/".join(map(str, fixed_path))
        fixed_url = urlunparse(req_url._replace(path=fixed_path_s))
        req.url = str(fixed_url)
        return req

    def handleQpRequest(self, req):

        queryParams = req.getQueryParams()

        if 'getQueuedRequest' in queryParams:
            self.getQueuedRequest(req)
        elif 'setQueuedResponse' in queryParams:
            self.setQueuedResponse(req)
        elif 'resetQueue' in queryParams:
            self.resetQueue()
        elif 'ping' in queryParams:
            self.ping()
        elif 'queueSizes' in queryParams:
            self.get_q_sizes()
        else:
            self.execQueueRequest(req)

    def execQueueRequest(self, req):
        site = self.extract_site_from_path(req)
        req = self.remove_qp_site_from_path(req)

        reqUu = str(uuid.uuid4())
        proxystate.log.debug(f'queueing request with id {reqUu} for site {site}')
        self.setQueuedRequest(req, reqUu, site)
        proxystate.log.debug(f'getting repsonse of queued request with id {reqUu} for site {site}')
        self.getQueuedResponse(reqUu, site)

    def setQueuedRequest(self, req, reqUu, site):

        try:
            req.addHeader('reqId', reqUu)
            proxystate.reqQueueList[site].put(req)
            proxystate.resQueueList[site][reqUu] = queue.Queue()
        except queue.Full as e:
            proxystate.log.debug(e.__str__())
            return

    def get_token_auth_header(self, req):
        """Obtains the Access Token from the Authorization Header
        """

        auth = req.getHeader("Authorization")

        if not auth:
            raise Exception({"code": "authorization_header_missing",
                            "description":
                                "Authorization header is expected"}, 401)

        parts = auth[0].split()

        if parts[0].lower() != "bearer":
            raise Exception({"code": "invalid_header",
                            "description":
                                "Authorization header must start with"
                                " Bearer"}, 401)
        elif len(parts) == 1:
            raise Exception({"code": "invalid_header",
                            "description": "Token not found"}, 401)
        elif len(parts) > 2:
            raise Exception({"code": "invalid_header",
                            "description":
                                "Authorization header must be"
                                " Bearer token"}, 401)
        return parts[1]

    def get_site_from_api_key(self, req):
        api_key = self.get_token_auth_header(req)

        if api_key not in proxystate.api_keys:
            proxystate.log.debug("api key is not valid")
            return None

        return proxystate.api_keys[api_key]

    def api_access(func):
        def wrap(*args, **kwargs):
            instance = args[0]
            if instance.get_site_from_api_key(instance.req) is None:
                res = HTTPResponse('HTTP/1.1', 401, 'FORBIDDEN')
                instance.sendResponse(res.serialize())
                return
            func(*args, **kwargs)
        return wrap

    @api_access
    def getQueuedRequest(self, req):

        site = self.get_site_from_api_key(req)

        try:
            req = proxystate.reqQueueList[site].get(timeout=proxystate.requestTimeout)
        except queue.Full as e:
            proxystate.log.debug(e.__str__())
            return
        except queue.Empty:
            res = HTTPResponse('HTTP/1.1', 204, 'NO CONTENT')
            self.sendResponse(res.serialize())
            return

        res = HTTPResponse('HTTP/1.1', 200, 'OK')
        res.body = req.serialize()

        self.sendResponse(res.serialize())

    @api_access
    def setQueuedResponse(self, req):

        site = self.get_site_from_api_key(req)

        try:
            reqId = req.getQueryParams()['reqId'][0]
            res = req.getBody()
            proxystate.resQueueList[site][reqId].put(res)
        except queue.Full as e:
            proxystate.log.debug(e.__str__())
            return

        res = HTTPResponse('HTTP/1.1', 200, 'OK')
        self.sendResponse(res.serialize())

    def getQueuedResponse(self, reqId, site):

        try:
            res = proxystate.resQueueList[site][reqId].get(timeout=proxystate.responseTimeout)
            del proxystate.resQueueList[site][reqId]
        except Exception:
            res = HTTPResponse('HTTP/1.1', 503, 'Queue timed out - poll server did not respond in seconds ' + str(proxystate.responseTimeout)).serialize()
            self.sendResponse(res)

        proxystate.log.debug("sending response with id %s back to client" % (reqId))
        self.sendResponse(res)

    @api_access
    def resetQueue(self):
        proxystate.resQueueList = {}
        proxystate.reqQueue.queue.clear()

        res = HTTPResponse('HTTP/1.1', 200, 'OK', body="queue reset \n")
        self.sendResponse(res.serialize())

    def ping(self):
        proxystate.log.info("Being pinged")
        res = HTTPResponse('HTTP/1.1', 200, 'OK', body="queue is still alive \n")
        self.sendResponse(res.serialize())

    def get_q_sizes(self):

        queue_sizes = {"request_q_size": proxystate.reqQueue.qsize(), "response_q_size": list(proxystate.resQueueList.keys())}

        res = HTTPResponse('HTTP/1.1', 200, 'OK', body=json.dumps(queue_sizes))
        self.sendResponse(res.serialize())

    def sendResponse(self, res):
        self.wfile.write(res.encode('latin-1'))
        self.wfile.flush()  # see if flushing improves performance


class ThreadedHTTPProxyServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

class ProxyServer():
    def __init__(self, init_state):
        global proxystate
        proxystate = init_state
        self.proxyServer_port = proxystate.listenport
        self.proxyServer_host = proxystate.listenaddr

    def startProxyServer(self):
        global proxystate

        self.proxyServer = ThreadedHTTPProxyServer((self.proxyServer_host, self.proxyServer_port), ProxyHandler)

        proxystate.log.info("Starting Queue...")

        if proxystate.https:

            proxystate.log.info("Starting Queue with HTTPS wrapper...")

            if os.path.isfile(CACERT):
                self.proxyServer.socket = ssl.wrap_socket(self.proxyServer.socket, keyfile=KEY_FILE, certfile=CERT_FILE, ca_certs=CACERT, server_side=True)
            else:
                self.proxyServer.socket = ssl.wrap_socket(self.proxyServer.socket, keyfile=KEY_FILE, certfile=CERT_FILE, server_side=True)

        server_thread = threading.Thread(target=self.proxyServer.serve_forever)

        server_thread.setDaemon(True)
        proxystate.log.info("Starting queue server, with configurations:" + 
                            " port: %d, loglevel: %s, req_timeout: %s, res_timeout: %s, allowed_ips: %s, "
                            % (self.proxyServer_port, proxystate.log.get_level(), proxystate.requestTimeout,
                               proxystate.responseTimeout, proxystate.allowed_ips))

        server_thread.start()

        while True:
            time.sleep(0.1)

    def stopProxyServer(self):
        self.proxyServer.shutdown()


class ProxyState:
    def __init__(self, port=8001, addr="0.0.0.0"):
        self.listenport = port
        self.listenaddr = addr

        # Internal state
        self.log = Logger()
        self.redirect = None

        # TODO - create queue per site

        self.reqQueueList = {"erlangen": queue.Queue()}
        self.resQueueList = {"erlangen": {}}
        self.responseTimeout = None
        self.requestTimeout = None
        self.allowed_ips = None

    @staticmethod
    def getTargetHost(req):
        global proxystate
        # Determine the target host (check if redirection is in place)
        if proxystate.redirect is None:
            target = req.getHost()
        else:
            target = proxystate.redirect

        return target
