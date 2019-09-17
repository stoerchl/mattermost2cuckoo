#!/usr/bin/env python
# Copyright (c) 2019 @stoerchl
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Usage:
# - python mattermost2cuckoo.py start mattermost2cuckoo.conf
# - python mattermost2cuckoo.py stop mattermost2cuckoo.conf
# - python mattermost2cuckoo.py restart mattermost2cuckoo.conf
#

import sys
import configparser
import multiprocessing
import urllib.parse
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from daemon import Daemon


def make_handler_class(config):

    class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self._config = config
            super(SimpleHTTPRequestHandler, self).__init__(*args, **kwargs)

        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Hello, world!')

        def do_POST(self):
            if self.path == "/cuckoo-submit":
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)

                try:
                    data = urllib.parse.parse_qs(body.decode('ascii'))

                    if "token" in data:
                        if str(data["token"][0]) == str(self._config['mattermost_token']):
                            if "text" in data:
                                sha256 = data["text"][0]

                                with open(str(self._config['sample_folder']) + str(sha256), "rb") as sample:
                                    files = {"file": (sha256, sample)}
                                    headers = {"Authorization": "Basic " + str(self._config['basic_auth_token'])}
                                    r = requests.post(str(self._config['rest_url']), headers=headers, files=files)

                                task_id = r.json()["task_id"]
                                self.send_response(r.status_code)
                                self.end_headers()

                                try:
                                    response = BytesIO()
                                    if r.status_code == 200:
                                        response.write(b'Submitted File to Cuckoo. Task-ID: ' + str(task_id).encode("utf-8"))
                                    else:
                                        response.write(b'Submitting File to Cuckoo Failed!')
                                    self.wfile.write(response.getvalue())
                                except:
                                    pass

                                return None

                    self.send_response(500)
                    self.end_headers()

                except:
                    self.send_response(500)
                    self.end_headers()


    return SimpleHTTPRequestHandler


class WebListener(object):

    def run(self, config):
        HandlerClass = make_handler_class(config)
        httpd = HTTPServer((str(config['listening_ip']), int(config['listening_port'])), HandlerClass)
        httpd.serve_forever()


class ELDaemon(Daemon):
    _config = None

    def __init__(self, pid_file, config):
        self._config = config
        Daemon.__init__(self, pid_file)

    def set_config(self, config):
        self.__config = config

    def run(self):
        web_listener = WebListener()
        web_listener.run(self._config)


def worker(arguments):
    s = arguments[0]
    x = arguments[1]
    config = arguments[2]

    daemon = ELDaemon('/tmp/daemon-web-listener_'+str(s)+'.pid', config)

    if 'start' == x:
        daemon.start()
    elif 'stop' == x:
        daemon.stop()
    elif 'restart' == x:
        daemon.restart()
    else:
        print("unknown command")
        sys.exit(2)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        configParser = configparser.RawConfigParser()
        configParser.read(sys.argv[2])
        jobs = []

        for s in configParser.sections():
            cfg=dict()
            for o in configParser.options(s):
                cfg[o] = configParser.get(s, o)

            arguments = [s, sys.argv[1], cfg]
            p = multiprocessing.Process(target=worker, args=(arguments, ))
            jobs.append(p)
            p.start()

        sys.exit(0)
    else:
        print("usage: %s start <config_name>|stop <config_name>|restart <config_name>" % sys.argv[0])
        sys.exit(2)
