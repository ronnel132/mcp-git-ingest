"""GitHub repository analysis tools."""

from fastmcp import FastMCP
import os
import subprocess
from typing import List, Optional
import tempfile
import shutil
from pathlib import Path
import hashlib
import git
import asyncio
from openai import OpenAI
import os
from mcp_git_ingest.consts import DEFAULT_SUMMARY_PROMPT

mcp = FastMCP(
    "GitHub Tools",
    dependencies=[
        "gitpython",
        "openai",
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
    entries = os.listdir(path)
    entries.sort()
    
    for i, entry in enumerate(entries):
        if entry.startswith('.git'):
            continue
            
        is_last = i == len(entries) - 1
        current_prefix = "└── " if is_last else "├── "
        next_prefix = "    " if is_last else "│   "
        
        entry_path = os.path.join(path, entry)
        size = os.path.getsize(entry_path) if os.path.isfile(entry_path) else 0
        size_str = f" ({size:,} bytes)" if size > 0 else ""
        output += prefix + current_prefix + entry + size_str + "\n"
        
        if os.path.isdir(entry_path):
            output += get_directory_tree(entry_path, prefix + next_prefix)
            
    return output

@mcp.tool()
def git_directory_structure(repo_url: str, commit_hash: str = None) -> str:
    """
    Clone a Git repository and return its directory structure in a tree format.
    
    Args:
        repo_url: The URL of the Git repository
        commit_hash: Optional specific commit hash to checkout
        
    Returns:
        A string representation of the repository's directory structure
    """
    try:
        # Clone the repository
        repo_path = clone_repo(repo_url, commit_hash)
        
        # Generate the directory tree
        tree = get_directory_tree(repo_path)
        return tree
            
    except Exception as e:
        return f"Error: {str(e)}"

async def summarize_file(client: OpenAI, content: str, prompt: str) -> str:
    """Summarize file content using DeepSeek API"""
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error summarizing content: {str(e)}"

@mcp.tool()
def git_read_important_files(
    repo_url: str, 
    file_paths: List[str], 
    commit_hash: str = None,
    summarize_threshold: int = 10000,  # Files larger than 10KB will be summarized
    summary_prompt: str = DEFAULT_SUMMARY_PROMPT
) -> dict[str, str]:
    """
    Read the contents of specified files in a given git repository.
    
    Args:
        repo_url: The URL of the Git repository
        file_paths: List of file paths to read (relative to repository root)
        commit_hash: Optional specific commit hash to checkout
        summarize_threshold: Size threshold in bytes above which files will be summarized
        summary_prompt: Custom prompt for the summarization
        
    Returns:
        A dictionary mapping file paths to their contents or summaries
    """
    try:
        # Clone the repository
        repo_path = clone_repo(repo_url, commit_hash)
        results = {}
        files_to_summarize = []
        
        # Initialize DeepSeek client if needed
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        if not deepseek_api_key:
            raise Exception("DEEPSEEK_API_KEY environment variable not set")
        client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")
        
        for file_path in file_paths:
            full_path = os.path.join(repo_path, file_path)
            
            if not os.path.isfile(full_path):
                results[file_path] = f"Error: File not found"
                continue
                
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content.encode('utf-8')) > summarize_threshold:
                        files_to_summarize.append((file_path, content))
                    else:
                        results[file_path] = content
            except Exception as e:
                results[file_path] = f"Error reading file: {str(e)}"
        
        # Summarize large files in parallel
        if files_to_summarize:
            async def process_summaries():
                tasks = [
                    summarize_file(client, content, summary_prompt)
                    for _, content in files_to_summarize
                ]
                summaries = await asyncio.gather(*tasks)
                for (file_path, _), summary in zip(files_to_summarize, summaries):
                    results[file_path] = f"[SUMMARY] {summary}"
            
            asyncio.run(process_summaries())
        
        return results
            
    except Exception as e:
        return {"error": f"Failed to process repository: {str(e)}"}
