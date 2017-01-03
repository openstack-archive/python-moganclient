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

import copy

import mock
import six

from moganclient.common import base
from moganclient.common import exceptions
from moganclient.tests.unit import base as test_base
from moganclient.tests.unit import fakes


class TestResource(test_base.TestBase):

    def test_resource_repr(self):
        r = base.Resource(None, dict(foo='bar', baz='spam'))
        self.assertEqual('<Resource baz=spam, foo=bar>', repr(r))

    def test_getid(self):
        self.assertEqual(4, base.getid(4))

        class TmpObject(object):
            uuid = 4
        self.assertEqual(4, base.getid(TmpObject))

    def test_init_with_attribute_info(self):
        r = base.Resource(None, dict(foo='bar', baz='spam'))
        self.assertTrue(hasattr(r, 'foo'))
        self.assertEqual('bar', r.foo)
        self.assertTrue(hasattr(r, 'baz'))
        self.assertEqual('spam', r.baz)

    def test_resource_lazy_getattr(self):
        fake_manager = mock.Mock()
        return_resource = base.Resource(None, dict(uuid=mock.sentinel.fake_id,
                                                   foo='bar',
                                                   name='fake_name'))
        fake_manager.get.return_value = return_resource

        r = base.Resource(fake_manager,
                          dict(uuid=mock.sentinel.fake_id, foo='bar'))
        self.assertTrue(hasattr(r, 'foo'))
        self.assertEqual('bar', r.foo)
        self.assertFalse(r.is_loaded())

        # Trigger load
        self.assertEqual('fake_name', r.name)
        fake_manager.get.assert_called_once_with(mock.sentinel.fake_id)
        self.assertTrue(r.is_loaded())

        # Missing stuff still fails after a second get
        self.assertRaises(AttributeError, getattr, r, 'blahblah')

    def test_eq(self):
        # Two resources of the same type with the same id: not equal
        r1 = base.Resource(None, {'id': 1, 'name': 'hi'})
        r2 = base.Resource(None, {'id': 1, 'name': 'hello'})
        self.assertNotEqual(r1, r2)

        # Two resources of different types: never equal
        r1 = base.Resource(None, {'id': 1})
        r2 = fakes.FakeResource(None, {'id': 1})
        self.assertNotEqual(r1, r2)

        # Two resources with no ID: equal if their info is equal
        r1 = base.Resource(None, {'name': 'joe', 'age': 12})
        r2 = base.Resource(None, {'name': 'joe', 'age': 12})
        self.assertEqual(r1, r2)

    def test_resource_object_with_request_ids(self):
        resp_obj = fakes.create_response_obj_with_header()
        r = base.Resource(None, {'name': '1'}, resp=resp_obj)
        self.assertEqual(fakes.FAKE_REQUEST_ID_LIST, r.request_ids)

    def test_resource_object_with_compute_request_ids(self):
        resp_obj = fakes.create_response_obj_with_compute_header()
        r = base.Resource(None, {'name': '1'}, resp=resp_obj)
        self.assertEqual(fakes.FAKE_REQUEST_ID_LIST, r.request_ids)


