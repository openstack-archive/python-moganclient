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

from osc_lib import utils

from moganclient.common.i18n import _

LOG = logging.getLogger(__name__)

DEFAULT_BAREMETAL_COMPUTE_API_VERSION = '1'
API_VERSION_OPTION = 'os_baremetal_compute_api_version'
API_NAME = 'baremetal_compute'
API_VERSIONS = {
    '1': 'moganclient.v1.client.Client',
}


def make_client(instance):
    """Returns an baremetal service client"""
    mogan_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    LOG.debug('Instantiating baremetal-compute client: %s', mogan_client)

    endpoint = instance.get_endpoint_for_service_type(
        API_NAME,
        region_name=instance.region_name,
        interface=instance.interface,
    )

    kwargs = {'endpoint': endpoint,
              'auth_url': instance.auth.auth_url,
              'region_name': instance.region_name,
              'username': instance.auth_ref.username}

    if instance.session:
        kwargs.update(session=instance.session)
    else:
        kwargs.update(token=instance.auth_ref.auth_token)

    client = mogan_client(**kwargs)

    return client


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-baremetal-compute-api-version',
        metavar='<baremetal-compute-api-version>',
        default=utils.env(
            'OS_BAREMETAL_COMPUTE_API_VERSION',
            default=DEFAULT_BAREMETAL_COMPUTE_API_VERSION),
        help=(_('Baremetal compute API version, default=%s '
                '(Env: OS_BAREMETAL_COMPUTE_API_VERSION)') %
              DEFAULT_BAREMETAL_COMPUTE_API_VERSION)
    )
    return parser
