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
from osc_lib import utils

LOG = logging.getLogger(__name__)


class ListManageableServers(command.Lister):
    """List all manageable servers"""

    def get_parser(self, prog_name):
        parser = super(ListManageableServers, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute

        if parsed_args.long:
            # This is the easiest way to change column headers
            column_headers = (
                "UUID",
                "Name",
                "Power State",
                "Provision State",
                "Image Id",
                "Resource Class",
                "Ports",
                "Port Groups"
            )
            columns = (
                "uuid",
                "name",
                "power_state",
                "provision_state",
                "image_source",
                "resource_class",
                "ports",
                "portgroups"
            )
        else:
            column_headers = (
                "UUID",
                "Name",
                "Power State",
                "Provision State",
                "Image Id",
                "Resource Class"
            )
            columns = (
                "uuid",
                "name",
                "power_state",
                "provision_state",
                "image_source",
                "resource_class"
            )

        data = bc_client.manageable_servers.list()
        return (column_headers,
                (utils.get_item_properties(
                    s, columns) for s in data))
