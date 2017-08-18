#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    required = f.read().splitlines()

packages = find_packages(exclude=['ex_setup'])

setup(
    name='aws_lambda_tools',
    version='1.0.0',
    author='StoryStream',
    author_email='hello@storystream.it',
    description='A set of basic utilities for development with AWS lambda',
    url='https://github.com/story-stream/aws-lambda-tools',
    packages=packages,
    install_requires=required,
    zip_safe=False,
)
