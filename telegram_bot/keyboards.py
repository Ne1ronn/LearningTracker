from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def create_choose_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="Filtering", callback_data="ask_filter")
    builder.button(text="Sorting", callback_data="ask_sort")
    builder.button(text="Result", callback_data="show_result")

    return builder.as_markup()

def create_sort_buttons():
    builder = InlineKeyboardBuilder()
    builder.button(text="Date", callback_data="sort_date")
    builder.button(text="Mood", callback_data="sort_mood")
    builder.button(text="Progress", callback_data="sort_progress")
    builder.button(text="Hours", callback_data="sort_hours")

    return builder.as_markup()

def create_choose_reply_buttons():
    builder = ReplyKeyboardBuilder()

    builder.button(text="Ascending")
    builder.button(text="Descending")

    return builder.as_markup()

def create_filter_buttons():
    builder = InlineKeyboardBuilder()
    builder.button(text="Private",
                   callback_data="ask_private")
    builder.button(text="Date",
                   callback_data="ask_date")
    builder.button(text="Mood",
                   callback_data="ask_mood")
    builder.button(text="Progress",
                   callback_data="ask_progress")
    builder.button(text="Hours",
                   callback_data="ask_hours")

    return builder.as_markup()

def create_private_reply_buttons():
    builder = ReplyKeyboardBuilder()

    builder.button(text="Only private")
    builder.button(text="Only public")
    builder.button(text="All")

    return builder.as_markup()

def create_date_reply_buttons():
    builder = ReplyKeyboardBuilder()

    builder.button(text="Today")
    builder.button(text="Yesterday")
    builder.button(text="Clear filter")

    return builder.as_markup()

def create_entry_crud_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="➕Add new entry", callback_data="add_entry")
    builder.button(text="🔍Get entry", callback_data="get_entry")
    builder.button(text="📋Get all entries", callback_data="get_all_entries")
    builder.button(text="✏️Edit entry", callback_data="patch_entry")
    builder.button(text="🔁Completely update entry", callback_data="update_entry")
    builder.button(text="🗑Delete entry", callback_data="delete_entry")
    builder.button(text="📊Summary", callback_data="summary")

    builder.adjust(2)
    return builder.as_markup()

def create_topic_crud_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="➕Add new topic", callback_data="add_topic")
    builder.button(text="🔍Get topic", callback_data="get_topic")
    builder.button(text="✏️Edit topic", callback_data="edit_topic")
    builder.button(text="🔁Completely update topic", callback_data="update_topic")
    builder.button(text="🗑Delete topic", callback_data="delete_topic")

    builder.adjust(2)
    return builder.as_markup()

def create_start_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="Entry actions", callback_data="entry_actions")
    builder.button(text="Topic actions", callback_data="topic_actions")
    builder.button(text="Log out", callback_data="logout")

    builder.adjust(2)
    return builder.as_markup()

def create_auth_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="Log in", callback_data="login")
    builder.button(text="Sign in", callback_data="register")

    return builder.as_markup()