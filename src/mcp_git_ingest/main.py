"""GitHub repository analysis tools."""

from fastmcp import FastMCP
import os
import subprocess
from typing import List
import tempfile
import shutil
from pathlib import Path
import hashlib
import git

mcp = FastMCP(
    "GitHub Tools",
    dependencies=[
        "gitpython",
    ]
)

def clone_repo(repo_url: str, commit_hash: str = None) -> str:
    """Clone a repository and optionally checkout a specific commit. Return the path."""
    repo_hash = hashlib.sha256((repo_url + (commit_hash or "")).encode()).hexdigest()[:12]
    temp_dir = os.path.join(tempfile.gettempdir(), f"github_tools_{repo_hash}")

    if os.path.exists(temp_dir):
        try:
            repo = git.Repo(temp_dir)
            if not repo.bare and repo.remote().url == repo_url:
                if commit_hash:
                    repo.git.checkout(commit_hash)
                return temp_dir
        except:
            shutil.rmtree(temp_dir, ignore_errors=True)

    os.makedirs(temp_dir, exist_ok=True)
    try:
        repo = git.Repo.clone_from(repo_url, temp_dir)
        if commit_hash:
            repo.git.checkout(commit_hash)
        return temp_dir
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise Exception(f"Failed to clone repository: {str(e)}")

def get_directory_tree(path: str, prefix: str = "") -> str:
    """Generate a tree-like directory structure string"""
    output = ""
    entries = sorted(os.listdir(path))
    
    for i, entry in enumerate(entries):
        if entry.startswith('.git'):
            continue
            
        is_last = i == len(entries) - 1
        current_prefix = "└── " if is_last else "├── "
        next_prefix = "    " if is_last else "│   "
        
        entry_path = os.path.join(path, entry)
        size = os.path.getsize(entry_path) if os.path.isfile(entry_path) else 0
        size_str = f" ({size//1000}K)" if size > 1000 else ""

        # Check code files for MCP keywords
        mcp_flag = ""
        CODE_EXTENSIONS = {'.js', '.mjs', '.cjs', '.jsx', '.py', '.pyw', '.pyi', '.go', '.ts', '.tsx', '.d.ts'}
        if os.path.isfile(entry_path) and entry_path.endswith(CODE_EXTENSIONS):
            try:
                with open(entry_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if any(keyword in content for keyword in ["mcp", "mcp.server", "@modelcontextprotocol", 
                                                            "mark3labs/mcp-go", "metoro-io/mcp-golang"]):
                        mcp_flag = " [MCP]"
            except:
                pass  # Skip if file can't be read
                
        output += f"{prefix}{current_prefix}{entry}{size_str}{mcp_flag}\n"
        
        if os.path.isdir(entry_path):
            output += get_directory_tree(entry_path, prefix + next_prefix)
            
    return output

@mcp.tool()
def git_directory_structure(repo_url: str, commit_hash: str = None) -> str:
    """
    Clone a Git repository and return its directory structure in a tree format.
    
    The output includes:
    - File sizes (in KB) for files over 1KB
    - [MCP] flag for code files containing Model Context Protocol-related keywords
        - Scans .js, .mjs, .cjs, .jsx, .py, .pyw, .pyi, .go, .ts, .tsx, and .d.ts files
        - Detects references to MCP packages like @modelcontextprotocol, mark3labs/mcp-go etc.
    
    Args:
        repo_url: The URL of the Git repository
        commit_hash: Optional specific commit hash to checkout
        
    Returns:
        A string representation of the repository's directory structure with size and MCP annotations
    """
    try:
        # Clone the repository
        repo_path = clone_repo(repo_url, commit_hash)
        
        # Generate the directory tree
        tree = get_directory_tree(repo_path)
        return tree
            
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def git_read_important_files(repo_url: str, file_paths: List[str], commit_hash: str = None) -> dict[str, str]:
    """
    Read the contents of specified files in a given git repository.
    
    Args:
        repo_url: The URL of the Git repository
        file_paths: List of file paths to read (relative to repository root)
        commit_hash: Optional specific commit hash to checkout
        
    Returns:
        A dictionary mapping file paths to their contents
    """
    try:
        # Clone the repository
        repo_path = clone_repo(repo_url, commit_hash)
        results = {}
        
        for file_path in file_paths:
            full_path = os.path.join(repo_path, file_path)
            
            # Check if file exists
            if not os.path.isfile(full_path):
                results[file_path] = f"Error: File not found"
                continue
                
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    results[file_path] = f.read()
            except Exception as e:
                results[file_path] = f"Error reading file: {str(e)}"
        
        return results
            
            
    except Exception as e:
        return {"error": f"Failed to process repository: {str(e)}"}
