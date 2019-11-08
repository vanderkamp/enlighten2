from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(name='enlighten2',
      version='0.1',
      description='Protocols and tools to run (automated) atomistic '
                  'simulations of enzyme-ligand systems',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/vanderkamp/enlighten2',
      author='Kirill Zinovjev',
      author_email='kzinovjev@gmail.com',
      license='GPL',
      packages=['enlighten2'],
      zip_safe=False)
