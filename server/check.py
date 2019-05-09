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
import config
import resize

feeds_file = sys.argv[1]
catagory = sys.argv[2]

print feeds_file
f = open(feeds_file, "r")
feeds = f.readlines()
f.close()


date = date.today().isoformat()
title = "Daily "+catagory+" "+date
feed_num = dailykindle.build(feeds, config.tmp_dir, title, timedelta(1))
if not feed_num == 0:
    print "resize "+config.tmp_dir + '/images/'
    resize.resize_dir(config.tmp_dir + '/images/')

    dailykindle.mobi(config.tmp_dir+'/daily.opf', config.kindle_gen)
    
    
    date = time.strftime("%m/%d/%Y")
    
    message = Mail(
        from_email=config.from_mail,
        to_emails=config.to_mail,
        subject='Daily RSS'+ date,
        html_content='RSS DAILY ' + date)
    
    file_path = config.tmp_dir+'/daily.mobi'
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
        sg = SendGridAPIClient(config.api_key)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
    
    
    
