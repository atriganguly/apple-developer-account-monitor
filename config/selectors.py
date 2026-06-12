from dataclasses import dataclass

@dataclass(frozen=True)
class ApplePortalSelectors:
    """DOM Selectors Registry for the Apple Developer Account Portal."""
    
    # Baseline Page State Verification
    ACCOUNT_CONTAINER: str = "main, #account-main, #main, [class*='team-switcher'], section:has-text('Membership')"
    
    # Global Team Dropdown / Switcher Controls (Broadened to catch modern Apple UI)
    TEAM_DROPDOWN_TRIGGER: str = "button[class*='team'], div[class*='team-switch'], .developer-profile-name, [aria-haspopup='listbox'], header button"
    TEAM_DROPDOWN_MENU: str = "[role='listbox'], [class*='team-menu'], ul.teams-list"
    TEAM_OPTION_ITEMS: str = "[role='listbox'] li, [role='listbox'] button, [class*='team-menu'] button, ul.teams-list li"
    
    @staticmethod
    def get_value_by_label_xpath(label_text: str) -> str:
        """
        Generates a highly-resilient multi-tiered XPath locator to extract text value elements.
        Supports both direct layout siblings and relative row parent element tracking patterns.
        """
        return (
            f"//*[text()='{label_text}' or contains(text(), '{label_text}')]/following-sibling::*[1] | "
            f"//*[text()='{label_text}' or contains(text(), '{label_text}')]/parent::*/following-sibling::*[1]"
        )

# Initialize global reference registry
selectors = ApplePortalSelectors()