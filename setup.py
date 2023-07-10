# -*- coding: utf-8 -*-
from setuptools import setup
from mypyc.build import mypycify

packages = [
    "frames2osb",
    "frames2osb.external",
    "frames2osb.pixels",
    "frames2osb.quadtree",
]

package_data = {"": ["*"]}

install_requires = [
    "Pillow>=10.0.0,<11.0.0",
    "numpy>=1.25.1,<2.0.0",
    "typed-argument-parser>=1.8.1,<2.0.0",
]

setup_kwargs = {
    "name": "frames2osb",
    "version": "0.1.0",
    "description": "Turns (video) frames to osu!storyboard",
    "long_description": "None",
    "author": "Rendy Arya Kemal",
    "author_email": "rendyarya22@gmail.com",
    "maintainer": "None",
    "maintainer_email": "None",
    "url": "None",
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "python_requires": ">3.9,<3.11",
    "ext_modules": mypycify(
        [
            "frames2osb/quadtree/osb.py",
            "frames2osb/quadtree/typings.py",
            "frames2osb/quadtree/pixel_extract.py",
        ]
    ),
}


setup(**setup_kwargs)
