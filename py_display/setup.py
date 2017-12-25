from setuptools import setup, find_packages

setup(
    name='ccd',
    description="Display daemon that communicates directly with LEDs/LCD",
    url='https://github.com/LucasPickering/case-control',
    author='Lucas Pickering',
    packages=find_packages(),
    # GPIO library has to be installed separately:
    # https://sourceforge.net/p/raspberry-gpio-python/wiki/install/
    install_requires=['pyserial'],
    entry_points={
        'console_scripts': ['ccd = ccd.ccd:main']
    },
)
