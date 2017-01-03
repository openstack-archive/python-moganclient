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

from moganclient.common import exceptions as exc
from moganclient.tests.unit import base


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
            'retry-after': 10,
        }
        err = exc.from_response(mock_resp, 'POST', 'fake_url')

        self.assertIsInstance(err, exc.RequestEntityTooLarge)
        self.assertEqual(413, err.status_code)
        self.assertEqual('POST', err.method)
        self.assertEqual('fake_url', err.url)
        self.assertEqual('Request Entity Too Large (HTTP 413) (Request-ID: '
                         'sentinel.fake_request_id)', err.message)
        self.assertEqual('Error Details...', err.details)
        self.assertEqual(10, err.retry_after)
        self.assertEqual(mock.sentinel.fake_request_id, err.request_id)

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
            'retry-after': 10,
        }
        err = exc.from_response(mock_resp, 'POST', 'fake_url')

        self.assertIsInstance(err, exc.RequestEntityTooLarge)
        self.assertEqual(413, err.status_code)
        self.assertEqual('POST', err.method)
        self.assertEqual('fake_url', err.url)
        self.assertEqual('Request Entity Too Large (HTTP 413) (Request-ID: '
                         'sentinel.fake_request_id)', err.message)
        self.assertEqual('Error Details...', err.details)
        self.assertEqual(10, err.retry_after)
        self.assertEqual(mock.sentinel.fake_request_id, err.request_id)

    def test_from_response_pecan_response_format(self):
        mock_resp = mock.Mock()
        mock_resp.status_code = 400
        mock_resp.json.return_value = {
            u'error_message': u'{"debuginfo": null, '
                              u'"faultcode": "Client", '
                              u'"faultstring": "Error Details..."}'
        }
        mock_resp.headers = {
            'Content-Type': 'application/json',
            'Openstack-Request-Id': 'fake_request_id',
            'Content-Length': '216',
            'Connection': 'keep-alive',
            'Date': 'Mon, 26 Dec 2016 06:59:04 GMT'
        }
        err = exc.from_response(mock_resp, 'POST', 'fake_url')

        self.assertEqual(400, err.status_code)
        self.assertEqual('POST', err.method)
        self.assertEqual('fake_url', err.url)
        self.assertEqual(
            'Error Details... (HTTP 400) (Request-ID: fake_request_id)',
            err.message)
        self.assertEqual('fake_request_id', err.request_id)
