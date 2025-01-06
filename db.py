import sqlite3, logging, datetime

logging.basicConfig(level=logging.INFO)


def init_db():
	"""
    	Initializes the SQLite database.

	Creates the following tables if they do not exist:
 	- `users`: Stores user data including user ID, username, name, parent ID, and creation date.
	- `events`: Stores event data including title, description, start and end times, and user associations.
	
	This function ensures the necessary database schema is in place for the application.
    	"""
	conn = sqlite3.connect('db.db')
	cursor = conn.cursor()
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY,
			user_id INTEGER NOT NULL,
			username TEXT NOT NULL,
			name TEXT NOT NULL,
			parent INTEGER NOT NULL,
			date_created DATETIME,
			FOREIGN KEY (parent) REFERENCES users(id)
		)
		''')
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS events (
		id INTEGER NOT NULL,
		user_id INTEGER NOT NULL,
		title TEXT NOT NULL,
		description TEXT,
		start_time DATETIME NOT NULL,
		end_time DATETIME NOT NULL,
		completed INTEGER,
		added_by INTEGER NOT NULL,
		edited_by INTEGER NOT NULL,
		PRIMARY KEY (title, start_time, end_time),
		FOREIGN KEY (user_id) REFERENCES users(user_id)
		);
		''')
	conn.commit()
	conn.close()


def get_users_from_db():
	"""
    	Retrieves all usernames from the `users` table in the database.

    	Returns:
        None: This function fetches data but does not return it.
        It needs further implementation to return or use the data.
    	"""
	conn = sqlite3.connect('db.db')
	cursor = conn.cursor()
	cursor.execute("SELECT username FROM users")
	conn.close()


def add_user(user_id, username, name):
	"""
    	Adds a new user to the `users` table.

    	Args:
        user_id (int): The unique ID of the user.
        username (str): The username of the user.
        name (str): The full name of the user.

	Returns:
	str: Success message if the user is created successfully.
	str: Error message if an error occurs.
	bool: False if the username is not provided.
    	"""
	if username:
		try:
			conn = sqlite3.connect('db.db')
			cursor = conn.cursor()
			cursor.execute('SELECT max(id) FROM users')
			id_ = cursor.fetchone()
			if id_[0] is None:
				id_ = 1
			else:
				id_ = id_[0] + 1
			cursor.execute(
				"INSERT INTO users (id, user_id, username, name, parent, date_created) VALUES (?, ?, ?, ?, ?, datetime('now'))",
				(id_, user_id, username, name, user_id)
			)
			conn.commit()
			conn.close()
			return f"The user '{username}' has been created successfully"
		except sqlite3.IntegrityError as e:
			return f"Error: {e}"
		except Exception as e:
			return f"An unexpected error occurred: {e}"
	else:
		return False


def delete_user(user_id):
	"""
    	Deletes a user and their associated events from the database.

    	Args:
        user_id (int): The unique ID of the user to be deleted.

    	Returns:
        str: Success message if the user is deleted successfully.
        str: Error message if an error occurs.
    	"""
	try:
		conn = sqlite3.connect('db.db')
		cursor = conn.cursor()
		cursor.execute('SELECT parent FROM users WHERE user_id = ?', (user_id,))
		parent = cursor.fetchone()[0]
		if parent != user_id:
			cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
			cursor.execute('DELETE FROM events WHERE added_by = ?', (user_id,))
		else:
			cursor.execute('SELECT user_id FROM users where parent = ? order by date_created', (user_id,))
			accounts = cursor.fetchall()
			if len(accounts) == 1:
				cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
				cursor.execute('DELETE FROM events WHERE user_id = ?', (user_id,))
			else:
				next_parent_acc = accounts[1][0]
				cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
				cursor.execute('DELETE FROM events WHERE added_by = ?', (user_id,))
				cursor.execute("""UPDATE events
					   SET user_id = ? WHERE user_id = ?""", (next_parent_acc, parent))
				cursor.execute('UPDATE users SET parent = ? WHERE parent =?', (next_parent_acc, parent))
		conn.commit()
		conn.close()
		return f"The user '{user_id}' has been deleted successfully."
	except sqlite3.IntegrityError as e:
		return f"Error: {e}"
	except Exception as e:
		return f"An unexpected error occurred: {e}"


