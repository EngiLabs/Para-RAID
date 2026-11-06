from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

INLINE_MOVEMENT = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="⬆️", callback_data="move_forward")
    ],
    [
        InlineKeyboardButton(text="⬅️", callback_data="move_left"),
        InlineKeyboardButton(text="⏹️", callback_data="move_stop"),
        InlineKeyboardButton(text="➡️", callback_data="move_right"),
    ],
    [
        InlineKeyboardButton(text="⬇️", callback_data="move_backward")
    ],
])


INLINE_MAIN = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🎮 Control", callback_data="show_control"),
        InlineKeyboardButton(text="📊 Status", callback_data="req_status"),
    ],
    [
        InlineKeyboardButton(text="📷 Photo", callback_data="req_photo"),
        InlineKeyboardButton(text="🏠 Home", callback_data="cmd_home"),
    ],
])


REPLY_RESET = ReplyKeyboardRemove()
