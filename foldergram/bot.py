from typing import Union
import aiogram, asyncio
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, ParseMode, ContentType, MediaGroup
from aiogram.types.message import Message
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.middlewares import BaseMiddleware


from .types import Bot
from . import database


def start(bot, proxy=None, token=None):
    fg_bot = Bot(bot, proxy=proxy, token=token)
    ai_bot = aiogram.Bot(token=fg_bot.token, proxy=fg_bot.proxy)
    dp = aiogram.Dispatcher(ai_bot, storage=MemoryStorage())
    dp.middleware.setup(AlbumMiddleware())

    # отправка рассылки (изменение стейта)
    @dp.message_handler(lambda m: m.from_user.id in fg_bot.admins and m.text == '/newpost')
    async def admin_message(message, state=FSMContext):
        if await state.get_state() != 'newpost':
            markup = keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add("Отмена")
            await ai_bot.send_message(message.from_user.id, text="Напишите сообщение которое будет разосланно всем", reply_markup=markup)
            await state.set_state('newpost')
            print(await state.get_state())
    
    @dp.message_handler(lambda m: m.from_user.id in fg_bot.admins and m.text == 'Отмена', state="*")
    async def admin_cancel_message(message, state=FSMContext):
        await state.finish()
        await message.answer("Рассылка отменена", reply_markup=ReplyKeyboardRemove())
        print(await state.get_state())

    # триггер на медиагруппу в рассылке
    @dp.message_handler(lambda m: m.text != 'Отмена', is_media_group=True, content_types=ContentType.ANY, state='newpost')
    async def handle_albums(message: Message, album: list[Message], state=FSMContext):
        """This handler will receive a complete album of any type."""
        await state.finish()

        all_users = database.all_users()
        media_group = MediaGroup()
        for obj in album:
            if obj.photo:
                file_id = obj.photo[-1].file_id
            else:
                file_id = obj[obj.content_type].file_id

            try:
                # We can also add a caption to each file by specifying `"caption": "text"`
                media_group.attach({"media": file_id, "type": obj.content_type, "caption": obj.caption})
            except ValueError:
                return await message.answer("This type of album is not supported by aiogram.")
        
        fails = 0
        await message.answer(f'Рассылка начата...', reply_markup=ReplyKeyboardRemove())
        for each in all_users:
            try:
                await ai_bot.send_media_group(each['user_id'], media_group)
            except:
                fails += 1
            await asyncio.sleep(0.25)
        await message.answer(f'Сообщения отправлены! [{len(all_users)-fails} из {len(all_users)}]')

    # триггер на простое сообщение на рассылку
    @dp.message_handler(lambda m: m.from_user.id in fg_bot.admins and m.text != 'Отмена', state='newpost', content_types=ContentType.ANY)
    async def send_admin_message(message, state=FSMContext):
        await state.finish()
        fails = 0
        print(message)
        all_users = database.all_users()
        await message.answer(f'Рассылка начата...\nБудет отправлено сообщений: {len(all_users)}', reply_markup=ReplyKeyboardRemove())
        for each in all_users:
            try:
                await message.copy_to(each['user_id'])
            except:
                fails += 1
            await asyncio.sleep(0.25)
        await message.answer(f'Сообщения отправлены! [{len(all_users)-fails} из {len(all_users)}]')


    @dp.message_handler(lambda m: fg_bot.get_command_by_alias(m.text.lower().strip()) or fg_bot.get_command(m.get_command()))
    async def send_message(message):

        if message.is_command():
            cmd = fg_bot.get_command(message.get_command())
            if cmd == 'start':
                print(f'add user {message}')
                database.add_user(message.from_user.id)
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

                elif attch.type == 'voice':
                    result = await message.answer_voice(
                        attch.cache_id or aiogram.types.InputFile(attch.file_path), 
                        caption=attch.description, 
                        reply_markup=keyboard,
                        )
                    attch.cache_id = result.voice.file_id

                elif attch.type == 'quiz':
                    result = await message.answer_poll(
                        attch.question,
                        attch.options,
                        type='quiz',
                        correct_option_id = attch.answer_indexes[0],
                        explanation=attch.description, 
                        reply_markup=keyboard,
                        )

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



class AlbumMiddleware(BaseMiddleware):
    """This middleware is for capturing media groups."""

    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: Message, data: dict):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()  # Tell aiogram to cancel handler for this group element
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: Message, result: dict, data: dict):
        """Clean up after handling our album."""
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]