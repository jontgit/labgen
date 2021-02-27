import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(
    name="labgen", # Replace with your username
    version="0.0.1",
    author="Jonny T",
    author_email="jonomaster@live.co.uk",
    description="Generates GNS3/EVEng Labs on the fly.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="<https://github.com/authorname/templatepackage>",
    packages=setuptools.find_packages(),
      install_requires=[
      'netmiko',
      'regex'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
