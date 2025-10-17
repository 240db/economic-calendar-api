from flask import Flask, render_template
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

def sanitize(text):
    if text:
        return text.replace(u'\xa0', u' ').strip()
    return None

def get_economic_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Set a realistic user agent
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

        url = "https://sslecal2.forexprostools.com/"
        page.goto(url, wait_until="networkidle")

        # Wait for the table to be loaded
        page.wait_for_selector("#ecEventsTable", timeout=60000)

        content = page.content()
        browser.close()

    soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="ecEventsTable")

    if not table:
        return []

    rows = table.find_all("tr", id=lambda x: x and 'eventRowId' in x)

    data = []
    for row in rows:
        economy_cell = row.find("td", class_="flagCur")
        economy = sanitize(economy_cell.text) if economy_cell else None

        impact_cell = row.find("td", class_="sentiment")
        impact = len(impact_cell.find_all("i", class_="grayFullBullishIcon")) if impact_cell else 0

        event_timestamp = row.get('event_timestamp')

        name_cell = row.find("td", class_="event")
        name = sanitize(name_cell.text) if name_cell else None

        actual_cell = row.find("td", class_="act")
        actual = sanitize(actual_cell.text) if actual_cell else None

        forecast_cell = row.find("td", class_="fore")
        forecast = sanitize(forecast_cell.text) if forecast_cell else None

        previous_cell = row.find("td", class_="prev")
        previous = sanitize(previous_cell.text) if previous_cell else None

        data.append({
            "economy": economy,
            "impact": impact,
            "data": event_timestamp,
            "name": name,
            "actual": actual,
            "forecast": forecast,
            "previous": previous
        })

    return data

@app.route('/')
def index():
    economic_data = get_economic_data()
    return render_template('index.html', events=economic_data)

if __name__ == "__main__":
    app.run(debug=True)