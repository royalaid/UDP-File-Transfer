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

while running:
    ##########
    # user input
    ##########
    timeout = raw_input("\nPlease specify a timeout duration in seconds.")
    try:
        timeout = float(timeout)
    except:
        print "\nIncorrect Format."

    port = raw_input("\nPlease specify a port number.")
    try:
        port = int(port)
        if port < 1024:
           raise Exception("Check your previllage")
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
    s.bind(('0.0.0.0', 10753))
    reqData, addr = s.recvfrom(SIZE)

    nameFile = processRequest()  #defined in ServerTools.py TODO
    pathFile = locateFile(nameFile)


