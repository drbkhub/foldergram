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
        # print(message)

        if message.is_command():
            cmd = fg_bot.get_command(message.get_command())
            gp = group_media(cmd)
        else:
            cmd = fg_bot.get_command_by_alias(message.text.lower().strip())
            gp = group_media(cmd)
        
        keyboard = None
        if cmd.keyboard:
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True,)# one_time_keyboard=True)
            for button_text in cmd.keyboard:
                keyboard.add(button_text)

        for attch in gp:
            print(attch)
            if not isinstance(attch, list):
                if attch.type == 'text':
                    if attch.message is None:
                        with open(attch.file_path, encoding='utf-8') as f:
                            msg = f.read()
                        attch.message = msg
                    await message.answer(attch.message or msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

                elif attch.type == 'audio':
                    result = await message.answer_audio(
                        attch.cache_id or aiogram.types.InputFile(attch.file_path),
                        caption=attch.description,
                        title=attch.pretty_name, 
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard,
                        )
                    attch.cache_id = result.audio.file_id

                elif attch.type == 'video':
                    result = await message.answer_video(
                        attch.cache_id or aiogram.types.InputFile(attch.file_path), 
                        caption=attch.description, 
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard,
                        )
                    attch.cache_id = result.video.file_id

                elif attch.type == 'image':
                    result = await message.answer_photo(
                        attch.cache_id or aiogram.types.InputFile(attch.file_path), 
                        caption=attch.description, 
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard,
                        )
                    # записываю id фото в кеш вложения
                    attch.cache_id = result.photo[-1].file_id

                elif attch.type == None:
                    result = await message.answer_document(
                        attch.cache_id or aiogram.types.InputFile(attch.file_path), 
                        caption=attch.description, 
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard,
                        )
                    attch.cache_id = result.document.file_id

            elif isinstance(attch, list):
                media = aiogram.types.MediaGroup()
                for item in attch:
                    print(item.cache_id)
                    if item.type == 'image':
                        media.attach_photo(
                            item.cache_id or aiogram.types.InputFile(item.file_path), 
                            caption=item.description
                            )
                    elif item.type == 'audio':
                        media.attach_audio(
                            item.cache_id or aiogram.types.InputFile(
                            item.file_path),
                            caption=item.description,
                            title=item.pretty_name
                            )
                    elif item.type == 'video':
                        media.attach_video(
                            item.cache_id or aiogram.types.InputFile(item.file_path), 
                            caption=item.description
                            )
                    elif item.type == None:
                        media.attach_document(
                            item.cache_id or aiogram.types.InputFile(item.file_path), 
                            caption=item.description
                            )
                result = await message.answer_media_group(media=media)

                # обновление кеша вложений
                print(result)
                for i, item in enumerate(attch):
                    if item.type == 'image':
                        attch[i].cache_id = result[i].photo[-1].file_id
                    elif item.type == 'audio':
                        attch[i].cache_id = result[i].audio.file_id
                    elif item.type == 'video':
                        attch[i].cache_id = result[i].video.file_id
                    elif item.type == None:
                        attch[i].cache_id = result[i].document.file_id
            keyboard=None
            


    aiogram.executor.start_polling(dp, skip_updates=True)
