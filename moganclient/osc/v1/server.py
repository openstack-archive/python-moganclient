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

import io
import json
import logging
import os

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from moganclient.common.i18n import _

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
                LOG.error(_("Failed to %(action)s server with name or UUID "
                            "'%(server)s': %(e)s") %
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
            metavar="net-id=NETWORK[,port-type=PORT_TYPE]",
            required=True,
            required_keys=['net-id'],
            optional_keys=['port-type'],
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
            if 'port-type' in nic:
                nic['port_type'] = nic['port-type']
                del nic['port-type']
            if 'net-id' in nic:
                nic['net_id'] = nic['net-id']
                del nic['net-id']

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
            extra=parsed_args.property,
            min_count=parsed_args.min,
            max_count=parsed_args.max
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
                LOG.error(_("Failed to delete server with name or UUID "
                            "'%(server)s': %(e)s") %
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
            '--all-projects',
            action='store_true',
            default=bool(int(os.environ.get("ALL_PROJECTS", 0))),
            help=_('Include all projects (admin only)'),
        )
        return parser

    @staticmethod
    def _nics_formatter(nics):
        return_info = []
        for nics in nics:
            port_ips = []
            for fixed_ip in nics['fixed_ips']:
                port_ips.append(fixed_ip['ip_address'])
            return_info.append(', '.join(port_ips))
        return '; '.join(return_info)

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
                "Image",
                "Flavor",
                "Availability Zone",
                'Properties',
            )
            columns = (
                "uuid",
                "name",
                "status",
                "power_state",
                "nics",
                "image_uuid",
                "flavor_uuid",
                "availability_zone",
                'extra',
            )
        else:
            column_headers = (
                "UUID",
                "Name",
                "Status",
                "Networks",
                "Image",
            )
            columns = (
                "uuid",
                "name",
                "status",
                "nics",
                "image_uuid",
            )

        data = bc_client.server.list(detailed=True,
                                     all_projects=parsed_args.all_projects)
        formatters = {'nics': self._nics_formatter,
                      'extra': utils.format_dict}
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

        info = {}
        info.update(data._info)
        return zip(*sorted(info.items()))


class UpdateServer(command.ShowOne):
    """Update a baremetal server"""

    @staticmethod
    def _partition_kv(kv_arg):
        if ':' not in kv_arg:
            msg = _("Input %s should be a pair of key/value combined "
                    "by ':'")
            raise exceptions.CommandError(msg)
        kv = kv_arg.partition(":")
        return kv[0], kv[2]

    def get_parser(self, prog_name):
        parser = super(UpdateServer, self).get_parser(prog_name)
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
            "--add-extra",
            action="append",
            type=self._partition_kv,
            metavar="<EXTRA_KEY:EXTRA_VALUE>",
            help="A pair of key:value to be added to the extra "
                 "field of the server.")
        parser.add_argument(
            "--replace-extra",
            action="append",
            type=self._partition_kv,
            metavar="<EXTRA_KEY:EXTRA_VALUE>",
            help="A pair of key:value to be update to the extra "
                 "field of the serve.")
        parser.add_argument(
            "--remove-extra",
            action="append",
            metavar="<EXTRA_KEY>",
            help="Delete an item of the field of the server with the key "
                 "specified.")
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
        for key, value in parsed_args.add_extra or []:
            updates.append({"op": "add",
                            "path": "/extra/%s" % key,
                            "value": value})

        for key, value in parsed_args.replace_extra or []:
            updates.append({"op": "replace",
                            "path": "/extra/%s" % key,
                            "value": value})
        for key in parsed_args.remove_extra or []:
            updates.append({"op": "remove",
                            "path": "/extra/%s" % key})
        data = bc_client.server.update(server_id=server.uuid,
                                       updates=updates)
        info = {}
        info.update(data._info)
        return zip(*sorted(info.items()))


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
                   'floatingip', 'port_type')
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
            '--serial',
            dest='url_type',
            action='store_const',
            const='serial',
            help=_("Show serial console URL"),
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        server = utils.find_resource(
            bc_client.server,
            parsed_args.server,
        )

        data = bc_client.server.get_serial_console(server.uuid)
        if not data:
            return ({}, {})

        info = {}
        info.update(data.get('console'))
        return zip(*sorted(info.items()))
