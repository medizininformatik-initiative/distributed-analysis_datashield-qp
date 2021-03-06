"""
  Copyright notice
  ================
  
  Copyright (C) 2018
      Julian Gruendner   <juliangruendner@googlemail.com>
      License: GNU, see LICENSE for more details.
  
"""

"""
  Copyright notice
  ================
  
  Copyright (C) 2011
      Roberto Paleari     <roberto.paleari@gmail.com>
      Alessandro Reina    <alessandro.reina@gmail.com>
  
  This program is free software: you can redistribute it and/or modify it under
  the terms of the GNU General Public License as published by the Free Software
  Foundation, either version 3 of the License, or (at your option) any later
  version.
  
  HyperDbg is distributed in the hope that it will be useful, but WITHOUT ANY
  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License along with
  this program. If not, see <http://www.gnu.org/licenses/>.
  
"""

import datetime
import copy
import urllib.parse
import select
import base64

class HTTPUtil():
    @staticmethod
    def wait_read(socket):
        select.select([socket], [], [])

class HTTPMessage():
    EOL = "\r\n"
    HTTP_CODE_OK = 200

    # Global message ID, incremented at each HTTP request/reponse
    uid = 0

    def __init__(self, headers = None):
        self.peer = None
        self.time = datetime.datetime.now()
        # Set unique message ID
        self.uid  = HTTPMessage.uid

        if headers is None:
            self.headers = {}
        elif isinstance(headers, list):
            self.headers = HTTPMessage._readheaders(headers)
        else:
            assert isinstance(headers, dict)
            self.headers = headers

        HTTPMessage.uid += 1

    @staticmethod
    def _readheaders(data):
        headers = {}
        
        for line in data:
            line = line.decode("latin-1")

            if line == HTTPMessage.EOL:
                break
            
            assert ":" in line
            line = line.rstrip(HTTPMessage.EOL)
            i = line.index(":")
            n = line[:i]
            v = line[i+1:]
            v = v.lstrip()
            v = v.strip("[']")
            
            if n not in headers:
                headers[n] = []
                headers[n].append(v)

        return headers

    @staticmethod
    def _readbody(data, headers):
        bodylen = None
        chunked = False
        for n,v in headers.items():
            if n.lower() == "content-length":
                assert bodylen is None, "[!] Duplicated content length"
                bodylen = int(v[0])
            elif n.lower() == "transfer-encoding" and v[0].lower() == "chunked":
                chunked = True
                break

        # Read HTTP body (if present)
        body = ""
        if bodylen is not None:
            body = data.read(bodylen)
            body = body.decode('latin-1')
        elif chunked:
            # Chunked encoding
            while True:
                # Determine chunk length
                chunklen = data.readline()
                chunklen = int(chunklen, 16)

                # Read the whole chunk
                chunk = ""
                chunk = data.read(chunklen)
                body += chunk

                if chunklen == 0: 
                    break

                # Read trailing CRLF
                eol = data.read(2)
                assert eol == HTTPMessage.EOL

        return body

    def isChunked(self):
        r = False
        for n, v in self.headers.items():
            if n.lower() == "transfer-encoding" and v[0].lower() == "chunked":
                r = True
                break
        return r

    def isKeepAlive(self):
        if 'Connection' in self.headers:
            if self.headers['Connection'][0] == 'keep-alive':
                return True
        elif 'Proxy-Connection' in self.headers:
            if self.headers['Proxy-Connection'][0] == 'keep-alive':
                return True
            
        return False
            
    def setPeer(self, h, link = True):
        self.peer = h
        if link:
            h.setPeer(self, link = False)

    def clone(self):
        return copy.deepcopy(self)

    def fixup(self):
        # Fix headers
        for n in self.headers:
            if n.lower() == "content-length":
                self.headers[n][0] = len(self.body)

    # Hack to fix HTTPS request 
    @staticmethod
    def _fixURLMalformed(scheme, url, headers):
        if ((url.find('http') != 0) and (url[0] == '/')):
            assert 'Host' in headers
            url = scheme + '://' + headers['Host'][0] + url
        return url

    def __findHeader(self, name, ignorecase = True):
        r = None
        for n in self.headers:
            if (ignorecase and name.lower() == n.lower()) or ((not ignorecase) and name == n):
                r = n
                break
        return r

    def getHeader(self, name, ignorecase = True):
        """
        Get the values of header(s) with name 'name'. If 'ignorecase' is True,
        then the case of the header name is ignored.
        """
        r = []
        for n,v in self.headers.items():
            if (ignorecase and name.lower() == n.lower()) or ((not ignorecase) and name == n):
                r.extend(v)
        return r

    def addHeader(self, name, value, ignorecase = True):
        """
        Add a new 'name' header with value 'value' to this HTTPMessage. If
        'ignorecase' is True, then the case of the header name is ignored.
        """
        k = self.__findHeader(name, ignorecase)
        if k not in self.headers:
            self.headers[name] = value
        #self.headers[name].append(value)

    def setHeader(self, name, value, ignorecase = True):
        """
        Set header with name 'name' to 'value'. Any existing header with the
        same name is replaced. If 'ignorecase' is True, then the case of the
        header name is ignored.
        """
        k = self.__findHeader(name, ignorecase)
        self.headers[k] = [value, ]

    def removeHeader(self, name, ignorecase = True):
        """
        Set header with name 'name' to 'value'. Any existing header with the
        same name is replaced. If 'ignorecase' is True, then the case of the
        header name is ignored.
        """
        k = self.__findHeader(name, ignorecase)
        del self.headers[k]


