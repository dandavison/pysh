import os

from parsimonious import Grammar
from parsimonious import NodeVisitor


with open(os.path.join(os.path.dirname(__file__), 'grammar')) as fp:
    GRAMMAR = Grammar(fp.read())


def execute(line):
    parse_tree = GRAMMAR.parse(line)
    node_visitor = PyshNodeVisitor()
    node_visitor.visit(parse_tree)
    Pipeline(node_visitor.commands).execute()


class Pipeline:

    def __init__(self, commands):
        self.commands = commands

    def execute(self):

        for command in self.commands:
            fd = self.fork_exec(command)
        for _ in self.commands:
            os.wait()

    def fork_exec(self, command):
        pid = os.fork()

        if pid == 0:
            os.execvp(command, [command])


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
