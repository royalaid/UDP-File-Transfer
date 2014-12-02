import sys
import os
import logging
import socket
import base64
import json
import hashlib
from ServerTools import constructPacket
from ServerTools import checkHash
# clear logging TODO
logging.basicConfig(format='%(message)s',
                    filename='log.log',
                    level=logging.DEBUG)
logging.debug('+++++++++++++++++++++++++++++++++++++++++++')

# Constants
BYTES = 4
loop = True
fileLength = 0
def getUserInput():
    filename = raw_input("Please specify a file: \n").rstrip()
    return filename


##########
# Open File and read first BYTES
##########
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 1235))
while True:
    filename = getUserInput()
    reqPacket = constructPacket(0, data=filename)
    # Makes new filename so we don't mess up the transferring file
    if os.path.isfile(filename):
        filename += '_new'
    f = open(filename, "wb")
    s.sendto(reqPacket, ('', 1234))

    (data, addr) = s.recvfrom(1024)
    recvPacket = json.loads(data)
    if checkHash(recvPacket):
        print "Size of the file(bytes): " + str(recvPacket[1])
        fileLength = recvPacket[1]
        if fileLength == 0:
            print "File doesn't exist."
        else:
            print "File found!"
            break

# start connection

while loop:  # not sure about connected TODO
    # configure sender ip
    # configure sequence number

    (data, addr) = s.recvfrom(1024)
    print repr(data)
    # configure checksum
    recvPacket = json.loads(data)
    print recvPacket
    # To check the hash take the received packet, decode the json, reencode the
    # json based on what is done in the server (extract to tools file?) and then
    # hash the new j;son string and check against the parsed hash/truncated hash

    # determine if sending


# at some point for with :

# pid = os.fork()

# if not pid :  #child???

# else: # parent???
