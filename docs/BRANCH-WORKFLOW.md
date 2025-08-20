# Branch-Based Development Workflow

This document defines the mandatory branch-based development workflow for the Anki German Language Deck Generator project.

## 🛡️ Purpose: Quality Protection

This workflow protects our critical quality achievements:
- **MyPy --strict compliance**: 502→0 errors (100% elimination)
- **Test suite integrity**: 691 passing tests (667 unit + 24 integration)
- **Code quality standards**: Zero Ruff violations, >73% test coverage
- **Clean Pipeline Architecture**: Maintained separation of concerns

## 🚨 Mandatory Process

### 1. Branch Creation
```bash
# Feature development
git checkout -b feature/your-feature-name

# Bug fixes  
git checkout -b fix/issue-description

# Documentation updates
git checkout -b docs/documentation-update

# Refactoring work
git checkout -b refactor/component-name

# Test improvements
git checkout -b test/test-description
```

### 2. Development Workflow

#### Local Development Loop:
1. **Make changes** on your feature branch
2. **Run quality gates** (mandatory 6-step workflow):
   ```bash
   hatch run type                         # MyPy: ZERO errors
   hatch run ruff check --fix            # Ruff: ZERO violations  
   hatch run format                       # Code formatting
   hatch run test                         # ALL tests pass
   hatch run test-cov                     # Coverage maintained
   hatch run type && hatch run test       # Final verification
   ```
3. **Commit only when** all 6 steps pass ✅
4. **Repeat** until feature is complete

### 3. Pull Request Process

#### Creating the PR:
```bash
# Push your branch
git push -u origin feature/your-feature-name

# Create PR via GitHub interface or CLI
gh pr create --title "Your feature description" --body-file .github/pull_request_template.md
```

#### PR Requirements:
- **Title**: Clear, descriptive summary of changes
- **Template**: Use auto-populated PR template checklist
- **Quality gates**: All CI/CD checks must pass
- **Self-review**: Review your own changes first

#### CI/CD Quality Gates:
The following checks run automatically on every PR:

1. **MyPy Type Check**: Must show "Success: no issues found in 112 source files"
2. **Ruff Linting**: Must show zero violations
3. **Code Formatting**: Must pass formatting check
4. **Unit Test Suite**: All 667 unit tests must pass
5. **Coverage Check**: Must maintain >73% coverage
6. **Final Verification**: Combined MyPy + test check

#### Review Process:
- **Self-review**: Verify all quality gates pass
- **Architectural review**: Ensure Clean Pipeline Architecture compliance
- **Documentation**: Verify docs are updated if needed

### 4. Merge Requirements

**✅ Required for merge:**
- All CI/CD quality gates pass
- PR template checklist completed
- No merge conflicts
- Branch is up to date with main

**❌ Prohibited (will block merge):**
- Any MyPy errors
- Any Ruff violations
- Any test failures
- Coverage decrease
- Missing quality gate checks

### 5. Post-Merge Cleanup
```bash
# After successful merge:
git checkout main
git pull origin main
git branch -d feature/your-feature-name  # Delete local branch
```

## 🚫 Prohibited Actions

**These actions are NEVER allowed:**

1. **Direct commits to main**: All changes must go through feature branches
2. **Bypassing quality gates**: Every PR must pass all CI/CD checks
3. **Force pushing to main**: Protected branch rules prevent this
4. **Merging failing PRs**: No merge allowed with failing quality gates
5. **Incomplete PR templates**: All checklist items must be completed

## 🏗️ Branch Protection Rules

The main branch is protected with these rules:

- **Require pull request reviews** before merging
- **Dismiss stale reviews** when new commits are pushed
- **Require status checks** to pass:
  - MyPy Type Check ✅
  - Ruff Linting ✅
  - Code Formatting ✅
  - Unit Test Suite ✅
  - Coverage Check ✅
  - Final Verification ✅
- **Require branches to be up to date** before merging
- **Include administrators** in restrictions
- **No force pushes** allowed

## 🎯 Quality Gate Integration

### Local Quality Gates (Before PR):
Developer runs all 6 mandatory steps locally before creating PR.

### CI/CD Quality Gates (During PR):
GitHub Actions enforces all quality gates automatically.

### Review Quality Gates (PR Review):
Reviewer confirms architectural and quality standards.

### Post-Merge Protection:
Main branch remains protected with metrics tracking.

## 🔄 Workflow Examples

### Example 1: New Feature
```bash
# Create feature branch
git checkout -b feature/add-verb-conjugation-cards

# Develop and test locally
# ... make changes ...
hatch run type && hatch run ruff check --fix && hatch run format && hatch run test && hatch run test-cov

# Push and create PR
git add -A
git commit -m "Add verb conjugation card generation"
git push -u origin feature/add-verb-conjugation-cards
gh pr create --title "Add verb conjugation card generation"

# After CI passes and review, merge via GitHub
```

### Example 2: Bug Fix
```bash
# Create fix branch
git checkout -b fix/media-enricher-error-handling

# Fix bug and test
# ... make changes ...
hatch run type && hatch run test

# Push and create PR
git add -A
git commit -m "Fix media enricher error handling for missing files"
git push -u origin fix/media-enricher-error-handling
gh pr create --title "Fix media enricher error handling"

# After CI passes, merge via GitHub
```

## 📊 Quality Metrics Tracking

We track these metrics over time:
- **MyPy compliance**: Must remain at 0 errors
- **Test suite health**: Must maintain 691 passing tests
- **Coverage trends**: Must stay above 73%
- **Ruff violations**: Must remain at 0
- **PR merge rate**: Track quality gate effectiveness

## 🚨 Emergency Procedures

**In rare emergencies requiring hotfixes:**

1. **Create hotfix branch**: `git checkout -b hotfix/critical-security-fix`
2. **Minimal changes only**: Fix the specific issue, nothing else
3. **Full quality gates**: Still must pass all 6 steps
4. **Expedited review**: Get immediate review but don't skip quality gates
5. **Post-hotfix analysis**: Review why emergency occurred

**Note**: Even emergencies cannot bypass MyPy/Ruff/Test requirements.

## 🎓 Training and Adoption

### For New Developers:
1. Read this document thoroughly
2. Practice branch workflow on test changes
3. Understand quality gate requirements
4. Know how to interpret CI/CD failures

### Common Issues and Solutions:
- **MyPy errors**: Run `hatch run type` locally and fix before pushing
- **Test failures**: Run `hatch run test` locally and ensure all pass
- **Coverage drops**: Add tests for new code to maintain >73%
- **Merge conflicts**: Keep branches up to date with main

## 🏆 Success Metrics

This workflow is successful when:
- **Zero quality regressions**: No degradation of MyPy/Ruff/Test achievements
- **Clean main branch**: Main always passes all quality gates
- **Predictable releases**: All changes thoroughly tested before merge
- **Maintainable codebase**: Quality standards enforced consistently

---

**Remember**: This workflow protects our hard-won quality achievements. Every step exists to prevent degradation of our 502→0 MyPy success and 691 passing tests.