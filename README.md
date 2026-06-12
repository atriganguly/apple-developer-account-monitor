# Apple Developer Account Monitor

Automated, enterprise-grade multi-workspace session preservation and performance tracking engine built on a zero-infrastructure cloud architecture.

Created by @atriganguly

---

## Overview

Managing corporate iOS digital distribution requires rigorous operational oversight across multiple distinct team entities. Manual monitoring of membership renewal timelines, payment schedules, device reset dates, and localized account warnings inside the Apple Developer Portal becomes error-prone and inefficient at scale.

The Apple Developer Account Monitor automates this process entirely. Operating as a headless background utility, the system sequentially accesses all tenant developer workspaces, parses critical account telemetry data, logs real-time updates directly into an unified Google Sheets spreadsheet ledger, and tracks automated session cookie expirations to maintain active system authorization windows headlessly.

No dedicated servers. No recurring infrastructure overhead. Just clean, actionable operations data delivered exactly where your team works.

---

## Getting Started

### 1. Persistent Storage Setup
The automation environment relies on Google Drive to maintain a persistent state layer across ephemeral runner contexts.
1. Create a directory folder inside your Google Drive workspace (e.g., "Apple Monitor Cloud State").
2. Share the folder granting Editor access to your Google Service Account email address.
3. Extract and copy the unique Folder ID found at the end of the directory URL path.

### 2. Configure Repository Secrets
To run headlessly inside the cloud without exposing private credentials, you must map the following encrypted access parameters within your private GitHub repository Settings > Secrets and variables > Actions:

* `APPLE_EMAIL`: The corporate email address used to log into the Apple Developer Portal.
* `APPLE_PASSWORD`: The corresponding account password string.
* `GOOGLE_SHEET_ID`: The unique target spreadsheet identifier token.
* `GOOGLE_DRIVE_FOLDER_ID`: The shared Google Drive storage directory folder ID mapped in Step 1.
* `GOOGLE_CREDS_JSON`: The complete, raw text payload of your Google Cloud Service Account JSON key credential file.

### 3. Usage
The system features a dual execution design pattern controlled via terminal arguments or direct frontend interaction:
* **Full Ingestion Scrape:** `python main.py --mode scrape` — Clears target matrices, launches a multi-tiered DOM extraction routine across all team profiles, and streams findings live into Google Sheets.
* **Session Keep-Alive:** `python main.py --mode keep-alive` — Accesses the base overview panel to force background OAuth handshakes, preserving the sliding cookie validity lifecycle automatically.

---

## Architecture & System Design

### 1. Stateful Keep-Alive & Cloud Storage Persistence
GitHub Actions provisions clean, isolated container spaces for each schedule execution, destroying local runtime artifacts upon completion. To bypass this barrier, the application utilizes a persistent loopback storage strategy:
* **Pre-Run Fetch:** Wakes up and immediately uses the Google Drive API to download the active browser cookie matrix (`auth.json`) and core runtime telemetry limits (`config.json`).
* **Post-Run Upload:** Updates session data parameters via Playwright browser context captures and synchronously uploads the refreshed state objects back to your secure Google Drive folder before the container environment closes down.

### 2. Daily Smart Guard Loop Pattern
To maximize resource utilization and protect your private workflow allowances, the background schedule triggers automatically once every 24 hours. Upon initialization, an internal Python timing filter calculates the exact time elapsed since the last recorded action:
* If the days elapsed do not meet your configured threshold, the process terminates immediately.
* If the duration matches your parameters, the core engine boots up the headless Chromium instance to execute the requested background tasks.

### 3. Multi-Tiered Selection Heuristics
Modern single-page applications heavily leverage asynchronous text rendering and dynamic flexbox/grid containers. To handle these UI conditions without throwing fatal tracking exceptions, the scraper uses a relative-proximity node lookup approach:
* **Tier 1:** Targets highly explicit relative XPath queries to locate exact value tokens relative to text element headers.
* **Tier 2:** Executes an outer parent container loop to omit boilerplate strings (such as interactive help nodes, buttons, or informational alerts).
* **Tier 3:** Isolates raw anchor element hypertext links to pull clean display data and parse underlying mailto addresses into distinct data cells.

### 4. Real-Time Row Streaming Ingestion
To eliminate memory bottlenecks and protect against total data drops on long execution passes, the integration replaces standard bulk-overwrite models with a real-time row streaming pipeline. The script clears target cells once at initialization, sets up structured layout headers on Row 1, and pushes data matrices row-by-row on calculated coordinates (`Scrape Index + 1`) the moment an individual workspace scrape pass concludes.