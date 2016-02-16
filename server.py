#!/usr/bin/python

"""
Save this file as server.py
>>> python server.py 0.0.0.0 8001
serving on 0.0.0.0:8001

or simply

>>> python server.py
Serving on localhost:8000

You can use this to test GET and POST methods.

"""

import SimpleHTTPServer
import SocketServer
import logging
import cgi

import sys
import os


if len(sys.argv) > 2:
    PORT = int(sys.argv[2])
    I = sys.argv[1]
elif len(sys.argv) > 1:
    PORT = int(sys.argv[1])
    I = ""
else:
    PORT = 8000
    I = ""


class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        logging.warning("======= GET STARTED =======")
        # logging.warning(self.headers)
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        logging.warning("======= POST STARTED =======")
        # logging.warning(self.headers)
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        logging.warning("======= POST VALUES =======")
        # for item in form.list:
        #     logging.warning(item)

        session = form.getvalue('session')

        directory = 'experiments/'+session

        if not os.path.exists(directory):
            os.makedirs(directory)

        # this is to process the final questionnaire:
        if(form.getvalue('q') == 't'):
            header = ""
            values = ""

            for key in form.keys():
                header += str(key)+", "
                values += str(form.getvalue(str(key)))+", "

            with open("experiments/questionnaires.csv", "a") as text_file:
                    text_file.write(header+"\n")
                    text_file.write(values+"\n")

            # redirect to thank you page
            self.send_response(301)
            self.send_header('Location','http://localhost:8000/thanks.html')
            self.end_headers()

        # this process the randomized car json datasets
        else:
            data = form.getvalue('data')
            page = form.getvalue('page')

            with open(directory+"/"+page+".json", "w") as text_file:
                text_file.write(data)

            logging.warning("\n")
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

Handler = ServerHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "Serving at: http://%(interface)s:%(port)s" % dict(interface=I or "localhost", port=PORT)
httpd.serve_forever()
