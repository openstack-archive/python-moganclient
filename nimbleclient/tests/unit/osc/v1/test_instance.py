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
        fk_instance = fakes.FakeInstance.create_fake_instance(
            name, type_id, image_id, networks)
        mock_create.return_value = fk_instance
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        mock_create.assert_called_once_with(
            '/instances',
            data=called_data)

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
