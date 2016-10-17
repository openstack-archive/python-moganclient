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

from nimbleclient.common import http
from nimbleclient.v1 import instance
from nimbleclient.v1 import instance_type


class Client(object):
    """Client for the Nimble v1 API."""

    def __init__(self, *args, **kwargs):
        """Initialize a new client for the Nimble v1 API."""
        self.http_client = http._construct_http_client(*args, **kwargs)

        self.instance_type = instance_type.InstanceTypeManager(
            self.http_client)
        self.instance = instance.InstanceManager(self.http_client)
