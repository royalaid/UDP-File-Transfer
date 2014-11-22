import sys
import socket
import logging

# clear logging TODO
logging.basicConfig(format='%(message)s',
                    filename='log.log',
                    level=logging.DEBUG)
logging.debug('+++++++++++++++++++++++++++++++++++++++++++')

SIZE = 1024  #max packet size as defined by spec
running = True


