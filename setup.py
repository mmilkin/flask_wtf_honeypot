
"""
Flask-WTF-HoneyPot
=========

WTF-HoneyPot Field

Links
-----

* development _<http://github.com/mmilkin/flask-wtf-honeypot>`_


"""
try:
    import multiprocessing
except ImportError:
    pass

from setuptools import setup

setup(
    name='flask-wtf-honeypot',
    version='0.0.1',
    url='http://github.com/mmilkin/flask-wtf-honeypot',
    license='MIT',
    author='Michael Milkin',
    author_email='mmilkin@gmail.com',
    description='HoneyPot Field for Flask WTForms',
    packages=[
        'flask_wtf_honeypot',
    ],
    test_suite='nose.collector',
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'WTForms>=1.0.5,<2.0'
    ],
    tests_require=[
        'nose',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
