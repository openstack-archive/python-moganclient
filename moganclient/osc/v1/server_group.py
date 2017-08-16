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

"""Mogan v1 Baremetal Server Group action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


_formatters = {
    'policies': utils.format_list,
    'members': utils.format_list,
}


class CreateServerGroup(command.ShowOne):
    """Create a new baremetal server group"""

    def get_parser(self, prog_name):
        parser = super(CreateServerGroup, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_("New baremetal server group name")
        )
        parser.add_argument(
            '--policy',
            metavar='<policy>',
            choices=['affinity', 'anti-affinity'],
            default='affinity',
            help=_("Add a policy to <name> "
                   "('affinity' or 'anti-affinity', "
                   "default to 'affinity')")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        info = {}
        server_group = bc_client.server_group.create(
            name=parsed_args.name,
            policies=[parsed_args.policy])
        info.update(server_group._info)

        columns = (
            'uuid',
            'name',
            'user_id',
            'project_id',
            'members',
            'policies',
        )
        data = utils.get_dict_properties(info, columns,
                                         formatters=_formatters)
        return columns, data


class DeleteServerGroup(command.Command):
    """Delete existing baremetal server group(s)."""

    def get_parser(self, prog_name):
        parser = super(DeleteServerGroup, self).get_parser(prog_name)
        parser.add_argument(
            'server_group',
            metavar='<server-group>',
            nargs='+',
            help=_("Baremetal server group(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        result = 0
        for group in parsed_args.server_group:
            try:
                group_obj = utils.find_resource(bc_client.server_group,
                                                group)
                bc_client.server_group.delete(group_obj.uuid)
            # Catch all exceptions in order to avoid to block the next deleting
            except Exception as e:
                result += 1
                LOG.error(e)

        if result > 0:
            total = len(parsed_args.server_group)
            msg = _("%(result)s of %(total)s baremetal server groups failed "
                    "to delete.")
            raise exceptions.CommandError(
                msg % {"result": result,
                       "total": total}
            )


class ListServerGroup(command.Lister):
    """List all baremetal server groups."""

    def get_parser(self, prog_name):
        parser = super(ListServerGroup, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_("Display information from all projects (admin only)")
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        data = bc_client.server_group.list(parsed_args.all_projects)

        if parsed_args.long:
            column_headers = columns = (
                'UUID',
                'Name',
                'Policies',
                'Members',
                'Project Id',
                'User Id',
            )
        else:
            column_headers = columns = (
                'UUID',
                'Name',
                'Policies',
            )

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={
                        'Policies': utils.format_list,
                        'Members': utils.format_list,
                    }
                ) for s in data))


class ShowServerGroup(command.ShowOne):
    """Display baremetal server group details."""

    def get_parser(self, prog_name):
        parser = super(ShowServerGroup, self).get_parser(prog_name)
        parser.add_argument(
            'server_group',
            metavar='<server-group>',
            help=_("Baremetal server group to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        group = utils.find_resource(bc_client.server_group,
                                    parsed_args.server_group)
        info = {}
        info.update(group._info)
        columns = (
            'uuid',
            'name',
            'user_id',
            'project_id',
            'members',
            'policies',
        )
        data = utils.get_dict_properties(info, columns,
                                         formatters=_formatters)
        return columns, data
