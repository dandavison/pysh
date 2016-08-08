import os
import readline
import sys

from clint.textui import colored

from pysh.interpreter import execute


class Pysh:

    def __init__(self):
        self.status = 0

    def run(self):
        while True:
            self.display_prompt()
            self.status = execute(input())

    def display_prompt(self):
        color = colored.red if self.status > 0 else colored.cyan
        sys.stdout.write("%s %s   " % (
            color(os.getcwd(), bold=True),
            "🐍"  # U+1F40D,
        ))


def main():
    try:
        Pysh().run()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
