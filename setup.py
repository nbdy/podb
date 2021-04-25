from setuptools import setup, find_packages

setup(
    long_description=open("README.md", "r").read(),
    name="podb",
    version="1.46",
    description="python object database",
    author="Pascal Eberlein",
    author_email="pascal@eberlein.io",
    url="https://github.com/nbdy/podb",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords="python object database",
    packages=find_packages(),
    install_requires=["setuptools", "filelock"],
    long_description_content_type="text/markdown",
)
