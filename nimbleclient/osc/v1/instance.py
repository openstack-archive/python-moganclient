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


"""Nimble v1 Instance action implementations"""

import logging

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from nimbleclient.common.i18n import _


LOG = logging.getLogger(__name__)


class CreateInstance(command.ShowOne):
    """Create a new instance"""

    def get_parser(self, prog_name):
        parser = super(CreateInstance, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help=_("New instance name")
        )
        parser.add_argument(
            "--type",
            metavar="<type>",
            required=True,
            help=_("ID or Name of instance type"),
        )
        parser.add_argument(
            "--image",
            metavar="<image>",
            required=True,
            help=_("ID or Name of image"),
        )
        parser.add_argument(
            "--nic",
            metavar="uuid=NETWORK[,port-type=PORT_TYPE]",
            required_keys=['uuid'],
            optional_keys=['port-type'],
            action=parseractions.MultiKeyValueAction,
            help=_("Create a NIC on the instance. "
                   "(repeat option to create multiple NICs)"),
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Instance description"),
        )
        parser.add_argument(
            "--availability-zone",
            metavar="<zone-name>",
            help=_("The availability zone for instance placement"),
        )
        parser.add_argument(
            "--extra",
            metavar="<extra>",
            help=_("The extra information for instance"),
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        type_data = utils.find_resource(
            bc_client.instance_type,
            parsed_args.type)
        image_data = utils.find_resource(
            self.app.client_manager.image.images,
            parsed_args.image)

        data = bc_client.instance.create(
            name=parsed_args.name,
            image_uuid=image_data.id,
            instance_type_uuid=type_data.uuid,
            description=parsed_args.description,
            networks=parsed_args.nic,
            availability_zone=parsed_args.availability_zone,
            extra=parsed_args.extra
        )
        info = {}
        info.update(data._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteInstance(command.Command):
    """Delete existing instance(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteInstance, self).get_parser(prog_name)
        parser.add_argument(
            'instance',
            metavar='<instance>',
            nargs='+',
            help=_("Instance(s) to delete (name or UUID)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        result = 0
        for one_instance in parsed_args.instance:
            try:
                data = utils.find_resource(
                    bc_client.instance, one_instance)
                bc_client.instance.delete(data.uuid)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete instance with name or UUID "
                            "'%(instance)s': %(e)s") %
                          {'instance': one_instance, 'e': e})

        if result > 0:
            total = len(parsed_args.instance)
            msg = (_("%(result)s of %(total)s instances failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListInstance(command.Lister):
    """List all instances"""

    def get_parser(self, prog_name):
        parser = super(ListInstance, self).get_parser(prog_name)
        parser.add_argument(
            '--detailed',
            action='store_true',
            default=False,
            help=_("List additional with details.")
        )
        return parser

    @staticmethod
    def _networks_formatter(data):
        network_info = getattr(data, 'network_info')
        return_info = []
        for port_uuid in network_info:
            port_ips = []
            for fixed_ip in network_info[port_uuid]['fixed_ips']:
                port_ips.append(fixed_ip['ip_address'])
            return_info.append(', '.join(port_ips))
        return '; '.join(return_info)

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute

        if parsed_args.detailed:
            data = bc_client.instance.list(detailed=True)
            formatters = {'network_info': self._networks_formatter}
            # This is the easiest way to change column headers
            column_headers = (
                "UUID",
                "Name",
                "Instance Type",
                "Status",
                "Image",
                "Description",
                "Availability Zone",
                "Networks"
            )
            columns = (
                "uuid",
                "name",
                "instance_type_uuid",
                "status",
                "image_uuid",
                "description",
                "availability_zone",
                "network_info"
            )
        else:
            data = bc_client.instance.list()
            formatters = None
            column_headers = (
                "UUID",
                "Name",
                "Status",
            )
            columns = (
                "uuid",
                "name",
                "status",
            )

        return (column_headers,
                (utils.get_item_properties(
                    s, columns, formatters=formatters
                ) for s in data))


class ShowInstance(command.ShowOne):
    """Display instance details"""

    def get_parser(self, prog_name):
        parser = super(ShowInstance, self).get_parser(prog_name)
        parser.add_argument(
            'instance',
            metavar='<instance>',
            help=_("Instance to display (name or UUID)")
        )
        return parser

    def take_action(self, parsed_args):

        bc_client = self.app.client_manager.baremetal_compute
        data = utils.find_resource(
            bc_client.instance,
            parsed_args.instance,
        )

        info = {}
        info.update(data._info)
        return zip(*sorted(six.iteritems(info)))
