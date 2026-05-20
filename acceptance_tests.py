import os
import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch, mock_open, MagicMock

from docguard import cli, scan_directory, parse_comments, parse_markdown, identify_drift

class TestDocGuardCLI:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_scan_directory(self, runner):
        with patch('docguard.scan_directory') as mock_scan:
            mock_scan.return_value = ['/test.py', '/test.md']
            with patch('docguard.identify_drift') as mock_drift:
                mock_drift.return_value = [{"type": "test", "items": []}]
                result = runner.invoke(cli, ['/test/path'])
                assert result.exit_code == 0
                mock_scan.assert_called_once_with('/test/path')

    def test_parse_comments(self):
        with patch('builtins.open', mock_open(read_data="def foo(): pass")):
            funcs = parse_comments('/test.py')
            assert 'foo' in funcs

    def test_parse_markdown(self):
        with patch('builtins.open', mock_open(read_data="## foo")):
            refs = parse_markdown('/test.md')
            assert 'foo' in refs

    def test_identify_drift(self):
        with patch('docguard.parse_comments') as mock_parse_comments:
            mock_parse_comments.return_value = {'foo', 'bar'}
            with patch('docguard.parse_markdown') as mock_parse_md:
                mock_parse_md.return_value = {'foo'}
                drift = identify_drift(['/test.py', '/test.md'])
                assert isinstance(drift, list)
                assert 'bar' in drift[0]['items']

    def test_rich_table_output(self, runner):
        with patch('docguard.scan_directory') as mock_scan:
            mock_scan.return_value = []
            with patch('docguard.identify_drift') as mock_drift:
                mock_drift.return_value = [{"type": "undocumented", "items": ["foo"]}]
                with patch('docguard.Console') as MockConsole:
                    mock_console = MagicMock()
                    MockConsole.return_value = mock_console
                    with patch('docguard.Table') as MockTable:
                        mock_table = MagicMock()
                        MockTable.return_value = mock_table
                        result = runner.invoke(cli, ['/test/path'])
                        assert result.exit_code == 0
                        mock_console.print.assert_called_once()

    def test_dry_run_mode(self, runner):
        with patch('docguard.scan_directory') as mock_scan:
            mock_scan.return_value = []
            with patch('docguard.identify_drift') as mock_drift:
                mock_drift.return_value = [{"type": "undocumented", "items": ["foo"]}]
                with patch('docguard.Console') as MockConsole:
                    mock_console = MagicMock()
                    MockConsole.return_value = mock_console
                    result = runner.invoke(cli, ['/test/path', '--dry-run'])
                    assert result.exit_code == 0
                    assert not mock_console.print.called

    def test_json_export(self, runner):
        with patch('docguard.scan_directory') as mock_scan:
            mock_scan.return_value = []
            with patch('docguard.identify_drift') as mock_drift:
                mock_drift.return_value = [{"type": "undocumented", "items": ["foo"]}]
                with patch('builtins.open', MagicMock()) as mock_file:
                    result = runner.invoke(cli, ['/test/path', '--output', 'test.json'])
                    assert result.exit_code == 0
                    mock_file.assert_called_with('test.json', 'w')
