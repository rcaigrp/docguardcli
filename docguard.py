import os
import re
import json
import click
from rich.console import Console
from rich.table import Table

def scan_directory(path):
    files = []
    for root, dirs, filenames in os.walk(path):
        for f in filenames:
            if f.endswith(('.py', '.md', '.txt')):
                files.append(os.path.join(root, f))
    return files

def parse_comments(filepath):
    functions = set()
    if filepath.endswith('.py'):
        with open(filepath) as f:
            content = f.read()
        for match in re.finditer(r'def\s+(\w+)', content):
            functions.add(match.group(1))
    return functions

def parse_markdown(filepath):
    refs = set()
    with open(filepath) as f:
        content = f.read()
    for match in re.finditer(r'##\s+(\w+)', content):
        refs.add(match.group(1))
    return refs

def identify_drift(files):
    drift = []
    py_files = [f for f in files if f.endswith('.py')]
    md_files = [f for f in files if f.endswith('.md')]
    
    py_funcs = set()
    for f in py_files:
        py_funcs.update(parse_comments(f))
        
    md_refs = set()
    for f in md_files:
        md_refs.update(parse_markdown(f))
        
    undocumented = py_funcs - md_refs
    drift.append({
        "type": "undocumented_functions",
        "items": list(undocumented)
    })
    return drift

@click.command()
@click.argument('path')
@click.option('--dry-run', is_flag=True, help='Run without exporting or printing table')
@click.option('--output', default='docguard.json', help='Output JSON file')
def cli(path, dry_run, output):
    console = Console()
    files = scan_directory(path)
    drift = identify_drift(files)
    
    if not dry_run:
        table = Table()
        table.add_column("Type")
        table.add_column("Items")
        for d in drift:
            table.add_row(d["type"], ", ".join(d["items"]))
        console.print(table)
        
        with open(output, 'w') as f:
            json.dump(drift, f)
        
    click.echo("Scan complete")

if __name__ == '__main__':
    cli()
