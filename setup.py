from setuptools import setup


with open('README.md', 'r') as fh:
    long_description = fh.read()


setup(
    name='typish',
    version='1.3.1',
    author='Ramon Hagenaars',
    author_email='ramon.hagenaars@gmail.com',
    description='Functionality for types',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ramonhagenaars/typish',
    packages=[
        'typish',
    ],
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
    ]
)
