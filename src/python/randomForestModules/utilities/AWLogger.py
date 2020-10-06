"""
Custom logger module

Author: Luigi di Corrado
Mail: luigi.dicorrado@eng.it
Date: 18/09/2020
Company: Engineering Ingegneria Informatica S.p.A.

Introduction : This logger is used to track the execution of Random Forest modules, 
               writing message that are labeled with some defined status tags like "ERROR" or "INFO" 
               followed by the function name that requested to write the message.
               Those messages are saved using append mode into a file that will be stored to the defined folder.
               It's possible to set a different logger level by setting the "loggerLevel" var into
               init function of the class.
               By default the logger level is set to "DEBUG", that will keep trace of all the message.
               When the application goes on production, just change the loggerLevel variable to "ERROR"
               that will set te logger to keep trace only of "ERROR" and "FATAL" messages.



Function     : __getStatusLevel (Private)

Description  : Read the status code given and return the correct status level.
               If the code given is not found within the dictionary the -1 status will be set.
               
               Current status levels:
               0 DEBUG
               1 INFO
               2 WARN
               3 ERROR
               4 FATAL
               
Parameters   : String   code     used to get the status level of the message               
               
Return       : int      status   contain the corresponding level



Function     : writeMessage

Description  : Write the given message and other infos into a log file

               Default filename is: animal_welfare.log
               Default folder path: ./logs
               
               The message structure is composed by:
               [DATE WITH TIMESTAMP] [STATUS LEVEL] [FUNCTION NAME] MESSAGE
               
Parameters   : String   message        contains the message to record
               String   statusLevel    used to get the level of the message
               String   functionName   show the function name that requested to record the message
               
Return       : 



Function     : error_debug

Description  : When an exception occurs under the context of error_debug function, 
               it will be saved into the log file with diagnostic information for debug.

               Error diagnostic info structure:
               File: the file where the exception was detected
               Function: the function name
               Code context: shows a slice of code and the row (signed with ">") where the exception occured
               Traceback: More info about the calls, the last row shows the last call 
               whit exception and the type of error.
               
Parameters   : 
               
Return       : 


How to use example

from Logger import log
import sys
functionName = sys._getframe().f_code.co_name
myLog = log()

def Execute():
    functionName = sys._getframe().f_code.co_name
    try:
        myLog.writeMessage("Executing division!","INFO",functionName)
        x = 5/0
        myLog.writeMessage("Division complete!","DEBUG",functionName)
    except:
        myLog.writeMessage("Warning an exception occured!","ERROR",functionName)
        raise
        
myLog.writeMessage("Process start","INFO",functionName)
with myLog.error_debug():
    try:
        Execute()
        myLog.writeMessage("Process completed successfully!","INFO",functionName)
    except:
        myLog.writeMessage("Warning an exception occured!","ERROR",functionName)
        raise   

Output 

[2020-08-28 16:04:19.646]    [INFO]        [<module>]           Process start 
[2020-08-28 16:04:19.646]    [INFO]        [Execute]            Executing division! 
[2020-08-28 16:04:19.647]    [WARN]        [Execute]            Warning an exception occured! 
[2020-08-28 16:04:19.647]    [WARN]        [<module>]           Warning an exception occured! 
[2020-08-28 16:04:19.652]    [FATAL]       [Execute]            Unhandled exception detected! 

----- Start diagnostic info ----- 

File: <ipython-input-3-d30319679655> 
Function: Execute 
Code context:
    8:     try:
    9:         myLog.writeMessage("Executing division!","INFO",functionName)
   10:>        x = 5/0
   11:         myLog.writeMessage("Division complete!","DEBUG",functionName)
   12:     except:

Traceback (most recent call last):
  File "C:............logger.py", line 112, in error_debug
    yield
  File "<ipython-input-3-d30319679655>", line 19, in <module>
    Execute()
  File "<ipython-input-3-d30319679655>", line 10, in Execute
    x = 5/0
ZeroDivisionError: division by zero

----- End diagnostic info -----

"""

import datetime as dt
import sys
import os
import inspect
import sys
import traceback
import configparser
from contextlib import contextmanager

class log:
    def __init__(self):
        self.config = configparser.ConfigParser()

        self.loggerLevel = ''
        self.folder = ''
        self.filename = ''
        self.fullpath = ''
        self.statusCodes = {
            "DEBUG":0,
            "INFO":1,
            "WARN":2,
            "ERROR":3,
            "FATAL":4
        }
        
    def initConfiguration(self, confFile):
        self.config.read(confFile)
        self.loggerLevel = self.config.get('PyLogger', 'animalwelfare.logger.level')
        self.folder = self.config.get('PyLogger', 'animalwelfare.logger.filePath')
        self.filename = self.config.get('PyLogger', 'animalwelfare.logger.fileName')
        self.fullpath = self.folder + '/' + self.filename

    def __getStatusLevel(self, code):
        status = self.statusCodes.get(code)
        if status is None:
            status = -1
        return status

    def writeMessage(self, message, statusLevel, functionName):
        messageLevel = self.__getStatusLevel(statusLevel)
        if messageLevel == -1 : 
            statusLevel = "DEBUG"
            messageLevel = self.__getStatusLevel(statusLevel)
        currentLoggerLevel = self.__getStatusLevel(self.loggerLevel)      
        try:
            # Check if directory exists, or create it
            os.makedirs(self.folder)
        except FileExistsError:
            # Directory already exists
            pass
        if os.path.exists(self.fullpath):
            append_write = 'a'  # append
        else:
            append_write = 'w'  # new file

        log = open(self.fullpath, append_write)
        try:
            if messageLevel >= currentLoggerLevel :
                log.write('[' + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + ']    {0:13} {1:20} {2} \n'.format('['+statusLevel+']','['+functionName+']',message))
        finally:
            log.close()
    
    @contextmanager
    def error_debug(self):
        try:
            yield
        except:
            message = ""
            message = message + 'Showing error information below : \n'
            message = message + '\n----- Start diagnostic info ----- \n'
            frame_info = inspect.trace(5)[-1]
            fileName = frame_info[1]
            functionName = frame_info[3]
            message = message + '\n' + 'File: {0} \n'.format(fileName)
            message = message + 'Function: {0} \n'.format(functionName)
            
            # read code context with rows numbers
            context = ''
            for i, line in enumerate(frame_info[4], frame_info[2] - frame_info[5]):
                if i == frame_info[2]:
                    context += '{0}:>{1}'.format(str(i).rjust(5), line)
                else:
                    context += '{0}: {1}'.format(str(i).rjust(5), line)
            message = message + 'Code context:\n' + context
            exc_type, exc_value, exc_traceback = sys.exc_info()
            message = message + '\n' + traceback.format_exc()
            message = message + '\n' + '----- End diagnostic info -----' +'\n'
            self.writeMessage(message,"FATAL",functionName)
            raise