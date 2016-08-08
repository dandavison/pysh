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
    Pipeline(node_visitor.pipeline, node_visitor.output_file).execute()


class Pipeline:

    def __init__(self, commands, output_file):
        self.commands = commands
        self.output_file = output_file

    def execute(self):
        if self.output_file:
            with open(self.output_file, 'w') as fp:
                os.dup2(fp.fileno(), sys.stdout.fileno())

        in_pipe = (sys.stdout.fileno(), None)
        self._execute(self.commands, in_pipe)
        for _ in self.commands:
            pid, status = os.wait()
            status >>=8
            if status != 0:
                sys.exit(status)

    def _execute(self, commands, in_pipe):
        """
        Fork and exec first command passing output to the rest of the pipeline.
        """
        if not commands:
            return
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

            try:
                os.execvp(command[0], command)
            except OSError as exc:
                sys.stderr.write('%s: %s\n' % (command[0], exc))
                sys.exit(exc.errno)
        else:
            if out_pipe:
                os.close(out_pipe[WRITE])
            self._execute(remaining_commands, out_pipe)


class PyshNodeVisitor(NodeVisitor):

    def __init__(self):
        super().__init__()
        self.pipeline = []
        self.current_command = []
        self.output_file = None

    def visit_command(self, node, children):
        self.pipeline.append(self.current_command)
        self.current_command = []

    def visit_word(self, node, children):
        self.current_command.append(node.text)

    def visit_output_file_path(self, node, children):
        self.output_file = node.text

    def generic_visit(self, node, children=None):
        pass


if __name__ == '__main__':
    [line] = sys.argv[1:]
    execute(line)
