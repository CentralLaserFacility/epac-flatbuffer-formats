# Development Workflow

> ***NOTE:***
>
> *Project specific guidance should be documented here and take precedence over the general guidelines below.*
>
> *See also the [releasing](../user_guide/releasing.md) section of the docs.*

All changes should be developed using a feature branch created from the repository's main development branch. Work should be committed regularly with clear, descriptive commit messages that explain the purpose of each change.

Before submitting a pull request:

1. Run all relevant tests and verify they pass.
2. Check that the code builds (if appropriate).
3. Update documentation, configuration, and release notes where required.

Pull requests should be reviewed by at least one team member before merging. Feedback should be addressed through additional commits rather than rebasing or force-pushing where review history would be lost.

After a review has been approved, commits may be amended or rebased without requiring reapproval, provided the overall diff remains unchanged. Any modification that alters the effective diff must be re-reviewed and approved before merging.

## Recommended Workflow

```text
Create Feature Branch
        ↓
Implement Changes
        ↓
Run Tests & Validation
        ↓
Update Documentation
        ↓
Open Pull Request
        ↓
Code Review
        ↓
Merge to Main Branch
```