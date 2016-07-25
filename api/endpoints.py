# -*- coding: utf-8 -*-

import tornado.web
import tornado.gen
import tornado.escape
import tornado.concurrent
import random
import datetime
import tornado.httpclient
import urllib.parse

# ------------------------------------------------------------------------------

class ApiRequestHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        if 'message' not in kwargs:
            if status_code == 405:
                kwargs['message'] = 'Invalid HTTP method.'
            else:
                kwargs['message'] = 'Unknown error {}.'.format(status_code)
        self.response = kwargs
        self.write(tornado.escape.json_encode(self.response))

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'GET')

# ------------------------------------------------------------------------------

class MockRequestHandler(ApiRequestHandler):
    def get(self, *args, **kwargs):
        num_events = random.randint(0, 8)
        data = [
            self.generateMockEvent() for _ in range(0, num_events)
        ]
        self.write(tornado.escape.json_encode(data))

    @staticmethod
    def generateMockEvent():
        str_choices = ('Foo', 'Bar', 'Egg', 'Spam')

        def generateMockId():
            return str(int(random.random() * 100000000.))

        return {
            'id':           generateMockId(),
            'name':         random.choice(str_choices),
            'description':  random.choice(str_choices),
            'start_time':   datetime.datetime.now().isoformat(),
            'end_time':     datetime.datetime.now().isoformat(),
            'attending':    random.randint(0, 42),
            'interested':   random.randint(0, 42),
            'place': {
                'id':       generateMockId(),
                'name':     random.choice(str_choices),
            }
        }

# ------------------------------------------------------------------------------

class FacebookEventListHandler(MockRequestHandler):

    async def get(self, *args, **kwargs):
        page_id = '1026070194112923'
        events = await self._fetch_page_events(page_id)
        data = []
        for event in events:
            data.append(await self._complete_event_data(event))
        self.write(tornado.escape.json_encode(data))

    # --

    async def _fetch_page_events(self, page_id):
        url = self._generate_api_url('{page}/events'.format(page=page_id))
        http_client = tornado.httpclient.AsyncHTTPClient()
        try:
            response = await http_client.fetch(url)
            data = tornado.escape.json_decode(response.body.decode('utf-8'))
            events = data.get('data', []) # ignore paging for now
            return events
        except tornado.httpclient.HTTPError as e:
            # HTTPError is raised for non-200 responses; the response
            # can be found in e.response.
            print("Error: " + str(e))
        except Exception as e:
            # Other errors are possible, such as IOError.
            print("Error: " + str(e))
        return []

    async def _complete_event_data(self, event_data):
        url = self._generate_api_url('{event}'.format(event=event_data['id']),
                                     fields='attending_count,interested_count')
        http_client = tornado.httpclient.AsyncHTTPClient()
        try:
            response = await http_client.fetch(url)
            data = tornado.escape.json_decode(response.body.decode('utf-8'))
            return {
                **event_data,
                'attending':    data.get('attending_count'),
                'interested':   data.get('interested_count'),
            }
        except tornado.httpclient.HTTPError as e:
            # HTTPError is raised for non-200 responses; the response
            # can be found in e.response.
            print("Error: " + str(e))
        except Exception as e:
            # Other errors are possible, such as IOError.
            print("Error: " + str(e))
        return { **event_data,  'attending': 0, 'interested': 0 }

    def _generate_api_url(self, node, **kwargs):
        kwargs['access_token'] = self.application.access_token
        args = urllib.parse.urlencode(kwargs)
        return 'https://graph.facebook.com/v2.7/' + node + '?' + args
