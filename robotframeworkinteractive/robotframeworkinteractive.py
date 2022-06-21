import os
import re
import sys
import glob

import robot
from robot.libdoc import LibraryDocumentation
from robot.libraries.BuiltIn import BuiltIn


if sys.version_info.major == 3 and sys.version_info.minor > 9:
    import collections
    collections.Callable = collections.abc.Callable


if os.name == 'nt':
    import pyreadline
    readline = pyreadline.Readline()

    def get_input(rfi):
        return readline.readline('RF> ')
elif os.name == 'posix':
    import readline

    def get_input(rfi):
        rfi.rfprint('RF> ')
        return input('RF> ')


WELCOME_MSG = """
Welcome to Robot Framework Interactive
Type any Robot Framework Command to run interactively

Special Commands:
    exit() - Will exit Robot Framework Interactive
    export() - Will export all successful commands since the last export into a robot framework test
    exportall() - Will export all successful commands in this session into a robot framework test
"""


class RobotFrameworkInteractive:
    COMMANDS = ['Library', 'Resource', 'exit()', 'export()', 'exportall()']

    SUCCESS_CMD_HISTORY = []
    SUCCESS_SETTINGS = []

    @staticmethod
    def list_filter_out_values(lst, values):
        result = lst
        for value in values:
            result = list(filter((value).__ne__, result))

        return result

    @staticmethod
    def list_last_index(lst, value):
        if value in lst:
            return len(lst) - lst[::-1].index(value) - 1
        else:
            return -1

    def convert_cmds_to_test(self, cmds):
        settings_str = ''
        test_steps_str = ''

        for setting in self.SUCCESS_SETTINGS:
            settings_str += f'{setting}\n'

        for test_step in cmds:
            test_steps_str += f'{test_step}\n\t'

        return f"""*** Settings ***
{settings_str}


*** Test Cases ***
Export
\t[Documentation]  Test Case exported from Robot Framework Interactive
\t{test_steps_str}
"""

    def export(self, allCmds=False):
        try:
            filename = 'export'
            file_extension = '.robot'
            file = None
            matching_files = glob.glob(f'{filename}*{file_extension}')
            if len(matching_files) == 0:
                file = open(filename + file_extension, 'w')
            else:
                if f'{filename}{file_extension}' in matching_files:
                    matching_files.remove(filename + file_extension)

                if len(matching_files) == 0:
                    file = open(f'{filename}_1{file_extension}', 'w')
                else:
                    file_numbers = [int(re.match(r'export_(\d+)\.robot', i).group(1)) for i in matching_files]
                    file = open(f'{filename}_{max(file_numbers) + 1}{file_extension}', 'w')

            if allCmds:
                cmds = self.list_filter_out_values(self.SUCCESS_CMD_HISTORY, ['export()', 'exportall()'])
            else:
                export_idx = self.list_last_index(self.SUCCESS_CMD_HISTORY, 'export()')
                exportall_idx = self.list_last_index(self.SUCCESS_CMD_HISTORY, 'exportall()')
                idx = max(export_idx, exportall_idx)
                cmds = self.SUCCESS_CMD_HISTORY[idx+1:]

            file.write(self.convert_cmds_to_test(cmds))
            self.rfprint(f'Successful commands written to {file.name}')
            file.close()
        except Exception as e:
            self.rfprint(e)

    def add_commands(self, lib_or_res):
        libdoc = LibraryDocumentation(lib_or_res, '', '', None)
        raw_keywords = libdoc.keywords
        for raw_keyword in raw_keywords:
            self.COMMANDS.append(raw_keyword.name)

    @staticmethod
    def alter_commands(cmd):
        if cmd.lower().startswith('open browser') and 'options=add_experimental_option' not in cmd:
            return f'{cmd}  options=add_experimental_option("excludeSwitches", ["enable-logging"])'

        return cmd

    def run_rf(self, cmd, log=True, throw=False):
        try:
            original_cmd = cmd
            is_setting = False
            result = None
            keyword, *args = re.split(r'\s{2,}', cmd)
            if keyword.lower() == 'library':
                is_setting = True
                self.add_commands(args[0])
                result = BuiltIn().import_library(args[0])
            elif keyword.lower() == 'resource':
                is_setting = True
                self.add_commands(args[0])
                result = BuiltIn().import_resource(args[0])
            elif keyword.lower() == 'variables':
                is_setting = True
                result = BuiltIn().import_variables(args[0])
            elif keyword.startswith(('$', '@', '&', '%')):
                variable = keyword.replace('=', '').strip()
                if args[0] in ['Create List', 'Create Dictionary', 'Set Variable']:
                    result = BuiltIn().set_local_variable(variable, *args[1:])
                else:
                    value = self.run_rf('    '.join(args), log=False, throw=True)
                    result = BuiltIn().set_local_variable(variable, value)
            elif keyword.startswith('#'):
                pass
            elif keyword == '':
                pass
            else:
                result = BuiltIn().run_keyword(keyword, *args)

            if log:
                if is_setting:
                    self.SUCCESS_SETTINGS.append(original_cmd)
                else:
                    self.SUCCESS_CMD_HISTORY.append(original_cmd)

            return result
        except Exception as e:
            if throw:
                raise e
            else:
                self.rfprint(e)

    def completer(self, text, state):
        sects = re.split(r'\s{2,}', text)
        if len(sects) > 1:
            if (sects[0].startswith('$') or sects[0].startswith('&') or sects[0].startswith('@')) and (len(sects) <= 2):
                options = [i for i in self.COMMANDS if i.startswith(sects[-1])]
            else:
                options = [i for i in BuiltIn().get_variables() if i.startswith(sects[-1])]
        else:
            options = [i for i in self.COMMANDS if i.startswith(text)]
        if state < len(options):
            sects[-1] = options[state]
            return '    '.join(sects)
        else:
            return None

    def rfprint(self, obj):
        lines = str(obj).splitlines()
        for line in lines:
            line = re.sub(r'([$@&%\[\]])', r'\\\1', line)
            line = line.replace(" ", "${SPACE}")
            self.run_rf(f'Log To Console    {line}', log=False)


def run_interactive():
    rfi = RobotFrameworkInteractive()
    rfi.add_commands("BuiltIn")
    readline.set_completer(rfi.completer)
    readline.set_completer_delims('')
    readline.parse_and_bind("tab: complete")

    while True:
        cmd = get_input(rfi).strip()

        if cmd == 'exit()':
            return

        if cmd == 'export()':
            rfi.export()
            rfi.SUCCESS_CMD_HISTORY.append(cmd)
            continue

        if cmd == 'exportall()':
            rfi.export(allCmds=True)
            rfi.SUCCESS_CMD_HISTORY.append(cmd)
            continue

        try:
            cmd = rfi.alter_commands(cmd)
            rfi.run_rf(cmd)
        except Exception as e:
            rfi.rfprint(str(e))


def main():
    print(WELCOME_MSG)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.devnull, 'w') as devnull:
        try:
            robot.run(os.path.join(dir_path, "Main.robot"), stdout=devnull, stderr=devnull, log=None, output=None,
                      report=None)
        except Exception as e:
            print(e)
