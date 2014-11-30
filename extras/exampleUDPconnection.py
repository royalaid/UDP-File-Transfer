#########################
# Set up Socket & Listen
#########################
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 10753))
while 1:
    data, addr = s.recvfrom(SIZE)
    print repr(data)
    (ipSeg, destIP,  ttl, srcIP, ttlExpired) = IPunpackET(data, add1[1])
    print "ttl: " + str(ttl) + "\nsrcIP: " + repr(srcIP)
    # Repack data with new ttl and src ip
    newIPData = IPrepackET(ipSeg, ttl, srcIP)
    # Unpack UDP segment
    newUDPData = data[20:]
    # Repack UDP segment
    destIP = destIP.split('.')
    try:
        route1 = ft[tuple(destIP[:2])]
    except:
        route1 = None
    try:
        route2 = ft[tuple(destIP[:3])]
    except:
        route2 = None
    # Look for destination in routing table
    if (ttlExpired):
        newIPData = IPrepackET(ipSeg, 64, srcIP,
                               socket.inet_aton(addr[0]), 0x01)
        print addr[0]
        print repr(addr[0])
        s.sendto(bytes(newIPData + ICMPPacket(data).packed),
                 (addr[0], 10753))

    elif (route2):
        print 'route2' + route2
        s.sendto(bytes(newIPData + newUDPData), (route2, 10753))
    elif (route1):
        print 'route1' + route1
        s.sendto(bytes(newIPData + newUDPData), (route1, 10753))
    else:
        newIPData = IPrepackET(ipSeg, 64, srcIP,
                               socket.inet_aton(addr[0]), 0x01)
        print addr[0]
        print repr(addr[0])
        s.sendto(newIPData + ICMPPacket(data).packed, (addr[0], 10753))
