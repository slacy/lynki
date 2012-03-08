"""The main engine for Lynki.  Finds and renders files."""
from jinja2 import Environment, FileSystemLoader
from lynki import corpus
from lynki.extensions.file import FileExtension
from lynki.extensions.link import LinkExtension
from lynki.extensions.markdown import MarkdownExtension
from lynki.extensions.meta import MetaExtension
from lynki.extensions.url import UrlExtension


class Engine(object):
    """Engine"""

    def root(self, filename):
        """Return the corpus root directory for the given filename."""
        return corpus.find_root(filename)

    def env(self, filename):
        """Return the Jinja2 Environment object that can render the given
        filename"""
        root = self.root(filename)
        if root in self.env_map:
            return self.env_map[root]

        env = Environment(
            loader=FileSystemLoader(root),
            extensions=[MarkdownExtension, MetaExtension,
                        LinkExtension, FileExtension,
                        UrlExtension])
        self.env_map[root] = env
        return env

    def __init__(self):
        self.env_map = {}

    def render(self, filename):
        """Render and save the given filename."""
        template_relative = filename.replace(self.root(filename), '')
        template = self.env(filename).get_template(template_relative)
        return template.render(ROOT=self.root(filename),
                               TEMPLATE=filename)

    def preprocess(self, filename):
        """Preprocess the given filename."""
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
