# -*- coding: utf-8 -*-

import ssl
import requests
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup

# Configure SSL
ssl._create_default_https_context = ssl._create_unverified_context

# Target companies for monitoring
target_companies = ["中工", "合一", "興富發", "鑽石生技", "中天"]

# Timestamps for tracking updates
old_time_stamp = "2023/03/26;09:59:49"
new_time_stamp = "0"

def Stockparser(url):
    global old_time_stamp
    global new_time_stamp
    repeat_flag = 1
    msg = ""

    try:
        # Fetch and parse the webpage
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Error fetching URL: {e}")
        sleep(300)
        return '', 1

    # Locate the table with the required data
    table = soup.find("table", attrs={"class": "hasBorder"})
    if not table:
        print("No table found!")
        return '', 1

    try:
        # Extract rows from the table
        rows = table.find_all("tr")
    except Exception as e:
        print(f"Error processing table rows: {e}")
        return '', 1

    # Determine the range of rows to check
    row_limit = min(300, len(rows) - 1)
    rows_range = range(row_limit, 0, -1)  # Reverse order to prioritize newest data
    max_count = 10  # Limit to 10 results

    try:
        for i in rows_range:
            cols = rows[i].find_all("td")
            if len(cols) < 5:  # Ensure the row has enough columns
                continue

            company_name = cols[1].text.strip()
            content = cols[4].text.strip()
            new_date = cols[2].text.strip()
            new_time = cols[3].text.strip()

            # Convert ROC date to standard format
            new_date_list = new_date.split("/")
            new_date_year = int(new_date_list[0]) + 1911
            new_date_month = int(new_date_list[1])
            new_date_day = int(new_date_list[2])
            new_date_str = f"{new_date_year}/{new_date_month:02d}/{new_date_day:02d}"
            new_time_stamp = f"{new_date_str};{new_time}"

            # Compare timestamps to filter new data
            old_datetime = datetime.strptime(old_time_stamp, '%Y/%m/%d;%H:%M:%S')
            new_datetime = datetime.strptime(new_time_stamp, '%Y/%m/%d;%H:%M:%S')

            if new_datetime > old_datetime and company_name in target_companies:
                print(f"New data found for: {company_name}")
                old_time_stamp = new_time_stamp
                msg += f"{company_name}: {new_time_stamp}: {content}\n"
                max_count -= 1

            if max_count == 0:
                break

    except Exception as e:
        print(f"Error during row processing: {e}")
        return msg, repeat_flag

    if msg:
        repeat_flag = 0

    return msg, repeat_flag

def LineNotify(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {"message": msg}
    try:
        requests.post("https://notify-api.line.me/api/notify", headers=headers, params=params)
    except Exception as e:
        print(f"Error sending LINE notification: {e}")

def DiscordNotify(webhook_url, msg):
    headers = {"Content-Type": "application/json"}
    payload = {"content": msg}
    try:
        response = requests.post(webhook_url, json=payload, headers=headers)
        if response.status_code != 204:
            print("Failed to send Discord message.")
    except Exception as e:
        print(f"Error sending Discord notification: {e}")

if __name__ == "__main__":
    webhook_url = "https://discordapp.com/api/webhooks/1308682093462683709/jUSEVpXsVDoKiF-aFnQKTmcx2gXDUKuN213R8QAy5xTJxMvVNoquRpUwYYDHoOae41ye"
    token = "82JoR58J42E8z3VTQ60U3RMWk5DysWiHe60WN8uWbRX"  # LINE Notify token
    url = "https://mops.twse.com.tw/mops/web/t05sr01_1"  # Target URL

    while True:
        now = datetime.now()
        current_time = now.strftime("%Y/%m/%d %H:%M:%S")
        print(f"Checking data at: {current_time}")

        msg, repeat_flag = Stockparser(url)
        if repeat_flag == 0:
            notification_msg = f"最新文章列表：\n{msg}\n{url}"
            print(notification_msg)
            LineNotify(token, notification_msg)
            DiscordNotify(webhook_url, notification_msg)

        sleep(300)  # Wait for 5 minutes before next check

