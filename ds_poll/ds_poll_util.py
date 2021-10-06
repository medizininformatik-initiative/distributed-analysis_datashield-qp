"""
  Copyright notice
  ================
  
  Copyright (C) 2018
      Julian Gruendner   <juliangruendner@googlemail.com>
      License: GNU, see LICENSE for more details.
  
"""

from ds_poll_logger import PollLogger

class PollState:
    def __init__(self, q_addr=('localhost', 8001), opal_addr=('localhost', 8880)):
        # Configuration options, set to default values
        self.q_addr = q_addr
        self.opal_addr = opal_addr

        # Internal state
        self.log = PollLogger()
