import ast
import re
from typing import List, Dict
from pathlib import Path

def parse_python_file(file_path: Path) -> List[Dict]:
    """Parse a Python file and extract function and class definitions."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)
        
        definitions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                definitions.append({
                    'name': node.name,
                    'type': 'function' if isinstance(node, ast.FunctionDef) else 'class',
                    'line': node.lineno,
                    'file': str(file_path)
                })
        return definitions
    except Exception as e:
        print(f"Warning: Failed to parse {file_path}: {e}")
        return []

def parse_markdown_file(file_path: Path) -> List[Dict]:
    """Parse a Markdown file and extract sections."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex to match markdown headers
        pattern = re.compile(r'^#{1,6}\s+(.*)', re.MULTILINE)
        matches = pattern.findall(content)
        
        sections = []
        for section in matches:
            sections.append({
                'title': section.strip(),
                'content': content,
                'file': str(file_path)
            })
        return sections
    except Exception as e:
        print(f"Warning: Failed to parse {file_path}: {e}")
        return []
