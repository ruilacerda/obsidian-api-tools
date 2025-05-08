#!/usr/bin/env python
# Fixed Obsidian DataviewJS Runner with Output Note - Enhanced with Execution Time

from .obsidian_rest_api import ObsidianFiles
import time
import json
import re
import uuid
import os

def run_dataview_query(obsidian, query):
    """Run a standard Dataview query.
    
    Args:
        obsidian (ObsidianFiles): An initialized ObsidianFiles instance
        query (str): The Dataview query to execute
        
    Returns:
        The results of the query execution
    """
    print(f"Executing Dataview query: {query}")
    results = obsidian._search_with_query(query)
    return results

def run_dataviewjs_with_output_note(obsidian, script):
    """Run a DataviewJS script that writes results to another note.
    
    This uses a two-note approach:
    1. A script note that executes the DataviewJS and writes results to another note
    2. An output note that stores the results in plain text format
    
    Args:
        obsidian (ObsidianFiles): An initialized ObsidianFiles instance
        script (str): The DataviewJS script to execute
        
    Returns:
        The results of the script execution
    """
    # Create unique IDs for our temporary notes
    temp_id = uuid.uuid4().hex[:8]
    script_file = f"temp_script_{temp_id}.md"
    output_file = f"temp_output_{temp_id}.md"
    
    print(f"Creating output file: {output_file}")
    # First create an empty output file
    obsidian._create_or_update_file(output_file, f"""---
created: {time.strftime("%Y-%m-%d %H:%M:%S")}
---

# DataviewJS Output

Results will appear below:

```
Waiting for results...
```

""")
    
    print(f"Creating script file: {script_file}")
    # Create the script file that will execute the DataviewJS and write to the output file
    # Avoid using template literals with backticks in the JavaScript to prevent syntax errors
    script_content = f"""---
created: {time.strftime("%Y-%m-%d %H:%M:%S")}
---

# DataviewJS Script

This note executes a DataviewJS query and writes results to {output_file}

```dataviewjs
try {{
    // Start timing the execution
    const startTime = performance.now();
    
    // Execute the script
    const scriptResults = (function() {{
{script}
    }})();
    
    // Calculate execution time in milliseconds
    const endTime = performance.now();
    const executionTime = endTime - startTime;
    
    // Convert results to JSON
    const resultsJson = JSON.stringify(scriptResults, null, 2);
    
    // Show results in this note
    dv.paragraph("✅ Script executed successfully!");
    dv.paragraph("⏱️ Execution time: " + executionTime.toFixed(2) + " ms");
    
    if (Array.isArray(scriptResults)) {{
        if (scriptResults.length > 0 && typeof scriptResults[0] === 'object') {{
            dv.table(scriptResults);
        }} else {{
            dv.list(scriptResults);
        }}
    }}
    
    // Create the output content with execution time
    const outputContent = "---\\ncreated: {time.strftime("%Y-%m-%d %H:%M:%S")}\\n---\\n\\n# DataviewJS Results\\n\\n⏱️ Execution time: " + executionTime.toFixed(2) + " ms\\n\\n```json\\n" + resultsJson + "\\n```\\n";
    
    // Write to the output file
    app.vault.adapter.write("{output_file}", outputContent);
    dv.paragraph("Results written to: [{output_file}]({output_file})");
}} catch (e) {{
    dv.paragraph("❌ Error: " + e.message);
    
    // Write error to output file without template literals
    const errorContent = "---\\ncreated: {time.strftime("%Y-%m-%d %H:%M:%S")}\\n---\\n\\n# DataviewJS Error\\n\\n```\\n" + e.message + "\\n" + (e.stack || "") + "\\n```\\n";
    
    app.vault.adapter.write("{output_file}", errorContent);
    dv.paragraph("Error details written to: [{output_file}]({output_file})");
}}
```

"""
    
    obsidian._create_or_update_file(script_file, script_content)
    
    # Open the script file to execute it
    print("Opening script file in Obsidian...")
    obsidian._open_file(script_file)
    
    # Wait for script to execute and write to output file
    print("Waiting for script execution (100 miliseconds)...")
    time.sleep(0.1)
    
    # Now read the output file which should contain the results in plain text
    print(f"Reading results from output file: {output_file}")
    
    try:
        response = obsidian._send_request("GET", f"/vault/{output_file}")
        
        if response.status_code != 200:
            print(f"Error retrieving output file: status code {response.status_code}")
            return {"error": f"Failed to retrieve output file: {response.status_code}"}
        
        content = response.text
        print(f"Successfully retrieved output content ({len(content)} characters)")
        
        # Extract execution time if available
        exec_time_pattern = r'⏱️ Execution time: (\d+\.\d+) ms'
        exec_time_match = re.search(exec_time_pattern, content)
        execution_time = float(exec_time_match.group(1)) if exec_time_match else None
        
        if execution_time:
            print(f"Execution time: {execution_time} ms")
        
        # Extract JSON from the code block
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        json_match = re.search(json_pattern, content, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1).strip()
            print(f"Found JSON result ({len(json_str)} characters)")
            
            try:
                result = json.loads(json_str)
                print("Successfully parsed JSON results")
                
                # Handle Dataview's container format if present
                if isinstance(result, dict) and 'values' in result and isinstance(result['values'], list):
                    print("Detected Dataview container format - extracting 'values' property")
                    result = result['values']
                
                # Add execution time to result if available
                if execution_time:
                    if isinstance(result, dict):
                        result['execution_time_ms'] = execution_time
                    elif isinstance(result, list) and result:
                        # For list results, we'll return a dict with the list and execution time
                        result = {
                            'values': result,
                            'execution_time_ms': execution_time
                        }
                
                # Clean up temporary files on success
                print(f"Cleaning up temporary files: {script_file} and {output_file}")
                try:
                    # Use the correct method from the class
                    obsidian._delete_target_file(script_file)
                    obsidian._delete_target_file(output_file)
                    print("Temporary files deleted successfully")
                except Exception as e:
                    print(f"Warning: Failed to delete temporary files: {e}")
                
                return result
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                return {"error": f"Failed to parse JSON: {e}", "json": json_str[:200] + "..."}
        else:
            # Check if there was an error
            error_pattern = r'```\s*(.*?)\s*```'
            error_match = re.search(error_pattern, content, re.DOTALL)
            if error_match:
                error = error_match.group(1).strip()
                print(f"Script error: {error}")
                return {"error": error}
            else:
                print("No JSON or error found in output file")
                print(f"Content preview: {content[:200]}...")
                return {"error": "No results found in output file"}
    
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
    
    finally:
        # Check if files still exist by trying to get their content
        try:
            script_response = obsidian._send_request("GET", f"/vault/{script_file}")
            output_response = obsidian._send_request("GET", f"/vault/{output_file}")
            
            script_exists = script_response.status_code == 200
            output_exists = output_response.status_code == 200
            
            if script_exists or output_exists:
                existing_files = []
                if script_exists:
                    existing_files.append(script_file)
                if output_exists:
                    existing_files.append(output_file)
                    
                print(f"Note: Temporary files {', '.join(existing_files)} still exist and have been kept for error inspection")
            else:
                print("All temporary files have been cleaned up")
        except Exception as e:
            print(f"Could not verify if temporary files still exist: {e}")

