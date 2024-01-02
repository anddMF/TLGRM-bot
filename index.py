import os
import mysql.connector
from mysql.connector import Error
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

conn = mysql.connector.connect(
    host=os.getenv('SQL_HOST'),
    port=os.getenv('SQL_PORT'),
    user=os.getenv('SQL_USER'),
    password=os.getenv('SQL_PASSWORD'),
    database=os.getenv('SQL_DATABASE')
)
cursor = conn.cursor()


# telegram bot token
TOKEN = os.getenv('TLGRM_TOKEN')


# function /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Bem-vindo! Teste o bot enviando uma mensagem')


# function to receive messages
def receive_message(update: Update, context: CallbackContext) -> None:
    # user_id = update.message.from_user.name
    user_id = update.message.from_user.id
    message_text = update.message.text
    print(f'mensagem recebida: {message_text}')

    # cursor.execute('INSERT INTO dados ...')
    # conn.commit()

    update.message.reply_text('Mensagem recebida e salva no banco')


# function to retrieve data from DB
def get_data(update: Update, context: CallbackContext) -> None:
    try:
        user_id = update.message.from_user.id
        proc_result = []
        proc_description = []
        # cursor.execute('SELECT * FROM develop2020.trd2022_event_type WHERE id=%s', (id))
        cursor.callproc('STP_TRD2022_GET_EVENTS')
        proc_data = cursor.stored_results()
        for result in proc_data:
            proc_result = result.fetchall()
            proc_description = result.description
            
        column_names = [column[0] for column in proc_description]

        if proc_result:
            table = list_to_mdtable(proc_result, column_names)

            update.message.reply_text(table, parse_mode='Markdown')
        else:
            update.message.reply_text('Nenhuma mensagem encontrada')
    except Exception as e:
        print(e)


# format list to table in markdown
def list_to_mdtable(list, column_names):
    table = f"```\n{' | '.join(column_names)} |\n"
    for line in list:
        table += ' | '.join(map(str, line)) + ' |\n'
    table += '```'

    return table


# config bot and handlers
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(
    Filters.text & ~Filters.command, receive_message))
dispatcher.add_handler(CommandHandler('get_data', get_data))

# start bot
updater.start_polling()
updater.idle()

conn.close()
