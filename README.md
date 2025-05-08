# Obsidian API Tools

A Python toolkit for programmatically interacting with your Obsidian vault using the [Obsidian Local REST API plugin](https://github.com/coddingtonbear/obsidian-local-rest-api).

## Features

- Execute DataviewJS queries and capture results programmatically
- Measure execution time of your Dataview queries
- Interact with notes programmatically (read, write, update, delete)
- Search your vault with complex queries
- Run Obsidian commands from Python
- Handle active files and target specific notes

## Requirements

- Obsidian with the [Local REST API plugin](https://github.com/coddingtonbear/obsidian-local-rest-api) installed and configured
- Python 3.6+
- Requests library

## Installation

1. First, install the Obsidian Local REST API plugin in your Obsidian vault:
   - Open Obsidian
   - Go to Settings -> Community Plugins
   - Turn off Safe Mode
   - Click Browse and search for "Local REST API"
   - Install the plugin and enable it

2. Configure the plugin with an API key and note the port number (default is 27123)

3. Install this package:
   ```bash
   # Not yet published to PyPI - install from GitHub
   pip install git+https://github.com/yourusername/obsidian-api-tools.git
   ```

## Quick Start

```python
from obsidian_api_tools import ObsidianFiles

# Initialize the API - replace with your own API key
API_URL = 'http://127.0.0.1:27123'
API_KEY = 'your-api-key-here'

obsidian = ObsidianFiles(api_url=API_URL, token=API_KEY)

# Get the content of the currently active file
active_content = obsidian._get_active_file_content()
print(active_content)

# Run a Dataview query
results = obsidian._search_with_query("TABLE tags FROM \"\" WHERE file.tags")
print(f"Found {len(results)} files with tags")

# Create a new note
obsidian._create_or_update_file("My New Note.md", "# Hello World\n\nThis note was created programmatically!")

# Open a note
obsidian._open_file("My New Note.md")
```

## Running DataviewJS

```python
from obsidian_api_tools.run_dataview_dataviewjs import run_dataviewjs_with_output_note

# Define a DataviewJS script
script = """
// Get all markdown files
let pages = dv.pages("");

// Group by folder
let folderGroups = {};
for (let page of pages) {
    let folder = page.file.folder || "Root";
    if (!folderGroups[folder]) {
        folderGroups[folder] = [];
    }
    folderGroups[folder].push(page.file.name);
}

// Create a folder summary
let result = Object.entries(folderGroups).map(([folder, files]) => {
    return {
        folder: folder,
        count: files.length,
        sampleFiles: files.slice(0, 3)  // Just show 3 files per folder
    };
}).sort((a, b) => b.count - a.count);  // Sort by count

return result;
"""

# Execute the script
results = run_dataviewjs_with_output_note(script)

# Display results with execution time
if isinstance(results, dict) and 'execution_time_ms' in results:
    print(f"Execution time: {results['execution_time_ms']:.2f} ms")
    
if isinstance(results, dict) and 'values' in results:
    for item in results['values']:
        print(f"{item['folder']}: {item['count']} files")
```

## Security Note

This library interacts with your Obsidian vault directly. Always keep your API key secure and be cautious with scripts that modify your notes. It's recommended to back up your vault before running automated scripts.

## License

MIT License
