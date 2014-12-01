import sys
import os
import logging

# clear logging TODO
logging.basicConfig(format='%(message)s',
                    filename='log.log',
                    level=logging.DEBUG)
logging.debug('+++++++++++++++++++++++++++++++++++++++++++')

#### Constants
BYTES = 4
loop = True

def getUserInput():
    filename = raw_input("Please specify a file: \n")
    return filename


##########
# Open File and read first BYTES
##########

f = open(getUserInput(),"r")

# start connection

while loop and connected:  #not sure about connected TODO
    # configure sender ip
    # configure sequence number

    curFileSeg = f.read(BYTES)

    # configure checksum

    # To check the hash take the received packet, decode the json, reencode the
    # json based on what is done in the server (extract to tools file?) and then
    # hash the new json string and check against the parsed hash/truncated hash

    # determine if sending


# at some point for with :

# pid = os.fork()

# if not pid :  #child???

# else: # parent???
