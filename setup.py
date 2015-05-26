"""
Favien
======

Network canvas community.

"""
from setuptools import setup


setup(
    name='Favien',
    version='0.0.0',
    url='https://github.com/limeburst/favien',
    author='Jihyeok Seo',
    author_email='me@limeburst.net',
    description='Network canvas community',
    long_description=__doc__,
    zip_safe=False,
    packages=['favien', 'favien.web'],
    package_data={
        'favien': ['migrations/env.py', 'migrations/*.mako',
                   'migrations/versions/*.py'],
        'favien.web': ['templates/*.*', 'templates/*/*.*',
                       'static/*.*', 'static/*/*.*',
                       'translations/*/LC_MESSAGES/*'],
    },
    message_extractors={
        'favien/web/templates': [
            ('**.html', 'jinja2', {
                'extensions': 'jinja2.ext.autoescape,'
                              'jinja2.ext.with_'
            })
        ]
    },
    install_requires=[
        'Flask == 0.10.1',
        'Flask-Babel == 0.9',
        'SQLAlchemy == 0.9.9',
        'alembic == 0.7.4',
        'boto == 2.36.0',
        'click == 3.3',
        'redis == 2.10.3',
        'requests == 2.6.0',
        'requests_oauthlib == 0.4.2',
    ],
    entry_points={
        'console_scripts': ['fav = favien.cli:cli'],
    },
    classifiers=[
        'License :: OSI Approved '
        ':: GNU Affero General Public License v3 or later (AGPLv3+)',
    ]
)
