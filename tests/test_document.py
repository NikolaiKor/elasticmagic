import datetime

import dateutil

from elasticmagic.types import Type, String, Integer, Date, Object, List
from elasticmagic.compat import string_types
from elasticmagic.document import Document
from elasticmagic.expression import Field

from .base import BaseTestCase


class GroupDocument(Document):
    name = Field(String)

class TagDocument(Document):
    id = Field(Integer)
    name = Field(String)

class TestDocument(Document):
    name = Field('test_name', String())
    status = Field(Integer)
    group = Field(Object(GroupDocument))
    tags = Field(List(Object(TagDocument)))
    date_created = Field(Date)
    unused = Field(String)


class DocumentTestCase(BaseTestCase):
    def test_document(self):
        class GroupDocument(Document):
            name = Field(String)

        class TagDocument(Document):
            id = Field(Integer)
            name = Field(String)

        class TestDocument(Document):
            name = Field('test_name', String())
            status = Field(Integer)
            group = Field(Object(GroupDocument))
            tags = Field(List(Object(TagDocument)))
            date_created = Field(Date)
            unused = Field(String)

        self.assertIsInstance(TestDocument._id, Field)
        self.assertIsInstance(TestDocument._id._type, String)
        self.assertIsInstance(TestDocument.name, Field)
        self.assertIsInstance(TestDocument.name._type, String)
        self.assertIsInstance(TestDocument.status, Field)
        self.assertIsInstance(TestDocument.status._type, Integer)
        self.assertIsInstance(TestDocument.group, Field)
        self.assertIsInstance(TestDocument.group._type, Object)
        self.assertIsInstance(TestDocument.group.f.name, Field)
        self.assertIsInstance(TestDocument.group.f.name._type, String)
        self.assertIsInstance(TestDocument.group.f.missing, Field)
        self.assertIsInstance(TestDocument.group.f.missing._type, Type)

        doc = TestDocument()
        self.assertIs(doc._id, None)
        self.assertIs(doc.name, None)
        self.assertIs(doc.status, None)
        doc._id = 123
        self.assertIsInstance(doc._id, int)
        self.assertEqual(doc._id, 123)

        doc = TestDocument(_id=123)
        self.assertIsInstance(doc._id, int)
        self.assertEqual(doc._id, 123)
        self.assertIs(doc.name, None)
        self.assertIs(doc.status, None)

        doc = TestDocument(_id=123, name='Test name', status=0,
                           group=GroupDocument(name='Test group'),
                           tags=[TagDocument(id=1, name='Test tag'),
                                 TagDocument(id=2, name='Just tag')])
        self.assertIsInstance(doc._id, int)
        self.assertEqual(doc._id, 123)
        self.assertIsInstance(doc.name, string_types)
        self.assertEqual(doc.name, 'Test name')
        self.assertIsInstance(doc.status, int)
        self.assertEqual(doc.status, 0)
        self.assertIsInstance(doc.group, GroupDocument)
        self.assertIsInstance(doc.group.name, string_types)
        self.assertEqual(doc.group.name, 'Test group')
        self.assertIsInstance(doc.tags, list)
        self.assertIsInstance(doc.tags[0].name, string_types)
        self.assertEqual(doc.tags[0].name, 'Test tag')

        hit_doc = TestDocument(
            _hit={
                '_id':'123',
                '_source': {
                    'test_name': 'Test name',
                    'status': 0,
                    'group': {'name': 'Test group'},
                    'tags': [{'id': 1, 'name': 'Test tag'},
                             {'id': 2, 'name': 'Just tag'}],
                    'date_created': '2014-08-14T14:05:28.789Z',
                }
            }
        )
        self.assertEqual(hit_doc._id, '123')
        self.assertEqual(hit_doc.name, 'Test name')
        self.assertEqual(hit_doc.status, 0)
        self.assertIsInstance(hit_doc.group, GroupDocument)
        self.assertEqual(hit_doc.group.name, 'Test group')
        self.assertIsInstance(hit_doc.tags, list)
        self.assertIsInstance(hit_doc.tags[0], TagDocument)
        self.assertEqual(hit_doc.tags[0].id, 1)
        self.assertEqual(hit_doc.tags[0].name, 'Test tag')
        self.assertEqual(hit_doc.tags[1].id, 2)
        self.assertEqual(hit_doc.tags[1].name, 'Just tag')
        self.assertEqual(hit_doc.date_created,
                         datetime.datetime(2014, 8, 14, 14, 5, 28, 789000, dateutil.tz.tzutc()))
        self.assertIs(hit_doc.unused, None)
        # 1/0

    def test_to_dict(self):
        doc = TestDocument(_id=123, name='Test name', status=0,
                           group=GroupDocument(name='Test group'),
                           tags=[TagDocument(id=1, name='Test tag'),
                                 TagDocument(id=2, name='Just tag')])
        self.assertEqual(
            doc.to_dict(),
            {
                'name': 'Test name',
                'status': 0,
                'group': {
                    'name': 'Test group'
                },
                'tags': [
                    {'id': 1, 'name': 'Test tag'},
                    {'id': 2, 'name': 'Just tag'},
                ],
                'date_created': None,
                'unused': None,
            }
        )
        

    def test_inheritance(self):
        class InheritedDocument(TestDocument):
            description = Field(String)

        doc = InheritedDocument(_id=123)
        print doc.__class__._fields
        self.assertIsInstance(doc._id, int)
        self.assertEqual(doc._id, 123)
        self.assertIs(doc.name, None)
        self.assertIs(doc.status, None)
        self.assertIs(doc.description, None)

        self.assertEqual(
            doc.to_dict(),
            {
                'name': None,
                'status': None,
                'group': None,
                'tags': None,
                'date_created': None,
                'unused': None,
                'description': None,
            }
        )
        


# class ProductCompanyDoc(Document):
#     id = Field(Integer)


# class ProductDoc(Document):
#     __doc_type__ = 'product'

#     name = Field(String)
#     keywords = Field(String)
#     name_keywords = Field(String)
#     description = Field(String)

#     company = Field(Object(ProductCompanyDoc))