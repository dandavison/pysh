import readline
from sys import stdout

from pysh.interpreter import execute


def repl():
    while True:
        display_prompt()
        execute(input())


def display_prompt():
    snake = "🐍"  # U+1F40D
    stdout.write("%s   " % snake)