def user_exists(user_id):
	"""
    	Checks if a user exists in the `users` table.

    	Args:
        user_id (int): The unique ID of the user.

    	Returns:
        bool: True if the user exists, False otherwise.
    	"""
	conn = sqlite3.connect('db.db')
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
	result = cursor.fetchone()
	conn.commit()
	conn.close()
	if result is None:
		return False
	else:
		return True


def get_today_events(user_id):
	"""
    	Retrieves today's events for a specific user.

    	Args:
        user_id (int): The unique ID of the user.

    	Returns:
        list: A list of events scheduled for today, or an empty list if none are found.
    	"""
	conn = sqlite3.connect('db.db')
	cursor = conn.cursor()
	cursor.execute('SELECT parent FROM users WHERE user_id = ?', (user_id,))
	try:
		parent_id = cursor.fetchone()[0]
		cursor.execute("""SELECT e.id, e.title, e.start_time, e.end_time, u.name FROM events e, users u
					   WHERE e.user_id = ?
					   AND u.user_id = e.added_by
					   AND DATE(start_time) = DATE('now')""", (parent_id,))
		events = cursor.fetchall()
		conn.commit()
		conn.close()
		return events
	except TypeError:
		return []


def get_upcoming_events(user_id):
	"""
    	Retrieves upcoming events for a specific user.

    	Args:
        user_id (int): The unique ID of the user.

    	Returns:
        list: A list of upcoming events, or an empty list if none are found.
    	"""
	conn = sqlite3.connect('db.db')
	cursor = conn.cursor()
	cursor.execute('SELECT parent FROM users WHERE user_id = ?', (user_id,))
	try:
		parent_id = cursor.fetchone()[0]
		cursor.execute("""SELECT e.id, e.title, e.start_time, e.end_time, u.name FROM events e, users u
					   WHERE e.user_id = ?
					   AND u.user_id = e.added_by
					   AND DATE('now') < DATE(start_time)""", (parent_id,))
		events = cursor.fetchall()
		conn.commit()
		conn.close()
		return events
	except TypeError:
		return []


def get_completed_events(user_id):
	"""
    	Retrieves completed events for a specific user.

    	Args:
        user_id (int): The unique ID of the user.

    	Returns:
        list: A list of completed events, including event ID, title, start time, and end time.
        If no events are found, an empty list is returned.
	"""
	conn = sqlite3.connect('db.db')
	cursor = conn.cursor()
	cursor.execute('SELECT parent FROM users WHERE user_id = ?', (user_id,))
	try:
		parent_id = cursor.fetchone()[0]
		cursor.execute("""SELECT id, title, start_time, end_time FROM events
						   WHERE user_id = ?
						   AND completed = 1""", (parent_id,))
		events = cursor.fetchall()
		conn.commit()
		conn.close()
		return events
	except TypeError:
		return []


def s_add_event(*args):
	"""
    	Adds a new event to the `events` table.

    	Args:
        args (tuple): 
            - args[0] (int): The user ID of the event creator.
            - args[1] (str): The title of the event.
            - args[2] (str): The description of the event.
            - args[3] (str): The start time of the event (in "YYYY-MM-DD HH:MM" format).
            - args[4] (str): The end time of the event (in "YYYY-MM-DD HH:MM" format).

    	Returns:
        str: Success message if the event is created successfully.
        str: Error message if the event already exists or if another error occurs.
    	"""
	try:
		conn = sqlite3.connect('db.db')
		cursor = conn.cursor()
		cursor.execute('SELECT max(id) FROM events')
		id_ = cursor.fetchone()
		if id_[0] is None:
			id_ = 1
		else:
			id_ = id_[0] + 1
		cursor.execute('SELECT parent FROM users WHERE user_id = ?', (args[0],))
		parent_id = int(cursor.fetchone()[0])
		cursor.execute('''
					INSERT INTO events (id, user_id, title, description, start_time, end_time, completed, added_by, edited_by)
					VALUES (?, ?, ?, ?, ?, ?, 0, ?, 0)
					''', (id_, parent_id, args[1], args[2], args[3], args[4], args[0]))
		conn.commit()
		conn.close()
		return f"The event '{args[1]}' has been successfully added"
	except sqlite3.IntegrityError as e:
		return f"The event: {args[1]} {args[3]} {args[4]} already exists"
	except Exception as e:
		return f"An unexpected error occurred in add_event: {e}"


