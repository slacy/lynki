"""yo gabba"""
import os

from jinja2 import Environment, FileSystemLoader

from lynki.extensions import MarkdownExtension, MetaExtension, LinkExtension, FileExtension

# Recursively find all text files
# Process files into lists of words
# Process bigrams and trigram frequency
# Create list of bigrams and trigrams that occur more than once
# filter out bigrams and trigrams that start or end with a stopword
# Create mapping from N-gram to list of documents that contain in
# reprocess all documents, generating links for every N-gram


def find_corpus(root, suffix):
    """find_corpus"""

    def visit(_found, dirname, names):
        """visit"""
        new = [os.path.abspath(os.path.join(dirname, fn))
               for fn in names if (
                fn.endswith(suffix) and not fn.startswith('.'))]
        _found += new

    found_files = []

    os.path.walk(root, visit, found_files)
    return found_files


def find_layout(filepath):
    """find_layout"""
    fullpath = os.path.abspath(filepath)
    while fullpath != '/':
        base = os.path.dirname(fullpath)
        layout = os.path.join(base, '_layout')
        if os.path.exists(layout):
            return layout
        fullpath = base
    return None


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


class Preprocessor(object):
    """Preprocessor"""

    def root(self, filename):
        return find_root(filename)

    def env(self, filename):
        root = self.root(filename)
        if root in self.env_map:
            return self.env_map[root]

        env = Environment(
            loader=FileSystemLoader(root),
            extensions=[MarkdownExtension, MetaExtension, LinkExtension, FileExtension])
        self.env_map[root] = env
        return env

    def __init__(self):
        self.env_map = {}

    def render(self, filename):
        template_relative = filename.replace(self.root(filename), '')
        template = self.env(filename).get_template(template_relative)
        return template.render(ROOT=self.root(filename),
                               TEMPLATE=filename)

    def preprocess(self, filename):
        self.env(filename).pre_process = True
        self.render(filename)

    def compile(self, filename):
        """compile"""
        print "compiling %s" % filename
        out_filename = filename.replace('.jinja2', '.html')
        out_file = open(out_filename, 'w+')
        # html = open(filename, 'r').read()

        self.env(filename).pre_process = False
        final = self.render(filename)
        out_file.write(final)
        out_file.close()


def main():
    """main"""
    corpus = find_corpus(os.curdir, '.jinja2')

    pre = Preprocessor()

    for filename in corpus:
        pre.preprocess(filename)

    for filename in corpus:
        pre.compile(filename)

if __name__ == '__main__':
    main()
