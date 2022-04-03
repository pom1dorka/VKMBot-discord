from discord import Embed
from discord.utils import get


async def are_in_the_same_voice(bot, ctx):  # функция, которая проверяет, находятся ли пользователь и бот в одном голосовом канале
    bot_voice_cnction = get(bot.voice_clients, guild=ctx.guild)
    if ctx.author.voice is not None:
        if bot_voice_cnction is not None and bot_voice_cnction.is_connected():
            if bot_voice_cnction.channel.id == ctx.author.voice.channel.id:
                return 1
            else:
                await ctx.send(embed=Embed(description='Бот подключен к другому голосовому каналу!', color=0x0077FF))
                return 0
        else:
            await ctx.send(embed=Embed(description='Бот не подключен к голосовому каналу!', color=0x0077FF))
            return 0
    else:
        await ctx.send(embed=Embed(description='Вы не можете управлять ботом, не находясь в голосовом канале!', color=0x0077FF))
        return 0