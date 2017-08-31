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

from moganclient.common import http
from moganclient.v1 import aggregate
from moganclient.v1 import availability_zone
from moganclient.v1 import flavor
from moganclient.v1 import keypair
from moganclient.v1 import manageable_server
from moganclient.v1 import node
from moganclient.v1 import server
from moganclient.v1 import server_group


class Client(object):
    """Client for the Mogan v1 API."""

    def __init__(self, *args, **kwargs):
        """Initialize a new client for the Mogan v1 API."""
        self.http_client = http._construct_http_client(*args, **kwargs)

        self.flavor = flavor.FlavorManager(
            self.http_client)
        self.server = server.ServerManager(self.http_client)
        self.availability_zone = availability_zone.AvailabilityZoneManager(
            self.http_client)
        self.keypair = keypair.KeyPairManager(self.http_client)
        self.node = node.NodeManager(self.http_client)
        self.aggregate = aggregate.AggregateManager(self.http_client)
        self.server_group = server_group.ServerGroupManager(self.http_client)
        self.aggregate_node = aggregate.AggregateNodeManager(self.http_client)
        self.manageable_server = manageable_server.ManageableServerManager(
            self.http_client)
