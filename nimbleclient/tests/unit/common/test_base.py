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

import mock
import six

from nimbleclient.common import base
from nimbleclient.tests.unit import base as test_base
from nimbleclient.tests.unit import fakes


class TestResource(test_base.TestBase):

    def test_resource_repr(self):
        r = base.Resource(None, dict(foo='bar', baz='spam'))
        self.assertEqual('<Resource baz=spam, foo=bar>', repr(r))

    def test_getid(self):
        self.assertEqual(4, base.getid(4))

        class TmpObject(object):
            id = 4
        self.assertEqual(4, base.getid(TmpObject))

    def test_init_with_attribute_info(self):
        r = base.Resource(None, dict(foo='bar', baz='spam'))
        self.assertTrue(hasattr(r, 'foo'))
        self.assertEqual('bar', r.foo)
        self.assertTrue(hasattr(r, 'baz'))
        self.assertEqual('spam', r.baz)

    def test_resource_lazy_getattr(self):
        fake_manager = mock.Mock()
        return_resource = base.Resource(None, dict(id=mock.sentinel.fake_id,
                                                   foo='bar',
                                                   name='fake_name'))
        fake_manager.get.return_value = return_resource

        r = base.Resource(fake_manager,
                          dict(id=mock.sentinel.fake_id, foo='bar'))
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
        r2 = fakes.FaksResource(None, {'id': 1})
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

    def setUp(self):
        super(TestManager, self).setUp()
        self.fake_manager.api.reset_mock()

    def test_manager_get(self):
        fake_resource = fakes.FaksResource(
            None, dict(id=fakes.FAKE_RESOURCE_ID,
                       name=fakes.FAKE_RESOURCE_NAME))
        result = self.fake_manager.get(fake_resource)
        self.assertIsInstance(result, base.Resource)
        expect_url = (fakes.FAKE_RESOURCE_COLLECTION_URL %
                      fakes.FAKE_RESOURCE_ID)
        self.fake_manager.api.get.assert_called_once_with(expect_url,
                                                          headers={})

    def test_manager_list(self):
        pass

    def test_manager_update(self):
        pass

    def test_manager_delete(self):
        pass

    def test_manager_create(self):
        pass

    def test_manager_find(self):
        pass


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
