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
    try:
        fileName = sys.argv[1]
    except Exception:
        fileName = raw_input("Please specify a file: \n").rstrip()
    return fileName


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
        filename += 'New'
    mode = 'wb'

    s.sendto(reqPacket, ('148.61.112.111', 1236))

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
curSeq = 0
ackPacketsDict = {}
totalByteRecv = 0
with open(filename, mode) as f:
    while loop:  # not sure about connected TODO
        # configure sender ip
        # configure sequence number

        (data, addr) = s.recvfrom(1024)
        #print repr(data)
        # configure checksum
        recvPacket = json.loads(data)
        if checkHash(recvPacket):
            ackPacketsDict[recvPacket[2]] = base64.decodestring(recvPacket[1])
            if(recvPacket[2] == curSeq):
                #print repr(ackPacketsDict[curSeq])
                totalByteRecv += len(ackPacketsDict[curSeq])
                print "The Bytes So far: " + str(totalByteRecv)
                print "curSeq is " + str(curSeq)
                f.write(ackPacketsDict[curSeq])
                curSeq += 1
            s.sendto(constructPacket(2, data=recvPacket[2]), addr)
            print constructPacket(2, data=recvPacket[2])
    # To check the hash take the received packet, decode the json, reencode the
    # json based on what is done in the server (extract to tools file?) and then
    # hash the new j;son string and check against the parsed hash/truncated hash

    # determine if sending

    # at some point for with :

    # pid = os.fork()

    # if not pid :  #child???

    # else: # parent???
