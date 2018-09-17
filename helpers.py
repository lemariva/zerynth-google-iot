# -*- coding: utf-8 -*-
# @Author: Lorenzo
# @Date:   2017-10-03 10:56:02
# @Last Modified by:   lorenzo
# @Last Modified time: 2017-10-26 10:44:43

import json

def load_key(key_file):
    mstream = open('resource://' + key_file)
    pkey = bytearray(64)
    for i in range(64):
        pkey[i] = mstream.read(1)[0]
    return pkey

def load_device_conf():
    confstream = open('resource://device.conf.json')
    conf = ''
    while True:
        line = confstream.readline()
        if not line:
            break
        conf += line
    return json.loads(conf)
