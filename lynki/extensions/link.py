import os
from jinja2 import nodes
from jinja2.ext import Extension


class LinkExtension(Extension):
    """A link tag for Jinja2"""
    tags = set(['link'])

    def parse(self, parser):
        stream = parser.stream
        tag = stream.next()

        args = [nodes.Const(parser.name),
                nodes.Name('ROOT', 'load'),
                nodes.Name('TEMPLATE', 'load')]
        while not parser.stream.current.test_any('block_end'):
            args.append(parser.parse_expression())

        make_call_node = lambda: self.call_method(
            '_link_support', args=args)

        return nodes.Output([make_call_node()]).set_lineno(tag.lineno)

    def format_result(self, href, page_title):
        return '<a href="%s">%s</a>' % (href, page_title)


    def _link_support(self, this_page, root, this_template, page_title):
        """WAT"""

        if self.environment.pre_process:
            return page_title

        target_filename = None
        for template, meta in self.environment.metamap.iteritems():
            inbound_lower = [s.lower() for s in meta['inbound']]
            if 'inbound' in meta and page_title.lower() in inbound_lower:
                target_filename = template

        if not target_filename:
            raise Exception(
                "Can't find target_filename link for '%s'" % page_title)

        (target_dir, target_file) = os.path.split(target_filename)
        (this_dir, _this_file) = os.path.split(this_template)
        relative_dir = os.path.relpath(target_dir, this_dir)
        relative_filename = os.path.join(relative_dir, target_file)

        # Switch here relative vs. absolute, etc.
        return self.format_result(relative_filename.replace(".jinja2", ".html"),
                                  page_title)
