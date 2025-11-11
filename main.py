import os
import sys
import re
import pathlib
import time
import logging
from telethon import TelegramClient
from telethon.utils import is_audio, is_gif, is_image, is_video
from telethon.tl.types import MessageEntityBold, MessageEntityItalic, MessageEntityCode, MessageEntityPre, MessageEntityTextUrl, MessageEntityStrike
from telethon import functions, types

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def usage(error: str = ""):
    if error: eprint(">>>>>", error)
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
    eprint("    -C id: export saved messages to ./{phonenumber}/{chat_id}")
    eprint("    -F id1 id2: forward all messages (history) from 1 to 2")
    eprint()
    eprint("GLOBAL OPTIONS:")
    eprint("    --help: print this help message")
    sys.exit(0)


phone: str = os.environ.get("TELEGRAM_PHONE") or usage("phone is required")
password: str = os.environ.get("TELEGRAM_PASSWORD") or ""
api_id: int = int(os.environ.get("TELEGRAM_API_ID") or usage("api_id is required"))
api_hash: str = os.environ.get("TELEGRAM_API_HASH") or usage("api_hash is required")

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="[%(asctime)s] %(levelname)s %(module)s - %(message)s")

session_dir = pathlib.Path(phone)
session_dir.mkdir(exist_ok=True, parents=True)

