"""
  Copyright notice
  ================
  
  Copyright (C) 2018
      Julian Gruendner   <juliangruendner@googlemail.com>
      License: GNU, see LICENSE for more details.
  
"""

from ds_poll_logger import PollLogger

class PollState:
    def __init__(self):
        # Internal state
        self.log = PollLogger()
