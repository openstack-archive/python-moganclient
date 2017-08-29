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
import mock

from osc_lib import exceptions
from osc_lib import utils
from oslo_utils import uuidutils

from moganclient.osc.v1 import server
from moganclient.tests.unit import base as test_base
from moganclient.tests.unit import fakes
from moganclient.v1 import server as server_mgr


class TestServer(test_base.TestBaremetalComputeV1):
    fake_server = fakes.FakeServer.create_one_server()

    columns = (
        'addresses',
        'availability_zone',
        'created_at',
        'description',
        'flavor_uuid',
        'image_uuid',
        'links',
        'max_count',
        'min_count',
        'name',
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
        1,
        1,
        fake_server.name,
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
                                 availability_zone=None, properties=None):
        arglist = [
            name,
            '--flavor', flavor_id,
            '--image', image_id]
        verifylist = [
            ('name', name),
            ('flavor', flavor_id),
            ('image', image_id)]
        called_networks = copy.deepcopy(networks)
        for nic in called_networks:
            if 'port-type' in nic:
                nic['port_type'] = nic['port-type']
                del nic['port-type']
            if 'net-id' in nic:
                nic['net_id'] = nic['net-id']
                del nic['net-id']
        called_data = {'name': name,
                       'image_uuid': image_id,
                       'flavor_uuid': flavor_id,
                       'networks': called_networks,
                       'min_count': 1,
                       'max_count': 1}
        for network in networks:
            network_id = network.get('net-id')
            port_type = network.get('port-type')
            if port_type:
                arglist.extend(
                    ['--nic',
                     'net-id=' + network_id + ',port-type=' + port_type])
                verifylist.append(
                    ('nic', [{'net-id': network_id, 'port-type': port_type}]))
            else:
                arglist.extend(['--nic', 'net-id=' + network_id])
                verifylist.append(('nic', [{'net-id': network_id}]))
        if description:
            arglist.extend(['--description', description])
            verifylist.append(('description', description))
            called_data['description'] = description
        if availability_zone:
            arglist.extend(['--availability-zone', availability_zone])
            verifylist.append(('availability_zone', availability_zone))
            called_data['availability_zone'] = availability_zone
        if properties:
            arglist.extend(['--property', properties])
            verifylist.append(('property', {'key1': 'test'}))
            called_data['metadata'] = {'key1': 'test'}

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
            '/servers',
            data=called_data)
        self.assertEqual(self.columns, columns)
        expected_data = (
            fk_server.addresses,
            fk_server.availability_zone,
            fk_server.created_at,
            fk_server.description,
            fk_server.flavor_uuid,
            fk_server.image_uuid,
            fk_server.links,
            1,
            1,
            fk_server.name,
            utils.format_dict(fk_server.metadata),
            fk_server.updated_at,
            fk_server.uuid)
        self.assertEqual(expected_data, data)

    def test_server_create(self, mock_create, mock_find):
        name = 'server1'
        flavor_id = 'flavor-id-' + uuidutils.generate_uuid(
            dashed=False)
        image_id = 'image-id-' + uuidutils.generate_uuid(
            dashed=False)
        networks = [{'net-id': 'net-id-' + uuidutils.generate_uuid(
            dashed=False)}]
        self._test_create_fake_server(mock_create, mock_find,
                                      name, flavor_id, image_id, networks)

    def test_server_create_with_description(self, mock_create, mock_find):
        name = 'server1'
        flavor_id = 'flavor-id-' + uuidutils.generate_uuid(
            dashed=False)
        image_id = 'image-id-' + uuidutils.generate_uuid(
            dashed=False)
        networks = [{'net-id': 'net-id-' + uuidutils.generate_uuid(
            dashed=False)}]
        description = 'fake_description'
        self._test_create_fake_server(mock_create, mock_find,
                                      name, flavor_id, image_id,
                                      networks, description)

    def test_server_create_with_az(self, mock_create, mock_find):
        name = 'server1'
        flavor_id = 'flavor-id-' + uuidutils.generate_uuid(
            dashed=False)
        image_id = 'image-id-' + uuidutils.generate_uuid(
            dashed=False)
        networks = [{'net-id': 'net-id-' + uuidutils.generate_uuid(
            dashed=False)}]
        fake_az = 'fake_availability_zone'
        self._test_create_fake_server(mock_create, mock_find,
                                      name, flavor_id, image_id,
                                      networks, availability_zone=fake_az)

    def test_server_create_with_port_type(self, mock_create, mock_find):
        name = 'server1'
        flavor_id = 'flavor-id-' + uuidutils.generate_uuid(dashed=False)
        image_id = 'image-id-' + uuidutils.generate_uuid(dashed=False)
        networks = [{'net-id': 'net-id-' + uuidutils.generate_uuid(
            dashed=False),
            'port-type': 'normal'}]
        self._test_create_fake_server(mock_create, mock_find,
                                      name, flavor_id, image_id,
                                      networks)

    def test_server_create_with_metadata(self, mock_create, mock_find):
        name = 'server1'
        flavor_id = 'flavor-id-' + uuidutils.generate_uuid(dashed=False)
        image_id = 'image-id-' + uuidutils.generate_uuid(dashed=False)
        networks = [{'net-id': 'net-id-' + uuidutils.generate_uuid(
            dashed=False)}]
        properties = 'key1=test'
        self._test_create_fake_server(mock_create, mock_find,
                                      name, flavor_id, image_id,
                                      networks, properties=properties)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(server_mgr.ServerManager, '_update')
