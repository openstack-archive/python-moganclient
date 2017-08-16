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

from moganclient.common import base


class ServerGroup(base.Resource):
    pass


class ServerGroupManager(base.ManagerWithFind):
    resource_class = ServerGroup

    def create(self, name, policies):
        url = '/server_groups'
        data = {'name': name, 'policies': policies}
        return self._create(url, data=data)

    def delete(self, server_group):
        url = '/server_groups/%s' % base.getid(server_group)
        return self._delete(url)

    def get(self, server_group):
        url = '/server_groups/%s' % base.getid(server_group)
        return self._get(url)

    def list(self, all_projects=False):
        url = '/server_groups'
        if all_projects:
            url += '?all_tenants=true'
        return self._list(url, response_key='server_groups')
