# Updating from the Latest Skeleton Template

A key feature of the [EPAC Data Python Skeleton](https://github.com/CentralLaserFacility/epac-data-py-skeleton) is that changes to the template can be merged into inheriting projects for consistency and alignment.

Before starting, ensure your working tree is clean:

```bash
git status
```

## Update Your Local Development Branch

Switch to your project's development branch:

```bash
git checkout development
```

Update it with the latest changes from your repository:

```bash
git pull origin development
```

## Create an Update Branch

Create a dedicated branch for the skeleton update:

```bash
git checkout -b update-from-skeleton
```

Using a dedicated branch makes it easier to review the imported changes and keeps the `development` branch clean until the update has been validated.

## Pull the Latest Template Changes

Pull the latest template changes directly from the template repository:

`````{tab-set}

````{tab-item} SSH

```bash
git pull git@github.com:CentralLaserFacility/epac-data-py-skeleton.git development
```

````

````{tab-item} HTTPS

```bash
git pull https://github.com/CentralLaserFacility/epac-data-py-skeleton.git development
```

````

`````

If no conflicts occur, Git will complete the merge automatically.

````{note}
If Git reports unrelated histories, repeat the command with:

```bash
git pull <repository-url> development --allow-unrelated-histories
```
This is typically only required if the repositories do not share a common history.
````

## Review the Imported Changes

View the commits introduced by the update:

```bash
git log --oneline ORIG_HEAD..HEAD
```

View the changes introduced by the update:

```bash
git diff ORIG_HEAD..HEAD
```

## Resolve Any Merge Conflicts

If conflicts are reported:

Check the status:

```bash
git status
```

Review and resolve the conflicts manually.

Once resolved, stage the files:

```bash
git add <file>
```

Complete the merge:

```bash
git commit -m "Merge updates from EPAC Data Python Skeleton"
```

## Run Validation Checks

Run all standard project validation checks.

For example:

```bash
./dev.py pre-commit
```

```bash
./dev.py test
```

## Push the Update Branch and Request Review

Push the branch to your repository:

```bash
git push -u origin update-from-skeleton
```

If you are using HTTPS authentication, Git may prompt for credentials when pushing changes.

You can then create a pull request and merge your changes when approved.

## Troubleshooting

Review Changes Introduced by the Update:

```bash
git diff ORIG_HEAD..HEAD
```

View Commits Introduced by the Update:

```bash
git log --oneline ORIG_HEAD..HEAD
```

Abort the Merge Before Committing:

```bash
git merge --abort
```

Compare Your Branch with the Previous State:

```bash
git diff HEAD~1..HEAD
```

## Why Use This Approach?

This approach avoids creating a permanent `skeleton` remote in the repository configuration and is useful for occasional template synchronisation.

If your project regularly aligns with new skeleton releases, configuring a dedicated `skeleton` remote may be more convenient because it simplifies fetching, comparison, and review of future updates.
