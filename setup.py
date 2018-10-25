from setuptools import setup, find_packages
from perkeeppy import __version__

setup(
    name="perkeeppy",
    version=__version__,
    description="Library for interacting with the Perkeep API",
    packages=find_packages(),
    maintainer="Dariusz Anzorge",
    maintainer_email="d.anzorge@gmail.com",
    author="Martin Atkins",
    author_email="mart@degeneration.co.uk",

    test_suite='tests.get_tests',

    setup_requires=[
        'sphinx>=1.7.0'
    ],
    tests_require=[
        'pycodestyle',
        'requests_mock',
        'requests_toolbelt'
    ],
    install_requires=[
        "requests",
        "python-dateutil",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6"
    ]
)
