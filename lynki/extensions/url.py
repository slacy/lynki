import os
from jinja2 import nodes
from jinja2.ext import Extension
from lynki.extensions.link import LinkExtension


class UrlExtension(LinkExtension):
    """A URL generator"""
    tags = set(['url'])

    def format_result(self, href, page_title):
        return href
