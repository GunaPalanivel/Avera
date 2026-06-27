## Summary

<!-- What changed and why (2–4 sentences). Link the problem, not the diff. -->

## Linked issues

<!-- Closes #123 / Depends on #456 -->

## Labels

<!-- type:___ area:___ — optional -->

## Changes

<!-- Bullet list of user-visible or reviewer-relevant changes -->

-

## Test plan

<!-- Exact commands you ran. Reviewer should copy-paste. -->

- [ ] `make lint`
- [ ] `make test`
- [ ] <!-- milestone-specific, e.g. python rank.py --health -->

```bash
# paste commands here
```

## Reviewer checklist

- [ ] Scope matches **one milestone** (or focused fix/docs)
- [ ] Acceptance criteria met
- [ ] Tests added or updated for new behavior
- [ ] Public docs updated if CLI, config, or scoring changed
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] No `idea/` files in diff
- [ ] No secrets, API keys, or local paths in committed files
- [ ] CI green

## Risk & rollback

<!-- Low / Medium. How to revert if this breaks main. -->

**Risk:**

**Rollback:** `git revert <merge-commit-sha>`

## Screenshots / logs

<!-- CI link, benchmark output, CSV sample row, HF Space screenshot — optional -->
