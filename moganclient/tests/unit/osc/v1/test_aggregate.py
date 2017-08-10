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

import mock

from osc_lib import utils

from moganclient.common import base
from moganclient.osc.v1 import aggregate
from moganclient.tests.unit import base as test_base
from moganclient.tests.unit import fakes
from moganclient.v1 import aggregate as aggregate_mgr


class TestAggregateBase(test_base.TestBaremetalComputeV1):
    fake_agg = fakes.FakeAggregate.create_one_aggregate()

    columns = (
        'created_at',
        'links',
        'metadata',
        'name',
        'updated_at',
        'uuid',
    )

    data = (
        fake_agg.created_at,
        fake_agg.links,
        fake_agg.metadata,
        fake_agg.name,
        fake_agg.updated_at,
        fake_agg.uuid,
    )


@mock.patch.object(aggregate_mgr.AggregateManager, '_create')
class TestAggregateCreate(TestAggregateBase):
    def setUp(self):
        super(TestAggregateCreate, self).setUp()
        self.cmd = aggregate.CreateAggregate(self.app, None)

    def test_aggregate_create(self, mock_create):
        arglist = [
            'test_agg',
            '--metadata', 'k1=v1'
        ]
        verifylist = [
            ('name', 'test_agg'),
            ('metadata', {'k1': 'v1'}),
        ]
        mock_create.return_value = self.fake_agg
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_create.assert_called_once_with('/aggregates',
                                            data={
                                                'name': 'test_agg',
                                                'metadata': {'k1': 'v1'},
                                            })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(aggregate_mgr.AggregateManager, '_delete')
class TestAggregateDelete(TestAggregateBase):
    def setUp(self):
        super(TestAggregateDelete, self).setUp()
        self.cmd = aggregate.DeleteAggregate(self.app, None)

    def test_aggregate_delete(self, mock_delete, mock_find):
        arglist = [
            'test_agg1',
        ]
        verifylist = [
            ('aggregate', ['test_agg1']),
        ]
        mock_find.return_value = self.fake_agg
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expected_url = '/aggregates/%s' % base.getid(self.fake_agg)
        mock_delete.assert_called_once_with(expected_url)
        self.assertIsNone(result)

    def test_aggregate_multiple_delete(self, mock_delete, mock_find):
        arglist = [
            'agg1',
            'agg2',
            'agg3'
        ]
        verifylist = [
            ('aggregate', ['agg1', 'agg2', 'agg3']),
        ]
        mock_find.return_value = self.fake_agg
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        expected_url = '/aggregates/%s' % base.getid(self.fake_agg)
        expected_call = [mock.call(expected_url), mock.call(expected_url),
                         mock.call(expected_url)]
        mock_delete.assert_has_calls(expected_call)
        self.assertIsNone(result)


@mock.patch.object(aggregate_mgr.AggregateManager, '_list')
class TestAggregateList(TestAggregateBase):
    list_columns = (
        "UUID",
        "Name",
        "Metadata"
    )

    list_data = ((
        TestAggregateBase.fake_agg.uuid,
        TestAggregateBase.fake_agg.name,
        TestAggregateBase.fake_agg.metadata,
        ),)

    def setUp(self):
        super(TestAggregateList, self).setUp()
        self.cmd = aggregate.ListAggregate(self.app, None)

    def test_aggregate_list(self, mock_list):
        arglist = []
        verifylist = []
        mock_list.return_value = [self.fake_agg]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_list.assert_called_once_with('/aggregates',
                                          response_key='aggregates')
        self.assertEqual(self.list_columns, columns)
        self.assertEqual(self.list_data, tuple(data))


@mock.patch.object(aggregate_mgr.AggregateManager, '_get')
class TestAggregateShow(TestAggregateBase):
    def setUp(self):
        super(TestAggregateShow, self).setUp()
        self.cmd = aggregate.ShowAggregate(self.app, None)

    def test_agregate_show(self, mock_get):
        arglist = [
            'agg1',
        ]
        verifylist = [
            ('aggregate', 'agg1'),
        ]
        mock_get.return_value = self.fake_agg
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        expected_url = '/aggregates/%s' % parsed_args.aggregate
        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


@mock.patch.object(utils, 'find_resource')
@mock.patch.object(aggregate_mgr.AggregateManager, '_update')
class TestAggregateUpdate(TestAggregateBase):
    def setUp(self):
        super(TestAggregateUpdate, self).setUp()
        self.cmd = aggregate.UpdateAggregate(self.app, None)

    def test_aggregate_update(self, mock_update, mock_find):
        mock_find.return_value = self.fake_agg
        arglist = [
            '--name', 'test_agg',
            '--set-metadata', 'k1=v1',
            '--unset-metadata', 'key1',
            self.fake_agg.uuid,
        ]
        verifylist = [
            ('aggregate', self.fake_agg.uuid),
            ('name', 'test_agg'),
            ('unset_metadata', ['key1']),
            ('set_metadata', {'k1': 'v1', 'k2': 'v2'}),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        expected_url = '/aggregates/%s' % base.getid(self.fake_agg)
        expected_args = [
            {'path': '/name', 'value': 'test_agg', 'op': 'replace'},
            {'path': '/metadata/k1', 'value': 'v1', 'op': 'add'},
            {'path': '/metadata/key1', 'op': 'remove'}
        ]
        mock_update.assert_called_once_with(expected_url,
                                            data=expected_args)


@mock.patch.object(aggregate_mgr.AggregateNodeManager, '_list')
class TestAggregateListNode(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestAggregateListNode, self).setUp()
        self.cmd = aggregate.AggregateListNode(self.app, None)
        self.fake_nodes = ("node-1", "node-1", "node-1")

    def test_agg_node_list(self, mock_list):
        arglist = [
            'agg1-uuid',
        ]
        verifylist = [
            ('aggregate', 'agg1-uuid'),
        ]
        mock_list.return_value = [self.fake_nodes]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        url = '/aggregates/agg1-uuid/nodes'
        mock_list.assert_called_once_with(url, response_key='nodes')
        self.assertEqual(('Node',), columns)
        self.assertEqual(((("node-1", "node-1", "node-1"),),), data)


@mock.patch.object(aggregate_mgr.AggregateNodeManager, '_create')
class TestAggregateAddNode(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestAggregateAddNode, self).setUp()
        self.cmd = aggregate.AggregateAddNode(self.app, None)

    def test_agg_node_add(self, mock_create):
        arglist = [
            'agg1-uuid', 'node-1',
        ]
        verifylist = [
            ('aggregate', 'agg1-uuid'),
            ('node', 'node-1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        url = '/aggregates/agg1-uuid/nodes'
        mock_create.assert_called_once_with(url, data={'node': 'node-1'})


@mock.patch.object(aggregate_mgr.AggregateNodeManager, '_delete')
class TestAggregateRemoveNode(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestAggregateRemoveNode, self).setUp()
        self.cmd = aggregate.AggregateRemoveNode(self.app, None)

    def test_agg_node_remove(self, mock_delete):
        arglist = [
            'agg1-uuid', 'node-1',
        ]
        verifylist = [
            ('aggregate', 'agg1-uuid'),
            ('node', 'node-1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        url = '/aggregates/agg1-uuid/nodes/node-1'
        mock_delete.assert_called_once_with(url)
