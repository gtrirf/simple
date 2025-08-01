import asyncio
import re
from datetime import datetime, time, date, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, ForceReply
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.db.models import Q
from django.utils.timezone import localtime, now as dj_now
from django.contrib.auth import get_user_model
import django
import sys
import os
from pathlib import Path

# Django setup
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from todo.models import Task, Staff_attendance, TaskComment
from core.models import CustomUser as User


os.environ['TZ'] = 'Asia/Tashkent'

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Constants
STATUS_CHOICES = {
    'in_class': "📘 Darsda",
    'on_lunch': "🍽 Tushlikda",
    'not_at_office': "🏠 Ishda emas",
    'available': "✅ Ishda",
    'busy': "🔴 Band",
}

TASK_STATUS_ACTIONS = {
    'done': '✅ Bajarildi',
    'in_progress': '🔃 Jarayonda',
    'cancelled': '❌ Bekor qilish'
}

PRIORITY_ICONS = {
    'low': '🟢',
    'medium': '🟡',
    'high': '🔴'
}


# Helper Functions
@sync_to_async
def get_user(telegram_id):
    return User.objects.filter(telegram_id=telegram_id).first()


@sync_to_async
def get_active_tasks(user):
    return list(Task.objects.filter(
        assigned_to=user,
        is_active=True,
        status__in=['pending', 'in_progress']
    ).order_by('-due_date'))

@sync_to_async
def update_task_status(task_id, status):
    task = Task.objects.get(id=task_id)
    task.status = status
    task.save()
    return task

@sync_to_async
def create_attendance(user, status):
    Staff_attendance.objects.create(user=user, status=status)


@sync_to_async
def create_comment(task_id, user_id, comment_text):
    task = Task.objects.get(id=task_id)
    user = User.objects.get(id=user_id)
    TaskComment.objects.create(task=task, user=user, comment=comment_text)


@sync_to_async
def get_today_attendance(user):
    today = date.today()
    return Staff_attendance.objects.filter(
        user=user,
        created_at__date=today
    ).exists()


# Command Handlers
@dp.message(CommandStart())
async def start(message: types.Message):
    user = await get_user(message.from_user.id)
    if user:
        await message.answer(
            f"👋 Assalomu alaykum, {user.first_name or user.username}!\n\n"
            "📋 Vazifalaringizni ko'rish: /tasks\n"
            "💼 Holatingizni o'zgartirish: /status\n"
            "📊 Bugungi davomatni belgilash: /checkin"
        )
    else:
        await message.answer(
            "❌ Siz tizimda ro'yxatdan o'tmagansiz!\n"
            "Iltimos, admin bilan bog'laning."
        )

@dp.message(Command("clear"))
async def cmd_clear(message: Message, bot: Bot) -> None:
    try:
        # Все сообщения, начиная с текущего и до первого (message_id = 0)
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        # Если сообщение не найдено (уже удалено или не существует),
        # код ошибки будет "Bad Request: message to delete not found"
        if ex.message == "Bad Request: message to delete not found":
            print("Все сообщения удалены")

@dp.message(Command("tasks"))
async def show_tasks(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("❌ Siz ro'yxatdan o'tmagansiz!")

    tasks = await get_active_tasks(user)
    if not tasks:
        return await message.answer("🎉 Sizda bajarish uchun vazifalar yo'q!")

    await message.answer(f"📋 Sizda {len(tasks)} ta faol vazifa mavjud:")

    for task in tasks:
        text = (
            f"<b>📌 {task.title}</b>\n"
            f"📝 {task.description or 'Tavsif mavjud emas'}\n"
            f"⏳ Deadline: {task.due_date.strftime('%Y-%m-%d') if task.due_date else 'Muddatsiz'}\n"
            f"{PRIORITY_ICONS.get(task.priority, '🟡')} {task.get_priority_display()}\n"
            f"🔄 {task.get_repetition_display()}\n"
            f"📍 Holati: {task.get_status_display()}"
        )

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Bajarildi", callback_data=f"task_done:{task.id}"),
                InlineKeyboardButton(text="🚧 Jarayonda", callback_data=f"task_progress:{task.id}"),
            ],
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"task_cancel:{task.id}"),
                InlineKeyboardButton(text="💬 Izoh qoldirish", callback_data=f"task_comment:{task.id}"),
            ]
        ])

        await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=markup)
        return None
    return None


@dp.message(Command("status"))
async def set_status(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("❌ Siz ro'yxatdan o'tmagansiz!")

    keyboard = InlineKeyboardBuilder()
    for key, label in STATUS_CHOICES.items():
        keyboard.button(text=label, callback_data=f"set_status:{key}")
    keyboard.adjust(2)

    await message.answer("💼 O'z holatingizni tanlang:", reply_markup=keyboard.as_markup())


@dp.message(Command("checkin"))
async def daily_checkin(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("❌ Siz ro'yxatdan o'tmagansiz!")

    # Check if already checked in today
    already_checked = await get_today_attendance(user)
    if already_checked:
        return await message.answer("✅ Siz bugun davomatni allaqachon belgilagansiz!")

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, ishdaman", callback_data="checkin:yes"),
            InlineKeyboardButton(text="❌ Yo'q, kelmadim", callback_data="checkin:no"),
        ]
    ])

    await message.answer(
        "🏢 Bugun ishga keldingizmi?",
        reply_markup=markup
    )


