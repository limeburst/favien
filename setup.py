"""
Favien
======

Network canvas community.

"""
from setuptools import setup


setup(
    name='Favien',
    version='dev',
    url='https://github.com/limeburst/favien',
    author='Jihyeok Seo',
    author_email='me@limeburst.net',
    description='Network canvas community',
    long_description=__doc__,
    zip_safe=False,
    packages=['favien', 'favien.web'],
    package_data={
        'favien.web': ['templates/*.*', 'static/*.*',
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
        'Flask',
        'Flask-Babel',
        'SQLAlchemy',
        'boto',
        'click',
        'redis',
        'requests',
        'requests_oauthlib',
    ]
)
