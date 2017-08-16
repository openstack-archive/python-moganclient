#   Copyright 2017 Huawei, Inc. All rights reserved.
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

import fixtures
import mock

from osc_lib import exceptions
from osc_lib import utils

from moganclient.osc.v1 import server_group
from moganclient.tests.unit import base as test_base
from moganclient.tests.unit import fakes


class TestServerGroup(test_base.TestBaremetalComputeV1):
    fake_server_group = fakes.FakeServerGroup.create_one_server_group()

    columns = (
        'uuid',
        'name',
        'user_id',
        'project_id',
        'members',
        'policies',
    )

    data = (
        fake_server_group.uuid,
        fake_server_group.name,
        fake_server_group.user_id,
        fake_server_group.project_id,
        utils.format_list(fake_server_group.members),
        utils.format_list(fake_server_group.policies),
    )

    def setUp(self):
        self.server_group_mock = mock.Mock()
        self.useFixture(fixtures.MockPatch(
            'moganclient.v1.server_group.ServerGroupManager',
            return_value=self.server_group_mock))
        super(TestServerGroup, self).setUp()


class TestServerGroupCreate(TestServerGroup):

    def setUp(self):
        super(TestServerGroupCreate, self).setUp()
        self.server_group_mock.create.return_value = self.fake_server_group
        self.cmd = server_group.CreateServerGroup(self.app, None)

    def test_server_group_create(self):
        arglist = [
            '--policy', 'anti-affinity',
            'affinity_group',
        ]
        verifylist = [
            ('policy', 'anti-affinity'),
            ('name', 'affinity_group'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.server_group_mock.create.assert_called_once_with(
            name=parsed_args.name,
            policies=[parsed_args.policy],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestServerGroupDelete(TestServerGroup):

    def setUp(self):
        super(TestServerGroupDelete, self).setUp()
        self.server_group_mock.get.return_value = self.fake_server_group
        self.cmd = server_group.DeleteServerGroup(self.app, None)

    def test_server_group_delete(self):
        arglist = [
            'affinity_group',
        ]
        verifylist = [
            ('server_group', ['affinity_group']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.server_group_mock.get.assert_called_once_with('affinity_group')
        self.server_group_mock.delete.assert_called_once_with(
            self.fake_server_group.uuid
        )
        self.assertIsNone(result)

    def test_server_group_multiple_delete(self):
        arglist = [
            'affinity_group',
            'anti_affinity_group'
        ]
        verifylist = [
            ('server_group', ['affinity_group', 'anti_affinity_group']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.server_group_mock.get.assert_any_call('affinity_group')
        self.server_group_mock.get.assert_any_call('anti_affinity_group')
        self.server_group_mock.delete.assert_called_with(
            self.fake_server_group.uuid
        )
        self.assertEqual(2, self.server_group_mock.get.call_count)
        self.assertEqual(2, self.server_group_mock.delete.call_count)
        self.assertIsNone(result)

    def test_server_group_multiple_delete_with_exception(self):
        arglist = [
            'affinity_group',
            'anti_affinity_group'
        ]
        verifylist = [
            ('server_group', ['affinity_group', 'anti_affinity_group']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        find_mock_result = [self.fake_server_group, exceptions.CommandError]
        with mock.patch.object(utils, 'find_resource',
                               side_effect=find_mock_result) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual(
                    '1 of 2 baremetal server groups failed to delete.',
                    str(e))

            find_mock.assert_any_call(self.server_group_mock,
                                      'affinity_group')
            find_mock.assert_any_call(self.server_group_mock,
                                      'anti_affinity_group')

            self.assertEqual(2, find_mock.call_count)
            self.server_group_mock.delete.assert_called_once_with(
                self.fake_server_group.uuid
            )


class TestServerGroupList(TestServerGroup):

    list_columns = (
        'UUID',
        'Name',
        'Policies',
    )

    list_columns_long = (
        'UUID',
        'Name',
        'Policies',
        'Members',
        'Project Id',
        'User Id',
    )

    list_data = ((
        TestServerGroup.fake_server_group.uuid,
        TestServerGroup.fake_server_group.name,
        utils.format_list(TestServerGroup.fake_server_group.policies),
    ),)

    list_data_long = ((
        TestServerGroup.fake_server_group.uuid,
        TestServerGroup.fake_server_group.name,
        utils.format_list(TestServerGroup.fake_server_group.policies),
        utils.format_list(TestServerGroup.fake_server_group.members),
        TestServerGroup.fake_server_group.project_id,
        TestServerGroup.fake_server_group.user_id,
    ),)

    def setUp(self):
        super(TestServerGroupList, self).setUp()

        self.server_group_mock.list.return_value = [self.fake_server_group]
        self.cmd = server_group.ListServerGroup(self.app, None)

    def test_server_group_list(self):
        arglist = []
        verifylist = [
            ('all_projects', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.server_group_mock.list.assert_called_once_with(False)

        self.assertEqual(self.list_columns, columns)
        self.assertEqual(self.list_data, tuple(data))

    def test_server_group_list_with_all_projects_and_long(self):
        arglist = [
            '--all-projects',
            '--long',
        ]
        verifylist = [
            ('all_projects', True),
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.server_group_mock.list.assert_called_once_with(True)

        self.assertEqual(self.list_columns_long, columns)
        self.assertEqual(self.list_data_long, tuple(data))


class TestServerGroupShow(TestServerGroup):

    def setUp(self):
        super(TestServerGroupShow, self).setUp()

        self.server_group_mock.get.return_value = self.fake_server_group
        self.cmd = server_group.ShowServerGroup(self.app, None)

    def test_server_group_show(self):
        arglist = [
            'affinity_group',
        ]
        verifylist = [
            ('server_group', 'affinity_group'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
