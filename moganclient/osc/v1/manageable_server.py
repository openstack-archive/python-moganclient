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

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import utils

from moganclient.common.i18n import _

LOG = logging.getLogger(__name__)


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

    def _ports_formatter(self, ports):
        output = []
        for port in ports:
            for key, value in port.items():
                group = "%s=%s" % (key, value)
                output.append(group)
        return '; '.join(output)

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
        formatters = {'ports': self._ports_formatter,
                      'portgroups': self._ports_formatter
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

    def _format_image_field(self, data):
        image_client = self.app.client_manager.image
        image_uuid = data._info.pop('image_uuid')
        if image_uuid:
            image = image_client.images.get(image_uuid)
            return '%s (%s)' % (image.name, image_uuid)

    def _format_flavor_field(self, data):
        bc_client = self.app.client_manager.baremetal_compute
        flavor_uuid = data._info.pop('flavor_uuid')
        if flavor_uuid:
            flavor = bc_client.flavor.get(flavor_uuid)
            return '%s (%s)' % (flavor.name, flavor_uuid)

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute

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
                'flavor': self._format_flavor_field(data),
                'image': self._format_image_field(data)
            },
        )

        info = {}
        info.update(data._info)
        return zip(*sorted(info.items()))
