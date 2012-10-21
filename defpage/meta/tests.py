# coding: utf-8

import unittest
import transaction
import base64
from pyramid import testing

def _testingDB():
    from sqlalchemy import create_engine
    from defpage.meta.sql import (DBSession,
                                  Base,
                                  Collection,
                                  Source,
                                  Transmission,
                                  CollectionUserRole,
                                  Document,
                                  Entry,
                                  initialize_sql)
    
    initialize_sql(create_engine('sqlite://'))
    return DBSession

class UnitTests(unittest.TestCase):

    def setUp(self):
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        #self.dbs = _testingDB()

    def tearDown(self):
        testing.tearDown()

    def test_quick(self):
        pass

SETTINGS = {'sqlalchemy.url':'sqlite://',
            'system.system_user':'system'}

def _basic_user(userid):
    return "Basic " + base64.b64encode(str(userid) + ":1")

class FuncTests(unittest.TestCase):

    def setUp(self):
        from defpage.meta import main
        app = main({}, **SETTINGS)
        from webtest import TestApp
        self.app = TestApp(app)

    def tearDown(self):
        self.app.reset()

    def test_functional(self):
        r = self.app.get('/', status=404)

        # get collections info
        r = self.app.get('/collections/',
                         params={'info':'total_num'})
        self.assertEqual(r.json['total_num'], 0)

        r = self.app.get('/collections/',
                         params={'info':'max_id'})
        self.assertEqual(r.json['max_id'], None)

        # create collection
        r = self.app.post_json('/collections/',
                               params={'title':u'Первая коллекция',
                                       'owner':1},
                               status=201)
        self.assertEqual(r.json['id'], 1)

        r = self.app.post_json('/collections/',
                               params={'title':u'Вторая коллекция',
                                       'owner':1},
                               status=201)
        self.assertEqual(r.json['id'], 2)

        # get collections info
        r = self.app.get('/collections/',
                         params={'info':'total_num'})
        self.assertEqual(r.json['total_num'], 2)

        r = self.app.get('/collections/',
                         params={'info':'max_id'})
        self.assertEqual(r.json['max_id'], 2)

        r = self.app.get('/collections/',
                         params={'user_id':1})
        self.assertEqual(type(r.json), list)

        self.assertEqual(r.json[0]['id'], 1)
        self.assertEqual(r.json[0]['title'], u'Первая коллекция')
        self.assertEqual(r.json[0]['role'], 'owner')

        self.assertEqual(r.json[1]['id'], 2)
        self.assertEqual(r.json[1]['title'], u'Вторая коллекция')
        self.assertEqual(r.json[1]['role'], 'owner')

        # get collection
        r = self.app.get('/collections/1',
                         headers={'Authorization':_basic_user(1)})
        self.assertEqual(r.json['title'], u'Первая коллекция')
        #self.assertEqual(r.json['source'], '')
