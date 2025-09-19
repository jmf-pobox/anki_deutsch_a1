# GitHub Actions Workflows

This directory contains GitHub Actions workflows for continuous integration and testing.

## Workflows

### 1. `ci.yml` - Main CI Pipeline
**Triggers**: Push to `main`/`develop`, Pull Requests
**Jobs**:
- **Lint and Type Check**: Runs ruff linting and mypy type checking
- **Unit Tests**: Runs unit tests with coverage on Python 3.13  
- **Integration Tests**: Runs integration tests (PR to main only)
- **Coverage Report**: Posts coverage report on PRs

### 2. `manual-integration.yml` - Manual Test Runner  
**Triggers**: Manual workflow dispatch
**Options**:
- Run all tests, unit only, integration only, or coverage only
- Useful for testing with API keys or debugging CI issues

## Required GitHub Secrets

To enable integration tests, add these secrets to your GitHub repository:

### AWS Secrets (for Polly audio generation)
```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key  
AWS_DEFAULT_REGION=us-east-1
```

### API Secrets
```
ANTHROPIC_API_KEY=your_anthropic_api_key
PEXELS_API_KEY=your_pexels_api_key
```

## Adding Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact name and value

## Workflow Behavior

### On Push/PR:
- ✅ Linting and type checking always run
- ✅ Unit tests always run (no API keys needed)
- ⚠️  Integration tests only run on PRs to `main` (requires API keys)
- 📊 Coverage reports posted on PRs

### Manual Runs:
- 🎯 Choose specific test type to run
- 🔧 Full access to all test suites with API keys
- 📁 Test artifacts uploaded for analysis

## Local Testing

Before pushing, test locally:
```bash
# Test what CI will run
hatch run lint                # Linting
hatch run type               # Type checking  
hatch run test-unit          # Unit tests
hatch run test-integration   # Integration tests (needs API keys)
hatch run test-cov          # Coverage report
```

## Coverage Requirements

- **Current Coverage**: 73.84% (must not decrease)
- **Target Coverage**: 85%+
- **Quality Gate**: Coverage decreases will be flagged in PR comments

## Troubleshooting

### Integration Test Failures
- Check API key configuration in GitHub secrets
- Verify AWS credentials and region
- Integration test failures don't block PRs (unit tests must still pass)

### Coverage Issues  
- Run `hatch run test-cov` locally to debug
- Check `htmlcov/index.html` for detailed coverage report
- Add tests for uncovered code paths

### Local vs CI Differences
- CI uses clean environment - test with fresh hatch environment
- API keys may behave differently in CI environment
- File paths and permissions may differ on GitHub runners