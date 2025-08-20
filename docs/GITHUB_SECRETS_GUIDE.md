# GitHub Secrets and CI/CD Environment Configuration Guide

## Executive Summary

This guide provides the **architectural design and implementation strategy** for securely managing API keys and environment variables in the Anki German Language Deck Generator's GitHub Actions CI/CD pipeline. It ensures **zero quality degradation** while enabling both unit tests (mocked services) and integration tests (real API calls) to run correctly in CI.

## Current Architecture Analysis

### Problem Statement
- **CI Failure**: Tests fail due to missing AWS region configuration and API credentials
- **Service Initialization**: `boto3.client("polly")` requires AWS region at initialization time
- **Test Separation**: 667 unit tests should use mocks, 24 integration tests need real credentials
- **Security Requirements**: No secrets in code, logs, or version control

### Root Cause
The `AudioService` class initializes boto3 client in `__init__` method (line 89), which triggers immediate AWS credential and region checks even when services should be mocked for unit tests.

## Recommended Solution Architecture

### 1. GitHub Secrets Configuration

#### Repository Secrets Setup (User Action Required)
Navigate to: `Settings → Secrets and variables → Actions`

**Required Secrets:**
```yaml
AWS_ACCESS_KEY_ID       # AWS access key for Polly service
AWS_SECRET_ACCESS_KEY   # AWS secret key for Polly service
PEXELS_API_KEY         # Pexels API key for image service
ANTHROPIC_API_KEY      # Anthropic API key (optional)
```

**Environment Variables (Non-Secret):**
These can be defined directly in the workflow file:
```yaml
AWS_DEFAULT_REGION: eu-central-1  # Or your preferred region
```

### 2. CI/CD Workflow Architecture

#### Modified `.github/workflows/ci.yml`

