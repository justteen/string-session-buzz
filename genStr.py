import asyncio

from bot import bot, HU_APP
from pyromod import listen
from asyncio.exceptions import TimeoutError

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    SessionPasswordNeeded, FloodWait,
    PhoneNumberInvalid, ApiIdInvalid,
    PhoneCodeInvalid, PhoneCodeExpired
)

API_TEXT = """Hi, {}.
ini adalah Pyrogram's String Session Generator Bot. Saya akan generate String Session akun telegram kamu.

By @psycho_syridwan
reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Support Group', url='https://t.me/ossuport'),
                InlineKeyboardButton('Developer', url='https://t.me/psycho_syridwan')
            ],
            [
                InlineKeyboardButton('Bots Updates Channel', url='https://t.me/ossuport3'),
            ]
        ]
    )

Sekarang kirim `API_ID` sesuai `APP_ID` untuk Start Generating Session."""
HASH_TEXT = "Kirim `API_HASH`.\n\ntekan /cancel untuk cancel tugas."
PHONE_NUMBER_TEXT = (
    "Sekarang kirim no Telegram kamu, format internasional. \n"
    "seperti kode negara indonesia. Example: **+629999**\n\n"
    "tekan /cancel untuk cancel tugas."
)

@bot.on_message(filters.private & filters.command("start"))
async def genStr(_, msg: Message):
    chat = msg.chat
    api = await bot.ask(
        chat.id, API_TEXT.format(msg.from_user.mention)
    )
    if await is_cancel(msg, api.text):
        return
    try:
        check_api = int(api.text)
    except Exception:
        await msg.reply("`API_ID` salah.\ntekan /start memulai lagi.")
        return
    api_id = api.text
    hash = await bot.ask(chat.id, HASH_TEXT)
    if await is_cancel(msg, hash.text):
        return
    if not len(hash.text) >= 30:
        await msg.reply("`API_HASH` salah.\ntekan /start untuk memulai lagi.")
        return
    api_hash = hash.text
    while True:
        number = await bot.ask(chat.id, PHONE_NUMBER_TEXT)
        if not number.text:
            continue
        if await is_cancel(msg, number.text):
            return
        phone = number.text
        confirm = await bot.ask(chat.id, f'`ini "{phone}" benar? (y/n):` \n\nKirim: `y` (Kalau benar)\nKirim: `n` (Kalau salah)')
        if await is_cancel(msg, confirm.text):
            return
        if "y" in confirm.text:
            break
    try:
        client = Client("my_account", api_id=api_id, api_hash=api_hash)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`\ntekan /start untuk memulai lagi.")
        return
    try:
        await client.connect()
    except ConnectionError:
        await client.disconnect()
        await client.connect()
    try:
        code = await client.send_code(phone)
        await asyncio.sleep(1)
    except FloodWait as e:
        await msg.reply(f"You have Floodwait of {e.x} Seconds")
        return
    except ApiIdInvalid:
        await msg.reply("API ID dan API Hash salah.\n\ntekan /start mulai lagi.")
        return
    except PhoneNumberInvalid:
        await msg.reply("No. SALAH.\n\nTekan /start Mulai lagi.")
        return
    try:
        otp = await bot.ask(
            chat.id, ("OTP telah dikirim, "
                      "Kirim OTP dalam `1 2 3 4 5` format. __(Spasi di antara setiap angka!)__ \n\n"
                      "Kalau OTP tidak terkirim /restart dan mulai lagi /start perintah Bot.\n"
                      "Tekan /cancel untuk Cancel."), timeout=300)

    except TimeoutError:
        await msg.reply("Waktu telah habis 5 menit.\ntekan /start untuk ulangi.")
        return
    if await is_cancel(msg, otp.text):
        return
    otp_code = otp.text
    try:
        await client.sign_in(phone, code.phone_code_hash, phone_code=' '.join(str(otp_code)))
    except PhoneCodeInvalid:
        await msg.reply("Kode Salah.\n\nTekan /start untuk mulai lagi")
        return
    except PhoneCodeExpired:
        await msg.reply("Kode Expired.\n\nTekan /start untuk mulai lagi")
        return
    except SessionPasswordNeeded:
        try:
            two_step_code = await bot.ask(
                chat.id, 
                "Akun kamu ada Two-Step Verification.\nMasukan password anda.\n\ntekan /cancel untuk Cancel.",
                timeout=300
            )
        except TimeoutError:
            await msg.reply("`Waktu habis 5 min.\n\nTekan /start untuk mulai lagi`")
            return
        if await is_cancel(msg, two_step_code.text):
            return
        new_code = two_step_code.text
        try:
            await client.check_password(new_code)
        except Exception as e:
            await msg.reply(f"**ERROR:** `{str(e)}`")
            return
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return
    try:
        session_string = await client.export_session_string()
        await client.send_message("me", f"#PYROGRAM #STRING_SESSION\n\n```{session_string}``` \n\nBy [@stringsessionbuzz_bot](tg://openmessage?user_id=1457097205) \nA Bot By @psycho_syridwan")
        await client.disconnect()
        text = "String Session telah sukses.\nKlik dalam menu dibawah."
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Lihat String Session", url=f"tg://openmessage?user_id={chat.id}")]]
        )
        await bot.send_message(chat.id, text, reply_markup=reply_markup)
    except Exception as e:
        await bot.send_message(chat.id ,f"**ERROR:** `{str(e)}`")
        return


@bot.on_message(filters.private & filters.command("restart"))
async def restart(_, msg: Message):
    await msg.reply("Bot dimuat ulang!")
    HU_APP.restart()


@bot.on_message(filters.private & filters.command("help"))
async def restart(_, msg: Message):
    out = f"""
Hi, {msg.from_user.mention}. Ini adalah Pyrogram Session String Generator Bot. \
Saya akan mengirim `STRING_SESSION` untuk UserBot kamu.

Membutuhkan `API_ID`, `API_HASH`, No. HP dan One Time Verification Code. \
Akan terkirim OTP pada nomor kamu.
kamu harus masukan **OTP** in `1 2 3 4 5` this format. __(SPASI SETIAP ANGKA!)__

**NOTE:** kalau bot tidak memberikan OTP /restart dan /start untuk memulai ulang proses. 

Harus Join Group untuk Bot Updates !!
"""
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Support Group', url='https://t.me/ossuport'),
                InlineKeyboardButton('Developer', url='https://t.me/psycho_syridwan')
            ],
            [
                InlineKeyboardButton('Bots Updates Channel', url='https://t.me/ossuport3'),
            ]
        ]
    )
    await msg.reply(out, reply_markup=reply_markup)


async def is_cancel(msg: Message, text: str):
    if text.startswith("/cancel"):
        await msg.reply("Proses Dihentikan.")
        return True
    return False

if __name__ == "__main__":
    bot.run()
