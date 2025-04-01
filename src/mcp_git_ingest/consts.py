DEFAULT_SUMMARY_PROMPT = """Perform a detailed analysis of this file to extract the following information:

1. Key Functionality and Purpose
- Main functions and classes
- Core features and capabilities 
- Integration points with other components
- Public APIs and interfaces exposed

2. Configuration and Installation
- Required environment variables
- Configuration file formats and options
- Step-by-step installation instructions
- System prerequisites and dependencies
- Build/compilation requirements

3. Dependencies and Technical Requirements
- External library dependencies with versions
- Operating system compatibility
- Hardware requirements
- Runtime environment needs
- Network/infrastructure requirements

4. Security Analysis
- Authentication/authorization mechanisms
- Data encryption and protection
- Input validation and sanitization
- Known security vulnerabilities
- Access control implementation
- Network security considerations

5. Code Quality Assessment
- Code organization and structure
- Documentation completeness
- Error handling practices
- Testing coverage
- Performance considerations
- Maintainability factors
- Coding standards compliance

6. Network and API Usage
- External API endpoints called
- Network protocols used
- Data transfer patterns
- Rate limiting implementation
- API authentication methods
- Error handling for network calls

7. Tools and Capabilities
- Command-line interfaces
- API endpoints exposed
- Integration capabilities
- Automation features
- Development tools provided
- Plugin/extension systems

8. Development Practices
- Version control usage
- Build automation
- Testing frameworks
- Code review process indicators
- Release management approach
- Documentation practices

9. Critical Vulnerabilities
- Security weaknesses
- Resource leaks
- Race conditions
- Input validation issues
- Authentication bypasses
- Privilege escalation vectors

Format findings under these exact headings. Provide specific examples, code snippets, and detailed explanations where relevant. Note any missing information or areas requiring further investigation."""
