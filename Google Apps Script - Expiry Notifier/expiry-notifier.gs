/**
 * Core Processing Execution Engine.
 * Manages row iterations, date translations, and data batching.
 * Interfaces directly with parameters defined inside APP_ALERT_CONFIG.
 */

/**
 * Instantiates custom interface components inside the worksheet toolbar.
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Apple Account Alerts')
    .addItem('Run Manual Expiry Verification', 'runManualExpiryCheck')
    .addItem('Send On-Demand Status Digest', 'runManualDigest')
    .addSeparator()
    .addItem('Setup Automated Daily Trigger', 'setupDailyTrigger')
    .addToUi();
}

/**
 * Entry point for manual expiration monitoring sequences.
 */
function runManualExpiryCheck() {
  checkExpirations(true);
}

/**
 * Entry point for manual comprehensive status digest generation.
 */
function runManualDigest() {
  generateDigestReport(true);
}

/**
 * Automated script execution coordinator mapped to time-driven daily triggers.
 */
function dailyAutomationEntry() {
  console.log("Starting automated background loop sequence.");
  checkExpirations(false);
  checkAndRunScheduledDigest();
}

/**
 * Clears historical project configurations and provisions a clean daily runtime cron task.
 */
function setupDailyTrigger() {
  const ui = SpreadsheetApp.getUi();
  const triggers = ScriptApp.getProjectTriggers();
  
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() === 'dailyAutomationEntry') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  ScriptApp.newTrigger('dailyAutomationEntry')
    .timeBased()
    .everyDays(1)
    .atHour(APP_ALERT_CONFIG.AUTOMATION_TRIGGER_HOUR)
    .create();
    
  ui.alert('Success: Background processing infrastructure initialized. Sweeps will execute daily between ' + 
           APP_ALERT_CONFIG.AUTOMATION_TRIGGER_HOUR + ':00 AM and ' + (APP_ALERT_CONFIG.AUTOMATION_TRIGGER_HOUR + 1) + ':00 AM local time.');
}

/**
 * Scans the live ledger range to calculate expiration deltas and distribute batched communications.
 */
function checkExpirations(isManual) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(APP_ALERT_CONFIG.SHEET_NAME);
  if (!sheet) {
    handleInitializationFailure("Worksheet target tab not located: " + APP_ALERT_CONFIG.SHEET_NAME, isManual);
    return;
  }

  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  if (lastRow <= 1) {
    if (isManual) SpreadsheetApp.getUi().alert('Execution notice: Sheet contains no data entries underneath header definitions.');
    return;
  }

  const data = sheet.getRange(2, 1, lastRow - 1, lastCol).getValues();
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  let milestoneBatch = [];
  let countdownBatch = [];

  data.forEach(function(row) {
    const accountName = row[APP_ALERT_CONFIG.COLUMN_MAP.ACCOUNT_NAME] ? row[APP_ALERT_CONFIG.COLUMN_MAP.ACCOUNT_NAME].toString().trim() : '';
    const holderName = row[APP_ALERT_CONFIG.COLUMN_MAP.ACCOUNT_HOLDER] ? row[APP_ALERT_CONFIG.COLUMN_MAP.ACCOUNT_HOLDER].toString().trim() : '';
    const holderEmail = row[APP_ALERT_CONFIG.COLUMN_MAP.ACCOUNT_HOLDER_EMAIL] ? row[APP_ALERT_CONFIG.COLUMN_MAP.ACCOUNT_HOLDER_EMAIL].toString().trim() : '';
    const rawDate = row[APP_ALERT_CONFIG.COLUMN_MAP.RENEWAL_DATE];

    if (!accountName || accountName === 'N/A' || accountName === '') return;

    const expDate = parseBulletproofDate(rawDate);
    if (!expDate) return;

    const diffTime = expDate.getTime() - today.getTime();
    const daysRemaining = Math.round(diffTime / (1000 * 60 * 60 * 24));

    const record = {
      name: accountName,
      holder: holderName,
      email: holderEmail,
      dateString: Utilities.formatDate(expDate, Session.getScriptTimeZone(), "MMMM dd, yyyy"),
      days: daysRemaining
    };

    if (daysRemaining === APP_ALERT_CONFIG.MILESTONE_DAYS || APP_ALERT_CONFIG.FORCE_SEND_ALL) {
      milestoneBatch.push(record);
    }
    
    if (APP_ALERT_CONFIG.COUNTDOWN_DAYS.indexOf(daysRemaining) !== -1 || APP_ALERT_CONFIG.FORCE_SEND_ALL) {
      countdownBatch.push(record);
    }
  });

  if (milestoneBatch.length > 0) {
    dispatchConsolidatedEmail(milestoneBatch, APP_ALERT_CONFIG.MILESTONE_EMAIL);
  }
  
  if (countdownBatch.length > 0) {
    dispatchConsolidatedEmail(countdownBatch, APP_ALERT_CONFIG.COUNTDOWN_EMAIL);
  }

  if (isManual) {
    SpreadsheetApp.getUi().alert('Verification processing completed. Milestone Matches: ' + milestoneBatch.length + '. Countdown Matches: ' + countdownBatch.length + '. Emails sent accordingly.');
  }
}

