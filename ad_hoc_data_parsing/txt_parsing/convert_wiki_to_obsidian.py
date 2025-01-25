import os
import re
from pathlib import Path


class WikiToMarkdownConverter:
    def __init__(self):
        # Common wiki markup patterns and their markdown equivalents
        self.conversion_patterns = [
            # Headers
            (r'=====(.+?)=====', r'##### \1'),  # h5
            (r'====(.+?)====', r'#### \1'),     # h4
            (r'===(.+?)===', r'### \1'),        # h3
            (r'==(.+?)==', r'## \1'),           # h2
            (r'=(.+?)=', r'# \1'),              # h1
            
            # Text formatting
            (r"'''(.+?)'''", r'**\1**'),        # bold
            (r"''(.+?)''", r'*\1*'),            # italic
            
            # Lists
            (r'^\* ', r'- '),                   # unordered lists
            (r'^\*\* ', r'  - '),               # nested unordered lists
            (r'^\# ', r'1. '),                  # ordered lists
            (r'^\#\# ', r'  1. '),              # nested ordered lists
            
            # Links
            (r'\[\[([^|]+?)\]\]', r'[[\1]]'),                      # internal links
            (r'\[\[([^|]+?)\|([^]]+?)\]\]', r'[[\1|\2]]'),        # internal links with alias
            (r'\[([^]]+?)\s+([^]]+?)\]', r'[\2](\1)'),            # external links
            
            # Code blocks
            (r'<code>(.*?)</code>', r'`\1`'),                      # inline code
            (r'<pre>(.*?)</pre>', r'```\n\1\n```'),                # code blocks
        ]

    def convert_content(self, wiki_content):
        """Convert wiki markup to markdown"""
        md_content = wiki_content
        
        # Handle multiline code blocks first
        md_content = re.sub(
            r'<pre>\n?(.*?)\n?</pre>',
            lambda m: f"```\n{m.group(1)}\n```",
            md_content,
            flags=re.DOTALL
        )
        
        # Apply all other conversion patterns
        for pattern, replacement in self.conversion_patterns:
            md_content = re.sub(pattern, replacement, md_content, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        md_content = re.sub(r'\n\s*\n\s*\n', '\n\n', md_content)
        
        return md_content.strip()

    def convert_file(self, input_path, output_path):
        """Convert a single wiki file to markdown"""
        try:
            with open(input_path, 'r', encoding='utf-8') as file:
                wiki_content = file.read()
            
            md_content = self.convert_content(wiki_content)
            
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(md_content)
            
            return True
        except Exception as e:
            print(f"Error converting {input_path}: {str(e)}")
            return False

def convert_directory(input_dir, output_dir):
    """Convert all .wiki files in a directory to markdown"""
    converter = WikiToMarkdownConverter()
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all .wiki files in input directory
    input_path = Path(input_dir)
    wiki_files = list(input_path.glob('**/*.wiki'))
    
    if not wiki_files:
        print(f"No .wiki files found in {input_dir}")
        return
    
    successful = 0
    failed = 0
    
    for wiki_file in wiki_files:
        # Preserve directory structure in output
        relative_path = wiki_file.relative_to(input_path)
        output_file = output_path / relative_path.with_suffix('.md')
        
        # Create necessary subdirectories
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if converter.convert_file(wiki_file, output_file):
            successful += 1
            print(f"Converted: {relative_path}")
        else:
            failed += 1
    
    print(f"\nConversion complete!")
    print(f"Successfully converted: {successful} files")
    print(f"Failed to convert: {failed} files")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python wiki_to_md.py <input_directory> <output_directory>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        sys.exit(1)
    
    convert_directory(input_dir, output_dir)
