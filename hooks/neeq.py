#!/usr/bin/env python
# encoding: utf-8
"""
    @author: madgd
    @license: (C) Copyright 2020-2021 madgd. All Rights Reserved.
    @contact: madgdtju@gmail.com
    @software: 
    @file: neeq.py
    @time: 2021/5/19 11:03 下午
    @desc: parse neeq 分工表
"""
import sqlite3
import openpyxl

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def parse_neeq(file):
    """

    :param file:
    :return:
    """
    # db conn
    conn = sqlite3.connect('workdivision.db')
    conn.row_factory = dict_factory
    c = conn.cursor()

    # read excel and update
    wb = openpyxl.load_workbook(filename=file)

    # sheet4
    sheet4 = wb["组别AB岗"]
    allRows = sheet4.rows
    next(allRows) # skip header
    for row in allRows:
        name = row[0].value
        team = row[1].value
        backup = row[2].value
        state = row[3].value
        c.execute("insert or replace into staff (id, name, backup, team, state) values (\
                    (select id from staff where name = ?), ?, ?, ?, ?)",
                  (name, name, backup, team, state)
                 )
        conn.commit()

    # sheet5
    sheet5 = wb['监管员券商对应']
    allRows = sheet5.rows
    next(allRows) # skip header
    for row in allRows:
        name = row[0].value
        staff_name = row[1].value
        ori = ""
        if "、" in staff_name or\
            "," in staff_name or\
            "，" in staff_name or\
            "（" in staff_name:
            ori = staff_name
            staff_name = staff_name.split("、")[0].split(",")[0].split("，")[0].split("（")[0]
        c.execute("insert or replace into client_group (id, name, staff_id, staff_name, type, customize) values (\
                    (select id from client_group where name = ?), ?, (select id from staff where name = ?), ?, ?, ?)",
                  (name, name, staff_name, staff_name, "broker", ori)
                 )
        conn.commit()

    # sheet1
    sheet1 = wb["基础创新层挂牌公司"]
    allRows = sheet1.rows
    next(allRows) # skip header
    for row in allRows:
        code = row[0].value
        name = row[1].value
        broker = row[2].value
        staff_name = row[3].value
        c.execute("insert or replace into client (id, name, staff_id, staff_name, group_id, group_name, type) values (\
                    ?, ?, (select id from staff where name = ?), ?, (select id from client_group where name = ?),?, ?)",
                  (code, name, staff_name, staff_name, broker, broker, "company")
                 )
        conn.commit()

    # sheet2
    sheet2 = wb["创新层明细"]
    allRows = sheet2.rows
    next(allRows) # skip header
    for row in allRows:
        code = row[0].value
        level = "创新层"
        top_industry_tag = row[3].value
        detail_industry_tag = row[4].value
        c.execute("update client set level=?, industry=? where id=?",\
                  (level, "%s;%s"%(top_industry_tag, detail_industry_tag), code))
        conn.commit()

    # sheet3
    sheet3 = wb["基础层明细"]
    allRows = sheet3.rows
    next(allRows) # skip header
    for row in allRows:
        code = row[0].value
        level = "基础层"
        c.execute("update client set level=? where id=?",\
                  (level, code))
        conn.commit()

    # sheet6
    sheet6 = wb["老三板"]
    allRows = sheet6.rows
    next(allRows) # skip header
    for row in allRows:
        code = row[1].value
        name = row[2].value
        broker = row[3].value
        staff_name = row[4].value
        trade_time = row[6].value
        customize = row[7].value
        level = "老三板"
        type = "old3"
        c.execute("insert or replace into client (id, name, staff_id, staff_name, group_id, group_name,\
                    type, level, trade_time, customize) values (\
                    ?, ?, (select id from staff where name = ?), ?, (select id from client_group where name = ?),\
                    ?, ?, ?, ?, ?)",
                  (code, name, staff_name, staff_name, broker, broker, type, level, trade_time, customize)
                 )
        conn.commit()

    # sheet7
    sheet7 = wb["派出机构对接"]
    allRows = sheet7.rows
    next(allRows) # skip header
    next(allRows) # skip header
    for row in allRows:
        id = row[0].value
        area = row[1].value
        staff_name = row[2].value
        type = "agency"
        c.execute("insert or replace into client (id, name, staff_id, staff_name, type) values (\
                    ?, ?, (select id from staff where name = ?), ?, ?)",
                  (id, area, staff_name, staff_name, type)
                 )
        conn.commit()

def parse_contacts(file):
    """

    :param file:
    :return:
    """
    # db conn
    conn = sqlite3.connect('workdivision.db')
    conn.row_factory = dict_factory
    c = conn.cursor()

    # read excel and update
    wb = openpyxl.load_workbook(filename=file)

    # sheet1
    sheet1 = wb["券商联系人"]
    allRows = sheet1.rows
    next(allRows) # skip header
    for row in allRows:
        name = row[3].value
        if row[0].value is None or not name:
            continue
        print(row[0].value)
        client_group_name = row[0].value
        client_group_fullname = row[1].value
        staff_name = row[2].value

        # raw_type = row[1].value
        type = "client_group"
        target_table = "client_group"
        # if raw_type == "券商":
        #     target_table = "client_group"
        #     type = "client_group"
        # elif raw_type == "监管员":
        #     target_table = "staff"
        #     type = "staff"

        position = row[4].value
        email = row[5].value
        phone = row[6].value
        tele = row[7].value
        wechat = row[8].value
        prime = 1
        # check client_group exist 
        sql = "SELECT id from client_group where name = '%s'" % client_group_name
        print(sql)
        cursor = c.execute(sql)
        # in case of duplicate names
        if len(list(cursor)):
            c.execute("insert or replace into contacts (id, name, type, related_id, position, prime,\
                        phone, tele, email, wechat) values (\
                        (select id from contacts where name = ? and related_id = (select id from client_group where name = ?)), ?, ?,\
                        (select id from client_group where name = ?), ?, ?, ?, ?, ?, ?)",
                      (name, client_group_name, name, type, client_group_name, position, prime,\
                       phone, tele, email, wechat)
                     )
            res = conn.commit()

    # sheet2
    sheet2 = wb["监管员联系方式"]
    allRows = sheet2.rows
    next(allRows) # skip header
    for row in allRows:
        name = row[0].value
        phone = row[1].value
        tele = row[2].value
        email = row[3].value
        wechat = row[4].value
        prime = 1
        position = ""
        type = "staff"
        # check client_group exist 
        sql = "SELECT id from staff where name = '%s'" % name
        print(sql)
        cursor = c.execute(sql)
        # in case of duplicate names
        if len(list(cursor)):
            c.execute("insert or replace into contacts (id, name, type, related_id, position, prime,\
                        phone, tele, email, wechat) values (\
                        (select id from contacts where name = ?), ?, ?,\
                        (select id from staff where name = ?), ?, ?, ?, ?, ?, ?)",
                      (name, name, type, name, position, prime,\
                       phone, tele, email, wechat)
                     )
            conn.commit()