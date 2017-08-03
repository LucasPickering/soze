from setuptools import setup, find_packages

setup(name='ccs',
      description="Server that controls configuration of connected LCD and LEDs",
      url='https://github.com/LucasPickering/Case-Control-CLI',
      author='Lucas Pickering',
      packages=find_packages(),
      entry_points={
          'console_scripts': ['ccs = ccs:main']
      },
      # scripts=['cc.py'],
      # data_files=('/etc/systemd/user', ['casecontrol.service']),
      install_requires=['flask'])
