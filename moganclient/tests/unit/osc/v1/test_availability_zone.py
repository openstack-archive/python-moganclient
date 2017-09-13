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

from moganclient.osc.v1 import availability_zone
from moganclient.tests.unit import base as test_base
from moganclient.v1 import availability_zone as az_mgr


@mock.patch.object(az_mgr.AvailabilityZoneManager, '_list')
class TestAvailabilityZoneList(test_base.TestBaremetalComputeV1):
    def setUp(self):
        super(TestAvailabilityZoneList, self).setUp()
        self.cmd = availability_zone.ListAvailabilityZone(self.app, None)
        self.fake_az = ("az1", "az2", "az3")

    def test_list_az(self, mock_list):
        arglist = []
        verifylist = []
        mock_list.return_value = [self.fake_az]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_list.assert_called_once_with('/availability_zones',
                                          response_key='availability_zones')
        self.assertEqual(('Zone Name',), columns)
        self.assertEqual(((('az1', 'az2', 'az3'),),), data)
