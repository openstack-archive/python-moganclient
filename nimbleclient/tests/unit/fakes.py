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
from oslo_serialization import jsonutils
from requests import Response

from nimbleclient.common import base

# fake request id
FAKE_REQUEST_ID = 'req-0594c66b-6973-405c-ae2c-43fcfc00f2e3'
FAKE_REQUEST_ID_LIST = [FAKE_REQUEST_ID]

# fake resource id
FAKE_RESOURCE_ID = '0594c66b-6973-405c-ae2c-43fcfc00f2e3'
FAKE_RESOURCE_NAME = 'name-0594c66b-6973-405c-ae2c-43fcfc00f2e3'

# fake resource response key
FAKE_RESOURCE_ITEM_URL = '/resources/%s'
FAKE_RESOURCE_COLLECTION_URL = '/resources'


def create_response_obj_with_header():
    resp = Response()
    resp.headers['x-openstack-request-id'] = FAKE_REQUEST_ID
    return resp


def create_response_obj_with_compute_header():
    resp = Response()
    resp.headers['x-compute-request-id'] = FAKE_REQUEST_ID
    return resp


def create_resource_manager():
    return FakeManager()


class FaksResource(base.Resource):
    id = 'N/A'


class FakeManager(base.ManagerWithFind):
    resource_class = FaksResource

    def __init__(self, api=None):
        if not api:
            api = mock.Mock()
            api.get.return_value = (create_response_obj_with_header(),
                                    mock.MagicMock())
            api.head.return_value = (create_response_obj_with_header(),
                                     mock.MagicMock())
            api.post.return_value = (create_response_obj_with_header(),
                                     mock.MagicMock())
            api.put.return_value = (create_response_obj_with_header(),
                                    mock.MagicMock())
            api.delete.return_value = (create_response_obj_with_header(),
                                       mock.MagicMock())
            api.patch.return_value = (create_response_obj_with_header(),
                                      mock.MagicMock())
        super(FakeManager, self).__init__(api)

    def get(self, resource):
        return self._get(FAKE_RESOURCE_ITEM_URL % base.getid(resource),
                         response_key='resources')

    def list(self):
        return self._list(FAKE_RESOURCE_COLLECTION_URL,
                          response_key='resources')

    def update(self, resource):
        return self._update(FAKE_RESOURCE_ITEM_URL % base.getid(resource),
                            resource)

    def create(self, resource):
        return self._create(FAKE_RESOURCE_COLLECTION_URL, resource)

    def delete(self, resource):
        return self._delete(FAKE_RESOURCE_ITEM_URL % base.getid(resource))


class FakeRaw(object):
    version = 110


class FakeHTTPResponse(object):

    version = 1.1

    def __init__(self, status_code, reason, headers, content):
        self.headers = headers
        self.content = content
        self.status_code = status_code
        self.reason = reason
        self.raw = FakeRaw()

    def getheader(self, name, default=None):
        return self.headers.get(name, default)

    def getheaders(self):
        return self.headers.items()

    def read(self, amt=None):
        b = self.content
        self.content = None
        return b

    def iter_content(self, chunksize):
        return self.content

    def json(self):
        return jsonutils.loads(self.content)
