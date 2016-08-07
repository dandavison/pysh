import os
import sys

from parsimonious import Grammar
from parsimonious import NodeVisitor


READ, WRITE = 0, 1

with open(os.path.join(os.path.dirname(__file__), 'grammar')) as fp:
    GRAMMAR = Grammar(fp.read())


def execute(line):
    parse_tree = GRAMMAR.parse(line)
    node_visitor = PyshNodeVisitor()
    node_visitor.visit(parse_tree)
    Pipeline(node_visitor.pipeline).execute()


class Pipeline:

    def __init__(self, commands):
        self.commands = commands

    def execute(self):
        in_pipe = (sys.stdout.fileno(), None)
        self._execute(self.commands, in_pipe)
        for _ in self.commands:
            os.wait()

    def _execute(self, commands, in_pipe):
        """
        Fork and exec first command passing output to the rest of the pipeline.
        """
        command, *remaining_commands = commands
        is_first = not in_pipe[WRITE]
        is_last = not remaining_commands
        out_pipe = os.pipe() if not is_last else None

        in_child = os.fork() == 0

        if in_child:
            if not is_first:
                os.dup2(in_pipe[READ], sys.stdin.fileno())
            if not is_last:
                os.dup2(out_pipe[WRITE], sys.stdout.fileno())
                os.close(out_pipe[READ])

            # TODO: Commands with multiple words
            command = [command]
            # TODO: Handle OSError?
            os.execvp(command[0], command)
        else:
            if out_pipe:
                os.close(out_pipe[WRITE])
            if remaining_commands:
                self._execute(remaining_commands, out_pipe)


class PyshNodeVisitor(NodeVisitor):

    def __init__(self):
        super().__init__()
        self.pipeline = []

    def visit_pipeline(self, node, children):
        pass

    def visit_command(self, node, children):
        self.pipeline.append(node.text)

    def generic_visit(self, node, children=None):
        pass


if __name__ == '__main__':
    [line] = sys.argv[1:]
    execute(line)
