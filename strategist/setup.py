# NOTE: This file is using ONLY for running py.test tool correctly
import os
from setuptools import setup


def get_packages(package):
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, '__init__.py'))
    ]


args = dict(
    name='app',
    version="1.0.0",
    license='BSD',
    packages=get_packages('app'),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)


if __name__ == '__main__':
    setup(**args)
