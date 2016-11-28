#!/usr/bin/python

import logging
import cgi

import sys
import os

# enable debugging
import cgitb
cgitb.enable()

print 'Content-Type: text/html'
print 'Status: 200 OK'
print

print '<!DOCTYPE html>'
print '<meta charset="utf-8">'
print '<link rel="stylesheet" href="css/pure-min.css" />'
print '<link rel="stylesheet" href="css/style.css" />'
print '<body>'

session = "1477907679284"

for i in range(1,12):

    f = "experiments/"+session+"/"+str(i)+".json"

    try:
        os.remove(f)
        print f + " deleted<br />"
    except Exception as e:
        logging.error(type(e))
        logging.error(e.args)
        logging.error(e)
        print f + " does not exist<br />"

# and remove the folder:
f = "experiments/"+session

try:
    os.remove(f+"/log.txt")
except Exception as e:
    logging.error(type(e))
    logging.error(e.args)
    logging.error(e)
    print f + " does not exist or could not be deleted<br />"

try:
    os.rmdir(f)
    print f + " folder deleted<br />"
except Exception as e:
    logging.error(type(e))
    logging.error(e.args)
    logging.error(e)
    print f + " folder does not exist or could not be deleted<br />"

print '<h1>Done.</h1> </body>'
