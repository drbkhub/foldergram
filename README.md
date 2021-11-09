# foldergram
Создавайте бота телеграм из папки с файлами!

БЫСТРЫЙ СТАРТ

1. Создайте папку с навзванием вашего бота (придумайте любое)
2. В папке бота создайте папку с командами "commands"
3. В папке "commands" создайте папку "start"
4. В папке "start" создайте текстовый файл (оканчивается на .txt) и напишите свое любое сообщение (длиной до 15000 символов).

Также вам понадобиться создать в папке с башим ботом файл "token.txt" и вписать туда токен вашего бота.

СТРУКТУРА:
```
[Мой Бот]
--- [commands]
--- --- [start]
--- --- --- Сообщение.txt
--- token.txt
```
Поместите исполняемый файл в папку вашего бота!

Запустите бота (бот не имеет интерфейся)

## Поддерживаемые типы сообщений
- **текстовое сообщение** - ('.txt') - текстовый файл (в кодировке utf-8)
- **изображения** ('.bmp', '.gif', '.jpeg', '.jpg', '.png')
- **аудио** ('.aac', '.mp3', '.wav')
- **видео** ('.avi', '.mkv', '.mp4', '.webm')
- **документы** (любые другие расширения файлов)
- **точка на карте** ('.loc') - *текстовый файл, с долготой и широтой на разных строках
- **голосовое сообщение** - аудио в с расширением '.ogg' в кодеке opus! (vorbis может не подойти). Конвертировать аудио - https://audio.online-convert.com/ru/convert-to-ogg
- **визитка** - ('.num') - *текстовый файл, c номером, именем, фамилией(необязательна) на разных строках
- **квиз** - ('.ogg') - *текстовый файл, первая строка вопрос, остальные - варианты ответов (каждая строка да 10 вариантов, минимум 2), правильный ответ начинается с *

В команде может быть несколько сообщений (добавляете в папку)! Порядок следования - по возрастанию.

Изображения, аудио, видео, документы - могут иметь подпись (создайте текстовый файл с таким же названием только с расширением .txt - и добавьте подпись)
