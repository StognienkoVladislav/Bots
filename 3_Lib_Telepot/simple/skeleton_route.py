
import sys
import time
import threading
import random
import config
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent

"""
It works like this:
- First, you send it one of these 4 characters - `c`, `i`, `h`, `f` - and it replies accordingly:
    - `c` - a custom keyboard with various buttons
    - `i` - an inline keyboard with various buttons
    - `h` - hide custom keyboard
    - `f` - force reply
- Press various buttons to see their effects
- Within inline mode, what you get back depends on the **last character** of the query:
    - `a` - a list of articles
    - `p` - a list of photos
    - `b` - to see a button above the inline results to switch back to a private chat with the bot
"""

message_with_inline_keyboard = None


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat: ', content_type, chat_type, chat_id)

    if content_type != 'text':
        return

    command = msg['text'][-1:].lower()

    if command == 'c':
        markup = ReplyKeyboardMarkup(keyboard=[
            ['Plain text', KeyboardButton(text='Text only')],
            [dict(text='Phone', request_contact=True),
                KeyboardButton(text='Location', request_location=True)],
            ])
        bot.sendMessage(chat_id, 'Custom keyboard with various buttons', reply_markup=markup)

    elif command == 'i':
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [dict(text='Telegram URL', url='https://core.telegram.org/')],
            [InlineKeyboardButton(text='Callback - show notification', callback_data='notification')],
            [dict(text='Callback - show alert', callback_data='alert')],
            [InlineKeyboardButton(text='Callback - edit message', callback_data='edit')],
            [dict(text='Switch to using bot inline', switch_inline_query='initial query')],
        ])
        global message_with_inline_keyboard
        message_with_inline_keyboard = bot.sendMessage(chat_id, 'Inline keyboard with various buttons',
                                                       reply_markup=markup)

    elif command == 'h':
        markup = ReplyKeyboardRemove()
        bot.sendMessage(chat_id, 'Hide cutom keyboard', reply_markup=markup)

    elif command == 'f':
        markup = ForceReply()
        bot.sendMessage(chat_id, 'Force reply', reply_markup=markup)


def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print('Callback query: ', query_id, from_id, data)

    if data == 'notification':
        bot.answerCallbackQuery(query_id, text='Notification at top of screen')
    elif data == 'alert':
        bot.answerCallbackQuery(query_id, text='Alert!', show_alert=True)
    elif data == 'edit':
        global message_with_inline_keyboard

        if message_with_inline_keyboard:
            msg_idf = telepot.message_identifier(message_with_inline_keyboard)
            bot.editMessageText(msg_idf, "NEW MESSAGE HERE!!!!")
        else:
            bot.answerCallbackQuery(query_id, text='No previous message to edit')


def on_inline_query(msg):
    def compute():
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        print('{}: Computing for: {}'.format(threading.current_thread().name, query_string))

        articles = [InlineQueryResultArticle(
            id='abcde', title='Telegram', input_message_content=InputTextMessageContent(
                message_text='Telegram is a messaging app'
            )),
            dict(type='article',
                 id='Efnjwf', title='Google', input_message_content=dict(message_text='Google is a search engine'))
        ]
        photo1_url = 'https://core.telegram.org/file/811140934/1/tbDSLHSaijc/fdcc7b6d5fb3354adf'
        photo2_url = 'https://www.telegram.org/img/t_logo.png'
        photos = [InlineQueryResultPhoto(
            id='1231', photo_url=photo1_url, thumb_url=photo1_url),
            dict(type='photo',
                 id='14331', photo_url=photo2_url, thumb_url=photo2_url)]

        result_type = query_string[-1:].lower()

        if result_type == 'a':
            return articles
        if result_type == 'p':
            return photos
        else:
            results = articles if random.randint(0, 1) else photos
            if result_type == 'b':
                return dict(results, switch_pm_text='Back to Bot', switch_pm_parameter='Optional_start_parameter')
            else:
                return dict(results=results)
    answer.answer(msg, compute)


def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print('Chosen Inline Result: ', result_id, from_id, query_string)


bot = telepot.Bot(config.token)
answer = telepot.helper.Answerer(bot)

MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query,
                  'inline_query': on_inline_query,
                  'chosen_inline_result': on_chosen_inline_result}).run_as_thread()
print("Listening...")


# Keep the program running.
while True:
    time.sleep(10)