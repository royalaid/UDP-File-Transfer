import sys
import socket
import logging
import time
import json
import hashlib
# clear logging TODO
logging.basicConfig(format='%(message)s',
                    filename='log.log',
                    level=logging.DEBUG)
logging.debug('+++++++++++++++++++++++++++++++++++++++++++')

SIZE = 1024  # max packet size as defined by spec
elementSize = 1  # size of element in bytes TODO ?user determined?
running = False  # TODO testing, change back
fileIncomplete = True
seqPointer = -1  # no packets set yet TODO should be next valid to use
seqNum = 0
MAXSEQNUM = 65535
# key = seq
# value = (data,ackBool)
window = {}


def constructPacket(opcode, curSeq, data=""):
    """TODO: Docstring for constructPacket.

    :opcode: OpCodes are as follows, Request = 0, Data = 1, Ack = 2,
    Retransmit packet = 3, Timeout-Error = 4
    :data: The data to be transmitted
    :returns: A json string representing the packet to be sent
    """
    if opcode != 1:
        packetData = ""
    else:
        packetData = data

    curSeq += 1
    if curSeq > MAXSEQNUM:
        curSeq = 0
    # Remeber to make any changes to both the hashPacket and return val encodes
    hashPacket = json.dumps([opcode, packetData, curSeq], separators=(',', ':'))
    # For info about this see here http://bit.ly/1vA3gms
    hashSig = hashlib.sha1(hashPacket.encode("UTF-8")).hexdigest()
    return json.dumps([opcode, packetData, curSeq, hashSig],
                      separators=(',', ':'))


def removeAndSlideElements(w, s, f, sp, es, ms):
    """ remove appropriate elements from window
        and set ack-ed element
        appropriate = consecutive lowest seq
        also slides window by adding bytes from file
    """
    wkeys = w.keys()
    delCount = 0

    if dangerzone(w):
        properSort(wkeys, s)
    else:
        wkeys = wkeys.sort()
        s = s.sort()

    setAcks(w, wkeys, s)

    # removing elements
    if wkeys[0] == s[0]:  # we can remove elements
        for i in range(1, len(s)):
            if s[i] - s[i-1] == 1 and i != 0:  # contigous from first get del
                del w[wkeys[i-1]]
                delCount += 1
        del w[wkeys[0]]
        delCount += 1

    # sliding window
    for i in range(0, delCount):
        chunk = f.read(es)
        w[sp] = (chunk, False)
        sp = (sp + 1) % ms


def setAcks(w, wkeys, s):
    """Sets all ackbools of window elements to true for
    sequence numbers that we have gotten acks for
    """

    for x in s:
        if x in wkeys:
            w[x][1] = True


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
    w = window.keys().sort()
    if w[0] - w[len(w)-1] > len(w):
        return True
    else:
        return False


def listenForAcks(s):
    """ listens on socket s for packets
    processes those acks
    stores acknowledged seq numbers and returns
    """
    seqNums = []
    start_time = time.time()
    while (time.time() - start_time) < timeout:  # wait timeout sec
        packet = s.recvfrom(SIZE)
        processAck(packet, seqNums)  # append seq nums to list seqNums
    return seqNums


def processAck(packet, seqNums):
    """Verify checksum
    pull out sequence num
    append seq num to seqNums
    """


def processRequest(data):
    """Handles request packet, verify checksum, get desired file info from
    file in working directory
    """
    # TODO
    pass


def locateFile(fileName):
    """
    """


def function(arg1):
    """TODO: Docstring for function.

    :arg1: TODO
    :returns: TODO

    """
    pass
while running:
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
            raise Exception("Check your previllage (and your port)")
    except:
        print "\nIncorrect Format, please use an integer above '1024'"

    windowLength = raw_input("\nPlease specify a window length.")
    try:
        windowLength = int(windowLength)
        if windowLength > 10 or windowLength < 5:
            raise Exception("Wrong Window Size")
    except:
        print "\nIncorrect Format, please use an integer between 5-10 inclusive"

    ##############################
    # Listen for initial request #
    ##############################
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('0.0.0.0', port))
    reqData, cAddr = s.recvfrom(SIZE)

    nameFile = processRequest(reqData)  # defined in ServerTools.py TODO
    pathFile = locateFile(nameFile)

    # create file object
    # fill window
    f = (pathFile, 'r')
    for x in range(0, windowLength):
        chunk = f.read(elementSize)
        window[x] = (chunk, False)
        seqPointer = x

    while fileIncomplete:

        # shoot out entire window if not ack-ed
        for x in window.keys():
            if not window[x][2]:
                packet = constructPacket(window[x], x)
                s.sendto(packet, (cAddr, port))
                # update sequence pointer? TODO

        seqNums = listenForAcks(s)

        removeAndSlideElements(window, seqNums, f, seqPointer,
                               elementSize, MAXSEQNUM)
        # NOTE changed w to Window

        # TODO check if file complete