class TestManager(test_base.TestBase):
    fake_manager = fakes.create_resource_manager()

    @mock.patch.object(fakes.FakeHTTPClient, 'get')
    def test_manager_get(self, mock_get):
        mock_get.return_value = (fakes.create_response_obj_with_header(),
                                 mock.MagicMock())
        fake_resource = fakes.FakeResource(
            None, dict(uuid=fakes.FAKE_RESOURCE_ID,
                       name=fakes.FAKE_RESOURCE_NAME))
        result = self.fake_manager.get(fake_resource)
        self.assertIsInstance(result, base.Resource)
        self.assertIsInstance(result._info, mock.MagicMock)
        self.assertTrue(result.is_loaded())
        expect_url = (fakes.FAKE_RESOURCE_ITEM_URL % fakes.FAKE_RESOURCE_ID)
        mock_get.assert_called_once_with(expect_url, headers={})

    @mock.patch.object(fakes.FakeHTTPClient, 'get')
    def test_manager_list(self, mock_get):
        mock_get.return_value = (fakes.create_response_obj_with_header(),
                                 mock.MagicMock())
        result = self.fake_manager.list()
        self.assertIsInstance(result, base.ListWithMeta)
        self.assertEqual([], result)
        expect_url = fakes.FAKE_RESOURCE_COLLECTION_URL
        mock_get.assert_called_once_with(expect_url, headers={})

    @mock.patch.object(fakes.FakeHTTPClient, 'patch')
    def test_manager_update(self, mock_patch):
        mock_patch.return_value = (fakes.create_response_obj_with_header(),
                                   mock.MagicMock())
        fake_resource = fakes.FakeResource(
            None, dict(uuid=fakes.FAKE_RESOURCE_ID,
                       name=fakes.FAKE_RESOURCE_NAME))
        result = self.fake_manager.update(fake_resource)
        self.assertIsInstance(result, base.Resource)
        self.assertIsInstance(result._info, mock.MagicMock)
        self.assertFalse(result.is_loaded())
        expect_url = (fakes.FAKE_RESOURCE_ITEM_URL % fakes.FAKE_RESOURCE_ID)
        mock_patch.assert_called_once_with(expect_url, data=fake_resource,
                                           headers={})

    @mock.patch.object(fakes.FakeHTTPClient, 'delete')
    def test_manager_delete(self, mock_delete):
        mock_delete.return_value = (fakes.create_response_obj_with_header(),
                                    None)
        fake_resource = fakes.FakeResource(
            None, dict(uuid=fakes.FAKE_RESOURCE_ID,
                       name=fakes.FAKE_RESOURCE_NAME))
        result = self.fake_manager.delete(fake_resource)
        self.assertIsInstance(result, base.TupleWithMeta)
        self.assertEqual(tuple(), result)
        expect_url = (fakes.FAKE_RESOURCE_ITEM_URL % fakes.FAKE_RESOURCE_ID)
        mock_delete.assert_called_once_with(expect_url, headers={})

    @mock.patch.object(fakes.FakeHTTPClient, 'post')
    def test_manager_create(self, mock_post):
        mock_post.return_value = (fakes.create_response_obj_with_header(),
                                  mock.MagicMock())
        fake_resource = fakes.FakeResource(
            None, dict(uuid=fakes.FAKE_RESOURCE_ID,
                       name=fakes.FAKE_RESOURCE_NAME))
        result = self.fake_manager.create(fake_resource)
        self.assertIsInstance(result, base.Resource)
        self.assertIsInstance(result._info, mock.MagicMock)
        self.assertFalse(result.is_loaded())
        expect_url = fakes.FAKE_RESOURCE_COLLECTION_URL
        mock_post.assert_called_once_with(expect_url, data=fake_resource,
                                          headers={})

    @mock.patch.object(fakes.FakeHTTPClient, 'get')
    def test_manager_find(self, mock_get):
        fake_json_body_1 = dict(uuid=fakes.FAKE_RESOURCE_ID,
                                name=fakes.FAKE_RESOURCE_NAME)
        fake_json_body_2 = dict(uuid='no_existed_id',
                                name='no_existed_name')
        mock_get.side_effect = [
            (fakes.create_response_obj_with_header(),
             {'resources': [fake_json_body_1,
                            fake_json_body_2]}),
            (fakes.create_response_obj_with_header(),
             fake_json_body_1)
        ]
        result = self.fake_manager.find(uuid=fakes.FAKE_RESOURCE_ID,
                                        name=fakes.FAKE_RESOURCE_NAME)
        self.assertIsInstance(result, base.Resource)
        self.assertEqual(fakes.FAKE_RESOURCE_ID, result.uuid)
        self.assertEqual(fakes.FAKE_RESOURCE_NAME, result.name)
        self.assertTrue(result.is_loaded())
        expect_collection_url = fakes.FAKE_RESOURCE_COLLECTION_URL
        expect_item_url = (fakes.FAKE_RESOURCE_ITEM_URL %
                           fakes.FAKE_RESOURCE_ID)
        mock_get.assert_has_calls(
            [mock.call(expect_collection_url, headers={}),
             mock.call(expect_item_url, headers={})])

    @mock.patch.object(fakes.FakeHTTPClient, 'get')
    def test_manager_find_no_result(self, mock_get):
        mock_get.return_value = (fakes.create_response_obj_with_header(),
                                 {'resources': []})
        self.assertRaises(exceptions.NotFound,
                          self.fake_manager.find,
                          uuid=fakes.FAKE_RESOURCE_ID,
                          name=fakes.FAKE_RESOURCE_NAME)
        expect_collection_url = fakes.FAKE_RESOURCE_COLLECTION_URL
        mock_get.assert_called_once_with(expect_collection_url, headers={})

    @mock.patch.object(fakes.FakeHTTPClient, 'get')
    def test_manager_find_more_than_one_result(self, mock_get):
        fake_json_body_1 = dict(uuid=fakes.FAKE_RESOURCE_ID,
                                name=fakes.FAKE_RESOURCE_NAME)
        fake_json_body_2 = copy.deepcopy(fake_json_body_1)
        mock_get.return_value = (fakes.create_response_obj_with_header(),
                                 {'resources': [fake_json_body_1,
                                                fake_json_body_2]})
        self.assertRaises(exceptions.NoUniqueMatch,
                          self.fake_manager.find,
                          uuid=fakes.FAKE_RESOURCE_ID,
                          name=fakes.FAKE_RESOURCE_NAME)
        expect_collection_url = fakes.FAKE_RESOURCE_COLLECTION_URL
        mock_get.assert_called_once_with(expect_collection_url, headers={})


