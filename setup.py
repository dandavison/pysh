import os

from setuptools import find_packages
from setuptools import setup


def parse_requirements():
    with open('requirements.txt') as fp:
        return [
            line.strip().split('==')[0]
            for line in fp
            if not line.startswith('#')
        ]


setup(
    name='pysh',
    version=(open(os.path.join(os.path.dirname(__file__),
                               'pysh',
                               'version.txt'))
             .read().strip()),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=parse_requirements(),
    entry_points={
        'console_scripts': [
            'pysh = pysh.repl:repl',
        ],
    },
)
