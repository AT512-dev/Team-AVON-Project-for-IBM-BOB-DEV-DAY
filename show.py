import os

def print_project_tree(start_directory="."):
    print("\n===================================================")
    print("CURRENT WORKSPACE FILES")
    print("===================================================")
    
    # Folders we want to ignore so the terminal stay clean
    ignore_folders = {
        '.git', '__pycache__', 'node_modules', 
        '.next', '.pytest_cache', '.venv', 'venv'
    }
    
    for root, dirs, files in os.walk(start_directory):
        # Filter out ignored directories in-place
        dirs[:] = [d for d in dirs if d not in ignore_folders]
        
        # Calculate indentation level based on directory depth
        depth = root.replace(start_directory, '').count(os.sep)
        indent = '    ' * depth
        
        # Print the current folder name
        folder_name = os.path.basename(root)
        if folder_name and folder_name not in ignore_folders:
            print(f"{indent}📁 {folder_name}/")
        elif not folder_name:
            print("📁 root/")
            
        # Print the files inside this folder
        file_indent = '    ' * (depth + 1)
        for file in files:
            print(f"{file_indent}📄 {file}")
            
    print("===================================================\n")

if __name__ == "__main__":
    print_project_tree()