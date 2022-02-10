"""
  Copyright notice
  ================
  
  Copyright (C) 2018
      Julian Gruendner   <juliangruendner@googlemail.com>
      License: GNU, see LICENSE for more details.
  
"""

from ds_poll_logger import PollLogger

class PollState:
    def __init__(self, queue_addr="http://localhost:8001", opal_addr="http://localhost:8880"):
        # Configuration options, set to default values
        self.queue_addr = queue_addr
        self.opal_addr = opal_addr

        # Internal state
        self.log = PollLogger()
