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

import copy
import uuid

import mock
from oslo_serialization import jsonutils
from requests import Response

from nimbleclient.common import base
from nimbleclient.v1 import availability_zone
from nimbleclient.v1 import flavor
from nimbleclient.v1 import server


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


class FakeBaremetalComputeV1Client(object):

    def __init__(self, **kwargs):
        self.fake_http_client = mock.Mock()

        self.flavor = flavor.FlavorManager(
            self.fake_http_client)
        self.server = server.ServerManager(self.fake_http_client)
        self.availability_zone = availability_zone.AvailabilityZoneManager(
            self.fake_http_client)


class FakeHTTPClient(object):

    def get(self):
        pass

    def head(self):
        pass

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    def patch(self):
        pass


class FakeResource(base.Resource):
    pass


class FakeManager(base.ManagerWithFind):
    resource_class = FakeResource

    def __init__(self, api=None):
        if not api:
            api = FakeHTTPClient()
        super(FakeManager, self).__init__(api)

    def get(self, resource):
        return self._get(FAKE_RESOURCE_ITEM_URL % base.getid(resource))

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


class FakeFlavor(object):
    """Fake one baremetal flavor."""

    @staticmethod
    def create_one_flavor(attrs=None):
        """Create a fake baremetal flavor..

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with uuid and other attributes
        """
        attrs = attrs or {}

        # Set default attribute
        flavor_info = {
            "created_at": "2016-09-27T02:37:21.966342+00:00",
            "description": "fake_description",
            "extra_specs": {"key0": "value0"},
            "is_public": True,
            "name": "flavor-name-" + uuid.uuid4().hex,
            "updated_at": None,
            "uuid": "flavor-id-" + uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        flavor_info.update(attrs)

        flavor = FakeResource(
            manager=None,
            info=copy.deepcopy(flavor_info),
            loaded=True)
        return flavor

    @staticmethod
    def create_flavors(attrs=None, count=2):
        """Create multiple fake baremetal flavors.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of flavors to fake
        :return:
            A list of FakeResource objects faking the flavors
        """
        flavors = []
        for i in range(0, count):
            flavors.append(
                FakeFlavor.create_one_flavor(attrs))

        return flavors

    @staticmethod
    def get_flavors(flavors=None, count=2):
        """Get an iterable Mock object with a list of faked baremetal flavors.

        If flavors list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List flavors:
            A list of FakeResource objects faking flavors
        :param int count:
            The number of flavors to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            baremetal flavors
        """
        if flavors is None:
            flavors = FakeFlavor.create_flavors(count)
        return mock.Mock(side_effect=flavors)


class FakeServer(object):
    """Fake one server."""

    @staticmethod
    def create_one_server(attrs=None):
        """Create a fake server.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with uuid and other attributes
        """
        attrs = attrs or {}
        attrs_data = copy.deepcopy(attrs)
        networks = attrs_data.pop('networks', [])
        network_info = {}
        for network in networks:
            network_info[network.get('uuid')] = {}
        attrs_data["network_info"] = network_info

        # Set default attribute
        server_info = {
            "created_at": "2016-11-14T08:03:18.926737+00:00",
            "description": "fake_description",
            "image_uuid": "image-id-" + uuid.uuid4().hex,
            "instance_type_uuid": "server-type-id-" + uuid.uuid4().hex,
            "links": [],
            "name": "server-name-" + uuid.uuid4().hex,
            "network_info": {"net-id-" + uuid.uuid4().hex: {}},
            "updated_at": None,
            "uuid": "server-id-" + uuid.uuid4().hex,
            "availability_zone": "zone-name-" + uuid.uuid4().hex,
            'extra': "fake_extra"
        }

        # Overwrite default attributes.
        server_info.update(attrs_data)
        server = FakeResource(
            manager=None,
            info=copy.deepcopy(server_info),
            loaded=True)
        return server

    @staticmethod
    def create_servers(attrs=None, count=2):
        """Create multiple fake servers.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of server types to fake
        :return:
            A list of FakeResource objects faking the server
        """
        servers = []
        for i in range(0, count):
            servers.append(FakeServer.create_one_server(attrs))

        return servers

    @staticmethod
    def get_servers(servers=None, count=2):
        """Get an iterable Mock object with a list of faked servers.

        If servers list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List servers:
            A list of FakeResource objects faking servers
        :param int count:
            The number of servers to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            servers
        """
        if servers is None:
            servers = FakeServer.create_servers(count)
        return mock.Mock(side_effect=servers)
