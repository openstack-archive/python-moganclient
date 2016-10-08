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


"""Nimble v1 Type action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from nimbleclient.common.i18n import _


LOG = logging.getLogger(__name__)


class CreateType(command.ShowOne):
    """Create a new instance type"""

    def get_parser(self, prog_name):
        parser = super(CreateType, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help=_("New type name")
        )
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            action="store_true",
            help=_("Type is available to other projects (default)")
        )
        public_group.add_argument(
            "--private",
            action="store_true",
            help=_("Type is not available to other projects")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Type description"),
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute

        info = {}
        is_public = True
        if parsed_args.public:
            is_public = True
        if parsed_args.private:
            is_public = False

        data = bc_client.instance_type.create(
            name=parsed_args.name,
            is_public=is_public,
            description=parsed_args.description,
        )
        info.update(data._info)

        return zip(*sorted(six.iteritems(info)))


class DeleteType(command.Command):
    """Delete existing instance type(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteType, self).get_parser(prog_name)
        parser.add_argument(
            'type',
            metavar='<type>',
            nargs='+',
            help=_("Type(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        result = 0
        for one_type in parsed_args.type:
            try:
                data = utils.find_resource(
                    bc_client.instance_type, one_type)
                bc_client.instance_type.delete(data.id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete type with name or ID '%(type)s':"
                            " %(e)s") % {'type': one_type, 'e': e})

        if result > 0:
            total = len(parsed_args.type)
            msg = (_("%(result)s of %(total)s types failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListType(command.Lister):
    """List all types"""

    def get_parser(self, prog_name):
        parser = super(ListType, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute

        data = bc_client.instance_type.list()

        if parsed_args.long:
            # This is the easiest way to change column headers
            column_headers = (
                "UUID",
                "Name",
                "Is Public",
                "Description",
                "Properties",
            )
            columns = (
                "UUID",
                "Name",
                "Is Public",
                "Description",
                "Extra Specs",
            )
        else:
            column_headers = columns = (
                "UUID",
                "Name",
                "Is Public",
            )

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowType(command.ShowOne):
    """Display instance type details"""

    def get_parser(self, prog_name):
        parser = super(ShowType, self).get_parser(prog_name)
        parser.add_argument(
            'type',
            metavar='<type>',
            help=_("Type to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):

        bc_client = self.app.client_manager.baremetal_compute
        data = utils.find_resource(
            bc_client.instance_type,
            parsed_args.type,
        )

        info = {}
        info.update(data._info)
        return zip(*sorted(six.iteritems(info)))
