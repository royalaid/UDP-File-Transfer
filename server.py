import sys
import socket
import logging
import time
import json
import hashlib
import os
from ServerTools import constructPacket
from ServerTools import checkHash
# clear logging TODO
logging.basicConfig(format='%(message)s',
                    filename='log.log',
                    level=logging.DEBUG)
logging.debug('+++++++++++++++++++++++++++++++++++++++++++')

SIZE = 1024  # max packet size as defined by spec
elementSize = 687  # size of element in bytes TODO ?user determined?
running = True  # TODO testing, change back
MAXSEQNUM = 99999
fileSize = 0
# key = seq
# value = (data,ackBool)


def removeAndSlideElements(w, confirmedAcks, f, sp, es, ms):
    """ remove appropriate elements from window
    and set ack-ed element
    appropriate = consecutive lowest seq
    also slides window by adding bytes from file
    w: Window (Dictionary), confirmedAcks: confirmed Sequence Numbers (list),
    f: File, sp: sequence pointer, es: element size, ms: max sequence number
    """
    wkeys = w.keys()
    delCount = 0

    if dangerzone(w):
        properSort(wkeys, confirmedAcks) #TODO make proper sort return
    else:
        wkeys.sort()
        confirmedAcks.sort()

    lowestWindowKey = wkeys[0]
    lowerBoundWindow = lowestWindowKey
    removedElms = 0
    #print "Wkeys before setAcks:"
    #print str(wkeys)
    #print "seqNumArr before setAcks:"
    #print str(confirmedAcks) + '\n'
    w = setAcks(w, wkeys, confirmedAcks)
    #print "Wkeys after setAcks:"
    #print str(wkeys)
    #print "seqNumArr after setAcks:"
    #print str(confirmedAcks) + '\n'
    # removing elements
    for x in confirmedAcks:
        packetConfirmed = w[x][1]
        if packetConfirmed:
            #print "Current X: " + str(x)
            if x == (lowestWindowKey):
                # We have removed the bottom, time to shift our lower window
                del w[x]
                wkeys.remove(x)
                print "Removed " + str(x) + " from w and wkeys"
                print wkeys
                removedElms += 1
                #print "RemovedElms = " + str(removedElms)
                if(len(wkeys) > 0):
                    lowestWindowKey = wkeys[0]
                    lowerBoundWindow = lowestWindowKey
                    if wkeys[0] > MAXSEQNUM:
                        pass
                        #TODO deal with this corner case
                else:
                    lowerBoundWindow = (lowestWindowKey + 1) % MAXSEQNUM
        else:
            break

    ackNeededElm = lowerBoundWindow
    topOfWindow = ackNeededElm + removedElms
    # sliding window
    for i in range(0, removedElms):
        sp = (sp + 1) % ms #TODO handle wrap around
        posOfNeededChunk = es * sp
        if(posOfNeededChunk >= fileSize):
           print "Read through end of file"
           return (w, sp)
        f.seek(posOfNeededChunk)
        chunk = f.read(es)
        w[sp] = (chunk, False)
        print "Adding chuck " + str(sp)
        #print "Len of window: " + str(len(w))
    #raw_input("Continue?")
    return (w, sp)


def setAcks(w, wkeys, seqNumArr):
    """Sets all ackbools of window elements to true for
    sequence numbers that we have gotten acks for
    """

    for x in seqNumArr:
        if x in wkeys:
            w[x] = (w[x][0], True)
    return w


def properSort(wkeys, s):
    """Sorts two arguments properly
    when the window is mid wrap around valid seq numbers the
    higher value numbers are actually the lower logical sequence numbers
    ProperSort orders them according to that principle
    """

    s = s.sort()
    wkeys = wkeys.sort()
    actslow = []
    actwklow = []
    restWK = []
    restS = []

    for i in range(1, len(s)):
        if s[i] - s[i-1] > len(wkeys):
            actslow = s[i:]
            restS = s[:i]
            break

    for i in range(1, len(wkeys)):
        if wkeys[i] - wkeys[i-1] > len(wkeys):
            actwklow = wkeys[i:]
            restWK = wkeys[:i]
            break

    wkeys = actwklow + restWK
    s = actslow + restS


def dangerzone(window):
    w = window.keys()
    w.sort()
    if w[0] - w[len(w)-1] > len(w):
        return True
    else:
        return False


