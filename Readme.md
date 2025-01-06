# TaskMania Bot

TaskMania Bot is a powerful Telegram bot designed to help users manage tasks, events, and shared calendars. With features like adding, editing, and deleting events, as well as managing accounts, TaskMania Bot is perfect for personal use or group collaborations.

---

## Features

- **Event Management**:
  - Add events with specific times or for the whole day.
  - Edit and delete existing events.
  - View today's, upcoming, and completed events.
  
- **Account Management**:
  - Create a new account.
  - Join an existing account.
  - Delete your account.
  
- **Calendar Navigation**:
  - Navigate through months and years.
  - Select specific dates for events.
  - View and manage events using an interactive calendar.

- **Responsive Menu**:
  - Main menu with options for calendar, about, and contacts.
  - Dynamic calendar menu based on user state.

---

## Requirements

- Python 3.8 or later
- Telegram Bot API token
- SQLite3 (built-in with Python)

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/asstrix/TelegramBot.git
   cd TelegramBot
   ```
2. Install dependencies:
  ```bash
  pip install aiogram
  ```
3. Set up your Telegram bot:
  - Create a bot using BotFather on Telegram.
  - Copy your bot token.
4. Add your bot token to cfg.py:
  ```python
  API_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
  ```
5. Run the bot:
  ```bash
  python main.py
  ```

## File Structure
```bash
├── main.py                 # Main entry point for the bot
├── handlers.py             # Handlers for Telegram bot commands and callbacks
├── db.py                   # Database initialization and operations
├── keyboards.py            # Keyboard creation functions
├── states.py               # States to handle sequences of actions
├── README.md               # Project documentation
├── requirements.txt        # Project dependencies
```

## Usage

### Commands
- /start: Starts the bot and displays the main menu.
- ### Inline Buttons:
- 📅 Calendar: Opens the user's calendar menu.
- 🛈 About: Displays information about the bot.
- 📞 Contacts: Shows the developer's contact information.
- ➕ Add: Adds a new event.
- 🔧 Manage: Opens account management options.

### Menus
1. Main Menu:
- Access the calendar or learn about the bot.
2. Calendar Menu:
- View today's, upcoming, and completed events.
- Add new events or manage accounts.
3. Account Management:
- Create or join an account.
- Delete your account.
4. Event Editing:
- Edit or delete specific events.

## Database Structure
### Tables
### users Table:
```
| Column Name  | Data Type | Description                              |
|--------------|-----------|------------------------------------------|
| `id`         | INTEGER   | Primary key.                             |
| `user_id`    | INTEGER   | Unique ID of the user.                   |
| `username`   | TEXT      | Telegram username of the user.           |
| `name`       | TEXT      | Full name of the user.                   |
| `parent`     | INTEGER   | ID of the parent account.                |
| `date_created` | DATETIME | Timestamp when the account was created. |
```

### events Table:
```
| Column Name   | Data Type | Description                                           |
|---------------|-----------|-------------------------------------------------------|
| `id`          | INTEGER   | Primary key for the event.                            |
| `user_id`     | INTEGER   | ID of the user associated with the event.             |
| `title`       | TEXT      | Title of the event.                                   |
| `description` | TEXT      | Description of the event.                             |
| `start_time`  | DATETIME  | Start time of the event.                              |
| `end_time`    | DATETIME  | End time of the event.                                |
| `completed`   | INTEGER   | Completion status (0 = not completed, 1 = completed). |
| `added_by`    | INTEGER   | ID of the user who added the event.                   |
| `edited_by`   | INTEGER   | ID of the user who last edited the event.             |
```
## Screenshots:

### Startup menu:

![create](https://github.com/asstrix/files/blob/main/TaskManiaBot/start.png)

### Create or join to an account:

![start](https://github.com/asstrix/files/blob/main/TaskManiaBot/create.png)

### Main menu:

![main](https://github.com/asstrix/files/blob/main/TaskManiaBot/main_menu.png)

### Choose a day:

![choose](https://github.com/asstrix/files/blob/main/TaskManiaBot/choose.png)

## Select event's period:

![period](https://github.com/asstrix/files/blob/main/TaskManiaBot/event%20period.png)

### Choose a day:

![choose](https://github.com/asstrix/files/blob/main/TaskManiaBot/choose.png)

### View an event:

![view](https://github.com/asstrix/files/blob/main/TaskManiaBot/view_event.png)
