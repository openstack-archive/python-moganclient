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

import json

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import utils

from moganclient.common.i18n import _
from moganclient.common import utils as cli_utils


class ListManageableServer(command.Lister):
    """List all manageable servers"""

    def get_parser(self, prog_name):
        parser = super(ListManageableServer, self).get_parser(prog_name)
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

        data = bc_client.manageable_server.list()
        net_formatter = lambda s: json.dumps(s, indent=2, sort_keys=True)
        formatters = {'ports': net_formatter,
                      'portgroups': net_formatter
                      }
        return (column_headers,
                (utils.get_item_properties(
                    s, columns, formatters=formatters) for s in data))


class ManageServer(command.ShowOne):
    """Manage an existing bare metal node"""

    def get_parser(self, prog_name):
        parser = super(ManageServer, self).get_parser(prog_name)
        parser.add_argument(
            "node_uuid",
            metavar="<node_uuid>",
            help=_("The manageable bare metal node uuid")
        )
        parser.add_argument(
            "name",
            metavar="<name>",
            help=_("New bare metal server name")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Bare metal server description"),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Set a property on this server '
                   '(repeat option to set multiple values)'),
        )

        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        image_client = self.app.client_manager.image
        network_client = self.app.client_manager.network

        boot_kwargs = dict(
            name=parsed_args.name,
            node_uuid=parsed_args.node_uuid,
            description=parsed_args.description,
            metadata=parsed_args.property
        )

        data = bc_client.manageable_server.manage(**boot_kwargs)
        data._info.update(
            {
                'properties': utils.format_dict(data._info.pop('metadata')),
                'partitions': utils.format_dict(data._info.pop('partitions')),
                'flavor': cli_utils.flavor_formatter(
                    bc_client, data._info.pop('flavor_uuid')),
                'image': cli_utils.image_formatter(
                    image_client, data._info.pop('image_uuid')),
                'addresses': cli_utils.addresses_formatter(
                    network_client,
                    data._info.pop('addresses'))
            },
        )

        info = {}
        info.update(data._info)
        return zip(*sorted(info.items()))
