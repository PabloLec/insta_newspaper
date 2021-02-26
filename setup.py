from setuptools import setup, find_packages

with open("requirements.txt", "r") as req_fp:
    required_packages = req_fp.readlines()

# Use README for long description
with open("README.md", "r") as readme_fp:
    long_description = readme_fp.read()

setup(
    name="insta_newspaper",
    version="1.0",
    author="PabloLec",
    author_email="pablolec@pm.me",
    description="A CLI to download old newspaper front pages and post it on Instagram. ",
    license="MIT License",
    keywords="instagram bot",
    url="https://github.com/pabloleco/insta_newspaper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests", "docs"]),
    entry_points={
        "console_scripts": [
            "insta_newspaper = insta_newspaper:main",
        ],
    },
    install_requires=required_packages,
    package_data={
        "insta_newspaper": [
            "insta_newspaper/config.yaml.example",
            "insta_newspaper/instagram_strings.yaml",
            "newspaper_reference.yaml",
        ]
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
