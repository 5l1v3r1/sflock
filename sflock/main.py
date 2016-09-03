# Copyright (C) 2015-2016 Jurriaan Bremer.
# This file is part of SFlock - http://www.sflock.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import click
import glob
import os.path

from sflock.abstracts import File
from sflock.pick import picker
from sflock.unpack import plugins

def supported():
    """Returns the supported unpackers for this machine."""

def unpack(filepath, contents=None):
    """Unpacks the file or contents provided."""
    if contents:
        f = File(filepath, contents)
    else:
        f = File.from_path(filepath)

    # Determine how we're going to unpack this file (if at all). It may not
    # have a file extension, e.g., when its filename is a hash. In those cases
    # we're going to take a look at the contents of the file.
    unpacker = picker(filepath)
    if not unpacker and f.get_signature():
        unpacker = f.get_signature()["unpacker"]

    # Actually unpack any embedded files in this archive.
    if unpacker:
        f.children = plugins[unpacker](f).unpack()
    return f

def process_file(filepath):
    f = unpack(filepath)
    for entry in f.children:
        print entry.to_dict()

def process_directory(dirpath):
    for rootpath, directories, filenames in os.walk(dirpath):
        for filename in filenames:
            process_file(os.path.join(rootpath, filename))

@click.command()
@click.argument("files", nargs=-1)
def main(files):
    for pattern in files:
        for path in glob.iglob(pattern):
            if os.path.isdir(path):
                process_directory(path)
            else:
                process_file(path)