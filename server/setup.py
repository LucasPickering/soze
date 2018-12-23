from setuptools import setup, find_packages

setup(
    name="soze_server",
    description="Server that controls configuration of connected LCD and LEDs",
    url="https://github.com/LucasPickering/soze",
    author="Lucas Pickering",
    packages=find_packages(),
    install_requires=["soze_core", "flask"],
    entry_points={"console_scripts": ["sozes = soze_server.core.server:main"]},
)
