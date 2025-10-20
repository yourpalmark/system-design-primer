#!/usr/bin/env python3
"""
Generate a unified PDF from all Markdown files in the system-design-primer repository.
This script combines all markdown files while preserving internal links.
"""

import os
import re
import subprocess
from pathlib import Path
import argparse
import sys

class MarkdownPDFGenerator:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.combined_markdown = ""

        self.file_order = [
            "README.md",
            "CONTRIBUTING.md", 
            # Solutions - System Design (English only)
            "solutions/system_design/pastebin/README.md",
            "solutions/system_design/twitter/README.md", 
            "solutions/system_design/web_crawler/README.md",
            "solutions/system_design/mint/README.md",
            "solutions/system_design/social_graph/README.md",
            "solutions/system_design/query_cache/README.md",
            "solutions/system_design/sales_rank/README.md",
            "solutions/system_design/scaling_aws/README.md",
            # Solutions - Object-Oriented Design
            "solutions/object_oriented_design/hash_table/hash_map.ipynb",
            "solutions/object_oriented_design/lru_cache/lru_cache.ipynb",
            "solutions/object_oriented_design/call_center/call_center.ipynb",
            "solutions/object_oriented_design/deck_of_cards/deck_of_cards.ipynb",
            "solutions/object_oriented_design/parking_lot/parking_lot.ipynb",
            "solutions/object_oriented_design/online_chat/online_chat.ipynb"
        ]
        

    def find_all_markdown_files(self):
        """Find all English markdown and notebook files in the repository."""
        content_files = []
        for root, dirs, files in os.walk(self.repo_path):
            # Skip .github directory
            if '.github' in root:
                continue
            for file in files:
                if file.endswith('.md') or file.endswith('.ipynb'):
                    rel_path = os.path.relpath(os.path.join(root, file), self.repo_path)
                    # Only include English files (exclude translated versions)
                    if not self.is_non_english_file(rel_path):
                        content_files.append(rel_path)
        return content_files
    

    def is_non_english_file(self, file_path):
        """Check if a file is a non-English translation or generated file."""
        # Skip files with language suffixes
        non_english_patterns = [
            'README-ja.md',      # Japanese
            'README-zh-Hans.md', # Simplified Chinese
            'README-zh-TW.md',   # Traditional Chinese
            '-zh-Hans.md',       # Simplified Chinese suffix
            '-ja.md'             # Japanese suffix
        ]
        

        # Skip generated files (our own output) and translation-related files
        excluded_files = [
            'combined-system-design-primer.md',
            'combined-system-design-primer.html',
            'TRANSLATIONS.md'  # Not needed for English-only PDF
        ]
        
        for pattern in non_english_patterns:
            if pattern in file_path:
                return True
                

        for excluded_file in excluded_files:
            if excluded_file in file_path:
                return True
                
        return False
    
    def process_internal_links(self, content, current_file):
        """Process internal links to work in a unified document."""
        
        # Convert relative links to other .md files to internal references
        def replace_md_link(match):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # Skip external links (http/https)
            if link_url.startswith(('http://', 'https://')):
                return match.group(0)
            

            # Handle links to solution files (.md, .ipynb, .py)
            if link_url.startswith('solutions/'):
                parts = link_url.split('/')
                if len(parts) >= 4:
                    section_type = parts[1].replace('_', '-')  # system_design -> system-design or object_oriented_design -> object-oriented-design
                    problem_name = parts[2].replace('_', '-')  # pastebin -> pastebin
                    

                    # For system design solutions with README.md files, link to internal sections
                    if section_type == 'system-design' and link_url.endswith('README.md'):
                        section_id = f"{section_type}-{problem_name}".lower()
                        return f"[{link_text}](#{section_id})"
                    
                    # For object-oriented design .ipynb files, now link to internal sections too
                    elif section_type == 'object-oriented-design' and link_url.endswith('.ipynb'):
                        section_id = f"{section_type}-{problem_name}".lower()
                        return f"[{link_text}](#{section_id})"
                    
                    # For other solution files, link to GitHub
                    else:
                        github_base = "https://github.com/donnemartin/system-design-primer/blob/master"
                        return f"[{link_text}]({github_base}/{link_url})"
            
            # Handle links to other .md files
            if link_url.endswith('.md'):
                
                # Convert to section reference for other .md files
                filename = os.path.basename(link_url).replace('.md', '').replace('README', '')
                if filename:
                    section_name = filename.replace('_', '-').replace(' ', '-').lower()
                    return f"[{link_text}](#{section_name})"
                else:
                    # If it's README.md, link to the main section
                    dir_name = os.path.dirname(link_url)
                    if dir_name:
                        section_name = os.path.basename(dir_name).replace('_', '-')
                        return f"[{link_text}](#{section_name})"
                    else:
                        return f"[{link_text}](#main-readme)"
            
            # Keep internal section links as is
            if link_url.startswith('#'):
                return match.group(0)
                
            # Convert relative paths to absolute GitHub links for resources
            if link_url.startswith('images/') or link_url.startswith('resources/'):
                github_base = "https://raw.githubusercontent.com/donnemartin/system-design-primer/master"
                return f"[{link_text}]({github_base}/{link_url})"
            
            return match.group(0)
        
        # Pattern to match markdown links [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        content = re.sub(link_pattern, replace_md_link, content)
        

        return content
    
    def clean_unicode_characters(self, content):
        """Clean up problematic Unicode characters for LaTeX."""
        # Replace common problematic Unicode characters
        replacements = {
            '∙': '•',  # Replace bullet operator with regular bullet
            '…': '...',  # Replace ellipsis with three dots
            '–': '--',  # Replace en dash with double dash
            '—': '---',  # Replace em dash with triple dash
            ''': "'",   # Replace left single quote
            ''': "'",   # Replace right single quote  
            '"': '"',   # Replace left double quote
            '"': '"',   # Replace right double quote
            '†': '+',   # Replace dagger
            '‡': '++',  # Replace double dagger
            '§': 'Section',  # Replace section sign
            '¶': 'Para',    # Replace pilcrow sign
            '©': '(c)',     # Replace copyright
            '®': '(R)',     # Replace registered trademark
            '™': '(TM)',    # Replace trademark
        }
        
        for unicode_char, replacement in replacements.items():
            content = content.replace(unicode_char, replacement)
        
        return content
    
    def add_section_header(self, file_path, content):
        """Add a clear section header for each file."""
        if file_path == "README.md":
            return content  # Main README keeps its original structure
        

        # Create section header based on file path
        if file_path.startswith("solutions/"):
            parts = file_path.split('/')
            if len(parts) >= 4:
                section_type = parts[1].replace('_', ' ').title()  # system_design -> System Design
                problem_name = parts[2].replace('_', ' ').title()   # pastebin -> Pastebin
                # Create header with explicit anchor ID to match our link format
                section_id = f"{parts[1].replace('_', '-')}-{parts[2].replace('_', '-')}".lower()
                header = f"\n\n# {section_type}: {problem_name} {{#{section_id}}}\n\n"
            else:
                header = f"\n\n# {os.path.dirname(file_path)}\n\n"
        else:
            # For top-level files
            filename = os.path.basename(file_path).replace('.md', '')
            if filename.startswith('README-'):
                lang = filename.replace('README-', '')
                header = f"\n\n# System Design Primer ({lang})\n\n"
            else:
                header = f"\n\n# {filename}\n\n"
        

        return header + content
    
    def convert_notebook_to_markdown(self, notebook_path):
        """Convert a Jupyter notebook to markdown using pandoc."""
        try:
            cmd = [
                '/opt/homebrew/bin/pandoc',
                str(notebook_path),
                '-o', '-',  # Output to stdout
                '--from', 'ipynb',
                '--to', 'markdown'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"Warning: Could not convert notebook {notebook_path}: {result.stderr}")
                return f"# {notebook_path}\n\n*Notebook conversion failed*\n\n"
                
        except Exception as e:
            print(f"Warning: Error converting notebook {notebook_path}: {e}")
            return f"# {notebook_path}\n\n*Notebook conversion failed*\n\n"
    
    def combine_markdown_files(self):
        """Combine all markdown files in the correct order."""
        all_files = self.find_all_markdown_files()
        
        # Process files in the specified order first
        processed_files = set()
        
        for file_path in self.file_order:
            if file_path in all_files:

                full_path = self.repo_path / file_path
                if full_path.exists():
                    print(f"Processing: {file_path}")
                    
                    # Handle different file types
                    if file_path.endswith('.ipynb'):
                        content = self.convert_notebook_to_markdown(full_path)
                    else:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    
                    # Clean up Unicode characters, process links and add section header
                    content = self.clean_unicode_characters(content)
                    content = self.process_internal_links(content, file_path)
                    content = self.add_section_header(file_path, content)
                    
                    self.combined_markdown += content
                    processed_files.add(file_path)
        
        # Add any remaining markdown files not in the order list
        for file_path in all_files:
            if file_path not in processed_files:
                full_path = self.repo_path / file_path

                if full_path.exists():
                    print(f"Processing additional English file: {file_path}")
                    
                    # Handle different file types
                    if file_path.endswith('.ipynb'):
                        content = self.convert_notebook_to_markdown(full_path)
                    else:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    
                    content = self.clean_unicode_characters(content)
                    content = self.process_internal_links(content, file_path)
                    content = self.add_section_header(file_path, content)
                    
                    self.combined_markdown += content
    
    def save_combined_markdown(self, output_path):
        """Save the combined markdown to a file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.combined_markdown)
        print(f"Combined markdown saved to: {output_path}")
    

    def create_custom_css(self):
        """Create custom CSS for better PDF formatting."""

        css_content = """
        <style>
        @media print {

            @page {
                margin: 0.8in 0.6in 1in 0.6in;  /* Extra bottom margin for page numbers */
                size: A4;

                @bottom-center {
                    content: counter(page);
                    font-size: 12px;
                    color: #666;
                }
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                line-height: 1.6;
                color: #24292e;
                max-width: none;
                margin: 0 !important;

                padding: 30px 20px !important;
            }
            
            /* Image sizing for PDF */
            img {
                max-width: 100% !important;
                height: auto !important;
                display: block;
                margin: 10px auto;
                page-break-inside: avoid;
            }
            
            /* Ensure large images fit within page width */
            img[src*="jj3A5N8.png"], img[src*="4edXG0T.png"] {
                max-width: 90% !important;
                width: auto !important;
            }
            
            /* Links styling */
            a {
                color: #0366d6;
                text-decoration: underline;
            }
            
            a:hover {
                text-decoration: underline;
            }
            
            /* Code blocks */
            pre {
                background-color: #f6f8fa;
                border-radius: 6px;
                padding: 16px;
                overflow-x: auto;
                page-break-inside: avoid;
            }
            
            /* Tables */
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 16px 0;
                page-break-inside: avoid;
            }
            
            th, td {
                border: 1px solid #d0d7de;
                padding: 8px 12px;
                text-align: left;
            }
            
            th {
                background-color: #f6f8fa;
                font-weight: 600;
            }
            
            /* Headings */
            h1, h2, h3, h4, h5, h6 {
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
                page-break-after: avoid;
            }
            
            h1 {
                font-size: 2em;
                border-bottom: 1px solid #eaecef;
                padding-bottom: 10px;
            }
            
            h2 {
                font-size: 1.5em;
                border-bottom: 1px solid #eaecef;
                padding-bottom: 8px;
            }

        }
        
        @media screen {
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                line-height: 1.6;
                color: #24292e;
                max-width: 1200px;
                margin: 0 auto;

                padding: 30px 20px;
            }
        }
        </style>
        """
        return css_content

    def generate_html(self, markdown_path, html_path):
        """Generate HTML from markdown using pandoc."""
        try:
            cmd = [
                '/opt/homebrew/bin/pandoc',
                str(markdown_path),
                '-o', str(html_path),

                '--toc',  # Table of contents
                '--toc-depth=3',
                '--standalone',  # Creates complete HTML document
                '--css=https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/github-markdown-light.min.css',
                '--syntax-highlighting=tango',
                '--metadata', 'title=System Design Primer - Complete Guide'
            ]
            
            print("Generating HTML...")
            print(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Post-process HTML to add custom CSS and fix links
                self.post_process_html(html_path)
                print(f"HTML generated successfully: {html_path}")
                return True
            else:
                print(f"Error generating HTML: {result.stderr}")
                return False
                

        except Exception as e:
            print(f"Exception during HTML generation: {e}")
            return False
    
    def post_process_html(self, html_path):
        """Post-process HTML to improve PDF formatting and fix links."""
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Add custom CSS before closing </head> tag
            custom_css = self.create_custom_css()
            html_content = html_content.replace('</head>', f'{custom_css}</head>')
            
            # Fix image paths to use absolute GitHub URLs
            github_base = "https://raw.githubusercontent.com/donnemartin/system-design-primer/master"
            
            # Fix relative image paths
            html_content = re.sub(
                r'<img([^>]*) src="images/([^"]+)"([^>]*)>',
                f'<img\\1 src="{github_base}/images/\\2"\\3>',
                html_content
            )
            
            # Ensure all internal links are preserved and external links work
            # Fix anchor links to work properly in PDF
            html_content = re.sub(
                r'<a href="#([^"]+)"([^>]*)>',
                '<a href="#\\1"\\2>',
                html_content
            )
            
            # Make external links open in new tab/window
            html_content = re.sub(
                r'<a href="(https?://[^"]+)"([^>]*)>',
                '<a href="\\1" target="_blank"\\2>',
                html_content
            )
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        except Exception as e:
            print(f"Warning: Could not post-process HTML: {e}")

    def generate_pdf_from_html(self, html_path, pdf_path):
        """Generate PDF from HTML using wkhtmltopdf or chromium."""
        # First try wkhtmltopdf
        try:

            cmd = [
                'wkhtmltopdf',
                '--page-size', 'A4',

                '--margin-top', '1.25in',
                '--margin-right', '1in', 
                '--margin-bottom', '1.25in',
                '--margin-left', '1in',
                '--enable-local-file-access',
                '--print-media-type',
                '--disable-smart-shrinking',
                '--no-header-line',  # Remove header line
                '--no-footer-line',  # Remove footer line
                '--header-spacing', '0',  # Remove header spacing
                '--footer-spacing', '0',  # Remove footer spacing
                str(html_path),
                str(pdf_path)
            ]
            
            print("Attempting PDF generation with wkhtmltopdf...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"PDF generated successfully with wkhtmltopdf: {pdf_path}")
                return True
                
        except FileNotFoundError:
            print("wkhtmltopdf not found, trying Chrome/Chromium...")
            
        # Try Chrome/Chromium as fallback
        chrome_paths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/google-chrome',
            'chromium',
            'google-chrome'
        ]
        
        for chrome_path in chrome_paths:
            try:

                cmd = [
                    chrome_path,
                    '--headless',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--run-all-compositor-stages-before-draw',
                    '--print-to-pdf=' + str(pdf_path),

                    '--print-to-pdf-no-header',  # Disable header only
                    '--print-to-pdf-page-ranges=1-999999',  # Print all pages
                    '--print-to-pdf-page-size=A4',  # Set page size

                    '--no-pdf-header-footer',  # Completely disable Chrome's header/footer system
                    '--print-to-pdf-margins-top=20',  # ~0.8 inches (20mm)
                    '--print-to-pdf-margins-bottom=20',  # ~0.8 inches (20mm)
                    '--print-to-pdf-margins-left=15',  # ~0.6 inches (15mm)
                    '--print-to-pdf-margins-right=15',  # ~0.6 inches (15mm)
                    '--virtual-time-budget=25000',  # Give more time for rendering
                    str(html_path)
                ]
                
                print(f"Attempting PDF generation with Chrome: {chrome_path}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and Path(pdf_path).exists():
                    print(f"PDF generated successfully with Chrome: {pdf_path}")
                    return True
                    
            except FileNotFoundError:
                continue
                
        print("Could not find wkhtmltopdf or Chrome/Chromium for PDF generation")
        return False

    def generate_pdf(self, markdown_path, pdf_path):
        """Generate PDF from markdown via HTML intermediate."""
        # Generate HTML first
        html_path = Path(markdown_path).with_suffix('.html')
        
        if not self.generate_html(markdown_path, html_path):
            return False
            
        # Then convert HTML to PDF
        if not self.generate_pdf_from_html(html_path, pdf_path):
            return False
            
        print(f"\n✅ PDF generation completed successfully!")
        print(f"📄 PDF file: {pdf_path}")
        print(f"🌐 HTML file: {html_path}")
        return True

def main():
    parser = argparse.ArgumentParser(description='Generate PDF from system-design-primer markdown files')
    parser.add_argument('--repo-path', default='.', help='Path to the repository')
    parser.add_argument('--output', default='system-design-primer.pdf', help='Output PDF filename')
    
    args = parser.parse_args()
    
    repo_path = Path(args.repo_path).resolve()
    output_pdf = repo_path / args.output
    combined_md = repo_path / 'combined-system-design-primer.md'
    
    print(f"Repository path: {repo_path}")
    print(f"Output PDF: {output_pdf}")
    
    # Generate the PDF
    generator = MarkdownPDFGenerator(repo_path)
    generator.combine_markdown_files()
    generator.save_combined_markdown(combined_md)
    
    if generator.generate_pdf(combined_md, output_pdf):
        print(f"\n✅ PDF generation completed successfully!")
        print(f"📄 PDF file: {output_pdf}")
        print(f"📝 Combined markdown: {combined_md}")
    else:
        print("\n❌ PDF generation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()