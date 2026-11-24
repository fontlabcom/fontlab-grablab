---
this_file: WORK.md
---

## 2026-11-24 — Release and planning review

PyPI identifies `fontlabcom/fontlab-grablab`, `release.yml` and environment `pypi` as the trusted publisher of both v1.1.19 files. Both downloads match the GitHub release SHA-256 digests. The sdist installer and four menu scripts match the release source. The release workflow passed `actionlint`, and all three local release scripts passed `bash -n`.

On the merged branch, `./test.sh` passed all 164 runtime tests. With fly-january 0.2.1, `python -m unittest discover -s tests_docs -v` ran 36 tests with 30 passes, four failures and two errors. The asset check rejects `fly-tokens.css`. Both it and `fly.css` differ from their recorded 0.1.1 hashes. The earlier 54-file reproducible build and 36 passing docs tests applied to 0.1.1.

See [CHANGELOG.md](CHANGELOG.md) for the Issue 131 capture receipts and prior release checks, and [TODO.md](TODO.md) for open verification.

Prior WORK bytes are retained exactly in the private external delivery ledger, SHA256 `73c732904e341a330c34f225fbee2923923ee4481e8de7c6a21d56c68cb892fe`.