class TestServerSet(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestServerSet, self).setUp()
        self.cmd = server.SetServer(self.app, None)
        self.fake_server = fakes.FakeServer.create_one_server()

    def test_server_set(self, mock_update, mock_find):
        mock_find.return_value = self.fake_server
        arglist = [
            '--name', 'test_server',
            '--property', 'k1=v1',
            self.fake_server.uuid,
        ]
        verifylist = [
            ('server', self.fake_server.uuid),
            ('name', 'test_server'),
            ('property', {'k1': 'v1'}),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        expected_url = '/servers/%s' % self.fake_server.uuid
        expected_args = [
            {'path': '/name', 'value': 'test_server', 'op': 'replace'},
            {'path': '/metadata/k1', 'value': 'v1', 'op': 'add'},
        ]
        mock_update.assert_called_once_with(expected_url,
                                            data=expected_args)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(server_mgr.ServerManager, '_update')
class TestServerUnset(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestServerUnset, self).setUp()
        self.cmd = server.UnsetServer(self.app, None)
        self.fake_server = fakes.FakeServer.create_one_server()

    def test_server_unset(self, mock_update, mock_find):
        mock_find.return_value = self.fake_server
        arglist = [
            '--property', 'key1',
            self.fake_server.uuid,
        ]
        verifylist = [
            ('server', self.fake_server.uuid),
            ('property', ['key1']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        expected_url = '/servers/%s' % self.fake_server.uuid
        expected_args = [
            {'path': '/metadata/key1', 'op': 'remove'}
        ]
        mock_update.assert_called_once_with(expected_url,
                                            data=expected_args)


@mock.patch.object(server_mgr.ServerManager, '_list')
class TestServerList(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestServerList, self).setUp()
        self.cmd = server.ListServer(self.app, None)
        fake_return_net = {
            "f31af5a2-f14d-4007-b2e5-abeb82429b87": [
                {
                    "addr": "172.24.4.4",
                    "type": "fixed"
                },
                {
                    "addr": "2001:db8::a",
                    "type": "fixed"
                }
            ]
        }
        self.fake_servers = fakes.FakeServer.create_servers(
            attrs={'status': 'active', 'power_state': 'power on'}, count=3)
        for s in self.fake_servers:
            setattr(s, 'addresses', fake_return_net)
        self.list_columns = (
            "UUID",
            "Name",
            "Status",
            'Networks',
            'Image'
        )

        self.list_columns_long = (
            "UUID",
            "Name",
            "Status",
            "Power State",
            "Networks",
            "Image",
            "Flavor",
            "Availability Zone",
            "Properties"
        )

        self.list_data = tuple((
            self.fake_servers[i].uuid,
            self.fake_servers[i].name,
            self.fake_servers[i].status,
            'f31af5a2-f14d-4007-b2e5-abeb82429b87=172.24.4.4, 2001:db8::a',
            self.fake_servers[i].image_uuid,
            ) for i in range(3))

        self.list_data_long = tuple((
            self.fake_servers[i].uuid,
            self.fake_servers[i].name,
            self.fake_servers[i].status,
            self.fake_servers[i].power_state,
            'f31af5a2-f14d-4007-b2e5-abeb82429b87=172.24.4.4, 2001:db8::a',
            self.fake_servers[i].image_uuid,
            self.fake_servers[i].flavor_uuid,
            self.fake_servers[i].availability_zone,
            '',
            ) for i in range(3))

    def test_server_list(self, mock_list):
        arglist = []
        verifylist = []
        mock_list.return_value = self.fake_servers
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_list.assert_called_once_with('/servers/detail',
                                          response_key='servers')
        self.assertEqual(self.list_columns, columns)
        self.assertEqual(self.list_data, tuple(data))

    def test_server_list_long(self, mock_list):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        mock_list.return_value = self.fake_servers
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_list.assert_called_once_with('/servers/detail',
                                          response_key='servers')
        self.assertEqual(self.list_columns_long, columns)
        self.assertEqual(self.list_data_long, tuple(data))

    def test_server_list_with_all_projects(self, mock_list):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        mock_list.return_value = self.fake_servers
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_list.assert_called_once_with('/servers/detail?all_tenants=True',
                                          response_key='servers')
        self.assertEqual(self.list_columns, columns)
        self.assertEqual(self.list_data, tuple(data))


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
        mock_delete.assert_called_with('/servers/%s' % fake_server.uuid)

    def test_server_delete_more_than_one(self, mock_delete, mock_find):
        fake_servers = fakes.FakeServer.create_servers(count=3)
        mock_find.side_effect = fake_servers
        args = [s.name for s in fake_servers]
        verify_args = [('server', [s.name for s in fake_servers])]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        self.cmd.take_action(parsed_args)
        expected = [mock.call('/servers/%s' % s.uuid) for s in fake_servers]
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
                         str(exc))


@mock.patch.object(server_mgr.ServerManager, '_get')
class TestServerShow(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestServerShow, self).setUp()
        self.cmd = server.ShowServer(self.app, None)
        self.fake_server = fakes.FakeServer.create_one_server()

    def test_server_show_with_uuid_specified(self, mock_get):
        args = [self.fake_server.uuid]
        verify_args = [('server', self.fake_server.uuid)]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        self.cmd.take_action(parsed_args)
        mock_get.assert_called_once_with(
            '/servers/%s' % self.fake_server.uuid)

    @mock.patch.object(server_mgr.ServerManager, 'list')
    def test_server_show_with_name_specified(self, mock_list, mock_get):
        args = [self.fake_server.name]
        verify_args = [('server', self.fake_server.name)]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        mock_get.side_effect = [exceptions.NotFound(404),
                                self.fake_server]
        mock_list.return_value = [self.fake_server]
        self.cmd.take_action(parsed_args)
        expected = [mock.call('/servers/%s' % self.fake_server.name),
                    mock.call('/servers/%s' % self.fake_server.uuid)]
        self.assertEqual(expected, mock_get.call_args_list)


class TestServerPowerActionBase(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestServerPowerActionBase, self).setUp()
        self.action = None
        self.action_name = None

    def _test_server_power_action_one(self, mock_update_all, mock_find):
        fake_server = fakes.FakeServer.create_one_server()
        mock_find.return_value = fake_server
        args = [fake_server.uuid]
        verify_args = [('server', [fake_server.uuid])]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        self.cmd.take_action(parsed_args)
        mock_update_all.assert_called_with(
            '/servers/%s/states/power' % fake_server.uuid,
            data={'target': self.action})

    def _test_server_power_action_multiple(self, mock_update_all,
                                           mock_find):
        fake_servers = fakes.FakeServer.create_servers(count=3)
        mock_find.side_effect = fake_servers
        args = [s.name for s in fake_servers]
        verify_args = [('server', [s.name for s in fake_servers])]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        self.cmd.take_action(parsed_args)
        expected = [mock.call(
            '/servers/%s/states/power' % s.uuid,
            data={'target': self.action}) for s in fake_servers]
        self.assertEqual(expected, mock_update_all.call_args_list)

    def _test_server_delete_more_than_one_partly_failed(
            self, mock_update_all, mock_find):
        fake_servers = fakes.FakeServer.create_servers(count=3)
        mock_find.side_effect = fake_servers
        args = [s.name for s in fake_servers]
        verify_args = [('server', [s.name for s in fake_servers])]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        mock_update_all.side_effect = [mock.Mock(), Exception(), mock.Mock()]
        exc = self.assertRaises(exceptions.CommandError,
                                self.cmd.take_action, parsed_args)
        self.assertEqual(
            '1 of 3 baremetal servers failed to %s.' % self.action_name,
            str(exc))


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(server_mgr.ServerManager, '_update_all')
class TestServerStart(TestServerPowerActionBase):
    def setUp(self):
        super(TestServerStart, self).setUp()
        self.cmd = server.StartServer(self.app, None)
        self.action = 'on'
        self.action_name = 'start'

    def test_server_start_one(self, mock_update_all, mock_find):
        self._test_server_power_action_one(mock_update_all, mock_find)

    def test_server_start_multiple(self, mock_update_all, mock_find):
        self._test_server_power_action_multiple(mock_update_all, mock_find)

    def test_server_start_multiple_partly_failed(self,
                                                 mock_update_all, mock_find):
        self._test_server_delete_more_than_one_partly_failed(
            mock_update_all, mock_find)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(server_mgr.ServerManager, '_update_all')
class TestServerStop(TestServerPowerActionBase):
    def setUp(self):
        super(TestServerStop, self).setUp()
        self.cmd = server.StopServer(self.app, None)
        self.action = 'off'
        self.action_name = 'stop'

    def test_server_stop_one(self, mock_update_all, mock_find):
        self._test_server_power_action_one(mock_update_all, mock_find)

    def test_server_stop_multiple(self, mock_update_all, mock_find):
        self._test_server_power_action_multiple(mock_update_all, mock_find)

    def test_server_stop_multiple_partly_failed(self,
                                                mock_update_all, mock_find):
        self._test_server_delete_more_than_one_partly_failed(
            mock_update_all, mock_find)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(server_mgr.ServerManager, '_update_all')
class TestServerReboot(TestServerPowerActionBase):
    def setUp(self):
        super(TestServerReboot, self).setUp()
        self.cmd = server.RebootServer(self.app, None)
        self.action = 'reboot'
        self.action_name = 'reboot'

    def test_server_reboot_one(self, mock_update_all, mock_find):
        self._test_server_power_action_one(mock_update_all, mock_find)

    def test_server_reboot_multiple(self, mock_update_all, mock_find):
        self._test_server_power_action_multiple(mock_update_all, mock_find)

    def test_server_reboot_multiple_partly_failed(self,
                                                  mock_update_all, mock_find):
        self._test_server_delete_more_than_one_partly_failed(
            mock_update_all, mock_find)


class TestServerLockActionBase(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestServerLockActionBase, self).setUp()
        self.action = None
        self.action_name = None

    def _test_server_lock_action_one(self, mock_update_all, mock_find):
        fake_server = fakes.FakeServer.create_one_server()
        mock_find.return_value = fake_server
        args = [fake_server.uuid]
        verify_args = [('server', [fake_server.uuid])]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        self.cmd.take_action(parsed_args)
        mock_update_all.assert_called_with(
            '/servers/%s/states/lock' % fake_server.uuid,
            data={'target': self.action})

    def _test_server_lock_action_multiple(self, mock_update_all,
                                          mock_find):
        fake_servers = fakes.FakeServer.create_servers(count=3)
        mock_find.side_effect = fake_servers
        args = [s.name for s in fake_servers]
        verify_args = [('server', [s.name for s in fake_servers])]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        self.cmd.take_action(parsed_args)
        expected = [mock.call(
            '/servers/%s/states/lock' % s.uuid,
            data={'target': self.action}) for s in fake_servers]
        self.assertEqual(expected, mock_update_all.call_args_list)

    def _test_server_lock_more_than_one_partly_failed(
            self, mock_update_all, mock_find):
        fake_servers = fakes.FakeServer.create_servers(count=3)
        mock_find.side_effect = fake_servers
        args = [s.name for s in fake_servers]
        verify_args = [('server', [s.name for s in fake_servers])]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        mock_update_all.side_effect = [mock.Mock(), Exception(), mock.Mock()]
        exc = self.assertRaises(exceptions.CommandError,
                                self.cmd.take_action, parsed_args)
        self.assertEqual(
            '1 of 3 baremetal servers failed to %s.' % self.action_name,
            str(exc))


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(server_mgr.ServerManager, '_update_all')
class TestServerLock(TestServerLockActionBase):
    def setUp(self):
        super(TestServerLock, self).setUp()
        self.cmd = server.LockServer(self.app, None)
        self.action = True
        self.action_name = 'lock'

    def test_server_lock_one(self, mock_update_all, mock_find):
        self._test_server_lock_action_one(mock_update_all, mock_find)

    def test_server_lock_multiple(self, mock_update_all, mock_find):
        self._test_server_lock_action_multiple(mock_update_all, mock_find)

    def test_server_lock_multiple_partly_failed(self,
                                                mock_update_all, mock_find):
        self._test_server_lock_more_than_one_partly_failed(
            mock_update_all, mock_find)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(server_mgr.ServerManager, '_update_all')
class TestServerUnLock(TestServerLockActionBase):
    def setUp(self):
        super(TestServerUnLock, self).setUp()
        self.cmd = server.UnLockServer(self.app, None)
        self.action = False
        self.action_name = 'unlock'

    def test_server_unlock_one(self, mock_update_all, mock_find):
        self._test_server_lock_action_one(mock_update_all, mock_find)

    def test_server_unlock_multiple(self, mock_update_all, mock_find):
        self._test_server_lock_action_multiple(mock_update_all, mock_find)

    def test_server_unlock_multiple_partly_failed(self,
                                                  mock_update_all, mock_find):
        self._test_server_lock_more_than_one_partly_failed(
            mock_update_all, mock_find)


@mock.patch.object(server_mgr.ServerManager, 'get_server_nics')
@mock.patch.object(server_mgr.ServerManager, 'get')
class TestServerShowNetInfo(TestServer):
    def setUp(self):
        super(TestServerShowNetInfo, self).setUp()
        self.cmd = server.ShowServerNetworkInfo(self.app, None)
        self.fake_server = fakes.FakeServer.create_one_server()

    def test_server_netinfo_show(self, mock_get, mock_netinfo):
        args = [self.fake_server.uuid]
        verify_args = [('server', self.fake_server.uuid)]
        mock_get.return_value = self.fake_server
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        self.cmd.take_action(parsed_args)
        mock_get.assert_called_once_with(self.fake_server.uuid)
        mock_netinfo.assert_called_once_with(self.fake_server.uuid)
