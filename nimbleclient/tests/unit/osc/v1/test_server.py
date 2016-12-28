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
import uuid

from osc_lib import exceptions
from osc_lib.tests import utils as osc_test_utils
from osc_lib import utils

from nimbleclient.osc.v1 import server
from nimbleclient.tests.unit import base as test_base
from nimbleclient.tests.unit import fakes
from nimbleclient.v1 import server as server_mgr


class TestServer(test_base.TestBaremetalComputeV1):
    fake_server = fakes.FakeServer.create_one_server()

    columns = (
        'availability_zone',
        'created_at',
        'description',
        'extra',
        'image_uuid',
        'instance_type_uuid',
        'links',
        'name',
        'network_info',
        'updated_at',
        'uuid')

    data = (
        fake_server.availability_zone,
        fake_server.created_at,
        fake_server.description,
        fake_server.image_uuid,
        fake_server.instance_type_uuid,
        fake_server.links,
        fake_server.name,
        fake_server.network_info,
        fake_server.updated_at,
        fake_server.uuid)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(server_mgr.ServerManager, '_create')
class TestServerCreate(TestServer):
    def setUp(self):
        super(TestServerCreate, self).setUp()
        self.cmd = server.CreateServer(self.app, None)
        self.app.client_manager.image = mock.Mock()

    def _test_create_fake_server(self, mock_create, mock_find,
                                 name, flavor_id, image_id, networks,
                                 description=None,
                                 availability_zone=None, extra=None):
        arglist = [
            name,
            '--flavor', flavor_id,
            '--image', image_id]
        verifylist = [
            ('name', name),
            ('flavor', flavor_id),
            ('image', image_id)]
        called_data = {'name': name,
                       'image_uuid': image_id,
                       'instance_type_uuid': flavor_id,
                       'networks': networks}
        for network in networks:
            network_id = network.get('uuid')
            port_type = network.get('port-type')
            if port_type:
                arglist.extend(
                    ['--nic',
                     'uuid=' + network_id + ',port-type=' + port_type])
                verifylist.append(
                    ('nic', [{'uuid': network_id, 'port-type': port_type}]))
            else:
                arglist.extend(['--nic', 'uuid=' + network_id])
                verifylist.append(('nic', [{'uuid': network_id}]))
        if description:
            arglist.extend(['--description', description])
            verifylist.append(('description', description))
            called_data['description'] = description
        if availability_zone:
            arglist.extend(['--availability-zone', availability_zone])
            verifylist.append(('availability_zone', availability_zone))
            called_data['availability_zone'] = availability_zone
        if extra:
            arglist.extend(['--extra', extra])
            verifylist.append(('extra', extra))
            called_data['extra'] = extra

        flavor_obj = mock.Mock()
        flavor_obj.uuid = flavor_id
        image_obj = mock.Mock()
        image_obj.id = image_id
        mock_find.side_effect = [flavor_obj, image_obj]
        fk_server = fakes.FakeServer.create_one_server(called_data)
        mock_create.return_value = fk_server
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        mock_create.assert_called_once_with(
            '/instances',
            data=called_data)
        self.assertEqual(self.columns, columns)
        expected_data = (
            fk_server.availability_zone,
            fk_server.created_at,
            fk_server.description,
            fk_server.extra,
            fk_server.image_uuid,
            fk_server.instance_type_uuid,
            fk_server.links,
            fk_server.name,
            fk_server.network_info,
            fk_server.updated_at,
            fk_server.uuid)
        self.assertEqual(expected_data, data)

    def test_server_create(self, mock_create, mock_find):
        name = 'server1'
        flavor_id = 'flavor-id-' + uuid.uuid4().hex
        image_id = 'image-id-' + uuid.uuid4().hex
        networks = [{'uuid': 'net-id-' + uuid.uuid4().hex}]
        self._test_create_fake_server(mock_create, mock_find,
                                      name, flavor_id, image_id, networks)

    def test_server_create_with_description(self, mock_create, mock_find):
        name = 'server1'
        flavor_id = 'flavor-id-' + uuid.uuid4().hex
        image_id = 'image-id-' + uuid.uuid4().hex
        networks = [{'uuid': 'net-id-' + uuid.uuid4().hex}]
        description = 'fake_description'
        self._test_create_fake_server(mock_create, mock_find,
                                      name, flavor_id, image_id,
                                      networks, description)

    def test_server_create_with_az(self, mock_create, mock_find):
        name = 'server1'
        flavor_id = 'flavor-id-' + uuid.uuid4().hex
        image_id = 'image-id-' + uuid.uuid4().hex
        networks = [{'uuid': 'net-id-' + uuid.uuid4().hex}]
        fake_az = 'fake_availability_zone'
        self._test_create_fake_server(mock_create, mock_find,
                                      name, flavor_id, image_id,
                                      networks, availability_zone=fake_az)

    def test_server_create_with_port_type(self, mock_create, mock_find):
        name = 'server1'
        flavor_id = 'flavor-id-' + uuid.uuid4().hex
        image_id = 'image-id-' + uuid.uuid4().hex
        networks = [{'uuid': 'net-id-' + uuid.uuid4().hex,
                     'port-type': 'normal'}]
        self._test_create_fake_server(mock_create, mock_find,
                                      name, flavor_id, image_id,
                                      networks)

    def test_server_create_with_extra(self, mock_create, mock_find):
        name = 'server1'
        flavor_id = 'flavor-id-' + uuid.uuid4().hex
        image_id = 'image-id-' + uuid.uuid4().hex
        networks = [{'uuid': 'net-id-' + uuid.uuid4().hex}]
        extra_info = 'key1=test'
        self._test_create_fake_server(mock_create, mock_find,
                                      name, flavor_id, image_id,
                                      networks, extra=extra_info)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(server_mgr.ServerManager, '_update')
