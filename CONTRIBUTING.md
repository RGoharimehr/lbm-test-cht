# Contributing to LBM-CHT

Thank you for your interest in contributing to the LBM-CHT project!

## Ways to Contribute

1. **Report Bugs**: Open an issue describing the bug, including steps to reproduce
2. **Suggest Features**: Open an issue with your feature proposal
3. **Submit Code**: Fix bugs or implement features via pull requests
4. **Improve Documentation**: Help make the docs clearer and more complete
5. **Add Examples**: Contribute new example cases or validation tests

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/lbm-test-cht.git
cd lbm-test-cht
```

### 2. Create Development Environment

```bash
python -m venv dev_env
source dev_env/bin/activate
pip install -e ".[dev]"
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

## Code Standards

### Python Style

Follow PEP 8 guidelines:
```bash
flake8 src/
black src/
```

### Documentation

- Add docstrings to all functions and classes
- Use Google-style docstrings
- Update README if adding major features

Example docstring:
```python
def my_function(param1, param2):
    """
    Brief description of function.
    
    More detailed description if needed.
    
    Parameters:
    -----------
    param1 : type
        Description of param1
    param2 : type
        Description of param2
        
    Returns:
    --------
    result : type
        Description of return value
    """
    pass
```

### Testing

- Write unit tests for new features
- Ensure all existing tests pass
- Aim for >80% code coverage

Run tests:
```bash
pytest tests/ -v
pytest tests/ --cov=src
```

### Commit Messages

Use clear, descriptive commit messages:
```
Add gyroid smoothing function

- Implement morphological smoothing
- Add test cases
- Update documentation
```

## Pull Request Process

1. **Update Tests**: Ensure all tests pass
2. **Update Documentation**: Add/modify docs as needed
3. **Clean Code**: Run linters and formatters
4. **Create PR**: Submit with clear description
5. **Review**: Address reviewer comments
6. **Merge**: Maintainers will merge when ready

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Added unit tests
- [ ] All tests pass
- [ ] Validated with example cases

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## Areas for Contribution

### High Priority

- [ ] Additional boundary condition implementations
- [ ] Parallel processing support
- [ ] GPU acceleration
- [ ] More validation cases
- [ ] Performance optimizations

### Medium Priority

- [ ] Additional geometry types
- [ ] Interactive visualization
- [ ] Configuration file validation
- [ ] Better error handling
- [ ] Progress bars and logging

### Documentation

- [ ] Tutorial notebooks
- [ ] Video tutorials
- [ ] API reference
- [ ] Theory documentation
- [ ] Best practices guide

## Code Review Guidelines

When reviewing PRs, check:

1. **Correctness**: Does the code do what it claims?
2. **Tests**: Are there adequate tests?
3. **Style**: Does it follow project conventions?
4. **Documentation**: Is it well-documented?
5. **Performance**: Are there obvious inefficiencies?

## Getting Help

- Open an issue for questions
- Join discussions on GitHub
- Check existing issues and PRs

## Code of Conduct

Be respectful and constructive in all interactions. We aim to maintain a welcoming environment for all contributors.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
