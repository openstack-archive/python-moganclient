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


"""Mogan v1 Baremetal flavor action implementations"""

import logging

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from oslo_utils import strutils

from moganclient.common.i18n import _

LOG = logging.getLogger(__name__)


class CreateFlavor(command.ShowOne):
    """Create a new baremetal flavor"""

    def get_parser(self, prog_name):
        parser = super(CreateFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help=_("New baremetal flavor name")
        )
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            action="store_true",
            help=_("Flavor is available to other projects (default)")
        )
        public_group.add_argument(
            "--private",
            action="store_true",
            help=_("Flavor is not available to other projects")
        )
        public_group.add_argument(
            "--disabled",
            metavar='<disabled|True>',
            default=False,
            help=_("Flavor is disabled for users.")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Flavor description"),
        )
        parser.add_argument(
            "--resource",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Resource to add to this flavor "
                   "(repeat option to set multiple resources)")
        )
        parser.add_argument(
            "--resource-aggregate",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Aggregate metadata to add to this flavor "
                   "(repeat option to set multiple aggregate metadata)")
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

        data = bc_client.flavor.create(
            name=parsed_args.name,
            description=parsed_args.description,
            resource=parsed_args.resource,
            resource_aggregate=parsed_args.resource_aggregate,
            is_public=is_public,
            disabled=parsed_args.disabled,
        )

        data._info.update(
            {
                'resources': utils.format_dict(
                    data._info.get('resources', {})),
                'resource_aggregates': utils.format_dict(
                    data._info.get('resource_aggregates', {})),
            },
        )
        info.update(data._info)

        return zip(*sorted(info.items()))


class DeleteFlavor(command.Command):
    """Delete existing baremetal flavor(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteFlavor, self).get_parser(prog_name)
        parser.add_argument(
            'flavor',
            metavar='<flavor>',
            nargs='+',
            help=_("Flavor(s) to delete (name or UUID)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        result = 0
        for one_flavor in parsed_args.flavor:
            try:
                data = utils.find_resource(
                    bc_client.flavor, one_flavor)
                bc_client.flavor.delete(data.uuid)
            except Exception as e:
                result += 1
                LOG.error("Failed to delete flavor with name or UUID "
                          "'%(flavor)s': %(e)s",
                          {'flavor': one_flavor, 'e': e})

        if result > 0:
            total = len(parsed_args.flavor)
            msg = (_("%(result)s of %(total)s flavors failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListFlavor(command.Lister):
    """List all baremetal flavors"""

    def get_parser(self, prog_name):
        parser = super(ListFlavor, self).get_parser(prog_name)
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
            column_headers = (
                "UUID",
                "Name",
                "Is Public",
                "Description",
                "Resources",
                "Aggregates",
                "Disabled",
            )
            columns = (
                "uuid",
                "name",
                "is_public",
                "description",
                "resources",
                "resource_aggregates",
                "disabled",
            )
        else:
            column_headers = (
                "UUID",
                "Name",
                "Is Public",
                "Description",
                "Resources",
            )
            columns = (
                "uuid",
                "name",
                "is_public",
                "description",
                "resources",
            )

        data = bc_client.flavor.list()
        formatters = {'resources': utils.format_dict,
                      'resource_aggregates': utils.format_dict
                      }
        return (column_headers,
                (utils.get_item_properties(
                    s, columns, formatters=formatters) for s in data))


class ShowFlavor(command.ShowOne):
    """Display baremetal flavor details"""

    def get_parser(self, prog_name):
        parser = super(ShowFlavor, self).get_parser(prog_name)
        parser.add_argument(
            'flavor',
            metavar='<flavor>',
            help=_("Flavor to display (name or UUID)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        data = utils.find_resource(
            bc_client.flavor,
            parsed_args.flavor,
        )

        data._info.update(
            {
                'resources': utils.format_dict(
                    data._info.get('resources', {})),
                'resource_aggregates': utils.format_dict(
                    data._info.get('resource_aggregates', {})),
            },
        )
        info = {}
        info.update(data._info)
        return zip(*sorted(info.items()))


class SetFlavor(command.Command):
    """Set baremetal flavor properties"""

    def get_parser(self, prog_name):
        parser = super(SetFlavor, self).get_parser(prog_name)
        parser.add_argument(
            'flavor',
            metavar='<flavor>',
            help=_("Flavor to modify (name or UUID)")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Set flavor access to project (name or ID) '
                   '(admin only)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set a new name to a flavor (admin only)')
        )
        parser.add_argument(
            '--is-public',
            metavar='<is-public>',
            type=strutils.bool_from_string,
            help=_('Set a flavor to be public or private '
                   '(admin only)'),
        )
        parser.add_argument(
            '--disabled',
            metavar='<disabled>',
            type=strutils.bool_from_string,
            help=_('Set a flavor to be disabled or enabled '
                   '(admin only)'),
        )
        return parser

    def take_action(self, parsed_args):

        bc_client = self.app.client_manager.baremetal_compute
        data = utils.find_resource(
            bc_client.flavor,
            parsed_args.flavor,
        )
        updates = []
        if parsed_args.name:
            updates.append({"op": "replace",
                            "path": "/name",
                            "value": parsed_args.name})
        if parsed_args.is_public is not None:
            updates.append({"op": "replace",
                            "path": "/is_public",
                            "value": parsed_args.is_public})
        if parsed_args.disabled is not None:
            updates.append({"op": "replace",
                            "path": "/disabled",
                            "value": parsed_args.disabled})
        if updates:
            bc_client.flavor.update(data, updates)
        if parsed_args.project:
            if data.is_public:
                msg = _("Cannot set access for a public flavor")
                raise exceptions.CommandError(msg)
            else:
                bc_client.flavor.add_tenant_access(
                    data, parsed_args.project)


class UnsetFlavor(command.Command):
    """Unset baremetal flavor properties"""

    def get_parser(self, prog_name):
        parser = super(UnsetFlavor, self).get_parser(prog_name)
        parser.add_argument(
            'flavor',
            metavar='<flavor>',
            help=_("Flavor to modify (name or UUID)")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Remove flavor access from project (name or ID) '
                   '(admin only)'),
        )
        return parser

    def take_action(self, parsed_args):

        bc_client = self.app.client_manager.baremetal_compute
        data = utils.find_resource(
            bc_client.flavor,
            parsed_args.flavor,
        )
        if parsed_args.project:
            if data.is_public:
                msg = _("Cannot remove access for a public flavor")
                raise exceptions.CommandError(msg)
            else:
                bc_client.flavor.remove_tenant_access(
                    data, parsed_args.project)
