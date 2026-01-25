# 🤝 Contributing Guide

Thank you for your interest in contributing to NullSec Tools! This guide will help you get started.

---

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Follow responsible disclosure for security issues
- Keep discussions professional

---

## Ways to Contribute

### 🐛 Report Bugs
- Search existing issues first
- Include OS, version, and steps to reproduce
- Provide error messages and logs

### 💡 Suggest Features
- Check if feature already exists or is planned
- Explain the use case clearly
- Consider security implications

### 📝 Improve Documentation
- Fix typos and clarify confusing sections
- Add examples and use cases
- Translate documentation

### 🔧 Submit Code
- Bug fixes
- New tools
- Performance improvements
- Test coverage

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/nullsec-tools.git
cd nullsec-tools
git remote add upstream https://github.com/bad-antics/nullsec-tools.git
```

### 2. Create Branch

```bash
git checkout -b feature/my-new-feature
# or
git checkout -b fix/bug-description
```

### 3. Set Up Environment

```bash
# Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Go
cd go && go mod download

# Rust
cd rust && cargo build
```

### 4. Run Tests

```bash
# Python
pytest tests/ -v

# Go
go test ./...

# Rust
cargo test
```

---

## Coding Standards

### Python
- Follow PEP 8 style guide
- Use type hints
- Document functions with docstrings
- Run `black` and `flake8` before committing

```python
def scan_ports(
    target: str,
    ports: list[int],
    timeout: float = 1.0
) -> dict[int, str]:
    """
    Scan TCP ports on target host.
    
    Args:
        target: IP address or hostname
        ports: List of ports to scan
        timeout: Connection timeout in seconds
    
    Returns:
        Dictionary mapping port numbers to status
    """
    ...
```

### Go
- Follow Go conventions (`gofmt`)
- Use meaningful variable names
- Handle errors explicitly
- Add comments for exported functions

```go
// ScanPorts scans TCP ports on the target host.
// Returns a map of port numbers to their status.
func ScanPorts(target string, ports []int, timeout time.Duration) (map[int]string, error) {
    ...
}
```

### Rust
- Follow Rust conventions (`rustfmt`)
- Use `clippy` for linting
- Document public APIs
- Handle errors with Result types

```rust
/// Scans TCP ports on the target host.
///
/// # Arguments
/// * `target` - IP address or hostname
/// * `ports` - Slice of ports to scan
/// * `timeout` - Connection timeout
///
/// # Returns
/// HashMap of port numbers to status strings
pub fn scan_ports(
    target: &str,
    ports: &[u16],
    timeout: Duration,
) -> Result<HashMap<u16, String>, ScanError> {
    ...
}
```

### C
- Follow K&R style
- Use meaningful names
- Check return values
- Free allocated memory

```c
/**
 * Parse a log file and extract entries matching the filter.
 *
 * @param filename Path to log file
 * @param filter Filter string (NULL for all entries)
 * @param entries Output array of log entries
 * @return Number of entries found, -1 on error
 */
int parse_log(const char *filename, const char *filter, log_entry_t **entries);
```

---

## Commit Messages

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

```
feat(portscan): add UDP scanning support

- Implement UDP probe packets
- Add --udp flag
- Update documentation

Closes #42
```

```
fix(hashcrack): handle bcrypt cost > 12

Previously crashed on high-cost bcrypt hashes.
Now correctly handles cost factors up to 31.

Fixes #87
```

---

## Pull Request Process

### 1. Update Your Branch

```bash
git fetch upstream
git rebase upstream/main
```

### 2. Run All Tests

```bash
# Run full test suite
./scripts/test-all.sh

# Or individually
pytest tests/ -v
cd go && go test ./...
cd rust && cargo test
```

### 3. Update Documentation

- Update README if adding new tool
- Add wiki page for new features
- Update man pages if applicable

### 4. Create Pull Request

- Use descriptive title
- Reference related issues
- Include screenshots/examples if applicable
- Ensure CI passes

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
How was this tested?

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code follows style guide
- [ ] Commits are signed
```

---

## Adding a New Tool

### 1. Create Tool Structure

```bash
# Python tool
mkdir -p tools/python/my_tool
touch tools/python/my_tool/__init__.py
touch tools/python/my_tool/main.py
touch tools/python/my_tool/README.md

# Go tool
mkdir -p go/cmd/mytool
touch go/cmd/mytool/main.go

# Rust tool
cargo new --bin rust/mytool
```

### 2. Implement Core Functionality

- Follow existing tool patterns
- Use shared libraries where possible
- Implement proper error handling
- Add progress indicators for long operations

### 3. Add Tests

```bash
# Python
touch tests/test_my_tool.py

# Go
touch go/cmd/mytool/main_test.go

# Rust
# Tests go in src/main.rs or tests/
```

### 4. Add Documentation

- Tool README with usage examples
- Wiki page with detailed options
- Update main README tool list

### 5. Add to Build System

- Update `setup.py` or `pyproject.toml`
- Update `go.mod` if needed
- Update `Makefile`

---

## Security Considerations

### Responsible Disclosure
- Do not include real exploits that could be misused
- Tools should be for defensive/authorized use only
- Add appropriate warnings and disclaimers

### Code Security
- Validate all user input
- Avoid command injection
- Use secure defaults
- Don't log sensitive data

---

## Getting Help

- Open an issue for questions
- Join discussions on GitHub
- Check existing documentation

---

## Recognition

Contributors are recognized in:
- README contributors section
- Release notes
- GitHub contributors page

Thank you for helping make NullSec Tools better! 🙏
