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


import socket

from keystoneauth1 import adapter
import mock
from osc_lib.tests import fakes as osc_fakes
from oslo_serialization import jsonutils
import six

from moganclient.common import exceptions as exc
from moganclient.common import http
from moganclient.common import utils
from moganclient.tests.unit import base
from moganclient.tests.unit import fakes


@mock.patch('moganclient.common.http.requests.request')
class TestHttpClient(base.TestBase):

    def setUp(self):
        super(TestHttpClient, self).setUp()

    def test_http_raw_request(self, mock_request):
        headers = {'User-Agent': 'python-moganclient',
                   'Content-Type': 'application/octet-stream'}
        mock_request.return_value = fakes.FakeHTTPResponse(200, 'OK', {}, '')
        client = http.HTTPClient('http://example.com:6688')
        resp, body = client.raw_request('GET', '/prefix')
        self.assertEqual(200, resp.status_code)
        self.assertEqual('', ''.join([x for x in resp.content]))
        mock_request.assert_called_once_with('GET',
                                             'http://example.com:6688/prefix',
                                             allow_redirects=False,
                                             headers=headers)

    def test_token_or_credentials(self, mock_request):
        # Record a 200
        fake200 = fakes.FakeHTTPResponse(200, 'OK', {}, '')
        mock_request.side_effect = [fake200, fake200, fake200]

        # Replay, create client, assert
        client = http.HTTPClient('http://example.com:6688')
        resp, body = client.raw_request('GET', '')
        self.assertEqual(200, resp.status_code)

        client.username = osc_fakes.USERNAME
        client.password = osc_fakes.PASSWORD
        resp, body = client.raw_request('GET', '')
        self.assertEqual(200, resp.status_code)

        client.auth_token = osc_fakes.AUTH_TOKEN
        resp, body = client.raw_request('GET', '')
        self.assertEqual(200, resp.status_code)

        # no token or credentials
        mock_request.assert_has_calls([
            mock.call('GET', 'http://example.com:6688',
                      allow_redirects=False,
                      headers={'User-Agent': 'python-moganclient',
                               'Content-Type': 'application/octet-stream'}),
            mock.call('GET', 'http://example.com:6688',
                      allow_redirects=False,
                      headers={'User-Agent': 'python-moganclient',
                               'X-Auth-Key': osc_fakes.PASSWORD,
                               'X-Auth-User': osc_fakes.USERNAME,
                               'Content-Type': 'application/octet-stream'}),
            mock.call('GET', 'http://example.com:6688',
                      allow_redirects=False,
                      headers={'User-Agent': 'python-moganclient',
                               'X-Auth-Token': osc_fakes.AUTH_TOKEN,
                               'Content-Type': 'application/octet-stream'})
        ])

    def test_region_name(self, mock_request):
        # Record a 200
        fake200 = fakes.FakeHTTPResponse(200, 'OK', {}, '')
        mock_request.return_value = fake200

        client = http.HTTPClient('http://example.com:6688')
        client.region_name = osc_fakes.REGION_NAME
        resp, body = client.raw_request('GET', '')
        self.assertEqual(200, resp.status_code)

        mock_request.assert_called_once_with(
            'GET', 'http://example.com:6688',
            allow_redirects=False,
            headers={'X-Region-Name': osc_fakes.REGION_NAME,
                     'User-Agent': 'python-moganclient',
                     'Content-Type': 'application/octet-stream'})

    def test_http_json_request(self, mock_request):
        # Record a 200
        mock_request.return_value = fakes.FakeHTTPResponse(
            200, 'OK', {'Content-Type': 'application/json'}, '{}')

        client = http.HTTPClient('http://example.com:6688')
        resp, body = client.json_request('GET', '')
        self.assertEqual(200, resp.status_code)
        self.assertEqual({}, body)

        mock_request.assert_called_once_with(
            'GET', 'http://example.com:6688',
            allow_redirects=False,
            headers={'Content-Type': 'application/json',
                     'Accept': 'application/json',
                     'User-Agent': 'python-moganclient'})

    def test_http_json_request_argument_passed_to_requests(self, mock_request):
        """Check that we have sent the proper arguments to requests."""
        # Record a 200
        mock_request.return_value = fakes.FakeHTTPResponse(
            200, 'OK', {'Content-Type': 'application/json'}, '{}')

        client = http.HTTPClient('http://example.com:6688')
        client.verify_cert = True
        client.cert_file = 'RANDOM_CERT_FILE'
        client.key_file = 'RANDOM_KEY_FILE'
        client.auth_url = osc_fakes.AUTH_URL
        resp, body = client.json_request('POST', '', data='text')
        self.assertEqual(200, resp.status_code)
        self.assertEqual({}, body)

        mock_request.assert_called_once_with(
            'POST', 'http://example.com:6688',
            allow_redirects=False,
            cert=('RANDOM_CERT_FILE', 'RANDOM_KEY_FILE'),
            verify=True,
            data='"text"',
            headers={'Content-Type': 'application/json',
                     'Accept': 'application/json',
                     'X-Auth-Url': osc_fakes.AUTH_URL,
                     'User-Agent': 'python-moganclient'})

    def test_http_json_request_w_req_body(self, mock_request):
        # Record a 200
        mock_request.return_value = fakes.FakeHTTPResponse(
            200, 'OK', {'Content-Type': 'application/json'}, '{}')

        client = http.HTTPClient('http://example.com:6688')
        resp, body = client.json_request('POST', '', data='test-body')
        self.assertEqual(200, resp.status_code)
        self.assertEqual({}, body)
        mock_request.assert_called_once_with(
            'POST', 'http://example.com:6688',
            data='"test-body"',
            allow_redirects=False,
            headers={'Content-Type': 'application/json',
                     'Accept': 'application/json',
                     'User-Agent': 'python-moganclient'})

    def test_http_json_request_non_json_resp_cont_type(self, mock_request):
        # Record a 200
        mock_request.return_value = fakes.FakeHTTPResponse(
            200, 'OK', {'Content-Type': 'not/json'}, '{}')

        client = http.HTTPClient('http://example.com:6688')
        resp, body = client.json_request('POST', '', data='test-data')
        self.assertEqual(200, resp.status_code)
        self.assertIsNone(body)
        mock_request.assert_called_once_with(
            'POST', 'http://example.com:6688', data='"test-data"',
            allow_redirects=False,
            headers={'Content-Type': 'application/json',
                     'Accept': 'application/json',
                     'User-Agent': 'python-moganclient'})

    def test_http_json_request_invalid_json(self, mock_request):
        # Record a 200
        mock_request.return_value = fakes.FakeHTTPResponse(
            200, 'OK', {'Content-Type': 'application/json'}, 'invalid-json')

        client = http.HTTPClient('http://example.com:6688')
        resp, body = client.json_request('GET', '')
        self.assertEqual(200, resp.status_code)
        self.assertEqual('invalid-json', body)
        mock_request.assert_called_once_with(
            'GET', 'http://example.com:6688',
            allow_redirects=False,
            headers={'Content-Type': 'application/json',
                     'Accept': 'application/json',
                     'User-Agent': 'python-moganclient'})

    def test_http_json_request_redirect_delete(self, mock_request):
        mock_request.side_effect = [
            fakes.FakeHTTPResponse(
                302, 'Found',
                {'location': 'http://example.com:6688/foo/bar'},
                ''),
            fakes.FakeHTTPResponse(
                200, 'OK',
                {'Content-Type': 'application/json'},
                '{}')]

        client = http.HTTPClient('http://example.com:6688/foo')
        resp, body = client.json_request('DELETE', '')

        self.assertEqual(200, resp.status_code)
        mock_request.assert_has_calls([
            mock.call('DELETE', 'http://example.com:6688/foo',
                      allow_redirects=False,
                      headers={'Content-Type': 'application/json',
                               'Accept': 'application/json',
                               'User-Agent': 'python-moganclient'}),
            mock.call('DELETE', 'http://example.com:6688/foo/bar',
                      allow_redirects=False,
                      headers={'Content-Type': 'application/json',
                               'Accept': 'application/json',
                               'User-Agent': 'python-moganclient'})
        ])

    def test_http_json_request_redirect_post(self, mock_request):
        mock_request.side_effect = [
            fakes.FakeHTTPResponse(
                302, 'Found',
                {'location': 'http://example.com:6688/foo/bar'},
                ''),
            fakes.FakeHTTPResponse(
                200, 'OK',
                {'Content-Type': 'application/json'},
                '{}')]

        client = http.HTTPClient('http://example.com:6688/foo')
        resp, body = client.json_request('POST', '')

        self.assertEqual(200, resp.status_code)
        mock_request.assert_has_calls([
            mock.call('POST', 'http://example.com:6688/foo',
                      allow_redirects=False,
                      headers={'Content-Type': 'application/json',
                               'Accept': 'application/json',
                               'User-Agent': 'python-moganclient'}),
            mock.call('POST', 'http://example.com:6688/foo/bar',
                      allow_redirects=False,
                      headers={'Content-Type': 'application/json',
                               'Accept': 'application/json',
                               'User-Agent': 'python-moganclient'})
        ])

    def test_http_json_request_redirect_put(self, mock_request):
        mock_request.side_effect = [
            fakes.FakeHTTPResponse(
                302, 'Found',
                {'location': 'http://example.com:6688/foo/bar'},
                ''),
            fakes.FakeHTTPResponse(
                200, 'OK',
                {'Content-Type': 'application/json'},
                '{}')]

        client = http.HTTPClient('http://example.com:6688/foo')
        resp, body = client.json_request('PUT', '')

        self.assertEqual(200, resp.status_code)
        mock_request.assert_has_calls([
            mock.call('PUT', 'http://example.com:6688/foo',
                      allow_redirects=False,
                      headers={'Content-Type': 'application/json',
                               'Accept': 'application/json',
                               'User-Agent': 'python-moganclient'}),
            mock.call('PUT', 'http://example.com:6688/foo/bar',
                      allow_redirects=False,
                      headers={'Content-Type': 'application/json',
                               'Accept': 'application/json',
                               'User-Agent': 'python-moganclient'})
        ])

    def test_http_json_request_redirect_diff_location(self, mock_request):
        mock_request.side_effect = [
            fakes.FakeHTTPResponse(
                302, 'Found',
                {'location': 'http://example.com:6688/diff_lcation'},
                ''),
            fakes.FakeHTTPResponse(
                200, 'OK',
                {'Content-Type': 'application/json'},
                '{}')]

        client = http.HTTPClient('http://example.com:6688/foo')
        resp, body = client.json_request('PUT', '')

        self.assertEqual(200, resp.status_code)
        mock_request.assert_has_calls([
            mock.call('PUT', 'http://example.com:6688/foo',
                      allow_redirects=False,
                      headers={'Content-Type': 'application/json',
                               'Accept': 'application/json',
                               'User-Agent': 'python-moganclient'}),
            mock.call('PUT', 'http://example.com:6688/diff_lcation',
                      allow_redirects=False,
                      headers={'Content-Type': 'application/json',
                               'Accept': 'application/json',
                               'User-Agent': 'python-moganclient'})
        ])

    def test_http_json_request_redirect_error_without_location(self,
                                                               mock_request):
        mock_request.return_value = fakes.FakeHTTPResponse(
            302, 'Found', {}, '')
        client = http.HTTPClient('http://example.com:6688/foo')
        self.assertRaises(exc.EndpointException,
                          client.json_request, 'DELETE', '')
        mock_request.assert_called_once_with(
            'DELETE', 'http://example.com:6688/foo',
            allow_redirects=False,
            headers={'Content-Type': 'application/json',
                     'Accept': 'application/json',
                     'User-Agent': 'python-moganclient'})

    def test_http_json_request_redirect_get(self, mock_request):
        # Record the 302
        mock_request.side_effect = [
            fakes.FakeHTTPResponse(
                302, 'Found',
                {'location': 'http://example.com:6688'},
                ''),
            fakes.FakeHTTPResponse(
                200, 'OK',
                {'Content-Type': 'application/json'},
                '{}')]

        client = http.HTTPClient('http://example.com:6688')
        resp, body = client.json_request('GET', '')
        self.assertEqual(200, resp.status_code)
        self.assertEqual({}, body)

        mock_request.assert_has_calls([
            mock.call('GET', 'http://example.com:6688',
                      allow_redirects=False,
                      headers={'Content-Type': 'application/json',
                               'Accept': 'application/json',
                               'User-Agent': 'python-moganclient'}),
            mock.call('GET', 'http://example.com:6688',
                      allow_redirects=False,
                      headers={'Content-Type': 'application/json',
                               'Accept': 'application/json',
                               'User-Agent': 'python-moganclient'})
        ])

    def test_http_404_json_request(self, mock_request):
        mock_request.return_value = fakes.FakeHTTPResponse(
            404, 'Not Found', {'Content-Type': 'application/json'}, '')

        client = http.HTTPClient('http://example.com:6688')
        e = self.assertRaises(exc.NotFound, client.json_request, 'GET', '')
        # Assert that the raised exception can be converted to string
        self.assertIsNotNone(str(e))
        # Record a 404
        mock_request.assert_called_once_with(
            'GET', 'http://example.com:6688',
            allow_redirects=False,
            headers={'Content-Type': 'application/json',
                     'Accept': 'application/json',
                     'User-Agent': 'python-moganclient'})

    def test_http_300_json_request(self, mock_request):
        mock_request.return_value = fakes.FakeHTTPResponse(
            300, 'OK', {'Content-Type': 'application/json'}, '')
        client = http.HTTPClient('http://example.com:6688')
        e = self.assertRaises(
            exc.MultipleChoices, client.json_request, 'GET', '')
        # Assert that the raised exception can be converted to string
        self.assertIsNotNone(str(e))

        # Record a 300
        mock_request.assert_called_once_with(
            'GET', 'http://example.com:6688',
            allow_redirects=False,
            headers={'Content-Type': 'application/json',
                     'Accept': 'application/json',
                     'User-Agent': 'python-moganclient'})

    def test_fake_json_request(self, mock_request):
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'User-Agent': 'python-moganclient'}
        mock_request.side_effect = [socket.gaierror]

        client = http.HTTPClient('fake://example.com:6688')
        self.assertRaises(exc.EndpointNotFound,
                          client.json_request, "GET", "/")
        mock_request.assert_called_once_with('GET', 'fake://example.com:6688/',
                                             allow_redirects=False,
                                             headers=headers)

    def test_http_request_socket_error(self, mock_request):
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'User-Agent': 'python-moganclient'}
        mock_request.side_effect = [socket.error]

        client = http.HTTPClient('http://example.com:6688')
        self.assertRaises(exc.ConnectionError,
                          client.json_request, "GET", "/")
        mock_request.assert_called_once_with('GET', 'http://example.com:6688/',
                                             allow_redirects=False,
                                             headers=headers)

    def test_http_request_socket_timeout(self, mock_request):
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'User-Agent': 'python-moganclient'}
        mock_request.side_effect = [socket.timeout]

        client = http.HTTPClient('http://example.com:6688')
        self.assertRaises(exc.ConnectionError,
                          client.json_request, "GET", "/")
        mock_request.assert_called_once_with('GET', 'http://example.com:6688/',
                                             allow_redirects=False,
                                             headers=headers)

    def test_http_request_specify_timeout(self, mock_request):
        mock_request.return_value = fakes.FakeHTTPResponse(
            200, 'OK', {'Content-Type': 'application/json'}, '{}')

        client = http.HTTPClient('http://example.com:6688', timeout='123')
        resp, body = client.json_request('GET', '')
        self.assertEqual(200, resp.status_code)
        self.assertEqual({}, body)
        mock_request.assert_called_once_with(
            'GET', 'http://example.com:6688',
            allow_redirects=False,
            headers={'Content-Type': 'application/json',
                     'Accept': 'application/json',
                     'User-Agent': 'python-moganclient'},
            timeout=float(123))

    def test_get_system_ca_file(self, mock_request):
        chosen = '/etc/ssl/certs/ca-certificates.crt'
        with mock.patch('os.path.exists') as mock_os:
            mock_os.return_value = chosen

            ca = http.get_system_ca_file()
            self.assertEqual(chosen, ca)

            mock_os.assert_called_once_with(chosen)

    def test_insecure_verify_cert_none(self, mock_request):
        client = http.HTTPClient('https://foo', insecure=True)
        self.assertFalse(client.verify_cert)

    def test_passed_cert_to_verify_cert(self, mock_request):
        client = http.HTTPClient('https://foo', ca_file="NOWHERE")
        self.assertEqual("NOWHERE", client.verify_cert)

        with mock.patch('moganclient.common.http.get_system_ca_file') as gsf:
            gsf.return_value = "SOMEWHERE"
            client = http.HTTPClient('https://foo')
            self.assertEqual("SOMEWHERE", client.verify_cert)

    def test_methods(self, mock_request):
        fake = fakes.FakeHTTPResponse(
            200, 'OK', {'Content-Type': 'application/json'}, '{}')
        mock_request.return_value = fake

        client = http.HTTPClient('http://example.com:6688')
        methods = [client.get, client.put, client.post, client.patch,
                   client.delete, client.head]
        for method in methods:
            resp, body = method('')
            self.assertEqual(200, resp.status_code)


