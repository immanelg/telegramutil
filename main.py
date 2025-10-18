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
    print("    -LL: print list of subscribed channels")
    print("    -L: print list of all chats")
    print("    -S: subscribe to a list of channels from stdin by links")
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

phone: str    = os.environ.get("TELEGRAM_PHONE")      or usage()
password: str = os.environ.get("TELEGRAM_PASSWORD")   or usage()
api_id: int   = int(os.environ.get("TELEGRAM_API_ID") or usage())
api_hash: str = os.environ.get("TELEGRAM_API_HASH")   or usage()

client = TelegramClient("current", api_id, api_hash)

client = client.start(phone=phone, password=password,force_sms=False)
match sys.argv[1:]:
    case ["-L"]:
        dialogs = client.get_dialogs()
        for dialog in dialogs:
            if dialog.is_channel:
                username = dialog.entity.username or (dialog.entity.usernames and dialog.entity.usernames[0].username) or ''
                username and print(f"t.me/{username}")
    case ["-LL"]:
        dialogs = client.get_dialogs()
        for dialog in dialogs:
            print(f"{dialog.title},{dialog.id}")
    case ["-S"]:
        for link in sys.stdin:
            client(JoinChannelRequest(link))
    case ["-C", id]:
            chat = client.get_input_entity(int(id))
            i = 0
            for message in client.iter_messages(chat):
                print("Id:", message.id)
                print("Message:", message.message)
                # print("Media:", message.media)
                print("File:", message.file)
                print("Photo:", message.photo)
                print("Video:", message.video)
                print("Voice:", message.voice)
                print("Audio:", message.audio)
                print("Sticker:", message.sticker)
                print("Doc:", message.document)
                print("---------------------------------------------")
                i += 1
                if i > 128: break

            print(i)
    case _:
        usage()