# Callback Handlers
@dp.callback_query(lambda c: c.data.startswith("set_status"))
async def handle_status_update(callback: types.CallbackQuery):
    _, status_key = callback.data.split(":")
    user = await get_user(callback.from_user.id)
    if user:
        await create_attendance(user, status_key)
        await callback.message.edit_text(
            f"✅ Holatingiz yangilandi: {STATUS_CHOICES[status_key]}"
        )
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("task_"))
async def handle_task_action(callback: types.CallbackQuery):
    action, task_id = callback.data.split(":")[0], callback.data.split(":")[1]
    user = await get_user(callback.from_user.id)

    if not user:
        await callback.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
        return

    if action == "task_comment":
        await callback.message.answer(
            f"Izohingizni yuboring (vazifa ID: {task_id}):",
            reply_markup=ForceReply(selective=True)
        )
        await callback.answer()
        return

    # Handle status changes
    status_map = {
        "task_done": "done",
        "task_progress": "in_progress",
        "task_cancel": "cancelled"
    }

    new_status = status_map.get(action)
    if new_status:
        task = await update_task_status(int(task_id), new_status)
        await callback.message.edit_text(
            f"✅ <b>{task.title}</b> vazifasi yangilandi!\n"
            f"📌 Yangi holat: {task.get_status_display()}",
            parse_mode=ParseMode.HTML
        )
    await callback.answer()

@dp.message()
async def handle_comments(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user or not message.text or not message.reply_to_message:
        return

    text0 = message.reply_to_message.text or ""
    # regex yordamida faqat raqamlarni olamiz
    match = re.search(r"vazifa ID[: ]+(\d+)", text0)
    if not match:
        return  # ID topilmasa chetga chiq
    task_id = int(match.group(1))

    try:
        await create_comment(task_id, user.id, message.text)
        await message.answer("✅ Izohingiz qo‘shildi!")
    except Exception as e:
        # real xatoni log qil, foydalanuvchiga oddiy habar
        print(f"[CommentError] {e}")
        await message.answer("❌ Izoh qo‘shishda xatolik yuz berdi.")


@dp.callback_query(lambda c: c.data.startswith("checkin"))
async def handle_checkin(callback: types.CallbackQuery):
    _, response = callback.data.split(":")
    user = await get_user(callback.from_user.id)

    if not user:
        await callback.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
        return

    if response == "yes":
        await create_attendance(user, "available")
        message = "✅ Davomat belgilandi! Ishga kelganingiz uchun rahmat!"
    else:
        await create_attendance(user, "not_at_office")
        message = "❌ Davomat belgilandi. Sababini izoh bilan yozib qoldiring."

    await callback.message.edit_text(message)
    await callback.answer()


@dp.message()
async def handle_comments(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user or not message.text:
        return

    # Check if it's a task comment
    if message.reply_to_message and "vazifa ID" in message.reply_to_message.text:
        try:
            task_id = message.reply_to_message.text.split(":")[1].strip()
            await create_comment(int(task_id), user.id, message.text)
            await message.answer("✅ Izohingiz qo'shildi!")
        except Exception as e:
            print(f"Comment error: {e}")
            await message.answer("❌ Xatolik! Izoh qo'shilmadi.")


# Scheduled Tasks
async def send_daily_checkin():
    while True:
        now = localtime(dj_now()).time()
        if now.hour == 8 and now.minute == 0:  # At 9:00 AM
            users = await sync_to_async(list)(User.objects.exclude(telegram_id__isnull=True))

            for user in users:
                # Skip if already checked in today
                already_checked = await get_today_attendance(user)
                if already_checked:
                    continue

                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Ha, ishdaman", callback_data="checkin:yes"),
                        InlineKeyboardButton(text="❌ Yo'q, kelmadim", callback_data="checkin:no"),
                    ]
                ])

                try:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text="🏢 Bugun ishga keldingizmi?",
                        reply_markup=markup
                    )
                except Exception as e:
                    print(f"Check-in error for {user.telegram_id}: {e}")

            # Wait until tomorrow
            await asyncio.sleep(86400)  # 24 hours
        else:
            # Check every minute
            await asyncio.sleep(60)


async def send_task_reminders():
    while True:
        now = localtime(dj_now())
        tasks = await sync_to_async(list)(Task.objects.filter(
            is_active=True,
            status__in=["pending", "in_progress"],
            sending_time__hour=now.hour,
            sending_time__minute=now.minute
        ))

        for task in tasks:
            users = await sync_to_async(list)(task.assigned_to.all())
            for user in users:
                if not user.telegram_id:
                    continue

                text = (
                    f"🔔 <b>Vazifa eslatmasi</b>\n\n"
                    f"📌 {task.title}\n"
                    f"📝 {task.description or ''}\n"
                    f"⏳ Deadline: {task.due_date.strftime('%Y-%m-%d') if task.due_date else 'Muddatsiz'}\n"
                    f"{PRIORITY_ICONS.get(task.priority, '🟡')} {task.get_priority_display()}"
                )

                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Bajarildi", callback_data=f"task_done:{task.id}"),
                        InlineKeyboardButton(text="🚧 Jarayonda", callback_data=f"task_progress:{task.id}"),
                    ],
                    [
                        InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"task_cancel:{task.id}"),
                        InlineKeyboardButton(text="💬 Izoh qoldirish", callback_data=f"task_comment:{task.id}"),
                    ]
                ])

                try:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=markup
                    )
                except Exception as e:
                    print(f"Reminder error: {e}")

        await asyncio.sleep(60)


# Main Function
async def main():
    # Start scheduled tasks
    asyncio.create_task(send_daily_checkin())
    asyncio.create_task(send_task_reminders())

    # Set bot commands
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Botni ishga tushurish"),
        types.BotCommand(command="tasks", description="Vazifalarni ko'rish"),
        types.BotCommand(command="status", description="Holatni yangilash"),
        types.BotCommand(command="checkin", description="Bugungi davomatni belgilash"),
        types.BotCommand(command="clear", description="chatni tozalash")
    ])

    # Start polling
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
