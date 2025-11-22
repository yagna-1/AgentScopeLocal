# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.5.x   | :white_check_mark: |
| < 1.5   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to the project maintainers. You can find maintainer contacts in the [AUTHORS](AUTHORS) file or by looking at recent commits.

### What to Include

Please include the following information:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### What to Expect

- Acknowledgment of your email within 48 hours
- Regular updates about our progress
- Notification when the issue is fixed
- Public disclosure coordination

## Security Best Practices

When using AgentScope Local:

1. **Local Database Security**

   - The trace database may contain sensitive prompts and responses
   - Restrict file permissions on `agentscope_traces.db`
   - Do not commit database files to version control

2. **API Keys**

   - Never commit API keys to git
   - Use environment variables for credentials
   - Rotate keys regularly

3. **Web UI Access**

   - By default, web UI binds to localhost only
   - Be cautious when exposing ports in production
   - Use authentication if deploying publicly

4. **Dependencies**
   - Keep dependencies updated
   - Review security advisories for dependencies
   - Use `pip-audit` to check for known vulnerabilities

## Security Updates

Security updates will be released as patch versions (e.g., 1.5.1, 1.5.2) and documented in the [CHANGELOG](CHANGELOG.md).

## Responsible Disclosure

We kindly ask you to:

- Give us reasonable time to address the issue before public disclosure
- Make a good faith effort to avoid privacy violations and destructive behavior
- Not access or modify data that doesn't belong to you

Thank you for helping keep AgentScope Local and our users safe!
