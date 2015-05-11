#! /usr/bin/env python
# --*-- coding:utf-8 --*--

# running configure, when import druid data with this tool, this file should be configure carefully at the beginning

indexFileList = ["ymds_druid_datasource.json", "ymds_druid_datasource6.json"]
# importDataUrl = "http://10.1.5.61:8090/druid/indexer/v1/task"   # post this
# queryStatusUrl = "http://10.1.5.61:8090/druid/indexer/v1/task/{0}/status" # get this

importDataUrl = "http://172.20.0.49:8090/druid/indexer/v1/task"   # post this
queryStatusUrl = "http://172.20.0.49:8090/druid/indexer/v1/task/{0}/status" # get this
wait_time = 1800
