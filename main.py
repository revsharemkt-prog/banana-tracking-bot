
import gspread
from google.oauth2.service_account import Credentials
from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import os

# GOOGLE SHEETS AUTH (GITHUB SECRET)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])

creds = Credentials.from_service_account_info(
    creds_json,
    scopes=SCOPES
)

client = gspread.authorize(creds)

sheet = client.open_by_key(
    "1qVvlUiLqyh93LsfdFHFwKLEMUra3qlrDIMSbqNhTVV8"
).sheet1

rows = sheet.get_all_values()

def color_row_rto(sheet, row_number):
    sheet.format(f"A{row_number}:G{row_number}", {
        "backgroundColor": {
            "red": 1,
            "green": 0.6,
            "blue": 0.6
        }
    })

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for row_number, row in enumerate(rows[1:], start=2):

        if len(row) < 6:
            continue

        tracking = row[5].strip()
        current_status = row[1].strip() if len(row) > 1 else ""

        if not tracking:
            continue

        # SKIP ONLY DELIVERED
        if current_status.upper() == "DELIVERED":
            continue

        is_new = (current_status == "")

        page.goto("https://bananaexpressgroup.com/tracking/")
        page.wait_for_timeout(2000)

        page.locator('input[name="trackno"]').fill(tracking)
        page.get_by_text("Track Now").click()

        page.wait_for_timeout(5000)

        all_rows = page.locator("tr").all_inner_texts()

        new_status = current_status if current_status else "Unknown"

        for r in all_rows:
            text = r.upper()

            if "RTO" in text:
                new_status = "RTO"
                break

            elif "OUT FOR DELIVERY" in text:
                new_status = "Out for Delivery"

            elif "DELIVERED" in text:
                new_status = "Delivered"
                break

        # UPDATE SHEET
        if is_new or current_status != new_status:

            sheet.update_cell(row_number, 2, new_status)

            if new_status == "RTO":
                color_row_rto(sheet, row_number)

        # UPDATE TIMESTAMP (COLUMN G)
        sheet.update_cell(
            row_number,
            7,
            datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )

    browser.close()

print("Finished")
