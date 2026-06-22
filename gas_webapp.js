# Google Apps Script - Deploy sebagai Web App
# Paste di https://script.google.com/

function doPost(e) {
  var sheet = SpreadsheetApp.openById('YOUR_SHEET_ID').getActiveSheet();
  var data = JSON.parse(e.postData.contents);
  
  if (data.action === 'delete') {
    sheet.deleteRows(data.startRow, data.numRows);
    return ContentService.createTextOutput(JSON.stringify({success: true})).setMimeType(ContentService.MimeType.JSON);
  }
  
  if (data.action === 'clear') {
    var lastRow = sheet.getLastRow();
    if (lastRow > 1) sheet.getRange(2, 1, lastRow - 1, 7).clearContent();
    return ContentService.createTextOutput(JSON.stringify({success: true})).setMimeType(ContentService.MimeType.JSON);
  }
  
  if (data.rows && data.rows.length > 0) {
    var lastRow = sheet.getLastRow();
    var range = sheet.getRange(lastRow + 1, 1, data.rows.length, data.rows[0].length);
    range.setValues(data.rows);
    
    // Force TEXT format untuk kolom B-G (kolom 2-7)
    sheet.getRange(lastRow + 1, 2, data.rows.length, 6).setNumberFormat('@');
    
    return ContentService.createTextOutput(JSON.stringify({
      success: true, rowsAdded: data.rows.length, totalRows: lastRow + data.rows.length
    })).setMimeType(ContentService.MimeType.JSON);
  }
  
  return ContentService.createTextOutput(JSON.stringify({success: false})).setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  var sheet = SpreadsheetApp.openById('YOUR_SHEET_ID').getActiveSheet();
  return ContentService.createTextOutput(JSON.stringify({status: 'ok', totalRows: sheet.getLastRow()})).setMimeType(ContentService.MimeType.JSON);
}
