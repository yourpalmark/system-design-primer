#!/usr/bin/env python3
"""
List all markdown files that would be included in the PDF generation.
"""

import os
from pathlib import Path

def is_non_english_file(file_path):
    """Check if a file is a non-English translation or generated file."""
    # Skip files with language suffixes
    non_english_patterns = [
        'README-ja.md',      # Japanese
        'README-zh-Hans.md', # Simplified Chinese
        'README-zh-TW.md',   # Traditional Chinese
        '-zh-Hans.md',       # Simplified Chinese suffix
        '-ja.md'             # Japanese suffix
    ]
    
    # Skip generated files (our own output)
    generated_files = [
        'combined-system-design-primer.md',
        'combined-system-design-primer.html'
    ]
    
    for pattern in non_english_patterns:
        if pattern in file_path:
            return True
            
    for generated_file in generated_files:
        if generated_file in file_path:
            return True
            
    return False

def find_all_markdown_files(repo_path):
    """Find all English markdown files in the repository."""
    markdown_files = []
    for root, dirs, files in os.walk(repo_path):
        # Skip .github directory
        if '.github' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                rel_path = os.path.relpath(os.path.join(root, file), repo_path)
                # Only include English files (exclude translated versions)
                if not is_non_english_file(rel_path):
                    markdown_files.append(rel_path)
    return sorted(markdown_files)

if __name__ == "__main__":
    repo_path = "."
    files = find_all_markdown_files(repo_path)
    
    print("📄 MARKDOWN FILES THAT WOULD BE INCLUDED:")
    print("=" * 60)
    
    for i, file_path in enumerate(files, 1):
        # Get file size
        full_path = Path(repo_path) / file_path
        if full_path.exists():
            size_kb = full_path.stat().st_size // 1024
            print(f"{i:2d}. {file_path:<50} ({size_kb:>4d} KB)")
        else:
            print(f"{i:2d}. {file_path:<50} (missing)")
    
    print(f"\nTotal: {len(files)} files")
    
    # Calculate total size
    total_size = 0
    for file_path in files:
        full_path = Path(repo_path) / file_path
        if full_path.exists():
            total_size += full_path.stat().st_size
    
    print(f"Total size: {total_size // 1024:.0f} KB ({total_size / (1024*1024):.1f} MB)")