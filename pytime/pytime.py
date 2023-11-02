#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time

# !/usr/bin/python3

ticks = time.time()
print("当前时间戳为:", ticks)

localtime = time.localtime(time.time())
print("本地时间为 :", localtime)

localtime = time.asctime(time.localtime(time.time()))
print("本地时间为 :", localtime)