class TestServerUpdate(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestServerUpdate, self).setUp()
        self.cmd = server.UpdateServer(self.app, None)
        self.fake_server = fakes.FakeServer.create_one_server()

    def test_server_update_description(self, mock_update, mock_find):
        mock_find.return_value = self.fake_server
        arglist = [
            '--description', 'test_description',
            self.fake_server.uuid]
        verifylist = [
            ('server', self.fake_server.uuid),
            ('description', 'test_description')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_update.assert_called_with(
            '/instances/%s' % self.fake_server.uuid,
            data=[{'path': '/description',
                   'value': 'test_description',
                   'op': 'replace'}])

    def test_server_update_add_extra(self, mock_update, mock_find):
        mock_find.return_value = self.fake_server
        arglist = [
            '--add-extra', 'extra_key:extra_value',
            self.fake_server.uuid]
        verifylist = [
            ('server', self.fake_server.uuid),
            ('add_extra', [('extra_key', 'extra_value')])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_update.assert_called_with(
            '/instances/%s' % self.fake_server.uuid,
            data=[{'path': '/extra/extra_key',
                   'value': 'extra_value',
                   'op': 'add'}])

    def test_server_update_add_replace_remove_multi_extra(
            self, mock_update, mock_find):
        mock_find.return_value = self.fake_server
        arglist = [
            '--add-extra', 'add_key1:add_value1',
            '--add-extra', 'add_key2:add_value2',
            '--replace-extra', 'replace_key1:replace_value1',
            '--replace-extra', 'replace_key2:replace_value2',
            '--remove-extra', 'remove_key1',
            '--remove-extra', 'remove_key2',
            self.fake_server.uuid]
        verifylist = [
            ('server', self.fake_server.uuid),
            ('add_extra', [('add_key1', 'add_value1'),
                           ('add_key2', 'add_value2')]),
            ('replace_extra', [('replace_key1', 'replace_value1'),
                               ('replace_key2', 'replace_value2')]),
            ('remove_extra', ['remove_key1', 'remove_key2'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_update.assert_called_with(
            '/instances/%s' % self.fake_server.uuid,
            data=[{'path': '/extra/add_key1',
                   'value': 'add_value1',
                   'op': 'add'},
                  {'path': '/extra/add_key2',
                   'value': 'add_value2',
                   'op': 'add'},
                  {'path': '/extra/replace_key1',
                   'value': 'replace_value1',
                   'op': 'replace'},
                  {'path': '/extra/replace_key2',
                   'value': 'replace_value2',
                   'op': 'replace'},
                  {'path': '/extra/remove_key1',
                   'op': 'remove'},
                  {'path': '/extra/remove_key2',
                   'op': 'remove'}])


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(server_mgr.ServerManager, '_delete')
class TestServerDelete(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestServerDelete, self).setUp()
        self.cmd = server.DeleteServer(self.app, None)

    def test_server_delete_one(self, mock_delete, mock_find):
        fake_server = fakes.FakeServer.create_one_server()
        mock_find.return_value = fake_server
        args = ['server1']
        verify_args = [('server', ['server1'])]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        self.cmd.take_action(parsed_args)
        mock_delete.assert_called_with('/instances/%s' % fake_server.uuid)

    def test_server_delete_more_than_one(self, mock_delete, mock_find):
        fake_servers = fakes.FakeServer.create_servers(count=3)
        mock_find.side_effect = fake_servers
        args = [s.name for s in fake_servers]
        verify_args = [('server', [s.name for s in fake_servers])]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        self.cmd.take_action(parsed_args)
        expected = [mock.call('/instances/%s' % s.uuid) for s in fake_servers]
        self.assertEqual(expected, mock_delete.call_args_list)

    def test_server_delete_more_than_one_partly_failed(
            self, mock_delete, mock_find):
        fake_servers = fakes.FakeServer.create_servers(count=3)
        mock_find.side_effect = fake_servers
        args = [s.name for s in fake_servers]
        verify_args = [('server', [s.name for s in fake_servers])]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        mock_delete.side_effect = [mock.Mock(), Exception(), mock.Mock()]
        exc = self.assertRaises(exceptions.CommandError,
                                self.cmd.take_action, parsed_args)
        self.assertEqual('1 of 3 baremetal servers failed to delete.',
                         exc.message)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(server_mgr.ServerManager, '_update_all')
class TestSetServerPowerState(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestSetServerPowerState, self).setUp()
        self.cmd = server.SetServerPowerState(self.app, None)
        self.fake_server = fakes.FakeServer.create_one_server()

    def test_server_set_power_state(self, mock_update_all, mock_find):
        mock_find.return_value = self.fake_server
        args = ['--power-state', 'off', self.fake_server.uuid]
        verify_args = [('power_state', 'off'),
                       ('server', self.fake_server.uuid)]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        self.cmd.take_action(parsed_args)
        mock_update_all.assert_called_with(
            '/instances/%s/states/power' % self.fake_server.uuid,
            data={'target': 'off'})

    def test_server_set_invalid_power_state(self,
                                            mock_update_all, mock_find):
        mock_find.return_value = self.fake_server
        args = ['--power-state', 'non_state', self.fake_server.uuid]
        verify_args = [('power_state', 'off'),
                       ('server', self.fake_server.uuid)]
        self.assertRaises(osc_test_utils.ParserException,
                          self.check_parser,
                          self.cmd, args, verify_args)
