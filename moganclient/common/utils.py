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

import logging


LOG = logging.getLogger(__name__)


def get_response_body(resp):
    body = resp.content
    content_type = resp.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        try:
            body = resp.json()
        except ValueError:
            LOG.error('Could not decode response body as JSON')
    elif 'application/octet-stream' in content_type:
        try:
            body = resp.body()
        except ValueError:
            LOG.error('Could not decode response body as raw')
    else:
        body = None
    return body
