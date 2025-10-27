# Merge Conflict Resolution and PR Fixing

## Context
Multiple parallel sessions have created Pull Requests that may have merge conflicts or build failures. Your job is to fix these issues so all PRs can be cleanly merged.

## Repositories
- **Target Repository**: `[TARGET_REPO]`
- **GitHub URL**: https://github.com/taylor-curran/target-springboot-cics

## Pull Requests to Fix
The following PRs were created by parallel sessions:
[PR_LIST]

## Your Tasks

### 1. Check Each PR Status
For each PR listed above:
- Check if it has merge conflicts
- Check if CI/build is passing
- Check if tests are passing

### 2. Fix Merge Conflicts
If a PR has merge conflicts:
1. Checkout the PR branch
2. Merge or rebase with main branch
3. Resolve conflicts intelligently:
   - Keep all new functionality from the PR
   - Ensure no duplicate code
   - Maintain proper imports
   - Fix any compilation errors
4. Push the resolved changes

### 3. Fix Build/Test Failures  
If a PR has failing builds or tests:
1. Identify the failure cause
2. Fix compilation errors
3. Update broken tests
4. Ensure all tests pass
5. Push the fixes

### 4. Verify All PRs Are Green
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
- [ ] All PRs listed are checked
- [ ] All merge conflicts resolved
- [ ] All builds passing
- [ ] All tests green
- [ ] Each PR is ready to merge (no blockers)

## Output
Create a single PR if you made any fixes, with title:
"fix: Resolve merge conflicts and build failures for parallel PRs"

Include in the PR description:
- List of PRs fixed
- Summary of conflicts resolved
- Summary of build issues fixed
