"""
  Copyright notice
  ================

  Copyright (C) 2018
      Julian Gruendner   <juliangruendner@googlemail.com>
      License: GNU, see LICENSE for more details.

"""

import io
import http.client
from ds_http.ds_http import HTTPRequest, HTTPResponse
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)

CA_PATH = '/etc/ssl/certs'

class Pollworker():

    def __init__(self, pollstate, threadName):
        self.pollstate = pollstate
        self.threadName = threadName

    def _getresponse_with_body_as_string(self, res):

        body = res.raw.read()  # add body decoding to convert to bytes
        body = body.decode('latin-1')
        proto = "HTTP/1.1"

        code = res.status_code
        msg = 'OK'
        headers = res.headers

        dict_headers = {}

        for header in headers.keys():
            dict_headers[header] = headers[header]

        if 'Transfer-Encoding' in dict_headers.keys():
            del dict_headers['Transfer-Encoding']
            dict_headers['Content-Length'] = str(len(body))

        parceled_res = HTTPResponse(proto, code, msg, dict_headers, body)

        return parceled_res

    def getNextRequest(self):

        try:
            url = f'{self.pollstate.queue_addr}?getQueuedRequest=True'
            res = requests.get(url)

        except requests.exceptions.ConnectionError as e:
            print(e)
            self.pollstate.log.debug(f'Queue at address: {self.pollstate.queue_addr} not available')
            return None

        return res

    def handleRequest(self, res):

        if res.status_code == 204:
            return

        if res.status_code != 200:
            self.pollstate.log.debug("Connected to queue, but error getting next request, check if your queue and nginx are running correctly," +
                                     " response from queue: %s %s \n" % (str(res.code), res.msg))
            return

        res_buf = io.BytesIO(res.content)
        req = HTTPRequest.build(res_buf)

        self.pollstate.log.log_message_as_json(req)

        reqId = req.getHeader('reqId')[0]
        req.removeHeader('reqId')

        try:
            self.pollstate.log.debug(f'sending request to opal with id {reqId}')

            opal_url = f'{self.pollstate.opal_addr}{req.getPath()}'
            headers = {}
            for header in req.headers.keys():
                headers[header] = req.headers[header][0]

            res = requests.request(req.getMethod(), opal_url, data=req.getBody(), headers=headers, stream=True)

        except Exception as e:
            self.pollstate.log.info(f'Error connecting to Opal with address: {self.pollstate.opal_addr}')
            url = f'{self.pollstate.opal_addr}?setQueuedResponse=True&reqId={reqId}'
            res = HTTPResponse("HTTP/1.1", "502", "Opal not accessbile", body="")
            payload = res.serialize()
            requests.post(url, data=payload)
            return

        parceled_res = self._getresponse_with_body_as_string(res)
        self.pollstate.log.log_message_as_json(parceled_res)
        payload = parceled_res.serialize()

        self.pollstate.log.debug(f'sending response from opal to queue with id {reqId}')
        url = f'{self.pollstate.queue_addr}?setQueuedResponse=True&reqId={reqId}'
        requests.post(url, data=payload)
