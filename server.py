#!/usr/bin/python

import logging
import cgi

import sys
import os

# enable debugging
import cgitb
cgitb.enable()

# logging.warning("======= POST STARTED =======")
# logging.warning(self.headers)
form = cgi.FieldStorage()
# logging.warning("======= POST VALUES =======")
# for item in form.list:
#     logging.warning(item)

session = form.getvalue('session')

directory = 'experiments/'+session


try:
    if not os.path.exists(directory):
        os.makedirs(directory, 0777)
    # else:
    #     os.chmod(directory, 0777)   # just in case
except Exception as e:
    logging.error(type(e))
    logging.error(e.args)
    logging.error(e)

# this is to process the final questionnaire:
if(form.getvalue('q') == 't'):

    csv = "experiments/questionnaires.csv"

    header = ""
    values = ""

    for key in form.keys():
        header += str(key)+", "
        values += str(form.getvalue(str(key)))+", "

    with open(csv, "a") as text_file:
            text_file.write(header+"\n")
            text_file.write(values+"\n")

    os.chmod(csv, 0777)

    print 'Content-Type: text/html'
    print 'Status: 200 OK'
    print
    print '<!DOCTYPE html>'
    print '<meta charset="utf-8">'
    print '<link rel="stylesheet" href="css/pure-min.css" />'
    print '<link rel="stylesheet" href="css/style.css" />'
    print '<body> <h1>Thank you.</h1> </body>'

# this processes the randomized car json datasets
else:
    data = form.getvalue('data')
    page = form.getvalue('page')

    json = directory+"/"+page+".json"

    with open(json, "w") as text_file:
        text_file.write(data)

    os.chmod(json, 0777)

    SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
