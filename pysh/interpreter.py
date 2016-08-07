import os
import sys

from parsimonious import Grammar
from parsimonious import NodeVisitor


READ_END, WRITE_END = 0, 1

with open(os.path.join(os.path.dirname(__file__), 'grammar')) as fp:
    GRAMMAR = Grammar(fp.read())


def execute(line):
    parse_tree = GRAMMAR.parse(line)
    node_visitor = PyshNodeVisitor()
    node_visitor.visit(parse_tree)
    Pipeline(node_visitor.commands).execute_recursive()


class Pipeline:

    def __init__(self, commands):
        self.commands = commands

    def execute_recursive(self):
        in_pipe = (sys.stdout.fileno(), None)
        self._execute_recursive(self.commands, in_pipe)
        for _ in self.commands:
            os.wait()

    def _execute_recursive(self, commands, in_pipe):
        """
        Fork and exec the first command, passing output on to the rest of the pipeline.
        """
        command, *remaining_commands = commands
        is_first = not in_pipe[WRITE_END]
        is_last = not remaining_commands
        out_pipe = os.pipe() if not is_last else None

        in_child = os.fork() == 0

        if in_child:
            if not is_first:
                os.dup2(in_pipe[READ_END], sys.stdin.fileno())
                # os.close(in_pipe[WRITE_END])
            if not is_last:
                os.dup2(out_pipe[WRITE_END], sys.stdout.fileno())
                os.close(out_pipe[READ_END])

            # TODO: Commands with multiple words
            command = [command]
            # TODO: Handle OSError?
            os.execvp(command[0], command)
        else:
            if out_pipe:
                os.close(out_pipe[WRITE_END])
            if remaining_commands:
                self._execute_recursive(remaining_commands, out_pipe)

    def execute(self):

        redirect = False
        if redirect:
            with open(redirect_file, 'w') as fp:
                os.dup2(fp.fileno(), sys.stdout.fileno())

        pipe = sys.stdin.fileno(), None
        for i in range(len(self.commands)):
            pipe = self.fork_exec(i, pipe)
        for _ in self.commands:
            os.wait()

    def fork_exec(self, i, in_pipe):
        is_first = i == 0
        is_last = i == len(self.commands) - 1
        out_pipe = os.pipe() if not is_last else None

        log('fork_exec(i=%d, in_pipe=%r, commands=%r)' % (i, in_pipe, self.commands))
        log('is_first=%s, is_last=%s, out_pipe=%r' % (is_first, is_last, out_pipe))

        in_child = os.fork() == 0

        if not in_child:
            if not is_last:
                os.close(out_pipe[WRITE_END])
            return out_pipe

        # If this is the first command, the read end is already set to stdin,
        # and there is no write end.
        if not is_first:
            # Take our input from the read end of the pipe to our left and
            # close our copy of its write end.
            os.dup2(in_pipe[READ_END], sys.stdin.fileno())
            os.close(in_pipe[WRITE_END])

        # If this is the last command, leave our output going to stdout.
        if not is_last:
            # Create a pipe and send our output to it. Close our copy of its
            # read end.
            os.dup2(out_pipe[WRITE_END], sys.stdout.fileno())
            os.close(out_pipe[READ_END])

        # TODO: commands with multiple words
        command = [self.commands[i]]
        try:
            os.execvp(command[0], command)
        except OSError as exc:
            import ipdb ; ipdb.set_trace()
            sys.exit(1)


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
    [line] = sys.argv[1:]
    execute(line)
