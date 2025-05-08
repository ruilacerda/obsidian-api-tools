#!/usr/bin/env python
"""
Basic usage example for the Obsidian API Tools package.
This script demonstrates how to interact with your Obsidian vault.

Before running, make sure to:
1. Install the Obsidian Local REST API plugin
2. Configure an API key
3. Set the OBSIDIAN_API_KEY environment variable or update the API_KEY below
"""

import os
import sys
import time

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from obsidian_api_tools import ObsidianFiles
from obsidian_api_tools.run_dataview_dataviewjs import run_dataviewjs_with_output_note

# API configuration - replace with your own or set environment variables
API_URL = os.environ.get('OBSIDIAN_API_URL', 'http://127.0.0.1:27123')
API_KEY = os.environ.get('OBSIDIAN_API_KEY', '')  # Replace with your API key if not using env vars

if not API_KEY:
    print("Please set your OBSIDIAN_API_KEY environment variable or edit this file")
    sys.exit(1)

def main():
    """Run a basic demonstration of the Obsidian API Tools package."""
    print("==== Obsidian API Tools Basic Demo ====")
    
    # Initialize the API
    obsidian = ObsidianFiles(api_url=API_URL, token=API_KEY)
    
    # Create a test note
    test_note_name = f"Test Note {time.strftime('%Y%m%d_%H%M%S')}.md"
    print(f"\nCreating test note: {test_note_name}")
    
    obsidian._create_or_update_file(test_note_name, f"""---
created: {time.strftime("%Y-%m-%d %H:%M:%S")}
tags: [test, api, python]
---

# API Test Note

This note was created using the Obsidian API Tools package.

## Features
- File operations
- Dataview integration
- API access

""")
    
    # Open the note
    print("Opening the test note in Obsidian...")
    obsidian._open_file(test_note_name)
    
    # Wait a moment for the file to open
    time.sleep(1)
    
    # Get the active file content
    print("\nReading active file content...")
    active_content = obsidian._get_active_file_content()
    print(f"Active file has {len(active_content)} characters")
    
    # Append content to the note
    print("\nAppending content to the note...")
    obsidian._append_content_to_active_file("\n## Added Content\nThis section was added programmatically!")
    
    # Run a DataviewJS script to get tags
    print("\nRunning a DataviewJS script to find notes with tags...")
    tags_script = """
    // Find all notes with tags
    let notes = dv.pages("#test");
    
    // Format the results
    let result = notes.map(page => {
        return {
            filename: page.file.name,
            tags: page.file.tags,
            created: page.file.ctime
        };
    });
    
    return result;
    """
    
    tag_results = run_dataviewjs_with_output_note(obsidian, tags_script)
    
    # Print the results
    if isinstance(tag_results, dict) and 'values' in tag_results:
        print(f"\nFound {len(tag_results['values'])} notes with the #test tag:")
        for note in tag_results['values']:
            print(f"  - {note['filename']} (Tags: {', '.join(note['tags'])})")
    
    # Clean up - delete the test note
    print(f"\nCleaning up - deleting test note: {test_note_name}")
    obsidian._delete_target_file(test_note_name)
    
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()
