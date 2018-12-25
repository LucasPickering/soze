from setuptools import setup, find_packages

setup(
    name="soze_api",
    description="API to expose configuration of connected LCD and LEDs",
    url="https://github.com/LucasPickering/soze",
    author="Lucas Pickering",
    packages=find_packages(),
    install_requires=["flask", "flatten-dict", "redis"],
    entry_points={"console_scripts": ["sozes = soze_api.api:main"]},
)
