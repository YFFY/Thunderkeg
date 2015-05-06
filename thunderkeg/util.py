#! /usr/bin/env python
# --*-- coding:utf-8 --*--

from config.setting import *
import os
import sys
import json
import requests
import logging
import logging.config


def getLogger():
    loggingConfigFile = os.path.join(os.path.split(os.path.abspath(sys.path[0]))[0], 'config/logging.conf')
    logging.config.fileConfig(loggingConfigFile)
    logger = logging.getLogger()
    return logger

def getIndexingContent():
    logger = getLogger()
    indeingContentMap = dict()
    for fileName in indexFileList:
        fileAbsPath = os.path.join(os.path.split(os.path.abspath(sys.path[0]))[0], 'indexing\{0}'.format(fileName))
        if not os.path.exists(fileAbsPath):
            logger.error('i have not found indexing file: [{0}]'.format(fileAbsPath))
            sys.exit()
        with open(fileAbsPath, 'r') as fr:
            rawContent = fr.read()
            try:
                jsonContent = json.loads(rawContent)
                try:
                    firehoseDir = jsonContent.get('firehose').get('baseDir')
                    firehoseFile =  jsonContent.get('firehose').get('filter')
                    fireAbsFilePath = os.path.join(firehoseDir, firehoseFile)
                    if not os.path.exists(fireAbsFilePath):
                        logger.error('i have not found firehouse file: [{0}]'.format(fireAbsFilePath))
                        sys.exit()
                    else:
                        with open(fireAbsFilePath, 'r') as fs:
                            for line in fs:
                                stripline = line.strip()
                                try:
                                    json.loads(stripline)
                                except Exception as ex:
                                    logger.error('i have found a invalid json: [{0}] in firehouse filter file: [{1}], may be is can cause import data failed'.format(stripline, fireAbsFilePath))
                except Exception as ex:
                    logger.error('get firehouse filter file failed, may be there is no key "baseDir" or "filter" in firehouse section')
            except Exception as ex:
                logger.error('i have found this is a invalid json in [{0}]'.format(fileAbsPath))
                sys.exit()
            else:
                indeingContentMap[fileName] = jsonContent
    logger.info('check file success, get indexing file content success')
    return indeingContentMap

def sendPost():
    indexingContentMap = getIndexingContent()
    logger = getLogger()
    taskNameMap = dict()
    for indexFile in indexingContentMap:
        r = requests.post(importDataUrl, data=indexingContentMap.get(indexFile))
        if r.status_code == 200:
            text = r.text
            print text
        else:
            logger.error('send import request with post method failed, get response code : [{0}]'.format(r.status_code))


if __name__ == '__main__':
    sendPost()