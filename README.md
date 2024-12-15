# MCP Git Ingest

A Model Context Protocol (MCP) server that helps read GitHub repository structure and important files.

Inspired by [gitingest](https://gitingest.com/).

## Configuration

{
    "mcpServers": {
        "mcp-git-ingest": {
            "command": "uvx",
            "args": ["--from", "git+https://github.com/adhikasp/mcp-git-ingest", "mcp-git-ingest"],
        }
    }
}

## Usage

```
$ llm read https://github.com/JetBrains/mcp-jetbrains dir structure and determine the important files. How does the code works?

I'll help you explore the GitHub repository for mcp-jetbrains by first examining its directory structure and then reading its important files.

Tool Calls:
  github_directory_structure
  Args:
    repo_url: https://github.com/JetBrains/mcp-jetbrains
   Built mcp-git-ingest @ file:///home/adhikasp/mcp-git-ingest


Now, I'll read the important files to understand how the code works:

Tool Calls:
  github_read_important_files
  Args:
    repo_url: https://github.com/JetBrains/mcp-jetbrains
    file_paths: ['README.md', 'src/index.ts', 'package.json']


Let me break down how this code works:

1. Purpose:
This is a JetBrains MCP (Model Context Protocol) Proxy Server that acts as an intermediary between a client (like Claude Desktop) and JetBrains IDEs.

2. Key Components:
- The main logic is in `src/index.ts`
- It's a TypeScript project using the `@modelcontextprotocol/sdk`
- Uses stdio (standard input/output) for communication

3. Core Functionality:
- Dynamically finds a running JetBrains IDE by:
  a. Checking a specific port if `IDE_PORT` is set in environment
  b. Scanning ports 63342-63352 to find a responsive IDE
  c. Sends requests to the IDE's built-in webserver

4. Key Functions:
- `findWorkingIDEEndpoint()`: Discovers a running JetBrains IDE
- `testListTools()`: Checks if an IDE endpoint is responsive
- `handleToolCall()`: Forwards tool calls to the IDE and returns results

5. Server Capabilities:
- Supports listing available tools
- Allows calling tools on the IDE
- Periodically checks for IDE availability (every 10 seconds)
- Sends notifications if tools list changes

6. Usage:
To use with Claude Desktop, users add a configuration in `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "jetbrains": {
      "command": "npx",
      "args": ["-y", "@jetbrains/mcp-proxy"]
    }
  }
}
```

7. Build & Run:
- Requires Node.js and pnpm
- Build command: `pnpm build`
- Runs as a CLI tool via `npx @jetbrains/mcp-proxy`

The proxy essentially creates a standardized way to interact with JetBrains IDEs, allowing tools like Claude to discover and use IDE-specific capabilities dynamically.

Would you like me to elaborate on any specific aspect of the code or its functionality?
```