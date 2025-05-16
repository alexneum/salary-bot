import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class SalaryForm(StatesGroup):
    choose_department = State()
    choose_employee = State()
    worked_days = State()
    ftd_count = State()

EMPLOYEES = {
    "Ivan": {"rate": 1000, "days_in_month": 22},
    "Anna": {"rate": 1200, "days_in_month": 21},
}

start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(KeyboardButton("DE SALE"), KeyboardButton("DE RET"))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Выберите отдел:", reply_markup=start_kb)
    await SalaryForm.choose_department.set()

@dp.message_handler(state=SalaryForm.choose_department)
async def choose_employee(message: types.Message, state: FSMContext):
    dept = message.text
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for name in EMPLOYEES.keys():
        kb.add(KeyboardButton(name))
    await message.answer("Выберите сотрудника:", reply_markup=kb)
    await state.update_data(department=dept)
    await SalaryForm.choose_employee.set()

@dp.message_handler(state=SalaryForm.choose_employee)
async def get_worked_days(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(employee=name)
    await message.answer("Сколько дней отработал?")
    await SalaryForm.worked_days.set()

@dp.message_handler(state=SalaryForm.worked_days)
async def get_ftd(message: types.Message, state: FSMContext):
    try:
        worked_days = int(message.text)
    except ValueError:
        return await message.answer("Введите число.")
    await state.update_data(worked_days=worked_days)
    await message.answer("Сколько FTD?")
    await SalaryForm.ftd_count.set()

@dp.message_handler(state=SalaryForm.ftd_count)
async def calculate(message: types.Message, state: FSMContext):
    try:
        ftd = int(message.text)
    except ValueError:
        return await message.answer("Введите число.")

    data = await state.get_data()
    name = data['employee']
    worked_days = data['worked_days']
    emp_data = EMPLOYEES[name]

    daily_rate = emp_data['rate'] / emp_data['days_in_month']
    salary_part = daily_rate * worked_days

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

    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
