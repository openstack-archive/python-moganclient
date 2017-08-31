#   Copyright 2017 Fiberhome, Inc. All rights reserved.
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
import mock

from moganclient.osc.v1 import manageable_server
from moganclient.tests.unit import base as test_base
from moganclient.tests.unit import fakes
from moganclient.v1 import manageable_server as ms_mgr


@mock.patch.object(ms_mgr.ManageableServerManager, '_list')
class TestManageableServerList(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestManageableServerList, self).setUp()
        self.cmd = manageable_server.ListManageableServer(self.app, None)
        self.fake_ms = {
            "portgroups": [],
            "uuid": "166f5efc-f1c8-421b-b909-47cea4e59f25",
            "image_source": "755cac03-a460-4de0-8d8e-d1ac842768bf",
            "name": "node-0",
            "power_state": "power on",
            "provision_state": "active",
            "resource_class": "baremetal",
            "ports": [{
                "uuid": "935ff2f1-89ca-4d6e-b7ab-286c01dc40bb",
                "address": "52:54:00:01:c6:db",
                "neutron_port_id": "0c19889a-67f1-443a-85a9-21afcedcfc92"}],
            "portgroups": [{
                "neutron_port_id": None,
                "address": "52:54:00:0e:00:ef",
                "uuid": "5c84edb4-66f8-4199-aa57-6c08be362bbc"}]
            }
        self.fake_ms_obj = fakes.FakeResource(
            manager=None,
            info=copy.deepcopy(self.fake_ms),
            loaded=True)

    def test_list_manageable_server(self, mock_list):
        arglist = []
        verifylist = []
        mock_list.return_value = [self.fake_ms_obj]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_list.assert_called_once_with('/manageable_server',
                                          response_key='manageable_server')
        self.assertEqual(('UUID', 'Name', 'Power State', 'Provision State',
                          'Image Id', 'Resource Class'), columns)
        self.assertEqual((("166f5efc-f1c8-421b-b909-47cea4e59f25",
                           "node-0", "power on", "active",
                           "755cac03-a460-4de0-8d8e-d1ac842768bf",
                           "baremetal"),), tuple(data))

    def test_list_manageable_server_long(self, mock_list):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        mock_list.return_value = [self.fake_ms_obj]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_list.assert_called_once_with('/manageable_server',
                                          response_key='manageable_server')
        self.assertEqual(('UUID', 'Name', 'Power State', 'Provision State',
                          'Image Id', 'Resource Class', 'Ports',
                          'Port Groups'), columns)
        p_str = "address=52:54:00:01:c6:db; \n" \
                "neutron_port_id=0c19889a-67f1-443a-85a9-21afcedcfc92; \n" \
                "uuid=935ff2f1-89ca-4d6e-b7ab-286c01dc40bb; \n"
        pg_str = "address=52:54:00:0e:00:ef; \n" \
                 "neutron_port_id=None; \n" \
                 "uuid=5c84edb4-66f8-4199-aa57-6c08be362bbc; \n"
        self.assertEqual((("166f5efc-f1c8-421b-b909-47cea4e59f25",
                           "node-0", "power on", "active",
                           "755cac03-a460-4de0-8d8e-d1ac842768bf",
                           "baremetal", p_str, pg_str
                           ),), tuple(data))
