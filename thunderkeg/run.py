#! /usr/bin/env python
# --*-- coding:utf-8 --*--

from config.setting import *
import os
import sys
from time import sleep
import json
import requests
import logging
import logging.config


def getlogger():
    loggingConfigFile = os.path.join(os.path.split(os.path.abspath(sys.path[0]))[0], 'config/logging.conf')
    logging.config.fileConfig(loggingConfigFile)
    logger = logging.getLogger()
    return logger

class Importer(object):

    def __init__(self):
        self.logger = getlogger()
        self.taskMap = dict()

    def getIndexingContent(self):
        indeingContentMap = dict()
        self.indexingCount = len(indexFileList)

        for fileName in indexFileList:
            fileAbsPath = os.path.join(os.path.split(os.path.abspath(sys.path[0]))[0], 'indexing/{0}'.format(fileName))
            if not os.path.exists(fileAbsPath):
                self.logger.error('i have not found indexing file: [{0}]'.format(fileAbsPath))
                sys.exit()
            with open(fileAbsPath, 'r') as fr:
                rawContent = fr.read()
                try:
                    jsonContent = json.loads(rawContent)
                    fireHouseDir = jsonContent.get('firehose').get('baseDir')
                except Exception as ex:
                    self.logger.error('i have found this is a invalid json in [{0}]'.format(fileAbsPath))
                    sys.exit()
                else:
                    indeingContentMap[fileName] = rawContent
        self.logger.info('check file success, get indexing file content success')
        return fireHouseDir, indeingContentMap

    def sendImportPost(self):
        fireHouseDir, indexingContentMap = self.getIndexingContent()
        headers = {'content-type': 'application/json'}
        self.fileCount = len(os.listdir(fireHouseDir))
        self.logger.info('get indexing file count: {0}'.format(self.indexingCount))
        self.logger.info('get data file count: {0}'.format(self.fileCount))
        self.logger.info('i should get task count: {0}'.format(self.indexingCount * self.fileCount))
        for dataFileName in os.listdir(fireHouseDir):
            for indexFile in indexingContentMap:
                data = indexingContentMap.get(indexFile)
                jsonData = json.loads(data)
                jsonData['firehose']['filter'] = dataFileName
                r = requests.post(importDataUrl, data=json.dumps(jsonData), headers=headers)
                if r.status_code == 200:
                    text = r.text
                    try:
                        taskName = json.loads(text).get('task')
                        self.logger.info('get task: {0}'.format(taskName))
                    except Exception as ex:
                        self.logger.error('i have find a error when send post request: [{0}]'.format(ex))
                    else:
                        sleep(wait_time)
                        status = self.getTaskStatus(taskName)
                        if status == "RUNNING":
                            sleep(wait_time)
                            status = self.getTaskStatus(taskName)
                            logging.info('{0} {1} {2} {3}'.format(dataFileName, indexFile, taskName, status))
                        else:
                            logging.info('{0} {1} {2} {3}'.format(dataFileName, indexFile, taskName, status))
                else:
                    self.logger.error('send overlord request with post method failed, get response code : [{0}]'.format(r.status_code))


    def getTaskStatus(self, taskName):
        r = requests.get(queryStatusUrl.format(taskName))
        if r.status_code == 200:
            status = json.loads(r.text).get('status').get('status')
            return status

if __name__ == '__main__':
    i = Importer()
    i.sendImportPost()