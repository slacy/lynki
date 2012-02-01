from setuptools import setup, find_packages

setup(name='lynki',
      version='0.1',
      packages=find_packages(),
      entry_points={
        'console_scripts': [
            'lynki = lynki.simple:main',
            ],
        },
      )
