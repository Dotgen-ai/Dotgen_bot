# 🤖 DOTGEN.AI Discord Bot

Advanced Discord bot with dynamic voice channels, high-quality ad-free music player, welcome system, and comprehensive admin tools.

## ✨ Features

- 🎵 **Advanced Ad-Free Music Player** - High-quality, anonymous music streaming from YouTube
  - No credentials or cookies required
  - Advanced bot detection evasion (2024 methods)
  - Queue management, shuffle, loop, search
  - Volume control, skip, previous track
  - Automatic fallback extraction methods
- 🎤 **Dynamic Voice Channels** - Auto-create temporary voice channels based on user roles
- 🎉 **Welcome System** - Custom welcome images and messages for new members
- 📝 **Comprehensive Logging** - Track all server activity including joins, leaves, and voice activity
- 🔧 **Admin Tools** - Server management, anonymous announcements, and configuration
- 🌐 **24/7 Uptime** - Built for cloud deployment with keepalive webserver
- ⚡ **Modern Interface** - Both slash commands and legacy prefix commands supported
- 🛡️ **Anonymous Operation** - Music functionality works without any account connections

## 📋 Prerequisites

### Required Software
1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **FFmpeg** - [Download FFmpeg](https://ffmpeg.org/download.html)
   - **Windows**: Download and add to PATH
   - **Linux**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`

### Discord Bot Setup
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and go to "Bot" section
3. Create a bot and copy the bot token
4. **Enable Privileged Gateway Intents**:
   - ✅ **SERVER MEMBERS INTENT**
   - ✅ **MESSAGE CONTENT INTENT**
   - ✅ **PRESENCE INTENT** (optional)
5. **Bot Permissions**: Administrator (or minimum required permissions)

## 🚀 Installation

### 1. Clone/Download
```bash
git clone <repository-url>
cd Discord-Bot
```

### 2. Install Dependencies

**Core Dependencies (Required):**
```bash
pip install discord.py>=2.3.2 python-dotenv yt-dlp>=2024.4.9 PyNaCl ffmpeg-python aiohttp Pillow requests
```

**Enhanced Anti-Detection (Recommended):**
```bash
pip install fake-useragent urllib3 certifi
```

**All Dependencies:**
```bash
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the project root:

```env
# REQUIRED - Your Discord bot token
DISCORD_TOKEN=your_bot_token_here

# OPTIONAL - Channel Configuration
WELCOME_CHANNEL_ID=123456789012345678    # Channel for welcome messages
LOBBY_VOICE_CHANNEL_ID=123456789012345678 # "Join to Create" voice channel
VOICE_LOG_CHANNEL_ID=123456789012345678   # Voice activity logs
VOICE_CATEGORY_ID=123456789012345678      # Category for temp voice channels

# OPTIONAL - Logging Channels
MEMBER_LOG_CHANNEL_ID=123456789012345678     # Member join/leave logs
ROLE_LOG_CHANNEL_ID=123456789012345678       # Role change logs  
MESSAGE_LOG_CHANNEL_ID=123456789012345678    # Message edit/delete logs
MODERATION_LOG_CHANNEL_ID=123456789012345678 # General moderation logs

# OPTIONAL - Role Configuration
DEFAULT_ROLE_ID=123456789012345678           # Default role for voice channels
AUTO_ROLE_ID=123456789012345678              # Auto-assign role for new members
ALLOWED_ROLES=123456789012345678,987654321098765432  # Roles that can create voice channels
SPECIFIC_VC_ROLE_IDS=123456789012345678,987654321098765432  # Specific roles for voice channel naming

# OPTIONAL - Server Configuration
GUILD_ID=123456789012345678                  # Guild ID for slash command sync
BOT_PREFIX=!                                 # Command prefix (default: !)
MAX_VOICE_CHANNEL_LIMIT=10                   # Max temporary voice channels
```

### 4. Run the Bot
```bash
python main.py
```

## 🎵 Music Commands

### 🎯 Essential Music Commands
| Slash Command | Prefix Command | Description |
|---------------|----------------|-------------|
| `/dotgen_play <song>` | `!play <song>` | Play music from YouTube (URL or search) |
| `/dotgen_skip` | `!skip` | Skip the current song |
| `/dotgen_stop` | `!stop` | Stop music and clear queue |
| `/dotgen_queue` | `!queue` | Show the music queue |
| `/dotgen_disconnect` | `!disconnect` | Disconnect from voice channel |

### 🎛️ Advanced Music Controls
| Slash Command | Prefix Command | Description |
|---------------|----------------|-------------|
| `/dotgen_shuffle` | `!shuffle` | Toggle shuffle mode on/off |
| `/dotgen_loop [mode]` | `!loop [mode]` | Loop current song or entire queue |
| `/dotgen_previous` | `!previous` | Play the previous song |
| `/dotgen_volume <1-100>` | `!volume <1-100>` | Change music volume |
| `/dotgen_nowplaying` | `!nowplaying` | Show currently playing song with progress |
| `/dotgen_search <query>` | `!search <query>` | Search for songs without playing |
| `/dotgen_remove <position>` | `!remove <position>` | Remove song from queue |
| `/dotgen_move <from> <to>` | `!move <from> <to>` | Move song to different position |

### 🎵 Music Features
- **Ad-Free Playback**: Advanced anti-ad measures and high-quality audio extraction
- **Auto-Join**: Bot automatically joins your current voice channel
- **Smart Queue**: Add multiple songs, view upcoming tracks
- **Loop Modes**: Loop single song or entire queue
- **Shuffle**: Randomize queue playback order
- **Volume Control**: Adjust volume from 1-100%
- **Progress Tracking**: See song progress and duration
- **Search**: Find songs without immediately playing them
- **Queue Management**: Remove, move, and reorder songs

## 🤖 Bot Commands

### 🎯 Essential Commands
| Slash Command | Prefix Command | Description |
|---------------|----------------|-------------|
| `/dotgen_help` | `!help` | Show all available commands |
| `/dotgen_info` | `!info` | Display bot information and features |
| `/dotgen_ping` | `!ping` | Check bot latency and status |
| `/dotgen_config` | `!config` | View current bot configuration |

### 👋 Welcome System
| Slash Command | Prefix Command | Description |
|---------------|----------------|-------------|
| `/dotgen_welcome [@member]` | `!welcome [@member]` | Send welcome message for a member |
| - | `!setup_welcome` | Configure welcome channel |

### 📢 Admin Commands
| Slash Command | Prefix Command | Description |
|---------------|----------------|-------------|
| `/dotgen_announce <channel> <message>` | `!announce <channel> <message>` | Send **anonymous** announcement to channel (mentions work) |
| - | `!setup_logging` | Configure logging channels |
| - | `!setup_lobby` | Set up voice channel lobby |
| - | `!cleanup_voice` | Clean up temporary voice channels |

### 🎤 Voice Channel Commands
| Command | Description |
|---------|-------------|
| `!setup_lobby` | Create "Join to Create" voice channel |
| `!cleanup_voice` | Remove all temporary voice channels |
| `!voice_limit <number>` | Set user limit for new voice channels |

## ⚙️ Configuration

### Required Permissions
The bot needs these permissions in your Discord server:
- **Administrator** (recommended) OR these specific permissions:
  - View Channels
  - Send Messages
  - Embed Links
  - Attach Files
  - Read Message History
  - Connect to Voice
  - Speak in Voice
  - Manage Channels
  - Manage Messages
  - Manage Roles

### Voice Channel Setup
1. Run `!setup_lobby` to create the "Join to Create" channel
2. Users joining this channel will trigger automatic voice channel creation
3. Channels are named based on the user's highest role
4. Empty channels are automatically deleted

### Music Setup
1. Ensure FFmpeg is installed and in your system PATH
2. Bot will automatically join your voice channel when you use music commands
3. High-quality, ad-free audio is automatically configured
4. Supports YouTube URLs and search queries

## 🌐 24/7 Deployment

### Cloud Deployment Options
- **Railway**: Easy deployment with automatic git integration
- **Heroku**: Free tier available with hobby dynos
- **Replit**: Simple setup for educational use
- **VPS**: Full control with services like DigitalOcean or AWS

### Deployment Tips
1. Set up environment variables in your hosting platform
2. Ensure FFmpeg is available in the deployment environment
3. Configure keep-alive settings for 24/7 operation
4. Monitor logs for any deployment issues

## 🔧 Troubleshooting

### Common Issues

#### Bot Not Responding
- ✅ Check bot token in `.env` file
- ✅ Verify bot permissions in Discord server
- ✅ Ensure bot is online and invite link is valid

#### Music Not Playing
- ✅ Install FFmpeg and add to system PATH
- ✅ Check bot has Connect and Speak permissions in voice channels
- ✅ Verify yt-dlp is installed: `pip install yt-dlp>=2024.4.9`
- ✅ Try a different YouTube video/search term
- ✅ **Bot Detection Issues**: 
  - Bot automatically uses 4 different extraction methods
  - No credentials or cookies required
  - Advanced anti-detection headers and user agents
  - If all methods fail, try again in a few minutes

#### Music Extraction Errors
- **"Age-restricted content"**: Bot will try alternative extraction methods automatically
- **"Video unavailable"**: Video may be private, deleted, or region-blocked
- **"Rate limited"**: Bot will add automatic delays and retry
- **"Sign in required"**: Bot uses anonymous extraction (no sign-in needed)
- **All methods fail**: Try a different video or wait a few minutes for YouTube rate limits to reset

#### Voice Channels Not Creating
- ✅ Run `!setup_lobby` to create the lobby channel
- ✅ Ensure bot has "Manage Channels" permission
- ✅ Check voice category configuration in `.env`

#### Slash Commands Not Working
- ✅ Wait up to 1 hour for global slash command sync
- ✅ Use GUILD_ID in `.env` for instant local testing
- ✅ Check bot has necessary permissions

### Error Messages
- **"Missing FFmpeg"**: Install FFmpeg and restart bot
- **"No voice channel"**: Join a voice channel before using music commands
- **"Permission denied"**: Check bot permissions in server settings
- **"Invalid token"**: Verify DISCORD_TOKEN in `.env` file

## 📊 Features Overview

### 🎵 Music Player
- **Anonymous Operation** - No credentials, cookies, or account connections required
- **Advanced Bot Detection Evasion** - 4-tier fallback extraction system (2024 methods)
- **High-quality audio streaming** - Up to 320kbps with noise filtering and audio enhancement
- **YouTube support** - Direct URLs and search functionality
- **Queue management** - Add, remove, move, shuffle, loop modes
- **Volume control** - Individual track volume and progress tracking
- **Auto-join voice channels** - Seamless voice channel connection
- **User-friendly error handling** - Clear messages for different failure types

### 🎤 Dynamic Voice Channels
- Automatic channel creation based on user roles
- Customizable permissions and user limits
- Auto-cleanup when channels become empty
- Role-based channel naming

### 🎉 Welcome System
- Custom welcome images with member avatars
- Random welcome message selection
- Member count and join date display
- Automatic role assignment

### 📝 Comprehensive Logging
- Member join/leave tracking
- Voice channel activity logs
- Message edit/delete logs
- Role change notifications
- Moderation action logs

## 💡 Tips & Best Practices

### Music Usage
- Use `/dotgen_play` instead of `!play` for better autocomplete
- Queue multiple songs at once for continuous playback
- Use shuffle mode for variety in long playlists
- Adjust volume before playing for better experience

### Administration
- Set up logging channels for better server monitoring
- Use role-based permissions for voice channel creation
- Configure welcome channels for new member engagement
- Regular cleanup of temporary channels

### Performance
- Monitor bot CPU usage during heavy music usage
- Consider voice channel limits to prevent spam
- Use slash commands for better user experience
- Enable privileged intents for full functionality

## 🆘 Support

### Getting Help
1. Check this README for common solutions
2. Review console output for error messages
3. Verify all permissions and configuration
4. Test with minimal configuration first

### Development
- Bot uses discord.py 2.3.0+
- Modern async/await patterns
- Comprehensive error handling
- Modular command structure

---

**🌟 Enjoy your advanced Discord bot with high-quality music and comprehensive server management!**
# Required
DISCORD_TOKEN=your_bot_token_here

# Optional Configuration
WELCOME_CHANNEL_ID=123456789012345678
LOBBY_VOICE_CHANNEL_ID=123456789012345678
VOICE_LOG_CHANNEL_ID=123456789012345678
VOICE_CATEGORY_ID=123456789012345678
GUILD_ID=123456789012345678
DEFAULT_ROLE_ID=123456789012345678
AUTO_ROLE_ID=123456789012345678
BOT_PREFIX=!
MAX_VOICE_CHANNEL_LIMIT=10

# Logging Channels
MEMBER_LOG_CHANNEL_ID=123456789012345678
ROLE_LOG_CHANNEL_ID=123456789012345678
MESSAGE_LOG_CHANNEL_ID=123456789012345678
MODERATION_LOG_CHANNEL_ID=123456789012345678

# Role-based Access
ALLOWED_ROLES=123456789012345678,987654321098765432
SPECIFIC_VC_ROLE_IDS=123456789012345678,987654321098765432

# Deployment (Optional)
PORT=8080
```

### 4. Run the Bot
```bash
python main.py
```

## 🎵 Music Commands

### Slash Commands (Recommended)
| Command | Description | Usage |
|---------|-------------|-------|
| `/dotgen_play` | Play music from YouTube | `/dotgen_play Never Gonna Give You Up` |
| `/dotgen_skip` | Skip current song | `/dotgen_skip` |
| `/dotgen_stop` | Stop music and clear queue | `/dotgen_stop` |
| `/dotgen_queue` | Show music queue | `/dotgen_queue` |
| `/dotgen_volume` | Set volume (0-100) | `/dotgen_volume 50` |
| `/dotgen_shuffle` | Toggle shuffle mode | `/dotgen_shuffle` |
| `/dotgen_loop` | Toggle loop mode | `/dotgen_loop song` |
| `/dotgen_previous` | Play previous song | `/dotgen_previous` |
| `/dotgen_remove` | Remove song from queue | `/dotgen_remove 3` |
| `/dotgen_move` | Move song in queue | `/dotgen_move 3 1` |
| `/dotgen_nowplaying` | Show current song info | `/dotgen_nowplaying` |
| `/dotgen_search` | Search for songs | `/dotgen_search acoustic guitar` |
| `/dotgen_disconnect` | Disconnect from voice | `/dotgen_disconnect` |

### Legacy Prefix Commands
| Command | Aliases | Description |
|---------|---------|-------------|
| `!play <song>` | `!p` | Play music |
| `!skip` | `!s` | Skip current song |
| `!stop` | | Stop music |
| `!queue` | `!q` | Show queue |
| `!volume <0-100>` | `!vol` | Set volume |
| `!disconnect` | `!dc`, `!leave` | Disconnect |

## 🎤 Voice Channel Commands

| Command | Description |
|---------|-------------|
| `!setup_lobby` | Create lobby voice channel |
| `!voice_stats` | Show voice channel statistics |
| `!cleanup` | Clean up empty voice channels |

## 👋 Welcome & Admin Commands

### Slash Commands
| Command | Description | Permissions |
|---------|-------------|-------------|
| `/dotgen_welcome` | Send welcome message | Manage Messages |
| `/dotgen_announce` | Send **anonymous** announcement (mentions work properly) | Administrator |
| `/dotgen_config` | View bot configuration | Administrator |
| `/dotgen_help` | Show all commands | Everyone |
| `/dotgen_info` | Bot information | Everyone |
| `/dotgen_ping` | Check bot status | Everyone |

### Prefix Commands
| Command | Description | Permissions |
|---------|-------------|-------------|
| `!welcome @user` | Manual welcome | Everyone |
| `!announce <channel> <message>` | Send announcement | Administrator |
| `!config` | View configuration | Administrator |
| `!setup_logging` | Setup logging channels | Administrator |
| `!get_ids` | Get channel IDs | Administrator |

## 🔧 Admin & Management Commands

| Command | Aliases | Description | Permissions |
|---------|---------|-------------|-------------|
| `!add_role @role` | | Add allowed role for VC | Administrator |
| `!remove_role @role` | | Remove allowed role | Administrator |
| `!list_roles` | `!roles` | List allowed roles | Administrator |
| `!send <channel> <message>` | | Send message as bot | Administrator |
| `!echo <message>` | | Repeat message | Manage Messages |
| `!botstatus` | `!activity` | Control bot status | Administrator |

## 📊 Information Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `!bot_info` | `!info` | Bot information |
| `!ping` | | Check bot latency |
| `!help [command]` | | Dynamic help system |

## ⚙️ Configuration Guide

### Channel IDs Setup
1. Enable Developer Mode in Discord
2. Right-click channels → "Copy ID"
3. Add IDs to `.env` file
4. Use `!get_ids` command for help

### Voice Channel Setup
1. Use `!setup_lobby` to create lobby channel
2. Set `LOBBY_VOICE_CHANNEL_ID` in `.env`
3. Users join lobby → auto-create temporary channels
4. Channels auto-delete when empty

### Logging Setup
1. Create log channels (`#member-logs`, `#voice-logs`, etc.)
2. Get channel IDs with `!get_ids`
3. Set in `.env` file
4. Use `!setup_logging` for detailed setup

### Role-based Access
- `ALLOWED_ROLES`: Who can create voice channels
- `SPECIFIC_VC_ROLE_IDS`: Special voice channel roles
- `AUTO_ROLE_ID`: Role given to new members

## 🎵 Music Features

### Advanced Features
- **Ad-free Playback** - Optimized for clean audio streams
- **Queue Management** - Add, remove, move, shuffle songs
- **Loop Modes** - Loop current song or entire queue
- **History** - Track and replay previous songs
- **Volume Control** - Per-server volume settings
- **Search** - Preview songs before adding to queue
- **Auto-join** - Bot joins your voice channel automatically

### Supported Sources
- YouTube (primary)
- YouTube Music
- Direct audio links
- Playlists (coming soon)

### Audio Quality
- High-quality audio (192kbps MP3)
- No ads or interruptions
- Optimized for Discord voice channels
- FFmpeg audio processing

## 🌐 Deployment

### Local Development
```bash
python main.py
```

### Cloud Deployment (Heroku, Railway, etc.)
1. Set environment variables in platform
2. Include `Procfile`:
   ```
   worker: python main.py
   ```
3. Enable webserver for keepalive
4. Bot includes automatic uptime monitoring

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 🔧 Troubleshooting

### Common Issues

**Music not working:**
- Install FFmpeg and add to PATH
- Install yt-dlp: `pip install yt-dlp`
- Check voice channel permissions

**Commands not showing:**
- Enable privileged intents in Discord Developer Portal
- Wait up to 1 hour for global slash command sync
- Use guild-specific sync with `GUILD_ID` in `.env`

**Permission errors:**
- Check bot has required permissions in Discord
- Verify role hierarchy (bot role above managed roles)

**Bot disconnecting:**
- Enable webserver with Flask
- Use process manager (PM2, systemd)
- Check hosting platform requirements

### Getting Help
1. Check console output for errors
2. Use `!config` to verify setup
3. Ensure all IDs in `.env` are correct
4. Verify Discord permissions

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🚀 Features in Development

- [ ] Playlist support
- [ ] Spotify integration
- [ ] Custom sound effects
- [ ] Advanced admin dashboard
- [ ] Multi-language support
- [ ] Voice channel templates

---

**Made with ❤️ for the Discord community**

*For support, issues, or feature requests, please check the repository issues or contact the development team.*

### 1. Create a Discord Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Copy the bot token

### 2. Bot Permissions
Your bot needs the following permissions:
- Send Messages
- Embed Links
- Read Message History
- View Channels
- Connect (Voice)
- Move Members
- Manage Channels
- Manage Roles

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
1. Copy `.env.example` to `.env`
2. Replace `your_bot_token_here` with your actual bot token
3. **Get Channel/Server IDs:**
   - Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
   - Right-click on channels/server and select "Copy ID"
   - Or use the bot command `!get_ids` after the bot is running
4. Fill in the IDs in your `.env` file:
   - `WELCOME_CHANNEL_ID` - Channel where welcome messages are sent
   - `LOBBY_VOICE_CHANNEL_ID` - Voice channel users join to create temporary channels
   - `VOICE_CATEGORY_ID` - Category where temporary voice channels are created
   - `GUILD_ID` - Your Discord server ID
   - `DEFAULT_ROLE_ID` - Default role for users without specific roles (optional)
5. Save the file

### 5. Run the Bot
```bash
python main.py
```

## Commands

### Admin Commands (Requires Administrator permission)
- `!setup_lobby [category_name]` - Creates the "Join to Create" voice channel
- `!cleanup_channels` - Manually clean up empty temporary voice channels
- `!welcome_test [member]` - Test the welcome message system
- `!get_ids [channel_mention]` - Get channel and server IDs for .env configuration
- `!config_status` - Check current bot configuration status

### General Commands
- `!bot_info` - Display bot information and features

## Easy Setup with IDs

### Method 1: Automatic Setup (Recommended)
1. Run the bot with just the token in your .env file
2. Use `!get_ids` command to get all necessary IDs
3. Use `!setup_lobby` to create the lobby voice channel
4. Copy the IDs from the bot's response into your .env file
5. Restart the bot

### Method 2: Manual Setup
1. Enable Developer Mode in Discord
2. Right-click on channels/server to copy IDs
3. Add them to your .env file before running the bot

## How It Works

### Welcome Messages
When a new member joins:
1. Bot selects a random welcome message from the template list
2. Creates an embed with member information
3. Sends to the server's system channel or a general channel

### Voice Channel Creation
1. Admin runs `!setup_lobby` to create the lobby channel
2. When a user joins the "Join to Create" channel:
   - Bot identifies the user's highest role
   - Creates a new voice channel named after their role
   - Sets appropriate permissions
   - Moves the user to the new channel
3. When the channel becomes empty, it's automatically deleted

## Customization

### Adding More Welcome Messages
Edit the `WELCOME_MESSAGES` list in `main.py` to add your own welcome messages. Use `{member}` as a placeholder for the member mention.

### Changing Voice Channel Settings
Modify the `handle_voice_channel_creation` function to:
- Change user limits
- Adjust permissions
- Modify naming conventions

## Troubleshooting

### Bot Not Responding
- Check that the bot token is correct in your `.env` file
- Ensure the bot has proper permissions in your server
- Check the console for error messages

### Voice Channels Not Creating
- Make sure the bot has "Manage Channels" permission
- Verify the lobby channel exists and is named "Join to Create"
- Check that the bot can see and access voice channels

### Welcome Messages Not Sending
- Ensure the bot has "Send Messages" and "Embed Links" permissions
- Check that there's an appropriate channel for welcome messages
- Verify the bot can access the system channel or general channels

## Support

If you encounter any issues, check the console output for error messages and ensure all permissions are properly configured.
