import os
import readline
from sys import stdout

from clint.textui import colored

from pysh.interpreter import execute


def repl():
    while True:
        display_prompt()
        execute(input())


def display_prompt():
    stdout.write("%s %s   " % (
        colored.cyan(os.getcwd(), bold=True),
        "🐍"  # U+1F40D,
    ))
