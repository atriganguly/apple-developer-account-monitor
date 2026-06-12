class AppleAutomationError(Exception):
    """Base exception class for all custom errors encountered during automation execution."""
    def __init__(self, message: str, context: dict = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}


class SessionExpiredError(AppleAutomationError):
    """
    Fatal exception raised when the storage state session is invalid, expired, or 
    blocked by an unhandled multi-factor authentication (2FA) checkpoint.
    """
    pass


class TeamTraversalError(AppleAutomationError):
    """
    Non-fatal exception raised when the automation fails to interact with or extract 
    data from a specific team from the dropdown roster.
    """
    def __init__(self, team_index: int, team_name: str, reason: str, context: dict = None) -> None:
        ctx = context or {}
        ctx.update({"team_index": team_index, "team_name": team_name, "reason": reason})
        msg = f"Failed to traverse team '{team_name}' at index {team_index}. Reason: {reason}"
        super().__init__(msg, context=ctx)


class GoogleSheetsSyncError(AppleAutomationError):
    """
    Exception raised when syncing operations with the Google Sheets API fail due to 
    network drops, authorization errors, or rate limits.
    """
    pass