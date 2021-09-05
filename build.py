from mypyc.build import mypycify

extensions = mypycify(
    [
        "frames2osb/convert.py",
        "frames2osb/helper.py",
        "frames2osb/pixels",
        "frames2osb/quadtree",
    ]
)


def build(setup_kwargs):
    """Build extension modules."""
    kwargs = dict(ext_modules=extensions, zip_safe=False)
    setup_kwargs.update(kwargs)
