import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="oceantools",
    version="0.0.0",
    author="Salvatore Causio",
    author_email="salvatore.causio@cmcc.it",
    description="A collection of simple tools for regular netcdf",
    long_description='',
    url="https://github.com/scausio/oceantools.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
