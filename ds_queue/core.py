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
        orig_ip = req.getHeader("X-Real-IP")

        if len(orig_ip) > 0:
            orig_ip = orig_ip[0]

        if proxystate.allowed_ips and orig_ip not in proxystate.allowed_ips:
            print("rejecting ip : " + str(orig_ip))
            return

        self.handleQpRequest(req)

    def handleQpRequest(self, req):

        queryParams = req.getQueryParams()

        if 'getQueuedRequest' in queryParams:
            self.getQueuedRequest()
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
        reqUu = str(uuid.uuid4())
        proxystate.log.debug("queueing request with id %s" % (reqUu))
        self.setQueuedRequest(req, reqUu)
        proxystate.log.debug("getting repsonse of queued request with id %s" % (reqUu))
        self.getQueuedResponse(reqUu)

    def setQueuedRequest(self, req, reqUu):

        try:
            req.addHeader('reqId', reqUu)
            proxystate.reqQueue.put(req)
            proxystate.resQueueList[reqUu] = queue.Queue()
        except queue.Full as e:
            proxystate.log.debug(e.__str__())
            return

    def getQueuedRequest(self):

        try:
            req = proxystate.reqQueue.get(timeout=proxystate.requestTimeout)
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

    def setQueuedResponse(self, req):

        try:
            reqId = req.getQueryParams()['reqId'][0]
            res = req.getBody()
            proxystate.resQueueList[reqId].put(res)
        except queue.Full as e:
            proxystate.log.debug(e.__str__())
            return

        res = HTTPResponse('HTTP/1.1', 200, 'OK')
        self.sendResponse(res.serialize())

    def getQueuedResponse(self, reqId):

        try:
            res = proxystate.resQueueList[reqId].get(timeout=proxystate.responseTimeout)
            del proxystate.resQueueList[reqId]
        except Exception:
            res = HTTPResponse('HTTP/1.1', 503, 'Queue timed out - poll server did not respond in seconds ' + str(proxystate.responseTimeout)).serialize()
            self.sendResponse(res)

        proxystate.log.debug("sending response with id %s back to client" % (reqId))
        self.sendResponse(res)

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
        self.reqQueue = queue.Queue()
        self.resQueueList = {}
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
