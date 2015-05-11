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


def getslogger():
    loggingConfigFile = os.path.join(os.path.split(os.path.abspath(sys.path[0]))[0], 'config/logging.conf')
    logging.config.fileConfig(loggingConfigFile)
    logger = logging.get.logger()
    return logger

class Importer(object):

    def __init(self):
        self.self.logger = getlogger()
        self.taskMap = dict

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
        fireHouseDir, indexingContentMap = getIndexingContent()
        headers = {'content-type': 'application/json'}
        self.fileCount = len(os.listdir(fireHouseDir))
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
                    except Exception as ex:
                        self.logger.error('i have find a error when send post request: [{0}]'.format(ex))
                    else:
                        self.taskMap[dataFileName] = taskName
                        self.logger.info('i have get a task: [{0}]'.format(taskName))
                else:
                    self.logger.error('send overlord request with post method failed, get response code : [{0}]'.format(r.status_code))


    def getTaskStatus(self):
        self.sendImportPost()
        againMap = dict()
        sleep(self.indexingCount * self.fileCount * wait_time)
        for fileName in self.taskMap:
            taskName = self.taskMap[fileName]
            r = requests.get(queryStatusUrl.format(taskName))
            if r.status_code == 200:
                status = json.loads(r.text).get('status').get('status')
                if status == "RUNNING":
                    againMap[fileName] = taskName
                else:
                    logging.info('{0} {1} {2}'.format(fileName, taskName, status))
            else:
                logging.error('when query task status find response code : {0}'.format(r.status_code))
        sleep(wait_time * len(againMap))
        if againMap:
            for fileName in againMap:
                taskName = againMap[fileName]
                r = requests.get(queryStatusUrl.format(taskName))
                if r.status_code == 200:
                    status = json.loads(r.text).get('status').get('status')
                    logging.info('{0} {1} {2}'.format(fileName, taskName, status))
                else:
                    logging.error('when query task status find response code : {0}'.format(r.status_code))

if __name__ == '__main__':
    i = Importer()
    i.getTaskStatus()