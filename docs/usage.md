# Obsidian API Tools - Usage Guide

This guide explains how to use the Obsidian API Tools package to interact with your Obsidian vault programmatically.

## Prerequisites

1. Install and enable the [Local REST API plugin](https://github.com/coddingtonbear/obsidian-local-rest-api) in your Obsidian vault.
2. Generate an API key in the plugin settings.
3. Note the port number (default is 27123).

## Basic Usage

### Initialization

```python
from obsidian_api_tools import ObsidianFiles

# Replace with your own API key
API_URL = 'http://127.0.0.1:27123'
API_KEY = 'your-api-key-here'

obsidian = ObsidianFiles(api_url=API_URL, token=API_KEY)
```

### Working with Files

```python
# Get active file content
content = obsidian._get_active_file_content()
print(content)

# Create a new note
obsidian._create_or_update_file("My Test Note.md", "# Hello World\n\nThis is a test note created with the API.")

# Open a note
obsidian._open_file("My Test Note.md")

# Append content to the active note
obsidian._append_content_to_active_file("\n\nThis line was appended programmatically!")

# Update content of a note
obsidian._create_or_update_file("My Test Note.md", "# Updated Note\n\nThis content has been completely replaced.")

# List files in a folder
files = obsidian._list_files_in_vault("Projects")
for file in files:
    print(file['name'])

# Delete a note
obsidian._delete_target_file("My Test Note.md")
```

## Working with Dataview

### Run a Dataview Query

```python
from obsidian_api_tools.run_dataview_dataviewjs import run_dataview_query

# Run a simple Dataview query
results = run_dataview_query(obsidian, "TABLE file.ctime as Created FROM \"Projects\"")
for item in results:
    print(f"File: {item['filename']}, Created: {item['result']['Created']}")
```

### Run a DataviewJS Script

```python
from obsidian_api_tools.run_dataview_dataviewjs import run_dataviewjs_with_output_note

# Define a DataviewJS script that finds all tasks
script = """
// Find all tasks
let tasks = dv.pages("").file.tasks
    .where(t => !t.completed)
    .sort(t => t.due || "2099-12-31", 'asc');

// Format the results
let result = tasks.map(task => {
    return {
        text: task.text,
        due: task.due ? task.due.toString() : "No date",
        path: task.path
    };
});

return result;
"""

# Execute the script
results = run_dataviewjs_with_output_note(obsidian, script)

# Print the results
if isinstance(results, dict) and 'values' in results:
    for task in results['values']:
        print(f"Task: {task['text']}")
        print(f"Due: {task['due']}")
        print(f"File: {task['path']}")
        print()

# You can also access execution time
if 'execution_time_ms' in results:
    print(f"Script execution time: {results['execution_time_ms']:.2f} ms")
```

## Advanced Usage

### Working with Headings

```python
# Insert content under a specific heading
obsidian._insert_content_of_target_file(
    "My Note.md",
    "This content will be inserted under the specified heading.",
    "My Heading",
    "end"
)

# Insert content under a nested heading
obsidian._insert_content_of_target_file(
    "My Note.md",
    "This content will be inserted under a nested heading.",
    "Chapter 1::Section 2",
    "beginning"
)
```

### Running Obsidian Commands

```python
# List all available commands
commands = obsidian._list_commands()
for cmd in commands:
    print(f"ID: {cmd['id']}, Name: {cmd['name']}")

# Execute a command by ID
obsidian._run_command("app:go-back")
```

### Complex Searching

```python
# Search with JsonLogic query
json_query = {
    "and": [
        {"glob": ["*.md", {"var": "file.name"}]},
        {"in": ["#project", {"var": "tags"}]}
    ]
}
results = obsidian._search_with_query(json_query)

# Search with GUI
results = obsidian._search_with_gui("tag:#project", content_length=150)
```

## Error Handling

Most methods in this package return None on failure and log the error. It's good practice to check for None returns:

```python
result = obsidian._get_target_file_content("non-existent-file.md")
if result is None:
    print("File not found or other error occurred.")
```

## Performance Considerations

- The DataviewJS execution can be resource-intensive for large vaults.
- Consider adding appropriate timeouts and error handling for production use.
- The `run_dataviewjs_with_output_note` function includes execution time metrics to help optimize your scripts.
