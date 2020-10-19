#! /usr/bin/env python3

import sys, os
sys.path.append("../lib")       # for params
import re, socket, params
from os.path import exists

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

from framedSock import framedSend, framedReceive

while True:

    sock, addr = lsock.accept()
    print("connection rec'd from", addr)

    if not os.fork():
        while True:

            #get file name for transferFile
            fileName = framedReceive(sock, debug)


            #convert transferFile name to string
            fileName = fileName.decode()

            #check if file exists and send response
            if exists(fileName):
                framedSend(sock, b"True", debug)
            #continue if file doesn't exist
            else:
                framedSend(sock, b"False", debug)

                try:
                    #recieve file
                    fileContents = framedReceive(sock, debug)
                except:
                    print("error while receiving!")
                    sys.exit(0)

                #if not fileContents:
                #    break

                try:
                    #send response
                    framedSend(sock, fileContents, debug)
                except:
                    print('error while sending!')

                #write new filename
                newFile = open(fileName, 'wb')
                #write contents to file
                newFile.write(fileContents)
                #close file
                newFile.close()

sock.close()
