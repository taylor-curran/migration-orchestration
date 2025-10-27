# PR Compatibility Analysis and Integration

## Context
Multiple parallel sessions have created Pull Requests. Your job is to:
1. Analyze the compatibility and interactions between these PRs
2. Test their combined functionality
3. Fix any conflicts, issues, or incompatibilities
4. Make necessary adjustments to ensure they work well together

## Repositories
- **Target Repository**: `[TARGET_REPO]`
- **GitHub URL**: https://github.com/taylor-curran/target-springboot-cics

## Pull Requests to Fix
The following PRs were created by parallel sessions:
[PR_LIST]

## Your Tasks

### 1. Analyze PR Compatibility
For each PR listed above:
- Review what changes each PR makes
- Identify potential interactions or overlaps between PRs
- Check for any architectural conflicts or design inconsistencies
- Verify naming conventions and patterns are consistent

### 2. Check Each PR Status
For each PR:
- Check if it has merge conflicts
- Check if CI/build is passing
- Check if tests are passing
- Review test coverage and quality

### 3. Test Combined Functionality
Create a test branch that combines all PRs:
1. Create a new branch from main
2. Cherry-pick or merge all PR changes into this branch
3. Run full test suite
4. Test integration points between the different PR changes
5. Verify no functionality is broken by the combination

### 4. Fix Merge Conflicts
If a PR has merge conflicts:
1. Checkout the PR branch
2. Merge or rebase with main branch
3. Resolve conflicts intelligently:
   - Keep all new functionality from the PR
   - Ensure no duplicate code
   - Maintain proper imports
   - Fix any compilation errors
4. Push the resolved changes

### 5. Fix Build/Test Failures  
If a PR has failing builds or tests:
1. Identify the failure cause
2. Fix compilation errors
3. Update broken tests
4. Ensure all tests pass
5. Push the fixes

### 6. Make Compatibility Adjustments
If PRs work but could be better integrated:
1. Refactor duplicate code into shared utilities
2. Align naming conventions
3. Consolidate similar functionality
4. Improve test coverage for integration points
5. Add integration tests if needed

### 7. Verify All PRs Are Green and Compatible
After fixing issues:
- All PRs should be mergeable (no conflicts)
- All PR checks should be passing
- All tests should be green

## Important Guidelines

### When Resolving Conflicts
- **Preserve all work**: Never delete functionality from any PR
- **Smart merging**: If two PRs modify the same area, combine changes intelligently
- **Import management**: Consolidate duplicate imports
- **Method ordering**: Arrange methods logically if multiple were added to same class

### Common Conflict Patterns
1. **Multiple PRs adding to same file**: Merge all additions
2. **Import conflicts**: Keep all unique imports, remove duplicates
3. **Similar functionality**: Keep the most complete implementation
4. **Test conflicts**: Keep all tests, renumber if needed

### Build Fix Patterns
1. **Missing dependencies**: Add to pom.xml or build.gradle
2. **Import errors**: Add missing imports
3. **Type mismatches**: Fix method signatures
4. **Test failures**: Update test expectations if code changed

## Definition of Done
- [ ] All PRs analyzed for compatibility
- [ ] Combined functionality tested
- [ ] All merge conflicts resolved (if any)
- [ ] All builds passing
- [ ] All tests green
- [ ] PRs work well together when combined
- [ ] Integration points tested
- [ ] Each PR is ready to merge (no blockers)

## Output
Create a single PR if you made any changes (fixes, improvements, or integration enhancements), with title:
"fix: Ensure PR compatibility and integration for parallel tasks"

Include in the PR description:
- List of PRs analyzed
- Compatibility findings
- Summary of any conflicts resolved
- Summary of any build issues fixed
- Integration improvements made
- Test coverage added
