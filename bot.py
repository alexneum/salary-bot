import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

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

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Выберите отдел:", reply_markup=start_kb)
    await state.set_state(SalaryForm.choose_department)

@router.message(SalaryForm.choose_department)
async def choose_employee(message: types.Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for name in EMPLOYEES:
        kb.add(KeyboardButton(name))
    await state.update_data(department=message.text)
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
    
    daily_rate = emp_data["rate"] / emp_data["days_in_month"]
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
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
