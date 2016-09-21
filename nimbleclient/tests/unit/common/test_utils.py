#   Copyright 2016 Huawei, Inc. All rights reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import mock

from nimbleclient.common import utils
from nimbleclient.tests.unit import base


class TestUtils(base.TestBase):

    def test_get_response_body(self):
        resp = mock.Mock()
        resp.headers = {'Content-Type': 'application/json'}
        resp.json.return_value = mock.sentinel.fake_body
        body = utils.get_response_body(resp)
        self.assertEqual(mock.sentinel.fake_body, body)

    def test_get_response_body_not_json(self):
        resp = mock.Mock()
        resp.headers = {'Content-Type': 'application/xml'}
        body = utils.get_response_body(resp)
        self.assertIsNone(body)

    def test_get_response_body_value_error(self):
        resp = mock.Mock()
        resp.content = mock.sentinel.fake_content
        resp.headers = {'Content-Type': 'application/json'}
        resp.json.side_effect = ValueError('json format error.')
        body = utils.get_response_body(resp)
        self.assertEqual(mock.sentinel.fake_content, body)
