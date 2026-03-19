from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def create_choose_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="Filtering", callback_data="ask_filter")
    builder.button(text="Sorting", callback_data="ask_sort")
    builder.button(text="Result", callback_data="show_result")
    builder.button(text="Cancel", callback_data="cancel")

    builder.adjust(2)
    return builder.as_markup()


def create_page_buttons(offset: int, limit: int, total: int):
    builder = InlineKeyboardBuilder()

    if offset > 0:
        builder.button(text="◀️ Previous", callback_data="previous")
    if offset + limit < total:
        builder.button(text="▶️ Next", callback_data="next")

    builder.adjust(2)
    return builder.as_markup()


def create_sort_buttons():
    builder = InlineKeyboardBuilder()
    builder.button(text="Date", callback_data="sort_date")
    builder.button(text="Mood", callback_data="sort_mood")
    builder.button(text="Progress", callback_data="sort_progress")
    builder.button(text="Hours", callback_data="sort_hours")
    builder.button(text="Cancel", callback_data="cancel")

    builder.adjust(2)
    return builder.as_markup()


def create_asc_desc_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="Ascending", callback_data="Ascending")
    builder.button(text="Descending", callback_data="Descending")
    builder.button(text="Cancel", callback_data="cancel")

    builder.adjust(2)
    return builder.as_markup()


def create_filter_buttons():
    builder = InlineKeyboardBuilder()
    builder.button(text="Private", callback_data="ask_private")
    builder.button(text="Date", callback_data="ask_date")
    builder.button(text="Mood", callback_data="ask_mood")
    builder.button(text="Progress", callback_data="ask_progress")
    builder.button(text="Hours", callback_data="ask_hours")
    builder.button(text="Cancel", callback_data="cancel")

    builder.adjust(2)
    return builder.as_markup()


def create_private_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="Only private", callback_data="private")
    builder.button(text="Only public", callback_data="public")
    builder.button(text="All", callback_data="all")
    builder.button(text="Cancel", callback_data="cancel")

    builder.adjust(2)
    return builder.as_markup()


def create_date_reply_buttons():
    builder = ReplyKeyboardBuilder()

    builder.button(text="Today")
    builder.button(text="Yesterday")
    builder.button(text="Clear filter")
    builder.button(text="Cancel", callback_data="cancel")

    builder.adjust(2)
    return builder.as_markup()


def create_entry_crud_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="➕Add new entry", callback_data="add_entry")
    builder.button(text="🔍Get entry", callback_data="get_entry")
    builder.button(text="📋Get all entries", callback_data="get_all_entries")
    builder.button(text="✏️Edit entry", callback_data="patch_entry")
    builder.button(text="🔁Completely update entry", callback_data="update_entry")
    builder.button(text="🗑Delete entry", callback_data="delete_entry")
    builder.button(text="📊Weekly statistics", callback_data="weekly_stats")
    builder.button(text="📊Summary", callback_data="summary")
    builder.button(text="🔥Streak", callback_data="streak")

    builder.adjust(2)
    return builder.as_markup()


def create_topic_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="➕Add new topic", callback_data="add_topic")
    builder.button(text="🔍Get topic", callback_data="get_topic")
    builder.button(text="✏️Edit topic", callback_data="edit_topic")
    builder.button(text="🔁Completely update topic", callback_data="update_topic")
    builder.button(text="🗑Delete topic", callback_data="delete_topic")

    builder.adjust(2)
    return builder.as_markup()


def create_goal_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="➕Add new goal", callback_data="add_goal")
    builder.button(text="🔍Get goal", callback_data="get_goal")
    builder.button(text="✏️Edit goal", callback_data="patch_goal")
    builder.button(text="🗑Delete goal", callback_data="delete_goal")

    builder.adjust(2)
    return builder.as_markup()


def create_start_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="Entry actions", callback_data="entry_actions")
    builder.button(text="Topic actions", callback_data="topic_actions")
    builder.button(text="Goal actions", callback_data="goal_actions")
    builder.button(text="Log out", callback_data="logout")

    builder.adjust(2)
    return builder.as_markup()


def create_auth_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="Log in", callback_data="login")
    builder.button(text="Sign in", callback_data="register")

    return builder.as_markup()


def create_yes_no_buttons(prefix: str):
    builder = InlineKeyboardBuilder()

    builder.button(text="Yes", callback_data=f"yes_{prefix}")
    builder.button(text="No", callback_data=f"no_{prefix}")
    builder.button(text="Cancel", callback_data="cancel")

    builder.adjust(2)
    return builder.as_markup()


def create_entry_attribute_choose_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="Title", callback_data="title")
    builder.button(text="Description", callback_data="description")
    builder.button(text="Tags", callback_data="tags")
    builder.button(text="Mood score", callback_data="mood_score")
    builder.button(text="Progress score", callback_data="progress_score")
    builder.button(text="Learning hours", callback_data="learning_hours")
    builder.button(text="Privacy", callback_data="private")
    builder.button(text="Topics", callback_data="topic_ids")
    builder.button(text="Cancel", callback_data="cancel")

    builder.adjust(2)
    return builder.as_markup()


def create_topic_attribute_choose_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="Title", callback_data="title")
    builder.button(text="Skill", callback_data="skill")
    builder.button(text="Description", callback_data="description")
    builder.button(text="Category", callback_data="category")
    builder.button(text="Is active", callback_data="is_active")
    builder.button(text="Cancel", callback_data="cancel")

    builder.adjust(2)
    return builder.as_markup()


def create_goal_attribute_choose_buttons():
    builder = InlineKeyboardBuilder()

    builder.button(text="Target date", callback_data="target_date")
    builder.button(text="Target hours", callback_data="target_hours")
    builder.button(text="Cancel", callback_data="cancel")

    builder.adjust(2)
    return builder.as_markup()


def create_cancel_button():
    builder = InlineKeyboardBuilder()
    builder.button(text="Cancel", callback_data="cancel")
    return builder.as_markup()


def create_topics_buttons(topics, many_topics: bool = True):
    builder = InlineKeyboardBuilder()

    for topic in topics:
        builder.button(text=topic["title"], callback_data=f"topic_{topic['id']}")
    builder.button(text="Ready", callback_data="ready")
    if many_topics:
        builder.button(text="Clear", callback_data="clear")
    builder.button(text="Cancel", callback_data="cancel")

    builder.adjust(2)
    return builder.as_markup()
