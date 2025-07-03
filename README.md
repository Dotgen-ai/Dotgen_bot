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

## 🎵 Music Commands

### Basic Music Controls
| Command | Aliases | Description |
|---------|---------|-------------|
| `!play <song/url>` | `!p` | Play music or add to queue |
| `!skip` | `!s` | Skip current track (voting system) |
| `!stop` | - | Stop music and clear queue |
| `!queue [page]` | `!q` | Show current queue with pagination |
| `!nowplaying` | `!np`, `!current` | Show current track with progress |
| `!disconnect` | `!dc`, `!leave` | Disconnect from voice channel |

### Advanced Queue Management
| Command | Description |
|---------|-------------|
| `!search <query>` | Search for tracks without adding to queue |
| `!remove <position>` | Remove track from queue by position |
| `!move <from> <to>` | Move track to different position |
| `!swap <pos1> <pos2>` | Swap two tracks in queue |
| `!clear` | Clear entire queue |
| `!history [page]` | Show recently played tracks |

### Player Controls
| Command | Aliases | Description |
|---------|---------|-------------|
| `!loop [mode]` | `!repeat` | Set loop mode: `none`, `track`, `queue` |
| `!shuffle` | - | Toggle shuffle mode on/off |
| `!volume [0-100]` | `!vol` | Set or show player volume |
| `!previous` | `!prev`, `!back` | Play previous track from history |

### Music Features
- 🎵 **High-quality audio** with yt-dlp and FFmpeg
- 🔁 **Multiple loop modes**: none, track, or entire queue
- 🔀 **Shuffle support** with queue randomization
- 📊 **Rich embeds** with track info, thumbnails, and progress bars
- 🗳️ **Vote-to-skip system** (configurable threshold)
- 📜 **Play history** tracking with pagination
- 🎛️ **Volume control** per-server
- 🔍 **Advanced search** with multiple results
- ⏱️ **Progress tracking** with visual progress bars
- 🎯 **Smart error handling** with bot detection evasion

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
2. Install music dependencies: `pip install yt-dlp PyNaCl`
3. Bot automatically joins your voice channel when you use music commands
4. Advanced features include:
   - **Multiple extraction methods** for reliable playback
   - **Bot detection evasion** with rotating user agents
   - **Smart error handling** with fallback options
   - **Queue persistence** across bot restarts
   - **Rich metadata** with thumbnails and track info
   - **Progress tracking** with visual progress bars
   - **Vote-to-skip system** for democratic control

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

#### Player Issues
- **"No music player found"**: Use `!play` first to initialize the player
- **"Track skipped unexpectedly"**: Check if enough users voted to skip
- **"Volume not changing"**: Volume affects new tracks - try skipping current track
- **"Queue not showing"**: Use `!queue` or `!q` to display current queue
- **"History empty"**: Play some tracks first to build play history

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
- **"Queue is full"**: Maximum 1000 tracks allowed per queue
- **"No skip votes"**: Need majority vote to skip (unless you're the requester)

## 📊 Features Overview

### 🎵 Advanced Music Player
- **Anonymous Operation** - No credentials, cookies, or account connections required
- **Advanced Bot Detection Evasion** - 4-tier fallback extraction system (2024 methods)
- **High-quality audio streaming** - Up to 320kbps with noise filtering and audio enhancement
- **YouTube support** - Direct URLs and search functionality with metadata extraction
- **Rich Queue Management** - Add, remove, move, swap, shuffle with visual feedback
- **Multiple Loop Modes** - None, track repeat, or full queue looping
- **Vote-to-Skip System** - Democratic track skipping with configurable thresholds
- **Progress Tracking** - Visual progress bars and position display
- **Play History** - Track previously played songs with pagination
- **Volume Control** - Per-server volume settings with real-time adjustment
- **Smart Search** - Multi-result search without adding to queue
- **Auto-join voice channels** - Seamless voice channel connection
- **User-friendly error handling** - Clear messages for different failure types
- **Rich Embeds** - Detailed track info with thumbnails and metadata

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
- **Member join/leave tracking** - Monitor server growth and member activity
- **Voice channel activity logs** - Track voice channel joins, leaves, and moves
- **Message edit/delete logs** - Complete message moderation tracking
- **Role change notifications** - Shows WHO changed roles for whom (using audit logs)
- **Nickname change tracking** - Monitor self-changes vs. moderator changes
- **Moderation action logs** - Complete audit trail for all staff actions

**Note**: Role and nickname change logs now use Discord audit logs to show exactly who made the changes, eliminating confusion about who performed moderation actions.

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