class ListWithMetaTest(test_base.TestBase):
    def test_list_with_meta(self):
        resp = fakes.create_response_obj_with_header()
        obj = base.ListWithMeta([], resp)
        self.assertEqual([], obj)
        # Check request_ids attribute is added to obj
        self.assertTrue(hasattr(obj, 'request_ids'))
        self.assertEqual(fakes.FAKE_REQUEST_ID_LIST, obj.request_ids)


class DictWithMetaTest(test_base.TestBase):
    def test_dict_with_meta(self):
        resp = fakes.create_response_obj_with_header()
        obj = base.DictWithMeta({}, resp)
        self.assertEqual({}, obj)
        # Check request_ids attribute is added to obj
        self.assertTrue(hasattr(obj, 'request_ids'))
        self.assertEqual(fakes.FAKE_REQUEST_ID_LIST, obj.request_ids)


class TupleWithMetaTest(test_base.TestBase):
    def test_tuple_with_meta(self):
        resp = fakes.create_response_obj_with_header()
        expected_tuple = (1, 2)
        obj = base.TupleWithMeta(expected_tuple, resp)
        self.assertEqual(expected_tuple, obj)
        # Check request_ids attribute is added to obj
        self.assertTrue(hasattr(obj, 'request_ids'))
        self.assertEqual(fakes.FAKE_REQUEST_ID_LIST, obj.request_ids)


class StrWithMetaTest(test_base.TestBase):
    def test_str_with_meta(self):
        resp = fakes.create_response_obj_with_header()
        obj = base.StrWithMeta('test-str', resp)
        self.assertEqual('test-str', obj)
        # Check request_ids attribute is added to obj
        self.assertTrue(hasattr(obj, 'request_ids'))
        self.assertEqual(fakes.FAKE_REQUEST_ID_LIST, obj.request_ids)


class BytesWithMetaTest(test_base.TestBase):
    def test_bytes_with_meta(self):
        resp = fakes.create_response_obj_with_header()
        obj = base.BytesWithMeta(b'test-bytes', resp)
        self.assertEqual(b'test-bytes', obj)
        # Check request_ids attribute is added to obj
        self.assertTrue(hasattr(obj, 'request_ids'))
        self.assertEqual(fakes.FAKE_REQUEST_ID_LIST, obj.request_ids)


if six.PY2:
    class UnicodeWithMetaTest(test_base.TestBase):
        def test_unicode_with_meta(self):
            resp = fakes.create_response_obj_with_header()
            obj = base.UnicodeWithMeta(u'test-unicode', resp)
            self.assertEqual(u'test-unicode', obj)
            # Check request_ids attribute is added to obj
            self.assertTrue(hasattr(obj, 'request_ids'))
            self.assertEqual(fakes.FAKE_REQUEST_ID_LIST, obj.request_ids)
