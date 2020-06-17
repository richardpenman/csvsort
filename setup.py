import os
from distutils.core import setup

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name='csvsort', 
    version='1.6.1',
    packages=['csvsort'],
    package_dir={'csvsort' : '.'}, 
    author='Richard Penman',
    author_email='richard.penman@gmail.com',
    description='Sort large CSV files on disk rather than in memory',
    long_description=read('README.rst'),
    url='https://github.com/richardpenman/csvsort',
    license='lgpl',
)
