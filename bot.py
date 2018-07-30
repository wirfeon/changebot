#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import os
import time
import sys
from copy import copy
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Handler
from telegram import Chat
from datetime import datetime
import requests

_port = int(os.environ['PORT'])
_webhook = "%s%s" % (os.environ["WEB_HOOK"], os.environ["BOT_TOKEN"])
_token = os.environ["BOT_TOKEN"]
_location = os.environ["URL_LOCATION"]
_certificate = os.environ["CERTIFICATE"]
_listen = "127.0.0.1"

# Enable logging
logging.basicConfig(stream=sys.stderr, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

def change(bot, update):
    logger.info("Change")
    
    if (update.message.text):
        params = update.message.text.split()

        if (len(params) == 2):
            if (params[0].strip().lower() == "czk"):
                amount = float(params[1].strip())

                reply = requests.get("https://www.revolut.com/api/quote/internal?symbol=USDCZK&symbol=CZKUSD")
                reply = json.loads(reply.text)

                usdczk = 0

                for pair in reply:
                    if (pair["from"] == "CZK"):
                        usdczk += 1 / pair["rate"]                        
                    elif (pair["from"] == "USD"):
                        usdczk += pair["rate"]
                #endif

                usdczk = usdczk / 2
                #update.message.reply_text("USDCZK %.4f" % usdczk)

                reply = requests.get("https://api.coinmarketcap.com/v2/ticker/873/?convert=USD")
                reply = json.loads(reply.text)

                usdxem = 1 / reply["data"]["quotes"]["USD"]["price"]
                #update.message.reply_text("USDXEM %.4f" % usdxem)

                xemczk = usdczk / usdxem
                #update.message.reply_text("XEMCZK %.4f" % xemczk)

                update.message.reply_text("XEM %.4f" % (amount / xemczk))

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.error('Update "%s" caused error "%s"', update, error)

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    logger.info("Creating updater object with token: '%s'" % (_token))

    updater = Updater(_token)

    i = 0
    while i < 3:
        try:
            logger.info("Starting webhook '%s' %d '%s'" % (_listen, _port, _location))
            updater.start_webhook(listen=_listen, port=_port, url_path=_location)
            logger.info("Setting webhook with certificate '%s'" % (_certificate))
            updater.bot.set_webhook(url=_webhook, certificate=open(_certificate, 'rb'), timeout=5000)
            break
        except Exception as e:
            logger.error("Exception: %s" % e)
            updater.stop()

        i += 1
        time.sleep(2)
    #endwhile
 
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text, change))

    # log all errors
    dp.add_error_handler(error)

    logger.info("Running")

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
