import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.db.models import Q
from django.utils.timezone import localtime, now as dj_now
from django.contrib.auth import get_user_model
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))  # bu config papkani import qilishga imkon beradi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from todo.models import Task

User = get_user_model()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

STATUS_CHOICES = {
    'in_class': "📘 Darsda",
    'on_lunch': "🍽 Tushlikda",
    'not_at_office': "🏠 Ishda emas",
    'available': "✅ Ishda",
    'busy': "🔴 Band",
}


async def set_default_commands():
    await bot.set_my_commands(
        [
            types.BotCommand(command="start", description="Botni ishga tushurish"),
            types.BotCommand(command="status", description="Statusni yangilash"),
            types.BotCommand(command="task_status", description="Task statusini yangilash"),
            types.BotCommand(command="tasks", description="Tasklar ro'yxati")
        ]
    )


@sync_to_async
def get_user(telegram_id):
    return User.objects.filter(telegram_id=telegram_id).first()


@dp.message(CommandStart())
async def start(message: types.Message):
    user = await get_user(message.from_user.id)
    if user:
        await message.answer("👋 Hush kelibsiz!")
    else:
        await message.answer("❌ Siz bizning bazamizda yo'qsiz!")


@dp.message(Command("tasks"))
async def tasks(message:types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("Siz ro'yxatdan o'tmagansiz!")
    now = localtime(dj_now())
    tasks = await get_tasks(now.hour, now.minute, now.date())

    for task in tasks:
        users = await get_users(task)
        for user in users:
            if not user.telegram_id:
                continue
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Bajarildi", callback_data=f"status:{task.id}:done")],
                [InlineKeyboardButton(text="🚧 Jarayonda", callback_data=f"status:{task.id}:in_progress")],
                [InlineKeyboardButton(text="❌ Bekor qilindi", callback_data=f"status:{task.id}:cancelled")],
            ])
            try:
                await bot.send_message(
                    chat_id=int(user.telegram_id),
                    text=await generate_task_text(task),
                    parse_mode=ParseMode.HTML,
                    reply_markup=markup
                )
            except Exception as e:
                print(f"Xatolik: {e}")
    return None

@dp.message(Command("status"))
async def set_status(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("Siz ro'yxatdan o'tmagansiz!")

    keyboard = InlineKeyboardBuilder()
    for key, label in STATUS_CHOICES.items():
        keyboard.button( text=label, callback_data=f"set_status:{key}")
    keyboard.adjust(2)
    await message.answer("💼 Statusni tanlang:", reply_markup=keyboard.as_markup())


@dp.callback_query(lambda c: c.data.startswith("set_status"))
async def update_status(callback: types.CallbackQuery):
    _, status_key = callback.data.split(":")
    user = await get_user(callback.from_user.id)
    if user:
        user.status = status_key
        await sync_to_async(user.save)()
        await callback.message.edit_text(f"✅ Status yangilandi: {STATUS_CHOICES[status_key]}")
        await callback.answer()


@sync_to_async
def get_tasks(hour, minute, today):
    return list(Task.objects.filter(
        is_active=True,
        status__in=["pending", "in_progress"],
    ).filter(
        Q(repetition__in=["daily", "weekly", "monthly"]) | Q(due_date=today)
    ))


@sync_to_async
def get_users(task):
    return list(task.assigned_to.all())


@sync_to_async
def update_due_date(task):
    if task.repetition == 'daily':
        task.due_date += timedelta(days=1)
    elif task.repetition == 'weekly':
        task.due_date += timedelta(weeks=1)
    elif task.repetition == 'monthly':
        next_month = task.due_date.replace(day=1) + timedelta(days=32)
        task.due_date = next_month.replace(day=task.due_date.day)
    task.save()


async def generate_task_text(task: Task) -> str:
    return f"""📝 <b>{task.title}</b>
📌 <b>Tavsif:</b> {task.description}
📅 <b>Deadline:</b> {task.due_date}
🔥 <b>Prioritet:</b> {task.priority.title()}
📍 <b>Status:</b> {task.status.title()}
"""


async def send_task_reminders():
    while True:
        now = localtime(dj_now())
        tasks = await get_tasks(now.hour, now.minute, now.date())

        for task in tasks:
            users = await get_users(task)
            for user in users:
                if not user.telegram_id:
                    continue
                try:
                    if task.due_date and task.due_date < now.date() and task.status not in ['done', 'cancelled']:
                        await bot.send_message(chat_id=int(user.telegram_id),
                                               text=f"⚠️ <b>{task.title}</b> vazifasining muddati o'tgan!",
                                               parse_mode=ParseMode.HTML)
                        continue

                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="✅ Bajarildi", callback_data=f"status:{task.id}:done")],
                        [InlineKeyboardButton(text="🚧 Jarayonda", callback_data=f"status:{task.id}:in_progress")],
                        [InlineKeyboardButton(text="❌ Bekor qilindi", callback_data=f"status:{task.id}:cancelled")],
                    ])

                    await bot.send_message(
                        chat_id=int(user.telegram_id),
                        text=await generate_task_text(task),
                        parse_mode=ParseMode.HTML,
                        reply_markup=markup
                    )

                except Exception as e:
                    print(f"Xatolik: {e}")

            if task.repetition != "none" and task.due_date == now.date():
                await update_due_date(task)

        await asyncio.sleep(60)


@dp.callback_query(lambda c: c.data.startswith("status"))
async def task_status_update(callback: types.CallbackQuery):
    _, task_id, status = callback.data.split(":")
    from apps.todo.models import Task
    task = await sync_to_async(Task.objects.get)(id=int(task_id))
    task.status = status
    await sync_to_async(task.save)()
    await callback.message.edit_text(f"✅ Status yangilandi: {status.title()}")


async def main():
    asyncio.create_task(send_task_reminders())
    await set_default_commands()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
