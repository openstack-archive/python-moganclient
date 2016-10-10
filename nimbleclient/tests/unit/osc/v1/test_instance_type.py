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

from osc_lib import utils

from nimbleclient.common import base
from nimbleclient.osc.v1 import instance_type
from nimbleclient.tests.unit import base as test_base
from nimbleclient.tests.unit import fakes
from nimbleclient.v1 import instance_type as instance_type_mgr


class TestInstanceType(test_base.TestBaremetalComputeV1):
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
        mock_create.assert_called_once_with('/types',
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
        mock_create.assert_called_once_with('/types',
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
        mock_create.assert_called_once_with('/types',
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
            '/types',
            data={
                'name': 'type1',
                'is_public': True,
                'description': 'test description.',
            })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    @mock.patch.object(instance_type_mgr.InstanceTypeManager, '_get')
    @mock.patch.object(instance_type_mgr.InstanceTypeManager, '_update')
    def test_type_create_with_property(self, mock_create, mock_update,
                                       mock_get):
        arglist = [
            '--property', 'key1=value1',
            'type1',
        ]
        verifylist = [
            ('property', {'key1': 'value1'}),
            ('name', 'type1'),
        ]
        mock_create.return_value = self.fake_type
        mock_get.return_value = {'extra_specs': {'key1': 'value1'}}
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_create.assert_called_once_with('/types',
                                            data={
                                                'name': 'type1',
                                                'is_public': True,
                                                'description': None,
                                            })
        expected_url = '/types/%s/extraspecs' % base.getid(self.fake_type)
        mock_update.assert_called_once_with(expected_url,
                                            data=parsed_args.property,
                                            return_raw=True)
        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(self.columns, columns)
        expected_data = copy.deepcopy(self.data)
        # update extra specs
        expected_data[2].update({'key1': 'value1'})
        self.assertEqual(expected_data, data)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(instance_type_mgr.InstanceTypeManager, '_delete')
class TestInstanceTypeDelete(TestInstanceType):

    def setUp(self):
        super(TestInstanceTypeDelete, self).setUp()
        self.cmd = instance_type.DeleteType(self.app, None)

    def test_type_delete(self, mock_delete, mock_find):
        arglist = [
            'type1',
        ]
        verifylist = [
            ('type', ['type1']),
        ]
        mock_find.return_value = self.fake_type
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expected_url = '/types/%s' % base.getid(self.fake_type)
        mock_delete.assert_called_once_with(expected_url)
        self.assertIsNone(result)

    def test_type_multiple_delete(self, mock_delete, mock_find):
        arglist = [
            'type1',
            'type2',
            'type3'
        ]
        verifylist = [
            ('type', ['type1', 'type2', 'type3']),
        ]
        mock_find.return_value = self.fake_type
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expected_url = '/types/%s' % base.getid(self.fake_type)
        expected_call = [mock.call(expected_url), mock.call(expected_url),
                         mock.call(expected_url)]
        mock_delete.assert_has_calls(expected_call)
        self.assertIsNone(result)


@mock.patch.object(instance_type_mgr.InstanceTypeManager, '_list')
class TestInstanceTypeList(TestInstanceType):

    list_columns = (
        "UUID",
        "Name",
        "Is Public",
    )

    list_columns_long = (
        "UUID",
        "Name",
        "Is Public",
        "Description",
        "Properties",
    )

    list_data = ((
        TestInstanceType.fake_type.uuid,
        TestInstanceType.fake_type.name,
        TestInstanceType.fake_type.is_public,
    ), )

    list_data_long = ((
        TestInstanceType.fake_type.uuid,
        TestInstanceType.fake_type.name,
        TestInstanceType.fake_type.is_public,
        TestInstanceType.fake_type.description,
        TestInstanceType.fake_type.extra_specs,
    ), )

    def setUp(self):
        super(TestInstanceTypeList, self).setUp()
        self.cmd = instance_type.ListType(self.app, None)

    def test_type_list(self, mock_list):
        arglist = []
        verifylist = []
        mock_list.return_value = [self.fake_type]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_list.assert_called_once_with('/types', response_key='types')
        self.assertEqual(self.list_columns, columns)
        self.assertEqual(self.list_data, tuple(data))

    def test_type_list_with_long(self, mock_list):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        mock_list.return_value = [self.fake_type]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_list.assert_called_once_with('/types', response_key='types')
        self.assertEqual(self.list_columns_long, columns)
        self.assertEqual(self.list_data_long, tuple(data))


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(instance_type_mgr.InstanceTypeManager, '_delete')
@mock.patch.object(instance_type_mgr.InstanceTypeManager, '_update')
class TestInstanceTypeSet(TestInstanceType):

    def setUp(self):
        super(TestInstanceTypeSet, self).setUp()
        self.cmd = instance_type.SetType(self.app, None)

    def test_type_set_property(self, mock_update, mock_delete, mock_find):
        arglist = [
            '--property', 'key1=value1',
            '--property', 'key2=value2',
            'type1',
        ]
        verifylist = [
            ('property',  {'key1': 'value1', 'key2': 'value2'}),
            ('type', 'type1'),
        ]
        mock_find.return_value = self.fake_type
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expected_url = '/types/%s/extraspecs' % base.getid(self.fake_type)
        expected_data = {'key1': 'value1', 'key2': 'value2'}
        mock_update.assert_called_once_with(expected_url,
                                            data=expected_data,
                                            return_raw=True)
        self.assertNotCalled(mock_delete)
        self.assertIsNone(result)

    def test_type_set_clean_property(self, mock_update, mock_delete,
                                     mock_find):
        arglist = [
            '--no-property',
            'type1',
        ]
        verifylist = [
            ('no_property', True),
            ('type', 'type1'),
        ]
        mock_find.return_value = self.fake_type
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expected_url = '/types/%s/extraspecs/key0' % base.getid(self.fake_type)
        self.assertNotCalled(mock_update)
        mock_delete.assert_called_once_with(expected_url)
        self.assertIsNone(result)

    def test_type_set_overrider_property(self, mock_update, mock_delete,
                                         mock_find):
        arglist = [
            '--property', 'key1=value1',
            '--no-property',
            'type1',
        ]
        verifylist = [
            ('property',  {'key1': 'value1'}),
            ('no_property', True),
            ('type', 'type1'),
        ]
        mock_find.return_value = self.fake_type
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expected_url = '/types/%s/extraspecs' % base.getid(self.fake_type)
        expected_data = {'key1': 'value1'}
        mock_update.assert_called_once_with(expected_url,
                                            data=expected_data,
                                            return_raw=True)
        expected_url = '/types/%s/extraspecs/key0' % base.getid(self.fake_type)
        mock_delete.assert_called_once_with(expected_url)
        self.assertIsNone(result)


@mock.patch.object(instance_type_mgr.InstanceTypeManager, '_get')
class TestInstanceTypeShow(TestInstanceType):

    def setUp(self):
        super(TestInstanceTypeShow, self).setUp()
        self.cmd = instance_type.ShowType(self.app, None)

    def test_type_show(self, mock_get):
        arglist = [
            'type1',
        ]
        verifylist = [
            ('type', 'type1'),
        ]
        mock_get.return_value = self.fake_type
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        expected_url = '/types/%s' % parsed_args.type
        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(instance_type_mgr.InstanceTypeManager, '_delete')
class TestInstanceTypeUnset(TestInstanceType):

    def setUp(self):
        super(TestInstanceTypeUnset, self).setUp()
        self.cmd = instance_type.UnsetType(self.app, None)

    def test_type_unset_property(self, mock_delete, mock_find):
        arglist = [
            '--property', 'key0=value0',
            '--property', 'key2=value2',
            'type1',
        ]
        verifylist = [
            ('property',  {'key0': 'value0', 'key2': 'value2'}),
            ('type', 'type1'),
        ]
        mock_find.return_value = self.fake_type
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expected_url = '/types/%s/extraspecs/key0' % base.getid(self.fake_type)
        mock_delete.assert_called_once_with(expected_url)
        self.assertIsNone(result)
