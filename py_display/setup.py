from setuptools import setup, find_packages

setup(
    name='soze_display',
    description="Display daemon that communicates directly with LEDs/LCD",
    url='https://github.com/LucasPickering/soze',
    author='Lucas Pickering',
    packages=find_packages(),
    # Motor HAT library can be installed from the submodule in this repo
    install_requires=['soze_core', 'pyserial'],
    entry_points={
        'console_scripts': ['sozed = soze_display.display:main']
    },
)
