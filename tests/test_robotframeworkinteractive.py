import unittest
from unittest.mock import MagicMock, mock_open, patch, PropertyMock

from robotframeworkinteractive.robotframeworkinteractive import os, glob, RobotFrameworkInteractive, main, \
    run_interactive, WELCOME_MSG

EXCEPTION = Exception('Test')


def raise_exception(*args, **kwargs):
    raise EXCEPTION


class RobotFrameworkInteractiveTests(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.rfi = RobotFrameworkInteractive()

    def test_list_filter_out_values_no_values(self):
        lst = ['a', 'b', 'c']
        result = self.rfi.list_filter_out_values(lst, [])
        self.assertEqual(['a', 'b', 'c'], result)

    def test_list_filter_out_values_one_value(self):
        lst = ['a', 'b', 'c']
        result = self.rfi.list_filter_out_values(lst, ['b'])
        self.assertEqual(['a', 'c'], result)

    def test_list_filter_out_values_multiple_values(self):
        lst = ['a', 'b', 'c']
        result = self.rfi.list_filter_out_values(lst, ['b', 'c'])
        self.assertEqual(['a'], result)

    def test_list_filter_out_values_value_not_exists(self):
        lst = ['a', 'b', 'c']
        result = self.rfi.list_filter_out_values(lst, ['d'])
        self.assertEqual(['a', 'b', 'c'], result)

    def test_list_filter_out_values_empty_list(self):
        lst = []
        result = self.rfi.list_filter_out_values(lst, ['d'])
        self.assertEqual([], result)

    def test_list_last_index_last_value(self):
        lst = ['a', 'b', 'c']
        result = self.rfi.list_last_index(lst, 'c')
        self.assertEqual(2, result)

    def test_list_last_index_first_value(self):
        lst = ['a', 'b', 'c']
        result = self.rfi.list_last_index(lst, 'a')
        self.assertEqual(0, result)

    def test_list_last_index_no_value(self):
        lst = ['a', 'b', 'c']
        result = self.rfi.list_last_index(lst, 'd')
        self.assertEqual(-1, result)

    def test_list_last_index_duplicate_value(self):
        lst = ['a', 'b', 'c', 'c', 'b', 'a']
        result = self.rfi.list_last_index(lst, 'b')
        self.assertEqual(4, result)

    def test_convert_cmds_to_test_no_settings_no_cmds(self):
        cmds = []
        result = self.rfi.convert_cmds_to_test(cmds)
        self.assertEqual("""*** Settings ***



*** Test Cases ***
Export
\t[Documentation]  Test Case exported from Robot Framework Interactive
\t
""", result)

    def test_convert_cmds_to_test_only_settings(self):
        cmds = []
        self.rfi.SUCCESS_SETTINGS = ['Library  SeleniumLibrary']
        result = self.rfi.convert_cmds_to_test(cmds)
        self.assertEqual("""*** Settings ***
Library  SeleniumLibrary



*** Test Cases ***
Export
\t[Documentation]  Test Case exported from Robot Framework Interactive
\t
""", result)

    def test_convert_cmds_to_test_only_cmds(self):
        cmds = ['Log To Console  Test']
        result = self.rfi.convert_cmds_to_test(cmds)
        self.assertEqual("""*** Settings ***



*** Test Cases ***
Export
\t[Documentation]  Test Case exported from Robot Framework Interactive
\tLog To Console  Test
\t
""", result)

    def test_convert_cmds_to_test_settings_and_commands(self):
        cmds = ['Log To Console  Test']
        self.rfi.SUCCESS_SETTINGS = ['Library  SeleniumLibrary']
        result = self.rfi.convert_cmds_to_test(cmds)
        self.assertEqual("""*** Settings ***
Library  SeleniumLibrary



*** Test Cases ***
Export
\t[Documentation]  Test Case exported from Robot Framework Interactive
\tLog To Console  Test
\t
""", result)

    def test_convert_cmds_to_test_multiple_settings_and_commands(self):
        cmds = ['Open Browser  https://www.google.com  chrome', 'Close Browser']
        self.rfi.SUCCESS_SETTINGS = ['Library  SeleniumLibrary']
        result = self.rfi.convert_cmds_to_test(cmds)
        self.assertEqual("""*** Settings ***
Library  SeleniumLibrary



*** Test Cases ***
Export
\t[Documentation]  Test Case exported from Robot Framework Interactive
\tOpen Browser  https://www.google.com  chrome
\tClose Browser
\t
""", result)

    @patch('builtins.open', new_callable=mock_open, read_data='1')
    def test_export_first_export(self, m_open):
        glob.glob = MagicMock(return_value=[])
        self.rfi.rfprint = MagicMock()
        self.rfi.export()
        m_open.assert_called_once_with('export.robot', 'w')

    @patch('builtins.open', new_callable=mock_open, read_data='1')
    def test_export_with_export(self, m_open):
        glob.glob = MagicMock(return_value=['export.robot'])
        self.rfi.rfprint = MagicMock()
        self.rfi.export()
        m_open.assert_called_once_with('export_1.robot', 'w')

    @patch('builtins.open', new_callable=mock_open, read_data='1')
    def test_export_with_export_and_export_1(self, m_open):
        glob.glob = MagicMock(return_value=['export.robot', 'export_1.robot'])
        self.rfi.rfprint = MagicMock()
        self.rfi.export()
        m_open.assert_called_once_with('export_2.robot', 'w')

    @patch('builtins.open', new_callable=mock_open, read_data='1')
    def test_export_with_export_1(self, m_open):
        glob.glob = MagicMock(return_value=['export_1.robot'])
        self.rfi.rfprint = MagicMock()
        self.rfi.export()
        m_open.assert_called_once_with('export_2.robot', 'w')

    @patch('builtins.open', new_callable=mock_open, read_data='1')
    def test_export_all_commands(self, m_open):
        glob.glob = MagicMock(return_value=[])
        self.rfi.rfprint = MagicMock()
        self.rfi.list_filter_out_values = MagicMock(return_value=[])
        self.rfi.list_last_index = MagicMock(return_value=-1)
        self.rfi.export(allCmds=True)
        self.rfi.list_filter_out_values.assert_called_once_with(self.rfi.SUCCESS_CMD_HISTORY, ['export()', 'exportall()'])
        self.rfi.list_last_index.assert_not_called()

    @patch('builtins.open', new_callable=mock_open, read_data='1')
    def test_export_latest_commands(self, m_open):
        glob.glob = MagicMock(return_value=[])
        self.rfi.rfprint = MagicMock()
        self.rfi.list_filter_out_values = MagicMock(return_value=[])
        self.rfi.list_last_index = MagicMock(return_value=-1)
        self.rfi.export(allCmds=False)
        self.rfi.list_filter_out_values.assert_not_called()
        self.assertEqual(2, self.rfi.list_last_index.call_count)
        self.assertEqual('export()', self.rfi.list_last_index.call_args_list[0].args[1])
        self.assertEqual('exportall()', self.rfi.list_last_index.call_args_list[1].args[1])

    def test_add_commands(self):
        self.rfi.COMMANDS = []
        self.rfi.add_commands('BuiltIn')
        self.assertTrue('Log To Console' in self.rfi.COMMANDS)

    def test_alter_commands_open_browser(self):
        result = self.rfi.alter_commands('Open Browser  https://www.google.com  chrome')
        self.assertEqual('Open Browser  https://www.google.com  chrome  '
                         'options=add_experimental_option("excludeSwitches", ["enable-logging"])', result)

    def test_alter_commands_other(self):
        result = self.rfi.alter_commands('Log To Console  Test')
        self.assertEqual('Log To Console  Test', result)

    def test_run_rf_library(self):
        self.rfi.add_commands = MagicMock()
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).import_library = MagicMock(return_value='good')
            type(patched_builtin.return_value).import_resource = MagicMock(return_value='bad')
            type(patched_builtin.return_value).import_variables = MagicMock(return_value='bad')
            type(patched_builtin.return_value).set_local_variable = MagicMock(return_value='bad')
            type(patched_builtin.return_value).run_keyword = MagicMock(return_value='bad')
            result = self.rfi.run_rf('Library  SeleniumLibrary')
            type(patched_builtin.return_value).import_library.assert_called_once_with('SeleniumLibrary')
            type(patched_builtin.return_value).import_resource.assert_not_called()
            type(patched_builtin.return_value).import_variables.assert_not_called()
            type(patched_builtin.return_value).set_local_variable.assert_not_called()
            type(patched_builtin.return_value).run_keyword.assert_not_called()
            self.assertEqual('good', result)

    def test_run_rf_resource(self):
        self.rfi.add_commands = MagicMock()
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).import_library = MagicMock(return_value='bad')
            type(patched_builtin.return_value).import_resource = MagicMock(return_value='good')
            type(patched_builtin.return_value).import_variables = MagicMock(return_value='bad')
            type(patched_builtin.return_value).set_local_variable = MagicMock(return_value='bad')
            type(patched_builtin.return_value).run_keyword = MagicMock(return_value='bad')
            result = self.rfi.run_rf('Resource  Test.robot')
            type(patched_builtin.return_value).import_library.assert_not_called()
            type(patched_builtin.return_value).import_resource.assert_called_once_with('Test.robot')
            type(patched_builtin.return_value).import_variables.assert_not_called()
            type(patched_builtin.return_value).set_local_variable.assert_not_called()
            type(patched_builtin.return_value).run_keyword.assert_not_called()
            self.assertEqual('good', result)

    def test_run_rf_variables(self):
        self.rfi.add_commands = MagicMock()
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).import_library = MagicMock(return_value='bad')
            type(patched_builtin.return_value).import_resource = MagicMock(return_value='bad')
            type(patched_builtin.return_value).import_variables = MagicMock(return_value='good')
            type(patched_builtin.return_value).set_local_variable = MagicMock(return_value='bad')
            type(patched_builtin.return_value).run_keyword = MagicMock(return_value='bad')
            result = self.rfi.run_rf('Variables  Vars.robot')
            type(patched_builtin.return_value).import_library.assert_not_called()
            type(patched_builtin.return_value).import_resource.assert_not_called()
            type(patched_builtin.return_value).import_variables.assert_called_once_with('Vars.robot')
            type(patched_builtin.return_value).set_local_variable.assert_not_called()
            type(patched_builtin.return_value).run_keyword.assert_not_called()
            self.assertEqual('good', result)

    def test_run_rf_specialcharacter_normal(self):
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).import_library = MagicMock(return_value='bad')
            type(patched_builtin.return_value).import_resource = MagicMock(return_value='bad')
            type(patched_builtin.return_value).import_variables = MagicMock(return_value='bad')
            type(patched_builtin.return_value).set_local_variable = MagicMock(return_value='good')
            type(patched_builtin.return_value).run_keyword = MagicMock(return_value='bad')
            result = self.rfi.run_rf('&{TEST}=  Create Dictionary  foo=bar')
            type(patched_builtin.return_value).import_library.assert_not_called()
            type(patched_builtin.return_value).import_resource.assert_not_called()
            type(patched_builtin.return_value).import_variables.assert_not_called()
            type(patched_builtin.return_value).set_local_variable.assert_called_once_with('&{TEST}', 'foo=bar')
            type(patched_builtin.return_value).run_keyword.assert_not_called()
            self.assertEqual('good', result)

    def test_run_rf_specialcharacter_keyword(self):
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).import_library = MagicMock(return_value='bad')
            type(patched_builtin.return_value).import_resource = MagicMock(return_value='bad')
            type(patched_builtin.return_value).import_variables = MagicMock(return_value='bad')
            type(patched_builtin.return_value).set_local_variable = MagicMock(return_value='good')
            type(patched_builtin.return_value).run_keyword = MagicMock(return_value='bad')
            result = self.rfi.run_rf('${TEST}=  Get On Session  beeceptor  /ready')
            type(patched_builtin.return_value).import_library.assert_not_called()
            type(patched_builtin.return_value).import_resource.assert_not_called()
            type(patched_builtin.return_value).import_variables.assert_not_called()
            type(patched_builtin.return_value).set_local_variable.assert_called_once_with('${TEST}', 'bad')
            type(patched_builtin.return_value).run_keyword.assert_any_call('Get On Session', 'beeceptor', '/ready')
            type(patched_builtin.return_value).run_keyword.assert_called_with('Log To Console', 'bad')
            self.assertEqual('good', result)

    def test_run_rf_comment(self):
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).import_library = MagicMock(return_value='bad')
            type(patched_builtin.return_value).import_resource = MagicMock(return_value='bad')
            type(patched_builtin.return_value).import_variables = MagicMock(return_value='bad')
            type(patched_builtin.return_value).set_local_variable = MagicMock(return_value='bad')
            type(patched_builtin.return_value).run_keyword = MagicMock(return_value='bad')
            result = self.rfi.run_rf('# Test Comment')
            type(patched_builtin.return_value).import_library.assert_not_called()
            type(patched_builtin.return_value).import_resource.assert_not_called()
            type(patched_builtin.return_value).import_variables.assert_not_called()
            type(patched_builtin.return_value).set_local_variable.assert_not_called()
            type(patched_builtin.return_value).run_keyword.assert_not_called()
            self.assertEqual(None, result)

    def test_run_rf_empty(self):
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).import_library = MagicMock(return_value='bad')
            type(patched_builtin.return_value).import_resource = MagicMock(return_value='bad')
            type(patched_builtin.return_value).import_variables = MagicMock(return_value='bad')
            type(patched_builtin.return_value).set_local_variable = MagicMock(return_value='bad')
            type(patched_builtin.return_value).run_keyword = MagicMock(return_value='bad')
            result = self.rfi.run_rf('')
            type(patched_builtin.return_value).import_library.assert_not_called()
            type(patched_builtin.return_value).import_resource.assert_not_called()
            type(patched_builtin.return_value).import_variables.assert_not_called()
            type(patched_builtin.return_value).set_local_variable.assert_not_called()
            type(patched_builtin.return_value).run_keyword.assert_not_called()
            self.assertEqual(None, result)

    def test_run_rf_keyword(self):
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).import_library = MagicMock(return_value='bad')
            type(patched_builtin.return_value).import_resource = MagicMock(return_value='bad')
            type(patched_builtin.return_value).import_variables = MagicMock(return_value='bad')
            type(patched_builtin.return_value).set_local_variable = MagicMock(return_value='bad')
            type(patched_builtin.return_value).run_keyword = MagicMock(return_value='good')
            result = self.rfi.run_rf('Log To Console  Test')
            type(patched_builtin.return_value).import_library.assert_not_called()
            type(patched_builtin.return_value).import_resource.assert_not_called()
            type(patched_builtin.return_value).import_variables.assert_not_called()
            type(patched_builtin.return_value).set_local_variable.assert_not_called()
            type(patched_builtin.return_value).run_keyword.assert_called_once_with('Log To Console', 'Test')
            self.assertEqual('good', result)

    def test_run_rf_log_setting(self):
        self.rfi.add_commands = MagicMock()
        self.rfi.SUCCESS_SETTINGS = []
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).import_library = MagicMock(return_value='good')
            result = self.rfi.run_rf('Library  SeleniumLibrary')
            self.assertEqual('good', result)
            self.assertEqual(['Library  SeleniumLibrary'], self.rfi.SUCCESS_SETTINGS)

    def test_run_rf_log_cmd(self):
        self.rfi.SUCCESS_CMD_HISTORY = []
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).run_keyword = MagicMock(return_value='good')
            result = self.rfi.run_rf('Log To Console  Test')
            self.assertEqual('good', result)
            self.assertEqual(['Log To Console  Test'], self.rfi.SUCCESS_CMD_HISTORY)

    def test_run_rf_no_log(self):
        self.rfi.SUCCESS_CMD_HISTORY = []
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).run_keyword = MagicMock(return_value='good')
            result = self.rfi.run_rf('Log To Console  Test', log=False)
            self.assertEqual('good', result)
            self.assertEqual([], self.rfi.SUCCESS_CMD_HISTORY)

    def test_run_rf_exception_throw(self):
        self.rfi.rfprint = MagicMock()
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).run_keyword = MagicMock(side_effect=raise_exception)
            result = self.rfi.run_rf('Log To Console  Test')
            self.assertEqual(None, result)
            self.rfi.rfprint.assert_called_once_with(EXCEPTION)

    def test_run_rf_exception_no_throw(self):
        self.rfi.rfprint = MagicMock()
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).run_keyword = MagicMock(side_effect=raise_exception)
            with self.assertRaises(Exception):
                self.rfi.run_rf('Log To Console  Test', throw=True)
            self.rfi.rfprint.assert_not_called()

    def test_completer_variables_one_match(self):
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).get_variables = MagicMock(return_value=['${TEST_NAME}'])
            result = self.rfi.completer('Log To Console  ${TEST_', 0)
            self.assertEqual('Log To Console    ${TEST_NAME}', result)

    def test_completer_variables_many_matches(self):
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).get_variables = MagicMock(return_value=['${TEST_NAME}', '${TEST_VALUE}'])
            result1 = self.rfi.completer('Log To Console  ${TEST_', 0)
            result2 = self.rfi.completer('Log To Console  ${TEST_', 1)
            self.assertEqual('Log To Console    ${TEST_NAME}', result1)
            self.assertEqual('Log To Console    ${TEST_VALUE}', result2)

    def test_completer_variables_no_match(self):
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).get_variables = MagicMock(return_value=['${TEST_NAME}'])
            result = self.rfi.completer('Log To Console  ${COW', 0)
            self.assertEqual(None, result)

    def test_completer_commands_one_match(self):
        self.rfi.COMMANDS = ['Log To Console', 'Log']
        result = self.rfi.completer('Log To C', 0)
        self.assertEqual('Log To Console', result)

    def test_completer_commands_many_matches(self):
        self.rfi.COMMANDS = ['Log To Console', 'Log']
        result1 = self.rfi.completer('L', 0)
        result2 = self.rfi.completer('L', 1)
        self.assertEqual('Log To Console', result1)
        self.assertEqual('Log', result2)

    def test_completer_commands_no_match(self):
        self.rfi.COMMANDS = ['Log To Console', 'Log']
        result = self.rfi.completer('C', 0)
        self.assertEqual(None, result)

    def test_completer_command_after_variable(self):
        self.rfi.COMMANDS = ['Set Variable']
        result = self.rfi.completer('${TEST}=  Set V', 0)
        self.assertEqual('${TEST}=    Set Variable', result)

    def test_completer_no_command_after_command_after_variable(self):
        with patch('robotframeworkinteractive.robotframeworkinteractive.BuiltIn') as patched_builtin:
            type(patched_builtin.return_value).get_variables = MagicMock(return_value=['${TEST_NAME}'])
            self.rfi.COMMANDS = ['Set Variable']
            result = self.rfi.completer('${TEST}=  Set Variable  ', 0)
            self.assertEqual('${TEST}=    Set Variable    ${TEST_NAME}', result)

    def test_rfprint_empty(self):
        self.rfi.run_rf = MagicMock()
        self.rfi.rfprint('')
        self.rfi.run_rf.assert_not_called()

    def test_rfprint_single_line_space(self):
        self.rfi.run_rf = MagicMock()
        self.rfi.rfprint('This is a test')
        self.rfi.run_rf.assert_called_once_with('Log To Console    This${SPACE}is${SPACE}a${SPACE}test', log=False)

    def test_rfprint_multi_line_escapes(self):
        self.rfi.run_rf = MagicMock()
        self.rfi.rfprint('${STRING}\n@{LIST}\n&{DICT}\n%{ENV}\n[]')
        self.assertEqual(5, self.rfi.run_rf.call_count)
        self.assertEqual('Log To Console    \\${STRING}', self.rfi.run_rf.call_args_list[0].args[0])
        self.assertEqual('Log To Console    \\@{LIST}', self.rfi.run_rf.call_args_list[1].args[0])
        self.assertEqual('Log To Console    \\&{DICT}', self.rfi.run_rf.call_args_list[2].args[0])
        self.assertEqual('Log To Console    \\%{ENV}', self.rfi.run_rf.call_args_list[3].args[0])
        self.assertEqual('Log To Console    \\[\\]', self.rfi.run_rf.call_args_list[4].args[0])


