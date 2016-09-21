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

from nimbleclient.common import exceptions as exc
from nimbleclient.tests.unit import base


class TestHTTPExceptions(base.TestBase):

    def test_from_response(self):
        mock_resp = mock.Mock()
        mock_resp.status_code = 413
        mock_resp.json.return_value = {
            'entityTooLarge': {
                'code': 413,
                'message': 'Request Entity Too Large',
                'details': 'Error Details...',
            }
        }
        mock_resp.headers = {
            'Content-Type': 'application/json',
            'x-openstack-request-id': mock.sentinel.fake_request_id,
            'retry-after': mock.sentinel.fake_retry,
        }
        err = exc.from_response(mock_resp, 'POST', 'fake_url')
        self.assertIsInstance(err, exc.RequestEntityTooLarge)
        self.assertEqual(413, err.http_status)
        self.assertEqual('Request Entity Too Large', err.message)
        self.assertEqual('Error Details...', err.details)
        self.assertEqual(mock.sentinel.fake_request_id, err.request_id)
        self.assertEqual(mock.sentinel.fake_retry, err.retry_after)

    def test_from_response_webob_new_format(self):
        mock_resp = mock.Mock()
        mock_resp.status_code = 413
        mock_resp.json.return_value = {
            'code': 413,
            'message': 'Request Entity Too Large',
            'details': 'Error Details...',
        }
        mock_resp.headers = {
            'Content-Type': 'application/json',
            'x-openstack-request-id': mock.sentinel.fake_request_id,
            'retry-after': mock.sentinel.fake_retry,
        }
        err = exc.from_response(mock_resp, 'POST', 'fake_url')
        self.assertIsInstance(err, exc.RequestEntityTooLarge)
        self.assertEqual(413, err.http_status)
        self.assertEqual('Request Entity Too Large', err.message)
        self.assertEqual('Error Details...', err.details)
        self.assertEqual(mock.sentinel.fake_request_id, err.request_id)
        self.assertEqual(mock.sentinel.fake_retry, err.retry_after)