```yaml
name: Quality Gates CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  # Non-secret environment variables
  AWS_DEFAULT_REGION: eu-central-1
  PYTHONUNBUFFERED: 1

jobs:
  # STAGE 1: Unit Tests (No External Services)
  unit-tests:
    name: Unit Tests & Quality Gates
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"
    
    - name: Install Hatch
      run: pip install hatch
    
    - name: MyPy Type Check (ZERO errors allowed)
      run: |
        echo "🔍 Running MyPy --strict type checking..."
        hatch run type
        if [ $? -ne 0 ]; then
          echo "❌ FAILED: MyPy errors detected. NO MERGE ALLOWED."
          exit 1
        fi
        echo "✅ SUCCESS: MyPy type checking passed - zero errors found"
    
    - name: Ruff Linting (ZERO violations allowed)
      run: |
        echo "🔍 Running Ruff linting checks..."
        hatch run ruff check --fix
        if [ $? -ne 0 ]; then
          echo "❌ FAILED: Ruff violations detected. NO MERGE ALLOWED."
          exit 1
        fi
        echo "✅ SUCCESS: Ruff linting passed - zero violations found"
    
    - name: Code Formatting Check
      run: |
        echo "🔍 Checking code formatting..."
        hatch run format
        if ! git diff --exit-code; then
          echo "❌ FAILED: Code formatting issues detected. NO MERGE ALLOWED."
          exit 1
        fi
        echo "✅ SUCCESS: Code formatting is correct"
    
    - name: Unit Test Suite (ALL must pass)
      env:
        # Provide minimal env vars to prevent initialization errors
        AWS_DEFAULT_REGION: ${{ env.AWS_DEFAULT_REGION }}
        # Mock credentials for service initialization (never used)
        AWS_ACCESS_KEY_ID: mock-key-for-unit-tests
        AWS_SECRET_ACCESS_KEY: mock-secret-for-unit-tests
      run: |
        echo "🔍 Running full unit test suite..."
        hatch run test-unit
        if [ $? -ne 0 ]; then
          echo "❌ FAILED: Unit tests failing. NO MERGE ALLOWED."
          exit 1
        fi
        echo "✅ SUCCESS: All unit tests passed"
    
    - name: Coverage Check (Must maintain ≥73%)
      env:
        AWS_DEFAULT_REGION: ${{ env.AWS_DEFAULT_REGION }}
        AWS_ACCESS_KEY_ID: mock-key-for-unit-tests
        AWS_SECRET_ACCESS_KEY: mock-secret-for-unit-tests
      run: |
        echo "🔍 Running test coverage analysis..."
        hatch run test-unit-cov --cov-fail-under=73
        if [ $? -ne 0 ]; then
          echo "❌ FAILED: Test coverage below 73%. NO MERGE ALLOWED."
          exit 1
        fi
        echo "✅ SUCCESS: Test coverage maintained at ≥73%"
    
    - name: Final Verification
      env:
        AWS_DEFAULT_REGION: ${{ env.AWS_DEFAULT_REGION }}
        AWS_ACCESS_KEY_ID: mock-key-for-unit-tests
        AWS_SECRET_ACCESS_KEY: mock-secret-for-unit-tests
      run: |
        echo "🔍 Running final verification check..."
        hatch run type && hatch run test-unit
        if [ $? -ne 0 ]; then
          echo "❌ FAILED: Final verification failed. NO MERGE ALLOWED."
          exit 1
        fi
        echo "✅ SUCCESS: All quality gates passed! Ready for merge."

  # STAGE 2: Integration Tests (Real External Services)
  integration-tests:
    name: Integration Tests (Live APIs)
    runs-on: ubuntu-latest
    needs: unit-tests  # Only run after unit tests pass
    # Make this job optional for external contributors
    if: github.event_name == 'push' || github.event.pull_request.head.repo.full_name == github.repository
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"
    
    - name: Install Hatch
      run: pip install hatch
    
    - name: Run Integration Tests
      env:
        # Real credentials from GitHub Secrets
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        AWS_DEFAULT_REGION: ${{ env.AWS_DEFAULT_REGION }}
        PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      run: |
        echo "🔍 Running integration tests with live APIs..."
        # Only run if secrets are available
        if [ -z "$AWS_ACCESS_KEY_ID" ]; then
          echo "⚠️  WARNING: Skipping integration tests - AWS credentials not configured"
          echo "ℹ️  This is expected for external contributors"
          exit 0
        fi
        
        hatch run test-integration
        if [ $? -ne 0 ]; then
          echo "❌ FAILED: Integration tests failing"
          exit 1
        fi
        echo "✅ SUCCESS: All integration tests passed"
```

### 3. Test Infrastructure Improvements

#### A. Service Initialization Pattern (Lazy Loading)

**Current Problem:** Services initialize immediately in `__init__`, requiring credentials even for mocked tests.

**Solution:** Implement lazy initialization pattern for external services.

```python
# src/langlearn/services/audio.py
class AudioService:
    """Service for generating audio files using AWS Polly."""
    
    def __init__(
        self,
        output_dir: str = "audio",
        voice_id: VoiceIdType = "Daniel",
        language_code: LanguageCodeType = "de-DE",
        speech_rate: int = 75,
    ) -> None:
        """Initialize the AudioService."""
        self.output_dir = Path(output_dir)
        self.voice_id = voice_id
        self.language_code = language_code
        self.speech_rate = speech_rate
        self.output_dir.mkdir(exist_ok=True)
        
        # Lazy initialization - client created on first use
        self._client: PollyClient | None = None
        
        logger.info(
            "AudioService initialized with voice_id=%s, language_code=%s, "
            "speech_rate=%d",
            voice_id,
            language_code,
            speech_rate,
        )
    
    @property
    def client(self) -> PollyClient:
        """Lazy load the Polly client on first access."""
        if self._client is None:
            self._client = boto3.client("polly")
        return self._client
    
    def generate_audio(self, text: str, filename: str) -> Path:
        """Generate audio file from text."""
        # Client is only created when this method is actually called
        response = self.client.synthesize_speech(...)
        # ... rest of implementation
```

