#Jerardo Velazquez
#! /usr/bin/env python3

import sys, os
sys.path.append("../lib")       # for params
import re, socket, params
from os.path import exists
from threading import Thread, enumerate, Lock
from time import time, sleep

global dictionary
global dictLock
dictLock = Lock()
dictionary = dict()

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

from threading import Thread;
from encapFramedSock import EncapFramedSock


class Server(Thread):

    def __init__(self, sockAddr):
        Thread.__init__(self)
        self.sock, self.addr = sockAddr
        self.fsock = EncapFramedSock(sockAddr)
    def run(self):

        global dictionary, dictLock

        print("new thread handling connection from", self.addr)

        #get file name for transferFile
        fileName = self.fsock.receive(debug)

        #if debug: print("rec'd: ", fileName)

        #if not fileName:     # done
        #    if debug: print(f"thread connected to {addr} done")
        #    self.fsock.close() #possible error
        #    return          # exit


        #convert transferFile name to string
        fileName = fileName.decode()     #receive byte array of name to be saved and convert to string

        #check if file exists and send response
        if exists(fileName):
            self.fsock.send(b"True", debug)
        else:
            #lock
            dictLock.acquire()
            currentCheck = dictionary.get(fileName)

            #Check dictionary
            if currentCheck == 'running':
                self.fsock.send(b"True", debug)
                dictLock.release()
                print(fileName+ "is currently being transfered")
            #continue if file doesn't exist
            else:
                #not being transferred
                dictionary[fileName] = "running"
                #release lock
                dictLock.release()

                sleep(10)
                self.fsock.send(b"False", debug)
                try:
                    #receive file
                    fileContents = self.fsock.receive(debug)
                except:
                    print("error while receiving.")
                    sys.exit(0)


                try:
                    #send response
                    self.fsock.send(fileContents, debug)
                except:
                    print('error while sending!')

                #write new filename
                newFile = open(fileName, 'wb') #open and set to write byte array
                #write contents to file
                newFile.write(fileContents) #writing to file
                #close file
                newFile.close()


                dictLock.acquire()
                #delete file from dictionary
                del dictionary[fileName]
                dictLock.release()
        self.fsock.close()


while True:
    sockAddr = lsock.accept()
    server = Server(sockAddr)
    server.start()
