def genChecksum(largeChecksum):
    checksum = 0
    logging.debug("largeChecksum inital: " + str(largeChecksum) + ' hex(' +
                  str(hex(largeChecksum)) + ')')
    count = 0
    while True:
        highChecksum = largeChecksum >> 16
        logging.debug("highChecksum = " + str(highChecksum) + ' hex(' +
                      hex(highChecksum) + ')')
        lowChecksum = largeChecksum % 0x10000
        logging.debug("lowChecksum = " + str(lowChecksum) + ' hex(' +
                      hex(lowChecksum) + ')')
        checksum = lowChecksum + highChecksum
        largeChecksum = checksum
        logging.debug("New largeChecksum: " + str(largeChecksum) + ' hex(' +
                      str(hex(largeChecksum)) + ')')
        count += 1
        if largeChecksum <= 0xffff or count > 10:
            break

    logging.debug("checksum: " + str(checksum) + ' hex(' +
                  str(hex(checksum)) + ')')
    checksum = ~checksum
    logging.debug("inverted checksum: " + str(checksum) + ' hex(' +
                  str(hex(checksum)) + ')')

    logging.debug("returned checksum: " + str(int(hex(checksum & 2**16-1), 16))
                  + ' hex(' + str(hex(checksum & 2**16-1)) + ')')
    return int(hex(checksum & 2**16-1), 16)