#### B. Test Fixture for Service Mocking

Create a centralized test fixture for proper service mocking:

```python
# tests/conftest.py
import os
import pytest
from unittest.mock import Mock, patch

@pytest.fixture(autouse=True)
def mock_aws_for_unit_tests(request):
    """Automatically mock AWS services for unit tests."""
    # Skip for integration tests
    if "live" in request.keywords:
        yield
        return
    
    # Set mock environment variables if not present
    if not os.environ.get("AWS_DEFAULT_REGION"):
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    
    # Mock boto3 client creation
    with patch("boto3.client") as mock_client:
        mock_polly = Mock()
        mock_client.return_value = mock_polly
        yield mock_polly

@pytest.fixture
def mock_media_service():
    """Provide a fully mocked MediaService for tests."""
    from langlearn.protocols import MediaServiceProtocol
    
    service = Mock(spec=MediaServiceProtocol)
    service.generate_audio.return_value = Path("/mock/audio.mp3")
    service.fetch_image.return_value = Path("/mock/image.jpg")
    return service
```

### 4. Security Best Practices

#### A. Secret Access Control
- **Repository Secrets**: Only accessible to workflows in the repository
- **Environment Secrets**: Create separate environments (staging, production) with different secret sets
- **Branch Protection**: Require PR approval before secrets are accessible

#### B. Secret Masking
GitHub automatically masks secrets in logs, but follow these practices:
- Never echo or print secret values
- Use `::add-mask::` command for derived values
- Validate secrets exist before use

#### C. Least Privilege Principle
- Create IAM users with minimal required permissions
- Use separate credentials for CI vs production
- Rotate credentials regularly

### 5. Implementation Strategy

#### Phase 1: Immediate CI Fix (Quick Win)
1. Add mock environment variables to existing workflow
2. This allows tests to pass without code changes

#### Phase 2: Service Refactoring (Recommended)
1. Implement lazy loading pattern in AudioService
2. Update PexelsService similarly
3. Add comprehensive test fixtures

#### Phase 3: Full Integration Testing
1. Configure GitHub Secrets
2. Deploy updated workflow with integration test job
3. Monitor and adjust based on results

## Implementation Checklist

### For Repository Owner (User Actions):

- [ ] Navigate to repository Settings → Secrets and variables → Actions
- [ ] Add `AWS_ACCESS_KEY_ID` secret
- [ ] Add `AWS_SECRET_ACCESS_KEY` secret
- [ ] Add `PEXELS_API_KEY` secret
- [ ] Add `ANTHROPIC_API_KEY` secret (optional)
- [ ] Update `.github/workflows/ci.yml` with new configuration
- [ ] Test workflow with a new PR

### For Codebase (Development Actions):

- [ ] Implement lazy loading in AudioService
- [ ] Implement lazy loading in PexelsService
- [ ] Add centralized test fixtures in conftest.py
- [ ] Update backend initialization tests
- [ ] Verify all 691 tests still pass
- [ ] Maintain 73.84% coverage threshold

## Monitoring and Maintenance

### CI/CD Health Metrics
- Unit test success rate: Must remain 100%
- Integration test success rate: Monitor for API issues
- Coverage percentage: Must not drop below 73.84%
- Build time: Target < 5 minutes for unit tests

### Security Auditing
- Review secret access logs monthly
- Rotate credentials quarterly
- Audit IAM permissions semi-annually
- Monitor for exposed secrets in logs

## Rollback Plan

If issues occur:
1. Revert workflow changes to previous version
2. Tests will fail but codebase remains secure
3. Debug locally with proper credentials
4. Re-implement with fixes

## Conclusion

This architecture provides:
- **Secure secret management** with zero exposure risk
- **Proper test separation** between unit and integration tests
- **Backward compatibility** with existing test suite
- **Developer-friendly** local development experience
- **CI/CD reliability** with proper error handling

The implementation maintains all quality gates while enabling comprehensive testing of external service integrations.