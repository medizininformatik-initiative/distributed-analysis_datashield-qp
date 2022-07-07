#!/usr/bin/env python

"""
  Copyright notice
  ================

  Copyright (C) 2018
      Julian Gruendner     <juliangruendner@googlemail.com>

"""
import logging
import sys
import getopt
import ds_http
from core import ProxyState, ProxyServer
import json


def show_help():
    print("""\
Syntax: python %s <options>
 -a <addr>         listen address (default 0.0.0.0)
 -h                show this help screen
 -p <port>         listen port  (default 8080)
 -r <host:[port]>  redirect HTTP traffic to target host (default port: 80)
 -l                set the log level
 -i                activate queue-poll
 -s                activate https
 -t <requestTimeout:responseTimeout> set request and response timeout note "None" is for no timeout
 -c  <ip,ip,ip>              set restriction to certain client ip ("," seperated ip addresses) - note for poll to work poll server needs to be one of them
""" % sys.argv[0])

def parse_options():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:d:hp:r:l:x:ist:c:")
    except getopt.GetoptError as e:
        print(str(e))
        show_help()
        exit(1)

    opts = dict([(k.lstrip('-'), v) for (k, v) in opts])

    if 'h' in opts:
        show_help()
        exit(0)

    ps = ProxyState()

    if 'l' in opts:
        ps.log.set_level(int(opts['l']))

    if 'p' in opts:
        ps.listenport = int(opts['p'])

    if 'a' in opts:
        ps.listenaddr = opts['a']

    # Check and parse redirection host
    if 'r' in opts:
        h = opts['r']
        if ':' not in h:
            p = 80
        else:
            h, p = h.split(':')
            p = int(p)
        ps.redirect = (h, p)

    if 't' in opts:
        timeouts = opts['t']
        req_t, res_t = timeouts.split(':')

        if req_t != "None":
            ps.requestTimeout = int(req_t)

        if res_t != "None":
            ps.responseTimeout = int(res_t)

    if 'i' in opts:
        ps.activateQp = True
    else:
        ps.activateQp = False

    if 'c' in opts:
        ps.allowed_ips = opts['c'].split(",")

    ps.https = True if 's' in opts else False

    return ps

def main():
    global proxystate
    proxystate = parse_options()
    proxyServer = ProxyServer(proxystate)
    proxyServer.startProxyServer()


if __name__ == "__main__":
    global proxystate
    try:
        main()
    except KeyboardInterrupt as e:
        proxystate.log.info("Terminating queue ...")
