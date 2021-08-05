import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
meta_info = {}
with open(os.path.join(here, 'typish', '_meta.py'), 'r') as f:
    exec(f.read(), meta_info)

with open('README.md', 'r') as fh:
    long_description = fh.read()


requirements = []

test_requirements = [
    'numpy',
    'nptyping>=1.3.0',
    'pycodestyle',
    'pylint',
    'mypy',
    'pytest',
    'coverage',
    'codecov',
]

extras = {
    'test': test_requirements,
}


setup(
    name=meta_info['__title__'],
    version=meta_info['__version__'],
    author=meta_info['__author__'],
    author_email=meta_info['__author_email__'],
    description=meta_info['__description__'],
    url=meta_info['__url__'],
    license=meta_info['__license__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=('tests', 'tests.*', 'test_resources', 'test_resources.*')),
    install_requires=requirements,
    tests_require=test_requirements,
    extras_require=extras,
    test_suite='tests',
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
