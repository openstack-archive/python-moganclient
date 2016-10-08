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

from nimbleclient.v1 import instance_type as instance_type_mgr
from nimbleclient.osc.v1 import instance_type
from nimbleclient.tests.unit import base
from nimbleclient.tests.unit import fakes


class TestInstanceType(base.TestBaremetalComputeV1):
    fake_type = fakes.FakeInstanceType.create_one_instance_type()

    columns = (
        'created_at',
        'description',
        'extra_specs',
        'is_public',
        'name',
        'updated_at',
        'uuid',
    )

    data = (
        fake_type.created_at,
        fake_type.description,
        fake_type.extra_specs,
        fake_type.is_public,
        fake_type.name,
        fake_type.updated_at,
        fake_type.uuid,
    )


@mock.patch.object(instance_type_mgr.InstanceTypeManager, '_create')
class TestInstanceTypeCreate(TestInstanceType):

    def setUp(self):
        super(TestInstanceTypeCreate, self).setUp()
        self.cmd = instance_type.CreateType(self.app, None)

    def test_type_create(self, mock_create):
        arglist = [
            'type1',
        ]
        verifylist = [
            ('name', 'type1'),
        ]
        mock_create.return_value = self.fake_type
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_create.assert_called_once_with(url='/types',
                                            data={
                                                'name': 'type1',
                                                'is_public': True,
                                                'description': None,
                                            })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_type_create_with_public(self, mock_create):
        arglist = [
            '--public',
            'type1',
        ]
        verifylist = [
            ('public', True),
            ('name', 'type1'),
        ]
        mock_create.return_value = self.fake_type
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_create.assert_called_once_with(url='/types',
                                            data={
                                                'name': 'type1',
                                                'is_public': True,
                                                'description': None,
                                            })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_type_create_with_private(self, mock_create):
        arglist = [
            '--private',
            'type1',
        ]
        verifylist = [
            ('private', True),
            ('name', 'type1'),
        ]
        mock_create.return_value = self.fake_type
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_create.assert_called_once_with(url='/types',
                                            data={
                                                'name': 'type1',
                                                'is_public': False,
                                                'description': None,
                                            })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_type_create_with_description(self, mock_create):
        arglist = [
            '--description', 'test description.',
            'type1',
        ]
        verifylist = [
            ('description', 'test description.'),
            ('name', 'type1'),
        ]
        mock_create.return_value = self.fake_type
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_create.assert_called_once_with(
            url='/types',
            data={
                'name': 'type1',
                'is_public': True,
                'description': 'test description.',
            })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
