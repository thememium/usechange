# Reporting a Vulnerability

To report a security vulnerability, please email boswell.labs@gmail.com.

We take security seriously and will respond to security reports within 48 hours. Please include as much detail as possible about the vulnerability, including:

- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)

Please do not open public GitHub issues for security reports.

## Supported Versions

Security fixes, when available, are provided for the latest release. If you are unsure, upgrade to the newest version before reporting.

## Disclosure Process

We will confirm receipt of your report and follow up with remediation or mitigation guidance. Coordinated disclosure is welcome.

## Scope and Impact

usechange is a Python CLI for generating changelogs and release notes from git history, and for running release workflows. The following behaviors are relevant when assessing impact:

- **Command execution**: The release workflow invokes local commands such as `uv`, `git`, and `gh` to update versions, commit, tag, and push releases.
- **Network access**: GitHub release sync uses the GitHub API, and may fetch `CHANGELOG.md` from GitHub when not present locally.
- **Credentials**: GitHub release sync can use a token provided via CLI option, environment variables, or the GitHub CLI configuration file.
- **File system access**: usechange reads and writes files like `CHANGELOG.md`, `pyproject.toml`, and `uv.lock` within the target repository.
- **Git metadata**: changelog generation reads commit history, including author names and emails.

## Security Considerations for usechange

- **Command Execution**: Some usechange features execute system commands. Only run commands you trust and review outputs before publishing.
- **Release Automation**: The release workflow will commit and push changes and tags. Verify the repository state before running `usechange release`.
- **GitHub Tokens**: Treat tokens as secrets and avoid logging or sharing them. Prefer scoped tokens where possible.
- **File System Access**: Be cautious when running usechange in directories with sensitive files.

## Security Hall of Fame

We would like to thank the following security researchers for responsibly disclosing security issues to us.

*No security researchers have been added to the hall of fame yet. Will you be the first?*
