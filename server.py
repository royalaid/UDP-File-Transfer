import sys
import socket
import logging
import time

# clear logging TODO
logging.basicConfig(format='%(message)s',
                    filename='log.log',
                    level=logging.DEBUG)
logging.debug('+++++++++++++++++++++++++++++++++++++++++++')

SIZE = 1024  #max packet size as defined by spec
elementSize = 1  # size of element in bytes
running = True
fileIncomplete = True
seqPointer = -1  #no packets set yet
# key = seq
# value = (data,ackBool)
window = {}

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
        windowlength = int(windowlength)
        if windowlength > 10 or windowlength < 5:
            raise Exception("Wrong Window Size")
    except:
        print "\nIncorrect Format, please use an integer between 5 - 10 inclusive"

    ############
    #Listen for initial request
    ############
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('0.0.0.0', port))
    reqData, cAddr = s.recvfrom(SIZE)

    nameFile = processRequest(reqData)  #defined in ServerTools.py TODO
    pathFile = locateFile(nameFile)

    # create file object
    # fill window
    f = (pathFile,'r')
    for x in range (0,windowLength):
        chunk = f.read(elementSize)
        window[x] = (chunk,False)
        seqPointer = x

    while fileIncomplete:

        for x in window.keys():
            if not window[x][2]:
                packet = constructPacket(window[x],x)
                s.sendto(packet,(cAddr,port))


        seqNums = listenForAcks(s)

        # check if the file is incomplete

        # add new elements
        # mark appropriate remaining ack elements


def removeElements(w, seqNums):
    """ remove appropriate elements from window
             appropriate = consecutive lowest seq
    """
    dangerzone = False
    actualLowest = []
    keys = w.keys()
    keys.sort()
    seqNums.sort()

    for x in range(1,len(keys)):
        if (keys[x] - keys[x-1]) > windowLength:
            dangerzone = True

        if dangerzone:
            actualLowest.append(keys[x])

    if dangerzone:
        actualLowestACKed = list(set(seqNums).intersection(actualLowest))
        restACK = list(set(seqNums).difference(actualLowest))
        orderedSeqACK = actualLowestToRemove.sort() + rest.sort()

        restKeys = list(set(keys).difference(actualLowest))
        realOrderedKeys = actualLowest.sort() + restKeys.sort()

        # set all ack seq nums to ack=True in window
        for x in orderedSeqACK:
            w[x][1] = True

        if (orderedSeqACK[0] == realOrderedKeys[0]):
            # we can remove some
            for x in range(1,len(orderedSeqACK)):
                if orderedSeqACK[x] - orderedSeqACK[x-1] == 1:
                    del w[x-1]  # TODO also fudged
                    """
                    only slide when the 'lowest' value seq num is acked
                    and if that value is acked then check for consecutive
                    lowest acks
                    remove all

                    then add to window from file
                    """

    else:
        # not in danger zone
        for x in seqNums:
            w[x][1] = True  # set ack to true for all ack seq nums

        if seqNums[0] == keys[0]:
            #time to slide
            for x in range(1,len(seqNums)):
                if seqNums[x] - seqNums[x-1] == 1:
                    del w[x-1]  # TODO this is fudged

def listenForAcks(s):
    """ listens on socket s for packets
    processes those acks
    stores acknowledged seq numbers and returns
    """
    seqNums = []
    start_time = time.time()
    while (time.time() - start_time) < timeout:  # wait timeout sec
        packet = s.recvfrom(SIZE)
        processAck(packet,seqNums)  # append seq nums to list seqNums
    return seqNums

def processAck(packet,seqNums):
    """Verify checksum
    pull out sequence num
    append seq num to seqNums
    """

def processRequest(data):
    """Handles request packet, verify checksum, get desired file info from
    file in working directory
    """
    #TODO
    pass

def locateFile(fileName):
    """
    """