/**
 * Evaluates timing thresholds via local PropertiesService context to run automated scheduled status dispatches.
 */
function checkAndRunScheduledDigest() {
  const props = PropertiesService.getScriptProperties();
  const lastRunStr = props.getProperty('LAST_DIGEST_TIMESTAMP');
  const now = new Date();
  
  if (lastRunStr) {
    const lastRunDate = new Date(parseInt(lastRunStr, 10));
    const deltaMillis = now.getTime() - lastRunDate.getTime();
    const daysElapsed = deltaMillis / (1000 * 60 * 60 * 24);
    
    if (daysElapsed >= APP_ALERT_CONFIG.DIGEST_INTERVAL_DAYS) {
      generateDigestReport(false);
    } else {
      console.log("System digest execution bypassed. Minimum tracking interval delta has not been reached.");
    }
  } else {
    generateDigestReport(false);
  }
}

/**
 * Builds an aggregated report matrix of all profiles stored inside the tracking workspace ledger.
 */
function generateDigestReport(isManual) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(APP_ALERT_CONFIG.SHEET_NAME);
  if (!sheet) {
    handleInitializationFailure("Worksheet target tab not located: " + APP_ALERT_CONFIG.SHEET_NAME, isManual);
    return;
  }

  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  if (lastRow <= 1) return;

  const data = sheet.getRange(2, 1, lastRow - 1, lastCol).getValues();
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  let fullReportBatch = [];

  data.forEach(function(row) {
    const accountName = row[APP_ALERT_CONFIG.COLUMN_MAP.ACCOUNT_NAME] ? row[APP_ALERT_CONFIG.COLUMN_MAP.ACCOUNT_NAME].toString().trim() : '';
    const holderName = row[APP_ALERT_CONFIG.COLUMN_MAP.ACCOUNT_HOLDER] ? row[APP_ALERT_CONFIG.COLUMN_MAP.ACCOUNT_HOLDER].toString().trim() : '';
    const holderEmail = row[APP_ALERT_CONFIG.COLUMN_MAP.ACCOUNT_HOLDER_EMAIL] ? row[APP_ALERT_CONFIG.COLUMN_MAP.ACCOUNT_HOLDER_EMAIL].toString().trim() : '';
    const rawDate = row[APP_ALERT_CONFIG.COLUMN_MAP.RENEWAL_DATE];

    if (!accountName || accountName === 'N/A' || accountName === '') return;

    const expDate = parseBulletproofDate(rawDate);
    let daysRemaining = 'N/A';
    let dateStr = 'Unknown';

    if (expDate) {
      const diffTime = expDate.getTime() - today.getTime();
      daysRemaining = Math.round(diffTime / (1000 * 60 * 60 * 24));
      dateStr = Utilities.formatDate(expDate, Session.getScriptTimeZone(), "MMMM dd, yyyy");
    }

    fullReportBatch.push({
      name: accountName,
      holder: holderName,
      email: holderEmail,
      dateString: dateStr,
      days: daysRemaining
    });
  });

  if (fullReportBatch.length > 0) {
    dispatchConsolidatedEmail(fullReportBatch, APP_ALERT_CONFIG.DIGEST_EMAIL);
    if (!isManual) {
      PropertiesService.getScriptProperties().setProperty('LAST_DIGEST_TIMESTAMP', today.getTime().toString());
    }
  }

  if (isManual) {
    SpreadsheetApp.getUi().alert('Status report generated successfully. Total records cataloged: ' + fullReportBatch.length + '. Digest email distributed.');
  }
}

/**
 * Translates cell parameters, textual timestamps, or system data objects into standard calendar entities.
 */
