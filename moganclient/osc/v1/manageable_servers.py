#   Copyright 2017 Fiberhome, Inc. All rights reserved.
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


"""Mogan v1 manageable servers action implementations"""

import logging

from osc_lib.command import command

LOG = logging.getLogger(__name__)


class ListManageableServers(command.Lister):
    """List all manageable servers"""

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute

        data = bc_client.manageable_servers.list()
        return (('manageable_servers',),
                tuple((d,) for d in data))
