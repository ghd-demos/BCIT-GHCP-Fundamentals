# Rename `globex_` to `chroma_`

## Goal

Rename tracked references from `globex_` to `chroma_` repository-wide while preserving a rollback point, validating behavior, and enforcing the change in CI.

## Assumptions

- The rename applies to the exact, case-sensitive literal `globex_`.
- Binary files, dependencies, `.git`, and generated artifacts are excluded unless explicitly tracked and reviewed.
- Compatibility aliases may be needed if external consumers or deployed configurations depend on existing names.

## Implementation Plan

1. **Discover and classify matches**
   - Search tracked text files for the case-sensitive literal `globex_`.
   - Record each filename, line, and usage type: source, test, CI/configuration, documentation, fixture/data, or generated content.
   - Review matches manually before editing.

2. **Create a rollback point**
   - Verify that the working tree is clean.
   - Record the current commit SHA.
   - Create a backup branch or tag with a unique name.
   - Save the pre-change match inventory for comparison.

3. **Perform the rename**
   - Replace exact `globex_` literals with `chroma_` in reviewed tracked text files.
   - Update affected tests, fixtures, scripts, configuration, CI, and documentation.
   - Do not change unrelated identifiers containing `globex` without the underscore unless separately required.

4. **Add regression coverage**
   - Add or update tests for affected behavior, configuration parsing, and external interfaces.
   - Add a repeatable check that fails when tracked text files still contain `globex_`.

5. **Add the CI gate**
   - Integrate the no-legacy-prefix check into the existing CI workflow.
   - Run the established build, lint, and test commands alongside the new check.
   - Keep the CI change compatible with the repository's existing tooling.

6. **Validate the change**
   - Review the complete diff for unintended replacements.
   - Confirm the exact literal `globex_` is absent from tracked text files.
   - Run focused tests first, followed by the full available build and test suite.
   - Exercise any affected CLI commands, configuration paths, and integrations.

7. **Verify rollback**
   - If validation fails, revert the change commit or reset to the recorded backup branch/tag.
   - Re-run the original validation suite after rollback.
   - For externally consumed identifiers, retain temporary compatibility aliases where needed instead of performing an irreversible cutover.

8. **Finalize**
   - Commit intentional source and test changes separately from generated artifacts.
   - Document the current commit SHA, backup branch/tag, validation results, and rollback command.
   - Ensure temporary backup files are not committed.

## Acceptance Criteria

- All reviewed tracked text references use `chroma_` instead of `globex_`.
- No unintended or binary-file changes are present.
- Tests, linting, builds, and affected integration checks pass.
- CI fails if a tracked text file reintroduces `globex_`.
- A tested backup and rollback path is recorded.

## Rollback Checklist

- Identify the rename commit and pre-change commit SHA.
- Revert the rename commit, or reset a recovery branch to the backup tag/branch.
- Restore any external compatibility configuration if deployment was attempted.
- Re-run build and tests to confirm recovery.
