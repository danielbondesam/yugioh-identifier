# Contributing Guide

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

Make commits in logical chunks:

```bash
git add path/to/files
git commit -m "clear description of changes"
```

### 3. Test Your Changes

```bash
# Backend
cd backend
python test_pipeline.py path/to/test_image.jpg

# Frontend
cd frontend
npm test
```

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
# Create PR on GitHub
```

## Code Style

### Python (Backend)

- Follow PEP 8
- Use type hints where possible
- Add docstrings to functions
- Max line length: 100 characters

Example:
```python
def process_image(image: np.ndarray, width: int = 400) -> np.ndarray:
    """
    Process image for OCR.
    
    Args:
        image: Input image array
        width: Output width
        
    Returns:
        Processed image array
    """
    pass
```

### JavaScript (Frontend)

- Use functional components and hooks
- Props should be destructured
- Use meaningful variable names
- Add JSDoc comments

Example:
```javascript
/**
 * Camera capture component with ROI overlay.
 * @param {Object} props
 * @param {Function} props.onCapture - Callback when image captured
 * @param {boolean} props.loading - Loading state
 * @returns {JSX.Element}
 */
function CameraCapture({ onCapture, loading }) {
  // ...
}
```

## Architecture Guidelines

### Backend

- Keep models and business logic separate
- Use dependency injection
- Handle errors gracefully
- Log important operations

### Frontend

- One component per file
- Use custom hooks for shared logic
- Separate styles from components
- Handle loading and error states

## Testing

### Backend

```bash
# Run all tests
python -m pytest

# Test specific file
python -m pytest test_image_processor.py

# With coverage
python -m pytest --cov=app
```

### Frontend

```bash
# Run tests
npm test

# With coverage
npm test -- --coverage
```

## Performance

### Backend

- Target <500ms end-to-end
- Profile with timing decorators
- Use caching for database
- Monitor memory usage

### Frontend

- Lazy load components
- Memoize expensive calculations
- Optimize images
- Monitor bundle size

## Documentation

- Update README.md if features change
- Add comments for complex logic
- Document API changes
- Update CLAUDE.md for architecture changes

## Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (no logic change)
- `refactor`: Refactoring
- `test`: Adding tests
- `chore`: Maintenance

Example:
```
feat: add batch identification endpoint

- Add POST /identify_batch endpoint
- Support multiple images in single request
- Return array of results

Closes #123
```

## Release Process

1. Update version in package.json and setup.py
2. Update CHANGELOG
3. Tag release: `git tag v1.0.0`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub Release

## Reporting Issues

Include:
- Clear description of problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, Python/Node version)
- Relevant logs

## Questions?

- Check CLAUDE.md for architecture
- Read API_TESTING.md for API usage
- Review existing code for patterns
