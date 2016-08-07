import os

from parsimonious import Grammar
from parsimonious import NodeVisitor


with open(os.path.join(os.path.dirname(__file__), 'grammar')) as fp:
    GRAMMAR = Grammar(fp.read())


def execute(line):
    parse_tree = GRAMMAR.parse(line)
    node_visitor = PyshNodeVisitor()
    node_visitor.visit(parse_tree)
    execute_pipeline(node_visitor.commands)


def execute_pipeline(commands):
    assert len(commands) == 1
    [command] = commands

    pid = os.fork()

    if pid == 0:
        os.execvp(command, [command])

    os.wait()


class PyshNodeVisitor(NodeVisitor):

    def __init__(self):
        super().__init__()
        self.commands = []

    def visit_commands(self, node, children):
        pass

    def visit_command(self, node, children):
        self.commands.append(node.text)

    def generic_visit(self, node, children=None):
        pass


if __name__ == '__main__':
    import sys
    [line] = sys.argv[1:]
    execute(line)
