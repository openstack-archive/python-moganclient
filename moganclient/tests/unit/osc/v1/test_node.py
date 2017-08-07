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

from moganclient.osc.v1 import node
from moganclient.tests.unit import base as test_base
from moganclient.v1 import node as node_mgr


@mock.patch.object(node_mgr.NodeManager, '_list')
class TestNodeList(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestNodeList, self).setUp()
        self.cmd = node.ListNode(self.app, None)
        self.fake_node = ("node-1", "node-2", "node-3")

    def test_list_node(self, mock_list):
        arglist = []
        verifylist = []
        mock_list.return_value = [self.fake_node]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_list.assert_called_once_with('/nodes', response_key='nodes')
        self.assertEqual(('Node',), columns)
        self.assertEqual(((("node-1", "node-2", "node-3"),),), data)
