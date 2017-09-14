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


"""Mogan v1 Baremetal server action implementations"""
import functools
import io
import json
import logging
import os

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from moganclient.common.i18n import _
from moganclient.common import utils as cli_utils

LOG = logging.getLogger(__name__)


class ServersActionBase(command.Command):
    def _get_parser_with_action(self, prog_name, action):
        parser = super(ServersActionBase, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs='+',
            help=_("Baremetal server(s) to %s (name or UUID)") % action
        )
        return parser

    def _action_multiple_items(self, parsed_args, action, method_name,
                               **kwargs):
        bc_client = self.app.client_manager.baremetal_compute
        result = 0
        for one_server in parsed_args.server:
            try:
                data = utils.find_resource(
                    bc_client.server, one_server)
                method = getattr(bc_client.server, method_name)
                method(data.uuid, **kwargs)
            except Exception as e:
                result += 1
                LOG.error("Failed to %(action)s server with name or UUID "
                          "'%(server)s': %(e)s",
                          {'action': action, 'server': one_server, 'e': e})

        if result > 0:
            total = len(parsed_args.server)
            msg = (_("%(result)s of %(total)s baremetal servers failed "
                     "to %(action)s.") % {'result': result, 'total': total,
                                          'action': action})
            raise exceptions.CommandError(msg)


class CreateServer(command.ShowOne):
    """Create a new baremetal server"""

    def get_parser(self, prog_name):
        parser = super(CreateServer, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help=_("New baremetal server name")
        )
        parser.add_argument(
            "--flavor",
            metavar="<flavor>",
            required=True,
            help=_('Create server with this flavor (name or ID)'),
        )
        parser.add_argument(
            "--image",
            metavar="<image>",
            required=True,
            help=_('Create server boot disk from this image (name or ID)'),
        )
        parser.add_argument(
            "--nic",
            metavar="<net-id=NETWORK, port-id=PORT>",
            required=True,
            optional_keys=['net-id', 'port-id'],
            action=parseractions.MultiKeyValueAction,
            help=_("Create a NIC on the server. "
                   "Specify option multiple times to create multiple NICs."),
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Baremetal server description"),
        )
        parser.add_argument(
            "--availability-zone",
            metavar="<zone-name>",
            help=_('Select an availability zone for the server'),
        )
        parser.add_argument(
            '--file',
            metavar='<dest-filename=source-filename>',
            action='append',
            default=[],
            help=_('File to inject into image before boot '
                   '(repeat option to set multiple files)'),
        )
        parser.add_argument(
            '--user-data',
            metavar='<user-data>',
            help=_('User data file to inject into the server'),
        )
        parser.add_argument(
            '--key-name',
            metavar='<key-name>',
            help=_('Keypair to inject into this server (optional extension)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Set a property on this server '
                   '(repeat option to set multiple values)'),
        )
        parser.add_argument(
            '--partition',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Create a partition on the root disk of this server, '
                   'only root_gb(required), ephemeral_gb, and swap_mb allowed '
                   '(repeat option to set multiple partitions)'),
        )
        parser.add_argument(
            "--min",
            metavar='<count>',
            type=int,
            default=1,
            help=_('Minimum number of servers to launch (default=1)'),
        )
        parser.add_argument(
            '--max',
            metavar='<count>',
            type=int,
            default=1,
            help=_('Maximum number of servers to launch (default=1)'),
        )
        parser.add_argument(
            "--hint",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Hints for the Mogan scheduler (optional extension)")
        )

        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        flavor_data = utils.find_resource(
            bc_client.flavor,
            parsed_args.flavor)
        image_data = utils.find_resource(
            self.app.client_manager.image.images,
            parsed_args.image)

        for nic in parsed_args.nic:
            if 'net-id' in nic:
                nic['net_id'] = nic['net-id']
                del nic['net-id']
            if 'port-id' in nic:
                nic['port_id'] = nic['port-id']
                del nic['port-id']

        files = {}
        for f in parsed_args.file:
            dst, src = f.split('=', 1)
            try:
                files[dst] = io.open(src, 'rb')
            except IOError as e:
                msg = _("Can't open '%(source)s': %(exception)s")
                raise exceptions.CommandError(
                    msg % {"source": src,
                           "exception": e}
                )

        if parsed_args.min > parsed_args.max:
            msg = _("min servers should be <= max servers")
            raise exceptions.CommandError(msg)
        if parsed_args.min < 1:
            msg = _("min servers should be > 0")
            raise exceptions.CommandError(msg)
        if parsed_args.max < 1:
            msg = _("max servers should be > 0")
            raise exceptions.CommandError(msg)

        userdata = None
        if parsed_args.user_data:
            try:
                userdata = io.open(parsed_args.user_data)
            except IOError as e:
                msg = _("Can't open '%(data)s': %(exception)s")
                raise exceptions.CommandError(
                    msg % {"data": parsed_args.user_data,
                           "exception": e}
                )

        boot_kwargs = dict(
            name=parsed_args.name,
            image_uuid=image_data.id,
            flavor_uuid=flavor_data.uuid,
            description=parsed_args.description,
            networks=parsed_args.nic,
            availability_zone=parsed_args.availability_zone,
            userdata=userdata,
            files=files,
            key_name=parsed_args.key_name,
            metadata=parsed_args.property,
            partitions=parsed_args.partition,
            min_count=parsed_args.min,
            max_count=parsed_args.max,
            hint=parsed_args.hint
        )

        try:
            data = bc_client.server.create(**boot_kwargs)
        finally:
            # Clean up open files - make sure they are not strings
            for f in files:
                if hasattr(f, 'close'):
                    f.close()
            if hasattr(userdata, 'close'):
                userdata.close()
        # Special mapping for columns to make the output easier to read:
        # 'metadata' --> 'properties'
        # 'image_uuid' --> '<image_name> (<image_uuid>)'
        # 'flavor_uuid' --> '<flavor_name> (<flavor_uuid>)'
        data._info.update(
            {
                'properties': utils.format_dict(data._info.pop('metadata')),
                'partitions': utils.format_dict(data._info.pop('partitions')),
                'image': '%s (%s)' % (image_data.name, image_data.id),
                'flavor': '%s (%s)' % (flavor_data.name, flavor_data.uuid)
            },
        )
        data._info.pop('flavor_uuid')
        data._info.pop('image_uuid')

        info = {}
        info.update(data._info)
        return zip(*sorted(info.items()))


