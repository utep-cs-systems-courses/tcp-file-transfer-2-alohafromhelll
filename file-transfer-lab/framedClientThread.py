#! /usr/bin/env python3
#Jerardo Velazquez

# Echo client program
import socket, sys, re, os

from os.path import exists

sys.path.append("../lib")       # for params
import params

from encapFramedSock import EncapFramedSock


switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

addrFamily = socket.AF_INET
socktype = socket.SOCK_STREAM
addrPort = (serverHost, serverPort)

s = socket.socket(addrFamily, socktype)

if s is None:
    print('could not open socket')
    sys.exit(1)

s.connect(addrPort)

fsock = EncapFramedSock((s, addrPort))

#Ask for file to transfer
transferFile = input('Enter file to transfer : ')

#check if file exists
if exists(transferFile):

    #get file object in binary - rb
    getFile = open(transferFile, 'rb') #open file

    #read entire file
    fileContents = getFile.read()

    #check for zero length files
    if len(fileContents) == 0:
        print('error zero length file')
        sys.exit(0)
    else:

        #splitting the file name by the period and adding enumeration to the end
        splitFileName = transferFile.split('.')
        copiedFileEnumeration = '_copy.'
        fileNameForCopy = splitFileName[0] + copiedFileEnumeration + splitFileName[1]
        fileNameForCopy = fileNameForCopy.strip()

        #send file name to server to check if already on server
        fsock.send(fileNameForCopy.encode(), debug)

        #response from server
        fileAlreadyOnServer = fsock.receive(debug)

        #decode response
        fileAlreadyOnServer = fileAlreadyOnServer.decode()

        #if file is already on server exit
        if fileAlreadyOnServer == 'True':
            print('File is already on server!')
            sys.exit(0)
        #file is not on server, continue
        else:
            try:
                #send file
                fsock.send(fileContents, debug)
            except:
                print('error while sending')
                sys.exit(0)
            try:
                #get response
                fsock.receive(debug)
            except:
                print('error whie receiving!')
                sys.exit(0)

else:
    print('no such file.')
    sys.exit(0)