function parseBulletproofDate(value) {
  if (!value) return null;
  
  if (value instanceof Date) {
    const d = new Date(value.getTime());
    d.setHours(0, 0, 0, 0);
    return d;
  }
  
  if (typeof value === 'string') {
    let cleanStr = value.trim();
    if (cleanStr === 'N/A' || cleanStr === '') return null;
    
    if (cleanStr.indexOf('/') !== -1) {
      const segments = cleanStr.split('/');
      if (segments.length === 3) {
        const d = new Date(parseInt(segments[2], 10), parseInt(segments[1], 10) - 1, parseInt(segments[0], 10));
        d.setHours(0, 0, 0, 0);
        if (!isNaN(d.getTime())) return d;
      }
    }
    
    const d = new Date(cleanStr);
    d.setHours(0, 0, 0, 0);
    if (!isNaN(d.getTime())) return d;
  }
  
  return null;
}

/**
 * Compiles aggregated batch objects into structured HTML table blocks for deployment.
 */
function dispatchConsolidatedEmail(batch, emailProfile) {
  let tableRows = '';
  
  batch.forEach(function(item) {
    const warningColor = (typeof item.days === 'number' && item.days <= 7) ? '#d9534f' : '#333333';
    
    tableRows += '<tr>' +
      '<td style="padding: 10px; border: 1px solid #dddddd; font-family: Arial, sans-serif; font-size: 13px; color: #333333; font-weight: bold;">' + item.name + '</td>' +
      '<td style="padding: 10px; border: 1px solid #dddddd; font-family: Arial, sans-serif; font-size: 13px; color: #555555;">' + item.holder + ' (' + item.email + ')</td>' +
      '<td style="padding: 10px; border: 1px solid #dddddd; font-family: Arial, sans-serif; font-size: 13px; color: #333333;">' + item.dateString + '</td>' +
      '<td style="padding: 10px; border: 1px solid #dddddd; font-family: Arial, sans-serif; font-size: 13px; color: ' + warningColor + '; font-weight: bold; text-align: center;">' + item.days + '</td>' +
      '</tr>';
  });

  const masterSheetUrl = SpreadsheetApp.getActiveSpreadsheet().getUrl();
  const fullHtmlBody = '<div style="font-family: Arial, sans-serif; line-height: 1.5; color: #333333; max-width: 800px;">' +
    emailProfile.HEADER_HTML +
    '<table style="width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 20px;">' +
    '<thead>' +
    '<tr style="background-color: #f8f9fa; border: 1px solid #dddddd;">' +
    '<th style="padding: 12px 10px; border: 1px solid #dddddd; text-align: left; font-size: 13px; color: #111111;">Account Name</th>' +
    '<th style="padding: 12px 10px; border: 1px solid #dddddd; text-align: left; font-size: 13px; color: #111111;">Administrative Contact</th>' +
    '<th style="padding: 12px 10px; border: 1px solid #dddddd; text-align: left; font-size: 13px; color: #111111;">Renewal Target Date</th>' +
    '<th style="padding: 12px 10px; border: 1px solid #dddddd; text-align: center; font-size: 13px; color: #111111; width: 100px;">Days Remaining</th>' +
    '</tr>' +
    '</thead>' +
    '<tbody>' +
    tableRows +
    '</tbody>' +
    '</table>' +
    '<p style="font-size: 13px;"><a href="' + masterSheetUrl + '" style="color: #0066cc; text-decoration: none; font-weight: bold;">Navigate to Master Management Spreadsheet Ledger</a></p>' +
    emailProfile.FOOTER_HTML +
    '</div>';

  const consolidatedSubject = emailProfile.SUBJECT_TEMPLATE.replace('{{COUNT}}', batch.length.toString());

  let mailOptions = {
    to: emailProfile.TO,
    subject: consolidatedSubject,
    htmlBody: fullHtmlBody
  };

  if (emailProfile.CC && emailProfile.CC.trim() !== '') mailOptions.cc = emailProfile.CC;
  if (emailProfile.BCC && emailProfile.BCC.trim() !== '') mailOptions.bcc = emailProfile.BCC;

  MailApp.sendEmail(mailOptions);
}

/**
 * Route logging signals to centralized dashboards when exceptions arise.
 */
function handleInitializationFailure(reason, isManual) {
  console.error(reason);
  if (isManual) {
    SpreadsheetApp.getUi().alert('Error context: ' + reason);
  }
}