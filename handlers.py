from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot, Router, types
from keyboards import *
from states import EventState
from cfg import API_TOKEN


router = Router()
bot = Bot(token=API_TOKEN)


async def delete_previous_messages(message: types.Message, amount=1):
    try:
        for i in range(message.message_id, message.message_id - amount, -1):
            await bot.delete_message(message.chat.id, i)
    except Exception as e:
        pass


# Main menu
@router.callback_query(lambda x: x.data == 'calendar')
async def manage_calendar(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(today_events=get_today_events(call.from_user.id),
                            upcoming_events=get_upcoming_events(call.from_user.id),
                            completed_events=get_completed_events(call.from_user.id))
    keyboard = await calendar_menu(call.from_user.id, state)
    await call.message.edit_text('Your calendar:', reply_markup=keyboard)


@router.callback_query(lambda c: c.data == 'about')
async def tell_about(call: types.CallbackQuery, state: FSMContext):
    keyboard = await main_menu(call.from_user.id, state)
    text = """The Bot is created to schedule tasks, events, actions. You can use it yourself or in groups, e.g.\
 like family shared calendar, enjoy!!!"""
    try:
        if call.message.text != text:
            await call.message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest:
        pass


@router.callback_query(lambda c: c.data == 'contacts')
async def show_contacts(call: types.CallbackQuery, state: FSMContext):
    keyboard = await main_menu(call.from_user.id, state)
    try:
        await call.message.edit_text('telegram: @francegid', reply_markup=keyboard)
    except TelegramBadRequest:
        pass


# Account menu
@router.callback_query(lambda c: c.data == 'today')
async def today(call: types.CallbackQuery, state: FSMContext):
    await update_state(call.from_user.id, state)
    data = await state.get_data()
    try:
        await call.message.edit_text(f"Today\'s events:\n{output_events(data['today_events'])}",
                                     reply_markup=edit_events())
        await state.update_data(delete_from='today_events', edit_from='today_events')
    except TelegramBadRequest:
        pass
    except KeyError:
        keyboard = await main_menu(call.from_user.id, state)
        await call.message.edit_text('Calendar menu', reply_markup=keyboard)


@router.callback_query(lambda c: c.data == 'upcoming')
async def upcoming(call: types.CallbackQuery, state: FSMContext):
    await update_state(call.from_user.id, state)
    data = await state.get_data()
    try:
        await call.message.edit_text(f"Upcoming events:\n{output_events(data['upcoming_events'])}",
                                     reply_markup=edit_events())
        await state.update_data(delete_from='upcoming_events', edit_from='upcoming_events')
    except TelegramBadRequest:
        pass
    except KeyError:
        keyboard = await main_menu(call.from_user.id, state)
        await call.message.edit_text('Calendar menu', reply_markup=keyboard)


@router.callback_query(lambda c: c.data == 'completed')
async def completed_events(call: types.CallbackQuery, state: FSMContext):
    await update_state(call.from_user.id, state)
    data = await state.get_data()
    try:
        await call.message.edit_text(f"Completed events:\n{output_events(data['completed_events'])}",
                                     reply_markup=view_events())
    except TelegramBadRequest:
        pass
    except KeyError:
        keyboard = await main_menu(call.from_user.id, state)
        await call.message.edit_text('Calendar menu', reply_markup=keyboard)


@router.callback_query(lambda c: c.data == 'manage_account')
async def manage_acc(call: types.CallbackQuery):
    try:
        await call.message.edit_text('Account manager', reply_markup=manage_account())
    except TelegramBadRequest:
        pass


# Manage account
@router.callback_query(lambda c: c.data == 'create_account')
async def add_account(call: types.CallbackQuery, state: FSMContext):
    result = add_user(call.from_user.id, call.from_user.username, call.from_user.first_name)
    if result:
        try:
            await delete_previous_messages(call.message)
            await call.answer(f'{result}', show_alert=True)
            keyboard = await calendar_menu(call.from_user.id, state)
            await call.message.answer('Calendar menu', reply_markup=keyboard)
        except TelegramBadRequest:
            pass
    else:
        await delete_previous_messages(call.message)
        await call.message.answer("""Failed to create your account.\nPlease specify your username in TG settings\n
        https://telegram.org/faq?setln=en#q-what-are-usernames-how-do-i-get-one\n
        then send /start command.""")


@router.callback_query(lambda c: c.data == 'join_account')
async def get_account(call: types.CallbackQuery, state: FSMContext):
    await delete_previous_messages(call.message)
    await call.message.answer('Enter account name you would like to join:')
    await state.update_data(last_callback=call.id)
    await state.set_state(EventState.join_account)


@router.message(EventState.join_account)
async def get_event_id(message: types.Message, state: FSMContext):
    await delete_previous_messages(message, 2)
    parent_acc = message.text
    result = s_join_account(parent_acc, message.from_user.id, message.from_user.username, message.from_user.first_name)
    if result:
        data = await state.get_data()
        last_callback = data.get("last_callback")
        if last_callback:
            await bot.answer_callback_query(last_callback, result, show_alert=True)
            keyboard = await calendar_menu(message.from_user.id, state)
            await message.answer('Calendar menu', reply_markup=keyboard)
            await state.clear()
    else:
        await delete_previous_messages(message, 2)
        await message.answer("""Failed to join your account.Please specify your username in TG settings\n
        https://telegram.org/faq?setln=en#q-what-are-usernames-how-do-i-get-one\n
        then send /start command.""")
        await state.clear()


@router.callback_query(lambda c: c.data == 'delete_account')
async def delete_account(call: types.CallbackQuery, state: FSMContext):
    result = delete_user(call.from_user.id)
    try:
        await delete_previous_messages(call.message)
        await call.answer(f'{result}', show_alert=True)
        keyboard = await calendar_menu(call.from_user.id, state)
        await call.message.answer('Calendar menu', reply_markup=keyboard)
        await state.clear()
    except TelegramBadRequest:
        pass


# Manage events
@router.callback_query(lambda c: c.data == 'add_event')
async def add_event(call: types.CallbackQuery, state: FSMContext):
    await delete_previous_messages(call.message)
    await state.update_data(event_type='add_event')
    await call.message.answer(f"Please enter the event title:")
    await state.set_state(EventState.title)


@router.callback_query(lambda c: c.data == 'event_edit')
async def upd_event(call: types.CallbackQuery, state: FSMContext):
    await delete_previous_messages(call.message)
    data = await state.get_data()
    if data['edit_from'] == 'upcoming_events':
        result = get_upcoming_events(call.from_user.id)
    else:
        result = get_today_events(call.from_user.id)
    await call.message.answer(f"Choose event to edit:\n{output_events(result)}")
    await state.set_state(EventState.edit_event)


@router.message(EventState.edit_event)
async def get_event_id(message: types.Message, state: FSMContext):
    await delete_previous_messages(message, 2)
    await state.update_data(event_type='edit_event', event_id=int(message.text))
    await message.answer(f"Please enter the event title:")
    await state.set_state(EventState.title)


@router.callback_query(lambda c: c.data == 'event_delete')
async def get_event_id(call: types.CallbackQuery, state: FSMContext):
    await delete_previous_messages(call.message)
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='◀ Back', callback_data='back_to_cal_menu')
    data = await state.get_data()
    if data['delete_from'] == 'upcoming_events':
        result = get_upcoming_events(call.from_user.id)
    else:
        result = get_today_events(call.from_user.id)
    await call.message.answer(f"Choose event to delete:\n{output_events(result)}")
    await state.update_data(last_callback=call.id)
    await state.set_state(EventState.delete_event)


