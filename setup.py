import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='yak-server',
    version='0.2',
    packages=['yak'],
    install_requires=[
        'Django>=1.8',
        'django-cache-machine>=0.9.1',
        'django-filter>=0.13',
        'django-model-utils>=2.4',
        'django-oauth-toolkit>=0.10.0',
        'djangorestframework>=3.1.0',
        'Pillow>=3.1.1',
        'pypushwoosh>=0.2.0',
        'python-social-auth>=0.2.14',
        'requests>=2.9.1'
    ],
    include_package_data=True,
    license='BSD License',
    description='Server-side implementation of Yeti App Kit built on Django',
    long_description=README,
    url='https://yeti.co/yeti-app-kit/',
    author='Yeti',
    author_email='hello@yeti.co',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
