import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'sqlalchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'webtest',
    'psycopg2',
    'httplib2',
    'defpage.lib',
    ]

setup(name='defpage.meta',
      version='0.1',
      description='defpage metadata server unit',
      long_description=README + '\n\n' +  CHANGES,
      packages=find_packages(),
      namespace_packages=['defpage'],
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      tests_require = requires,
      test_suite="defpage.meta",
      entry_points = """\
      [paste.app_factory]
      main = defpage.meta:main
      """
      )
