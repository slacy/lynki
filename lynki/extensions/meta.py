import simplejson
from jinja2 import nodes
from jinja2.ext import Extension


class MetaExtension(Extension):
    """A markdown tag for Jinja2"""
    tags = set(['meta'])

    def __init__(self, environment):
        super(MetaExtension, self).__init__(environment)
        if not hasattr(environment, 'metamap'):
            environment.extend(metamap={})

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(
            ['name:endmeta'],
            drop_needle=True
        )
        args = [nodes.Name('TEMPLATE', 'load')]
        return nodes.CallBlock(
            self.call_method('_meta_support', args),
            [],
            [],
            body
        ).set_lineno(lineno)

    def _meta_support(self, template_name, caller):
        # self.environment.metamap.update()
        python_data = simplejson.loads(caller())
        self.environment.metamap.update({template_name: python_data})
        return "<!-- META:\n%s\n-->\n" % str(python_data)
