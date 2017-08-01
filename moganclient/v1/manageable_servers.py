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

from moganclient.common import base


class ManageableServer(base.Resource):
    pass


class ManageableServersManager(base.ManagerWithFind):
    resource_class = ManageableServer

    def list(self):
        pass

    def manage(self, name, node_uuid, description=None, metadata=None,):
        url = '/manageable_servers'
        data = {
            'name': name,
            'node_uuid': node_uuid
        }

        if description is not None:
            data['description'] = description
        if metadata is not None:
            data['metadata'] = metadata

        return self._create(url, data=data)