def listenForAcks(s, keysToConfirm):
    """ listens on socket s for packets
    processes those acks
    stores acknowledged seq numbers and returns
    """

    confirmedAcks = []
    start_time = time.time()
    #print "Start Time: " + str(start_time)
    s.settimeout(None)
    while (time.time() - start_time) < timeout:  # wait timeout sec
        try:
            #print "About to recv"
            packet, caddr = s.recvfrom(SIZE)
            packet = json.loads(packet)
            print "Ack for " + str(packet[1])
            if(checkHash(packet)):
                confirmedAcks.append(packet[1])
            keysToConfirm.remove(packet[1])
            if(len(keysToConfirm) == 0):
                break
        except Exception, e:
            pass
            #print "SocketTimeout?"
            #print e
    return confirmedAcks


def processRequest(data):
    """Handles request packet, verify checksum, get desired file info from
    file in working directory

    [opcode, data, seq, hash]
    """
    reqData = json.loads(data)
    reqData[1] = reqData[1].encode("UTF-8")
    hashCheck = reqData[2]
    jsonPacket = json.dumps(reqData[:2], separators=(',', ':'))
    hashGen = hashlib.sha1(jsonPacket.encode("UTF-8")).hexdigest()
    if hashCheck != hashGen:
        pass
        #print "Hash error"
    else:
        try:
            return reqData[1]
        except:
            return None


'''
##########
# user input
##########
timeout = raw_input("\nPlease specify a timeout duration in seconds.")
try:
    timeout = float(timeout)
except:
    print "\nIncorrect Format for timeout."

port = raw_input("\nPlease specify a port number.")
try:
    port = int(port)
    if port < 1024:
        raise Exception("Check your privilege (and your port)")
except:
    print "\nIncorrect Format, please use an integer above '1024'"

windowLength = raw_input("\nPlease specify a window length.")
try:
    windowLength = int(windowLength)
    if windowLength > 10 or windowLength < 5:
        raise Exception("Wrong Window Size")
except:
    print "\nIncorrect Format, please use an integer between 5-10 inclusive"

'''
print "server running..."
port = 1236
timeout = 1
windowLength = 4
##############################
# Listen for initial request #
##############################
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', port))
while True:
    fileIncomplete = True
    seqPointer = 0  # no packets set yet TODO should be next valid to use
    seqNum = 0
    window = {}
    reqData, cAddr = s.recvfrom(SIZE)
    #print "request recieved"
    #print "client ip: " + str(cAddr)
    ##############################
    # Locate file and get size   #
    ##############################
    f = processRequest(reqData)  # defined in ServerTools.py
    if os.path.exists(f):  # check if the file exists
        #print "File requested " + str(f)
        fileSize = os.path.getsize(f)
        print "Size of files(bytes): " + str(fileSize)

        with open(f, 'rb') as f:
            sizePacket = constructPacket(0, data=fileSize)
            s.sendto(sizePacket, cAddr)
            #print "sent packet size"
            # TODO Loop until file is valid
            # fill window
            for x in range(0, windowLength):
                chunk = f.read(elementSize)
                window[x] = (chunk, False)
                seqPointer = x
                if (elementSize * (x + 1)) > fileSize:
                    break

            while fileIncomplete:

                # Check for completion of file transfer

                # shoot out entire window if not ack-ed
                for x in window.keys():
                    if not window[x][1]:
                        packet, seqNum = constructPacket(1, x, window[x][0])
                        print "Sent " + str(x * elementSize) + " bytes"
                        print "seqNum " + str(seqNum)
                        s.sendto(packet, cAddr)
                #print "Listening for Acks"
                ackedSeqNums = listenForAcks(s, window.keys())
                window, seqPointer = removeAndSlideElements(window, ackedSeqNums,
                                                           f, seqPointer,
                                                           elementSize,
                                                           MAXSEQNUM)
                if (seqPointer * elementSize) >= fileSize:
                    for x in window.keys():
                        if not window[x][1]:
                            packet, seqNum = constructPacket(1, x, window[x][0])
                            print "Sent " + str(x * elementSize) + " bytes"
                            print "seqNum " + str(seqNum)
                            s.sendto(packet, cAddr)
                    if len(window) > 0:
                        ackedSeqNums = listenForAcks(s, window.keys())
                    print "File Transfer Complete"
                    break

    else:
        sizePacket = constructPacket(0, data=0)
        s.sendto(sizePacket, cAddr)
        #print "invalid file name"
