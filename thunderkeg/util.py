#! /usr/bin/env python
# --*-- coding:utf-8 --*--

import os


def mergeFile(path):

    dirList = os.listdir(path)
    for dir in dirList:
        mergefile = 'native_{0}.json'.format(dir)
        abspath = os.path.join(path, dir)
        fileList = os.listdir(abspath)
        absfileList = [os.path.join(abspath, f) for f in fileList]
        with open(mergefile, 'a') as fa:
            for absfile in absfileList:
                with open(absfile, 'r') as fr:
                    for line in fr:
                        fa.writelines(line)

def transfer(path):
    for f in os.listdir(path):
        command = 'dyscp 10.1.5.61 /data/native {0}'.format(f)
        if f.endswith('json'):
            os.system(command)

if __name__ == '__main__':
    transfer('/sqldata/yufeng')