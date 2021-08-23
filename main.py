# coding=utf-8
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import httplib2
from apiclient import discovery
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

import auth, gmail
SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail Bot'

authInst = auth.auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
credentials = authInst.get_credentials()

http = credentials.authorize(httplib2.Http())
service = discovery.build('gmail', 'v1', http=http)


greeting = u'Че пацаны аниме?:)'

def start(bot, update):
    update.message.reply_text(greeting.encode('utf8'))

def caps(bot, update, args):
    text_caps = ' '.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id, text=text_caps)

def help(bot, update):
    update.message.reply_text('HELP!')


def echo(bot, update):
    update.message.reply_text(update.message.text)


# Send the last message in Important Mail when the /getgmail command is entered
def send_gmail_message(bot, update, args):
    if not args:
        n = 0
    else:
        n = int(args[0])
    gmailInst = gmail.gmail(service, "me", ["Label_1"])
    msg_id = gmailInst.listMessagesWithLabels()[n]["id"]
    gmail_message = gmailInst.getMessageBody(msg_id)
    bot.send_message(chat_id=update.message.chat_id, text=gmail_message)

# Same thing as the above function but Send the messages periodically
def callback_gmail(bot, job):
    gmailInst = gmail.gmail(service, "me", ["Label_1"])
    msg_id = gmailInst.listMessagesWithLabels()[0]["id"]
    gmail_message = gmailInst.getMessageBody(msg_id)
    bot.send_message(chat_id=job.context, text=gmail_message)

def callback_gmail_timer(bot, update, job_queue):
    bot.send_message(chat_id=update.message.chat_id, text='Now this bot will send you updates on Important Mail periodically')
    job_queue.run_repeating(callback_gmail, interval=60, first=0, context=update.message.chat_id)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("538873805:AAGbXW2PgMtulE6sunFFfwDkPytEwNfqDoM")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Instantiate a JobQueue to send emails periodically
    j = updater.job_queue

    # on different commands - answer in Telegram
    dp.add_handler( CommandHandler("start", start) )
    dp.add_handler( CommandHandler('caps', caps, pass_args=True) )
    dp.add_handler( CommandHandler("help", help) )
    dp.add_handler( CommandHandler("getgmail", send_gmail_message, pass_args=True) )
    dp.add_handler( CommandHandler('getgmailp', callback_gmail_timer, pass_job_queue=True) )
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler( MessageHandler(Filters.text, echo) )
    dp.add_error_handler(error)


    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()