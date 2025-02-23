from setuptools import setup

setup(
    name="asynclogger",
    version="0.1.0",
    packages=["asynclogger"],
    author="Islam Tazerout",
    author_email="islamtazerout3@gmail.com",
    description="A lightweight and efficient asynchronous logging package for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ixlammm/asynclogger",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "aiofile",
        "colorist"
    ]
)