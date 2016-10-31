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
if (form.getvalue('q') == 't'):

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
    print '<body>'
    print '<div id="fb-root"></div>'
    print '<script>(function(d, s, id) {'
    print 'var js, fjs = d.getElementsByTagName(s)[0];'
    print 'if (d.getElementById(id)) return;'
    print 'js = d.createElement(s); js.id = id;'
    print 'js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.8&appId=225759177445380";'
    print 'fjs.parentNode.insertBefore(js, fjs);'
    print '}(document, "script", "facebook-jssdk"));</script>'
    print '<h1 style ="margin-top: 100px">Thank you.</h1>'
    print '<p style="text-align: center"><a href="https://twitter.com/share" class="twitter-share-button" data-text="Help @carstenkessler do some research on visualizations of uncertainty by participating in this quick online test:" data-url="http://carsten.io/uncertainty" data-lang="en" data-show-count="false">Tweet</a></p><div class="fb-share-button" style="float: left"><a class="fb-xfbml-parse-ignore" target="_blank" href="https://www.facebook.com/sharer/sharer.php?u&amp;src=sdkpreparse">Share</a></div><script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>'
    print '</body>'

# # process the timing and coords of a single page
elif (form.getvalue('s') == 't'):

    log = directory+'/log.txt'
    logtxt = str(form.getvalue('page'))+', '+str(form.getvalue('time'))+', '+str(form.getvalue('x'))+', '+str(form.getvalue('y'))+'\n'

    logging.warning(logtxt)

    with open(log, "a") as text_file:
        text_file.write(logtxt)

    os.chmod(log, 0777)

    SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

# this processes the randomized car json datasets
else:
    data = form.getvalue('data')
    page = form.getvalue('page')

    json = directory+"/"+page+".json"

    with open(json, "w") as text_file:
        text_file.write(data)

    os.chmod(json, 0777)

    SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
