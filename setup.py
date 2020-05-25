from setuptools import setup, find_packages
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
      packages=find_packages(),
      package_data={'enlighten2.tleap': ['*.in'],
                    'enlighten2': ['sander/*']},
      entry_points={'console_scripts': ['prep.py = enlighten2.prep:main',
                                        'dynam.py = enlighten2.dynam:main']},
      zip_safe=False)
