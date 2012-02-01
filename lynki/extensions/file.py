import os
from jinja2 import nodes
from jinja2.ext import Extension


class FileExtension(Extension):
    """Take a path relative to ROOT and output a path relative to the current page being
    rendered. """
    tags = set(['file'])

    def parse(self, parser):
        stream = parser.stream
        tag = stream.next()

        args = [nodes.Const(parser.name),
                nodes.Name('ROOT', 'load'),
                nodes.Name('TEMPLATE', 'load')]
        while not parser.stream.current.test_any('block_end'):
            args.append(parser.parse_expression())

        make_call_node = lambda: self.call_method(
            '_file_support', args=args)

        return nodes.Output([make_call_node()]).set_lineno(tag.lineno)

    def _file_support(self, this_page, root, this_template, target_path):
        """WAT"""
        if self.environment.pre_process:
            return target_path

        target_full = os.path.join(root, target_path.strip('/'))
        (target_dir, target_file) = os.path.split(target_full)
        (this_dir, this_file) = os.path.split(this_template)

        relative_dir = os.path.relpath(target_dir, this_dir)
        relative_filename = os.path.join(relative_dir, target_file)

        # Add a switch here based on global configs for absolute vs. relative paths
        return relative_filename