async def main():
    client = TelegramClient(session=session_dir/"session", api_id=api_id, api_hash=api_hash)

    await client.start(phone=phone, password=password, force_sms=False)
    # result = await client(functions.help.GetTermsOfServiceUpdateRequest())
    # print(result.stringify())

    # Here comes the deepest indentation I ever wrote in python (and also the sloppiest code in existence)
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

        case ["-C", chatid]:
            logging.info(f"Saving chat: {chatid}")

            data_path = session_dir/chatid
            data_path.mkdir(parents=True, exist_ok=True)
            messages_md_path = data_path/"chat-messages.md"

            logging.info(f"Opening file {messages_md_path} for writing chat archive")
            with open(messages_md_path, "w", encoding="utf-8") as out:
                start_time = time.perf_counter()
                chat = await client.get_input_entity(int(chatid))
                n = 0
                last_group_id = None
                async for message in client.iter_messages(chat, reverse=True, limit=None):
                    dump = 0
                    if dump:
                        out.write(f"Id: {message.id}\n")
                        out.write(f"GroupId: {message.grouped_id}\n")  # album
                        out.write(f"Date: {message.date}\n")
                        out.write(f"Entities: {message.entities}\n")
                        out.write(f"Message: {message.message}\n")
                        out.write(f"Poll: {message.poll}\n")
                        out.write(f"File!: {message.file}\n")
                        if f := message.file:
                            out.write(f"audio video gif image -- {is_audio(f)} {is_video(f)} {is_gif(f)} {is_image(f)}\n")
                            out.write(f"file.name: {f.name}\n")
                            # out.write(dir(f))
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
                                        out.write(f"{attr} {v}\n")
                        out.write(f"Forward: {message.forward}\n")
                        if fw := message.forward:
                            chat = fw.chat
                            out.write(f"fwd {chat.title} {chat.id}\n")
                        out.write(f"Reactions: {message.reactions}\n")
                        # out.write("Media:", message.media)
                        # out.write("Photo:", message.photo)
                        # out.write("Video:", message.video)
                        # out.write("Voice:", message.voice)
                        # out.write("Audio:", message.audio)
                        # out.write("Sticker:", message.sticker)
                        # out.write("Doc:", message.document)
                        out.write("---------------------------------------------\n")
                    else:
                        logging.info(f"Processing message id={message.id}")
                        continuing_group = message.grouped_id is not None and last_group_id == message.grouped_id
                        last_group_id = message.grouped_id

                        if continuing_group:
                            # out.write("(grouped)")
                            pass
                        if not continuing_group:
                            # finish the previous one
                            # out.write("---")
                            pass

                        if not continuing_group:
                            # Create message prologue.

                            out.write(f"<h3 id='m_{message.id}'>Message m_{message.id}</h3>\n\n")
                            out.write(f"{message.date.strftime('Date: %Y-%m-%d_%H:%M:%S')}\n\n")

                            if fw := message.forward:
                                chat = fw.chat
                                out.write(f"Forwarded from: {chat.title}\n\n")

                            if rpl := message.reply_to:
                                hsh = f"#m_{rpl.reply_to_msg_id}"
                                out.write(f"Replied to: [{hsh}]({hsh})\n")
                                if q := rpl.quote_text:
                                    for line in q.split("\n"):
                                        out.write(f"> {line}\n")
                                out.write("\n")

                            if p := message.poll:
                                # POLL: message.poll =  MessageMediaPoll(poll=Poll(id=5472212957045724922, question=TextWithEntities(text='poll', entities=[]), answers=[PollAnswer(text=TextWithEntities(text='1', entities=[]), option=b'0'), PollAnswer(text=TextWithEntities(text='2', entities=[]), option=b'1')], closed=False, public_voters=True, multiple_choice=False, quiz=True, close_period=None, close_date=None), results=PollResults(min=False, results=[PollAnswerVoters(option=b'0', voters=0, chosen=False, correct=False), PollAnswerVoters(option=b'1', voters=1, chosen=True, correct=True)], total_voters=1, recent_voters=[PeerUser(user_id=8297349295)], solution='EXPLANATION!', solution_entities=[]))
                                out.write(f"Poll: {p.poll.question.text}\n")
                                for answer in p.poll.answers:
                                    out.write(f"  * {answer.text.text}\n")
                                out.write("\n")
                                if p.results.solution:
                                    out.write(f"Explanation: {p.results.solution}\n")

                            if txt := message.message:
                                if entities := message.entities:
                                    # from telethon.extensions.markdown import unparse
                                    # from telethon.extensions.html import unparse
                                    # txt = unparse(txt, entities)
                                    # Both markdown and html really are broken... so whatever, who gives a shit
                                    pass
                                out.write(f"{txt}\n\n")

                        # In group, we are only interested in files.
                        if f := message.file:
                            dl_dir = data_path/"tgfiles"
                            dl_dir.mkdir(exist_ok=True, parents=True)

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

                            out.write(f"File: [{name}](tgfiles/{name}), {f.mime_type} ({int(f.size / 1024)} kb)\n\n")


                    n += 1
                    if n > 128:
                        break

                end_time = time.perf_counter() 
                logging.info(f"Done. Total: {n}, took {end_time - start_time:.4f}s.")
                out.write(f"\n\n\n------------------------------\n\n\nTOTAL: {n}\n")
        case ["-F", id1, id2]:
            logging.info(f"Forwarding from chat: {id1} to {id2}")
            # Cache all dialogs to resolve entities by ID
            await client.get_dialogs()
            source = await client.get_input_entity(int(id1))
            target = await client.get_input_entity(int(id2))
            start_time = time.perf_counter()
            n = 0
            async for message in client.iter_messages(source, reverse=True, limit=None):
                try:
                    await message.forward_to(target)
                    logging.info(f"Forwarded message id={message.id} (Date: {message.date})")
                    n += 1
                    # Rate limit: sleep 1 second between forwards to avoid flood waits/bans
                    await asyncio.sleep(1)
                except Exception as e:
                    logging.error(f"Error forwarding message {message.id}: {e}")
                    # Continue on error, or add break if needed
                if n > 128:  # Optional limit for testing; remove or increase for full run
                    logging.info("Hit optional limit of 128 messages; stopping.")
                    break
            end_time = time.perf_counter()
            logging.info(f"Done forwarding. Total: {n}, took {end_time - start_time:.4f}s.")
        case _:
            usage("unknown command")


import asyncio
asyncio.run(main())
