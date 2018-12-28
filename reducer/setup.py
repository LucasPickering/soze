from setuptools import setup, find_packages

setup(
    name="soze_reducer",
    description="Service to derive state for LEDs and LCD",
    url="https://github.com/LucasPickering/soze",
    author="Lucas Pickering",
    packages=find_packages(),
    install_requires=["redis"],
    entry_points={
        "console_scripts": ["soze_reducer = soze_reducer.core.reducer:main"]
    },
)
