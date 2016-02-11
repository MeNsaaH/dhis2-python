from setuptools import setup

setup(name='dhis',
      version='0.1',
      description='Utilities for working with DHIS2',
      url='https://github.com/dhis2/dhis2-python',
      author='DHIS2 Development Team',
      author_email='post@dhis2.org',
      license='BSD',
      packages=['dhis'],
      zip_safe=False,
      install_requires=['requests','sqlparse','psycopg2'])
