"""
Custom logger module

Author: Luigi di Corrado
Mail: luigi.dicorrado@eng.it
Date: 28/08/2020
Company: Engineering Ingegneria Informatica S.p.A.

Introduction : This logger is used to track the execution of Random Forest modules, 
               writing message that are labeled with some defined status tags like "ERROR" or "INFO" 
               followed by the function name that requested to write the message.
               Those messages are saved using append mode into a file that will be stored to the defined folder.



Function     : __getStatus (Private)

Description  : Read the status code given and return the correct status label.
               If the code given is not found within the dictionary that contains the defined label
               the "UNDEFINED" status will be set.
               
               Current status labels:
               0 ERROR
               1 OK
               2 WARNING
               3 INFO
               4 COMPLETE
               
Parameters   : Integer  code     used to get the status label of the message               
               
Return       : String   status   contain the corresponding label



Function     : writeMessage

Description  : Write the given message and other infos into a log file

               Default filename is: Random_forest_log.log
               Default folder path: ./logs
               
               The message structure is composed by:
               [DATE WITH TIMESTAMP] [STATUS TAG] [FUNCTION NAME] MESSAGE
               
Parameters   : String   message        contains the message to record
               Integer  statusCode     used to get the status label of the message
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

from util.logger import log
import sys
functionName = sys._getframe().f_code.co_name
myLog = log()

def Execute():
    functionName = sys._getframe().f_code.co_name
    try:
        myLog.writeMessage("Executing division!",3,functionName)
        x = 5/0
        myLog.writeMessage("Division complete!",1,functionName)
    except:
        myLog.writeMessage("Warning an exception occured!",2,functionName)
        raise
        
myLog.writeMessage("Process start",3,functionName)
with myLog.error_debug():
    try:
        Execute()
        myLog.writeMessage("Process completed successfully!",1,functionName)
    except:
        myLog.writeMessage("Warning an exception occured!",2,functionName)
        raise   

Output 

[2020-08-28 16:04:19.646]    [INFO]        [<module>]           Process start 
[2020-08-28 16:04:19.646]    [INFO]        [Execute]            Executing division! 
[2020-08-28 16:04:19.647]    [WARNING]     [Execute]            Warning an exception occured! 
[2020-08-28 16:04:19.647]    [WARNING]     [<module>]           Warning an exception occured! 
[2020-08-28 16:04:19.652]    [ERROR]       [Execute]            Unhandled exception detected! 

----- Start diagnostic info ----- 

File: <ipython-input-3-d30319679655> 
Function: Execute 
Code context:
    8:     try:
    9:         myLog.writeMessage("Executing division!",3,functionName)
   10:>        x = 5/0
   11:         myLog.writeMessage("Division complete!",1,functionName)
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
from contextlib import contextmanager

class log:
    def __init__(self):
        self.statusCodes = {
            0: "ERROR",
            1: "OK",
            2: "WARNING",
            3: "INFO",
            4: "COMPLETE"
        }

    def __getStatus(self, code):
        status = self.statusCodes.get(code)
        if status is None:
            status = "UNDEFINED"
        return status

    def writeMessage(self, message, statusCode, functionName):
        status = self.__getStatus(statusCode)
        folder = './logs'
        filename = 'Random_forest.log'
        fullpath = folder + '/' + filename
        try:
            # Check if directory exists, or create it
            os.makedirs(folder)
        except FileExistsError:
            # Directory already exists
            pass
        if os.path.exists(fullpath):
            append_write = 'a'  # append
        else:
            append_write = 'w'  # new file

        log = open(fullpath, append_write)
        try:
            log.write('[' + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + ']    {0:13} {1:20} {2} \n'.format('['+status+']','['+functionName+']',message))
        finally:
            log.close()
    
    @contextmanager
    def error_debug(self):
        try:
            yield
        except:
            message = ""
            message = message + 'Unhandled exception detected! \n'
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
            self.writeMessage(message,0,functionName)
            raise