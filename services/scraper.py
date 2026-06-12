import logging
from typing import List, Dict, Any
from playwright.sync_api import Page, TimeoutError

from config.settings import settings
from config.selectors import selectors
from core.exceptions import TeamTraversalError

logger = logging.getLogger("apple_automation.services.scraper")

TARGET_FIELDS = [
    "Entity name",
    "Team ID",
    "Program",
    "Enrolled as",
    "Phone",
    "Street address",
    "Account Holder",
    "Your role",
    "Renewal date",
    "Annual fee",
    "Device reset date"
]

def scrape_all_teams(page: Page, dev_mode: bool = False, on_team_scraped=None) -> List[Dict[str, Any]]:
    scraped_dataset: List[Dict[str, Any]] = []
    
    logger.info(f"Navigating to primary portal overview: {settings.APPLE_PORTAL_URL}")
    page.goto(settings.APPLE_PORTAL_URL, wait_until="networkidle")
    
    try:
        page.click(selectors.TEAM_DROPDOWN_TRIGGER, timeout=5000)
        page.wait_for_selector(selectors.TEAM_OPTION_ITEMS, timeout=5000)
        team_elements = page.locator(selectors.TEAM_OPTION_ITEMS)
        total_teams = team_elements.count()
        
        # Apply dev mode execution boundaries if toggled
        if dev_mode:
            total_teams = min(5, total_teams)
            logger.info(f"[DEV MODE ACTIVE] Restricting tracking framework scope to the first 5 accessible teams.")
        else:
            logger.info(f"Discovered {total_teams} accessible team accounts in the dropdown roster.")
        
        # Close the dropdown before starting the loop
        page.click(selectors.TEAM_DROPDOWN_TRIGGER, timeout=3000)
    except TimeoutError:
        logger.warning("Dropdown selector was not found. Processing as a standalone team workspace.")
        standalone_record = _extract_current_membership_details(page, 0, "Standalone Account")
        if on_team_scraped:
            try:
                on_team_scraped(standalone_record)
            except Exception as cb_err:
                logger.error(f"Real-time streaming callback failed for standalone account: {cb_err}")
        return [standalone_record]

    for index in range(total_teams):
        logger.info(f"Processing target team workspace position {index + 1} of {total_teams}...")
        
        try:
            page.click(selectors.TEAM_DROPDOWN_TRIGGER, timeout=5000)
            page.wait_for_selector(selectors.TEAM_OPTION_ITEMS, timeout=5000)
            
            target_option = page.locator(selectors.TEAM_OPTION_ITEMS).nth(index)
            team_name = target_option.inner_text().strip().split("\n")[0]
            logger.info(f"Attempting workspace transition to team: '{team_name}'")
            
            target_option.click()
            
            # Allow the single page application to swap its asynchronous data fields entirely
            page.wait_for_timeout(2500)
            page.wait_for_load_state("domcontentloaded")
            
            team_record = _extract_current_membership_details(page, index, team_name)
            scraped_dataset.append(team_record)
            logger.info(f"Successfully scraped dataset for team: '{team_name}'")
            
            # Real-time streaming synchronization trigger
            if on_team_scraped:
                try:
                    on_team_scraped(team_record)
                except Exception as cb_err:
                    logger.error(f"Real-time streaming update failed for team index {index + 1}: {cb_err}")
            
        except Exception as e:
            error_context = TeamTraversalError(index, locals().get("team_name", f"Unknown_{index}"), str(e))
            logger.error(error_context.message)
            try:
                page.goto(settings.APPLE_PORTAL_URL, wait_until="domcontentloaded")
            except Exception:
                pass 
            continue

    return scraped_dataset


