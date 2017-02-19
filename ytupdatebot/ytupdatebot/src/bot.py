#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Bot.py"""
from Lib.Config import Config
from telegram.ext import *
from telegram.error import Unauthorized, NetworkError
from telegram.ext.dispatcher import run_async
from telegram import *
from emoji import emojize
import logging
import json
import feedparser
from apscheduler.schedulers.background import BackgroundScheduler
from Lib.Rss import GetFromLink
from Lib.YouTube import YouTube

from emoji import emojize
from uuid import *
import requests
import arrow
from tld import get_tld
import configparser
import datetime
import pytz
import time
import re
import math
import validators
import threading
import ftfy
from tabulate import tabulate
from pprint import pprint

lastUpdate = None
scheduler = None
config = None
tgBot = None
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARN)

logger = logging.getLogger(__name__)

@run_async
def start(bot, update):
    bot.sendMessage(update.message.chat_id, "I'm not your Bot, man")

@run_async
def settings(bot, update):
    bot.sendMessage(update.message.chat_id, "I'm not your Bot, man")

@run_async
def help(bot, update):
    bot.sendMessage(update.message.chat_id, "I'm not your Bot, man")

@run_async
def test(bot, update):
    print(str(update))
    bot.sendMessage(update.message.chat_id, "I'm not your Bot, man")

@run_async
def default(bot, update):
    pprint(str(update))        
    bot.sendMessage(update.message.chat_id, "I'm not your Bot, man")

@run_async
def inline(bot, update):
    query = update.inline_query.query
    results = list()
    results.append(InlineQueryResultArticle(id=uuid4(), title="YoutubeLink",input_message_content=InputTextMessageContent(query)))
    update.inline_query.answer(results)


def callback(bot, update):
    query = update.callback_query
    data = json.loads(str(query.data))
    pprint(data)
    thumbsup = data['up']
    thumbsdown = data['down']
    scream = data['wow']
    if data['cmd'] == 'up':
        thumbsup = thumbsup + 1
    if data['cmd'] == 'down':
        thumbsdown = thumbsdown + 1
    if data['cmd'] == 'wow':
        scream = scream + 1

    bot.editMessageReplyMarkup('@rapde', query.message.message_id, reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton(emojize(':thumbsup: ({0})'.format(thumbsup), use_aliases=True), callback_data='{"cmd":"up","up":'+str(thumbsup)+',"down":'+str(thumbsdown)+',"wow":'+str(scream)+'}'),
                            InlineKeyboardButton(emojize(':thumbsdown: ({0})'.format(thumbsdown), use_aliases=True), callback_data='{"cmd":"down","up":'+str(thumbsup)+',"down":'+str(thumbsdown)+',"wow":'+str(scream)+'}'),
                            InlineKeyboardButton(emojize(':scream: ({0})'.format(scream), use_aliases=True), callback_data='{"cmd":"wow","up":'+str(thumbsup)+',"down":'+str(thumbsdown)+',"wow":'+str(scream)+'}')],
                        ]
        )
    )
        
@run_async
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

@run_async
def postTheRss(bot, rss, lastUpdateDateTime):
    global lastUpdate
    global config
    for ent in rss:
        feed = GetFromLink.Parse(ent)
        for entry in feed.entries:
            if arrow.get(entry['published']) > lastUpdate:
                keyboard = [
                                [InlineKeyboardButton(emojize(':thumbsup:', use_aliases=True), callback_data='{"cmd":"up","up":0,"down":0,"wow":0}'),
                                InlineKeyboardButton(emojize(':thumbsdown:', use_aliases=True), callback_data='{"cmd":"down","up":0,"down":0,"wow":0}'),
                                InlineKeyboardButton(emojize(':scream:', use_aliases=True), callback_data='{"cmd":"wow","up":0,"down":0,"wow":0}')],
                                [InlineKeyboardButton("Video", url=entry['link']),
                                InlineKeyboardButton("Share", switch_inline_query=feed['feed']['link'])]
                            ]
                bot.sendMessage(
                    #config['ChannelName'],
                    "@rapde",
                    emojize(":musical_note: [{title}]({videolink})\n:bust_in_silhouette: [{channel}]({channellink})\nOnline seit {published}", use_aliases=True).format(
                    #config['MessageTemplate'].format(
                        title=entry['title'],
                        videolink=entry['link'],
                        channel=entry['author'],
                        channellink=feed['feed']['link'],
                        published = arrow.get(entry['published']).humanize(locale='de')
                        #duration=datetime.timedelta(seconds=entry['media_starrating']['average'])
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                    )
    pprint(str(lastUpdate))
    lastUpdate = arrow.utcnow()
    


def main():
    global config
    global tgBot
    global scheduler
    global lastUpdate
    withoutErrors = True

    lastUpdate = arrow.get('2017-02-10T02:51:13+00:00')#arrow.utcnow()
    scheduler = BackgroundScheduler()
    config = Config.Read.Config('config.json')
    updater = Updater(config['Bot']['Token'])
    tgBot = updater.bot
    scheduler.add_job(postTheRss, 'interval', minutes=1, start_date=datetime.datetime.now() + datetime.timedelta(seconds=5), id='postUpdatesToTheChannel', args=[tgBot, config['rss'], lastUpdate])
    scheduler.start()

    while withoutErrors:
        try:
            dp = updater.dispatcher
            dp.add_handler(CommandHandler("start", start))
            dp.add_handler(CommandHandler("settings", settings))
            dp.add_handler(CommandHandler("help", help))
            dp.add_handler(CommandHandler("test", test))
            dp.add_handler(CallbackQueryHandler(callback))
            dp.add_handler(InlineQueryHandler(inline))
        
            dp.add_handler(MessageHandler(None, default))

            dp.add_error_handler(error)
        
            updater.start_polling()
            updater.idle()
        except NetworkError:
            time.sleep(5)
        except Unauthorized:
            updater.last_update_id + 1
        except:
            withoutErrors = False 

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(sys.stderr + '\nExiting by user request.\n')
        sys.exit(0)
