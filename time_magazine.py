from datetime import datetime

import psycopg2
import requests
from bs4 import BeautifulSoup
from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
from environs import Env


def embed_to_discord(cover: str):

    # create embed object for webhook
    today = datetime.now().strftime("%B %d, %Y")
    embed = DiscordEmbed(title="Time Magazine " + today, color="ba0505")

    # set image
    embed.set_image(url="attachment://full_quality_covers.png")

    # set footer
    embed.set_footer(text='Made By Ibrahim Mudassar')

    # add embed object to webhook(s)
    for webhook_url in env.list("WEBHOOKS"):
        webhook = DiscordWebhook(url=webhook_url)

        with open("full_quality_cover.png", "rb") as f:
            webhook.add_file(file=f.read(), filename='full_quality_cover.png')

        webhook.add_embed(embed)
        webhook.execute()


env = Env()
env.read_env()  # read .env file, if it exists


# Get today's magazine cover


resp = requests.get("https://time.com/magazine/us/")

soup = BeautifulSoup(resp.content, "html.parser")

cover_class = soup.select_one("figure.cover-article-image")
cover = cover_class.select_one("img")["src"]
full_quality_cover = cover.split("?")[0]  # delete parameters


# Check if today's cover has already been posted


conn = psycopg2.connect(dbname=env("DBNAME"),
                        user=env("DBNAME"),
                        password=env("DBPASSWORD"),
                        host=env("DBHOST"))
cur = conn.cursor()
cur.execute("SELECT * FROM coverlinks")
records = [i[0] for i in cur.fetchall()]  # single element tuple to string


# If it hasn't then post it and add it to the db


if full_quality_cover not in records:
    img_data = requests.get(full_quality_cover).content
    with open('full_quality_cover.png', 'wb') as handler:
        handler.write(img_data)

    embed_to_discord(full_quality_cover)
    cur.execute("INSERT INTO coverlinks VALUES(%s);", (full_quality_cover,))
    # Make the changes to the database persistent
    conn.commit()
    # Close communication with the database
    cur.close()
    conn.close()
