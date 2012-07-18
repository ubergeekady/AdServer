#!/usr/bin/env python

import uuid
import os

import tornado.ioloop
import tornado.web

from os import listdir
from os.path import isfile, join
from logging.config import fileConfig

class MainHandler(tornado.web.RequestHandler):
    
    def post(self):
        if self.request.path == "/access":
            self.access()
        if self.request.path == "/poll":
            self.poll()
        if self.request.path == "/getFile":
            self.getFile()
    
    def access(self):
        global timeout
        global logList
        logMsg = self.get_argument('log')
        if len(logList) < 5000 : 
            logList.append(str(logMsg))
        elif len(logList) >= 5000 :
            try:
                f = open(logFolder+'/'+str(uuid.uuid4()),'w')
                f.write(str(logList))
                logList = []
                timeout = False
                f.close()
            except Exception, e:
                print "File create error in access"
                raise e
        
    def poll(self):
        try:
            allFiles = [ f for f in listdir(logFolder) if isfile(join(logFolder,f)) ]
            if allFiles:
                self.write(str(allFiles))
        except Exception, e:
            print "List file error" 
            raise e
              
    def getFile(self):
        try:
            fileName = str(self.get_argument('file'))
            if fileName:
                fileContent = open(logFolder+'/'+fileName).read()
                self.write(fileContent)
                try:
                    os.remove(logFolder+'/'+fileName)
                except Exception, e:
                    print "Cannot delete the file !"
                    raise e
        except Exception, e:
            print "File open error / File does not exist"
            raise e
                            
    
def timeoutFunction():
    global timeout
    global logList
    if timeout:
        try:
            if logList:
                f = open(logFolder+'/'+str(uuid.uuid4()),'w')
                f.write(str(logList))
                f.close()
            else:
                print "empty list"     
            logList = []
            timeout = False
            print "Successful timeout"
        except Exception, e :
            print "File create error in timeout"
            raise e
    timeout = True        
                    

application = tornado.web.Application([(r".*", MainHandler),])
logList = []
logFolder = './LogFolder'
timeout = False

if not os.path.exists(logFolder):
    try:
        os.makedirs(logFolder)
    except Exception, e:
        print "Cannot create LogFolder"    
        raise e

if __name__ == "__main__":
    application.listen(9000)
    tornado.ioloop.PeriodicCallback(timeoutFunction, 60000).start()
    tornado.ioloop.IOLoop.instance().start()