from setuptools import setup, find_packages

setup(
    name='ccs',
    description="Server that controls configuration of connected LCD and LEDs",
    url='https://github.com/LucasPickering/case-control',
    author='Lucas Pickering',
    packages=find_packages(),
    install_requires=['flask'],
    entry_points={
        'console_scripts': ['ccs = ccs.core.ccs:main']
    },
)
