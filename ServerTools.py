import json
import base64
import hashlib

MAXSEQNUM = 99999
# When base64 encoded this is the max size we can fit into the packet
MAXPACKLEN = 687


def base64Len(num):
        if (num % 3) > 0:
                num = num + (3 - (num % 3))
        else:
                num += 0
        num /= 3
        num *= 4
        num += ((num) / 72)
        return num


def checkHash(packet):
    #print "Checking Hash"
    # if checking an ack or request packet, only need to hash packet[0:2]
    i = 2
    # if checking a data packet, we'll need to hash packet[0:3]
    if len(packet) == 4:
        i = 3

    hashCheck = packet[i]  # pull received hash number

    jsonPacket = json.dumps(packet[:i], separators=(',', ':'))
    hashGen = hashlib.sha1(jsonPacket.encode("UTF-8")).hexdigest()  # new hash
    if (hashGen == hashCheck):  # compare received and actual
        #print "Hash confirmed"
        return True
    else:
        #print "Hash invalid, packet corrupt"
        return False


def constructPacket(opcode, curSeq=0, data=""):
    """Creates a packet in the form of a JSON string that holds either data or a
    command to be issued. The packet construct also increments
    :opcode: OpCodes are as follows, Request = 0, Data = 1, Ack = 2,
    :curSeq: The last sequence number used for the last packet sent
    :data: The data to be transmitted
    :returns: A tuple with (json string that is the packet, last used seqNum)
    """

    if curSeq > MAXSEQNUM:
        curSeq = 0

    def requestPacket(fileName):
        rawPacket = [opcode, fileName]
        jsonPacket = json.dumps(rawPacket, separators=(',', ':'))
        rawPacket.append(hashlib.sha1(jsonPacket.encode("UTF-8")).hexdigest())
        # For info about this see here http://bit.ly/1vA3gms
        packet = json.dumps(rawPacket, separators=(',', ':'))
        return packet

    def dataPacket(packetData):
        # Remeber to make any changes to both the hashPacket
        # and return val encodeso
        if len(packetData) > MAXPACKLEN:
            return None  # TODO Finish
        packetData = base64.encodestring(packetData)
        rawPacket = [opcode, packetData, curSeq]
        jsonPacket = json.dumps(rawPacket, separators=(',', ':'))
        rawPacket.append(hashlib.sha1(jsonPacket.encode("UTF-8")).hexdigest())
        # For info about this see here http://bit.ly/1vA3gms
        packet = json.dumps(rawPacket, separators=(',', ':'))
        return (packet, curSeq)

    def ackPacket(curSeq):
        return requestPacket(curSeq)

    opcodeDict = {0: requestPacket, 1: dataPacket, 2: ackPacket}
    return opcodeDict[opcode](data)
