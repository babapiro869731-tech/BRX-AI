import os
import discord
from discord.ext import commands
from groq import Groq

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

client_ai = Groq(api_key=GROQ_API_KEY)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

histories = {}

@bot.event
async def on_ready():
    print(f"BRX AI aktif: {bot.user}")

@bot.event
async def on_message(message):
    print("MESAJ GELDI:", message.author, repr(message.content))

    if message.author.bot:
        return

    await bot.process_commands(message)

    if bot.user not in message.mentions:
        return

    prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(
        f"<@!{bot.user.id}>", ""
    ).strip()

    if not prompt:
        return

    history = histories.setdefault(message.author.id, [])
    history.append({"role": "user", "content": prompt})
    history[:] = history[-12:]

    try:
        async with message.channel.typing():
            response = client_ai.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Sen BRX AI adlı Türkçe konuşan yardımsever bir Discord asistanısın. Kurucunun adı Vexterdir. Vexter, BRX AI sisteminin kurucusudur. Kurucusu sorulursa Vexter diye cevap ver."},
                    *history
                ],
                max_tokens=1000,
            )
            answer = response.choices[0].message.content or "Yanıt oluşturamadım."
            history.append({"role": "assistant", "content": answer})
            await message.reply(answer[:1900])
    except Exception as error:
        print("GROQ HATASI:", repr(error))
        await message.reply("Bir hata oluştu.")

bot.run(DISCORD_TOKEN)
