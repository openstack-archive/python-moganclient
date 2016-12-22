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

from osc_lib.tests import utils as osc_test_utils
from osc_lib import utils

from nimbleclient.osc.v1 import instance
from nimbleclient.tests.unit import base as test_base
from nimbleclient.tests.unit import fakes
from nimbleclient.v1 import instance as instance_mgr


class TestInstance(test_base.TestBaremetalComputeV1):
    fake_instance = fakes.FakeInstance.create_one_instance()

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
        fake_instance.availability_zone,
        fake_instance.created_at,
        fake_instance.description,
        fake_instance.image_uuid,
        fake_instance.instance_type_uuid,
        fake_instance.links,
        fake_instance.name,
        fake_instance.network_info,
        fake_instance.updated_at,
        fake_instance.uuid)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(instance_mgr.InstanceManager, '_create')
class TestInstanceCreate(TestInstance):

    def setUp(self):
        super(TestInstanceCreate, self).setUp()
        self.cmd = instance.CreateInstance(self.app, None)
        self.app.client_manager.image = mock.Mock()

    def _test_create_fake_instance(self, mock_create, mock_find,
                                   name, type_id, image_id, networks,
                                   description=None,
                                   availability_zone=None, extra=None):
        arglist = [
            name,
            '--type', type_id,
            '--image', image_id]
        verifylist = [
            ('name', name),
            ('type', type_id),
            ('image', image_id)]
        called_data = {'name': name,
                       'image_uuid': image_id,
                       'instance_type_uuid': type_id,
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

        type_obj = mock.Mock()
        type_obj.uuid = type_id
        image_obj = mock.Mock()
        image_obj.id = image_id
        mock_find.side_effect = [type_obj, image_obj]
        fk_instance = fakes.FakeInstance.create_one_instance(called_data)
        mock_create.return_value = fk_instance
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        mock_create.assert_called_once_with(
            '/instances',
            data=called_data)
        self.assertEqual(self.columns, columns)
        expected_data = (
            fk_instance.availability_zone,
            fk_instance.created_at,
            fk_instance.description,
            fk_instance.extra,
            fk_instance.image_uuid,
            fk_instance.instance_type_uuid,
            fk_instance.links,
            fk_instance.name,
            fk_instance.network_info,
            fk_instance.updated_at,
            fk_instance.uuid)
        self.assertEqual(expected_data, data)

    def test_instance_create(self, mock_create, mock_find):
        name = 'instance1'
        type_id = 'type-id-' + uuid.uuid4().hex
        image_id = 'image-id-' + uuid.uuid4().hex
        networks = [{'uuid': 'net-id-' + uuid.uuid4().hex}]
        self._test_create_fake_instance(mock_create, mock_find,
                                        name, type_id, image_id, networks)

    def test_instance_create_with_description(self, mock_create, mock_find):
        name = 'instance1'
        type_id = 'type-id-' + uuid.uuid4().hex
        image_id = 'image-id-' + uuid.uuid4().hex
        networks = [{'uuid': 'net-id-' + uuid.uuid4().hex}]
        description = 'fake_description'
        self._test_create_fake_instance(mock_create, mock_find,
                                        name, type_id, image_id,
                                        networks, description)

    def test_instance_create_with_az(self, mock_create, mock_find):
        name = 'instance1'
        type_id = 'type-id-' + uuid.uuid4().hex
        image_id = 'image-id-' + uuid.uuid4().hex
        networks = [{'uuid': 'net-id-' + uuid.uuid4().hex}]
        fake_az = 'fake_availability_zone'
        self._test_create_fake_instance(mock_create, mock_find,
                                        name, type_id, image_id,
                                        networks, availability_zone=fake_az)

    def test_instance_create_with_port_type(self, mock_create, mock_find):
        name = 'instance1'
        type_id = 'type-id-' + uuid.uuid4().hex
        image_id = 'image-id-' + uuid.uuid4().hex
        networks = [{'uuid': 'net-id-' + uuid.uuid4().hex,
                     'port-type': 'normal'}]
        self._test_create_fake_instance(mock_create, mock_find,
                                        name, type_id, image_id,
                                        networks)

    def test_instance_create_with_extra(self, mock_create, mock_find):
        name = 'instance1'
        type_id = 'type-id-' + uuid.uuid4().hex
        image_id = 'image-id-' + uuid.uuid4().hex
        networks = [{'uuid': 'net-id-' + uuid.uuid4().hex}]
        extra_info = 'key1=test'
        self._test_create_fake_instance(mock_create, mock_find,
                                        name, type_id, image_id,
                                        networks, extra=extra_info)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(instance_mgr.InstanceManager, '_update')
class TestInstanceUpdate(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestInstanceUpdate, self).setUp()
        self.cmd = instance.UpdateInstance(self.app, None)
        self.fake_instance = fakes.FakeInstance.create_one_instance()

    def test_instance_update_description(self, mock_update, mock_find):
        mock_find.return_value = self.fake_instance
        arglist = [
            '--description', 'test_description',
            self.fake_instance.uuid]
        verifylist = [
            ('instance', self.fake_instance.uuid),
            ('description', 'test_description')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_update.assert_called_with(
            '/instances/%s' % self.fake_instance.uuid,
            data=[{'path': '/description',
                   'value': 'test_description',
                   'op': 'replace'}])

    def test_instance_update_add_extra(self, mock_update, mock_find):
        mock_find.return_value = self.fake_instance
        arglist = [
            '--add-extra', 'extra_key:extra_value',
            self.fake_instance.uuid]
        verifylist = [
            ('instance', self.fake_instance.uuid),
            ('add_extra', [('extra_key', 'extra_value')])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_update.assert_called_with(
            '/instances/%s' % self.fake_instance.uuid,
            data=[{'path': '/extra/extra_key',
                   'value': 'extra_value',
                   'op': 'add'}])

    def test_instance_update_add_replace_remove_multi_extra(
            self, mock_update, mock_find):
        mock_find.return_value = self.fake_instance
        arglist = [
            '--add-extra', 'add_key1:add_value1',
            '--add-extra', 'add_key2:add_value2',
            '--replace-extra', 'replace_key1:replace_value1',
            '--replace-extra', 'replace_key2:replace_value2',
            '--remove-extra', 'remove_key1',
            '--remove-extra', 'remove_key2',
            self.fake_instance.uuid]
        verifylist = [
            ('instance', self.fake_instance.uuid),
            ('add_extra', [('add_key1', 'add_value1'),
                           ('add_key2', 'add_value2')]),
            ('replace_extra', [('replace_key1', 'replace_value1'),
                               ('replace_key2', 'replace_value2')]),
            ('remove_extra', ['remove_key1', 'remove_key2'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        mock_update.assert_called_with(
            '/instances/%s' % self.fake_instance.uuid,
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
@mock.patch.object(instance_mgr.InstanceManager, '_update_all')
class TestSetInstancePowerState(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestSetInstancePowerState, self).setUp()
        self.cmd = instance.SetInstancePowerState(self.app, None)
        self.fake_instance = fakes.FakeInstance.create_one_instance()

    def test_instance_set_power_state(self, mock_update_all, mock_find):
        mock_find.return_value = self.fake_instance
        args = ['--power-state', 'off', self.fake_instance.uuid]
        verify_args = [('power_state', 'off'),
                       ('instance', self.fake_instance.uuid)]
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        self.cmd.take_action(parsed_args)
        mock_update_all.assert_called_with(
            '/instances/%s/states/power' % self.fake_instance.uuid,
            data={'target': 'off'})

    def test_instance_set_invalid_power_state(self,
                                              mock_update_all, mock_find):
        mock_find.return_value = self.fake_instance
        args = ['--power-state', 'non_state', self.fake_instance.uuid]
        verify_args = [('power_state', 'off'),
                       ('instance', self.fake_instance.uuid)]
        self.assertRaises(osc_test_utils.ParserException,
                          self.check_parser,
                          self.cmd, args, verify_args)
