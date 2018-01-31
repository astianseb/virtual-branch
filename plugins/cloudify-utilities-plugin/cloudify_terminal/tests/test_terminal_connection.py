# Copyright (c) 2017 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.
import unittest
from mock import MagicMock, patch, mock_open, Mock, call

from cloudify.exceptions import RecoverableError

import cloudify_terminal.terminal_connection as terminal_connection


class TestTasks(unittest.TestCase):

    sleep_mock = None

    def setUp(self):
        super(TestTasks, self).setUp()
        mock_sleep = MagicMock()
        self.sleep_mock = patch('time.sleep', mock_sleep)
        self.sleep_mock.start()

    def tearDown(self):
        if self.sleep_mock:
            self.sleep_mock.stop()
            self.sleep_mock = None
        super(TestTasks, self).tearDown()

    def test_empty_send(self):
        conn = terminal_connection.connection()
        conn._conn_send("")

    def test_send(self):
        conn = terminal_connection.connection()
        conn.conn = MagicMock()
        conn.conn.send = MagicMock(return_value=4)
        conn.conn.closed = False
        conn.conn.log_file_name = False

        conn._conn_send("abcd")

        conn.conn.send.assert_called_with("abcd")

    def test_send_closed_connection(self):
        conn = terminal_connection.connection()
        conn.conn = MagicMock()
        conn.conn.send = MagicMock(return_value=3)
        conn.conn.closed = True
        conn.conn.log_file_name = False

        conn._conn_send("abcd")

        conn.conn.send.assert_called_with("abcd")

    def test_send_troubles(self):
        conn = terminal_connection.connection()
        conn.conn = MagicMock()
        conn.logger = MagicMock()
        conn.conn.send = MagicMock(return_value=-1)
        conn.conn.closed = True
        conn.conn.log_file_name = False

        conn._conn_send("abcd")

        conn.logger.info.assert_called_with("We have issue with send!")
        conn.conn.send.assert_called_with("abcd")

    def test_send_byte_by_byte(self):
        conn = terminal_connection.connection()
        conn.conn = MagicMock()
        conn.logger = MagicMock()
        conn.conn.send = Mock(return_value=2)
        conn.conn.closed = False
        conn.conn.log_file_name = False

        conn._conn_send("abcd")

        conn.conn.send.assert_has_calls([call('abcd'), call('cd')])

    def test_recv(self):
        conn = terminal_connection.connection()
        conn.conn = MagicMock()
        conn.logger = MagicMock()
        conn.conn.recv = MagicMock(return_value="AbCd")
        conn.conn.log_file_name = False

        self.assertEqual(conn._conn_recv(4), "AbCd")

        conn.conn.recv.assert_called_with(4)

    def test_recv_empty(self):
        conn = terminal_connection.connection()
        conn.conn = MagicMock()
        conn.logger = MagicMock()
        conn.conn.recv = MagicMock(return_value="")
        conn.conn.log_file_name = False

        self.assertEqual(conn._conn_recv(4), "")

        conn.logger.info.assert_called_with('We have empty response.')
        conn.conn.recv.assert_called_with(4)

    def test_find_any_in(self):
        conn = terminal_connection.connection()

        self.assertEqual(conn._find_any_in("abcd\n$abc", ["$", "#"]), 5)
        self.assertEqual(conn._find_any_in("abcd\n>abc", ["$", "#"]), -1)

    def test_delete_backspace(self):
        conn = terminal_connection.connection()

        self.assertEqual(conn._delete_backspace("abc\bd\n$a\bbc"), "abd\n$bc")

    def test_send_response(self):
        conn = terminal_connection.connection()

        self.assertEqual(conn._send_response("abcd?", []), -1)

        self.assertEqual(
            conn._send_response(
                "abcd?", [{
                    'question': 'yes?',
                    'answer': 'no'
                }]), -1
        )

        conn.conn = MagicMock()
        conn.logger = MagicMock()
        conn.conn.send = Mock(return_value=2)
        conn.conn.closed = False
        conn.conn.log_file_name = False

        self.assertEqual(
            conn._send_response(
                "continue, yes?", [{
                    'question': 'yes?',
                    'answer': 'no'
                }]), 14
        )

        conn.conn.send.assert_called_with("no")

    def test_is_closed(self):
        conn = terminal_connection.connection()

        conn.conn = MagicMock()

        conn.conn.closed = False
        self.assertFalse(conn.is_closed())

        conn.conn.closed = True
        self.assertTrue(conn.is_closed())

        conn.conn = None
        self.assertTrue(conn.is_closed())

    def test_close(self):
        conn = terminal_connection.connection()

        conn.conn = MagicMock()
        conn.conn.close = MagicMock()
        conn.ssh = MagicMock()
        conn.ssh.close = MagicMock()

        conn.close()

        conn.conn.close.assert_called_with()
        conn.ssh.close.assert_called_with()

    def test_write_to_log_no_logfile(self):
        conn = terminal_connection.connection()
        conn.log_file_name = None

        conn._write_to_log("Some_text")

    def test_write_to_log_write_file(self):
        conn = terminal_connection.connection()
        conn.log_file_name = '/proc/read_only_file'
        conn.logger = MagicMock()

        with patch("os.path.isdir", MagicMock(return_value=True)):
            fake_file = mock_open()
            with patch(
                    '__builtin__.open', fake_file
            ):
                conn._write_to_log("Some_text", False)

            fake_file.assert_called_once_with('/proc/read_only_file.in', 'a+')
            fake_file().write.assert_called_with('Some_text')

    def test_write_to_log_cantcreate_dir(self):
        conn = terminal_connection.connection()
        conn.log_file_name = '/proc/read_only/file'
        conn.logger = MagicMock()

        with patch("os.path.isdir", MagicMock(return_value=False)):
            with patch("os.makedirs", MagicMock(side_effect=Exception(
                "[Errno 13] Permission denied: '/proc/read_only'"
            ))):
                conn._write_to_log("Some_text")
        conn.logger.info.assert_called_with(
            "[Errno 13] Permission denied: '/proc/read_only'"
        )

    def test_connect_with_password(self):
        conn = terminal_connection.connection()

        ssh_mock = MagicMock()
        ssh_mock.connect = MagicMock(side_effect=OSError("e"))
        with patch("paramiko.SSHClient", MagicMock(return_value=ssh_mock)):
            with self.assertRaises(OSError):
                conn.connect("ip", "user", "password", None, port=44,
                             prompt_check="prompt_check", logger="logger",
                             log_file_name="log_file_name")

        ssh_mock.connect.assert_called_with(
            'ip', allow_agent=False, look_for_keys=False, password='password',
            port=44, timeout=5, username='user')

        self.assertEqual(conn.logger, "logger")
        self.assertEqual(conn.log_file_name, "log_file_name")

    def test_connect_with_key(self):
        conn = terminal_connection.connection()

        ssh_mock = MagicMock()
        ssh_mock.connect = MagicMock(side_effect=OSError("e"))
        with patch("paramiko.RSAKey.from_private_key",
                   MagicMock(return_value="key_value")):
            with patch("paramiko.SSHClient", MagicMock(return_value=ssh_mock)):
                with self.assertRaises(OSError):
                    conn.connect("ip", "user", None, "key",
                                 prompt_check=None, logger="logger",
                                 log_file_name="log_file_name")

        ssh_mock.connect.assert_called_with(
            'ip', allow_agent=False, pkey='key_value', port=22, timeout=5,
            username='user')

        self.assertEqual(conn.logger, "logger")
        self.assertEqual(conn.log_file_name, "log_file_name")

    def test_connect(self):
        conn = terminal_connection.connection()
        conn_mock = MagicMock()
        conn_mock.recv = MagicMock(return_value="some_prompt#")
        ssh_mock = MagicMock()
        ssh_mock.connect = MagicMock()
        ssh_mock.invoke_shell = MagicMock(return_value=conn_mock)
        with patch("paramiko.SSHClient", MagicMock(return_value=ssh_mock)):
            self.assertEqual(
                conn.connect("ip", "user", "password", None, port=44,
                             prompt_check=None, logger=MagicMock(),
                             log_file_name=None),
                "some_prompt"
            )

    def test_cleanup_response_empty(self):
        conn = terminal_connection.connection()

        self.assertEqual(conn._cleanup_response(" text ", ":", []), "text")

    def test_cleanup_response_with_prompt(self):
        conn = terminal_connection.connection()

        conn.logger = MagicMock()

        self.assertEqual(
            conn._cleanup_response("prompt> text ", "prompt>", ['error']),
            "text"
        )

        conn.logger.info.assert_not_called()

    def test_cleanup_response_without_prompt(self):
        conn = terminal_connection.connection()
        conn.logger = MagicMock()

        self.assertEqual(
            conn._cleanup_response("prmpt> text ", "prompt>", ['error']),
            "prmpt> text"
        )

        conn.logger.info.assert_called_with(
            "Have not found 'prompt>' in response: ''prmpt> text ''")

    def test_cleanup_response_mess_before_prompt(self):
        conn = terminal_connection.connection()
        conn.logger = MagicMock()

        self.assertEqual(
            conn._cleanup_response(
                "..prompt> text\n some", "prompt>", ['error']
            ),
            "some"
        )

        conn.logger.info.assert_called_with(
            "Some mess before 'prompt>' in response: ''..prompt> "
            "text\\n some''")

    def test_cleanup_response_error(self):
        conn = terminal_connection.connection()
        conn.logger = MagicMock()

        with self.assertRaises(RecoverableError) as error:
            conn._cleanup_response(
                "prompt> text\n some\nerror", "prompt>", ['error']
            )

        conn.logger.info.assert_not_called()

        self.assertEqual(
            str(error.exception),
            'Looks as we have error in response: prompt> text\n some\nerror'
        )

    def test_run_with_closed_connection(self):
        conn = terminal_connection.connection()
        conn.logger = MagicMock()
        conn.conn = MagicMock()
        conn.conn.closed = True
        conn.conn.send = MagicMock(return_value=5)

        self.assertEqual(conn.run("test"), "")

        conn.conn.send.assert_called_with("test\n")

    def test_run_with_closed_connection_after_twice_check(self):
        conn = terminal_connection.connection()
        conn.logger = MagicMock()
        conn.conn = MagicMock()
        conn.conn.closed = False

        conn.conn.call_count = 0

        def _recv(size):

            if conn.conn.call_count == 1:
                conn.conn.closed = True

            conn.conn.call_count += 1

            return "+"

        conn.conn.send = MagicMock(return_value=5)
        conn.conn.recv = _recv

        self.assertEqual(conn.run("test"), "++")

        conn.conn.send.assert_called_with("test\n")

    def test_run_with_closed_connection_after_third_check(self):
        conn = terminal_connection.connection()
        conn.logger = MagicMock()

        class _fake_conn(object):

            call_count = 0

            def send(self, text):
                return len(text)

            def recv(self, size):
                return "+\n"

            @property
            def closed(self):
                self.call_count += 1

                return (self.call_count >= 4)

        conn.conn = _fake_conn()

        self.assertEqual(conn.run("test"), "+")

    def test_run_return_without_delay(self):
        conn = terminal_connection.connection()
        conn.logger = MagicMock()
        conn.conn = MagicMock()
        conn.conn.closed = False
        conn.conn.send = MagicMock(return_value=5)
        conn.conn.recv = MagicMock(return_value="\nmessage\n#")

        self.assertEqual(conn.run("test"), "message")

        conn.conn.send.assert_called_with("test\n")

    def test_run_return_without_delay_with_responses(self):
        conn = terminal_connection.connection()
        conn.logger = MagicMock()
        conn.conn = MagicMock()
        conn.conn.closed = False
        conn.conn.send = MagicMock(side_effect=[5, 2])
        conn.conn.recv = MagicMock(side_effect=["\nmessage, yes?", "ok\n#"])

        self.assertEqual(
            conn.run("test", responses=[{
                'question': 'yes?',
                'answer': 'no'
            }]),
            "message, yes?ok"
        )

        conn.conn.send.assert_has_calls([call("test\n"), call('no')])


if __name__ == '__main__':
    unittest.main()
