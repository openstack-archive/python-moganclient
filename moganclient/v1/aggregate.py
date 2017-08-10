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


class Aggregate(base.Resource):
    pass


class AggregateManager(base.ManagerWithFind):
    resource_class = Aggregate

    def create(self, name, metadata=None):
        url = '/aggregates'
        data = {'name': name}
        if metadata:
            data['metadata'] = metadata
        return self._create(url, data=data)

    def delete(self, aggregate):
        url = '/aggregates/%s' % base.getid(aggregate)
        return self._delete(url)

    def get(self, aggregate):
        url = '/aggregates/%s' % base.getid(aggregate)
        return self._get(url)

    def list(self):
        url = '/aggregates'
        return self._list(url, response_key='aggregates')

    def update(self, aggregate, updates):
        url = '/aggregates/%s' % base.getid(aggregate)
        return self._update(url, data=updates)


class AggregateNode(base.Resource):
    pass


class AggregateNodeManager(base.Manager):
    resource_class = AggregateNode

    def add_node(self, aggregate_uuid, node):
        url = '/aggregates/%s/nodes' % aggregate_uuid
        data = {'node': node}
        return self._create(url, data=data)

    def list_node(self, aggregate_uuid):
        url = '/aggregates/%s/nodes' % aggregate_uuid
        return self._list(url, response_key='nodes')

    def remove_node(self, aggregate_uuid, node):
        url = '/aggregates/%s/nodes/%s' % (aggregate_uuid, node)
        return self._delete(url)
