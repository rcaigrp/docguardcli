import click
import os
import ast
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table

def scan_directory(directory):
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.py') or filename.endswith('.md'):
                files.append(os.path.join(root, filename))
    return files

def parse_python_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    try:
        tree = ast.parse(content)
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                functions.append({'name': node.name, 'docstring': docstring})
        return functions
    except SyntaxError:
        return []

def parse_markdown_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    headings = [line.lstrip('# ') for line in content.split('\n') if line.startswith('# ')]
    return headings

def identify_drift(py_files, md_files):
    drifts = []
    py_funcs = set()
    for f in py_files:
        funcs = parse_python_file(f)
        for func in funcs:
            if func['name']:
                py_funcs.add(func['name'])
    
    md_sections = set()
    for f in md_files:
        headings = parse_markdown_file(f)
        md_sections.update(headings)
    
    undocumented = py_funcs - md_sections
    for func_name in undocumented:
        for f in py_files:
            funcs = parse_python_file(f)
            for func in funcs:
                if func['name'] == func_name:
                    drifts.append({'type': 'undocumented_function', 'function': func_name, 'file': f})
                    break
    return drifts

def generate_table(drifts, dry_run=False):
    console = Console()
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Type", style="dim")
    table.add_column("Function/Section", style="cyan")
    table.add_column("File", style="green")
    for d in drifts:
        table.add_row(d['type'], d['function'], d['file'])
    console.print(table)
    if dry_run:
        console.print("[bold yellow]Dry run mode. Changes will not be applied.[/bold yellow]")
    return drifts

def export_to_json(drifts, output_path):
    with open(output_path, 'w') as f:
        json.dump(drifts, f, indent=2)
    return output_path

@click.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(allow_dash=True))
@click.option('--dry-run', is_flag=True)
def cli(directory, output, dry_run):
    """DocGuard CLI - Identify documentation drift in Python and Markdown files."""
    py_files = [f for f in scan_directory(directory) if f.endswith('.py')]
    md_files = [f for f in scan_directory(directory) if f.endswith('.md')]
    
    drifts = identify_drift(py_files, md_files)
    generate_table(drifts, dry_run)
    
    if output:
        export_to_json(drifts, output)
        click.echo(f"Exported to {output}")

if __name__ == '__main__':
    cli()
