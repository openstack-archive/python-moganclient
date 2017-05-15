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

import copy
import logging

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

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
        parser.add_argument(
            "--cpus",
            type=int,
            metavar="<cpus>",
            help=_("Number of cpus")
        )
        parser.add_argument(
            "--cpu-model",
            metavar="<cpu-model>",
            help=_("Cpu model of the flavor")
        )
        parser.add_argument(
            "--ram",
            type=int,
            metavar="<size-mb>",
            help=_("Memory size in MB")
        )
        parser.add_argument(
            "--ram-type",
            metavar="<ram-type>",
            help=_("Ram type of the flavor")
        )
        parser.add_argument(
            "--nic",
            metavar="speed=SPEED[,type=PORT_TYPE]",
            required_keys=['speed', 'type'],
            action=parseractions.MultiKeyValueAction,
            help=_("NIC of the flavor. "
                   "Specify option multiple times to create multiple NICs."),
        )
        parser.add_argument(
            "--disk",
            metavar="size_gb=SIZE[,type=DISK_TYPE]",
            required_keys=['size_gb', 'type'],
            action=parseractions.MultiKeyValueAction,
            help=_("Disk of the flavor. "
                   "Specify option multiple times to create multiple disks."),
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
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Flavor description"),
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Property to add to this flavor "
                   "(repeat option to set multiple properties)")
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

        cpus = {}
        if parsed_args.cpus:
            cpus['cores'] = parsed_args.cpus
        if parsed_args.cpu_model:
            cpus['model'] = parsed_args.cpu_model

        ram = {}
        if parsed_args.ram:
            ram['size_mb'] = parsed_args.ram
        if parsed_args.ram_type:
            ram['type'] = parsed_args.ram_type

        data = bc_client.flavor.create(
            name=parsed_args.name,
            cpus=cpus,
            memory=ram,
            nics=parsed_args.nic,
            disks=parsed_args.disk,
            is_public=is_public,
            description=parsed_args.description,
        )
        info.update(data._info)
        if parsed_args.property:
            bc_client.flavor.update_extra_specs(data,
                                                parsed_args.property)
            extra_specs = bc_client.flavor.get_extra_specs(data)
            info.update(extra_specs)

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
                LOG.error(_("Failed to delete flavor with name or UUID "
                            "'%(flavor)s': %(e)s") %
                          {'flavor': one_flavor, 'e': e})

        if result > 0:
            total = len(parsed_args.flavor)
            msg = (_("%(result)s of %(total)s flavors failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListFlavor(command.Lister):
    """List all baremetal flavors"""

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute

        data = bc_client.flavor.list()

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

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


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
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Property to set on <flavor> "
                   "(repeat option to set multiple properties)")
        )
        parser.add_argument(
            "--no-property",
            dest="no_property",
            action="store_true",
            help=_("Remove all properties from <flavor> "
                   "(specify both --property and --no-property to "
                   "overwrite the current properties)"),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Set flavor access to project (name or ID) '
                   '(admin only)'),
        )
        return parser

    def take_action(self, parsed_args):

        bc_client = self.app.client_manager.baremetal_compute
        data = utils.find_resource(
            bc_client.flavor,
            parsed_args.flavor,
        )

        set_property = None
        del_property_key = None
        # NOTE(RuiChen): extra specs update API is append mode, so if the
        #                options is overwrite mode, the update and delete
        #                properties need to be handled in client side.
        if parsed_args.no_property and parsed_args.property:
            # override
            del_property_key = data.extra_specs.keys()
            set_property = copy.deepcopy(parsed_args.property)
        elif parsed_args.property:
            # append
            set_property = copy.deepcopy(parsed_args.property)
        elif parsed_args.no_property:
            # clean
            del_property_key = data.extra_specs.keys()

        result = 0
        if del_property_key is not None:
            for each_key in del_property_key:
                try:
                    # If the key is in the set_property, it will be updated
                    # in the follow logic.
                    if (set_property is None or
                            each_key not in set_property):
                        bc_client.flavor.delete_extra_specs(
                            data,
                            each_key
                        )
                except Exception as e:
                    result += 1
                    LOG.error(_("Failed to remove flavor property with key "
                                "'%(key)s': %(e)s") % {'key': each_key,
                                                       'e': e})
        if set_property is not None:
            try:
                bc_client.flavor.update_extra_specs(
                    data,
                    set_property
                )
            except Exception as e:
                result += 1
                LOG.error(_("Failed to update flavor property with key/value "
                            "'%(key)s': %(e)s") % {'key': set_property,
                                                   'e': e})

        if parsed_args.project:
            try:
                if data.is_public:
                    msg = _("Cannot set access for a public flavor")
                    raise exceptions.CommandError(msg)
                else:
                    bc_client.flavor.add_tenant_access(
                        data, parsed_args.project)
            except Exception as e:
                LOG.error(_("Failed to set flavor access to project: %s"), e)
                result += 1

        if result > 0:
            raise exceptions.CommandError(_("Command Failed: One or more of"
                                            " the operations failed"))


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

        info = {}
        info.update(data._info)
        return zip(*sorted(info.items()))


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
            "--property",
            metavar="<key>",
            action='append',
            help=_("Property to remove from <flavor> "
                   "(repeat option to remove multiple properties)")
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

        unset_property_key = []
        if parsed_args.property:
            unset_property_key = list(
                set(data.extra_specs.keys()).intersection(
                    set(parsed_args.property)))

        result = 0
        for each_key in unset_property_key:
            try:
                bc_client.flavor.delete_extra_specs(data, each_key)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to remove flavor property with key "
                            "'%(key)s': %(e)s") % {'key': each_key, 'e': e})

        if parsed_args.project:
            try:
                if data.is_public:
                    msg = _("Cannot remove access for a public flavor")
                    raise exceptions.CommandError(msg)
                else:
                    bc_client.flavor.remove_tenant_access(
                        data, parsed_args.project)
            except Exception as e:
                LOG.error(_("Failed to remove flavor access to project: "
                            "%s"), e)
                result += 1

        if result > 0:
            raise exceptions.CommandError(_("Command Failed: One or more of"
                                            " the operations failed"))
