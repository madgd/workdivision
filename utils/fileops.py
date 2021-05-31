#!/usr/bin/env python
# encoding: utf-8
"""
    @author: madgd
    @license: (C) Copyright 2020-2021 madgd. All Rights Reserved.
    @contact: madgdtju@gmail.com
    @software: 
    @file: fileops.py.py
    @time: 2021/5/19 10:22 下午
    @desc:
"""
from os import walk, path

def find_newest_file(file_path, file_pre):
    """

    :param file_path:
    :param file_pre:
    :return:
    """
    # find the file
    # if file in net drive, try mount it local:
    # https://madgd.github.io/2021/05/20/wsL2%E4%B8%AD%E6%8C%82%E8%BD%BDwindows%E4%B8%8B%E7%9A%84%E7%BD%91%E7%BB%9C%E7%A1%AC%E7%9B%98/
    _, _, filenames = next(walk(file_path))
    filenames = filter(lambda x: x.startswith(file_pre), filenames)
    (ctime, filename) = max([(path.getctime(file_path + filename), filename) for filename in filenames])
    print(ctime, filename)
    return filename