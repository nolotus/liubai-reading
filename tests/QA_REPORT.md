# Independent QA report

Tested 2026-11-03 with isolated temporary SQLite/file storage. No external services were called.

## Passed

`python tests/qa_api.py` exercises actual HTTP handler methods in-process because this worker cannot open network sockets:

- Original two-page PDF and Chinese two-chapter EPUB import.
- Duplicate import reopens existing identity.
- Exact extracted-text anchors, including non-BMP emoji codepoints.
- Initial question, follow-up, manually labelled answer, appended understanding.
- Persistence through separate database reads/connections.
- Missing AI gives 503 and retains question history without fabricated answers.
- Export ZIP has Markdown, byte-identical source attachment, JSON anchors, and HTML jump IDs matching Markdown return-to-source links.
- Invalid PDF/EPUB, unsupported extension, malformed JSON, empty follow-up, wrong quote, negative section, unknown book, and cross-origin write return expected errors.
- Untrusted Host header is rejected.
- No-text PDF, password-protected PDF, and oversized declared upload body are rejected.

## Fixed during QA, inspection verified

A draft originally saved the latest selection even if its displayed quote differed. `draftSelection` now snapshots the selected passage on draft creation and is cleared on save/cancel/book change. Browser regression remains unexecuted.

## Browser limitation

`python tests/qa_browser.py` is provided, but Chromium launch failed with OS `socket() failed: Operation not permitted`, including after approved sandbox escalation. Thus this worker has not verified rendering, click interactions, reload UI restoration, screenshots, or the actual Obsidian application. No screenshot was produced. Browser launch failure is environmental, not an observed app defect.

## Additional fixes verified by regression tests

- Twenty simultaneous follow-up writes all succeed, retain every distinct entry, and lose no writes after transaction locking was added.
- A local mock AI response delayed while a new follow-up is written preserves both the follow-up and response. The mock never contacts a provider and only writes isolated QA storage.
- JSON arrays/null and null question/follow-up/answer/insight fields now return 400.

## Not verified

Real AI provider response, billing/network failures with a configured key, production-scale books, DRM EPUB fixture behavior, OCR, EPUB rendering fidelity, and native Obsidian link interaction. Export structure and internal link targets were verified programmatically.

## Alternate browser attempt

The parent implementation worker also tried the existing cloud CUA browser. Opening http://127.0.0.1:8765 returned net::ERR_CONNECTION_REFUSED because the browser could not reach the executor-local service. No network exposure or public deployment was introduced to work around this isolation.
