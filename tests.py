import unittest
from pathlib import Path
from parsers import parse_python_file, parse_markdown_file
from drift_detector import detect_drift

class TestParsers(unittest.TestCase):
    def test_parse_python_file(self):
        # Create a temp file
        with open('/tmp/test.py', 'w') as f:
            f.write('def foo(): pass\nclass Bar: pass')
        
        defs = parse_python_file(Path('/tmp/test.py'))
        names = [d['name'] for d in defs]
        self.assertIn('foo', names)
        self.assertIn('Bar', names)

    def test_parse_markdown_file(self):
        with open('/tmp/test.md', 'w') as f:
            f.write('# Hello\n## World')
        
        sections = parse_markdown_file(Path('/tmp/test.md'))
        titles = [s['title'] for s in sections]
        self.assertIn('Hello', titles)
        self.assertIn('World', titles)

class TestDriftDetector(unittest.TestCase):
    def test_detect_drift_undocumented(self):
        # Setup
        py_file = Path('/tmp/test.py')
        md_file = Path('/tmp/test.md')
        
        # Write test files
        with open(py_file, 'w') as f:
            f.write('def documented(): pass\ndef undocumented(): pass')
        with open(md_file, 'w') as f:
            f.write('# documented')
            
        findings = detect_drift([py_file], [md_file])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['element'], 'undocumented')

if __name__ == '__main__':
    unittest.main()