class RunInteractiveTests(unittest.TestCase):
    def setUp(self):
        self.counter = 0

    def test_run_interactive_cmd_exit(self):
        def internal_get_input(*args, **kwargs):
            inputs = ['Log To Console  Test', 'exit()']
            result = inputs[self.counter]
            self.counter += 1
            return result

        def passthrough_alter_commands(cmd):
            return cmd

        with patch('robotframeworkinteractive.robotframeworkinteractive.get_input') as patched_get_input:
            patched_get_input.side_effect = internal_get_input
            with patch('robotframeworkinteractive.robotframeworkinteractive.RobotFrameworkInteractive') as patched_rfi:
                type(patched_rfi.return_value).run_rf = MagicMock(return_value='good')
                type(patched_rfi.return_value).alter_commands = MagicMock(side_effect=passthrough_alter_commands)
                run_interactive()
                self.assertEqual(2, patched_get_input.call_count)
                type(patched_rfi.return_value).run_rf.assert_called_once_with('Log To Console  Test')

    def test_run_interactive_export_exit(self):
        def internal_get_input(*args, **kwargs):
            inputs = ['export()', 'exit()']
            result = inputs[self.counter]
            self.counter += 1
            return result

        with patch('robotframeworkinteractive.robotframeworkinteractive.get_input') as patched_get_input:
            patched_get_input.side_effect = internal_get_input
            with patch('robotframeworkinteractive.robotframeworkinteractive.RobotFrameworkInteractive') as patched_rfi:
                type(patched_rfi.return_value).export = MagicMock(return_value='good')
                type(patched_rfi.return_value).SUCCESS_CMD_HISTORY = PropertyMock(return_value=[])
                run_interactive()
                self.assertEqual(2, patched_get_input.call_count)
                type(patched_rfi.return_value).export.assert_called_once()
                self.assertEqual(['export()'], type(patched_rfi.return_value).SUCCESS_CMD_HISTORY)

    def test_run_interactive_exportall_exit(self):
        def internal_get_input(*args, **kwargs):
            inputs = ['exportall()', 'exit()']
            result = inputs[self.counter]
            self.counter += 1
            return result

        with patch('robotframeworkinteractive.robotframeworkinteractive.get_input') as patched_get_input:
            patched_get_input.side_effect = internal_get_input
            with patch('robotframeworkinteractive.robotframeworkinteractive.RobotFrameworkInteractive') as patched_rfi:
                type(patched_rfi.return_value).export = MagicMock(return_value='good')
                type(patched_rfi.return_value).SUCCESS_CMD_HISTORY = PropertyMock(return_value=[])
                run_interactive()
                self.assertEqual(2, patched_get_input.call_count)
                type(patched_rfi.return_value).export.assert_called_once_with(allCmds=True)
                self.assertEqual(['exportall()'], type(patched_rfi.return_value).SUCCESS_CMD_HISTORY)

    def test_run_interactive_exception_exit(self):
        def internal_get_input(*args, **kwargs):
            inputs = ['export()', 'exit()']
            result = inputs[self.counter]
            self.counter += 1
            return result

        with patch('robotframeworkinteractive.robotframeworkinteractive.get_input') as patched_get_input:
            patched_get_input.side_effect = internal_get_input
            with patch('robotframeworkinteractive.robotframeworkinteractive.RobotFrameworkInteractive') as patched_rfi:
                type(patched_rfi.return_value).export = MagicMock(side_effect=raise_exception)
                type(patched_rfi.return_value).SUCCESS_CMD_HISTORY = PropertyMock(return_value=[])
                with self.assertRaises(Exception):
                    run_interactive()
                self.assertEqual(1, patched_get_input.call_count)
                type(patched_rfi.return_value).export.assert_called_once()
                self.assertEqual([], type(patched_rfi.return_value).SUCCESS_CMD_HISTORY)


class MainTests(unittest.TestCase):
    @patch('builtins.print', new_callable=MagicMock)
    @patch('builtins.open', new_callable=mock_open, read_data='1')
    def test_main_success(self, m_open, m_print):
        with patch('robotframeworkinteractive.robotframeworkinteractive.robot.run') as patched_robot_run:
            main()
            m_open.assert_called_once_with(os.devnull, 'w')
            m_print.assert_called_once_with(WELCOME_MSG)
            dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            patched_robot_run.assert_called_once_with(os.path.join(dir_path, 'robotframeworkinteractive', "Main.robot"),
                                                      stdout=m_open.return_value, stderr=m_open.return_value, log=None,
                                                      output=None, report=None)

    @patch('builtins.print', new_callable=MagicMock)
    @patch('builtins.open', new_callable=mock_open, read_data='1')
    def test_main_exception(self, m_open, m_print):
        with patch('robotframeworkinteractive.robotframeworkinteractive.robot.run') as patched_robot_run:
            patched_robot_run.side_effect = raise_exception
            main()
            m_open.assert_called_once_with(os.devnull, 'w')
            m_print.assert_called_with(EXCEPTION)


if __name__ == '__main__':
    unittest.main()
