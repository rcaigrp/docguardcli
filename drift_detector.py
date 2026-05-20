from typing import List, Dict
from pathlib import Path
from parsers import parse_python_file, parse_markdown_file

def detect_drift(python_files: List[Path], markdown_files: List[Path]) -> List[Dict]:
    """Detect documentation drift by comparing code definitions with markdown sections."""
    findings = []
    
    # Collect all code definitions
    code_defs = []
    for p_file in python_files:
        code_defs.extend(parse_python_file(p_file))
    
    # Collect all markdown sections
    md_sections = []
    for m_file in markdown_files:
        md_sections.extend(parse_markdown_file(m_file))
        
    # Heuristic: Check if a function/class name appears in a markdown section title
    for defn in code_defs:
        found = False
        for section in md_sections:
            # Case-insensitive check
            if defn['name'].lower() in section['title'].lower():
                found = True
                break
        
        if not found:
            findings.append({
                'element': defn['name'],
                'type': defn['type'],
                'file': defn['file'],
                'status': 'undocumented'
            })
            
    return findings
