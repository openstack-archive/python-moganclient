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


"""Mogan v1 Baremetal keypair action implementations"""

import copy
import logging
import os
import sys

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from moganclient.common.i18n import _

LOG = logging.getLogger(__name__)


class CreateKeyPair(command.ShowOne):
    """Create new public or private key for baremetal server ssh access"""

    def get_parser(self, prog_name):
        parser = super(CreateKeyPair, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help=_("Name of key")
        )
        parser.add_argument(
            "--user",
            metavar="<user-id>",
            help=_("ID of user to whom to add key-pair (Admin only)")
        )
        parser.add_argument(
            "--key-type",
            metavar="<key-type>",
            help=_("Keypair type. Can be ssh or x509.")
        )
        parser.add_argument(
            "--public-key",
            metavar="<file>",
            help=_("Filename for public key to add. If not used, "
                   "creates a private key.")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        pub_key = parsed_args.public_key
        if pub_key:
            if pub_key == '-':
                pub_key = sys.stdin.read()
            else:
                try:
                    with open(os.path.expanduser(pub_key)) as f:
                        pub_key = f.read()
                except IOError as e:
                    raise exceptions.CommandError(
                        _("Can't open or read '%(key)s': %(exc)s")
                        % {'key': pub_key, 'exc': e}
                    )

        data = bc_client.keypair.create(parsed_args.name, parsed_args.user,
                                        pub_key, parsed_args.key_type)
        info = copy.copy(data._info)
        if not pub_key:
            private_key = info.pop('private_key')
            print(private_key)
        return zip(*sorted(info.items()))


class DeleteKeyPair(command.Command):
    """Delete baremetal server public or private key(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteKeyPair, self).get_parser(prog_name)
        parser.add_argument(
            'key',
            metavar='<key>',
            nargs='+',
            help=_("Name of key(s) to delete (name only)")
        )
        parser.add_argument(
            "--user",
            metavar="<user-id>",
            help=_("ID of user to whom to add key-pair (Admin only)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        result = 0
        for one_key in parsed_args.key:
            try:
                bc_client.keypair.delete(one_key, parsed_args.user)
            except Exception as e:
                result += 1
                LOG.error("Failed to delete keypair with name "
                          "'%(key)s': %(e)s",
                          {'key': one_key, 'e': e})

        if result > 0:
            total = len(parsed_args.key)
            msg = (_("%(result)s of %(total)s keypairs failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListKeyPair(command.Lister):
    """List baremetal server key fingerprints"""
    def get_parser(self, prog_name):
        parser = super(ListKeyPair, self).get_parser(prog_name)
        parser.add_argument(
            "--user",
            metavar="<user-id>",
            help=_("ID of user to whom to add key-pair (Admin only)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute

        data = bc_client.keypair.list(parsed_args.user)

        column_headers = (
            "Name",
            "Type",
            "Fingerprint",
        )
        columns = (
            "Name",
            "Type",
            "Fingerprint",
        )

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowKeyPair(command.ShowOne):
    """Display baremetal server key details"""

    def get_parser(self, prog_name):
        parser = super(ShowKeyPair, self).get_parser(prog_name)
        parser.add_argument(
            'keypair',
            metavar='<keypair>',
            help=_("Keypair to display (name only)")
        )
        parser.add_argument(
            "--user",
            metavar="<user-id>",
            help=_("ID of user to whom to add key-pair (Admin only)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        data = bc_client.keypair.get(parsed_args.keypair, parsed_args.user)
        info = {}
        info.update(data._info)
        return zip(*sorted(info.items()))
