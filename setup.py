#!/usr/bin/env python

# This is a shim to hopefully allow Github to detect the package, build is done with poetry

import setuptools

if __name__ == "__main__":
    setuptools.setup(
        name="rich",
        packages=setuptools.find_packages(include=["rich", "rich.*"]),
    )
