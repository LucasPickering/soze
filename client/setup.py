from setuptools import setup, find_packages

setup(
    name='ccc',
    description="Client wrapper for iteracting with the server that controls an LCD and LEDs",
    url='https://github.com/LucasPickering/Case-Control-CLI',
    author='Lucas Pickering',
    packages=find_packages(),
    install_requires=['requests'],
    entry_points={
        'console_scripts': ['ccc = ccc.ccc:main']
    },
)
