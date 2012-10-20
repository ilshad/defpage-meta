import unittest
import transaction
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
        self.dbs = _testingDB()

    def tearDown(self):
        testing.tearDown()

    def test_quick(self):
        pass

SETTINGS = {'sqlalchemy.url':'sqlite://'}

class FuncTests(unittest.TestCase):

    def setUp(self):
        from defpage.meta import main
        app = main({}, **SETTINGS)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/', status=404)