class DeleteServer(command.Command):
    """Delete existing baremetal erver(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs='+',
            help=_("Baremetal server(s) to delete (name or UUID)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        result = 0
        for one_server in parsed_args.server:
            try:
                data = utils.find_resource(
                    bc_client.server, one_server)
                bc_client.server.delete(data.uuid)
            except Exception as e:
                result += 1
                LOG.error("Failed to delete server with name or UUID "
                          "'%(server)s': %(e)s",
                          {'server': one_server, 'e': e})

        if result > 0:
            total = len(parsed_args.server)
            msg = (_("%(result)s of %(total)s baremetal servers failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListServer(command.Lister):
    """List all baremetal servers"""

    def get_parser(self, prog_name):
        parser = super(ListServer, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        parser.add_argument(
            '-n', '--no-name-lookup',
            action='store_true',
            default=False,
            help=_('Skip flavor and image name lookup.'),
        )
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=bool(int(os.environ.get("ALL_PROJECTS", 0))),
            help=_('Include all projects (admin only)'),
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute

        if parsed_args.long:
            # This is the easiest way to change column headers
            column_headers = (
                "UUID",
                "Name",
                "Status",
                "Power State",
                "Networks",
                "Image Name",
                "Image Id",
                "Flavor Name",
                "Flavor Id",
                "Availability Zone",
                'Properties',
            )
            columns = (
                "uuid",
                "name",
                "status",
                "power_state",
                "addresses",
                "image_name",
                "image_uuid",
                "flavor_name",
                "flavor_uuid",
                "availability_zone",
                'metadata',
            )
        else:
            column_headers = (
                "UUID",
                "Name",
                "Status",
                "Networks",
                "Image",
                "Flavor",
            )
            if parsed_args.no_name_lookup:
                columns = (
                    "uuid",
                    "name",
                    "status",
                    "addresses",
                    "image_uuid",
                    "flavor_uuid",
                )
            else:
                columns = (
                    "uuid",
                    "name",
                    "status",
                    "addresses",
                    "image_name",
                    "flavor_name",
                )

        data = bc_client.server.list(detailed=True,
                                     all_projects=parsed_args.all_projects)
        if not data:
            return (), ()
        net_client = self.app.client_manager.network
        addr_fmt = functools.partial(cli_utils.addresses_formatter, net_client)
        formatters = {'addresses': addr_fmt,
                      'metadata': utils.format_dict
                      }

        images = {}
        # Create a dict that maps image_id to image object.
        # Needed so that we can display the "Image Name" column.
        # "Image Name" is not crucial, so we swallow any exceptions.
        if not parsed_args.no_name_lookup:
            try:
                images_list = self.app.client_manager.image.images.list()
                for i in images_list:
                    images[i.id] = i
            except Exception:
                pass

        flavors = {}
        # Create a dict that maps flavor_id to flavor object.
        # Needed so that we can display the "Flavor Name" column.
        # "Flavor Name" is not crucial, so we swallow any exceptions.
        if not parsed_args.no_name_lookup:
            try:
                flavors_list = bc_client.flavor.list()
                for i in flavors_list:
                    flavors[i.uuid] = i
            except Exception:
                pass

        # Populate image_name, image_id, flavor_name and flavor_id attributes
        # of server objects so that we can display those columns.
        for s in data:
            image = images.get(s.image_uuid)
            if image:
                s.image_name = image.name
            else:
                s.image_name = ''
            flavor = flavors.get(s.flavor_uuid)
            if flavor:
                s.flavor_name = flavor.name
            else:
                s.flavor_name = ''

        return (column_headers,
                (utils.get_item_properties(
                    s, columns, formatters=formatters
                ) for s in data))


class ShowServer(command.ShowOne):
    """Display baremetal server details"""

    def get_parser(self, prog_name):
        parser = super(ShowServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_("Baremetal server to display (name or UUID)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        data = utils.find_resource(
            bc_client.server,
            parsed_args.server,
        )
        # Special mapping for columns to make the output easier to read:
        # 'metadata' --> 'properties'
        network_client = self.app.client_manager.network
        image_client = self.app.client_manager.image
        data._info.update(
            {
                'properties': utils.format_dict(data._info.pop('metadata')),
                'partitions': utils.format_dict(data._info.pop('partitions')),
                'addresses': cli_utils.addresses_formatter(
                    network_client,
                    data._info.pop('addresses')),
                'image': cli_utils.image_formatter(
                    image_client, data._info.pop('image_uuid')),
                'flavor': cli_utils.flavor_formatter(
                    bc_client, data._info.pop('flavor_uuid'))
            },
        )

        info = {}
        info.update(data._info)
        return zip(*sorted(info.items()))


class SetServer(command.Command):
    """Set properties for a baremetal server"""

    def get_parser(self, prog_name):
        parser = super(SetServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_("Baremetal server to update (name or UUID)")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Baremetal Server description"),
        )
        parser.add_argument(
            "--name",
            metavar="<description>",
            help=_("Baremetal server description"),
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Property to set on this server "
                   "(repeat option to set multiple properties)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        server = utils.find_resource(
            bc_client.server,
            parsed_args.server,
        )
        updates = []
        if parsed_args.description:
            updates.append({"op": "replace",
                            "path": "/description",
                            "value": parsed_args.description})
        if parsed_args.name:
            updates.append({"op": "replace",
                            "path": "/name",
                            "value": parsed_args.name})
        for key, value in (parsed_args.property or {}).items():
            updates.append({"op": "add",
                            "path": "/metadata/%s" % key,
                            "value": value})
        if updates:
            bc_client.server.update(server.uuid, updates)


class UnsetServer(command.Command):
    """Unset properties for a baremetal server"""

    def get_parser(self, prog_name):
        parser = super(UnsetServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_("Baremetal server to unset its properties (name or UUID)")
        )
        parser.add_argument(
            "--property",
            metavar="<key>",
            action='append',
            help=_("Property to remove from this server "
                   "(repeat option to remove multiple properties)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        server = utils.find_resource(
            bc_client.server,
            parsed_args.server,
        )
        updates = []
        for key in parsed_args.property or []:
            updates.append({"op": "remove",
                            "path": "/metadata/%s" % key})
        if updates:
            bc_client.server.update(server.uuid, updates)


class RebuildServer(command.Command):
    """Rebuild a baremetal server."""

    def get_parser(self, prog_name):
        parser = super(RebuildServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_("Baremetal server to be rebuilt (name or UUID)")
        )
        parser.add_argument(
            "--image",
            metavar="<image>",
            help=_('Rebuild baremetal server with this image (name or ID)'),
        )
        parser.add_argument(
            '--preserve-ephemeral',
            action='store_true',
            default=False,
            help=_("Preserve the ephemeral disk partition when rebuilding")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        server = utils.find_resource(
            bc_client.server,
            parsed_args.server,
        )
        if parsed_args.image:
            image = utils.find_resource(
                self.app.client_manager.image.images,
                parsed_args.image)
            image_id = image.id
        else:
            image_id = None
        bc_client.server.rebuild(server.uuid, image_id,
                                 parsed_args.preserve_ephemeral)


class StartServer(ServersActionBase):
    """Start a baremetal server."""

    def get_parser(self, prog_name):
        return self._get_parser_with_action(prog_name, 'start')

    def take_action(self, parsed_args):
        self._action_multiple_items(parsed_args, 'start', 'set_power_state',
                                    power_state='on')


class StopServer(ServersActionBase):
    """Stop baremetal server(s)."""

    def get_parser(self, prog_name):
        return self._get_parser_with_action(prog_name, 'stop')

    def take_action(self, parsed_args):
        self._action_multiple_items(parsed_args, 'stop', 'set_power_state',
                                    power_state='off')


class RebootServer(ServersActionBase):
    """Reboot baremetal server(s)."""

    def get_parser(self, prog_name):
        return self._get_parser_with_action(prog_name, 'reboot')

    def take_action(self, parsed_args):
        self._action_multiple_items(parsed_args, 'reboot', 'set_power_state',
                                    power_state='reboot')


class LockServer(ServersActionBase):
    """Lock baremetal server(s)."""

    def get_parser(self, prog_name):
        return self._get_parser_with_action(prog_name, 'lock')

    def take_action(self, parsed_args):
        self._action_multiple_items(parsed_args, 'lock', 'set_lock_state',
                                    lock_state=True)


class UnLockServer(ServersActionBase):
    """UnLock baremetal server(s)."""

    def get_parser(self, prog_name):
        return self._get_parser_with_action(prog_name, 'unlock')

    def take_action(self, parsed_args):
        self._action_multiple_items(parsed_args, 'unlock', 'set_lock_state',
                                    lock_state=False)


class ShowServerNetworkInfo(command.Lister):
    """Display baremetal server's network info"""

    def get_parser(self, prog_name):
        parser = super(ShowServerNetworkInfo, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_("Baremetal server to display its network information (name "
                   "or UUID)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        server = utils.find_resource(
            bc_client.server,
            parsed_args.server,
        )
        data = bc_client.server.get_server_nics(server.uuid)
        columns = ('network_id', 'port_id', 'mac_address', 'fixed_ips',
                   'floating_ip')
        formatters = {'fixed_ips': lambda s: json.dumps(s, indent=4)}
        return (columns,
                (utils.get_item_properties(
                    nic, columns, formatters=formatters) for nic in data))


class AddFloatingIP(command.Command):
    _description = _("Add floating IP address to server")

    def get_parser(self, prog_name):
        parser = super(AddFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to receive the floating IP address (name or ID)"),
        )
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help=_("Floating IP address to assign to server (IP only)"),
        )
        parser.add_argument(
            "--fixed-ip-address",
            metavar="<ip-address>",
            help=_("Fixed IP address to associate with this floating IP "
                   "address"),
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        server = utils.find_resource(
            bc_client.server,
            parsed_args.server,
        )

        bc_client.server.add_floating_ip(server.uuid,
                                         parsed_args.ip_address,
                                         parsed_args.fixed_ip_address)


class RemoveFloatingIP(command.Command):
    _description = _("Remove floating IP address from server")

    def get_parser(self, prog_name):
        parser = super(RemoveFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_(
                "Server to remove the floating IP address from (name or ID)"
            ),
        )
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help=_("Floating IP address to remove from server (IP only)"),
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        server = utils.find_resource(
            bc_client.server,
            parsed_args.server,
        )

        bc_client.server.remove_floating_ip(server.uuid,
                                            parsed_args.ip_address)


class AddInterface(command.Command):
    _description = _("Add interface to server")

    def get_parser(self, prog_name):
        parser = super(AddInterface, self).get_parser(prog_name)
        excluded_group = parser.add_mutually_exclusive_group(required=True)
        excluded_group.add_argument(
            "--net-id",
            metavar="<net-id>",
            help=_("Network to link to server"),
        )
        excluded_group.add_argument(
            "--port-id",
            metavar="<port-id>",
            help=_("Port to link to server"),
        )
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to attach interface for"),
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        server = utils.find_resource(
            bc_client.server,
            parsed_args.server,
        )

        bc_client.server.add_interface(server.uuid,
                                       parsed_args.net_id,
                                       parsed_args.port_id)


class RemoveInterface(command.Command):
    _description = _("Remove interface from server")

    def get_parser(self, prog_name):
        parser = super(RemoveInterface, self).get_parser(prog_name)
        parser.add_argument(
            "port_id",
            metavar="<port-id>",
            help=_("Interface to remove from server"),
        )
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_(
                "Server to remove the interface from"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        server = utils.find_resource(
            bc_client.server,
            parsed_args.server,
        )

        bc_client.server.remove_interface(server.uuid,
                                          parsed_args.port_id)


class ShowConsoleURL(command.ShowOne):
    _description = _("Show server's remote console URL")

    def get_parser(self, prog_name):
        parser = super(ShowConsoleURL, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_("Server to show URL (name or ID)")
        )
        type_group = parser.add_mutually_exclusive_group()
        type_group.add_argument(
            '--shellinabox',
            dest='url_type',
            action='store_const',
            const='shellinabox',
            help=_("Show shellinabox serial console URL"),
        )
        type_group.add_argument(
            '--socat',
            dest='url_type',
            action='store_const',
            const='socat',
            help=_("Show socat serial console URL"),
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        server = utils.find_resource(
            bc_client.server,
            parsed_args.server,
        )

        data = bc_client.server.get_remote_console(
            server.uuid, parsed_args.url_type)
        if not data:
            return ({}, {})

        info = {}
        info.update(data._info)
        return zip(*sorted(info.items()))
