"""
Pre render script to run inside clarisse on the render node.

Strips drive letters on windows. 
Ensures images are renderable for the given range.
Ensures directories exist for renders.
"""
import argparse
import errno
import os
import re
import sys
from contextlib import contextmanager

import ix

LETTER_RX = re.compile(r"^([a-zA-Z]):")


@contextmanager
def disabled_app():
    """
    Run functions in the app while disabled.

    Clarisse crashes while resolving drive letters in contexts unless the
    operation is done while disabled.
    """
    app = ix.application
    app.disable()
    yield
    app.enable()


def main():
    """
    Prepare this project to be rendered.
    """
    desc = "Prepare a Clarisse project file for rendering on Conductor"
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument(
        "-convert_windows_paths",
        action="store_true",
        default=True,
        help="If this was submitted from windows, strip drive letters.",
    )

    parser.add_argument(
        "-range", nargs=2, type=int, help="Ensure image ranges are turned on."
    )

    parser.add_argument("-images", nargs="+", type=str, help="Image object names.")

    options, _ = parser.parse_known_args()
    ix.log_info("convert_windows_paths {}".format(options.convert_windows_paths))

    resolve_contexts()

    # strip regular drive letters AFTER resolving contexts so we catch any paths
    # that were inside contexts.
    if options.convert_windows_paths:
        convert_windows_paths()

    if options.range and options.images:
        start, end = options.range
        force_image_ranges(start, end, options.images)

    ensure_image_directories(options.images)


def resolve_contexts():
    """
    Find the root context and recurse down, resolving xrefs in children.

    If a context (A) is a reference to another file and that file
    contains a reference context (B), and A's filepath is wrong, then we
    don't know anything about B, so we can't gather all contexts in one
    hit and replace drive letters. We must recurse down, and for each
    reference context, resolve its path and then visit the contexts it
    contains.

    We have to disable the app for this operation otherwise it tends to crash Clarisse.
    """
    contexts = ix.api.OfContextSet()
    ix.application.get_factory().get_root().resolve_all_contexts(contexts)
    with disabled_app():
        resolve(contexts[0])


def resolve(ctx):
    """
    Recursively fix windows paths in xref contexts and discover their children.

    Args:
        ctx (OfContext): parent context.
    """
    level = ctx.get_level()

    if ctx.is_reference():
        attr = ctx.get_attribute("filename")
        convert_windows_path(attr)

    next_level = level + 1
    contexts = ix.api.OfContextSet()
    ctx.resolve_all_contexts(contexts)
    for ctx in [c for c in list(contexts) if c.get_level() == next_level]:
        resolve(ctx)


def convert_windows_paths():
    """
    Fix windows paths in regular path attrs.
    """
    attrs = ix.api.OfAttr.get_path_attrs()
    total = len(list(attrs))
    ix.log_info("Stripping drive letters for {:d} paths".format(total))
    count = 0
    for attr in attrs:
        if convert_windows_path(attr):
            count += 1
    ix.log_info("Done conforming {:d} of {:d} paths".format(count, total))


def convert_windows_path(attr):
    """
    Fix windows paths in one path attribute.

    Args:
        attr (OfAttr): Attribute to modify.

    Returns:
        bool: Whether the attribute was modified
    """
    path = attr.get_string()
    attr_name = attr.get_name()
    item_name = attr.get_parent_object().get_name()

    if path:
        result = re.sub(LETTER_RX, "", path).replace("\\", "/")
        if result == path:
            ix.log_info("Path OK: {}.{} {}".format(item_name, attr_name, path))
        else:
            attr.set_string(result)
            ix.log_info(
                "Conformed: {}.{} {} -> {}".format(item_name, attr_name, path, result)
            )
            return True
    return False


def force_image_ranges(start, end, images):
    """
    Ensure the sequence attributes on image ranges are valid.

    Clarisse doesn't respect frame range overrides, so we make sure the image
    ranges are covered.

    Args:
        start (int): first frame
        end (int): last frame
        images (list): Clarisse paths to all images
    """

    ix.log_info(
        "Ensuring image ranges are on for the sequence {}:{}".format(start, end)
    )
    for image_path in images:
        image = ix.get_item(image_path)
        ix.log_info("Setting range for: {} ".format(image.get_name()))
        image.get_attribute("first_frame").set_long(start)
        image.get_attribute("last_frame").set_long(end)
        image.get_attribute("frame_step").set_long(1)


def ensure_image_directories(images):
    """
    Create directories in preparation for image output.

    Clarisse fails to render if the destination
    directories don't exist.

    Args:
        images (list): Clarisse paths to all images
    """

    ix.log_info("Ensure directories exist for images")
    directories = []
    for image_path in images:
        image = ix.get_item(image_path)
        directory = os.path.dirname(image.get_attribute("save_as").get_string())
        directories.append(directory)
        sys.stdout.write("{} save to disk at: {}\n".format(image_path, directory))
    mkdir_p(directories)


def mkdir_p(dirs):
    """
    Make directories unless they already exist.

    Args:
        dirs (list): directories to create
    """
    for d in dirs:
        sys.stdout.write("Ensure directory: {} exists\n".format(d))
        try:
            os.makedirs(d)
            sys.stdout.write("Successfully made Directory:{}\n".format(d))
        except OSError as ex:
            if ex.errno == errno.EEXIST and os.path.isdir(d):
                sys.stdout.write("Directory exists: {}\n".format(d))
                pass
            else:
                sys.stderr.write(
                    "There's something wrong with the path: ('{}')\n".format(d)
                )
                raise


main()
