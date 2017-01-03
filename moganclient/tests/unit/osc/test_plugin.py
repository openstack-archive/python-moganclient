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

from osc_lib.tests import fakes

from moganclient.osc import plugin
from moganclient.tests.unit import base


class TestBaremetalComputePlugin(base.TestBase):

    @mock.patch('moganclient.v1.client.Client')
    def test_make_client_with_session(self, mogan_client):
        instance = mock.Mock()
        instance._api_version = {
            plugin.API_NAME: plugin.DEFAULT_BAREMETAL_COMPUTE_API_VERSION}
        instance.get_endpoint_for_service_type.return_value = mock.sentinel.ep
        instance.region_name = fakes.REGION_NAME
        instance.interface = fakes.INTERFACE
        instance.auth.auth_url = fakes.AUTH_URL
        instance.auth_ref.username = fakes.USERNAME
        instance.session = 'fake_session'

        plugin.make_client(instance)

        instance.get_endpoint_for_service_type.assert_called_once_with(
            plugin.API_NAME,
            region_name=fakes.REGION_NAME,
            interface=fakes.INTERFACE,
        )
        mogan_client.assert_called_once_with(
            endpoint=mock.sentinel.ep,
            auth_url=fakes.AUTH_URL,
            region_name=fakes.REGION_NAME,
            username=fakes.USERNAME,
            session='fake_session',
        )

    @mock.patch('moganclient.v1.client.Client')
    def test_make_client_no_session(self, mogan_client):
        instance = mock.Mock()
        instance._api_version = {
            plugin.API_NAME: plugin.DEFAULT_BAREMETAL_COMPUTE_API_VERSION}
        instance.get_endpoint_for_service_type.return_value = mock.sentinel.ep
        instance.region_name = fakes.REGION_NAME
        instance.interface = fakes.INTERFACE
        instance.auth.auth_url = fakes.AUTH_URL
        instance.auth_ref.username = fakes.USERNAME
        instance.auth_ref.auth_token = fakes.AUTH_TOKEN
        instance.session = None

        plugin.make_client(instance)

        instance.get_endpoint_for_service_type.assert_called_once_with(
            plugin.API_NAME,
            region_name=fakes.REGION_NAME,
            interface=fakes.INTERFACE,
        )
        mogan_client.assert_called_once_with(
            endpoint=mock.sentinel.ep,
            auth_url=fakes.AUTH_URL,
            region_name=fakes.REGION_NAME,
            username=fakes.USERNAME,
            token=fakes.AUTH_TOKEN,
        )
