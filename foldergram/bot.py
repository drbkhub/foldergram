import aiogram, asyncio
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, ParseMode
from aiogram.types.message import Message
from aiogram.contrib.fsm_storage.memory import MemoryStorage


from .types import Bot


def start(bot, proxy=None, token=None):
    fg_bot = Bot(bot, proxy=proxy, token=token)
    ai_bot = aiogram.Bot(token=fg_bot.token, proxy=fg_bot.proxy)
    dp = aiogram.Dispatcher(ai_bot, storage=MemoryStorage())


    @dp.message_handler(lambda m: fg_bot.get_command_by_alias(m.text.lower().strip()) or fg_bot.get_command(m.get_command()))
    async def send_message(message):

        if message.is_command():
            cmd = fg_bot.get_command(message.get_command())
            gp = fg_bot.get_group_media(cmd)
        else:
            cmd = fg_bot.get_command_by_alias(message.text.lower().strip())
            gp = fg_bot.get_group_media(cmd)

        
        keyboard = None
        if cmd.keyboard:
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True,)# one_time_keyboard=True)
            for button_text in cmd.keyboard:
                keyboard.add(button_text)
        elif isinstance(cmd.keyboard, list):
            keyboard = ReplyKeyboardRemove()

        for attch in gp:
            if not isinstance(attch, list):
                if attch.type == 'message':
                    await message.answer(attch.message, reply_markup=keyboard, parse_mode=ParseMode.HTML)

                elif attch.type == 'location':
                    if all(attch.location):
                        result = await message.answer_location(attch.location[0], attch.location[1], reply_markup=keyboard)

                elif attch.type == 'number':
                    result = await message.answer_contact(attch.number[0], attch.number[1], attch.number[2], reply_markup=keyboard)

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
            await asyncio.sleep(.25)
        # await message.delete()
            
    aiogram.executor.start_polling(dp, skip_updates=True)
