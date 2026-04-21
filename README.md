# 👻 Phantom

> A Discord-based remote administration bot built for **educational purposes only**.  
> Designed to demonstrate how bots, system APIs, and remote I/O can interact — not for unauthorized use.

---

## ⚠️ Disclaimer

This project was created **strictly for learning and educational purposes**.  
I am **completely against** any malicious, unauthorized, or illegal use of this software.

Using this bot on any machine **without explicit permission from the owner is illegal** and violates:
- Computer Fraud and Abuse Act (CFAA) — USA
- Computer Misuse Act — UK
- Comparable laws in most other countries

**By using this project, you agree to only run it on machines you own or have explicit written permission to access.**  
The author holds no responsibility for any misuse of this software.

---

## 📖 What is Phantom?

Phantom is a Discord bot that lets you remotely interact with a Windows machine through Discord commands. It was built as a hands-on way to learn:

- Python async programming with `discord.py`
- System-level APIs (`subprocess`, `pynput`, `cv2`, `mss`)
- Blocking vs non-blocking code in async environments
- Building structured Discord bots with Cogs

---

## ✨ Features

| Category | Command | Description |
|----------|---------|-------------|
| ⚙️ General | `!cmd` | Run a shell command on the host |
| ⚙️ General | `!screenshot` | Capture all monitors and send them |
| ⚙️ General | `!webcam` | Capture a webcam frame |
| ⚙️ General | `!sound` | Play an MP3 from a URL or attachment |
| ⚙️ General | `!download` | Download a file to the host machine |
| 🖱️ Mouse | `!move` | Move the cursor by (x, y) pixels |
| 🖱️ Mouse | `!set_position` | Set the cursor to an absolute position |
| 🖱️ Mouse | `!click` | Click a mouse button |
| 🖱️ Mouse | `!hold` | Hold down a mouse button |
| 🖱️ Mouse | `!release` | Release a held mouse button |
| 🖱️ Mouse | `!scroll` | Scroll the mouse wheel |
| ⌨️ Keyboard | `!type` | Type text on the host machine |
| ⌨️ Keyboard | `!start_keylogger` | Start capturing keystrokes |
| ⌨️ Keyboard | `!stop_keylogger` | Stop and print captured keystrokes |
| ⌨️ Keyboard | `!current_pressed` | Print keystrokes captured so far |

Run `!help` in Discord for the full help menu, or `!help <command>` for details on a specific command.

---

## 🛠️ Requirements

- Python 3.11+
- Windows (some features use Windows-only APIs)
- A Discord bot token

### Dependencies

```
discord.py
pynput
mss
opencv-python
pygame
requests
```

Install all at once:

```bash
pip install -r requirements.txt
```

---

## 🚀 Setup

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/phantom.git
cd phantom
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Create your Discord bot**
- Go to [discord.com/developers](https://discord.com/developers/applications)
- Create a new application and add a bot
- Under *Privileged Gateway Intents*, enable all three intents
- Copy your bot token

**4. Create the TOKEN file**
```bash
echo YOUR_BOT_TOKEN_HERE > TOKEN
```

**5. Update the owner ID**  
In `main.py`, replace the ID in `bot.fetch_user(...)` with your own Discord user ID.

**6. Run the bot**
```bash
python main.py
```

---

## 📁 Project Structure

```
phantom/
├── main.py          # Bot entry point, all commands and cogs
├── TOKEN            # Your bot token (never commit this!)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🔒 Security Notes

- **Never commit your TOKEN file.** It is in `.gitignore` for a reason.
- Run the bot only on your own machine or a machine you have permission to use.
- Consider restricting the bot to a private server with only trusted users.

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

You are free to use, copy, modify, and distribute this software for personal and educational purposes.  
You are **not permitted** to use this software for unauthorized access to systems you do not own.

---

## 🙏 Acknowledgements

Built with:
- [discord.py](https://github.com/Rapptz/discord.py)
- [pynput](https://github.com/moses-palmer/pynput)
- [mss](https://github.com/BoboTiG/python-mss)
- [OpenCV](https://opencv.org/)
- [pygame](https://www.pygame.org/)
