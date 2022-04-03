from discord.ext import commands
from discord import Embed
from asyncio import run_coroutine_threadsafe
from random import shuffle as r_shuffle

from auth_data import DS_TOKEN
from functions.are_in_the_same_voice import are_in_the_same_voice
from queueue import Queueue
# оосновной файл, отвечающий за работу бота
bot = commands.Bot(command_prefix='!', help_command=None)  # инициализация переменных, которые будут использоваться
queueue = Queueue()                                        # во всей программе
disconnected = False
with open('help.txt', encoding='utf-8') as f:  # в файле help.txt содержится текст, выводимый командой help.
    help_txt = f.readlines()                   # вынесен в отдельный файл, так как слишком большой


@bot.command(aliases=['h'])  # команда помощи, выводит список всех команд бота
async def help(ctx):
    global help_txt
    print(help_txt)
    await ctx.send(embed=Embed(title='Команды бота:', description=''.join(help_txt), color=0x0077FF))


async def playsong():  # вспомогательная ф-ция, отвечающая за переключение песен
    global context, disconnected
    try:
        song = queueue.pop(0)
    except IndexError:
        if not disconnected:
            await context.send(embed=Embed(description=f'Песни в очереди закончились!', color=0x0077FF))
        return

    player = song['player']
    queueue.current = f'{song["artist"]} - {song["title"]}'

    bot.voice_clients[0].play(player, after=nextsong)
    await context.send(embed=Embed(description=f'Сейчас играет `{queueue.current}`', color=0x0077FF))


def nextsong(error):  # вспомогательная ф-ция для запуска предыдущей ф-ции по окончании песни
    fut = run_coroutine_threadsafe(playsong(), bot.loop)
    fut.result()


@bot.command(aliases=['p', 'add'])
async def play(ctx, *query):  # команда для добавления песни в очередь
    if not bot.voice_clients and ctx.author.voice is not None:
        await ctx.author.voice.channel.connect()
    if await are_in_the_same_voice(bot, ctx):
        if len(queueue) >= 50:
            await ctx.send(embed=Embed(description='Ограничение очереди - 50 песен!', color=0x0077FF))
        else:
            song = queueue.add(' '.join(query))
            if song == 0:
                await ctx.send(embed=Embed(description='Такая песня не найдена!', color=0x0077FF))
                return
            elif len(queueue) == 1 and not (bot.voice_clients[0].is_playing() or bot.voice_clients[0].is_paused()):
                global context, disconnected
                disconnected = False
                context = ctx
                await playsong()
            else:
                await ctx.send(embed=Embed(description=f'Песня `{song["title"]}` от исполнителя `{song["artist"]}` добавлена в очередь!', color=0x0077FF))


@bot.command(aliases=['dc', 'leave'])
async def disconnect(ctx):  # команда для отключения бота от голосового канала
    if await are_in_the_same_voice(bot, ctx):
        global disconnected
        disconnected = True
        await ctx.send(embed=Embed(description='Бот покинул голосовой канал.', color=0x0077FF))
        queueue.clear()
        await bot.voice_clients[0].disconnect()


@bot.command(aliases=['np', 'current', 'cur'])
async def nowplaying(ctx):  # команда, выводящая название песни, которая играет
    if await are_in_the_same_voice(bot, ctx):
        if bot.voice_clients[0].is_paused():
            await ctx.send(embed=Embed(description=f'Сейчас играет `{queueue.current}` *(на паузе)*', color=0x0077FF))
        elif bot.voice_clients[0].is_playing():
            await ctx.send(embed=Embed(description=f'Сейчас играет `{queueue.current}`', color=0x0077FF))
        else:
            await ctx.send(embed=Embed(description='Сейчас ничего не играет.', color=0x0077FF))


@bot.command()
async def pause(ctx):  # команда для приостановки воспроизведения
    if await are_in_the_same_voice(bot, ctx):
        if bot.voice_clients[0].is_paused():
            await ctx.send(embed=Embed(description='Музыка уже на паузе!', color=0x0077FF))
            return
        elif bot.voice_clients[0].is_playing():
            bot.voice_clients[0].pause()
            await ctx.send(embed=Embed(description='Музыка поставлена на паузу.', color=0x0077FF))
        else:
            await ctx.send(embed=Embed(description='Сейчас ничего не играет!', color=0x0077FF))


@bot.command()
async def resume(ctx):  # команда для возобновления воспроизведения
    if await are_in_the_same_voice(bot, ctx):
        if bot.voice_clients[0].is_playing():
            await ctx.send(embed=Embed(description='Музыка уже играет!', color=0x0077FF))
            return
        elif bot.voice_clients[0].is_paused():
            bot.voice_clients[0].resume()
            await ctx.send(embed=Embed(description='Музыка возобновлена.', color=0x0077FF))
        else:
            await ctx.send(embed=Embed(description='Сейчас ничего не играет!', color=0x0077FF))


