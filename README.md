<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.iconify.design/fa6-brands/apple.svg?color=white">
    <source media="(prefers-color-scheme: light)" srcset="https://api.iconify.design/fa6-brands/apple.svg?color=111827">
    <img src="https://api.iconify.design/fa6-brands/apple.svg?color=111827" width="40" height="40" alt="Apple Monitor Icon"/>
  </picture>
  <h1>Apple Developer Account Monitor</h1>
  <p>Automated, enterprise-grade multi-workspace session preservation and telemetry engine.</p>
  
  <p>
    Created by 
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.iconify.design/fa6-brands/github.svg?color=white">
      <source media="(prefers-color-scheme: light)" srcset="https://api.iconify.design/fa6-brands/github.svg?color=111827">
      <img src="https://api.iconify.design/fa6-brands/github.svg?color=111827" width="16" height="16" style="vertical-align: middle; margin-bottom: 2px;" alt="GitHub"/>
    </picture>
    <a href="https://github.com/atriganguly"><b>@atriganguly</b></a> &nbsp;&bull;&nbsp; 
    <a href="https://github.com/atriganguly/apple-developer-account-monitor"><b>View Repository</b></a> &nbsp;&bull;&nbsp; 
    <a href="https://atriganguly.github.io/apple-developer-account-monitor/"><b>Official Website</b></a>
  </p>
</div>

<br>

## Overview

Managing corporate iOS digital distribution requires rigorous operational oversight across multiple distinct team entities. Manual monitoring of membership renewal timelines, payment schedules, device reset dates, and localized account warnings inside the Apple Developer Portal becomes error-prone and inefficient at scale.

The Apple Developer Account Monitor automates this process entirely. Operating as a headless background utility, the system sequentially accesses all tenant developer workspaces, parses critical account telemetry data, logs real-time updates directly into an unified Google Sheets spreadsheet ledger, and tracks automated session cookie expirations to maintain active system authorization windows headlessly.

No dedicated servers. No recurring infrastructure overhead. Just clean, actionable operations data delivered exactly where your team works.

<br>

## Technology Stack

