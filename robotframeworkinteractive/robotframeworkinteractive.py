import os
import re

import robot
from robot.libdoc import LibraryDocumentation
from robot.libraries.BuiltIn import BuiltIn

if os.name == 'nt':
    import pyreadline
    readline = pyreadline.Readline()

    def get_input():
        return readline.readline('RF> ')
elif os.name == 'posix':
    import readline

    def get_input():
        rfprint('RF> ')
        return input('RF> ')


COMMANDS = ['Library', 'Resource']


def add_commands(lib_or_res):
    libdoc = LibraryDocumentation(lib_or_res, '', '', None)
    raw_keywords = libdoc.keywords
    for raw_keyword in raw_keywords:
        COMMANDS.append(raw_keyword.name)


def alter_commands(cmd):
    if cmd.lower().startswith('open browser') and 'options=add_experimental_option' not in cmd:
        return f'{cmd}  options=add_experimental_option("excludeSwitches", ["enable-logging"])'

    return cmd


def run_rf(cmd):
    keyword, *args = re.split('\s{2,}',cmd)
    if keyword.lower() == 'library':
        add_commands(args[0])
        return BuiltIn().import_library(args[0])
    elif keyword.lower() == 'resource':
        add_commands(args[0])
        return BuiltIn().import_resource(args[0])
    elif keyword.lower() == 'variables':
        return BuiltIn().import_variables(args[0])
    elif keyword.startswith(('$', '@', '&', '%')):
        value = run_rf('    '.join(args))
        variable = keyword.replace('=', '').strip()
        BuiltIn().set_local_variable(variable, value)
    elif keyword.startswith('#'):
        pass
    elif keyword == '':
        pass
    else:
        return BuiltIn().run_keyword(keyword, *args)


def completer(text, state):
    sects = re.split('\s{2,}', text)
    if len(sects) > 1:
        options = [i for i in BuiltIn().get_variables() if i.startswith(sects[-1])]
    else:
        options = [i for i in COMMANDS if i.startswith(text)]
    if state < len(options):
        sects[-1] = options[state]
        return '    '.join(sects)
    else:
        return None


def rfprint(obj):
    lines = str(obj).splitlines()
    for line in lines:
        line = line.replace(" ", "${SPACE}")
        run_rf(f'Log To Console    {line}')


def run_interactive():
    add_commands("BuiltIn")
    readline.set_completer(completer)
    readline.set_completer_delims('')
    readline.parse_and_bind("tab: complete")

    while True:
        cmd = get_input().strip()

        if cmd == 'exit()':
            return

        try:
            cmd = alter_commands(cmd)
            run_rf(cmd)
        except Exception as e:
            rfprint(str(e))


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.devnull, 'w') as devnull:
        try:
            robot.run(os.path.join(dir_path, "Main.robot"), stdout=devnull, stderr=devnull, log=None, output=None,
                      report=None)
        except Exception as e:
            print(e)
