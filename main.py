import os
import sys
import re
import pathlib
import logging
from telethon import TelegramClient
from telethon.utils import is_audio, is_gif, is_image, is_video
from telethon.tl.types import MessageEntityBold, MessageEntityItalic, MessageEntityCode, MessageEntityPre, MessageEntityTextUrl, MessageEntityStrike


def eprint(*args, **kwargs):
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


phone: str = os.environ.get("TELEGRAM_PHONE") or usage()
password: str = os.environ.get("TELEGRAM_PASSWORD") or ""
api_id: int = int(os.environ.get("TELEGRAM_API_ID") or usage())
api_hash: str = os.environ.get("TELEGRAM_API_HASH") or usage()

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")


async def main():
    client = TelegramClient(session=phone, api_id=api_id, api_hash=api_hash)

    await client.start(phone=phone, password=password, force_sms=False)

    # Here comes the deepest indentation I ever wrote in python
    match sys.argv[1:]:
        case ["-L"]:
            dialogs = await client.get_dialogs()
            for dialog in dialogs:
                if dialog.is_channel:
                    username = dialog.entity.username or (dialog.entity.usernames and dialog.entity.usernames[0].username) or ""
                    username and print(f"t.me/{username}")  # pyright: ignore
        case ["-LL"]:
            dialogs = await client.get_dialogs()
            for dialog in dialogs:
                print(f"{dialog.title},{dialog.id}")
        case ["-S"]:
            from telethon.tl.functions.channels import JoinChannelRequest

            for link in sys.stdin:
                await client(JoinChannelRequest(link))
        case ["-C", id]:
            logging.info(f"Saving chat: {id}")

            chat = await client.get_input_entity(int(id))
            n = 0
            last_group_id = None
            async for message in client.iter_messages(chat, reverse=True, limit=None):
                dump = 0
                if dump:
                    print("Id:", message.id)
                    print("GroupId:", message.grouped_id)  # album
                    print("Date:", message.date)
                    print("Entities:", message.entities)
                    print("Message:", message.message)
                    print("Poll:", message.poll)
                    print("File!:", message.file)
                    if f := message.file:
                        print("audio video gif image -- ", is_audio(f), is_video(f), is_gif(f), is_image(f))
                        print("file.name:", f.name)
                        # print(dir(f))
                        for attr in (
                            "duration",
                            "emoji",
                            "ext",
                            "height",
                            "id",
                            "media",
                            "mime_type",
                            "name",
                            "performer",
                            "size",
                            "sticker_set",
                            "title",
                            "width",
                        ):
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
                else:
                    logging.info(f"Message {message.id}...")
                    continuing_group = message.grouped_id is not None and last_group_id == message.grouped_id
                    last_group_id = message.grouped_id

                    if continuing_group:
                        # print("(grouped)")
                        pass
                    if not continuing_group:
                        # finish the previous one
                        # print("---")
                        pass

                    if not continuing_group:
                        # Create message prologue.

                        print(f"<h3 id='m_{message.id}'>Message m_{message.id}</h3>")
                        print()
                        print(message.date.strftime("Date: %Y-%m-%d_%H:%M:%S"))
                        print()

                        if fw := message.forward:
                            chat = fw.chat
                            print("Forwarded from:", chat.title)
                            print()

                        if rpl := message.reply_to:
                            hsh = f"#m_{rpl.reply_to_msg_id}"
                            print(f"Replied to: [{hsh}]({hsh})")
                            if q := rpl.quote_text:
                                for line in q.split("\n"):
                                    print(f"> {line}")
                            print()

                        if p := message.poll:
                            # POLL: message.poll =  MessageMediaPoll(poll=Poll(id=5472212957045724922, question=TextWithEntities(text='poll', entities=[]), answers=[PollAnswer(text=TextWithEntities(text='1', entities=[]), option=b'0'), PollAnswer(text=TextWithEntities(text='2', entities=[]), option=b'1')], closed=False, public_voters=True, multiple_choice=False, quiz=True, close_period=None, close_date=None), results=PollResults(min=False, results=[PollAnswerVoters(option=b'0', voters=0, chosen=False, correct=False), PollAnswerVoters(option=b'1', voters=1, chosen=True, correct=True)], total_voters=1, recent_voters=[PeerUser(user_id=8297349295)], solution='EXPLANATION!', solution_entities=[]))
                            print("Poll:", p.poll.question.text)
                            for answer in p.poll.answers:
                                print("  * ", answer.text.text)
                            print()
                            if p.results.solution:
                                print("Explanation:", p.results.solution)

                        if txt := message.message:
                            if entities := message.entities:
                                entities = sorted(entities, key=lambda x: x.offset, reverse=True)
                                for entity in entities:
                                    start = entity.offset
                                    end = entity.offset + entity.length
                                    part = txt[start:end]

                                    if isinstance(entity, MessageEntityBold):
                                        part_md = f"**{part}**"
                                    elif isinstance(entity, MessageEntityItalic):
                                        part_md = f"*{part}*"
                                    elif isinstance(entity, MessageEntityCode):
                                        part_md = f"`{part}`"
                                    elif isinstance(entity, MessageEntityPre):
                                        part_md = f"```{part}```"
                                    elif isinstance(entity, MessageEntityTextUrl):
                                        part_md = f"[{part}]({entity.url})"
                                    elif isinstance(entity, MessageEntityStrike):
                                        part_md = f"~~{part}~~"
                                    else:
                                        continue

                                    txt = txt[:start] + part_md + txt[end:]
                            print(txt)
                            print()

                    # In group, we are only interested in files.
                    if f := message.file:
                        dl_dir = pathlib.Path("./tgfiles")
                        dl_dir.mkdir(exist_ok=True)

                        escape = lambda text: re.sub(r"[^A-Za-z0-9.]+", "", text)

                        # name = f"{message.id}_{message.date.strftime('%Y-%m-%d_%H-%M-%S')}"
                        name = f"{message.id}"
                        if f.name:
                            name += "-" + escape(f.name)
                        elif f.ext:
                            name += f.ext
                        path = dl_dir / name

                        if not path.exists():
                            logging.info(f"Downloading media: {path}")
                            await message.download_media(file=path)
                        else:
                            logging.info(f"Media cache hit: {path}")

                        print(f"File: [{name}]({path}), {f.mime_type} ({int(f.size / 1024)} kb)")
                        print()

                        print()

                n += 1
                if n > 128:
                    break

            logging.info(f"Done. Total: {n}")
            print("\n\n\n------------------------------\n\n\nTOTAL:", n)
        case _:
            usage()


import asyncio
asyncio.run(main())
