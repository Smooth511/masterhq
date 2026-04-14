# GitHub Data Exports

These are JSON files from GitHub's data portability export. They contain repository metadata, issue events, pull request data, and other structural information exported from the Smooth511 account.

**Source:** GitHub Settings → Account → Export account data
**Date:** Originally exported during account migration from Literatefool → Smooth511

## Contents

| File | Description |
|------|-------------|
| attachments_000001.json | File attachments metadata |
| bots_000001.json | Bot account data |
| discussion_categories_000001.json | Discussion category definitions |
| issue_comments_000001.json | Comments on issues |
| issue_events_*.json | Issue event timeline (5 files, paginated) |
| issues_000001.json | Issue metadata |
| pull_request_review_comments_000001.json | PR review comments |
| pull_request_review_threads_000001.json | PR review threads |
| pull_request_reviews_000001.json | PR reviews |
| pull_requests_000001.json | Pull request metadata |
| repositories_000001.json | Repository metadata |
| repository_files_000001.json | Repository file listings |
| schema.json | Export schema version |
| users_000001.json | User account data |

⚠️ **Note:** Copilot chat content is NOT included in GitHub data exports. Chat sessions tied to OAuth tokens can cascade-delete across accounts (learned the hard way 2026-03-18).
