from sys import stdout

from pysh.interpreter import execute


def repl():
    while True:
        display_prompt()
        execute(input())


def display_prompt():
    stdout.write("૭ ")
