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
 -q <full-url-of-server>  full address of queue (default = 8)
 -o <full-url-of-server>  full address of opal server
 -l <loglevel number> 
 -t <number>       number of threads to create for polling
 -c                if option given sets the ssl context to accept custom certificate authorities under 
""" % sys.argv[0])

def parse_options():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:d:hp:r:l:q:o:sct:")
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

    if 'q' in opts:
        ps.queue_addr = opts['q']

    if 'o' in opts:
        ps.opal_addr = opts['o']

    ps.own_ca = True if 'c' in opts else False

    ps.n_threads = 2
    if 't' in opts:
        ps.n_threads = opts['t']

    return ps


def pollworker_req_handler(threadName, pollstate, req):

    pollworker = Pollworker(pollstate, threadName)
    pollworker.handleRequest(req)


def pollworker_exec(threadName, pollstate):

    pollworker = Pollworker(pollstate, threadName)

    disconnected = True
    sleep_time = 10

    while(True):
        req = pollworker.getNextRequest()

        if req is None:
            disconnected = True
            pollstate.log.info(f'Could not connect to queue with address: {pollstate.queue_addr}' +
                               f' - sleep for {str(sleep_time)} seconds and try again')

            sleep_time = sleep_time * 2

            if sleep_time > 600:
                sleep_time = 600

            time.sleep(sleep_time)

            continue

        if disconnected:
            disconnected = False
            sleep_time = 10
            pollstate.log.info(f'Reconnected to queue with address: {pollstate.queue_addr}' +
                               f' - start processing requests')

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
