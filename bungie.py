from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
from dotenv import load_dotenv
from time import mktime

import feedparser
import sqlite3
import sys
import os

load_dotenv()
DB_PATH = os.getenv('DB_PATH')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

try:
    con = sqlite3.connect(DB_PATH)
except sqlite3.Error as e:
    sys.exit(1)

with con:
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS posts(id TEXT NOT NULL);')

    webhook = DiscordWebhook(url=WEBHOOK_URL)

    feed = feedparser.parse('https://nitter.cc/BungieHelp/rss')

    for entry in reversed(feed['entries']):
        cur.execute('SELECT * FROM posts WHERE id=?;', (entry['id'],))
        record = cur.fetchone()
        if record is None:
            embed = DiscordEmbed(
                description=entry['title'],
                color='1B95E0'
            )

            embed.set_author(name=feed['channel']['title'], url=feed['channel']['image']['link'],
                             icon_url=feed['channel']['image']['href'])

            dt = datetime.fromtimestamp(mktime(entry['published_parsed']))

            embed.set_timestamp(dt.timestamp())

            webhook.add_embed(embed)

            cur.execute('INSERT INTO posts VALUES(?, ?);', (entry['id'], dt,))

            if len(webhook.embeds) == 10:
                response = webhook.execute()
                webhook.embeds = []

    cur.execute('DELETE FROM posts WHERE id NOT IN (SELECT id FROM posts ORDER BY DATE DESC LIMIT 20)')

if len(webhook.embeds) > 0:
    response = webhook.execute()
con.commit()

