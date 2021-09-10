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
import poplib
from email.parser import Parser
from imbox import Imbox
import datetime
import time
from urllib.parse import unquote
import base64
from email.header import decode_header


EmailConfig = "%s/config/email.ini" % "/".join(__file__.split('/')[:-2])
ConfigSec = "DEFAULT"

def decodeAttachName(raw):
    """

    :param raw: email.header encoded str
    :return: decoded name
    """
    name = ""
    raw = raw.strip()
    if raw.startswith("utf-8''"):
        raw = raw.replace("utf-8''", '')
    try:
        decoded_string, charset = decode_header(raw)[0]
        if charset is not None:
            try:
                name = decoded_string.decode(charset)
            except UnicodeDecodeError:
                print("Cannot decode addr name %s", raw)
        else:
            name = decoded_string
    except:
        pass
    return unquote(name)


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

    # email content
    mail_content = content
    msg = MIMEMultipart()
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg.attach(MIMEText(mail_content, 'plain', 'utf-8'))
    msg = MIMEMultipart()
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = fromaddress
    msg["To"] = ",".join(addresses)
    msg["Cc"] = ",".join(cc)
    msg.attach(MIMEText(mail_content, 'html', 'utf-8'))
    # log
    attach_names = ";".join([a["filename"] for a in attach])
    print("[emailops][try send email][tm=%s]host:%s, port:%s, from:%s, to:%s, cc:%s, Subject:%s, attach:%s"
          % (f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}", host_server, inport, fromaddress, msg["To"], msg["Cc"], msg["Subject"],
             attach_names)
          )

    # attach
    for f in attach:
        try:
            mime = mimetypes.guess_type(f['filepath'])[0].split("/")
            attachfile = MIMEBase(mime[0], mime[1])
            attachfile.set_payload(open(f['filepath'], 'rb').read())
            name = f['filename']
            attachfile.add_header('Content-Disposition', 'attachment', filename=Header(name, 'utf-8').encode())
            encoders.encode_base64(attachfile)
            msg.attach(attachfile)
        except Exception as e:
            print("[emailops][attach failed][tm=%s]e:%s" % (f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}", e))

    # send
    retry = 0
    while retry < 5:
        try:
            smtp = SMTP_SSL(host_server)
            smtp.set_debuglevel(0)
            smtp.ehlo(host_server)
            smtp.login(fromaddress, password)
            smtp.sendmail(fromaddress, addresses + cc, msg.as_string())
            smtp.quit()
            print("[emailops][email sent][tm=%s][retry=%d]host:%s, port:%s, from:%s, to:%s, cc:%s, subject:%s, attach:%s"
              % (f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}", retry, host_server, inport, fromaddress, msg["to"], msg["cc"], msg["subject"],
                 attach_names)
              )
            break
        except Exception as e:
            print("[emailops][email send failed][tm=%s][retry=%d]host:%s, port:%s, from:%s, to:%s, cc:%s, subject:%s, attach:%s, err:"
              % (f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}", retry, host_server, inport, fromaddress, msg["to"], msg["cc"], msg["subject"],
                 attach_names),
                  e
              )
            retry += 1
            time.sleep(2 + retry)


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
    print(email_content)
    print((email_content[1]))
    print(email_content[0][0])
    email_content = email_content[0][1].decode()
    print(email_content)
    conn.close()
    conn.logout()

def receiveEmail2():
    # config
    config = configparser.ConfigParser()
    config.read(EmailConfig)
    email = config.get(ConfigSec, "fromaddress")
    password = config.get(ConfigSec, "password")
    pop3_server = config.get(ConfigSec, "host_server")

    # 连接到POP3 服务器
    server = poplib.POP3_SSL(pop3_server)
    # 可以打开或关闭调试信息
    server.set_debuglevel(1)
    # 可选：输出POP3服务器的欢迎文字
    print(server.getwelcome().decode('utf-8'))

    # 身份认证
    server.user(email)
    server.pass_(password)
    # stat()返回邮件数量和占用空间
    print('Messages: %s. Size: %s' % server.stat())
    # list()返回所有邮件的编号
    resp, mails, octets = server.list()
    # 可以查看返回的列表，类似[b'1 82923', b'2 2184', ...]
    print(mails)

    # 获取最新一封邮件, 注意索引号从1 开始
    index = len(mails)
    print(index)
    resp, lines, octets = server.retr(index)

    # lines 存储了邮件原始文本的每一行
    # 可以获得整个邮件的原始文本
    msg_content = b'\r\n'.join(lines).decode('utf-8')
    # 稍后解析邮件
    msg = Parser().parsestr(msg_content)

    # 可以根据邮件索引号直接从服务器删除邮件
    # server.dele(index)
    # 关闭连接
    server.quit()

# fixme: imbox should use master branch
def receiveEmail3(**kwargs):
    # config
    config = configparser.ConfigParser()
    config.read(EmailConfig)
    email = config.get(ConfigSec, "fromaddress")
    password = config.get(ConfigSec, "password")
    server = config.get(ConfigSec, "host_server")
    with Imbox(server, email, password, ssl=True) as imbox:
        # read messages
        all_inbox_messages = imbox.messages(**kwargs)
        res = list(all_inbox_messages)
        for uid, message in res:
            for attach in message.attachments:
                attach['filename'] = decodeAttachName(attach['filename'])
        return res

if __name__ == '__main__':
    addresses = ["iamnushead@gmail.com"]
    cc = []
    Subject = 'Python自动发送的邮件'  # 邮件标题
    content = "您好，这是使用python登录邮箱发送邮件的测试"
    attach = [
        {
            "filename": 'testdoc.docx',
            "filepath": "/Users/madgd/Downloads/test3/testdoc.docx",
        },
    ]
    # sendEmail(addresses, content, Subject, attach, cc)
    # receiveEmail()
    # receiveEmail2()
    res = receiveEmail3(uid__range='1598510969:*')
    for uid, message in res:
        print(uid)
        print(message.sent_from)
        for attach in message.attachments:
            print(attach['filename'])