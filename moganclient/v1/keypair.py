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


class KeyPair(base.Resource):
    pass


class KeyPairManager(base.ManagerWithFind):
    resource_class = KeyPair

    def create(self, name, user_id=None, public_key=None, keypair_type=None):
        url = '/keypairs'
        data = {'name': name}
        if user_id:
            data['user_id'] = user_id
        if public_key:
            data['public_key'] = public_key
        if keypair_type:
            data['type'] = keypair_type
        return self._create(url, data=data)

    def delete(self, name, user_id=None):
        url = '/keypairs/%s' % name
        url = url + '?user_id=%s' % user_id if user_id else url
        return self._delete(url)

    def get(self, name, user_id=None):
        url = '/keypairs/%s' % name
        url = url + '?user_id=%s' % user_id if user_id else url
        return self._get(url)

    def list(self, user_id=None):
        url = '/keypairs' if not user_id else '/keypairs?user_id=%s' % user_id
        return self._list(url, response_key='keypairs')
