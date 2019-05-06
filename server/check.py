#!/usr/bin/env pytthon
# -*- coding: utf-8 -*-  

from datetime import timedelta
import smtplib
import os
import sys
import dailykindle
import time
from datetime import date, timedelta

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
         Mail, Attachment, FileContent, FileName,
         FileType, Disposition, ContentId)
import base64


from_mail = 'liuwenmao@126.com'
to_mail = 'marvel1983@kindle.cn'
api_key='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'
tmp_dir = '/tmp/kindle'
kindle_gen = '../kindlegen/kindlegen'

feeds_file = sys.argv[1]
catagory = sys.argv[2]

print feeds_file
f = open(feeds_file, "r")
feeds = f.readlines()
f.close()


date = date.today().isoformat()
title = "Daily "+catagory+" "+date
feed_num = dailykindle.build(feeds, tmp_dir, title, timedelta(1))
if not feed_num == 0:
    dailykindle.mobi(tmp_dir+'/daily.opf', kindle_gen)
    
    
    date = time.strftime("%m/%d/%Y")
    
    message = Mail(
        from_email=from_mail,
        to_emails=to_mail,
        subject='Daily RSS'+ date,
        html_content='RSS DAILY ' + date)
    
    file_path = tmp_dir+'/daily.mobi'
    with open(file_path, 'rb') as f:
        data = f.read()
        f.close()
    encoded = base64.b64encode(data).decode()
    attachment = Attachment()
    attachment.file_content = FileContent(encoded)
    attachment.file_type = FileType('application/mobi')
    attachment.file_name = FileName("每日"+catagory+"RSS"+date+".mobi")
    attachment.disposition = Disposition('attachment')
    attachment.content_id = ContentId('DailyRSS')
    
    message.attachment = attachment 
    
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
    
    
    