def s_update_event(*args):
	"""
    	Updates an existing event in the `events` table.

    	Args:
        args (tuple): 
            - args[0] (int): The ID of the event to be updated.
            - args[1] (str): The new title of the event.
            - args[2] (str): The new description of the event.
            - args[3] (str): The new start time of the event (in "YYYY-MM-DD HH:MM" format).
            - args[4] (str): The new end time of the event (in "YYYY-MM-DD HH:MM" format).
            - args[5] (int): The ID of the user making the update.

    	Returns:
        str: Success message if the event is updated successfully.
        str: Error message if an error occurs.
    	"""
	try:
		conn = sqlite3.connect('db.db')
		cursor = conn.cursor()
		cursor.execute('select title from events where id =?', (args[0],))
		previous_title = cursor.fetchone()[0]
		cursor.execute("""UPDATE events
					   SET title = ?,
						description = ?,
						start_time = ?,
						end_time = ?,
						edited_by = ?
						WHERE id = ?""", (args[1], args[2], args[3], args[4], args[5], args[0]))
		conn.commit()
		conn.close()
		return f"The event '{previous_title}' has been updated successfully"
	except Exception as e:
		return f"An unexpected error occurred in update_event: {e}"


def s_delete_event(event_id):
	"""
    	Deletes an event from the `events` table.

    	Args:
        event_id (int): The ID of the event to be deleted.

    	Returns:
        str: Success message if the event is deleted successfully.
        str: Error message if an error occurs.
    	"""
	try:
		conn = sqlite3.connect('db.db')
		cursor = conn.cursor()
		cursor.execute('SELECT title FROM events WHERE id = ?', (event_id,))
		title = cursor.fetchone()[0]
		cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
		conn.commit()
		conn.close()
		return f"The event '{title}' has been deleted successfully"
	except Exception as e:
		return f"An unexpected error occurred in delete_event: {e}"


def s_join_account(parent, new_user_id, new_username, new_name):
	"""
    	Adds a new user to an existing parent account.

    	Args:
        parent (str): The username of the parent account to join.
        new_user_id (int): The unique ID of the new user.
        new_username (str): The username of the new user.
        new_name (str): The full name of the new user.

    	Returns:
        str: Success message if the user joins successfully.
        str: Error message if the parent account is not found.
        bool: False if the new username is not provided.
    	"""
	if new_username:
		conn = sqlite3.connect('db.db')
		cursor = conn.cursor()
		cursor.execute('SELECT max(id) FROM users')
		id_ = cursor.fetchone()
		if id_[0] is None:
			id_ = 1
		else:
			id_ = id_[0] + 1
		try:
			cursor.execute('SELECT user_id FROM users WHERE username = ?', (parent,))
			parent_id = cursor.fetchone()[0]
			cursor.execute("""INSERT INTO users (id, user_id, username, name, parent, date_created)
						   VALUES (?, ?, ?, ?, ?, datetime('now'))""", (id_, new_user_id, new_username, new_name, parent_id))
			conn.commit()
			conn.close()
			return f"The user '{new_username}' has been successfully joined to '{parent}'"
		except Exception as e:
			return "The account you wish to join was not found"
	else:
		return False


def complete_events():
	"""
    	Marks events as completed if their end time has passed.

    	This function checks the `events` table for events whose end time is earlier
    	than the current time and sets their `completed` status to 1.

    	Returns:
        None
    	"""
	conn = sqlite3.connect('db.db')
	cursor = conn.cursor()
	current_time = datetime.datetime.now()
	cursor.execute("""
		UPDATE events
		SET completed = 1
		WHERE end_time < ?
	""", (current_time,))
	conn.commit()
	conn.close()