def _extract_current_membership_details(page: Page, current_index: int, fallback_name: str) -> Dict[str, Any]:
    record: Dict[str, Any] = {
        "Scrape Index": current_index + 1,
        "Team Dropdown Name": fallback_name,
        "Account Alerts / Warnings": _extract_warning_banners(page),
        "Account Holder Email": "N/A"
    }
    
    # Explicitly navigate to the Membership details tab
    try:
        membership_tab = page.locator("a:has-text('Membership details'), a:has-text('Membership')").first
        if membership_tab.count() > 0 and membership_tab.is_visible():
            membership_tab.click()
            page.wait_for_timeout(1500)  # Safe settlement for SPA rendering animations
    except Exception as e:
        logger.warning(f"Membership tab transition notice: {e}")

    # Proceed to scrape fields using a localized, proximity-focused approach
    for field_label in TARGET_FIELDS:
        field_value = "N/A"
        try:
            # Tier 1: Core Sibling Relative Target Extraction
            xpath_locator = selectors.get_value_by_label_xpath(field_label)
            value_element = page.locator(xpath_locator).first
            
            if value_element.count() > 0:
                raw_val = value_element.inner_text().strip()
                if raw_val and "Only members with" not in raw_val and "Enterprise App Store" not in raw_val:
                    field_value = raw_val

            # Tier 2: Outer Parent Container Deduction
            if field_value == "N/A" or not field_value:
                container_selectors = [
                    f"div:has-text('{field_label}')",
                    f"li:has-text('{field_label}')",
                    f"tr:has-text('{field_label}')"
                ]
                for selector in container_selectors:
                    container_loc = page.locator(selector).last
                    if container_loc.count() > 0 and container_loc.is_visible():
                        txt = container_loc.inner_text().strip()
                        cleaned = txt.replace(field_label, "").strip()
                        if cleaned:
                            field_value = cleaned
                            break

            # Data Normalization & Boilerplate Stripping
            if field_value and field_value != "N/A":
                for boilerplate in ["Additional Help", "Help", "Learn more", "Learn More", "ℹ️", "?"]:
                    field_value = field_value.replace(boilerplate, "")
                
                # Filter out system accessibility descriptions or multi-line alerts
                lines = [line.strip() for line in field_value.splitlines() if line.strip()]
                filtered_lines = [
                    line for line in lines 
                    if "Only members with" not in line 
                    and "Enterprise App Store" not in line 
                    and "Contact" not in line
                ]
                field_value = " ".join(filtered_lines).strip() if filtered_lines else "N/A"

            # Custom Field Parsing Logic Override for Account Holder Profiles
            if field_label == "Account Holder":
                row_xpath = f"//*[normalize-space(text())='Account Holder' or contains(., 'Account Holder')]/ancestor::*[local-name()='div' or local-name()='li'][1]"
                row_container = page.locator(row_xpath).first
                if row_container.count() > 0:
                    mail_anchor = row_container.locator("a[href^='mailto:']").first
                    if mail_anchor.count() > 0:
                        href_attr = mail_anchor.get_attribute("href") or ""
                        record["Account Holder Email"] = href_attr.replace("mailto:", "").strip()
                        anchor_text = mail_anchor.inner_text().strip()
                        if anchor_text:
                            field_value = anchor_text

            # Custom Field Parsing Logic Override for Program Packages
            if field_label == "Program":
                if "Enterprise" in field_value:
                    field_value = "Apple Developer Enterprise Program"
                else:
                    field_value = "Apple Developer Program"

        except Exception as e:
            logger.debug(f"Field mapping skipped for target '{field_label}': {str(e)}")
            field_value = "N/A"
        
        record[field_label] = field_value if field_value else "N/A"
            
    return record


def _extract_warning_banners(page: Page) -> str:
    """Checks the dashboard for active warning banners (e.g., Pending License Agreements)."""
    try:
        banner_locator = page.locator(".message-banner, .notification-banner, [class*='banner']").first
        banner_locator.wait_for(state="visible", timeout=2000)
        banner_text = banner_locator.inner_text().strip()
        return " ".join(banner_text.splitlines())
    except Exception:
        return "None"