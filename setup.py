from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'readme.md'), encoding='utf-8') as f:
    long_description = f.read()


with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().split('\n')

setup(
    name='filtered-intervaltree',
    version='0.0.4',

    description='an intervaltree with early exit bloom filters',
    long_description=long_description,

    url='https://github.com/lostinplace/filtered-intervaltree',

    author='cwheeler',
    author_email='cmwhee@gmail.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    requires=[],

    keywords='rbtree intervaltree bloomfilter',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['test']),
    install_requires=requirements,
    extras_require={
        'test': ['coverage'],
    }
)
