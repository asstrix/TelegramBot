from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db import *
import datetime, calendar
from aiogram.fsm.context import FSMContext


async def update_state(user_id, state: FSMContext):
    if user_exists(user_id):
        await state.update_data(user_id=user_id,
                                today_events=get_today_events(user_id),
                                upcoming_events=get_upcoming_events(user_id),
                                completed_events=get_completed_events(user_id))
    else:
        await state.update_data(user_id=0,
                                today_events=[],
                                upcoming_events=[],
                                completed_events=[])


async def main_menu(user_id, state: FSMContext):
    await update_state(user_id, state)
    data = await state.get_data()
    builder = InlineKeyboardBuilder()
    if user_id == data['user_id']:
        builder.button(text='📅 My Calendar', callback_data='calendar')
    else:
        builder.button(text='📅 Calendar', callback_data='calendar')
    builder.button(text='🛈 About', callback_data='about')
    builder.button(text='📞 Contacts', callback_data='contacts')
    builder.adjust(2)
    return builder.as_markup()


async def calendar_menu(user_id, state: FSMContext):
    await update_state(user_id, state)
    data = await state.get_data()
    builder = InlineKeyboardBuilder()
    if user_id == data['user_id']:
        builder.button(text=f"📆 Today {emoji(len(data['today_events'])):\u2003>1}", callback_data='today')
        builder.button(text=f"🌌 Upcoming {emoji(len(data['upcoming_events'])):\u2003>1}", callback_data='upcoming')
        builder.button(text=f"✅ Completed {emoji(len(data['completed_events'])):\u2003>1}", callback_data='completed')
        builder.button(text='➕ Add', callback_data='add_event')
        builder.button(text='🔧 Manage', callback_data='manage_account')
    else:
        builder.button(text='➕ Create', callback_data='create_account')
        builder.button(text='👥 Join', callback_data='join_account')

    builder.button(text='◀ Back', callback_data='back_to_main_menu')
    builder.adjust(2)
    return builder.as_markup()


def choose_duration():
    builder = InlineKeyboardBuilder()
    builder.button(text="All Day", callback_data="all_day")
    builder.button(text="Specific Time", callback_data="specific_time")
    return builder.as_markup()


def manage_account():
    builder = InlineKeyboardBuilder()
    builder.button(text='❌ Delete', callback_data='delete_account')
    builder.button(text='◀ Back', callback_data='back_to_cal_menu')
    builder.adjust(2)
    return builder.as_markup()


def draw_calendar(year=None, month=None):
    now = datetime.datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    builder = InlineKeyboardBuilder()

    # Year navigation
    year_nav = [
        InlineKeyboardButton(text='◀', callback_data=f'year_back|{year}|{month}'),
        InlineKeyboardButton(text=str(year), callback_data='ignore'),
        InlineKeyboardButton(text='▶', callback_data=f'year_forward|{year}|{month}')
    ]
    builder.row(*year_nav)

    # Month navigation
    month_name = calendar.month_name[month]
    month_nav = [
        InlineKeyboardButton(text='◀', callback_data=f'month_back|{year}|{month}'),
        InlineKeyboardButton(text=month_name, callback_data=f'show_months|{year}'),
        InlineKeyboardButton(text='▶', callback_data=f'month_forward|{year}|{month}')
    ]
    builder.row(*month_nav)

    # Days of the week
    days_of_week = [i[0:3] for i in calendar.day_name]
    builder.row(*[InlineKeyboardButton(text=day, callback_data='ignore') for day in days_of_week])

    # Days in month
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        week_buttons = [InlineKeyboardButton(text=str(day) if day != 0 else ' ',
                                             callback_data=f'day|{year}|{month}|{day}') for day in week]
        builder.row(*week_buttons)

    # Back button
    back = InlineKeyboardButton(text='◀ Back', callback_data='back_to_cal_menu')
    builder.row(back)

    return builder.as_markup()


def draw_months(year):
    builder = InlineKeyboardBuilder()
    months = [i for i in calendar.month_name][1:]
    month_buttons = [InlineKeyboardButton(text=month, callback_data=f'select_month|{year}|{i + 1}') for i, month in
                     enumerate(months)]

    for i in range(0, len(month_buttons), 3):
        builder.row(*month_buttons[i:i + 3])
    return builder.as_markup()


def edit_events():
    builder = InlineKeyboardBuilder()
    builder.button(text='️️✏️ Edit', callback_data='event_edit')
    builder.button(text='❌ Delete', callback_data='event_delete')
    builder.button(text='◀ Back', callback_data='back_to_cal_menu')
    builder.adjust(3)
    return builder.as_markup()


def view_events():
    builder = InlineKeyboardBuilder()
    builder.button(text='◀ Back', callback_data='back_to_cal_menu')
    builder.adjust(3)
    return builder.as_markup()


def output_events(events):
    result = ''
    for i, event in enumerate(sorted(events, key=lambda j: datetime.datetime.strptime(j[2], '%Y-%m-%d %H:%M'))):
        name, start_time, end_time, added_by = event[1:]
        if start_time.split(' ')[0] == str(datetime.datetime.now()).split(' ')[0] and start_time.endswith('00:00') and end_time.endswith('23:59'):
            result += f"{i + 1}. {added_by}: {name}, today all day long\n"
        elif start_time.endswith('00:00') and end_time.endswith('23:59'):
            result += f"{i + 1}. {added_by}: {name}, {start_time.split(' ')[0]} all day\n"
        else:
            result += f"{i + 1}. {added_by}: {name}, {start_time} - {end_time.split(' ')[1]}\n"
    return result


def emoji(number):
    emoji_digits = {'0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣',
                    '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣'
                    }
    return ''.join(emoji_digits[digit] for digit in str(number))