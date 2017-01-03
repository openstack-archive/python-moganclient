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

    def create(self, name, is_public, description=None):
        url = '/types'
        data = {
            'name': name,
            'is_public': is_public,
            'description': description,
        }
        return self._create(url, data=data)

    def delete(self, flavor):
        url = '/types/%s' % base.getid(flavor)
        return self._delete(url)

    def get(self, flavor):
        url = '/types/%s' % base.getid(flavor)
        return self._get(url)

    def list(self):
        url = '/types'
        return self._list(url, response_key='types')

    def get_extra_specs(self, flavor):
        url = '/types/%s/extraspecs' % base.getid(flavor)
        return self._get(url, return_raw=True)

    def update_extra_specs(self, flavor, extra_specs):
        url = '/types/%s/extraspecs' % base.getid(flavor)
        data = extra_specs
        return self._update(url, data=data, return_raw=True)

    def delete_extra_specs(self, flavor, key):
        url = '/types/%(id)s/extraspecs/%(key)s' % {
            'id': base.getid(flavor), 'key': key}
        return self._delete(url)
