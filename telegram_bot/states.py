from telebot.handler_backends import State, StatesGroup


class ConversationStates(StatesGroup):
    cancel = State() # cancel (waiting),
    ask_category = State() # ask_category,
    low_reply = State() # low_reply,
    high_reply = State() # high_reply,
    wait_button = State() # button_reply
    wait_random = State() # wait for random
    list_reply = State() # ask for list type
