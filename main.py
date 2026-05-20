import argparse
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from drift_detector import detect_drift

console = Console()

def scan_directory(directory: str):
    """Recursively scan directory for Python and Markdown files."""
    path = Path(directory)
    python_files = list(path.glob('**/*.py'))
    markdown_files = list(path.glob('**/*.md'))
    return python_files, markdown_files

def main():
    parser = argparse.ArgumentParser(description='DocGuard CLI - Detect documentation drift')
    parser.add_argument('directory', help='Directory to scan')
    parser.add_argument('--dry-run', action='store_true', help='Simulate without scanning')
    parser.add_argument('--output', choices=['terminal', 'json'], default='terminal')
    parser.add_argument('--output-file', type=str, default=None)
    
    args = parser.parse_args()
    
    # Dry run logic
    if args.dry_run:
        console.print("Dry-run mode enabled. No scanning will occur.")
        return

    python_files, markdown_files = scan_directory(args.directory)
    
    findings = detect_drift(python_files, markdown_files)
    
    if args.output == 'terminal':
        console.print("[bold]DocGuard Scan Results:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Element", style="dim")
        table.add_column("Type", style="cyan")
        table.add_column("File", style="dim")
        table.add_column("Status", style="red")
        
        for f in findings:
            table.add_row(f['element'], f['type'], f['file'], f['status'])
        console.print(table)
        
    elif args.output == 'json':
        output = json.dumps(findings, indent=2)
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(output)
            console.print(f"Results exported to {args.output_file}")
        else:
            console.print(output)

if __name__ == '__main__':
    main()
