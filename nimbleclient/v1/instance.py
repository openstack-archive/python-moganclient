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

from nimbleclient.common import base


class Instance(base.Resource):
    pass


class InstanceManager(base.ManagerWithFind):
    resource_class = Instance

    def create(self, name, image_uuid, instance_type_uuid, networks,
               description=None, availability_zone=None, extra=None):
        url = '/instances'
        data = {
            'name': name,
            'image_uuid': image_uuid,
            'instance_type_uuid': instance_type_uuid,
            'networks': networks
        }
        if availability_zone is not None:
            data['availability_zone'] = availability_zone
        if description is not None:
            data['description'] = description
        if extra is not None:
            data['extra'] = extra
        return self._create(url, data=data)

    def delete(self, instance_id):
        url = '/instances/%s' % base.getid(instance_id)
        return self._delete(url)

    def get(self, instance_id):
        url = '/instances/%s' % base.getid(instance_id)
        return self._get(url)

    def list(self):
        url = '/instances'
        return self._list(url, response_key='instances')

    def update(self, instance_id, updates):
        url = '/instances/%s' % base.getid(instance_id)
        return self._update(url, data=updates)

    def set_power_state(self, instance_id, power_state):
        url = '/instances/%s/states/power' % base.getid(instance_id)
        return self._update_all(url, data={'target': power_state})
