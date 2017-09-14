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
import json

import mock
from osc_lib import utils

from moganclient.osc.v1 import manageable_server
from moganclient.tests.unit import base as test_base
from moganclient.tests.unit import fakes
from moganclient.v1 import manageable_server as ms_mgr


class TestManageableServer(test_base.TestBaremetalComputeV1):
    fake_server = fakes.FakeServer.create_one_server()

    columns = (
        'addresses',
        'availability_zone',
        'created_at',
        'description',
        'flavor',
        'image',
        'links',
        'name',
        'node_uuid',
        'partitions',
        'properties',
        'updated_at',
        'uuid')

    data = (
        fake_server.addresses,
        fake_server.availability_zone,
        fake_server.created_at,
        fake_server.description,
        fake_server.flavor_uuid,
        fake_server.image_uuid,
        fake_server.links,
        fake_server.name,
        fake_server.updated_at,
        fake_server.uuid)


@mock.patch.object(ms_mgr.ManageableServerManager, '_list')
class TestManageableServerList(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestManageableServerList, self).setUp()
        self.cmd = manageable_server.ListManageableServer(self.app, None)
        self.fake_ms = {
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
        mock_list.assert_called_once_with('/manageable_servers',
                                          response_key='manageable_servers')
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
        mock_list.assert_called_once_with('/manageable_servers',
                                          response_key='manageable_servers')
        self.assertEqual(('UUID', 'Name', 'Power State', 'Provision State',
                          'Image Id', 'Resource Class', 'Ports',
                          'Port Groups'), columns)
        p_str = json.dumps(self.fake_ms_obj.ports, indent=2, sort_keys=True)
        pg_str = json.dumps(self.fake_ms_obj.portgroups, indent=2,
                            sort_keys=True)
        self.assertEqual((("166f5efc-f1c8-421b-b909-47cea4e59f25",
                           "node-0", "power on", "active",
                           "755cac03-a460-4de0-8d8e-d1ac842768bf",
                           "baremetal", p_str, pg_str
                           ),), tuple(data))


class TestServerManage(TestManageableServer):
    def setUp(self):
        super(TestServerManage, self).setUp()
        self.cmd = manageable_server.ManageServer(self.app, None)
        mocked_img = mock.Mock()
        mocked_img.name = 'test-image'
        image_mock = mock.MagicMock()
        image_mock.images.get.return_value = mocked_img
        self.app.client_manager.image = image_mock

    def _test_manage_fake_server(self, mock_create, name, node,
                                 description=None, properties=None):
        arglist = [node, name]
        verifylist = [
            ('name', name),
            ('node_uuid', node)]

        called_data = {'name': name,
                       'node_uuid': node}

        if description:
            arglist.extend(['--description', description])
            verifylist.append(('description', description))
            called_data['description'] = description
        if properties:
            arglist.extend(['--property', properties])
            verifylist.append(('property', {'key1': 'test'}))
            called_data['metadata'] = {'key1': 'test'}

        fk_server = fakes.FakeServer.create_one_server(called_data)
        fk_server._info['flavor_uuid'] = None

        mock_create.return_value = fk_server
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_create.assert_called_once_with(
            '/manageable_servers',
            data=called_data)
        self.assertEqual(self.columns, columns)
        expected_data = (
            '',
            fk_server.availability_zone,
            fk_server.created_at,
            fk_server.description,
            '',
            'test-image (%s)' % fk_server.image_uuid,
            fk_server.links,
            fk_server.name,
            fk_server.node_uuid,
            utils.format_dict(fk_server.partitions),
            utils.format_dict(fk_server.metadata),
            fk_server.updated_at,
            fk_server.uuid)
        self.assertEqual(expected_data, data)

    @mock.patch.object(ms_mgr.ManageableServerManager, '_create')
    def test_server_manage(self, mock_create):
        name = 'server1'
        node = 'aacdbd78-d670-409e-95aa-ecfcfb94fee2'
        self._test_manage_fake_server(mock_create, name, node)
