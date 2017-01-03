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

from moganclient.common import base
from moganclient.osc.v1 import flavor
from moganclient.tests.unit import base as test_base
from moganclient.tests.unit import fakes
from moganclient.v1 import flavor as flavor_mgr


class TestFlavor(test_base.TestBaremetalComputeV1):
    fake_flavor = fakes.FakeFlavor.create_one_flavor()

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
        fake_flavor.created_at,
        fake_flavor.description,
        fake_flavor.extra_specs,
        fake_flavor.is_public,
        fake_flavor.name,
        fake_flavor.updated_at,
        fake_flavor.uuid,
    )


@mock.patch.object(flavor_mgr.FlavorManager, '_create')
class TestFlavorCreate(TestFlavor):
    def setUp(self):
        super(TestFlavorCreate, self).setUp()
        self.cmd = flavor.CreateFlavor(self.app, None)

    def test_flavor_create(self, mock_create):
        arglist = [
            'flavor1',
        ]
        verifylist = [
            ('name', 'flavor1'),
        ]
        mock_create.return_value = self.fake_flavor
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_create.assert_called_once_with('/types',
                                            data={
                                                'name': 'flavor1',
                                                'is_public': True,
                                                'description': None,
                                            })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_flavor_create_with_public(self, mock_create):
        arglist = [
            '--public',
            'flavor1',
        ]
        verifylist = [
            ('public', True),
            ('name', 'flavor1'),
        ]
        mock_create.return_value = self.fake_flavor
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_create.assert_called_once_with('/types',
                                            data={
                                                'name': 'flavor1',
                                                'is_public': True,
                                                'description': None,
                                            })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_flavor_create_with_private(self, mock_create):
        arglist = [
            '--private',
            'flavor1',
        ]
        verifylist = [
            ('private', True),
            ('name', 'flavor1'),
        ]
        mock_create.return_value = self.fake_flavor
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_create.assert_called_once_with('/types',
                                            data={
                                                'name': 'flavor1',
                                                'is_public': False,
                                                'description': None,
                                            })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_flavor_create_with_description(self, mock_create):
        arglist = [
            '--description', 'test description.',
            'flavor1',
        ]
        verifylist = [
            ('description', 'test description.'),
            ('name', 'flavor1'),
        ]
        mock_create.return_value = self.fake_flavor
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_create.assert_called_once_with(
            '/types',
            data={
                'name': 'flavor1',
                'is_public': True,
                'description': 'test description.',
            })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    @mock.patch.object(flavor_mgr.FlavorManager, '_get')
    @mock.patch.object(flavor_mgr.FlavorManager, '_update')
    def test_flavor_create_with_property(self, mock_update, mock_get,
                                         mock_create):
        arglist = [
            '--property', 'key1=value1',
            'flavor1',
        ]
        verifylist = [
            ('property', {'key1': 'value1'}),
            ('name', 'flavor1'),
        ]
        mock_create.return_value = self.fake_flavor
        mock_get.return_value = {'extra_specs': {'key1': 'value1'}}
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_create.assert_called_once_with('/types',
                                            data={
                                                'name': 'flavor1',
                                                'is_public': True,
                                                'description': None,
                                            })
        expected_url = '/types/%s/extraspecs' % base.getid(self.fake_flavor)
        mock_update.assert_called_once_with(expected_url,
                                            data=parsed_args.property,
                                            return_raw=True)
        mock_get.assert_called_once_with(expected_url, return_raw=True)
        self.assertEqual(self.columns, columns)
        expected_data = copy.deepcopy(self.data)
        # update extra specs
        expected_data[2].pop('key0')
        expected_data[2].update({'key1': 'value1'})
        self.assertEqual(expected_data, data)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(flavor_mgr.FlavorManager, '_delete')
class TestFlavorDelete(TestFlavor):
    def setUp(self):
        super(TestFlavorDelete, self).setUp()
        self.cmd = flavor.DeleteFlavor(self.app, None)

    def test_flavor_delete(self, mock_delete, mock_find):
        arglist = [
            'flavor1',
        ]
        verifylist = [
            ('flavor', ['flavor1']),
        ]
        mock_find.return_value = self.fake_flavor
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expected_url = '/types/%s' % base.getid(self.fake_flavor)
        mock_delete.assert_called_once_with(expected_url)
        self.assertIsNone(result)

    def test_flavor_multiple_delete(self, mock_delete, mock_find):
        arglist = [
            'flavor1',
            'flavor2',
            'flavor3'
        ]
        verifylist = [
            ('flavor', ['flavor1', 'flavor2', 'flavor3']),
        ]
        mock_find.return_value = self.fake_flavor
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expected_url = '/types/%s' % base.getid(self.fake_flavor)
        expected_call = [mock.call(expected_url), mock.call(expected_url),
                         mock.call(expected_url)]
        mock_delete.assert_has_calls(expected_call)
        self.assertIsNone(result)