def run_examples(api_url, api_key):
    """Run example queries to demonstrate the functionality.
    
    Args:
        api_url (str): The URL for the Obsidian Local REST API
        api_key (str): The API key for authentication
    """
    # Initialize the ObsidianFiles class
    obsidian = ObsidianFiles(api_url=api_url, token=api_key)
    
    print("==== Obsidian DataviewJS Runner ====")
    
    # Example 1: Standard Dataview query
    print("\n--- Running standard Dataview query ---")
    dataview_results = run_dataview_query(obsidian, "TABLE tags FROM \"\" WHERE file.tags")
    
    if dataview_results:
        print(f"\nFound {len(dataview_results)} files with tags:")
        for item in dataview_results[:3]:  # Show first 3 results
            if 'filename' in item and 'result' in item:
                print(f"📄 {item['filename']}")
                tags = item['result'].get('tags', [])
                if tags:
                    print(f"  Tags: {', '.join(str(t) for t in tags) if isinstance(tags, list) else tags}")
                print()
    
    # Example 2: DataviewJS query for folder statistics
    print("\n--- Running DataviewJS query for folder statistics ---")
    folder_script = """
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
    
    folder_results = run_dataviewjs_with_output_note(obsidian, folder_script)
    
    # Get execution time if available
    execution_time = None
    folder_items = folder_results
    
    if isinstance(folder_results, dict):
        if 'execution_time_ms' in folder_results:
            execution_time = folder_results['execution_time_ms']
        if 'values' in folder_results:
            folder_items = folder_results['values']
    
    # Print results with execution time if available
    if execution_time is not None:
        print(f"\n📁 Folder Distribution (Execution time: {execution_time:.2f} ms):")
    else:
        print("\n📁 Folder Distribution:")
        
    if isinstance(folder_items, list):
        for item in folder_items:
            if isinstance(item, dict) and 'folder' in item and 'count' in item:
                print(f"  {item['folder']}: {item['count']} files")
                if 'sampleFiles' in item:
                    for file in item['sampleFiles']:
                        print(f"    └─ {file}")
    elif isinstance(folder_results, dict) and 'error' in folder_results:
        print(f"Error: {folder_results['error']}")
    else:
        print(f"Unexpected result: {folder_results}")
    
    # Example 3: DataviewJS for link analysis
    print("\n--- Running DataviewJS query for link analysis ---")
    link_script = """
    // Get all markdown files
    let pages = dv.pages("");
    
    // Calculate link statistics
    let result = pages.map(page => {
        return {
            filename: page.file.name,
            outlinks: page.file.outlinks ? page.file.outlinks.length : 0,
            inlinks: page.file.inlinks ? page.file.inlinks.length : 0,
            totalLinks: (page.file.outlinks ? page.file.outlinks.length : 0) + 
                       (page.file.inlinks ? page.file.inlinks.length : 0)
        };
    })
    .sort((a, b) => b.totalLinks - a.totalLinks)  // Sort by total links
    .filter(page => page.totalLinks > 0)  // Only include notes with links
    .slice(0, 10);  // Top 10 results
    
    return result;
    """
    
    link_results = run_dataviewjs_with_output_note(obsidian, link_script)
    
    # Get execution time if available
    execution_time = None
    link_items = link_results
    
    if isinstance(link_results, dict):
        if 'execution_time_ms' in link_results:
            execution_time = link_results['execution_time_ms']
        if 'values' in link_results:
            link_items = link_results['values']
    
    # Print results with execution time if available
    if execution_time is not None:
        print(f"\n🔗 Most Connected Notes (Execution time: {execution_time:.2f} ms):")
    else:
        print("\n🔗 Most Connected Notes:")
    
    if isinstance(link_items, list):
        for i, item in enumerate(link_items):
            if isinstance(item, dict) and 'filename' in item:
                print(f"{i+1}. {item['filename']}")
                print(f"   Outgoing links: {item.get('outlinks', 0)}")
                print(f"   Incoming links: {item.get('inlinks', 0)}")
                print(f"   Total links: {item.get('totalLinks', 0)}")
    elif isinstance(link_results, dict) and 'error' in link_results:
        print(f"Error: {link_results['error']}")
    else:
        print(f"Unexpected result: {link_results}")

# For command-line usage
if __name__ == "__main__":
    # You can replace these values with your own or use environment variables
    API_URL = os.environ.get('OBSIDIAN_API_URL', 'http://127.0.0.1:27123')
    API_KEY = os.environ.get('OBSIDIAN_API_KEY', '')
    
    if not API_KEY:
        print("Please set your OBSIDIAN_API_KEY environment variable or edit this file")
        sys.exit(1)
        
    run_examples(API_URL, API_KEY)