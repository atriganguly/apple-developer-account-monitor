# Agent Directives: Apple Developer Account Monitor

## 1. System Context
You are modifying a production-ready, security-critical web automation architecture engineered to scrape metadata and maintain persistent authentication parameters across multiple corporate developer team workspaces within the Apple Developer Portal. The backend runs on Python, Playwright, and the Google API Client library, while orchestration is handled via GitHub Actions and Google Drive cloud storage.

## 2. Absolute Design Constraints
When generating, modifying, refactoring, or patch-updating code for this repository, you must adhere strictly to the following engineering rules:

* **No Emojis or AI Enthusiasm:** All codebase documentation, comments, log lines, pull summaries, and docstrings must be strictly minimal, professional, and follow standard styling. Do not introduce colloquial phrases, checkmarks, rocket ships, or exclamation commentary.
* **Immutable Configurations:** The unified application configuration schema resides entirely in a frozen dataclass within `config/settings.py`. Runtime code blocks must never attempt to mutate configuration parameters directly.
* **Surgical Proximity Selectors:** Never rely on broad, un-scoped global container lookups. Scraping elements must prioritize precise node tracking and text extraction boundaries to separate actual profile metadata values from surrounding accessibility tags, help links, or permission warnings.
* **Fail-Safe Exit Codes:** The system orchestrator must handle specific failure boundaries and return explicit exit signals:
    * Return Code `2` for fatal authentication or 2FA validation blocks.
    * Return Code `3` for downstream Google Sheets synchronization failures.
    * Return Code `4` for domain runtime execution skips.
* **Trigger Isolation:** Do not introduce code architectures that block background thread execution. Every file processing step must support clean, non-interactive headless cloud container environments.

## 3. Deployment Protocol & Namespace Integrity
Python components must use explicit exception blocks and clean imports to prevent namespace contamination.
* Do not introduce hardcoded credentials or key paths.
* All environment variable reads must go through `config/settings.py`.
* Ensure that any columns added to the Google Sheets data layer are accurately mapped across the column sequence tracking indices in `services/sheets.py`.

## 4. Documentation Maintenance Protocol
**CRITICAL:** The `/docs` directory houses the official web representation of this engine. If you modify any parameter definitions, execution flags, or core scraper properties, you must perform an immediate Documentation Impact Assessment.
* You must update `README.md`, `AGENT_README.md`, and the static frontend elements inside `docs/index.html` simultaneously to prevent architectural drift.
* You must never remove author tags, project links, or contribution directories pointing to the original codebase maintainers.