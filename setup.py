import os

from setuptools import find_packages
from setuptools import setup


setup(
    name='pysh',
    version=(open(os.path.join(os.path.dirname(__file__),
                               'pysh',
                               'version.txt'))
             .read().strip()),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'clint',
        'parsimonious',
    ],
    entry_points={
        'console_scripts': [
            'pysh = pysh.repl:main',
        ],
    },
)
