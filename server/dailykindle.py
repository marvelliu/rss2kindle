from datetime import date, timedelta
from shutil import copy
from os import path, listdir, system
import feedparser
from jinja2 import Environment, PackageLoader
import codecs
import re
import uuid
import urllib2
import os
import hashlib
import requests
import config
import resize


templates_env = Environment(loader=PackageLoader('dailykindle', 'templates'))
ROOT = path.dirname(path.abspath(__file__))


def download_file(url, local_file):
    request = requests.get(url, timeout=100, stream=True)

    try:
        with open(local_file, 'wb') as f:  
            for chunk in request.iter_content(1024 * 1024):
                f.write(chunk)
    except:
        pass


def update_link(content):
    reg = re.compile('src="(.*?\.(jpg|jpeg|png|gif|bmp|JPG|JPEG|PNG|GIF|BMP)(.*?))"')
    img_dir = config.tmp_dir + '/images/'
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
    imglist = re.findall(reg, content)
    print imglist
    for _img in imglist:
        ori_img = _img[0]
        img = ori_img.rstrip(_img[2])
        suffix = img.rsplit('.', 1)[1]
        f = img_dir + hashlib.md5(img.encode('utf-8')).hexdigest() +"."+suffix
        content = content.replace(ori_img, f)
        if os.path.exists(f) or os.path.exists(f+".origin"):
           print "file exists, skip %s"%f
           continue
        print "%s\t%s"%(img, f)
        download_file(img, f+".origin") 
    return content


def build(feeds_urls, output_dir, title, max_old=None):
    """
    Given a list of feeds URLs and the path of a directory, writes the necessary
    for building a MOBI document.

    max_old must be either None or a timedelta. It defines the maximum age of
    posts which should be considered.
    """

    # Convert max_old if needed.
    if max_old == None:
        max_old = timedelta.max

    # Give the feeds URLs to Feedparser to have nicely usable feed objects.
    print feeds_urls
    feeds = [feedparser.parse(feed_url) for feed_url in feeds_urls]
    #print feeds
    # Parse the feeds and grave useful information to build a structure
    # which will be passed to the templates.
    data = []

    ## Initialize some counters for the TOC IDs.
    ## We start counting at 2 because 1 is the TOC itself.
    feed_number = 1
    play_order = 1

    total_entry = 0
    for feed in feeds:
        feed_number += 1
        play_order += 1
        local = {
            'number': feed_number,
            'play_order': play_order,
            'entries': [],
            'title': feed.feed.title,
        }
        entry_number = 0
        for entry in feed.entries:
            # We don't want old posts, just fresh news.

            if date.today() - date(*entry.published_parsed[0:3]) > max_old:
                continue
            total_entry += 1


            play_order += 1
            entry_number += 1

            #import pdb
            #pdb.set_trace()
            try:
            	local_entry = {
                	'number': entry_number,
               		'play_order': play_order,
                	'title': entry.title,
                	'description': update_link(entry.description),
                	'content': update_link(entry.content[0].value),
            	}
	    except AttributeError:
                value = update_link(entry.summary_detail.value)
		local_entry = {
                        'number': entry_number,
                        'play_order': play_order,
                        'title': update_link(entry.title),
                        'description': update_link(entry.description),
                }
            local['entries'].append(local_entry)

        data.append(local)
    if total_entry == 0:
        #nothing, return
        return 0 
    # Wrap data and today's date in a dict to use the magic of **.
    wrap = {
        'date': date.today().isoformat(),
        'feeds': data,
        'title': title,
    }

    print output_dir

    # Render and output templates

    ## TOC (NCX)
    render_and_write('toc.xml', wrap, 'toc.ncx', output_dir)
    ## TOC (HTML)
    render_and_write('toc.html', wrap, 'toc.html', output_dir)
    ## OPF
    render_and_write('opf.xml', wrap, 'daily.opf', output_dir)
    ## Content
    for feed in data:
        render_and_write('feed.html', feed, '%s.html' % feed['number'], output_dir)

    # Copy the assets
    for name in listdir(path.join(ROOT, 'assets')):
        copy(path.join(ROOT, 'assets', name), path.join(output_dir, name))
    # copytree(path.join(ROOT, 'assets'), output_dir)
    return feed_number


def render_and_write(template_name, context, output_name, output_dir):
    """Render `template_name` with `context` and write the result in the file
    `output_dir`/`output_name`."""

    template = templates_env.get_template(template_name)
    f = codecs.open(path.join(output_dir, output_name), "w", "utf-8")
    ##f = open(path.join(output_dir, output_name), "w")
    f.write(template.render(**context))
    f.close()

def mobi(input_file, exec_path):
    """Execute the KindleGen binary to create a MOBI file."""
    system("%s %s" % (exec_path, input_file))

if __name__ == "__main__":
    from sys import argv, exit

    def usage():
        print("""DailyKindle usage:
python dailykindle.py <output dir> <day|week> <kindle_gen> <feed_url_1> [<feed_url_2> ...]""")

    if not len(argv) > 3:
        usage()
        exit(64)

    length = None
    if argv[2] == 'day':
        length = timedelta(1)
    elif argv[2] == 'week':
        length = timedelta(7)

    print("Running DailyKindle...")
    print("-> Generating files...")
    #print "argv[1]*****************" + argv[1]
    #for item in argv[1]:
    #    print "[[[[" + item + "]]]]"
    build(argv[4:], argv[1], "KindleDaily", length)

    print "resize "+config.tmp_dir + '/images/'
    resize.resize_dir(config.tmp_dir + '/images/')
    
    print("-> Build the MOBI file using KindleGen...")
    mobi(path.join(argv[1], 'daily.opf'), argv[3])
    print("Done")

