from setuptools import setup, find_packages
from mypyc.build import mypycify

setup(
    # Basic info
    name="frames2osb",
    version="0.1.0",
    author="Rendy Arya Kemal",
    author_email="renrror@gmail.com",
    url="",
    description="Turns (video) frames to osu!storyboard.",
    long_description=open("README.md").read(),
    classifiers=[],
    # Packages and depencies
    packages=find_packages(),
    install_requires=[
        "Pillow",
        "numpy",
        "typed-argument-parser",
    ],
    extras_require={
        "dev": [
            "mypy",
            "flake8",
            "black",
            "types-Pillow",
        ],
    },
    # Scripts
    entry_points={
        "console_scripts": ["frames2osb = frames2osb.cli:main"],
    },
    # Other configurations
    zip_safe=False,
    platforms="any",
    ext_modules=mypycify(
        [
            "frames2osb/convert.py",
            "frames2osb/helper.py",
            "frames2osb/pixels/osb.py",
            "frames2osb/pixels/pixel_extract.py",
            "frames2osb/quadtree/osb.py",
            "frames2osb/quadtree/pixel_extract.py",
        ]
    ),
)
