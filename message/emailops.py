#!/usr/bin/env python
# encoding: utf-8
"""
    @author: madgd
    @license: (C) Copyright 2020-2021 madgd. All Rights Reserved.
    @contact: madgdtju@gmail.com
    @software: 
    @file: emailops.py
    @time: 2021/5/27 11:31 上午
    @desc: email driver
"""
import smtplib
from smtplib import SMTP_SSL
import imaplib
import configparser
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from os.path import basename
import mimetypes
from email.mime.base import MIMEBase
from email import encoders


EmailConfig = "%s/config/email.ini" % "/".join(__file__.split('/')[:-2])
ConfigSec = "DEFAULT"

def sendEmail(addresses, content, mail_title, attach, cc=[]):
    """

    :param addresses: To list
    :param content:
    :param mail_title:
    :param attach: attach file list
    :return:
    """
    # config
    config = configparser.ConfigParser()
    config.read(EmailConfig)
    host_server = config.get(ConfigSec, "host_server")
    fromaddress = config.get(ConfigSec, "fromaddress")
    password = config.get(ConfigSec, "password")
    inport = config.get(ConfigSec, "inport")
    print(host_server, fromaddress, password, inport)

    # email content
    mail_content = content
    msg = MIMEMultipart()
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg.attach(MIMEText(mail_content, 'plain', 'utf-8'))
    msg = MIMEMultipart()
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = fromaddress
    msg["To"] = ";".join(addresses)
    msg["Cc"] = ";".join(cc)
    msg.attach(MIMEText(mail_content, 'html', 'utf-8'))
    # msgtext = MIMEText("<font color=red> 官网业务周平均延时图表 :<br><img src=\"cid:weekly\"border=\"1\"><br> 详细内容见附件。</font>",
    #                    "html", "utf-8")

    # attach
    for f in attach:
        try:
            mime = mimetypes.guess_type(f['filepath'])[0].split("/")
            attachfile = MIMEBase(mime[0], mime[1])
            attachfile.set_payload(open(f['filepath'], 'rb').read())
            # name = basename(f)
            name = f['filename']
            attachfile.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', name))  # 扩展标题设置
            encoders.encode_base64(attachfile)
            msg.attach(attachfile)
        except:
            print(f, "file wrong")

    # send
    try:
        smtp = SMTP_SSL(host_server)
        smtp.set_debuglevel(1)
        smtp.ehlo(host_server)
        smtp.login(fromaddress, password)
        smtp.sendmail(fromaddress, addresses, msg.as_string())
        smtp.quit()
        print("email sent")
    except smtplib.SMTPException:
        print("email send failed")


def receiveEmail():
    # config
    config = configparser.ConfigParser()
    config.read(EmailConfig)
    host_server = config.get(ConfigSec, "host_server")
    fromaddress = config.get(ConfigSec, "fromaddress")
    password = config.get(ConfigSec, "password")
    inport = config.get(ConfigSec, "inport")
    print(host_server, fromaddress, password, inport)

    # receive
    conn = imaplib.IMAP4_SSL(port=inport, host=host_server)
    conn.login(fromaddress, password)
    conn.select()
    count = len(conn.search(None, 'ALL')[1][0].split())
    # read last one
    typ, email_content = conn.fetch(f'{count}'.encode(), '(RFC822)')
    # byte 2 str
    email_content = email_content[0][1].decode()
    print(email_content)
    conn.close()
    conn.logout()


if __name__ == '__main__':
    addresses = ["iamnushead@gmail.com"]
    Subject = 'Python自动发送的邮件'  # 邮件标题
    content = "您好，这是使用python登录邮箱发送邮件的测试"
    attach = [
        {
            "filename": 'test.xlsx',
            "filepath": "/Users/madgd/Downloads/test3/test.xlsx",
        },
        {
            "filename": 'testdoc.docx',
            "filepath": "/Users/madgd/Downloads/test3/testdoc.docx",
        },
    ]
    sendEmail(addresses, content, Subject, attach)