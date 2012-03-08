"""Lynki is a simple static WIKI generator written in Python"""
import os

from jinja2 import Environment, FileSystemLoader

from lynki.extensions.file import FileExtension
from lynki.extensions.link import LinkExtension
from lynki.extensions.markdown import MarkdownExtension
from lynki.extensions.meta import MetaExtension
from lynki.extensions.url import UrlExtension
from lynki import corpus, engine


def main():
    """main"""
    document_corpus = corpus.find_corpus(os.path.abspath(os.curdir))

    pre = engine.Engine()

    for filename in document_corpus:
        pre.preprocess(filename)

    for filename in document_corpus:
        pre.compile(filename)

if __name__ == '__main__':
    main()
