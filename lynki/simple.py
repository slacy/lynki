"""yo gabba"""
import os

from jinja2 import Environment, FileSystemLoader

from lynki.extensions.file import FileExtension
from lynki.extensions.link import LinkExtension
from lynki.extensions.markdown import MarkdownExtension
from lynki.extensions.meta import  MetaExtension


# Recursively find all text files
# Process files into lists of words
# Process bigrams and trigram frequency
# Create list of bigrams and trigrams that occur more than once
# filter out bigrams and trigrams that start or end with a stopword
# Create mapping from N-gram to list of documents that contain in
# reprocess all documents, generating links for every N-gram


def find_corpus(root):
    """find_corpus"""

    def find_files(starting):
        """Recurse into starting_dir and return a list of files ending in .jinja2"""
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
    corpus = find_corpus(os.path.abspath(os.curdir))

    pre = Preprocessor()

    for filename in corpus:
        pre.preprocess(filename)

    for filename in corpus:
        pre.compile(filename)

if __name__ == '__main__':
    main()
