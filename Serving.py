#!/usr/bin/env python

import os
import logging
import sys
import traceback
import json

import tornado.escape
import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line
from tornado import gen
from tornado import escape
# from tornado.concurrent import run_on_executor
# from concurrent.futures import ThreadPoolExecutor

import Compute
from Analyze import VaingloryAI

logger = logging

define("port", default=3000, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")
define("config_file", default="platform.conf", help="specify the config file")



class BaseHandler(tornado.web.RequestHandler):
    SUCCESS = {"code": 0, "message": "success"}
    ERROR = {"code": 1, "message": "error"}
    BAD_REQUEST = {"code": 2, "message": "bad request"}


class Status(BaseHandler):
    @gen.coroutine
    def get(self):
        self.write(self.SUCCESS)

class VS(BaseHandler):
    @gen.coroutine
    def get(self):
        try:
            compare = self.get_argument("vs")

        except Exception as e:
            logger.error("%s\n%s" % (str(e), traceback.format_exc()))
            logger.debug(self.request.__dict__)
            ret = self.BAD_REQUEST
            self.write(ret)
            return

        try:
            ret, ok = VaingloryAI.predict(str(compare))
            if not ok:
                ret = self.ERROR
        except Exception as e:
            logger.error("%s\n%s" % (str(e), traceback.format_exc()))
            ret = self.ERROR

        self.write(ret)


def run():
    argv = sys.argv
    parse_command_line()

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    from vaingloryai import parseConfig
    config = parseConfig(options)

    Compute.DATA.initialize(config)
    hooks = config.get("general", "hooks").split(',')

    from Analyze import VaingloryAI
    VaingloryAI.setup(config)

    if 'twitter' in hooks:
        import TwitterHook
        TwitterHook.TwitterHooking.setup(config)

    paths = [
        (r"/status", Status),
        (r"/vs", VS)
    ]

    static_path = config.get("general", "image_dir")
    app = tornado.web.Application(paths,
                                  cookie_secret="udxas-efasx-ase323fs-3efsxf3eFdes",
                                  xsrf_cookies=False,  # TODO: Will set as True
                                  static_path = static_path,
                                  debug=options.debug,
                                  )

    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    run()
