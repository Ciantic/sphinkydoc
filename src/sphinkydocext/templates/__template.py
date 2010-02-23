import sys

def indent(num, str):
    s = str.split('\n')
    s = [(num * ' ') + line for line in s]
    s = "\n".join(s)
    return s

def pre_template(env):
    env.globals['indent'] = indent