class TestSessionClient(base.TestBase):

    def setUp(self):
        super(TestSessionClient, self).setUp()
        self.request = mock.patch.object(adapter.LegacyJsonAdapter,
                                         'request').start()

    def test_session_simple_request(self):
        resp = fakes.FakeHTTPResponse(
            200, 'OK', {'Content-Type': 'application/octet-stream'}, '{}')
        self.request.return_value = (resp, {})

        client = http.SessionClient(session=mock.ANY,
                                    auth=mock.ANY)
        resp, body = client.request(method='GET', url='')
        self.assertEqual(200, resp.status_code)
        self.assertEqual('{}', ''.join([x for x in resp.content]))
        self.assertEqual({}, body)

    def test_session_json_request(self):
        fake = fakes.FakeHTTPResponse(
            200, 'OK', {'Content-Type': 'application/json'},
            jsonutils.dumps({'some': 'body'}))
        self.request.return_value = (fake, {'some': 'body'})

        client = http.SessionClient(session=mock.ANY,
                                    auth=mock.ANY)

        resp, body = client.request('', 'GET')
        self.assertEqual(200, resp.status_code)
        self.assertEqual({'some': 'body'}, resp.json())
        self.assertEqual({'some': 'body'}, body)

    def test_404_error_response(self):
        fake = fakes.FakeHTTPResponse(
            404, 'Not Found', {'Content-Type': 'application/json'}, '')
        self.request.return_value = (fake, '')

        client = http.SessionClient(session=mock.ANY,
                                    auth=mock.ANY)
        e = self.assertRaises(exc.NotFound,
                              client.request, '', 'GET')
        # Assert that the raised exception can be converted to string
        self.assertIsNotNone(six.text_type(e))

    def test_redirect_302_location(self):
        fake1 = fakes.FakeHTTPResponse(
            302, 'OK', {'location': 'http://no.where/ishere'}, '')
        fake2 = fakes.FakeHTTPResponse(200, 'OK',
                                       {'Content-Type': 'application/json'},
                                       jsonutils.dumps({'Mount': 'Fuji'}))
        self.request.side_effect = [
            (fake1, None), (fake2, {'Mount': 'Fuji'})]

        client = http.SessionClient(session=mock.ANY,
                                    auth=mock.ANY,
                                    endpoint_override='http://no.where/')
        resp, body = client.request('', 'GET', redirect=True)

        self.assertEqual(200, resp.status_code)
        self.assertEqual({'Mount': 'Fuji'}, utils.get_response_body(resp))
        self.assertEqual({'Mount': 'Fuji'}, body)

        self.assertEqual(('', 'GET'), self.request.call_args_list[0][0])
        self.assertEqual(('ishere', 'GET'), self.request.call_args_list[1][0])
        for call in self.request.call_args_list:
            self.assertEqual({'user_agent': 'python-moganclient',
                              'raise_exc': False,
                              'redirect': True}, call[1])

    def test_302_location_not_override(self):
        fake1 = fakes.FakeHTTPResponse(
            302, 'OK', {'location': 'http://no.where/ishere'}, '')
        fake2 = fakes.FakeHTTPResponse(200, 'OK',
                                       {'Content-Type': 'application/json'},
                                       jsonutils.dumps({'Mount': 'Fuji'}))
        self.request.side_effect = [
            (fake1, None), (fake2, {'Mount': 'Fuji'})]

        client = http.SessionClient(session=mock.ANY,
                                    auth=mock.ANY,
                                    endpoint_override='http://endpoint/')
        resp, body = client.request('', 'GET', redirect=True)

        self.assertEqual(200, resp.status_code)
        self.assertEqual({'Mount': 'Fuji'}, utils.get_response_body(resp))
        self.assertEqual({'Mount': 'Fuji'}, body)

        self.assertEqual(('', 'GET'), self.request.call_args_list[0][0])
        self.assertEqual(('http://no.where/ishere',
                          'GET'), self.request.call_args_list[1][0])
        for call in self.request.call_args_list:
            self.assertEqual({'user_agent': 'python-moganclient',
                              'raise_exc': False,
                              'redirect': True}, call[1])

    def test_redirect_302_no_location(self):
        fake = fakes.FakeHTTPResponse(
            302, 'OK', {}, '')
        self.request.side_effect = [(fake, '')]

        client = http.SessionClient(session=mock.ANY,
                                    auth=mock.ANY)
        e = self.assertRaises(exc.EndpointException,
                              client.request, '', 'GET', redirect=True)
        self.assertEqual("Location not returned with redirect",
                         six.text_type(e))

    def test_no_redirect_302_no_location(self):
        fake = fakes.FakeHTTPResponse(302, 'OK',
                                      {'location': 'http://no.where/ishere'},
                                      '')
        self.request.side_effect = [(fake, '')]

        client = http.SessionClient(session=mock.ANY,
                                    auth=mock.ANY)
        resp, body = client.request('', 'GET')

        self.assertEqual(fake, resp)

    def test_300_error_response(self):
        fake = fakes.FakeHTTPResponse(
            300, 'FAIL', {'Content-Type': 'application/octet-stream'}, '')
        self.request.return_value = (fake, '')

        client = http.SessionClient(session=mock.ANY,
                                    auth=mock.ANY)
        e = self.assertRaises(exc.MultipleChoices,
                              client.request, '', 'GET')
        # Assert that the raised exception can be converted to string
        self.assertIsNotNone(six.text_type(e))

    def test_506_error_response(self):
        # for 506 we don't have specific exception type
        fake = fakes.FakeHTTPResponse(
            506, 'FAIL', {'Content-Type': 'application/octet-stream'}, '')
        self.request.return_value = (fake, '')

        client = http.SessionClient(session=mock.ANY,
                                    auth=mock.ANY)
        e = self.assertRaises(exc.HttpServerError,
                              client.request, '', 'GET')

        self.assertEqual(506, e.status_code)

    def test_kwargs(self):
        fake = fakes.FakeHTTPResponse(
            200, 'OK', {'Content-Type': 'application/json'}, '{}')
        kwargs = dict(endpoint_override='http://no.where/',
                      data='some_data')

        client = http.SessionClient(mock.ANY)

        self.request.return_value = (fake, {})

        resp, body = client.request('', 'GET', **kwargs)

        self.assertEqual({'endpoint_override': 'http://no.where/',
                          'json': 'some_data',
                          'user_agent': 'python-moganclient',
                          'raise_exc': False}, self.request.call_args[1])
        self.assertEqual(200, resp.status_code)
        self.assertEqual({}, body)
        self.assertEqual({}, utils.get_response_body(resp))

    @mock.patch.object(jsonutils, 'dumps')
    def test_kwargs_with_files(self, mock_dumps):
        fake = fakes.FakeHTTPResponse(
            200, 'OK', {'Content-Type': 'application/json'}, '{}')
        mock_dumps.return_value = "{'files': test}}"
        data = six.BytesIO(b'test')
        kwargs = {'endpoint_override': 'http://no.where/',
                  'data': {'files': data}}
        client = http.SessionClient(mock.ANY)

        self.request.return_value = (fake, {})

        resp, body = client.request('', 'GET', **kwargs)

        self.assertEqual({'endpoint_override': 'http://no.where/',
                          'json': {'files': data},
                          'user_agent': 'python-moganclient',
                          'raise_exc': False}, self.request.call_args[1])
        self.assertEqual(200, resp.status_code)
        self.assertEqual({}, body)
        self.assertEqual({}, utils.get_response_body(resp))

    def test_methods(self):
        fake = fakes.FakeHTTPResponse(
            200, 'OK', {'Content-Type': 'application/json'}, '{}')
        self.request.return_value = (fake, {})

        client = http.SessionClient(mock.ANY)
        methods = [client.get, client.put, client.post, client.patch,
                   client.delete, client.head]
        for method in methods:
            resp, body = method('')
            self.assertEqual(200, resp.status_code)

    def test_credentials_headers(self):
        client = http.SessionClient(mock.ANY)
        self.assertEqual({}, client.credentials_headers())
