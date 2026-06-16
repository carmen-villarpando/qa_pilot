---
description: Set up code quality tools (Black, Ruff, Pre-commit) for the project
---

# Setup Code Quality Tools

This workflow sets up comprehensive code quality tools including Black (formatting), Ruff (linting), and Pre-commit hooks to ensure consistent code quality before commits.

## Prerequisites

- Python 3.11+
- uv package manager
- Git repository initialized

## Steps

### 1. Install Development Dependencies

```bash
uv add --dev black ruff pre-commit
```

### 2. Configure Tools

Add configuration to `pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]
```

### 3. Set Up Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
```

### 4. Install Pre-commit Hooks

```bash
uv run pre-commit install
```

### 5. Test Pre-commit Hooks

```bash
# Run on all files
uv run pre-commit run --all-files

# Run on staged files (automatic before commit)
git add .
git commit -m "Test pre-commit hooks"
```

### 6. Set Up GitHub Actions (Optional)

Create `.github/workflows/lint.yml`:

```yaml
name: Lint and Format

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install uv
      uses: astral-sh/setup-uv@v3
      with:
        version: "latest"
    
    - name: Install dependencies
      run: |
        uv sync --dev
    
    - name: Run Ruff
      run: |
        uv run ruff check --output-format=github .
    
    - name: Run Black
      run: |
        uv run black --check --diff .
    
    - name: Run MyPy
      run: |
        uv run mypy app/ --ignore-missing-imports
```

## Usage

### Manual Formatting and Linting

```bash
# Format code with Black
uv run black .

# Lint and fix with Ruff
uv run ruff check --fix .

# Format with Ruff
uv run ruff format .
```

### Pre-commit Workflow

1. Make code changes
2. Stage files: `git add .`
3. Commit: `git commit -m "Your message"`
4. Pre-commit hooks automatically run and fix issues
5. If hooks fail, fix issues and retry commit

### Bypassing Hooks (Not Recommended)

```bash
git commit --no-verify -m "Commit message"
```

## Configuration Details

### Black Configuration

- Line length: 88 characters
- Target Python version: 3.11
- Excludes common build directories

### Ruff Configuration

- Line length: 88 characters
- Target Python version: 3.11
- Enabled rules: E (errors), F (pyflakes), I (imports), N (naming), W (warnings), UP (pyupgrade)
- Ignored: E501 (line too long, handled by Black)

### Pre-commit Hooks

- **trailing-whitespace**: Removes trailing whitespace
- **end-of-file-fixer**: Ensures files end with newline
- **check-yaml**: Validates YAML syntax
- **check-added-large-files**: Prevents large files
- **check-json**: Validates JSON syntax
- **check-merge-conflict**: Detects merge conflict markers
- **debug-statements**: Prevents debug statements in production
- **black**: Formats Python code
- **ruff**: Lints and fixes Python code
- **ruff-format**: Additional formatting

## Troubleshooting

### Common Issues

1. **Pre-commit hook fails**: Run `uv run pre-commit run --all-files` to see all issues
2. **Black formatting issues**: Run `uv run black .` to fix formatting
3. **Ruff errors**: Run `uv run ruff check --fix .` to auto-fix linting issues
4. **Hook installation fails**: Ensure `pre-commit` is installed: `uv add --dev pre-commit`

### Updating Hook Versions

```bash
# Update pre-commit configurations
uv run pre-commit autoupdate

# Reinstall with updated versions
uv run pre-commit install
```

## Benefits

- **Consistent Code Style**: Automatic formatting ensures consistent style
- **Quality Assurance**: Linting catches potential issues before they reach production
- **Developer Experience**: Pre-commit hooks provide immediate feedback
- **CI/CD Integration**: GitHub Actions ensure quality checks in pull requests
- **Team Collaboration**: Standardized tools reduce style debates

## Best Practices

1. **Always use pre-commit hooks** - they prevent poor quality code from being committed
2. **Run tools manually** before committing to understand issues
3. **Configure IDE** to integrate with Black and Ruff for real-time feedback
4. **Update dependencies** regularly to get latest improvements
5. **Review hook output** to understand and learn from issues found
