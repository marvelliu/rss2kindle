#!/usr/bin/env python
from os import path, listdir, system
import os
from PIL import Image 

def resize_file(filename):
    f = filename.rsplit(".",1)[0]
    try:
        im = Image.open(filename)
        w, h = im.size 
        max_width = 400
        #print w,h
        if w > max_width: 
           nw = max_width 
           nh = nw * h/w
           #print nw,nh
        else:
            os.copy(filename, f)
            return

        im.thumbnail((nw,nh), Image.ANTIALIAS)
        im.save(f, quality=80)
        #os.remove(filename)
    except IOError,e:
        print "cannot create thumbnail for '%s'" % filename 
        print e
    


def resize_dir(image_dir):
    for f in listdir(image_dir):
        if f.endswith(".origin"):
            resize_file(image_dir+"/"+f)

if __name__ == "__main__":
    from sys import argv, exit

    def usage():
        print("""resize usage:
python resize.py <dir>""")

    if not len(argv) == 2:
        usage()
        exit(64)

    img_dir = argv[1]
    if not os.path.exists(img_dir):
        print "%s not exist"
        exit(63)
    resize_dir(img_dir)
