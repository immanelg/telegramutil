import os
import sys
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest

def usage():
    print("Utility for manipulating Telegram channels/chats")
    print(f"Usage: {sys.argv[0]} [COMMAND] [OPTIONS...]")
    print()
    print("You need to specify phone, password, API ID and API hash as environment variables")
    print("You will be prompted for login code")
    print()
    print("COMMANDS:")
    print("    -L: print list of subscribed channels")
    print("    -S: subscribe to a list of channels")
    print()
    print("OPTIONS:")
    print("    --help: print this help message")
    print()
    print("ENVIRONMENT:")
    print("    TELEGRAM_PHONE")
    print("    TELEGRAM_PASSWORD")
    print("    TELEGRAM_API_ID")
    print("    TELEGRAM_API_HASH")
    sys.exit(0)

phone: str    = os.environ["TELEGRAM_PHONE"]      or usage()
password: str = os.environ["TELEGRAM_PASSWORD"]   or usage()
api_id: int   = int(os.environ["TELEGRAM_API_ID"] or usage())
api_hash: str = os.environ["TELEGRAM_API_HASH"]   or usage()

client = TelegramClient("current", api_id, api_hash)

client = client.start(phone=phone, password=password,force_sms=False)
match sys.argv[1:]:
    case ["-L"]:
        dialogs = client.get_dialogs()
        for dialog in dialogs:
            if dialog.is_channel:
                username = dialog.entity.username or (dialog.entity.usernames and dialog.entity.usernames[0].username) or ''
                username and print(f"t.me/{username}")
    case ["-S"]:
        for link in sys.stdin:
            client(JoinChannelRequest(link))
    case _:
        usage()

