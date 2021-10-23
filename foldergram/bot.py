import aiogram
from .types import Bot
from .utils import group_media

def start(bot, proxy=None, token=None):
    fg_bot = Bot(bot, proxy=proxy, token=token)
    ai_bot = aiogram.Bot(token=fg_bot.token, proxy=fg_bot.proxy)
    dp = aiogram.Dispatcher(ai_bot)

    print(fg_bot.get_command_names())
    @dp.message_handler(commands=fg_bot.get_command_names())
    async def send_message(message):
        await message.answer(str(message))
        print(message)

        gp = group_media(fg_bot.get_command(message.get_command()))
        print(gp)

        for attch in gp:
            if not isinstance(attch, list):
                if attch.type == 'text':
                    with open(attch.file_path, encoding='utf-8') as f:
                        msg = f.read()
                    await message.answer(msg)
                elif attch.type == 'audio':
                    await message.answer_audio(
                        aiogram.types.InputFile(attch.file_path),
                        caption=attch.description,
                        title=attch.pretty_name,
                        )
                elif attch.type == 'video':
                    await message.answer_video(aiogram.types.InputFile(attch.file_path), caption=attch.description)
                elif attch.type == 'image':
                    await message.answer_photo(aiogram.types.InputFile(attch.file_path), caption=attch.description)
                elif attch.type == None:
                    await message.answer_document(aiogram.types.InputFile(attch.file_path), caption=attch.description)

            elif isinstance(attch, list):
                media = aiogram.types.MediaGroup()
                for item in attch:
                    if item.type == 'image':
                        media.attach_photo(aiogram.types.InputFile(item.file_path), caption=item.description)
                    elif item.type == 'audio':
                        media.attach_audio(
                            aiogram.types.InputFile(
                                item.file_path),
                                caption=item.description,
                                title=item.pretty_name
                                )
                    elif item.type == 'video':
                        media.attach_video(aiogram.types.InputFile(item.file_path), caption=item.description)
                    elif item.type == None:
                        media.attach_document(aiogram.types.InputFile(item.file_path), caption=item.description)
                await message.answer_media_group(media=media)


    print('executor')
    aiogram.executor.start_polling(dp, skip_updates=True)


