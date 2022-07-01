#!/usr/bin/env python

"""
  Copyright notice
  ================
  
  Copyright (C) 2018
      Julian Gruendner   <juliangruendner@googlemail.com>
      License: GNU, see LICENSE for more details.
  
"""
import os
import sys
import getopt
import http.client
import threading
import sys
from ds_poll_util import PollState
from ds_pollworker import Pollworker
import time
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

global pollstate

def show_help():
    print("""\
Syntax: python %s <options>
 -h                show this help screen
 -p                protocol
 -q <host:[port]>  full address of queue (default = 8)
 -o <host:[port]>  full address of opal server
 -l <loglevel number> 
 -t <number>       number of threads to create for polling
 -s                set ssl context to verify server side
 -c                if option given sets the ssl context to accept custom certificate authorities under
 -k                api key to access queue
""" % sys.argv[0])

def parse_options():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:d:hp:r:l:q:o:sct:k:")
    except getopt.GetoptError as e:
        print(str(e))
        show_help()
        exit(1)

    opts = dict([(k.lstrip('-'), v) for (k, v) in opts])

    if 'h' in opts:
        show_help()
        exit(0)

    ps = PollState()

    if 'l' in opts:
        ps.log.set_level(int(opts['l']))

    if 'k' in opts:
        ps.api_key = opts['k']

    # Check and parse queue host
    if 'q' in opts:
        h = opts['q']
        if ':' not in h:
            p = 8001
        else:
            h, p = h.split(':')
            p = int(p)
        ps.q_addr = (h, p)

    # Check and parse redirection host
    if 'o' in opts:
        h = opts['o']
        if ':' not in h:
            p = 8880
        else:
            h, p = h.split(':')
            p = int(p)
        ps.opal_addr = (h, p)

    ps.https = True if 's' in opts else False

    ps.own_ca = True if 'c' in opts else False

    ps.n_threads = 2
    if 't' in opts:
        ps.n_threads = opts['t']

    return ps


def pollworker_req_handler(threadName, pollstate, req):
    q_host, q_port = pollstate.q_addr
    o_host, o_port = pollstate.opal_addr

    pollworker = Pollworker(q_host, q_port, o_host, o_port, pollstate, threadName)
    pollworker.handleRequest(req)


def pollworker_exec(threadName, pollstate):

    q_host, q_port = pollstate.q_addr
    o_host, o_port = pollstate.opal_addr

    pollworker = Pollworker(q_host, q_port, o_host, o_port, pollstate, threadName)

    disconnected = True
    sleep_time = 10

    while(True):
        req = pollworker.getNextRequest()

        if req is None:
            disconnected = True
            pollstate.log.info("Could not connect to queue with address " + str(pollstate.q_addr[0]) + ":" + str(pollstate.q_addr[1]) + 
                               " - sleep for " + str(sleep_time) + " seconds and try again")

            sleep_time = sleep_time * 2

            if sleep_time > 600:
                sleep_time = 600

            time.sleep(sleep_time)

            continue

        if disconnected:
            disconnected = False
            sleep_time = 10
            pollstate.log.info("Reconnected to queue with address " + str(pollstate.q_addr[0]) + ":" + str(pollstate.q_addr[1]) + 
                               " - start processing requests")

        try:
            t = threading.Thread(target=pollworker_req_handler, daemon=True, args=("Thread-", pollstate, req))
            t.start()
        except Exception as e:
            pollstate.log.error(e.__str__() + ": Error on starting response handler")


def main():

    pollstate = parse_options()
    threads = []

    if pollstate.own_ca:
        pollstate.log.info("own ca set -> adding certificates in /etc/ssl/certs/ and ca-certificates.crt")
        os.environ['REQUESTS_CA_BUNDLE'] = os.path.join('/etc/ssl/certs/',
                                                        'ca-certificates.crt')

    try:
        for i in range(0, int(pollstate.n_threads)):
            t = threading.Thread(target=pollworker_exec, daemon=True, args=("Thread-" + str(i), pollstate))
            threads.append(t)
            t.start()
    except Exception as e:
        pollstate.log.error(e.__str__() + ": Error on starting poll threads")
    while threading.active_count() > 1:
        time.sleep(10)
        pass


if __name__ == "__main__":
    pollstate = PollState()
    try:
        main()
    except KeyboardInterrupt:
        pollstate.log.info("Terminating due to keyboard interrupt")
