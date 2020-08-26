import datetime as dt
import sys
import os
import inspect

class log:
    def __init__(self):
        self.statusCodes = {
            0: "ERROR",
            1: "COMPLETE",
            2: "WARNING",
            3: "INFO"
        }

    # Get status name
    def getStatus(self, Code):
        status = self.statusCodes.get(Code)
        return status

    # Log file message, create a directory and write a file with log messages
    def writeMessage(self, Message, StatusCode):
        status = self.getStatus(StatusCode)
        folder = './logs'
        filename = 'Random_forest_log.log'
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
            #log.write('[' + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] -- [' + status + '] -- ' + Message + '\n')
            log.write('[' + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + ']     {0:14} {1} \n'.format('['+status+']',Message))
        finally:
            log.close()