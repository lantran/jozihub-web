#!/bin/bash

set -e

# Crappy way of dealing with dependencies not available on Pypi and
# pip has deprecated support for installing stuff straight from GitHub
mkdir -p src/project/media/uploads
pip install "pip<1.5"
pip install -e .
