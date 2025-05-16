import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router
from aiogram.filters import CommandStart
from dotenv import load_dotenv

# Загрузка токена из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Инициализация бота
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# Шаги FSM
class SalaryForm(StatesGroup):
    choose_department = State()
    choose_employee = State()
    worked_days = State()
    ftd_count = State()

# Данные по сотрудникам
EMPLOYEES = {
    "Ivan": {"rate": 1000, "days_in_month": 22},
    "Anna": {"rate": 1200, "days_in_month": 21},
}

# Клавиатура выбора отдела
start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="DE SALE")],
        [KeyboardButton(text="DE RET")]
    ],
    resize_keyboard=True
)

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Выберите отдел:", reply_markup=start_kb)
    await state.set_state(SalaryForm.choose_department)

@router.message(SalaryForm.choose_department)
async def choose_employee(message: types.Message, state: FSMContext):
    dept = message.text
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=name)] for name in EMPLOYEES.keys()],
        resize_keyboard=True
    )
    await state.update_data(department=dept)
    await message.answer("Выберите сотрудника:", reply_markup=kb)
    await state.set_state(SalaryForm.choose_employee)

@router.message(SalaryForm.choose_employee)
async def input_days(message: types.Message, state: FSMContext):
    await state.update_data(employee=message.text)
    await message.answer("Сколько дней отработал?")
    await state.set_state(SalaryForm.worked_days)

@router.message(SalaryForm.worked_days)
async def input_ftd(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Введите число.")
    await state.update_data(worked_days=int(message.text))
    await message.answer("Сколько FTD?")
    await state.set_state(SalaryForm.ftd_count)

@router.message(SalaryForm.ftd_count)
async def show_result(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Введите число.")
    
    ftd = int(message.text)
    data = await state.get_data()
    name = data["employee"]
    worked_days = data["worked_days"]
    emp_data = EMPLOYEES[name]

    # Расчёт оклада
    daily_rate = emp_data["rate"] / emp_data["days_in_month"]
    salary_part = daily_rate * worked_days

    # Бонус
    if ftd <= 5:
        bonus = 50
    elif ftd <= 15:
        bonus = 75
    else:
        bonus = 0

    bonus_part = ftd * bonus
    total = salary_part + bonus_part

    await message.answer(
        f"Hi, {name}!\n"
        f"You have a payment!\n\n"
        f"Worked days - {worked_days}\n"
        f"FTD Count - {ftd}\n"
        f"Total payment is - ${total:.2f}"
    )
    await state.clear()

# Запуск
async def main():
    await bot.delete_webhook(drop_pending_updates=True)  # Удалить активный webhook
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
