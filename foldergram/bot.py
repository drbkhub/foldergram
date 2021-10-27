import aiogram
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, ParseMode

from .types import Bot
from .utils import group_media

def start(bot, proxy=None, token=None):
    fg_bot = Bot(bot, proxy=proxy, token=token)
    ai_bot = aiogram.Bot(token=fg_bot.token, proxy=fg_bot.proxy)
    dp = aiogram.Dispatcher(ai_bot)

    print(fg_bot.get_aliases_names())
    @dp.message_handler(lambda m: fg_bot.get_command_by_alias(m.text.lower().strip()) or fg_bot.get_command(m.get_command()))
    async def send_message(message):
        print(message)

        if message.is_command():
            cmd = fg_bot.get_command(message.get_command())
            gp = group_media(cmd)
        else:
            cmd = fg_bot.get_command_by_alias(message.text.lower().strip())
            gp = group_media(cmd)
        
        keyboard = None
        if cmd.keyboard:
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            for button_text in cmd.keyboard:
                keyboard.add(button_text)

        for attch in gp:
            if not isinstance(attch, list):
                if attch.type == 'text':
                    with open(attch.file_path, encoding='utf-8') as f:
                        msg = f.read()
                    await message.answer(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)
                elif attch.type == 'audio':
                    await message.answer_audio(
                        aiogram.types.InputFile(attch.file_path),
                        caption=attch.description,
                        title=attch.pretty_name, 
                        parse_mode=ParseMode.HTML,
                        )
                elif attch.type == 'video':
                    await message.answer_video(
                        aiogram.types.InputFile(attch.file_path), 
                        caption=attch.description, 
                        parse_mode=ParseMode.HTML,
                        )
                elif attch.type == 'image':
                    await message.answer_photo(
                        aiogram.types.InputFile(attch.file_path), 
                        caption=attch.description, 
                        parse_mode=ParseMode.HTML,
                        )
                elif attch.type == None:
                    await message.answer_document(
                        aiogram.types.InputFile(attch.file_path), 
                        caption=attch.description, 
                        parse_mode=ParseMode.HTML,
                        )

            elif isinstance(attch, list):
                media = aiogram.types.MediaGroup()
                for item in attch:
                    if item.type == 'image':
                        media.attach_photo(
                            aiogram.types.InputFile(item.file_path), 
                            caption=item.description
                            )
                    elif item.type == 'audio':
                        media.attach_audio(
                            aiogram.types.InputFile(
                                item.file_path),
                                caption=item.description,
                                title=item.pretty_name
                                )
                    elif item.type == 'video':
                        media.attach_video(
                            aiogram.types.InputFile(item.file_path), 
                            caption=item.description
                            )
                    elif item.type == None:
                        media.attach_document(
                            aiogram.types.InputFile(item.file_path), 
                            caption=item.description
                            )
                await message.answer_media_group(media=media)


    aiogram.executor.start_polling(dp, skip_updates=True)
