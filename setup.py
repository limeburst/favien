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
        'favien.web': ['templates/*.*', 'static/*.*'],
    },
    install_requires=[
        'Flask',
        'SQLAlchemy',
        'click',
        'redis',
        'requests',
        'requests_oauthlib',
    ]
)
