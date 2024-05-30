import discord
import speech_recognition as sr
from discord.ext import commands
from pydub import AudioSegment


class Cog(commands.Cog, name="SpeechToTextCog"):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.Cog.listener(name="on_message")
    async def speech_to_text(
        self,
        message: discord.Message
    ) -> None:
        if message.attachments and (att := message.attachments[0]).is_voice_message():
            ogg_path = self.client.path(f"var/{att.filename}")
            wav_path = self.client.path(f"var/{att.filename}".replace(".ogg", ".wav"))
            await att.save(ogg_path)
            ogg = AudioSegment.from_file(ogg_path)
            ogg.export(self.client.path(wav_path), format="wav")

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as wav:
                voice = recognizer.record(wav)

            try:
                # TODO: move language to config/
                await message.reply(recognizer.recognize_google(voice, language="ru-RU"))
            except sr.UnknownValueError:
                await message.reply("Good!")
            except Exception as exc:
                print(f"Cannot respond to voice message: {exc}")
