#!/usr/bin/env python
# encoding: utf-8
"""
    @author: madgd
    @license: (C) Copyright 2020-2021 madgd. All Rights Reserved.
    @contact: madgdtju@gmail.com
    @software: 
    @file: main.py.py
    @time: 2021/5/18 10:44 上午
    @desc: the main entry
"""

from hooks import neeq
from os import walk, path
from utils import fileops

def batch_update(file_path, file_pre, hook_name):
    """

    :param file_path:
    :param file_pre:
    :param hook_name:
    :return:
    """
    # todo: export before import
    # find the file
    filename = fileops.find_newest_file(file_path, file_pre)

    # parse file using hook
    if hook_name == "neeq":
        neeq.parse_neeq(file_path + filename)

def batch_update_contacts(file_path, file_pre, hook_name):
    """

    :param file_path:
    :param file_pre:
    :param hook_name:
    :return:
    """
    # find the file
    filename = fileops.find_newest_file(file_path, file_pre)

    #
    if hook_name == "neeq":
        neeq.parse_contacts(file_path + filename)

def main():
    print("in main")
    # excelSplitBySheet()


if __name__ == '__main__':
    # read args

    # do work
    file_path = "/Users/madgd/Downloads/test3/"
    file_pre = "基本岗分工表"
    hook = "neeq"
    # batch_update(file_path, file_pre, hook)
    batch_update_contacts(file_path, "", hook)