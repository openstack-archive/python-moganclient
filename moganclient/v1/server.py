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

import base64

from oslo_utils import encodeutils
import six

from moganclient.common import base


class Server(base.Resource):
    pass


class ServerManager(base.ManagerWithFind):
    resource_class = Server

    def create(self, name, image_uuid, flavor_uuid, networks,
               description=None, availability_zone=None, extra=None,
               userdata=None, files=None, key_name=None, min_count=None,
               max_count=None):
        url = '/servers'
        data = {
            'name': name,
            'image_uuid': image_uuid,
            'flavor_uuid': flavor_uuid,
            'networks': networks
        }

        if userdata is not None:
            if hasattr(userdata, 'read'):
                userdata = userdata.read()

            # NOTE(melwitt): Text file data is converted to bytes prior to
            # base64 encoding. The utf-8 encoding will fail for binary files.
            if six.PY3:
                try:
                    userdata = userdata.encode("utf-8")
                except AttributeError:
                    # In python 3, 'bytes' object has no attribute 'encode'
                    pass
            else:
                try:
                    userdata = encodeutils.safe_encode(userdata)
                except UnicodeDecodeError:
                    pass

            userdata_b64 = base64.b64encode(userdata).decode('utf-8')
            data["user_data"] = userdata_b64

        # Files are a slight bit tricky. They're passed in a "personality"
        # list to the POST. Each item is a dict giving a file name and the
        # base64-encoded contents of the file. We want to allow passing
        # either an open file *or* some contents as files here.
        if files:
            personality = data['personality'] = []
            for filepath, file_or_string in sorted(files.items(),
                                                   key=lambda x: x[0]):
                if hasattr(file_or_string, 'read'):
                    file_data = file_or_string.read()
                else:
                    file_data = file_or_string

                if six.PY3 and isinstance(file_data, str):
                    file_data = file_data.encode('utf-8')
                cont = base64.b64encode(file_data).decode('utf-8')
                personality.append({
                    'path': filepath,
                    'contents': cont,
                })

        if availability_zone is not None:
            data['availability_zone'] = availability_zone
        if description is not None:
            data['description'] = description
        if key_name is not None:
            data['key_name'] = key_name
        if extra is not None:
            data['extra'] = extra
        if min_count is not None:
            data['min_count'] = min_count
        if max_count is not None:
            data['max_count'] = max_count

        return self._create(url, data=data)

    def delete(self, server_id):
        url = '/servers/%s' % base.getid(server_id)
        return self._delete(url)

    def get(self, server_id):
        url = '/servers/%s' % base.getid(server_id)
        return self._get(url)

    def list(self, detailed=False, all_projects=False):
        url = '/servers/detail' if detailed else '/servers'
        if all_projects:
            url = '%s?%s' % (url, 'all_projects=True')
        return self._list(url, response_key='servers')

    def update(self, server_id, updates):
        url = '/servers/%s' % base.getid(server_id)
        return self._update(url, data=updates)

    def set_power_state(self, server_id, power_state):
        url = '/servers/%s/states/power' % base.getid(server_id)
        return self._update_all(url, data={'target': power_state})

    def set_lock_state(self, server_id, lock_state):
        url = '/servers/%s/states/lock' % base.getid(server_id)
        return self._update_all(url, data={'target': lock_state})

    def get_server_nics(self, server_id):
        url = '/servers/%s/networks' % base.getid(server_id)
        return self._list(url, response_key='nics')

    def add_floating_ip(self, server_id, ip_address, fixed_ip_address):
        url = '/servers/%s/networks/floatingips' % base.getid(server_id)
        data = {'address': ip_address,
                'fixed_address': fixed_ip_address}
        return self._create(url, data=data)

    def remove_floating_ip(self, server_id, ip_address):
        url = '/servers/%(server)s/networks/floatingips/%(ip)s' % {
            'server': base.getid(server_id), 'ip': ip_address}
        return self._delete(url)

    def get_serial_console(self, server_id):
        url = '/servers/%(server)s/serial_console' % {
            'server': base.getid(server_id)}
        return self._get(url)
