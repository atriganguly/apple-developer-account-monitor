/**
 * Global Configuration Registry for Apple Developer Account Expiration Monitoring.
 * All parameters, column mappings, timing intervals, and communication templates reside here.
 * Modifications can be performed within this file without altering core processing logic.
 */
var APP_ALERT_CONFIG = {
  // Target worksheet tab name populated by the automation engine
  SHEET_NAME: 'Apple Developer Account Monitor',

  // Absolute zero-based array indices tracking columns from the python sheet ledger layout
  COLUMN_MAP: {
    ACCOUNT_NAME: 3,         // Column D: "Entity name"
    ACCOUNT_HOLDER: 9,       // Column J: "Account Holder"
    ACCOUNT_HOLDER_EMAIL: 10, // Column K: "Account Holder Email"
    RENEWAL_DATE: 12         // Column M: "Renewal date"
  },

  // Alert threshold intervals (measured in days remaining until renewal target)
  MILESTONE_DAYS: 30,
  COUNTDOWN_DAYS: [14, 7, 3, 1, 0],
  
  // Periodic system digest parameter configuration
  DIGEST_INTERVAL_DAYS: 14,

  // Automated background trigger hour window placement (e.g., 8 runs between 08:00 and 09:00 AM local time)
  AUTOMATION_TRIGGER_HOUR: 8,

  // Force communication routines to process regardless of target dates (set to false for production)
  FORCE_SEND_ALL: false,

  // Milestone Notification Profile Configuration (Type 1: Standard 30-Day Alert)
  MILESTONE_EMAIL: {
    TO: 'admin@example.com, operations@example.com',
    CC: 'manager@example.com',
    BCC: '',
    SUBJECT_TEMPLATE: 'Action Required: {{COUNT}} Apple Developer Account approaching milestone renewal window',
    HEADER_HTML: '<p>The following corporate Apple Developer account has reached its 30-day milestone threshold window and requires subscription processing:</p>',
    FOOTER_HTML: '<p style="font-size: 11px; color: #666; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px;">Distributed via Apple Account Expiration Monitor.</p>'
  },

  // Countdown Notification Profile Configuration (Type 2: Urgent Multi-Day Alerts)
  COUNTDOWN_EMAIL: {
    TO: 'admin@example.com, operations@example.com',
    CC: 'leadership@example.com',
    BCC: '',
    SUBJECT_TEMPLATE: 'URGENT: {{COUNT}} Apple Developer Subscriptions expiring imminently',
    HEADER_HTML: '<p>The following developer team accounts are crossing critical expiration countdown horizons. Execute necessary financial authorizations immediately to safeguard deployment lanes:</p>',
    FOOTER_HTML: '<p style="font-size: 11px; color: #aa3333; margin-top: 30px; border-top: 1px solid #ffcccc; padding-top: 10px; font-weight: bold;">Warning: Failure to execute renewal procedures prior to zero days remaining will freeze active application update structures.</p>'
  },

  // System Digest Profile Configuration (Type 3: Comprehensive Bi-Weekly Status Matrix)
  DIGEST_EMAIL: {
    TO: 'admin@example.com, operations@example.com',
    CC: 'audit@example.com',
    BCC: '',
    SUBJECT_TEMPLATE: 'System Report: Apple Developer Account Workspace Status Digest',
    HEADER_HTML: '<p>Automated bi-weekly monitoring review overview. The following matrix contains deployment data records across all accessible tenant digital workspaces:</p>',
    FOOTER_HTML: '<p style="font-size: 11px; color: #666; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px;">This automated status compilation is dispatched periodically according to configuration limits.</p>'
  }
};