* **[Python 3.11](https://docs.python.org/3/):** Core backend runtime environment.
* **[Playwright for Python](https://playwright.dev/python/):** Headless Chromium browser automation framework.
* **[GitHub Actions](https://docs.github.com/en/actions):** CI/CD orchestrator managing cron scheduling and ephemeral execution environments.
* **[Google Drive API v3](https://developers.google.com/drive/api/v3/about-sdk):** Persistent cloud storage layer for cookie (`auth.json`) and configuration loopback.
* **[Google Sheets API v4](https://developers.google.com/sheets/api):** Data layer used for real-time row ingestion and logging.

<br>

## Getting Started

### 1. Generate Google Service Account Credentials
This allows the automation to read/write to your Google Drive and Google Sheets without manual login prompts.
1. Visit the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2. Navigate to **APIs & Services > Library**. Search for and enable **both** the **Google Drive API** and **Google Sheets API**.
3. Navigate to **IAM & Admin > Service Accounts** and click **+ Create Service Account**. Name it (e.g., "Apple-Monitor").
4. Once created, click on the new Service Account, go to the **Keys** tab, click **Add Key > Create New Key**, and select **JSON**. 
5. Download this JSON file. Open it in a text editor—you will need its entire contents later. **Also, copy the `client_email` address found inside the file.**

### 2. Persistent Storage Setup
GitHub Actions destroys all files when a run finishes. We use Google Drive to save your Apple login cookies safely between runs.
1. Open your Google Drive and create a new folder (e.g., "Apple Monitor Cloud State").
2. Right-click the folder, select **Share**, and paste the `client_email` address from step 1. Grant it **Editor** permissions.
3. Look at the URL in your browser bar. It will look like `https://drive.google.com/drive/folders/1aBcD2eFgH3iJ4kL5mNoP6qRsT7uVwXyZ`. Copy **only** the string of letters and numbers at the end. This is your `GOOGLE_DRIVE_FOLDER_ID`.
4. Create a blank Google Sheet for your data, share it with the same `client_email`, and copy the Spreadsheet ID from its URL. This is your `GOOGLE_SHEET_ID`.

### 3. Configure Repository Secrets
To run headlessly inside the cloud without exposing private credentials, map your variables directly into GitHub.
1. Navigate to your forked GitHub repository.
2. Click **Settings > Secrets and variables > Actions**.
3. Click **New repository secret** and add the following entries exactly as named:
   * `APPLE_EMAIL`: The corporate email address used to log into the Apple Developer Portal.
   * `APPLE_PASSWORD`: The corresponding account password string.
   * `GOOGLE_SHEET_ID`: The unique target spreadsheet identifier token (from Step 2.4).
   * `GOOGLE_DRIVE_FOLDER_ID`: The shared Google Drive storage directory folder ID (from Step 2.3).
   * `GOOGLE_CREDS_JSON`: Paste the *entire* raw text payload of the Google Cloud Service Account JSON key you downloaded in Step 1.5.

### 4. Bootstrap Initial Authentication
Because Apple requires 2-Factor Authentication (2FA), the *very first* login must be done manually on your local computer to generate the initial cookies.
1. Clone the repo to your local machine, install dependencies (`pip install -r requirements.txt`), and run `playwright install`.
2. Execute `python bootstrap_auth.py`. 
3. A browser will open. Log in and approve the 2FA prompt on your iPhone/Mac.
4. Once completed, the script saves an `auth.json` file. The GitHub Action will take over from here!

<br>

## Architecture & System Design
*A brief technical overview of the system's underlying engineering principles.*

### 1. Stateful Keep-Alive & Cloud Storage Persistence
GitHub Actions provisions clean, isolated container spaces for each schedule execution, destroying local runtime artifacts upon completion. This ephemeral nature normally prevents long-term browser automation. To bypass this barrier, the application utilizes a persistent loopback storage strategy:
* **Pre-Run Fetch:** Wakes up and immediately uses the Google Drive API to download the active browser cookie matrix (`auth.json`) and core runtime telemetry limits (`config.json`).
* **Post-Run Upload:** Updates session data parameters via Playwright browser context captures and synchronously uploads the refreshed state objects back to your secure Google Drive folder before the container environment closes down.

### 2. Daily Smart Guard Loop Pattern
To maximize resource utilization and protect your private workflow allowances (GitHub Actions minute quotas), the background schedule triggers automatically once every 24 hours. Upon initialization, an internal Python timing filter calculates the exact time elapsed since the last recorded action:
* If the days elapsed do not meet your configured threshold, the process terminates immediately.
* If the duration matches your parameters, the core engine boots up the headless Chromium instance to execute the requested background tasks.

### 3. Multi-Tiered Selection Heuristics
Modern single-page applications (SPAs) heavily leverage asynchronous text rendering and dynamic flexbox/grid containers. To handle these UI conditions without throwing fatal tracking exceptions when class names inevitably change, the scraper uses a relative-proximity node lookup approach:
* **Tier 1:** Targets highly explicit relative XPath queries to locate exact value tokens relative to text element headers.
* **Tier 2:** Executes an outer parent container loop to omit boilerplate strings (such as interactive help nodes, buttons, or informational alerts).
* **Tier 3:** Isolates raw anchor element hypertext links to pull clean display data and parse underlying mailto addresses into distinct data cells.

### 4. Real-Time Row Streaming Ingestion
To eliminate memory bottlenecks and protect against total data drops on long execution passes, the integration replaces standard bulk-overwrite models with a real-time row streaming pipeline. The script clears target cells once at initialization, sets up structured layout headers on Row 1, and pushes data matrices row-by-row on calculated coordinates (`Scrape Index + 1`) the moment an individual workspace scrape pass concludes.

<br>

## Support & Contributions

I built this tool to solve complex, scale-heavy tracking challenges without relying on expensive SaaS infrastructure. 

If you encounter any bugs, have ideas for feature enhancements, or need help patching an edge case, please feel free to reach out. I actively maintain this project and welcome community feedback.

* **Bug Reports & Feature Requests:** [Open an Issue](https://github.com/atriganguly/apple-developer-account-monitor/issues)
* **Connect:** Reach out via my [GitHub Profile](https://github.com/atriganguly) for patches, suggestions, or technical discussions.