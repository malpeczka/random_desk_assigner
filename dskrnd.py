#!/usr/bin/env python3

"""

Random seating planner - 2020, Nien Huei Chang

dskrnd.py - main program

"""

import json
import curses
import random


DESK_POOL = 50
DATABASE_FILE_NAME = "dskrnd.json"

database = []
screen = curses.initscr()


def read_database_file():
    """ Read database from local json file """

    global database

    try:
        with open(DATABASE_FILE_NAME) as database_file:
            database = json.load(database_file)
            return True

    except (IOError, json.decoder.JSONDecodeError):
        return False


def write_database_file():
    """ Write the database list to local json file """

    try:
        with open(DATABASE_FILE_NAME, "w") as database_file:
            json.dump(database, database_file, indent=4)
            return True

    except IOError:
        return False


def get_assigned_desk_numbers():
    """ Get a list of all assigned desk numbers from the database list """

    desk_numbers = []

    for record in database:
        desk_number = record["desk_number"]
        desk_numbers.append(desk_number)

    return desk_numbers


def get_assigned_user_names():
    """ Get a list of all user names from the database list """

    user_names = []

    for record in database:
        user_name = record["user_name"]
        user_names.append(user_name)

    return user_names


def get_user_name(desk_number):
    """ Get user name assigned to a given desk number, if none assigned return empty string """

    for record in database:
        if record["desk_number"] == desk_number:
            return record["user_name"]

    return ""


def get_desk_number(user_name):
    """ Get desk number assigned to a given user name """

    for record in database:
        if record["user_name"] == user_name:
            return record["desk_number"]

    return 0


def add_desk_assignment(desk_number, user_name):
    """ Add record to the database """

    new_record = {
        "user_name": user_name,
        "desk_number": desk_number,
    }

    database.append(new_record)


def clear_desk_assignment(desk_number):
    """ Delete the record of a given desk number """

    for record in database:
        if record["desk_number"] == desk_number:
            del database[database.index(record)]


def wait_for_key(message=""):
    """ Dispaly message (if provided) followed by "Press any key to continue..." and wait for user to press key """

    if message:
        screen.clear()
        screen.border()
        screen.addstr(2, 2, message)

    screen.addstr(screen.getmaxyx()[0] - 2, 2, "Press any key to continue...")
    screen.getkey()


def get_user_input(message):
    """ Display message and wait for user to enter string """

    screen.clear()
    screen.border()

    screen.addstr(2, 2, message)

    curses.echo()  # Show characters on screen as they are typed by user
    curses.curs_set(True)  # Show cursor

    user_input = screen.getstr().decode("utf-8")

    curses.curs_set(False)  # Hide cursor
    curses.noecho()  # Do not show user typed characters on the screen

    return user_input


def assign_desk():
    """ Get user name and assign it to a random desk number """

    if len(get_assigned_desk_numbers()) >= DESK_POOL:
        wait_for_key("No free desk available.")
        return

    while True:
        user_name = get_user_input("Please enter user name (2 - 17 characters, empty to cancel): ")

        if len(user_name) == 0:
            break

        if len(user_name) < 2:
            wait_for_key("User name too short.")
            continue

        if len(user_name) > 17:
            wait_for_key("User name too long.")
            continue

        if user_name in get_assigned_user_names():
            wait_for_key(f"User '{user_name}' has been found in database assigned to desk number {get_desk_number(user_name)}.")
            continue

        all_desks = set(range(1, DESK_POOL + 1))

        assigned_desks = set(get_assigned_desk_numbers())

        free_desks = list(all_desks - assigned_desks)

        desk_number = random.choice(free_desks)

        add_desk_assignment(desk_number, user_name)

        wait_for_key(f"User '{user_name}' has been assigned to desk number {desk_number}.")

        break


def clear_desk():
    """ Remove the record associated with user provided desk number """

    if len(get_assigned_desk_numbers()) == 0:
        wait_for_key("No desks assigned yet.")
        return

    while True:
        desk_number = get_user_input(f"Please enter desk number (1 - {DESK_POOL}, empty to cancel): ")

        if len(desk_number) == 0:
            break

        if not desk_number.isdigit():
            wait_for_key(f"Desk number must be a number in range 1 - {DESK_POOL} range.")
            continue

        desk_number = int(desk_number)

        if not (1 <= desk_number <= DESK_POOL):
            wait_for_key(f"Desk number must be a number in range 1 - {DESK_POOL} range.")
            continue

        if desk_number not in get_assigned_desk_numbers():
            wait_for_key(f"Desk number {desk_number} is not assigned to any user.")
            continue

        clear_desk_assignment(desk_number)
        wait_for_key(f"Desk {desk_number} has been cleared.")
        break


def show_desks():
    """ Display all desk / user assignments sorted by desk number """

    screen.clear()
    screen.border()

    y = 2
    x = 2

    for desk_number in range(1, DESK_POOL + 1):
        if y == screen.getmaxyx()[0] - 4:
            y = 2
            x += 25

        screen.addstr(y, x, f"{desk_number:2} - {get_user_name(desk_number)}")
        y += 1

    wait_for_key()


def show_users():
    """ Display all desk / user assignments sorted by user name """

    screen.clear()
    screen.border()

    y = 2
    x = 2

    for user_name in sorted(get_assigned_user_names()):
        if y == screen.getmaxyx()[0] - 4:
            y = 2
            x += 25

        screen.addstr(y, x, f"{user_name:17} - {get_desk_number(user_name):2}")
        y += 1

    wait_for_key()


def main(_):
    """ Display main menu and wait for user's instruction """

    read_database_file()

    curses.noecho()  # Do not show user typed characters on the screen
    curses.curs_set(False)  # Hide cursor

    while True:
        if screen.getmaxyx()[0] < 24 or screen.getmaxyx()[1] < 80:
            screen.clear()
            screen.addstr(0, 0, f"Terminal window needs to be at least 80x24, please adjust the window size...")
            screen.getkey()  # Wait for 'KEY_RESIZE' keypad constant or any keycode returned by terminal when user resizes window
            continue

        screen.clear()
        screen.border()

        screen.addstr(2, 2, "Main menu")
        screen.addstr(4, 2, "1. Assign desk")
        screen.addstr(5, 2, "2. Clear desk")
        screen.addstr(6, 2, "3. Show desks")
        screen.addstr(7, 2, "4. Show users")
        screen.addstr(9, 2, "0. Save data and exit program")

        key = screen.getkey()

        if key == "1":
            assign_desk()

        elif key == "2":
            clear_desk()

        elif key == "3":
            show_desks()

        elif key == "4":
            show_users()

        elif key == "0":
            break

    write_database_file()


if __name__ == "__main__":
    curses.wrapper(main)


