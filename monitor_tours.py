import requests
from bs4 import BeautifulSoup
import os

URL = "https://www.engelbert.com/tour"
FILE_NAME = "known_tours.txt"

def get_tours_from_site():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        tour_entries = soup.find_all(class_="tour-entry")

        found_tours = []
        for entry in tour_entries:

            venue = entry.find(class_="tour-venue").get_text(strip=True)
            location = entry.find(class_="tour-location").get_text(strip=True)
            date = entry.find(class_="tour-date").get_text(strip=True)

            tour_details = f"{date} | {location} | {venue}"
            found_tours.append(tour_details)

        return found_tours
    except Exception as e:
        print(f"error scanning the site {e}")
        return []

def send_telegram_message(message):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"

#    data = {"chat_id": chat_id, "text": message}
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        if response.status_code == 200:
            print("התראת טלגרם נשלחה בהצלחה!")
        else:
            print(f"שגיאה מטלגרם: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"שגיאה בשליחת הודעת טלגרם: {e}")


def run_check():
    current_tours = get_tours_from_site()

    if not current_tours:
        print("לא נמצאו הופעות באתר. בדוק את החיבור או את ה-class.")
        return

    # קריאת היסטוריה
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            known_tours = f.read().splitlines()
    else:
        known_tours = []

    # זיהוי הופעות חדשות
    new_tours = [t for t in current_tours if t not in known_tours]

    if new_tours:
        if not known_tours:
            print(f"הרצה ראשונה: שומר {len(new_tours)} הופעות קיימות.")
        else:
            print("!!! נמצאו הופעות חדשות !!!")
            alert_text = "<b>נמצאו הופעות חדשות של אנגלברט!</b>\n\n"
            for tour in new_tours:
                print(f"הופעה חדשה: {tour}")
                alert_text += f"📍 {tour}\n"
                # כאן יבוא ה-WhatsApp/Email שלך

            # sending alert
            send_telegram_message(alert_text)

        # עדכון הקובץ
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            for tour in current_tours:
                f.write(tour + "\n")
    else:
        print("בדיקה הושלמה: לא נוספו הופעות חדשות מאז הבדיקה האחרונה.")


if __name__ == "__main__":
    run_check()