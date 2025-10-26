import os
import sys
from telethon.sync import TelegramClient

def eprint(*args, **kwargs):
    import sys
    print(*args, file=sys.stderr, **kwargs)

def usage():
    eprint("Random Telegram scripting commands")
    eprint(f"Usage: {sys.argv[0]} [COMMAND] [OPTIONS...]")
    eprint()
    eprint("You need to specify phone, password, API ID and API hash as environment variables")
    eprint("You will be prompted for login code")
    eprint("You can be BANNED forever by Telegram if you run this script. Be careful and BACK UP YOUR DATA.")
    eprint()
    eprint("ENVIRONMENT:")
    eprint("    TELEGRAM_PHONE - required")
    eprint("    TELEGRAM_PASSWORD")
    eprint("    TELEGRAM_API_ID - required")
    eprint("    TELEGRAM_API_HASH - required")
    eprint()
    eprint("COMMANDS:")
    eprint("    -L: list of all chats")
    eprint("    -LL: list of links of subscribed channels")
    eprint("    -S: restore a list of channels from links")
    eprint("    -C id: export saved messages")
    eprint()
    eprint("GLOBAL OPTIONS:")
    eprint("    --help: print this help message")
    sys.exit(0)

phone: str    = os.environ.get("TELEGRAM_PHONE")      or usage()
password: str = os.environ.get("TELEGRAM_PASSWORD")   or ""
api_id: int   = int(os.environ.get("TELEGRAM_API_ID") or usage())
api_hash: str = os.environ.get("TELEGRAM_API_HASH")   or usage()

client = TelegramClient(phone, api_id, api_hash)

client = client.start(phone=phone, password=password, force_sms=False)
match sys.argv[1:]:
    case ["-L"]:
        dialogs = client.get_dialogs()
        for dialog in dialogs:
            if dialog.is_channel:
                username = dialog.entity.username or (dialog.entity.usernames and dialog.entity.usernames[0].username) or ''
                username and print(f"t.me/{username}") # pyright: ignore
    case ["-LL"]:
        dialogs = client.get_dialogs()
        for dialog in dialogs:
            print(f"{dialog.title},{dialog.id}")
    case ["-S"]:
        from telethon.tl.functions.channels import JoinChannelRequest
        for link in sys.stdin:
            client(JoinChannelRequest(link))
    case ["-C", id]:
            from telethon.utils import is_audio, is_gif, is_image, is_video
            chat = client.get_input_entity(int(id))
            n = 0
            for message in client.iter_messages(chat, reverse=True):
                print("Id:", message.id)
                print("GroupId:", message.grouped_id) # album
                print("Date:", message.date)
                print("Entities:", message.entities)
                print("Message:", message.message)
                print("Poll:", message.poll)
                print("File!:", message.file)
                if f := message.file:
                    print("audio video gif image -- ", is_audio(f), is_video(f), is_gif(f), is_image(f))
                    print("file.name:", f.name)
                    # print(dir(f))
                    for attr in 'duration', 'emoji', 'ext', 'height', 'id', 'media', 'mime_type', 'name', 'performer', 'size', 'sticker_set', 'title', 'width':
                        if hasattr(f, attr): 
                            if v := getattr(f, attr):
                                print(attr, v)
                print("Forward:", message.forward)
                if fw := message.forward:
                    chat = fw.chat
                    print("fwd", chat.title, chat.id)
                print("Reactions:", message.reactions)
                # print("Media:", message.media)
                # print("Photo:", message.photo)
                # print("Video:", message.video)
                # print("Voice:", message.voice)
                # print("Audio:", message.audio)
                # print("Sticker:", message.sticker)
                # print("Doc:", message.document)
                print("---------------------------------------------")
                n += 1
                if n > 128: break

            print("TOTAL:", n)
    case _:
        usage()

