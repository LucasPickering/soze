from setuptools import setup, find_packages

setup(
    name='ccs',
    description="Server that controls configuration of connected LCD and LEDs",
    url='https://github.com/LucasPickering/Case-Control-CLI',
    author='Lucas Pickering',
    packages=find_packages(),
    # RPIO library has to be installed manually: https://github.com/limuxy/RPIO
    install_requires=['flask', 'pyserial'],
    entry_points={
        'console_scripts': ['ccs = ccs.core.ccs:main']
    },
)