@mock.patch.object(flavor_mgr.FlavorManager, '_list')
class TestFlavorList(TestFlavor):
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
        TestFlavor.fake_flavor.uuid,
        TestFlavor.fake_flavor.name,
        TestFlavor.fake_flavor.is_public,
        ),)

    list_data_long = ((
        TestFlavor.fake_flavor.uuid,
        TestFlavor.fake_flavor.name,
        TestFlavor.fake_flavor.is_public,
        TestFlavor.fake_flavor.description,
        TestFlavor.fake_flavor.extra_specs,
        ),)

    def setUp(self):
        super(TestFlavorList, self).setUp()
        self.cmd = flavor.ListFlavor(self.app, None)

    def test_flavor_list(self, mock_list):
        arglist = []
        verifylist = []
        mock_list.return_value = [self.fake_flavor]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_list.assert_called_once_with('/types', response_key='types')
        self.assertEqual(self.list_columns, columns)
        self.assertEqual(self.list_data, tuple(data))

    def test_flavor_list_with_long(self, mock_list):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        mock_list.return_value = [self.fake_flavor]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_list.assert_called_once_with('/types', response_key='types')
        self.assertEqual(self.list_columns_long, columns)
        self.assertEqual(self.list_data_long, tuple(data))


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(flavor_mgr.FlavorManager, '_delete')
@mock.patch.object(flavor_mgr.FlavorManager, '_update')
class TestFlavorSet(TestFlavor):
    def setUp(self):
        super(TestFlavorSet, self).setUp()
        self.cmd = flavor.SetFlavor(self.app, None)

    def test_flavor_set_property(self, mock_update, mock_delete, mock_find):
        arglist = [
            '--property', 'key1=value1',
            '--property', 'key2=value2',
            'flavor1',
        ]
        verifylist = [
            ('property', {'key1': 'value1', 'key2': 'value2'}),
            ('flavor', 'flavor1'),
        ]
        mock_find.return_value = self.fake_flavor
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expected_url = '/types/%s/extraspecs' % base.getid(self.fake_flavor)
        expected_data = {'key1': 'value1', 'key2': 'value2'}
        mock_update.assert_called_once_with(expected_url,
                                            data=expected_data,
                                            return_raw=True)
        self.assertNotCalled(mock_delete)
        self.assertIsNone(result)

    def test_flavor_set_clean_property(self, mock_update, mock_delete,
                                       mock_find):
        arglist = [
            '--no-property',
            'flavor1',
        ]
        verifylist = [
            ('no_property', True),
            ('flavor', 'flavor1'),
        ]
        mock_find.return_value = self.fake_flavor
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expected_url = '/types/%s/extraspecs/key0' % base.getid(
            self.fake_flavor)
        self.assertNotCalled(mock_update)
        mock_delete.assert_called_once_with(expected_url)
        self.assertIsNone(result)

    def test_flavor_set_overrider_property(self, mock_update, mock_delete,
                                           mock_find):
        arglist = [
            '--property', 'key1=value1',
            '--no-property',
            'flavor1',
        ]
        verifylist = [
            ('property', {'key1': 'value1'}),
            ('no_property', True),
            ('flavor', 'flavor1'),
        ]
        mock_find.return_value = self.fake_flavor
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expected_url = '/types/%s/extraspecs' % base.getid(self.fake_flavor)
        expected_data = {'key1': 'value1'}
        mock_update.assert_called_once_with(expected_url,
                                            data=expected_data,
                                            return_raw=True)
        expected_url = '/types/%s/extraspecs/key0' % base.getid(
            self.fake_flavor)
        mock_delete.assert_called_once_with(expected_url)
        self.assertIsNone(result)


@mock.patch.object(flavor_mgr.FlavorManager, '_get')
class TestFlavorShow(TestFlavor):
    def setUp(self):
        super(TestFlavorShow, self).setUp()
        self.cmd = flavor.ShowFlavor(self.app, None)

    def test_flavor_show(self, mock_get):
        arglist = [
            'flavor1',
        ]
        verifylist = [
            ('flavor', 'flavor1'),
        ]
        mock_get.return_value = self.fake_flavor
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        expected_url = '/types/%s' % parsed_args.flavor
        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(flavor_mgr.FlavorManager, '_delete')
class TestFlavorUnset(TestFlavor):
    def setUp(self):
        super(TestFlavorUnset, self).setUp()
        self.cmd = flavor.UnsetFlavor(self.app, None)

    def test_flavor_unset_property(self, mock_delete, mock_find):
        arglist = [
            '--property', 'key0',
            '--property', 'key2',
            'flavor1',
        ]
        verifylist = [
            ('property', ['key0', 'key2']),
            ('flavor', 'flavor1'),
        ]
        mock_find.return_value = self.fake_flavor
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expected_url = '/types/%s/extraspecs/key0' % base.getid(
            self.fake_flavor)
        mock_delete.assert_called_once_with(expected_url)
        self.assertIsNone(result)
