import pytest
import os
import json
from unittest.mock import patch, MagicMock
import ast

import sys
sys.path.insert(0, '/workspace/projects/DocGuardCLI')
from docguard import scan_directory, parse_python_file, parse_markdown_file, identify_drift, generate_table, export_to_json, cli

def test_criterion_1_scan_directory_recursively():
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [('/fake/path', [], ['file1.py', 'file2.md'])]
        result = scan_directory('/fake/path')
        assert len(result) == 2
        assert '/fake/path/file1.py' in result
        assert '/fake/path/file2.md' in result

def test_criterion_2_parse_code_comments_and_markdown():
    mock_py_content = "def foo():\n    '''Hello'''\n"
    mock_md_content = "# Foo\n"
    
    def side_effect(path, *args, **kwargs):
        if path.endswith('.py'):
            return MagicMock(read=MagicMock(return_value=mock_py_content))
        elif path.endswith('.md'):
            return MagicMock(read=MagicMock(return_value=mock_md_content))
        return MagicMock(read=MagicMock(return_value=""))
        
    with patch('builtins.open', MagicMock(side_effect=side_effect)):
        result_py = parse_python_file('/fake/file.py')
        assert len(result_py) == 1
        assert result_py[0]['name'] == 'foo'
        assert result_py[0]['docstring'] == 'Hello'
        
        result_md = parse_markdown_file('/fake/file.md')
        assert 'Foo' in result_md

def test_criterion_3_identify_potential_drift():
    py_files = ['/fake/file.py']
    md_files = ['/fake/file.md']
    
    mock_py_content = "def undocumented():\n    '''Doc'''\n"
    mock_md_content = "# Other\n"
    
    def side_effect(path, *args, **kwargs):
        if path.endswith('.py'):
            return MagicMock(read=MagicMock(return_value=mock_py_content))
        elif path.endswith('.md'):
            return MagicMock(read=MagicMock(return_value=mock_md_content))
        return MagicMock(read=MagicMock(return_value=""))
        
    with patch('builtins.open', MagicMock(side_effect=side_effect)):
        drifts = identify_drift(py_files, md_files)
        assert len(drifts) == 1
        assert drifts[0]['type'] == 'undocumented_function'
        assert drifts[0]['function'] == 'undocumented'
