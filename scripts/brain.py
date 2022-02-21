import json
import time
import threading
from pywebpush import webpush, WebPushException
import requests
from bs4 import BeautifulSoup
from .polishing_methods import extract_chapter_number
from .database import Manga

WEBSITE = "https://m.mangabat.com/"

class Brain:

    def __init__(self, db):
        self.db = db
        # self.begin_checking()

    def search_for_manga(self, query):
        query = query.replace(" ", "_")
        response = requests.get(f"{WEBSITE}search/manga/{query}")
        response.raise_for_status()
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        panel_search_story = soup.find(class_="panel-list-story")
        if panel_search_story is None:
            return []

        items = panel_search_story.find_all(class_="list-story-item")
        manga = []
        for item in items:
            manga.append({
                "img": item.select_one(".img-loading")["src"],
                "title": item.select_one(".item-title").get_text(),
                "latest chapter": item.select_one(".item-chapter").get_text(),
                "url": item.select_one(".item-title")["href"]
            })
        return manga

    def get_details(self, url):
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        status = "Unknown"
        for row in soup.select(".variations-tableInfo tbody tr"):
            if "Status :" in row.select_one(".table-label").get_text():
                status = row.select_one(".table-value").get_text()
                break

        desc = soup.select_one("#panel-story-info-description").get_text().strip()
        desc = desc[desc.find(":")+2:600]

        details = {
            "title": soup.select_one(".story-info-right h1").get_text(),
            "description": desc,
            "status": status,
            "latest_chapter": extract_chapter_number(soup.select_one('.chapter-name').get_text()),
            "thumbnail": soup.select_one(".story-info-left .info-image .img-loading")["src"],
            "url": url,
            "website": "read.mangabat.com"
        }

        return details

    def get_latest_chapter(self, url):
        response = requests.get(url)
        if response.status_code != 200: return
        soup = BeautifulSoup(response.content, "html.parser")
        element = soup.select_one(".chapter-name")
        chapter_num = extract_chapter_number(element.get_text())
        return chapter_num

    def run_checks(self):
        print("Beginning check!")
        all_manga = Manga.query.all()
        for manga in all_manga:
            current_chapter = self.get_latest_chapter(manga.url)
            if current_chapter > manga.latest_chapter:
                print(f"New chapter {current_chapter}")
                manga.latest_chapter = current_chapter
                self.db.session.commit()

                for subscription in manga.subscriptions:
                    try:
                        webpush(subscription.endpoint,
                                json.dumps({
                                    "title": manga.title,
                                    "body": f"New chapter {manga.latest_chapter}! Go read it now!",
                                }),
                                vapid_private_key="-RMX3o_klK67WLgFA2vc6IURRwqxkUQzDkHyh4bWAEw",
                                vapid_claims={"sub": "mailto:testemail@gmail.com"})
                    except WebPushException as e:
                        print(f"Failed to push to {subscription.user.email}")
                        print(e)
            time.sleep(0)
        print("Ended the check'")

    def checking_loop(self):
        print("Checking loop ON!")
        while True:
            self.run_checks()
            time.sleep(1800)

    def begin_checking(self):
        thread = threading.Thread(target=self.checking_loop)
        thread.start()