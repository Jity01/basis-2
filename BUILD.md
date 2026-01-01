# Building and Distributing the Package

## Building the Package

### Prerequisites

```bash
pip install build twine
```

### Build Distribution Files

```bash
# Build both wheel and source distribution
python -m build

# This creates:
# - dist/basis-router-0.1.0.tar.gz (source distribution)
# - dist/basis-router-0.1.0-py3-none-any.whl (wheel)
```

## Installing Locally

### Development Mode (Editable Install)

```bash
# From the project root
pip install -e .

# Or with all optional dependencies
pip install -e ".[all]"
```

### Regular Install from Local Build

```bash
# After building
pip install dist/basis-router-0.1.0-py3-none-any.whl
```

## Publishing to PyPI

### Test PyPI (for testing)

```bash
# Upload to test PyPI
python -m twine upload --repository testpypi dist/*

# Install from test PyPI
pip install --index-url https://test.pypi.org/simple/ basis-router
```

### Production PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# Install from PyPI
pip install basis-router
```

## Version Bumping

Update the version in:
- `pyproject.toml` (version field)
- `setup.py` (version field)

Then rebuild and upload.