@bot.command(aliases=['q'])
async def queue(ctx):  # команда, выводящая текущую очередь песен
    if await are_in_the_same_voice(bot, ctx):
        if queueue.is_empty() and not (bot.voice_clients[0].is_playing() or bot.voice_clients[0].is_paused()):
            await ctx.send(embed=Embed(description='В очереди нет песен.', color=0x0077FF))
        else:
            now = ':arrow_forward: ' + queueue.current + ' *`(играет сейчас)`*'
            list = '\n\n'.join([now] + [f'{n+1}.  {t["artist"]} - {t["title"]}' for n, t in enumerate(queueue.list)])
            await ctx.send(embed=Embed(title='Очередь воспроизведения:', description=list, color=0x0077FF))


@bot.command()  # команда для перемешивания очереди
async def shuffle(ctx):
    if await are_in_the_same_voice(bot, ctx):
        if queueue.is_empty():
            await ctx.send(embed=Embed(description='В очереди нет песен.', color=0x0077FF))
        else:
            r_shuffle(queueue.list)
            await ctx.send(embed=Embed(description='Очередь перемешана.', color=0x0077FF))


@bot.command(aliases=['rm', 'delete', 'del'])
async def remove(ctx, index):  # команда для удаления песни(-ен) из очереди
    if await are_in_the_same_voice(bot, ctx):
        if queueue.is_empty():
            await ctx.send(embed=Embed(description='В очереди нет песен.', color=0x0077FF))
        else:
            if index.isdigit() and 0 < int(index) <= len(queueue):
                del queueue.list[int(index)-1]
                await ctx.send(embed=Embed(description=f'Песня под номером {index} удалена из очереди.', color=0x0077FF))
                return

            elif [i.isdigit() and 0 < int(i) <= len(queueue) for i in index.split('-')] == [True, True]:
                a, b = [int(i) for i in index.split('-')]
                if a < b:
                    del queueue.list[a-1:b]
                    await ctx.send(embed=Embed(description=f'Песни c {a} по {b} удалены из очереди.', color=0x0077FF))
                    return

            elif index == 'next':
                del queueue.list[0]
                await ctx.send(embed=Embed(description=f'Следующая песня удалена из очереди.', color=0x0077FF))
                return

            await ctx.send(embed=Embed(description='Неверный аргумент для команды. Используйте !help, чтобы узнать, как правильно использовать данную команду.', color=0x0077FF))


@bot.command(aliases=['s', 'next'])
async def skip(ctx):  # команда для пропуска текущей песни
    if await are_in_the_same_voice(bot, ctx):
        if not (bot.voice_clients[0].is_playing() or bot.voice_clients[0].is_paused()):
            await ctx.send(embed=Embed(description='Сейчас ничего не играет!', color=0x0077FF))
        else:
            bot.voice_clients[0].stop()
            await ctx.send(embed=Embed(description=f'Песня `{queueue.current}` была пропущена.', color=0x0077FF))


@bot.command(aliases=['st'])
async def skipto(ctx, index):  # команда для пропуска всех песен до определённой
    if await are_in_the_same_voice(bot, ctx):
        if queueue.is_empty():
            await ctx.send(embed=Embed(description='В очереди нет песен.', color=0x0077FF))
        else:
            if index.isdigit() and 1 < int(index) <= len(queueue):
                del queueue.list[0:int(index)-1]
            elif index.isdigit() and int(index) == 1:
                pass
            else:
                await ctx.send(embed=Embed(description='Неверный аргумент для команды. Используйте !help, чтобы узнать, как правильно использовать данную команду.', color=0x0077FF))
                return

            await ctx.send(embed=Embed(description=f'Все песни до {index} (не включая её) пропущены.', color=0x0077FF))
            bot.voice_clients[0].stop()


@bot.command()
async def clear(ctx):  # команда для очистки очереди
    if await are_in_the_same_voice(bot, ctx):
        if queueue.is_empty():
            await ctx.send(embed=Embed(description='В очереди нет песен.', color=0x0077FF))
        else:
            queueue.clear()
            await ctx.send(embed=Embed(description='Очередь была очищена.', color=0x0077FF))


@bot.command()
async def stop(ctx):  # команда для очистки очереди и остановки вопроизведения
    if await are_in_the_same_voice(bot, ctx):
        queueue.__init__()
        global disconnected
        disconnected = True
        bot.voice_clients[0].stop()
        await ctx.send(embed=Embed(description='Воспроизведение остановлено, очередь очищена.', color=0x0077FF))


bot.run(DS_TOKEN)  # запуск бота