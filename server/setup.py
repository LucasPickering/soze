from setuptools import setup, find_packages

setup(name='ccs',
      description="Server that controls configuration of connected LCD and LEDs",
      url='https://github.com/LucasPickering/Case-Control-CLI',
      author='Lucas Pickering',
      packages=find_packages(),
      install_requires=['flask', 'pyserial'])
