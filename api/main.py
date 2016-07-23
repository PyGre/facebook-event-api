# -*- coding: utf-8 -*-

import os
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.autoreload
import tornado.log
import logging
from endpoints import MockRequestHandler, FacebookEventListHandler

# ------------------------------------------------------------------------------

class PyGreApplication(tornado.web.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.port = kwargs.get('port', 8000)
        self.access_token = kwargs['facebook_page_access_token'] # From config file.

    def start(self):
        try:
            self.listen(self.port)
            logger = logging.getLogger('tornado.general')
            logger.info('Listening on localhost:{}'.format(self.port))
            tornado.ioloop.IOLoop.current().start()
        except KeyboardInterrupt:
            logger = logging.getLogger('tornado.application')
            logger.critical('KeyboardInterrupt: Shutting down...')

def watchFiles(directory):
    for root, _, files in os.walk(directory):
        [tornado.autoreload.watch(root + '/' + f) for f in files]

# ------------------------------------------------------------------------------

def main():
    root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Define & parse command line options
    tornado.options.define('debug', default=False, help='Enable Debug mode')
    tornado.options.define('mock', default=False, help='Generate mock responses')
    tornado.options.define('cookie_secret', default='', help='Secret for encypting cookies')
    tornado.options.define('port', default=8000, help='Listening port')
    tornado.options.define('facebook_page_access_token', default='',
                           help='Facebook access token for the PyGre.io page (long lived)')
    try:
        tornado.options.parse_config_file(os.path.join(root_directory, 'config.py'))
    except FileNotFoundError:
        pass
    finally:
        tornado.options.parse_command_line()
        opt = tornado.options.options

    app = PyGreApplication(
        handlers=[
            (r'/', MockRequestHandler if opt.mock else FacebookEventListHandler),
        ],
        xsrf_cookies=True,
        **opt.as_dict()
    )

    if tornado.options.options.debug:
        tornado.log.enable_pretty_logging()

    app.start()

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
