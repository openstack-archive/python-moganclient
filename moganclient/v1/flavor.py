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


class Flavor(base.Resource):
    pass


class FlavorManager(base.ManagerWithFind):
    resource_class = Flavor

    def create(self, name, resource, resource_aggregate, is_public,
               disabled, description=None):
        url = '/flavors'
        data = {
            'name': name,
            'description': description,
            'is_public': is_public,
            'disabled': disabled,
        }
        if resource:
            data['resources'] = resource
        if resource_aggregate:
            data['resource_aggregates'] = resource_aggregate
        return self._create(url, data=data)

    def delete(self, flavor):
        url = '/flavors/%s' % base.getid(flavor)
        return self._delete(url)

    def get(self, flavor):
        url = '/flavors/%s' % base.getid(flavor)
        return self._get(url)

    def list(self):
        url = '/flavors'
        return self._list(url, response_key='flavors')

    def update(self, flavor, data):
        url = '/flavors/%s' % base.getid(flavor)
        return self._update(url, data)

    def add_tenant_access(self, flavor, project):
        url = '/flavors/%s/access' % base.getid(flavor)
        return self._create(url, data={'tenant_id': project})

    def remove_tenant_access(self, flavor, project):
        url = '/flavors/%(id)s/access/%(project)s' % {
            'id': base.getid(flavor), 'project': project}
        return self._delete(url)
