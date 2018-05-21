from setuptools import setup, find_packages

setup(
    name='ccd',
    description="Display daemon that communicates directly with LEDs/LCD",
    url='https://github.com/LucasPickering/case-control',
    author='Lucas Pickering',
    packages=find_packages(),
    # Motor HAT library can be installed from the submodule in this repo
    install_requires=['pyserial'],
    entry_points={
        'console_scripts': ['ccd = ccd.ccd:main']
    },
)
