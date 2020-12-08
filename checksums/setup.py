import setuptools

setuptools.setup(
    name="checksums",
    version="0.0.2",
    description="Testing integrity of files.",
    long_description=open("README.md", "r").read(),
    packages=setuptools.find_packages(),
    python_version=">=3.7",
    install_requires=[
        "click>=7.1.2",
        "tqdm>=4.54.1",
    ],
    entry_points={
        "console_scripts": "checksums=checksums.cli:cli"
    }
)