@router.message(EventState.delete_event)
async def delete_event(message: types.Message, state: FSMContext):
    await delete_previous_messages(message, 2)
    event_id = int(message.text)
    data = await state.get_data()
    if data['delete_from'] == 'upcoming_events':
        del_result = s_delete_event(data['upcoming_events'][event_id - 1][0])
    else:
        del_result = s_delete_event(data['today_events'][event_id - 1][0])
    last_callback = data.get("last_callback")
    if last_callback:
        await bot.answer_callback_query(last_callback, del_result, show_alert=True)
    keyboard = await calendar_menu(message.from_user.id, state)
    await message.answer('Calendar menu', reply_markup=keyboard)
    await state.clear()


@router.message(EventState.title)
async def event_title(message: types.Message, state: FSMContext):
    await delete_previous_messages(message, 2)
    await state.update_data(title=message.text)
    await message.answer('Please enter the event description:')
    await state.set_state(EventState.description)


@router.message(EventState.description)
async def event_desc(message: types.Message, state: FSMContext):
    await delete_previous_messages(message, 2)
    await state.update_data(description=message.text)
    await message.answer("Choose event's time interval:", reply_markup=choose_duration())


@router.callback_query(lambda c: c.data == "all_day")
async def event_whole_day(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_text('Select day', reply_markup=draw_calendar())
        await state.update_data(duration='all_day')
    except TelegramBadRequest:
        pass


@router.callback_query(lambda c: c.data == "specific_time")
async def event_specific_time(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.edit_text('Select a day', reply_markup=draw_calendar())
        await state.update_data(duration='specific_time')
    except TelegramBadRequest:
        pass


@router.callback_query(lambda c: c.data.startswith('day'))
async def event(call: types.CallbackQuery, state: FSMContext):
    await delete_previous_messages(call.message)
    result = ''
    data = await state.get_data()
    date = call.data.split('|')
    year, month, day = int(date[1]), int(date[2]), int(date[3])
    await state.update_data(year=year, month=month, day=day)
    if data['duration'] == 'all_day':
        if year is not None and month is not None and day is not None:
            start_time = datetime.datetime(year, month, day, 0, 0).strftime("%Y-%m-%d %H:%M")
            end_time = datetime.datetime(year, month, day, 23, 59).strftime("%Y-%m-%d %H:%M")
            if data['event_type'] == 'add_event':
                result = s_add_event(call.from_user.id, data['title'], data['description'], start_time, end_time)
            elif data['event_type'] == 'edit_event':
                event_id = data['event_id']
                if data['edit_from'] == 'upcoming_events':
                    result = s_update_event(data['upcoming_events'][event_id - 1][0], data['title'],
                                            data['description'], start_time, end_time, call.from_user.id)
                else:
                    result = s_update_event(data['today_events'][event_id - 1][0], data['title'],
                                            data['description'], start_time, end_time, call.from_user.id)
            await call.answer(result, show_alert=True)
            keyboard = await calendar_menu(call.from_user.id, state)
            await call.message.answer('Calendar menu', reply_markup=keyboard)
            pass
        else:
            await call.answer("A date was not selected.", show_alert=True)
            keyboard = await calendar_menu(call.from_user.id, state)
            await call.message.answer('Calendar menu', reply_markup=keyboard)
        await state.clear()
    elif data['duration'] == 'specific_time':
        await call.message.answer('Please enter start time in HH:MM format')
        await state.set_state(EventState.start_time)
    elif data['duration'] == 'spec_end_time':
        await call.message.answer('Please enter end time in HH:MM format')
        await state.update_data(last_callback=call.id)
        await state.set_state(EventState.end_time)


@router.message(EventState.start_time)
async def event_start_time(message: types.Message, state: FSMContext):
    await delete_previous_messages(message, 2)
    data = await state.get_data()
    year, month, day = data['year'], data['month'], data['day']
    hours, minutes = int(message.text.split(':')[0]), int(message.text.split(':')[1])
    start_time = datetime.datetime(year, month, day, hours, minutes).strftime("%Y-%m-%d %H:%M")
    await state.update_data(start_time=start_time, duration='spec_end_time')
    await message.answer('Select event end day', reply_markup=draw_calendar())


@router.message(EventState.end_time)
async def event_end_time(message: types.Message, state: FSMContext):
    result = ''
    await delete_previous_messages(message, 2)
    data = await state.get_data()
    year, month, day = data['year'], data['month'], data['day']
    hours, minutes = int(message.text.split(':')[0]), int(message.text.split(':')[1])
    end_time = datetime.datetime(year, month, day, hours, minutes).strftime("%Y-%m-%d %H:%M")
    await state.update_data(end_time=end_time)
    if data['event_type'] == 'add_event':
        result = s_add_event(message.from_user.id, data['title'], data['description'], data['start_time'], end_time)
    elif data['event_type'] == 'edit_event':
        event_id = data['event_id']
        if data['edit_from'] == 'upcoming_events':
            result = s_update_event(data['upcoming_events'][event_id - 1][0], data['title'],
                                    data['description'], data['start_time'], end_time, message.from_user.id)
        else:
            result = s_update_event(data['today_events'][event_id - 1][0], data['title'],
                                    data['description'], data['start_time'], end_time, message.from_user.id)
    last_callback = data.get("last_callback")
    if last_callback:
        await bot.answer_callback_query(last_callback, result, show_alert=True)
    keyboard = await calendar_menu(message.from_user.id, state)
    await message.answer('Calendar menu', reply_markup=keyboard)
    await state.clear()


# Calendar buttons
@router.callback_query(lambda c: c.data.startswith('year_back'))
async def year_back(call: types.CallbackQuery):
    data = call.data.split('|')
    year, month = int(data[1]) - 1, int(data[2])
    await call.message.edit_reply_markup(reply_markup=draw_calendar(year, month))


@router.callback_query(lambda c: c.data.startswith('year_forward'))
async def year_forward(call: types.CallbackQuery):
    data = call.data.split('|')
    year, month = int(data[1]) + 1, int(data[2])
    await call.message.edit_reply_markup(reply_markup=draw_calendar(year, month))


@router.callback_query(lambda c: c.data.startswith('month_back'))
async def month_back_(call: types.CallbackQuery):
    data = call.data.split('|')
    year, month = int(data[1]), int(data[2]) - 1
    if month < 1:
        month = 12
        year -= 1
    await call.message.edit_reply_markup(reply_markup=draw_calendar(year, month))


@router.callback_query(lambda c: c.data.startswith('select_month'))
async def select_month(call: types.CallbackQuery):
    data = call.data.split('|')
    year, month = int(data[1]), int(data[2])
    await call.message.edit_reply_markup(reply_markup=draw_calendar(year, month))


@router.callback_query(lambda c: c.data.startswith('show_months'))
async def show_months_handler(call: types.CallbackQuery):
    data = call.data.split('|')
    year = int(data[1])
    await call.message.edit_reply_markup(reply_markup=draw_months(year))


@router.callback_query(lambda c: c.data.startswith('month_forward'))
async def month_forward_(call: types.CallbackQuery):
    data = call.data.split('|')
    year, month = int(data[1]), int(data[2]) + 1
    if month > 12:
        month = 1
        year += 1
    await call.message.edit_reply_markup(reply_markup=draw_calendar(year, month))


# Back buttons
@router.callback_query(lambda c: c.data == 'back_to_main_menu')
async def to_main_menu(call: types.CallbackQuery, state: FSMContext):
    keyboard = await main_menu(call.from_user.id, state)
    await call.message.edit_text('Main menu', reply_markup=keyboard)


@router.callback_query(lambda c: c.data == 'back_to_cal_menu')
async def to_cal_menu(call: types.CallbackQuery, state: FSMContext):
    keyboard = await calendar_menu(call.from_user.id, state)
    await call.message.edit_text('Calendar menu', reply_markup=keyboard)


@router.callback_query(lambda c: c.data == 'back_to_edit_events')
async def to_cal_menu(call: types.CallbackQuery):
    await call.message.edit_text('Calendar menu', reply_markup=edit_events())


# Common handlers
@router.message(Command(commands=["start"]))
async def send_welcome(message: types.Message, state: FSMContext):
    for i in range(message.message_id, message.message_id - 30, -1):
        try:
            await bot.delete_message(message.chat.id, i)
        except Exception as e:
            pass
    keyboard = await main_menu(message.from_user.id, state)
    await message.answer(f"Hello {message.from_user.first_name}, welcome to TaskMania Bot!", reply_markup=keyboard)


@router.message()
async def any_message(message: types.Message):
    await delete_previous_messages(message)
    await message.answer('Enter the /start command to start chatting.')