class HTTPRequest(HTTPMessage):
    METHOD_GET     = 'GET'
    METHOD_POST    = 'POST'
    METHOD_PUT     = 'PUT'
    METHOD_DELETE  = 'DELETE'
    METHOD_HEAD    = 'HEAD'
    METHOD_OPTIONS = 'OPTIONS'
    METHOD_CONNECT = 'CONNECT'

    def __init__(self, method, url, proto, headers = None, body = ""):
        self.method  = method
        self.url     = url
        self.proto   = proto
        self.body    = body
        HTTPMessage.__init__(self, headers)

    @staticmethod
    def build(data):
        # Read request line
        # TODO - check if decoding good idea or wheather conversion without decoding is possible
        reqline = data.readline().decode("latin-1").rstrip(HTTPMessage.EOL)

        if reqline == '': 
            return None

        method, url, proto = reqline.split()

        # Read headers & body
        headers = HTTPMessage._readheaders(data)
        body    = HTTPMessage._readbody(data, headers)
        url = HTTPMessage._fixURLMalformed("https", url, headers)
        return HTTPRequest(method, url, proto, headers, body)

    def getHost(self):
        if self.getMethod() == HTTPRequest.METHOD_CONNECT:
            tmp = self.url.split(":")
            host = tmp[0]
            if len(tmp) > 0:
                port = int(tmp[1])
            else:
                port = 80
        else:
            r = urllib.parse.urlparse(self.url)
            port = r.port
            if port is None:
                if r.scheme != "https":
                    port = 80
                else:
                    port = 443
                
            host = r.hostname

        assert host is not None and len(host) > 0, "[!] Cannot find target host in URL '%s'" % self.url
        return host, port

    def getPath(self):
        r = urllib.parse.urlparse(self.url)
        s = r.path
        if len(r.params) > 0:
            s += ";%s" % r.params
        if len(r.query) > 0:
            s += "?%s" % r.query
        if len(r.fragment) > 0:
            s += "#%s" % r.fragment
        return s

    def getQueryParams(self):
        queryString = urllib.parse.urlparse(self.url).query
        return urllib.parse.parse_qs(queryString)


    def __str__(self):
        s = "{REQ #%d} method: %s ; host: %s ; path: %s ; proto: %s ; len(body): %d\n" % \
            (self.uid, self.method, self.getHost(), self.getPath(), self.proto, len(self.body))
        for n,v in self.headers.items():
            s += "  %s: %s\n" % (n, v)

        return s

    def isRequest(self):
        return True

    def isResponse(self):
        return False

    def getMethod(self):
        m = self.method.lower()
        if   m == "get":     r = HTTPRequest.METHOD_GET
        elif m == "post":    r = HTTPRequest.METHOD_POST
        elif m == "put":     r = HTTPRequest.METHOD_PUT
        elif m == "delete":  r = HTTPRequest.METHOD_DELETE
        elif m == "head":    r = HTTPRequest.METHOD_HEAD
        elif m == "options": r = HTTPRequest.METHOD_OPTIONS
        elif m == "connect": r = HTTPRequest.METHOD_CONNECT
        elif m == "unknown": r = HTTPRequest.METHOD_UNKNOWN
        return r

    def getBody(self):
        return self.body
    
    def getRequestLine(self):
        s = "%s %s %s" % (self.method, self.url, self.proto)
        s += HTTPMessage.EOL

        return s

    def serialize(self):
        # Request line
        s = "%s %s %s" % (self.method, self.url, self.proto)
        s += HTTPMessage.EOL

        # Headers
        for n,v in self.headers.items():
            s += "%s: %s" % (n, v)
            s += HTTPMessage.EOL
		
        s += HTTPMessage.EOL

        # Body
        if not self.isChunked():
            s += self.body
        else:
            # FIXME: Make a single-chunk body
            s += "%x" % len(self.body) + HTTPMessage.EOL
            s += self.body + HTTPMessage.EOL
            s += HTTPMessage.EOL
            s += "0" + HTTPMessage.EOL + HTTPMessage.EOL

        return s

class HTTPResponse(HTTPMessage):
    def __init__(self, proto, code, msg, headers = None, body = ""):
        self.proto   = proto
        self.code    = code
        self.msg     = msg
        self.body    = body
        HTTPMessage.__init__(self, headers)

    @staticmethod
    def build(data):
        # Read request line
        reqline = data.readline().rstrip(HTTPMessage.EOL)

        method, url, proto = reqline.split()

        # Read headers & body
        headers = HTTPMessage._readheaders(data)
        body    = HTTPMessage._readbody(data, headers)

        return HTTPRequest(method, url, proto, headers, body)

    def serialize(self):
        # Response line
        s = "%s %s %s" % (self.proto, self.code, self.msg)
        s += HTTPMessage.EOL

        # Headers

        for n,v in self.headers.items():
            #for i in v:
            s += "%s: %s" % (n, v)
            s += HTTPMessage.EOL

        s += HTTPMessage.EOL


        # Body
        if not self.isChunked():
            s += self.body
        else:
            # FIXME: Make a single-chunk body
            s += "%x" % len(self.body) + HTTPMessage.EOL
            s += self.body + HTTPMessage.EOL
            s += HTTPMessage.EOL
            s += "0" + HTTPMessage.EOL + HTTPMessage.EOL

        return s

    def __str__(self):
        s = "{RES #%d} code: %d (%s) ; proto: %s ; len(body): %d\n" % \
            (self.uid, self.code, self.msg, self.proto, len(self.body))
        for n,v in self.headers.items():
            s += "  %s: %s\n" % (n, v)
        
        return s

    def isResponse(self):
        return True
