# Copyright (C) 2014 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import yaml
from six.moves.urllib import request

from nodepool import tests
from nodepool import zk


class TestWebApp(tests.DBTestCase):
    log = logging.getLogger("nodepool.TestWebApp")

    def test_image_list(self):
        configfile = self.setup_config('node.yaml')
        pool = self.useNodepool(configfile, watermark_sleep=1)
        self.useBuilder(configfile)
        pool.start()
        webapp = self.useWebApp(pool, port=0)
        webapp.start()
        port = webapp.server.socket.getsockname()[1]

        self.waitForImage('fake-provider', 'fake-image')
        self.waitForNodes('fake-label')

        req = request.Request(
            "http://localhost:%s/image-list" % port)
        f = request.urlopen(req)
        self.assertEqual(f.info().get('Content-Type'),
                         'text/plain; charset=UTF-8')
        data = f.read()
        self.assertTrue('fake-image' in data.decode('utf8'))

    def test_image_list_json(self):
        configfile = self.setup_config('node.yaml')
        pool = self.useNodepool(configfile, watermark_sleep=1)
        self.useBuilder(configfile)
        pool.start()
        webapp = self.useWebApp(pool, port=0)
        webapp.start()
        port = webapp.server.socket.getsockname()[1]

        self.waitForImage('fake-provider', 'fake-image')
        self.waitForNodes('fake-label')

        req = request.Request(
            "http://localhost:%s/image-list.json" % port)
        f = request.urlopen(req)
        self.assertEqual(f.info().get('Content-Type'),
                         'application/json')
        data = f.read()
        objs = json.loads(data.decode('utf8'))
        self.assertDictContainsSubset({'id': '0000000001',
                                       'image': 'fake-image',
                                       'provider': 'fake-provider',
                                       'state': 'ready'}, objs[0])

    def test_dib_image_list_json(self):
        configfile = self.setup_config('node.yaml')
        pool = self.useNodepool(configfile, watermark_sleep=1)
        self.useBuilder(configfile)
        pool.start()
        webapp = self.useWebApp(pool, port=0)
        webapp.start()
        port = webapp.server.socket.getsockname()[1]

        self.waitForImage('fake-provider', 'fake-image')
        self.waitForNodes('fake-label')

        req = request.Request(
            "http://localhost:%s/dib-image-list.json" % port)
        f = request.urlopen(req)
        self.assertEqual(f.info().get('Content-Type'),
                         'application/json')
        data = f.read()
        objs = json.loads(data.decode('utf8'))
        # make sure this is valid json and has some of the
        # non-changing keys
        self.assertDictContainsSubset({'id': 'fake-image-0000000001',
                                       'formats': ['qcow2'],
                                       'state': 'ready'}, objs[0])

    def test_node_list_json(self):
        configfile = self.setup_config('node.yaml')
        pool = self.useNodepool(configfile, watermark_sleep=1)
        self.useBuilder(configfile)
        pool.start()
        webapp = self.useWebApp(pool, port=0)
        webapp.start()
        port = webapp.server.socket.getsockname()[1]

        self.waitForImage('fake-provider', 'fake-image')
        self.waitForNodes('fake-label')

        req = request.Request(
            "http://localhost:%s/node-list.json" % port)
        f = request.urlopen(req)
        self.assertEqual(f.info().get('Content-Type'),
                         'application/json')
        data = f.read()
        objs = json.loads(data.decode('utf8'))
        self.assertDictContainsSubset({'id': '0000000000',
                                       'ipv6': '',
                                       'label': 'fake-label',
                                       'locked': 'unlocked',
                                       'provider': 'fake-provider',
                                       'public_ipv4': 'fake',
                                       'state': 'ready'}, objs[0])
        # specify valid node_id
        req = request.Request(
            "http://localhost:%s/node-list.json?node_id=%s" % (port,
                                                               '0000000000'))
        f = request.urlopen(req)
        self.assertEqual(f.info().get('Content-Type'),
                         'application/json')
        data = f.read()
        objs = json.loads(data.decode('utf8'))
        self.assertDictContainsSubset({'id': '0000000000',
                                       'ipv6': '',
                                       'label': 'fake-label',
                                       'locked': 'unlocked',
                                       'provider': 'fake-provider',
                                       'public_ipv4': 'fake',
                                       'state': 'ready'}, objs[0])
        # node_id not found
        req = request.Request(
            "http://localhost:%s/node-list.json?node_id=%s" % (port,
                                                               '999999'))
        f = request.urlopen(req)
        self.assertEqual(f.info().get('Content-Type'),
                         'application/json')
        data = f.read()
        objs = json.loads(data.decode('utf8'))
        self.assertEqual(0, len(objs), objs)

    def test_label_list_json(self):
        configfile = self.setup_config('node.yaml')
        pool = self.useNodepool(configfile, watermark_sleep=1)
        self.useBuilder(configfile)
        pool.start()
        webapp = self.useWebApp(pool, port=0)
        webapp.start()
        port = webapp.server.socket.getsockname()[1]

        self.waitForImage('fake-provider', 'fake-image')
        self.waitForNodes('fake-label')

        req = request.Request(
            "http://localhost:%s/label-list.json" % port)
        f = request.urlopen(req)
        self.assertEqual(f.info().get('Content-Type'),
                         'application/json')
        data = f.read()
        objs = json.loads(data.decode('utf8'))
        self.assertEqual(['fake-label'], objs)

    def test_request_list_json(self):
        configfile = self.setup_config('node.yaml')
        pool = self.useNodepool(configfile, watermark_sleep=1)
        self.useBuilder(configfile)
        pool.start()
        webapp = self.useWebApp(pool, port=0)
        webapp.start()
        port = webapp.server.socket.getsockname()[1]

        self.waitForImage('fake-provider', 'fake-image')
        self.waitForNodes('fake-label')
        req = zk.NodeRequest()
        req.state = zk.PENDING   # so it will be ignored
        req.node_types = ['fake-label']
        req.requestor = 'test_request_list'
        self.zk.storeNodeRequest(req)

        http_req = request.Request(
            "http://localhost:%s/request-list.json" % port)
        f = request.urlopen(http_req)
        self.assertEqual(f.info().get('Content-Type'),
                         'application/json')
        data = f.read()
        objs = json.loads(data.decode('utf8'))
        self.assertDictContainsSubset({'node_types': ['fake-label'],
                                       'requestor': 'test_request_list', },
                                      objs[0])

    def test_webapp_config(self):
        configfile = self.setup_config('webapp.yaml')
        config = yaml.safe_load(open(configfile))
        self.assertEqual(config['webapp']['port'], 8080)
        self.assertEqual(config['webapp']['listen_address'], '127.0.0.1')
