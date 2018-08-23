from setuptools import setup, find_packages

setup(
    name='soze_client',
    description="Client wrapper for iteracting with the server that controls an LCD and LEDs",
    url='https://github.com/LucasPickering/soze',
    author='Lucas Pickering',
    packages=find_packages(),
    install_requires=['requests'],
    entry_points={
        'console_scripts': ['sozec = soze_client.client:main']
    },
)
