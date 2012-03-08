"""Utility functions for finding the corpus and root used to render a Lynki
wiki. """
import os


def find_root(filepath):
    """find_root"""
    fullpath = os.path.abspath(filepath)
    while fullpath != '/':
        dirname = os.path.dirname(fullpath)
        root = os.path.join(dirname, '_root')
        if os.path.exists(root):
            return dirname
        fullpath = dirname
    return None


def find_corpus(root):
    """find_corpus"""

    def find_files(starting):
        """Recurse into starting_dir and return a list of files ending
        in .jinja2"""
        contents = os.listdir(starting)
        found_files = []
        for name in contents:
            if name.startswith('.') or name.startswith('_'):
                continue
            elif os.path.isdir(name):
                found_files += find_files(os.path.join(starting, name))
            else:
                if name.endswith(".jinja2"):
                    found_files.append(os.path.join(starting, name))
        return found_files

    found_files = find_files(root)

    return found_files
