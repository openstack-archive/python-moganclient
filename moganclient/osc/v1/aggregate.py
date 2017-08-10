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

"""Mogan v1 Baremetal node aggregate action implementations"""

import copy
import logging

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from moganclient.common.i18n import _

LOG = logging.getLogger(__name__)


class CreateAggregate(command.ShowOne):
    """Create a node aggregate"""

    def get_parser(self, prog_name):
        parser = super(CreateAggregate, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help=_("Name of baremetal node aggregate")
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Property to add to this node aggregate "
                   "(repeat option to set multiple properties)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        data = bc_client.aggregate.create(parsed_args.name,
                                          parsed_args.property)
        # Special mapping for columns to make the output easier to read:
        # 'metadata' --> 'properties'
        data._info.update(
            {
                'properties': utils.format_dict(data._info.pop('metadata')),
            },
        )
        info = copy.copy(data._info)
        return zip(*sorted(info.items()))


class DeleteAggregate(command.Command):
    """Delete existing baremetal node aggregate(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteAggregate, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            nargs='+',
            help=_("Aggregate(s) to delete (name or UUID)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        result = 0
        for one_aggregate in parsed_args.aggregate:
            try:
                data = utils.find_resource(
                    bc_client.aggregate, one_aggregate)
                bc_client.aggregate.delete(data.uuid)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete node aggregate with name or "
                            "UUID '%(aggregate)s': %(e)s") %
                          {'aggregate': one_aggregate, 'e': e})

        if result > 0:
            total = len(parsed_args.aggregate)
            msg = (_("%(result)s of %(total)s node aggregates failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListAggregate(command.Lister):
    """List all baremetal node aggregates"""

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute

        data = bc_client.aggregate.list()

        column_headers = (
            "UUID",
            "Name",
            "Properties",
        )
        columns = (
            "UUID",
            "Name",
            "Metadata",
        )
        formatters = {'Metadata': utils.format_dict}
        return (column_headers,
                (utils.get_item_properties(
                    s, columns, formatters=formatters
                ) for s in data))


class ShowAggregate(command.ShowOne):
    """Display baremetal node aggregate details"""

    def get_parser(self, prog_name):
        parser = super(ShowAggregate, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate to display (name or UUID)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        data = utils.find_resource(
            bc_client.aggregate,
            parsed_args.aggregate,
        )
        # Special mapping for columns to make the output easier to read:
        # 'metadata' --> 'properties'
        data._info.update(
            {
                'properties': utils.format_dict(data._info.pop('metadata')),
            },
        )

        info = {}
        info.update(data._info)
        return zip(*sorted(info.items()))


class SetAggregate(command.Command):
    """Set properties for a baremetal node aggregate"""

    def get_parser(self, prog_name):
        parser = super(SetAggregate, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate(s) to delete (name or UUID)")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set a new name to a node aggregate (admin only)')
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Property to set on this node aggregate "
                   "(repeat option to set multiple properties)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        aggregate = utils.find_resource(
            bc_client.aggregate,
            parsed_args.aggregate,
        )
        updates = []
        if parsed_args.name:
            updates.append({"op": "replace",
                            "path": "/name",
                            "value": parsed_args.name})
        for key, value in (parsed_args.property or {}).items():
            updates.append({"op": "add",
                            "path": "/metadata/%s" % key,
                            "value": value})
        if updates:
            bc_client.aggregate.update(aggregate, updates)


class UnsetAggregate(command.Command):
    """Unset properties for a baremetal node aggregate"""

    def get_parser(self, prog_name):
        parser = super(UnsetAggregate, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate(s) to delete (name or UUID)")
        )
        parser.add_argument(
            "--property",
            metavar="<key>",
            action='append',
            help=_("Property to remove from this node aggregate "
                   "(repeat option to remove multiple properties)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        aggregate = utils.find_resource(
            bc_client.aggregate,
            parsed_args.aggregate,
        )
        updates = []
        for key in parsed_args.property or []:
            updates.append({"op": "remove",
                            "path": "/metadata/%s" % key})
        if updates:
            bc_client.aggregate.update(aggregate, updates)


class AggregateAddNode(command.Command):
    """Add a node for a specified node aggregate"""

    def get_parser(self, prog_name):
        parser = super(AggregateAddNode, self).get_parser(prog_name)
        parser.add_argument(
            "aggregate",
            metavar="<aggregate>",
            help=_("Aggregate to add nodes (name or UUID)")
        )
        parser.add_argument(
            "node",
            metavar="<node>",
            help=_("Name of baremetal node")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        aggregate = utils.find_resource(
            bc_client.aggregate,
            parsed_args.aggregate,
        )
        bc_client.aggregate_node.add_node(aggregate.uuid,
                                          parsed_args.node)


class AggregateListNode(command.Lister):
    """List all baremetal nodes names of a specified node aggregate"""

    def get_parser(self, prog_name):
        parser = super(AggregateListNode, self).get_parser(prog_name)
        parser.add_argument(
            "aggregate",
            metavar="<aggregate>",
            help=_("Aggregate to list its nodes (name or UUID)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        aggregate = utils.find_resource(
            bc_client.aggregate,
            parsed_args.aggregate,
        )
        data = bc_client.aggregate_node.list_node(aggregate.uuid)

        return (('Node',),
                tuple((d,) for d in data))


class AggregateRemoveNode(command.Command):
    """Remove a node for a specified node aggregate"""

    def get_parser(self, prog_name):
        parser = super(AggregateRemoveNode, self).get_parser(prog_name)
        parser.add_argument(
            "aggregate",
            metavar="<aggregate>",
            help=_("Aggregate to delete its node (name or UUID)")
        )
        parser.add_argument(
            "node",
            metavar="<node>",
            help=_("Name of baremetal node")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        aggregate = utils.find_resource(
            bc_client.aggregate,
            parsed_args.aggregate,
        )
        bc_client.aggregate_node.remove_node(aggregate.uuid,
                                             parsed_args.node)
