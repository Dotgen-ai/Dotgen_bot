import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import os
import re
import sys
from dotenv import load_dotenv
import threading
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests
import io

# Music functionality imports with enhanced error handling
try:
    import yt_dlp as youtube_dl
    YOUTUBE_DL_AVAILABLE = True
    print("✅ yt-dlp available - advanced music functionality enabled")
except ImportError:
    try:
        import youtube_dl
        YOUTUBE_DL_AVAILABLE = True
        print("✅ youtube-dl available - basic music functionality enabled")
    except ImportError:
        print("⚠️  YouTube downloader not available - music functionality disabled")
        print("   Install with: pip install yt-dlp")
        YOUTUBE_DL_AVAILABLE = False

# Anti-detection imports
try:
    from fake_useragent import UserAgent
    ua = UserAgent()
    FAKE_USERAGENT_AVAILABLE = True
    print("✅ fake-useragent available for enhanced bot detection evasion")
except ImportError:
    FAKE_USERAGENT_AVAILABLE = False
    print("⚠️  fake-useragent not available (optional for enhanced evasion)")

# Additional music imports for enhanced functionality (OPTIONAL - NO CREDENTIALS REQUIRED)
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIFY_AVAILABLE = True
    print("✅ Spotify integration available (optional - no credentials required for basic use)")
except ImportError:
    SPOTIFY_AVAILABLE = False
    print("⚠️  Spotify integration not available (optional)")

# Optional Flask import for webserver (for 24/7 deployment)
try:
    from flask import Flask, jsonify
    FLASK_AVAILABLE = True
    print("✅ Flask imported successfully - webserver will be available")
except ImportError:
    print("⚠️  Flask not available - running without webserver")
    FLASK_AVAILABLE = False

# Load environment variables
load_dotenv()

# Bot configuration from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
WELCOME_CHANNEL_ID = int(os.getenv('WELCOME_CHANNEL_ID', 0)) or None
LOBBY_VOICE_CHANNEL_ID = int(os.getenv('LOBBY_VOICE_CHANNEL_ID', 0)) or None
VOICE_LOG_CHANNEL_ID = int(os.getenv('VOICE_LOG_CHANNEL_ID', 0)) or None
VOICE_CATEGORY_ID = int(os.getenv('VOICE_CATEGORY_ID', 0)) or None
GUILD_ID = int(os.getenv('GUILD_ID', 0)) or None
DEFAULT_ROLE_ID = int(os.getenv('DEFAULT_ROLE_ID', 0)) or None
AUTO_ROLE_ID = int(os.getenv('AUTO_ROLE_ID', 0)) or None  # Role to give to new members
BOT_PREFIX = os.getenv('BOT_PREFIX', '!')
MAX_VOICE_LIMIT = int(os.getenv('MAX_VOICE_CHANNEL_LIMIT', 10))

# Logging channel configuration
MEMBER_LOG_CHANNEL_ID = int(os.getenv('MEMBER_LOG_CHANNEL_ID', 0)) or None  # Join/Leave logs
ROLE_LOG_CHANNEL_ID = int(os.getenv('ROLE_LOG_CHANNEL_ID', 0)) or None      # Role change logs
MESSAGE_LOG_CHANNEL_ID = int(os.getenv('MESSAGE_LOG_CHANNEL_ID', 0)) or None # Message edit/delete logs
MODERATION_LOG_CHANNEL_ID = int(os.getenv('MODERATION_LOG_CHANNEL_ID', 0)) or None # General moderation logs

# Parse specific VC roles from environment variable (multiple roles allowed)
SPECIFIC_VC_ROLE_IDS = []
if os.getenv('SPECIFIC_VC_ROLE_IDS'):
    try:
        SPECIFIC_VC_ROLE_IDS = [int(role_id.strip()) for role_id in os.getenv('SPECIFIC_VC_ROLE_IDS').split(',') if role_id.strip()]
    except ValueError:
        print("⚠️  Invalid SPECIFIC_VC_ROLE_IDS format in .env file. Should be comma-separated role IDs.")

# Parse allowed roles from environment variable
ALLOWED_ROLES = []
if os.getenv('ALLOWED_ROLES'):
    try:
        ALLOWED_ROLES = [int(role_id.strip()) for role_id in os.getenv('ALLOWED_ROLES').split(',') if role_id.strip()]
    except ValueError:
        print("⚠️  Invalid ALLOWED_ROLES format in .env file. Should be comma-separated role IDs.")

# Bot configuration with automatic privileged intent detection
intents = discord.Intents.default()
intents.message_content = True

# Try to enable privileged intents, detect if they're available
privileged_intents_available = True
try:
    intents.members = True
    intents.voice_states = True
except:
    privileged_intents_available = False

# Remove default help command to create our own dynamic one
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)

# Store temporary voice channels for cleanup and role-based grouping
temp_voice_channels = {}
role_voice_channels = {}  # Track voice channels by role

# Music functionality variables
music_queues = {}  # Store music queues per guild
voice_clients = {}  # Store voice clients per guild

# YouTube DL options for music (ENHANCED FOR MAXIMUM BOT DETECTION EVASION - 2024)
if YOUTUBE_DL_AVAILABLE:
    # Generate dynamic user agent
    def get_user_agent():
        if FAKE_USERAGENT_AVAILABLE:
            try:
                return ua.random
            except:
                pass
        # Fallback to recent Chrome user agents
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0'
        ]
        return random.choice(agents)

    ytdl_format_options = {
        # Audio format selection with fallback hierarchy
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio[ext=mp3]/bestaudio/best[height<=480]',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0',
        'prefer_ffmpeg': True,
        
        # ENHANCED BOT DETECTION EVASION - 2024 METHODS
        'http_headers': {
            'User-Agent': get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        },
        
        # Advanced extractor arguments for 2024 YouTube changes
        'extractor_args': {
            'youtube': {
                'skip': ['dash', 'hls'],
                'player_client': ['android_creator', 'android_music', 'android', 'web_creator', 'web_music', 'web'],
                'player_skip': ['configs'],
                'innertube_host': 'youtubei.googleapis.com',
                'innertube_key': None,
                'check_formats': None,
                'comment_sort': 'top',
                'max_comments': [0],
            }
        },
        
        # Enhanced anti-detection timing and retry logic
        'sleep_interval': random.uniform(1, 3),
        'max_sleep_interval': 8,
        'sleep_interval_requests': random.uniform(0.5, 2),
        'sleep_interval_subtitles': 0,
        'retries': 5,
        'fragment_retries': 5,
        'extract_flat': False,
        'writethumbnail': False,
        'writeinfojson': False,
        
        # Geographic and proxy settings
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        'force_ipv4': True,
        
        # NO CREDENTIALS OR COOKIES REQUIRED - Anonymous access only
        'cookiesfrombrowser': None,
        'cookiefile': None,
        'username': None,
        'password': None,
        'netrc': False,
        
        # Skip all unnecessary downloads and metadata
        'writesubtitles': False,
        'writeautomaticsub': False,
        'writedescription': False,
        'writecomments': False,
        'writeannotations': False,
        'writethumbnail': False,
        'writeinfojson': False,
        
        # Additional bypass options
        'youtube_include_dash_manifest': False,
        'mark_watched': False,
        'no_color': True,
        'extract_flat': False,
    }

    # Enhanced FFmpeg options with noise reduction and quality optimization
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin -loglevel panic -hide_banner',
        'options': '-vn -filter:a "volume=0.5,loudnorm=I=-16:TP=-1.5:LRA=11,highpass=f=85,lowpass=f=15000" -ar 48000 -ac 2 -threads 0'
    }

    # Create multiple YouTube DL instances for advanced fallback system
    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
    
    # Fallback #1: Mobile client priority
    ytdl_mobile_options = ytdl_format_options.copy()
    ytdl_mobile_options['extractor_args']['youtube']['player_client'] = ['android_music', 'android']
    ytdl_mobile_options['http_headers']['User-Agent'] = 'com.google.android.youtube/17.36.4 (Linux; U; Android 12; GB) gzip'
    ytdl_mobile = youtube_dl.YoutubeDL(ytdl_mobile_options)
    
    # Fallback #2: Web-only with different headers
    ytdl_web_options = ytdl_format_options.copy()
    ytdl_web_options['extractor_args']['youtube']['player_client'] = ['web_music', 'web']
    ytdl_web_options['http_headers']['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    ytdl_web = youtube_dl.YoutubeDL(ytdl_web_options)
    
    # Fallback #3: Minimal options (last resort)
    ytdl_minimal_options = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'extractflat': False,
        'default_search': 'ytsearch',
        'extractor_args': {'youtube': {'player_client': ['web']}},
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    }
    ytdl_minimal = youtube_dl.YoutubeDL(ytdl_minimal_options)

    class YTDLSource(discord.PCMVolumeTransformer):
        def __init__(self, source, *, data, volume=0.5):
            super().__init__(source, volume)
            self.data = data
            self.title = data.get('title')
            self.url = data.get('url')
            self.duration = data.get('duration')
            self.requester = data.get('requester')
            self.webpage_url = data.get('webpage_url')
            self.thumbnail = data.get('thumbnail')

        @classmethod
        async def from_url(cls, url, *, loop=None, stream=False, requester=None):
            loop = loop or asyncio.get_event_loop()
            
            # Advanced fallback system with multiple extraction methods
            extraction_methods = [
                ("Main extractor (web + mobile)", ytdl),
                ("Mobile-first extractor", ytdl_mobile),
                ("Web-only extractor", ytdl_web),
                ("Minimal extractor (fallback)", ytdl_minimal)
            ]
            
            data = None
            last_error = None
            
            for attempt, (method_name, ytdl_instance) in enumerate(extraction_methods, 1):
                try:
                    print(f"🎵 Trying {method_name} (method {attempt}/{len(extraction_methods)})...")
                    
                    # Add random delay to avoid rate limiting
                    if attempt > 1:
                        delay = random.uniform(1, 3)
                        await asyncio.sleep(delay)
                    
                    # Update user agent for each attempt
                    if hasattr(ytdl_instance, 'params') and 'http_headers' in ytdl_instance.params:
                        ytdl_instance.params['http_headers']['User-Agent'] = get_user_agent()
                    
                    data = await loop.run_in_executor(None, lambda: ytdl_instance.extract_info(url, download=not stream))
                    
                    if data:
                        print(f"✅ Successfully extracted using {method_name}")
                        break
                        
                except Exception as e:
                    last_error = e
                    error_msg = str(e)
                    print(f"⚠️  {method_name} failed: {error_msg[:100]}...")
                    
                    # Check for specific YouTube errors and provide helpful messages
                    if "Sign in to confirm your age" in error_msg:
                        print("🔞 Age-restricted content detected, trying alternative method...")
                    elif "Video unavailable" in error_msg:
                        print("📵 Video unavailable, trying alternative method...")
                    elif "Private video" in error_msg:
                        print("� Private video detected, trying alternative method...")
                    elif "region" in error_msg.lower():
                        print("🌍 Region-blocked content, trying geo-bypass...")
                    elif "rate limit" in error_msg.lower():
                        print("⏱️  Rate limited, adding extra delay...")
                        await asyncio.sleep(5)
                    
                    continue
            
            if not data:
                # Provide user-friendly error message
                error_context = "Unknown error"
                if last_error:
                    error_str = str(last_error).lower()
                    if "sign in" in error_str or "age" in error_str:
                        error_context = "Age-restricted or sign-in required content"
                    elif "unavailable" in error_str:
                        error_context = "Video unavailable or private"
                    elif "region" in error_str:
                        error_context = "Region-blocked content"
                    elif "rate limit" in error_str:
                        error_context = "Rate limited by YouTube"
                    else:
                        error_context = f"Extraction failed: {str(last_error)[:100]}"
                
                raise Exception(f"❌ Unable to play this content. Reason: {error_context}")
            
            if 'entries' in data:
                # Take first result if it's a search
                data = data['entries'][0]

            data['requester'] = requester
            filename = data['url'] if stream else ytdl.prepare_filename(data)
            
            # Try enhanced FFmpeg options first, fallback to basic if needed
            try:
                return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
            except Exception as ffmpeg_error:
                print(f"⚠️  Enhanced FFmpeg failed, using basic options: {ffmpeg_error}")
                basic_ffmpeg = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
                    'options': '-vn'
                }
                return cls(discord.FFmpegPCMAudio(filename, **basic_ffmpeg), data=data)

# Welcome messages templates
WELCOME_MESSAGES = [
    "🎉 Welcome to the server, {member}! We're excited to have you here!",
    "🌟 Hey {member}! Welcome aboard! Hope you enjoy your stay!",
    "🎊 Look who just joined! Welcome {member}! Let's make some memories!",
    "🚀 {member} has landed! Welcome to our amazing community!",
    "💎 A new gem has joined us! Welcome {member}!",
    "🎭 {member} has entered the stage! Welcome to the show!",
    "🏰 {member} has entered the kingdom! Welcome, noble one!",
    "🌈 {member} just added more color to our server! Welcome!",
    "⚡ {member} has charged into our server! Welcome!",
    "🎪 Step right up, {member}! Welcome to the greatest server on Earth!"
]

# Welcome image generation
async def create_welcome_image(member):
    """Create a welcome image with member's avatar and background"""
    try:
        # Create a 800x400 background image
        width, height = 800, 400
        background = Image.new('RGB', (width, height), color=(47, 49, 54))  # Discord dark theme color
        
        # Create drawing context
        draw = ImageDraw.Draw(background)
        
        # Try to get member's avatar
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        
        try:
            # Download avatar
            response = requests.get(avatar_url, timeout=10)
            avatar_image = Image.open(io.BytesIO(response.content))
            
            # Resize and make circular
            avatar_size = 150
            avatar_image = avatar_image.resize((avatar_size, avatar_size))
            
            # Create circular mask
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            # Apply mask to avatar
            avatar_image.putalpha(mask)
            
            # Paste avatar on background
            avatar_x = (width - avatar_size) // 2
            avatar_y = 50
            background.paste(avatar_image, (avatar_x, avatar_y), avatar_image)
            
        except Exception as e:
            print(f"Error loading avatar: {e}")
            # Draw a default circle if avatar fails
            avatar_x = (width - 150) // 2
            avatar_y = 50
            draw.ellipse([avatar_x, avatar_y, avatar_x + 150, avatar_y + 150], fill=(114, 137, 218))
        
        # Add welcome text
        try:
            # Try to use a nice font, fallback to default
            font_large = ImageFont.truetype("arial.ttf", 48)
            font_medium = ImageFont.truetype("arial.ttf", 32)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except:
            # Use default font if custom font not available
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Welcome text
        welcome_text = "Welcome!"
        text_bbox = draw.textbbox((0, 0), welcome_text, font=font_large)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (width - text_width) // 2
        draw.text((text_x, 220), welcome_text, fill=(255, 255, 255), font=font_large)
        
        # Member name
        member_name = member.display_name
        if len(member_name) > 20:
            member_name = member_name[:17] + "..."
        
        name_bbox = draw.textbbox((0, 0), member_name, font=font_medium)
        name_width = name_bbox[2] - name_bbox[0]
        name_x = (width - name_width) // 2
        draw.text((name_x, 280), member_name, fill=(114, 137, 218), font=font_medium)
        
        # Server info
        server_text = f"You're member #{len(member.guild.members)}"
        server_bbox = draw.textbbox((0, 0), server_text, font=font_small)
        server_width = server_bbox[2] - server_bbox[0]
        server_x = (width - server_width) // 2
        draw.text((server_x, 330), server_text, fill=(153, 170, 181), font=font_small)
        
        # Save to bytes
        img_bytes = io.BytesIO()
        background.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return discord.File(img_bytes, filename='welcome.png')
        
    except Exception as e:
        print(f"Error creating welcome image: {e}")
        return None

# =============================================================================
# MUSIC FUNCTIONALITY
# =============================================================================
# 
# This section provides full music bot functionality including:
# - YouTube music streaming with yt-dlp
# - Queue management with skip, stop, shuffle
# - Volume control and playback management
# - Automatic voice channel joining
# - Both slash commands (/dotgen_) and legacy prefix commands
#
# Requirements:
# - yt-dlp: pip install yt-dlp
# - PyNaCl: pip install PyNaCl (for voice support)
# - FFmpeg: Download from https://ffmpeg.org/download.html
#
# Music Commands Available:
# Slash: /dotgen_play, /dotgen_skip, /dotgen_stop, /dotgen_queue, /dotgen_volume, /dotgen_disconnect
# Prefix: !play, !skip, !stop, !queue, !volume, !disconnect
# =============================================================================

if YOUTUBE_DL_AVAILABLE:
    class MusicQueue:
        """Advanced music queue for a guild with enhanced features"""
        def __init__(self):
            self.queue = []
            self.current = None
            self.loop = False
            self.loop_queue = False  # Loop entire queue
            self.volume = 0.5
            self.shuffle_enabled = False
            self.history = []  # Track played songs
            self.max_history = 50
            self.auto_play = False  # Auto-play related songs

        def add_song(self, song):
            """Add a song to the queue"""
            self.queue.append(song)
            if self.shuffle_enabled:
                self.shuffle()

        def get_next(self):
            """Get the next song to play"""
            if self.loop and self.current:
                return self.current
            
            if self.queue:
                if self.current:
                    self.add_to_history(self.current)
                
                if self.shuffle_enabled:
                    # Get random song from queue
                    import random
                    index = random.randint(0, len(self.queue) - 1)
                    self.current = self.queue.pop(index)
                else:
                    self.current = self.queue.pop(0)
                    
                return self.current
            elif self.loop_queue and self.history:
                # Loop the entire queue by restoring from history
                self.queue = self.history.copy()
                self.history.clear()
                if self.queue:
                    self.current = self.queue.pop(0)
                    return self.current
            
            self.current = None
            return None

        def skip(self):
            """Skip current song and get next"""
            if self.current:
                self.add_to_history(self.current)
            
            if self.queue:
                if self.shuffle_enabled:
                    import random
                    index = random.randint(0, len(self.queue) - 1)
                    self.current = self.queue.pop(index)
                else:
                    self.current = self.queue.pop(0)
                return self.current
            
            self.current = None
            return None

        def previous(self):
            """Play previous song from history"""
            if self.history:
                if self.current:
                    self.queue.insert(0, self.current)  # Put current back in queue
                self.current = self.history.pop()
                return self.current
            return None

        def clear(self):
            """Clear the queue and current song"""
            self.queue.clear()
            self.current = None

        def shuffle(self):
            """Shuffle the current queue"""
            import random
            random.shuffle(self.queue)
            self.shuffle_enabled = True

        def remove_song(self, index):
            """Remove a song from queue by index"""
            if 0 <= index < len(self.queue):
                return self.queue.pop(index)
            return None

        def move_song(self, from_index, to_index):
            """Move a song in the queue"""
            if 0 <= from_index < len(self.queue) and 0 <= to_index < len(self.queue):
                song = self.queue.pop(from_index)
                self.queue.insert(to_index, song)
                return True
            return False

        def add_to_history(self, song):
            """Add song to history"""
            self.history.append(song)
            if len(self.history) > self.max_history:
                self.history.pop(0)

        def get_queue_info(self):
            """Get formatted queue information"""
            total_duration = 0
            for song in self.queue:
                if song.duration:
                    total_duration += song.duration
            
            return {
                'queue_length': len(self.queue),
                'total_duration': total_duration,
                'current_song': self.current.title if self.current else None,
                'loop': self.loop,
                'loop_queue': self.loop_queue,
                'shuffle': self.shuffle_enabled,
                'volume': int(self.volume * 100)
            }

    async def join_voice_channel(ctx):
        """Join the voice channel the user is in"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel to use music commands!")
            return None

        channel = ctx.author.voice.channel
        
        # Check if bot is already connected to voice
        if ctx.guild.voice_client:
            if ctx.guild.voice_client.channel == channel:
                return ctx.guild.voice_client
            else:
                await ctx.guild.voice_client.move_to(channel)
                return ctx.guild.voice_client
        
        # Connect to voice channel
        try:
            voice_client = await channel.connect()
            voice_clients[ctx.guild.id] = voice_client
            return voice_client
        except Exception as e:
            await ctx.send(f"❌ Failed to connect to voice channel: {e}")
            return None

    async def play_next_song(guild_id, voice_client):
        """Play the next song in the queue"""
        if guild_id not in music_queues:
            return

        queue = music_queues[guild_id]
        next_song = queue.get_next()

        if next_song:
            try:
                voice_client.play(next_song, after=lambda e: asyncio.run_coroutine_threadsafe(
                    play_next_song(guild_id, voice_client), bot.loop
                ))
                voice_client.source.volume = queue.volume
            except Exception as e:
                print(f"Error playing song: {e}")
        else:
            # Queue is empty, disconnect after 5 minutes of inactivity
            await asyncio.sleep(300)
            if not voice_client.is_playing():
                await voice_client.disconnect()
                if guild_id in voice_clients:
                    del voice_clients[guild_id]

    async def search_youtube(query):
        """Search YouTube for a song"""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{query}", download=False))
            
            if 'entries' in data and data['entries']:
                return data['entries'][0]
            return None
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None

# =============================================================================
# END MUSIC FUNCTIONALITY
# =============================================================================

@bot.event
async def on_ready():
    print(f'✅ {bot.user} has connected to Discord!')
    print(f'📊 Bot is in {len(bot.guilds)} guild(s)')
    print(f'🎛️  Using prefix: {BOT_PREFIX}')
    
    # Check if privileged intents are working
    if privileged_intents_available:
        print("✅ Running with privileged intents - all features available")
        print("   - Automatic welcome messages: ✅ Enabled")
        print("   - Voice channels: ✅ Enabled")    
    else:        
        print("⚠️  Running in LIMITED MODE (no privileged intents)")
        print("   - Welcome messages: Use !welcome command instead of automatic detection")
        print("   - Voice channels: Working normally")
    
    # Validate configuration
    if WELCOME_CHANNEL_ID:
        channel = bot.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            print(f'✅ Welcome channel configured: #{channel.name}')
        else:
            print(f'⚠️  Welcome channel ID {WELCOME_CHANNEL_ID} not found')
    
    if LOBBY_VOICE_CHANNEL_ID:
        channel = bot.get_channel(LOBBY_VOICE_CHANNEL_ID)
        if channel:
            print(f'✅ Lobby voice channel configured: {channel.name}')
        else:
            print(f'⚠️  Lobby voice channel ID {LOBBY_VOICE_CHANNEL_ID} not found')
    
    if VOICE_CATEGORY_ID:
        category = bot.get_channel(VOICE_CATEGORY_ID)
        if category:
            print(f'✅ Voice category configured: {category.name}')
        else:
            print(f'⚠️  Voice category ID {VOICE_CATEGORY_ID} not found')    
    if VOICE_LOG_CHANNEL_ID:
        channel = bot.get_channel(VOICE_LOG_CHANNEL_ID)
        if channel:
            print(f'✅ Voice log channel configured: #{channel.name}')
        else:
            print(f'⚠️  Voice log channel ID {VOICE_LOG_CHANNEL_ID} not found')
    
    if ALLOWED_ROLES:
        print(f'✅ Allowed roles configured: {len(ALLOWED_ROLES)} role(s)')
    else:
        print('⚠️  No allowed roles configured - all users can create voice channels')
    
    # Set rotating bot status
    try:
        await start_rotating_status()
        print("✅ Rotating bot status started successfully")
    except Exception as e:
        print(f"⚠️  Could not start rotating status: {e}")
    
    # Sync slash commands
    try:
        if GUILD_ID:
            # Sync to specific guild for faster updates during development
            guild = discord.Object(id=GUILD_ID)
            synced = await bot.tree.sync(guild=guild)
            print(f"✅ Synced {len(synced)} slash command(s) to guild {GUILD_ID}")
        else:
            # Sync globally (takes up to 1 hour to propagate)
            synced = await bot.tree.sync()
            print(f"✅ Synced {len(synced)} slash command(s) globally")
    except Exception as e:
        print(f"⚠️  Failed to sync slash commands: {e}")
    
    print("🚀 Bot is ready to use!")
    print(f"💡 Use {BOT_PREFIX}config to check your configuration")
    if not privileged_intents_available:
        print(f"💡 Use {BOT_PREFIX}welcome @member to send welcome messages manually")

# Manual welcome command (fallback for when privileged intents aren't available)
@bot.command(name="welcome")
async def manual_welcome(ctx, member: discord.Member = None):
    """Send a welcome message for a member"""
    if not member:
        member = ctx.author
    
    try:
        # Get the welcome channel from environment variable first
        welcome_channel = None
        
        if WELCOME_CHANNEL_ID:
            welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
        
        # Fallback to current channel if no specific channel ID is set
        if not welcome_channel:
            welcome_channel = ctx.channel
        
        if welcome_channel:
            # Select a random welcome message
            welcome_msg = random.choice(WELCOME_MESSAGES).format(member=member.mention)
            
            # Create a welcome embed
            embed = discord.Embed(
                title="🎉 Welcome Message!",
                description=welcome_msg,
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.add_field(
                name="Account Created", 
                value=discord.utils.format_dt(member.created_at, style='R'), 
                inline=True
            )
            embed.set_footer(text=f"Welcome to {ctx.guild.name}!")
            
            await welcome_channel.send(embed=embed)
            
            if welcome_channel != ctx.channel:
                await ctx.send(f"✅ Welcome message sent to {welcome_channel.mention} for {member.mention}")
            else:
                await ctx.send("✅ Welcome message sent!")
            
    except Exception as e:
        await ctx.send(f"❌ Error sending welcome message: {e}")

@bot.event
async def on_member_join(member):
    """Send a unique welcome message when a new member joins (only works with privileged intents)"""
    if not privileged_intents_available:
        return  # Skip if privileged intents aren't available
        
    try:
        # Auto-assign role if configured
        if AUTO_ROLE_ID:
            role = member.guild.get_role(AUTO_ROLE_ID)
            if role:
                try:
                    await member.add_roles(role)
                    print(f"✅ Auto-assigned role @{role.name} to {member.display_name}")
                except Exception as e:
                    print(f"❌ Failed to assign auto-role to {member.display_name}: {e}")
        
        # Get the welcome channel from environment variable first
        welcome_channel = None
        
        if WELCOME_CHANNEL_ID:
            welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
        
        # Fallback to automatic detection if no specific channel ID is set
        if not welcome_channel:
            # Try to find the system channel first
            if member.guild.system_channel:
                welcome_channel = member.guild.system_channel
            else:
                # Look for common welcome channel names
                for channel in member.guild.text_channels:
                    if channel.name.lower() in ['welcome', 'general', 'lobby', 'entrance']:
                        welcome_channel = channel
                        break
                if not welcome_channel and member.guild.text_channels:
                    welcome_channel = member.guild.text_channels[0]
        
        if welcome_channel:
            # Create welcome image
            welcome_image = await create_welcome_image(member)
            
            # Select a random welcome message
            welcome_msg = random.choice(WELCOME_MESSAGES).format(member=member.mention)
            
            # Create a welcome embed
            embed = discord.Embed(
                title="🎉 New Member Alert!",
                description=welcome_msg,
                color=discord.Color.gold()
            )
            
            if welcome_image:
                embed.set_image(url="attachment://welcome.png")
            else:
                embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            
            embed.add_field(
                name="Member Count", 
                value=f"You're member #{len(member.guild.members)}!", 
                inline=True
            )
            embed.add_field(
                name="Account Created", 
                value=discord.utils.format_dt(member.created_at, style='R'), 
                inline=True
            )
            embed.set_footer(text=f"Welcome to {member.guild.name}!")
            
            # Send welcome message with or without image
            if welcome_image:
                await welcome_channel.send(file=welcome_image, embed=embed)
            else:
                await welcome_channel.send(embed=embed)
        
        # Call extended member join logging
        await on_member_join_extended(member)
            
    except Exception as e:
        print(f"Error sending welcome message: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice channel join/leave events for dynamic role-based channels"""
    try:
        # Check if member joined the configured lobby voice channel
        if after.channel and LOBBY_VOICE_CHANNEL_ID and after.channel.id == LOBBY_VOICE_CHANNEL_ID:
            await handle_voice_channel_creation(member, after.channel)
        # Fallback: Check by channel name if ID not configured
        elif after.channel and not LOBBY_VOICE_CHANNEL_ID and after.channel.name.lower() == "join to create":
            await handle_voice_channel_creation(member, after.channel)
        
        # Check if member left a temporary voice channel
        if before.channel and before.channel.id in temp_voice_channels:
            await handle_voice_channel_cleanup(before.channel)
        
        # Call extended voice logging
        await on_voice_state_update_extended(member, before, after)
            
    except Exception as e:
        print(f"Error in voice state update: {e}")

async def handle_voice_channel_creation(member, lobby_channel):
    """Create a new voice channel based on the member's specific role"""
    try:
        guild = member.guild
        
        # Check if SPECIFIC_VC_ROLE_IDS is configured - only these roles can create VCs
        if SPECIFIC_VC_ROLE_IDS:
            # Find which specific role the member has (if any)
            member_specific_roles = []
            for role_id in SPECIFIC_VC_ROLE_IDS:
                role = guild.get_role(role_id)
                if role and role in member.roles:
                    member_specific_roles.append(role)
            
            # Check if member has any of the specific roles
            if not member_specific_roles:
                # Get role names for error message
                specific_role_names = []
                for role_id in SPECIFIC_VC_ROLE_IDS:
                    role = guild.get_role(role_id)
                    if role:
                        specific_role_names.append(f"@{role.name}")
                
                # Send notification that user doesn't have permission
                try:
                    roles_text = ", ".join(specific_role_names)
                    await member.send(f"❌ Only members with these roles can create voice channels: {roles_text}")
                except:
                    pass  # Can't send DM
                
                # Log the attempt
                log_channel = bot.get_channel(VOICE_LOG_CHANNEL_ID) if VOICE_LOG_CHANNEL_ID else None
                if log_channel:
                    embed = discord.Embed(
                        title="🚫 Voice Channel Creation Denied",
                        description=f"{member.mention} tried to create a voice channel but doesn't have any required roles.",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="User", value=f"{member.mention} ({member.display_name})", inline=True)
                    embed.add_field(name="Required Roles", value=", ".join(specific_role_names), inline=True)
                    await log_channel.send(embed=embed, delete_after=60)
                
                return  # Don't create the channel
            
            # Use the highest priority role (first one found)
            target_role = member_specific_roles[0]
            
            # Check if there's already a VC for this specific role
            role_name = target_role.name
            if target_role.id in role_voice_channels:
                existing_channel = role_voice_channels[target_role.id]
                # Check if the channel still exists
                if existing_channel and existing_channel.id in temp_voice_channels:
                    try:
                        # Move member to existing channel
                        await member.move_to(existing_channel)
                        
                        # Notify in log channel
                        log_channel = bot.get_channel(VOICE_LOG_CHANNEL_ID) if VOICE_LOG_CHANNEL_ID else None
                        if log_channel:
                            embed = discord.Embed(
                                title="🎤 Joined Existing Voice Channel",
                                description=f"{member.mention} joined the existing @{role_name} voice channel",
                                color=target_role.color
                            )
                            await log_channel.send(embed=embed, delete_after=120)
                        
                        return
                    except Exception as e:
                        print(f"Error moving member to existing channel: {e}")
                        # Remove invalid channel from tracking
                        del role_voice_channels[target_role.id]
        
        # Fallback to old system if SPECIFIC_VC_ROLE_ID is not configured
        elif ALLOWED_ROLES:
            member_role_ids = [role.id for role in member.roles]
            has_allowed_role = any(role_id in member_role_ids for role_id in ALLOWED_ROLES)
            
            if not has_allowed_role:
                # Send notification that user doesn't have permission
                try:
                    await member.send("❌ You don't have permission to create voice channels. Contact an administrator if you need access.")
                except:
                    pass  # Can't send DM
                
                # Log the attempt
                log_channel = bot.get_channel(VOICE_LOG_CHANNEL_ID) if VOICE_LOG_CHANNEL_ID else None
                if log_channel:
                    embed = discord.Embed(
                        title="🚫 Voice Channel Creation Denied",
                        description=f"{member.mention} tried to create a voice channel but doesn't have required roles.",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="User", value=f"{member.mention} ({member.display_name})", inline=True)
                    embed.add_field(name="User Roles", value=", ".join([role.name for role in member.roles if role.name != "@everyone"]) or "None", inline=False)
                    await log_channel.send(embed=embed, delete_after=60)
                
                return  # Don't create the channel
        
        # Determine which role to use for the channel
        if SPECIFIC_VC_ROLE_IDS:
            # Use the specific role for channel creation (already found above)
            role_name = target_role.name if target_role else "Member"
            highest_role = target_role
        else:
            # Get the member's highest role (excluding @everyone) - old system
            highest_role = None
            for role in reversed(member.roles):
                if role.name != "@everyone":
                    highest_role = role
                    break
            
            # Use default role if configured and no specific role found
            if not highest_role and DEFAULT_ROLE_ID:
                highest_role = guild.get_role(DEFAULT_ROLE_ID)
            
            role_name = highest_role.name if highest_role else "Member"
        
        # Create a unique channel name
        channel_name = f"{role_name}'s VC"
        
        # Get the category from environment variable or use lobby channel's category
        category = None
        if VOICE_CATEGORY_ID:
            category = bot.get_channel(VOICE_CATEGORY_ID)
        if not category:
            category = lobby_channel.category
        
        # Create the new voice channel
        new_channel = await guild.create_voice_channel(
            name=channel_name,
            category=category,
            user_limit=MAX_VOICE_LIMIT
        )
        
        # Set permissions based on the role
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=True, connect=True),
            member: discord.PermissionOverwrite(
                view_channel=True, 
                connect=True, 
                manage_channels=True,
                move_members=True,
                mute_members=True,
                deafen_members=True
            )
        }
        
        # If the member has a specific role, give that role special permissions
        if highest_role:
            overwrites[highest_role] = discord.PermissionOverwrite(
                view_channel=True,
                connect=True,
                speak=True
            )
        
        await new_channel.edit(overwrites=overwrites)
        
        # Move the member to the new channel
        await member.move_to(new_channel)
        
        # Store the channel for cleanup and role tracking
        temp_voice_channels[new_channel.id] = {
            'channel': new_channel,
            'creator': member.id,
            'role': role_name,
            'created_at': discord.utils.utcnow()
        }
        
        # Track channel by role if using specific role system
        if SPECIFIC_VC_ROLE_IDS and highest_role:
            role_voice_channels[highest_role.id] = new_channel
        
        # Send a notification to voice log channel (separate from welcome channel)
        log_channel = None
        if VOICE_LOG_CHANNEL_ID:
            log_channel = bot.get_channel(VOICE_LOG_CHANNEL_ID)
        
        # Fallback to finding a log/admin channel if no specific log channel
        if not log_channel:
            for channel in guild.text_channels:
                if channel.name.lower() in ['logs', 'admin-logs', 'voice-logs', 'bot-logs']:
                    log_channel = channel
                    break
        
        # Final fallback to welcome channel
        if not log_channel and WELCOME_CHANNEL_ID:
            log_channel = bot.get_channel(WELCOME_CHANNEL_ID)
            
        if log_channel:
            embed = discord.Embed(
                title="🎤 Voice Channel Created!",
                description=f"{member.mention} created a new voice channel",
                color=highest_role.color if highest_role else discord.Color.blue()
            )
            embed.add_field(name="Channel Name", value=f"**{channel_name}**", inline=False)
            embed.add_field(name="Creator", value=f"{member.mention} ({member.display_name})", inline=True)
            embed.add_field(name="Role", value=f"@{role_name}", inline=True)
            embed.add_field(name="Category", value=category.name if category else "None", inline=True)
            embed.add_field(name="User Limit", value=str(MAX_VOICE_LIMIT), inline=True)
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.set_footer(text=f"Channel ID: {new_channel.id}")
            await log_channel.send(embed=embed, delete_after=300)  # Delete after 5 minutes
            
    except Exception as e:
        print(f"Error creating voice channel: {e}")
        # Log error to voice log channel if available
        log_channel = bot.get_channel(VOICE_LOG_CHANNEL_ID) if VOICE_LOG_CHANNEL_ID else None
        if log_channel:
            embed = discord.Embed(
                title="❌ Voice Channel Creation Error",
                description=f"Failed to create voice channel for {member.mention}",
                color=discord.Color.red()
            )
            embed.add_field(name="Error", value=str(e), inline=False)
            await log_channel.send(embed=embed, delete_after=120)

async def handle_voice_channel_cleanup(channel):
    """Clean up empty temporary voice channels"""
    try:
        # Check if the channel is empty
        if len(channel.members) == 0:
            channel_info = temp_voice_channels.get(channel.id)
            if channel_info:
                # Calculate how long the channel existed
                created_at = channel_info.get('created_at')
                duration = ""
                if created_at:
                    duration_seconds = (discord.utils.utcnow() - created_at).total_seconds()
                    hours = int(duration_seconds // 3600)
                    minutes = int((duration_seconds % 3600) // 60)
                    duration = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                
                # Log the deletion to voice log channel
                log_channel = bot.get_channel(VOICE_LOG_CHANNEL_ID) if VOICE_LOG_CHANNEL_ID else None
                if log_channel:
                    embed = discord.Embed(
                        title="🗑️ Voice Channel Deleted",
                        description=f"Temporary voice channel was automatically deleted",
                        color=discord.Color.orange()
                    )
                    embed.add_field(name="Channel Name", value=f"**{channel.name}**", inline=False)
                    embed.add_field(name="Creator Role", value=f"@{channel_info.get('role', 'Unknown')}", inline=True)
                    if duration:
                        embed.add_field(name="Duration", value=duration, inline=True)
                    embed.add_field(name="Reason", value="Channel became empty", inline=True)
                    embed.set_footer(text=f"Channel ID: {channel.id}")
                    await log_channel.send(embed=embed, delete_after=180)  # Delete after 3 minutes
                
                await channel.delete()
                del temp_voice_channels[channel.id]
                print(f"Deleted empty voice channel: {channel.name} (existed for {duration})")
                
    except Exception as e:
        print(f"Error cleaning up voice channel: {e}")
        # Remove from tracking even if deletion failed
        if channel.id in temp_voice_channels:
            del temp_voice_channels[channel.id]

# =============================================================================
# COMPREHENSIVE LOGGING SYSTEM
# =============================================================================

@bot.event
async def on_member_update(before, after):
    """Log role changes and other member updates"""
    if not ROLE_LOG_CHANNEL_ID:
        return
        
    try:
        # Check for role changes
        roles_added = [role for role in after.roles if role not in before.roles]
        roles_removed = [role for role in before.roles if role not in after.roles]
        
        if roles_added or roles_removed:
            log_channel = bot.get_channel(ROLE_LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(
                    title="🎭 Role Changes",
                    color=discord.Color.orange()
                )
                
                embed.add_field(
                    name="👤 Member",
                    value=f"{after.mention} ({after.display_name})",
                    inline=False
                )
                
                if roles_added:
                    embed.add_field(
                        name="➕ Roles Added",
                        value=", ".join([f"@{role.name}" for role in roles_added]),
                        inline=False
                    )
                
                if roles_removed:
                    embed.add_field(
                        name="➖ Roles Removed", 
                        value=", ".join([f"@{role.name}" for role in roles_removed]),
                        inline=False
                    )
                
                embed.set_thumbnail(url=after.avatar.url if after.avatar else after.default_avatar.url)
                embed.timestamp = discord.utils.utcnow()
                embed.set_footer(text=f"User ID: {after.id}")
                
                await log_channel.send(embed=embed)
                
        # Check for nickname changes
        if before.display_name != after.display_name:
            log_channel = bot.get_channel(MODERATION_LOG_CHANNEL_ID) if MODERATION_LOG_CHANNEL_ID else bot.get_channel(ROLE_LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(
                    title="📝 Nickname Changed",
                    color=discord.Color.blue()
                )
                embed.add_field(name="👤 Member", value=after.mention, inline=True)
                embed.add_field(name="📛 Old Nickname", value=before.display_name or "None", inline=True)
                embed.add_field(name="🆕 New Nickname", value=after.display_name or "None", inline=True)
                embed.timestamp = discord.utils.utcnow()
                embed.set_footer(text=f"User ID: {after.id}")
                
                await log_channel.send(embed=embed)
                
    except Exception as e:
        print(f"Error logging member update: {e}")

@bot.event
async def on_member_remove(member):
    """Log member leaving the server"""
    if not MEMBER_LOG_CHANNEL_ID:
        return
        
    try:
        log_channel = bot.get_channel(MEMBER_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="👋 Member Left",
                description=f"{member.mention} has left the server",
                color=discord.Color.red()
            )
            
            embed.add_field(
                name="👤 User Info",
                value=f"**Name:** {member.display_name}\n**Tag:** {member}\n**ID:** {member.id}",
                inline=True
            )
            
            embed.add_field(
                name="📅 Joined Server",
                value=discord.utils.format_dt(member.joined_at, style='R') if member.joined_at else "Unknown",
                inline=True
            )
            
            embed.add_field(
                name="📊 Account Age",
                value=discord.utils.format_dt(member.created_at, style='R'),
                inline=True
            )
            
            # Show roles they had
            user_roles = [role.name for role in member.roles if role.name != "@everyone"]
            if user_roles:
                embed.add_field(
                    name="🎭 Roles",
                    value=", ".join(user_roles[:10]) + ("..." if len(user_roles) > 10 else ""),
                    inline=False
                )
            
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"Total members: {len(member.guild.members)}")
            
            await log_channel.send(embed=embed)
            
    except Exception as e:
        print(f"Error logging member leave: {e}")

@bot.event
async def on_message_edit(before, after):
    """Log message edits"""
    if not MESSAGE_LOG_CHANNEL_ID or before.author.bot:
        return
        
    # Skip if content is the same (embed updates, etc.)
    if before.content == after.content:
        return
        
    try:
        log_channel = bot.get_channel(MESSAGE_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="✏️ Message Edited",
                color=discord.Color.orange()
            )
            
            embed.add_field(
                name="👤 Author",
                value=f"{after.author.mention} ({after.author.display_name})",
                inline=True
            )
            
            embed.add_field(
                name="📍 Channel",
                value=f"{after.channel.mention}",
                inline=True
            )
            
            embed.add_field(
                name="🔗 Jump to Message",
                value=f"[Click here]({after.jump_url})",
                inline=True
            )
            
            # Truncate content if too long
            old_content = before.content[:500] + "..." if len(before.content) > 500 else before.content
            new_content = after.content[:500] + "..." if len(after.content) > 500 else after.content
            
            embed.add_field(
                name="📝 Before",
                value=old_content or "*No content*",
                inline=False
            )
            
            embed.add_field(
                name="🆕 After",
                value=new_content or "*No content*",
                inline=False
            )
            
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"Message ID: {after.id} | User ID: {after.author.id}")
            
            await log_channel.send(embed=embed)
            
    except Exception as e:
        print(f"Error logging message edit: {e}")

@bot.event
async def on_message_delete(message):
    """Log message deletions"""
    if not MESSAGE_LOG_CHANNEL_ID or message.author.bot:
        return
        
    try:
        log_channel = bot.get_channel(MESSAGE_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="🗑️ Message Deleted",
                color=discord.Color.red()
            )
            
            embed.add_field(
                name="👤 Author",
                value=f"{message.author.mention} ({message.author.display_name})",
                inline=True
            )
            
            embed.add_field(
                name="📍 Channel",
                value=f"{message.channel.mention}",
                inline=True
            )
            
            embed.add_field(
                name="📅 Sent",
                value=discord.utils.format_dt(message.created_at, style='R'),
                inline=True
            )
            
            # Truncate content if too long
            content = message.content[:1000] + "..." if len(message.content) > 1000 else message.content
            
            embed.add_field(
                name="📝 Content",
                value=content or "*No text content*",
                inline=False
            )
            
            # Show attachments if any
            if message.attachments:
                attachment_info = []
                for att in message.attachments[:3]:  # Limit to 3 attachments
                    attachment_info.append(f"📎 {att.filename} ({att.size} bytes)")
                
                embed.add_field(
                    name="📎 Attachments",
                    value="\n".join(attachment_info),
                    inline=False
                )
            
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"Message ID: {message.id} | User ID: {message.author.id}")
            
            await log_channel.send(embed=embed)
            
    except Exception as e:
        print(f"Error logging message deletion: {e}")

@bot.event
async def on_voice_state_update_extended(member, before, after):
    """Extended voice state logging (separate from channel creation logic)"""
    if not VOICE_LOG_CHANNEL_ID:
        return
        
    try:
        log_channel = bot.get_channel(VOICE_LOG_CHANNEL_ID)
        if not log_channel:
            return
            
        # Member joined a voice channel
        if not before.channel and after.channel:
            embed = discord.Embed(
                title="🎤 Voice Channel Joined",
                color=discord.Color.green()
            )
            embed.add_field(name="👤 Member", value=f"{member.mention} ({member.display_name})", inline=True)
            embed.add_field(name="📍 Channel", value=after.channel.name, inline=True)
            embed.add_field(name="👥 Members in Channel", value=len(after.channel.members), inline=True)
            
        # Member left a voice channel
        elif before.channel and not after.channel:
            embed = discord.Embed(
                title="🚪 Voice Channel Left",
                color=discord.Color.red()
            )
            embed.add_field(name="👤 Member", value=f"{member.mention} ({member.display_name})", inline=True)
            embed.add_field(name="📍 Channel", value=before.channel.name, inline=True)
            embed.add_field(name="👥 Members Remaining", value=len(before.channel.members), inline=True)
            
        # Member moved between voice channels
        elif before.channel and after.channel and before.channel != after.channel:
            embed = discord.Embed(
                title="🔄 Voice Channel Moved",
                color=discord.Color.blue()
            )
            embed.add_field(name="👤 Member", value=f"{member.mention} ({member.display_name})", inline=False)
            embed.add_field(name="📤 From", value=before.channel.name, inline=True)
            embed.add_field(name="📥 To", value=after.channel.name, inline=True)
            
        # Mute/unmute, deafen/undeafen changes
        elif before.channel == after.channel and after.channel:
            changes = []
            if before.self_mute != after.self_mute:
                changes.append(f"Self-muted: {after.self_mute}")
            if before.self_deaf != after.self_deaf:
                changes.append(f"Self-deafened: {after.self_deaf}")
            if before.mute != after.mute:
                changes.append(f"Server-muted: {after.mute}")
            if before.deaf != after.deaf:
                changes.append(f"Server-deafened: {after.deaf}")
                
            if changes:
                embed = discord.Embed(
                    title="🔊 Voice State Changed",
                    color=discord.Color.orange()
                )
                embed.add_field(name="👤 Member", value=f"{member.mention} ({member.display_name})", inline=True)
                embed.add_field(name="📍 Channel", value=after.channel.name, inline=True)
                embed.add_field(name="🔄 Changes", value="\n".join(changes), inline=False)
        else:
            return  # No significant change to log
            
        embed.timestamp = discord.utils.utcnow()
        embed.set_footer(text=f"User ID: {member.id}")
        
        await log_channel.send(embed=embed, delete_after=300)  # Auto-delete after 5 minutes
        
    except Exception as e:
        print(f"Error logging extended voice state: {e}")

# Enhance the existing member join event to also log to member log channel
@bot.event  
async def on_member_join_extended(member):
    """Enhanced member join logging (in addition to welcome messages)"""
    if not MEMBER_LOG_CHANNEL_ID:
        return
        
    try:
        log_channel = bot.get_channel(MEMBER_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="🎉 New Member Joined",
                description=f"{member.mention} has joined the server!",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="👤 User Info",
                value=f"**Name:** {member.display_name}\n**Tag:** {member}\n**ID:** {member.id}",
                inline=True
            )
            
            embed.add_field(
                name="📅 Account Created",
                value=discord.utils.format_dt(member.created_at, style='R'),
                inline=True
            )
            
            embed.add_field(
                name="📊 Member Count",
                value=f"#{len(member.guild.members)}",
                inline=True
            )
            
            # Check account age for security
            account_age = discord.utils.utcnow() - member.created_at
            if account_age.days < 7:
                embed.add_field(
                    name="⚠️ Security Alert",
                    value=f"Account is only {account_age.days} days old",
                    inline=False
                )
            
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"Total members: {len(member.guild.members)}")
            
            await log_channel.send(embed=embed)
            
    except Exception as e:
        print(f"Error logging member join: {e}")

# =============================================================================
# END LOGGING SYSTEM
# =============================================================================

# Commands for managing the bot
@bot.command(name="setup_lobby")
@commands.has_permissions(administrator=True)
async def setup_lobby(ctx, *, category_name="Voice Channels"):
    """Setup the lobby voice channel for creating temporary channels"""
    try:
        guild = ctx.guild
        
        # Find or create the category
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(category_name)
        
        # Create the lobby channel
        lobby_channel = await guild.create_voice_channel(
            name="Join to Create",
            category=category,
            user_limit=1
        )
        
        embed = discord.Embed(
            title="✅ Lobby Setup Complete!",
            description=f"Created **{lobby_channel.name}** in **{category.name}** category.\n\nUsers can now join this channel to create their own role-based voice channels!\n\n**Channel ID:** `{lobby_channel.id}`\n**Category ID:** `{category.id}`\n\nAdd these IDs to your .env file for automatic detection.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error setting up lobby: {e}")

@bot.command(name="get_ids", aliases=["ids"])
@commands.has_permissions(administrator=True)
async def get_ids(ctx, channel: discord.TextChannel = None):
    """Get channel and server IDs for .env configuration"""
    try:
        guild = ctx.guild
        
        embed = discord.Embed(
            title="📋 Server & Channel IDs",
            description="Copy these IDs to your .env file for easy configuration:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🏠 Server ID",
            value=f"`{guild.id}`",
            inline=False
        )
        
        embed.add_field(
            name="📝 Current Channel ID",
            value=f"`{ctx.channel.id}`",
            inline=True
        )
        
        # If a channel is mentioned, show its ID
        if channel:
            embed.add_field(
                name="🔗 Mentioned Channel ID",
                value=f"`{channel.id}`",
                inline=True
            )
        
        # Show voice channels
        voice_channels = [vc for vc in guild.voice_channels if "join to create" in vc.name.lower()]
        if voice_channels:
            embed.add_field(
                name="🎤 Lobby Voice Channels",
                value="\n".join([f"**{vc.name}:** `{vc.id}`" for vc in voice_channels[:5]]),
                inline=False
            )
        
        # Show categories
        if guild.categories:
            categories_text = "\n".join([f"**{cat.name}:** `{cat.id}`" for cat in guild.categories[:5]])
            embed.add_field(
                name="📁 Categories",
                value=categories_text,
                inline=False
            )
        
        embed.set_footer(text="💡 Right-click on channels/categories in Discord and select 'Copy ID' to get their IDs")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error getting IDs: {e}")

@bot.command(name="setup_logging", aliases=["logging_setup"])
@commands.has_permissions(administrator=True)
async def setup_logging(ctx):
    """Setup logging channels for comprehensive server monitoring"""
    try:
        guild = ctx.guild
        
        embed = discord.Embed(
            title="📋 Logging Channels Setup",
            description="Configure logging channels for comprehensive server monitoring:",
            color=discord.Color.blue()
        )
        
        # Check current logging channel configurations
        logging_configs = [
            ("MEMBER_LOG_CHANNEL_ID", MEMBER_LOG_CHANNEL_ID, "👥 Member Join/Leave", "member-logs"),
            ("ROLE_LOG_CHANNEL_ID", ROLE_LOG_CHANNEL_ID, "🎭 Role Changes", "role-logs"), 
            ("MESSAGE_LOG_CHANNEL_ID", MESSAGE_LOG_CHANNEL_ID, "💬 Message Edit/Delete", "message-logs"),
            ("VOICE_LOG_CHANNEL_ID", VOICE_LOG_CHANNEL_ID, "🎤 Voice Activity", "voice-logs"),
            ("MODERATION_LOG_CHANNEL_ID", MODERATION_LOG_CHANNEL_ID, "🛡️ Moderation Actions", "mod-logs")
        ]
        
        configured_channels = []
        missing_channels = []
        
        for env_var, channel_id, description, suggested_name in logging_configs:
            if channel_id:
                channel = bot.get_channel(channel_id)
                if channel:
                    configured_channels.append(f"✅ {description}: {channel.mention}")
                else:
                    missing_channels.append(f"❌ {description}: Invalid ID ({channel_id})")
            else:
                missing_channels.append(f"⚪ {description}: Not configured")
                
        if configured_channels:
            embed.add_field(
                name="✅ Configured Logging Channels",
                value="\n".join(configured_channels),
                inline=False
            )
            
        if missing_channels:
            embed.add_field(
                name="⚠️ Missing/Invalid Logging Channels", 
                value="\n".join(missing_channels),
                inline=False
            )
            
        # Instructions for setup
        embed.add_field(
            name="🔧 Setup Instructions",
            value="1. Create text channels for each log type\n2. Use `/get_ids` to get their channel IDs\n3. Add the IDs to your `.env` file\n4. Restart the bot\n\n**Suggested channel names:**\n`#member-logs` `#role-logs` `#message-logs`\n`#voice-logs` `#mod-logs`",
            inline=False
        )
        
        embed.add_field(
            name="📝 What Gets Logged",
            value="**Member Logs:** Join/leave events, account age warnings\n**Role Logs:** Role additions/removals, nickname changes\n**Message Logs:** Message edits and deletions\n**Voice Logs:** VC join/leave/move, mute/deafen changes\n**Mod Logs:** General moderation actions",
            inline=False
        )
        
        embed.set_footer(text="💡 Each log type can use the same channel or separate channels for organization")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error setting up logging: {e}")

@bot.command(name="config", aliases=["config_status", "status"])
@commands.has_permissions(administrator=True)
async def config_status(ctx):
    """Check the current configuration status"""
    try:
        embed = discord.Embed(
            title="⚙️ Configuration Status",
            description="Current bot configuration from .env file:",
            color=discord.Color.orange()
        )
        
        # Check token
        embed.add_field(
            name="🔑 Bot Token",
            value="✅ Configured" if TOKEN else "❌ Missing",
            inline=True
        )
        
        # Check welcome channel
        welcome_status = "❌ Not Set"
        if WELCOME_CHANNEL_ID:
            channel = bot.get_channel(WELCOME_CHANNEL_ID)
            welcome_status = f"✅ #{channel.name}" if channel else "❌ Invalid ID"
        embed.add_field(
            name="💬 Welcome Channel",
            value=welcome_status,
            inline=True
        )
        
        # Check lobby voice channel
        lobby_status = "❌ Not Set"
        if LOBBY_VOICE_CHANNEL_ID:
            channel = bot.get_channel(LOBBY_VOICE_CHANNEL_ID)
            lobby_status = f"✅ {channel.name}" if channel else "❌ Invalid ID"
        embed.add_field(
            name="🎤 Lobby Voice Channel",
            value=lobby_status,
            inline=True
        )
        
        # Check voice log channel
        log_status = "❌ Not Set"
        if VOICE_LOG_CHANNEL_ID:
            channel = bot.get_channel(VOICE_LOG_CHANNEL_ID)
            log_status = f"✅ #{channel.name}" if channel else "❌ Invalid ID"
        embed.add_field(
            name="📋 Voice Log Channel",
            value=log_status,
            inline=True
        )
        
        # Check voice category
        category_status = "❌ Not Set"
        if VOICE_CATEGORY_ID:
            category = bot.get_channel(VOICE_CATEGORY_ID)
            category_status = f"✅ {category.name}" if category else "❌ Invalid ID"
        embed.add_field(
            name="📁 Voice Category",
            value=category_status,
            inline=True
        )
        
        # Check default role
        role_status = "❌ Not Set"
        if DEFAULT_ROLE_ID:
            role = ctx.guild.get_role(DEFAULT_ROLE_ID)
            role_status = f"✅ @{role.name}" if role else "❌ Invalid ID"
        embed.add_field(
            name="👤 Default Role",
            value=role_status,
            inline=True
        )
        
        # Check allowed roles
        allowed_roles_status = "❌ Not Set (All users allowed)"
        if ALLOWED_ROLES:
            valid_roles = []
            for role_id in ALLOWED_ROLES:
                role = ctx.guild.get_role(role_id)
                if role:
                    valid_roles.append(f"@{role.name}")
            if valid_roles:
                allowed_roles_status = f"✅ {', '.join(valid_roles[:3])}"
                if len(valid_roles) > 3:
                    allowed_roles_status += f" +{len(valid_roles) - 3} more"
            else:
                allowed_roles_status = "❌ Invalid role IDs"
        embed.add_field(
            name="🎭 Allowed Roles",
            value=allowed_roles_status,
            inline=False
        )
        
        # Other settings
        embed.add_field(
            name="🔧 Other Settings",
            value=f"**Prefix:** `{BOT_PREFIX}`\n**Voice Limit:** {MAX_VOICE_LIMIT}",
            inline=True
        )
        
        # Privileged intents status
        intents_status = "✅ Enabled" if privileged_intents_available else "❌ Limited Mode"
        embed.add_field(
            name="🔐 Privileged Intents",
            value=intents_status,
            inline=True
        )
        
        # Check logging channels
        logging_status = []
        logging_channels = [
            ("Member Logs", MEMBER_LOG_CHANNEL_ID),
            ("Role Logs", ROLE_LOG_CHANNEL_ID), 
            ("Message Logs", MESSAGE_LOG_CHANNEL_ID),
            ("Mod Logs", MODERATION_LOG_CHANNEL_ID)
        ]
        
        for name, channel_id in logging_channels:
            if channel_id:
                channel = bot.get_channel(channel_id)
                status = f"✅ {name}" if channel else f"❌ {name}"
            else:
                status = f"⚪ {name}"
            logging_status.append(status)
        
        embed.add_field(
            name="📋 Logging Channels",
            value="\n".join(logging_status) + f"\n\nUse `{BOT_PREFIX}setup_logging` for details",
            inline=False
        )
        
        embed.set_footer(text=f"Use {BOT_PREFIX}get_ids to get channel/server IDs for your .env file")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error checking configuration: {e}")

@bot.command(name="bot_info", aliases=["info"])
async def bot_info(ctx):
    """Display bot information and features"""
    embed = discord.Embed(
        title="🤖 DOTGEN.AI Discord Bot",
        description=f"Advanced Discord bot with slash commands, dynamic voice channels and welcome system!{' (Limited Mode)' if not privileged_intents_available else ''}",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🚀 Modern Command Interface",
        value="**This bot uses slash commands for the best experience!**\n\nType `/` and look for `dotgen_` commands for full functionality.",
        inline=False
    )
    
    if privileged_intents_available:
        embed.add_field(
            name="🎉 Welcome System",
            value="Automatically sends unique welcome messages when new members join",
            inline=False
        )
    else:
        embed.add_field(
            name="🎉 Welcome System",
            value="Use `/dotgen_welcome @member` to send welcome messages",
            inline=False
        )
    
    embed.add_field(
        name="🎤 Dynamic Voice Channels",
        value="Join the 'Join to Create' channel to create role-based temporary voice channels",
        inline=False
    )
    
    if YOUTUBE_DL_AVAILABLE:
        embed.add_field(
            name="🎵 Music Player",
            value="Play music from YouTube with queue support, volume control, and more!\nUse `/dotgen_play` to get started.",
            inline=False
        )
    else:
        embed.add_field(
            name="🎵 Music Player (Disabled)",
            value="Music functionality available with yt-dlp installation.\nRun: `pip install yt-dlp`",
            inline=False
        )
    
    # Dynamically generate command categories
    general_cmds = []
    admin_cmds = []
    
    for command in bot.commands:
        if command.name in ["bot_info", "help"]:
            continue  # Skip info and help commands in listings
            
        # Check if it's an admin command by looking at decorators/checks
        is_admin = any(check.__name__ in ['has_permissions', 'is_owner'] for check in getattr(command, 'checks', []))
        
        cmd_line = f"`{BOT_PREFIX}{command.name}`"
        if command.aliases:
            cmd_line += f" (aliases: {', '.join(command.aliases)})"
        
        if command.help:
            short_help = command.help.split('\n')[0]
            if len(short_help) > 60:
                short_help = short_help[:57] + "..."
            cmd_line += f" - {short_help}"
        
        if is_admin:
            admin_cmds.append(cmd_line)
        else:
            general_cmds.append(cmd_line)
    
    embed.add_field(
        name="📖 General Commands",
        value="`/dotgen_help` - Complete help system\n`/dotgen_info` - Bot information\n`/dotgen_ping` - Check bot status",
        inline=False
    )
    
    embed.add_field(
        name="🛠️ Admin Commands", 
        value="`/dotgen_config` - View configuration\n`/dotgen_announce` - Send announcements\n`/dotgen_welcome` - Send welcome messages",
        inline=False
    )
    
    embed.add_field(
        name="� Stats",
        value=f"**Servers:** {len(bot.guilds)}\n**Commands:** {len(list(bot.commands))}\n**Temp Channels:** {len(temp_voice_channels)}",
        inline=True
    )
    
    embed.add_field(
        name="⚡ Quick Start",
        value=f"`{BOT_PREFIX}help` - View all commands\n`{BOT_PREFIX}help <command>` - Detailed help\n`/dotgen_` - Slash commands",
        inline=True
    )
    
    if not privileged_intents_available:
        embed.add_field(
            name="⚠️ Limited Mode",
            value="To enable automatic welcome messages, enable privileged intents in Discord Developer Portal",
            inline=False
        )
    
    embed.set_footer(text="💡 Use /dotgen_help for complete command list with slash commands!")
    
    await ctx.send(embed=embed)

@bot.command(name="ping")
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot latency: **{latency}ms**",
        color=discord.Color.green() if latency < 100 else discord.Color.orange() if latency < 200 else discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command(name="help")
async def help_command(ctx, *, command_name: str = None):
    """Dynamic help command that lists all available commands"""
    if command_name:
        # Show help for specific command
        cmd = bot.get_command(command_name.lower())
        if cmd:
            embed = discord.Embed(
                title=f"📖 Help: {BOT_PREFIX}{cmd.name}",
                description=cmd.help or "No description available.",
                color=discord.Color.blue()
            )
            
            if cmd.aliases:
                embed.add_field(
                    name="Aliases",
                    value=", ".join([f"`{BOT_PREFIX}{alias}`" for alias in cmd.aliases]),
                    inline=False
                )
            
            # Add usage information if available
            if cmd.signature:
                embed.add_field(
                    name="Usage",
                    value=f"`{BOT_PREFIX}{cmd.name} {cmd.signature}`",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Usage",
                    value=f"`{BOT_PREFIX}{cmd.name}`",
                    inline=False
                )
                
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Command `{command_name}` not found. Use `/help` (slash command) to see all commands.")
        return
    
    # Redirect to slash commands
    embed = discord.Embed(
        title="📖 DOTGEN.AI Bot Commands",
        description="**This bot primarily uses slash commands for the best experience!**",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🚀 Primary Command Interface",
        value="**Use `/` (slash commands) for all bot functions!**\n\nType `/` in chat and look for commands starting with `dotgen_`",
        inline=False
    )
    
    embed.add_field(
        name="⚡ Essential Slash Commands",
        value="`/dotgen_help` - Complete help\n`/dotgen_info` - Bot info\n`/dotgen_ping` - Status check\n`/dotgen_config` - Configuration\n`/dotgen_welcome` - Welcome messages" + (f"\n`/dotgen_play` - Play music\n`/dotgen_queue` - Music queue" if YOUTUBE_DL_AVAILABLE else ""),
        inline=False
    )
    
    embed.add_field(
        name="🎯 Quick Start",
        value="1. Type `/` in chat\n2. Look for `dotgen_` commands\n3. Use `/dotgen_help` for complete list\n4. Tab completion shows options!",
        inline=False
    )
    
    # Show limited prefix commands that still exist (shortened)
    prefix_cmds = [cmd.name for cmd in bot.commands if cmd.name not in ['help', 'bot_info']]
    if prefix_cmds:
        embed.add_field(
            name="⚠️ Legacy Commands",
            value=f"Admin commands use `{BOT_PREFIX}` prefix. **Use slash commands instead!**\nSee `/dotgen_help` for full list.",
            inline=False
        )
    
    embed.add_field(
        name="📊 Stats",
        value=f"**Slash Commands:** Available via `/dotgen_`\n**Servers:** {len(bot.guilds)}",
        inline=True
    )
    
    embed.set_footer(text="💡 Slash commands provide better autocomplete, validation, and user experience!")
    
    await ctx.send(embed=embed)

@bot.command(name="add_role")
@commands.has_permissions(administrator=True)
async def add_allowed_role(ctx, role: discord.Role):
    """Add a role to the allowed roles list for voice channel creation"""
    try:
        global ALLOWED_ROLES
        
        if role.id in ALLOWED_ROLES:
            await ctx.send(f"❌ Role @{role.name} is already in the allowed roles list.")
            return
        
        ALLOWED_ROLES.append(role.id)
        
        # Update .env file
        env_path = '.env'
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Update or add ALLOWED_ROLES line
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('ALLOWED_ROLES='):
                    lines[i] = f"ALLOWED_ROLES={','.join(map(str, ALLOWED_ROLES))}\n"
                    updated = True
                    break
            
            if not updated:
                lines.append(f"ALLOWED_ROLES={','.join(map(str, ALLOWED_ROLES))}\n")
            
            with open(env_path, 'w') as f:
                f.writelines(lines)
        
        embed = discord.Embed(
            title="✅ Role Added",
            description=f"Added @{role.name} to allowed roles for voice channel creation.",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Total Allowed Roles", 
            value=str(len(ALLOWED_ROLES)), 
            inline=True
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error adding role: {e}")

@bot.command(name="remove_role")
@commands.has_permissions(administrator=True)
async def remove_allowed_role(ctx, role: discord.Role):
    """Remove a role from the allowed roles list for voice channel creation"""
    try:
        global ALLOWED_ROLES
        
        if role.id not in ALLOWED_ROLES:
            await ctx.send(f"❌ Role @{role.name} is not in the allowed roles list.")
            return
        
        ALLOWED_ROLES.remove(role.id)
        
        # Update .env file
        env_path = '.env'
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Update ALLOWED_ROLES line
            for i, line in enumerate(lines):
                if line.startswith('ALLOWED_ROLES='):
                    lines[i] = f"ALLOWED_ROLES={','.join(map(str, ALLOWED_ROLES))}\n"
                    break
            
            with open(env_path, 'w') as f:
                f.writelines(lines)
        
        embed = discord.Embed(
            title="✅ Role Removed",
            description=f"Removed @{role.name} from allowed roles for voice channel creation.",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="Total Allowed Roles", 
            value=str(len(ALLOWED_ROLES)), 
            inline=True
        )
        if len(ALLOWED_ROLES) == 0:
            embed.add_field(
                name="⚠️ Note",
                value="All users can now create voice channels",
                inline=False
            )
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error removing role: {e}")

@bot.command(name="list_roles", aliases=["roles"])
@commands.has_permissions(administrator=True)
async def list_allowed_roles(ctx):
    """List all allowed roles for voice channel creation"""
    try:
        if not ALLOWED_ROLES:
            embed = discord.Embed(
                title="🎭 Allowed Roles",
                description="No specific roles are configured. All users can create voice channels.",
                color=discord.Color.blue()
            )
        else:
            role_list = []
            invalid_roles = []
            
            for role_id in ALLOWED_ROLES:
                role = ctx.guild.get_role(role_id)
                if role:
                    role_list.append(f"• @{role.name} (`{role_id}`)")
                else:
                    invalid_roles.append(str(role_id))
            
            embed = discord.Embed(
                title="🎭 Allowed Roles for Voice Channel Creation",
                description="\n".join(role_list) if role_list else "No valid roles found",
                color=discord.Color.blue()
            )
            
            if invalid_roles:
                embed.add_field(
                    name="⚠️ Invalid Role IDs",
                    value=", ".join(invalid_roles),
                    inline=False
                )
            
            embed.add_field(
                name="Total", 
                value=f"{len(role_list)} valid roles", 
                inline=True
            )
        
        embed.set_footer(text=f"Use {BOT_PREFIX}add_role @role to add roles or {BOT_PREFIX}remove_role @role to remove roles")
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error listing roles: {e}")

@bot.command(name="voice_stats", aliases=["vstats", "stats"])
@commands.has_permissions(administrator=True)
async def voice_stats(ctx):
    """Show voice channel statistics"""
    try:
        embed = discord.Embed(
            title="📊 Voice Channel Statistics",
            color=discord.Color.blue()
        )
        
        # Active temporary channels
        active_channels = len(temp_voice_channels)
        embed.add_field(
            name="🎤 Active Temp Channels",
            value=str(active_channels),
            inline=True
        )
        
        # Channels by role
        role_counts = {}
        for channel_info in temp_voice_channels.values():
            role = channel_info.get('role', 'Unknown')
            role_counts[role] = role_counts.get(role, 0) + 1
        
        if role_counts:
            role_stats = "\n".join([f"• {role}: {count}" for role, count in sorted(role_counts.items())])
            embed.add_field(
                name="📋 Channels by Role",
                value=role_stats,
                inline=False
            )
        
        # Active users
        active_users = []
        for channel_info in temp_voice_channels.values():
            channel = channel_info['channel']
            if len(channel.members) > 0:
                active_users.extend(channel.members)
        
        embed.add_field(
            name="👥 Users in Temp Channels",
            value=str(len(set(active_users))),
            inline=True
        )
        
        # Configuration status
        config_items = []
        if VOICE_LOG_CHANNEL_ID:
            config_items.append("✅ Log Channel")
        if ALLOWED_ROLES:
            config_items.append(f"✅ {len(ALLOWED_ROLES)} Allowed Roles")
        else:
            config_items.append("⚠️ No Role Restrictions")
        
        embed.add_field(
            name="⚙️ Configuration",
            value="\n".join(config_items),
            inline=True
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error getting stats: {e}")

@bot.command(name="cleanup", aliases=["cleanup_channels", "clean"])
@commands.has_permissions(administrator=True)
async def cleanup_channels(ctx):
    """Clean up all empty temporary voice channels"""
    cleaned = 0
    for channel_id, channel_info in list(temp_voice_channels.items()):
        channel = channel_info['channel']
        try:
            if len(channel.members) == 0:
                await channel.delete()
                del temp_voice_channels[channel_id]
                cleaned += 1
        except:
            # Channel might already be deleted
            del temp_voice_channels[channel_id]
    
    await ctx.send(f"✅ Cleaned up {cleaned} empty voice channels.")

@bot.command(name="send")
@commands.has_permissions(administrator=True)
async def send_message(ctx, channel: discord.TextChannel, *, message):
    """Send a message from the bot to any channel"""
    try:
        # Check if bot has permission to send messages in the target channel
        if not channel.permissions_for(ctx.guild.me).send_messages:
            await ctx.send(f"❌ I don't have permission to send messages in {channel.mention}")
            return
        
        await channel.send(message)
        await ctx.send(f"✅ Message sent to {channel.mention}")
            
    except Exception as e:
        await ctx.send(f"❌ Error sending message: {e}")

@bot.command(name="announce")
@commands.has_permissions(administrator=True)
async def announce(ctx, channel: discord.TextChannel, *, message):
    """Send an announcement to a specific channel"""
    try:
        # Check if bot has permission to send messages in the target channel
        if not channel.permissions_for(ctx.guild.me).send_messages:
            await ctx.send(f"❌ I don't have permission to send messages in {channel.mention}")
            return
        
        # Create announcement embed
        embed = discord.Embed(
            title="📢 Server Announcement",
            description=message,
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Announced by {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        # Send the announcement
        await channel.send(embed=embed)
        
        # Confirm to the user
        if channel != ctx.channel:
            await ctx.send(f"✅ Announcement sent to {channel.mention}")
        else:
            await ctx.send("✅ Announcement sent!")
        
    except Exception as e:
        await ctx.send(f"❌ Error sending announcement: {e}")

@bot.command(name="announce_all")
@commands.has_permissions(administrator=True)
async def announce_all(ctx, *, message):
    """Send an announcement to multiple common announcement channels"""
    try:
        # Look for common announcement channels
        target_channels = []
        for channel in ctx.guild.text_channels:
            if channel.name.lower() in ['announcements', 'announcement', 'general', 'news']:
                target_channels.append(channel)
        
        # If no announcement channels found, use current channel
        if not target_channels:
            target_channels = [ctx.channel]
        
        # Create announcement embed
        embed = discord.Embed(
            title="📢 Server Announcement",
            description=message,
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Announced by {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        sent_count = 0
        failed_channels = []
        
        for channel in target_channels:
            try:
                if channel.permissions_for(ctx.guild.me).send_messages:
                    await channel.send(embed=embed)
                    sent_count += 1
                else:
                    failed_channels.append(channel.name)
            except Exception as e:
                failed_channels.append(f"{channel.name} (Error: {str(e)[:50]})")
        
        # Send response
        response_msg = f"✅ Announcement sent to {sent_count} channel(s)"
        if failed_channels:
            response_msg += f"\n⚠️ Failed to send to: {', '.join(failed_channels)}"
        
        await ctx.send(response_msg)
        
    except Exception as e:
        await ctx.send(f"❌ Error sending announcement: {e}")

@bot.command(name="echo")
@commands.has_permissions(manage_messages=True)
async def echo(ctx, *, message):
    """Make the bot repeat a message in the current channel"""
    try:
        await ctx.message.delete()  # Delete the command message
        await ctx.send(message)
            
    except Exception as e:
        await ctx.send(f"❌ Error sending message: {e}")

# =============================================================================
# MUSIC PREFIX COMMANDS (Legacy support)
# =============================================================================

if YOUTUBE_DL_AVAILABLE:
    @bot.command(name="play", aliases=["p"])
    async def play_music(ctx, *, query):
        """Play music from YouTube (Legacy command - use /dotgen_play instead)"""
        # Check if user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel to play music!")
            return

        # Join voice channel
        voice_client = await join_voice_channel(ctx)
        if not voice_client:
            return

        # Initialize music queue for guild if needed
        if ctx.guild.id not in music_queues:
            music_queues[ctx.guild.id] = MusicQueue()

        queue = music_queues[ctx.guild.id]

        try:
            # Search for the song
            search_msg = await ctx.send(f"🔍 Searching for: **{query}**...")
            
            # Create the audio source
            player = await YTDLSource.from_url(query, loop=bot.loop, stream=True, requester=ctx.author)
            
            # Add to queue
            queue.add_song(player)
            
            # If nothing is currently playing, start playing
            if not voice_client.is_playing():
                await play_next_song(ctx.guild.id, voice_client)
                embed = discord.Embed(
                    title="🎵 Now Playing",
                    description=f"**{player.title}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
                if player.duration:
                    mins, secs = divmod(player.duration, 60)
                    embed.add_field(name="Duration", value=f"{mins}:{secs:02d}", inline=True)
                await search_msg.edit(content=None, embed=embed)
            else:
                embed = discord.Embed(
                    title="📝 Added to Queue",
                    description=f"**{player.title}**",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
                embed.add_field(name="Position in queue", value=str(len(queue.queue)), inline=True)
                if player.duration:
                    mins, secs = divmod(player.duration, 60)
                    embed.add_field(name="Duration", value=f"{mins}:{secs:02d}", inline=True)
                await search_msg.edit(content=None, embed=embed)
                
        except Exception as e:
            error_msg = str(e)
            
            # Provide user-friendly error messages
            if "Sign in to confirm you're not a bot" in error_msg or "bot" in error_msg.lower():
                embed = discord.Embed(
                    title="🤖 Bot Detection - Trying Alternatives",
                    description="YouTube detected bot access. Using alternative methods...",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="💡 What to try:",
                    value="• Search by song name instead of URL\n• Use `/dotgen_search` first\n• Try again in a few minutes",
                    inline=False
                )
                await search_msg.edit(content=None, embed=embed)
            else:
                await search_msg.edit(content=f"❌ Error: Unable to play music. Try searching by song name or use `/dotgen_search` first.")

    @bot.command(name="skip", aliases=["s"])
    async def skip_music(ctx):
        """Skip the current song"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel to use music commands!")
            return

        voice_client = ctx.guild.voice_client
        if not voice_client:
            await ctx.send("❌ I'm not playing any music!")
            return

        if voice_client.is_playing():
            voice_client.stop()
            await ctx.send("⏭️ Song skipped!")
        else:
            await ctx.send("❌ No music is currently playing!")

    @bot.command(name="stop")
    async def stop_music(ctx):
        """Stop music and clear queue"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel to use music commands!")
            return

        voice_client = ctx.guild.voice_client
        if not voice_client:
            await ctx.send("❌ I'm not connected to any voice channel!")
            return

        # Clear queue and stop music
        if ctx.guild.id in music_queues:
            music_queues[ctx.guild.id].clear()

        if voice_client.is_playing():
            voice_client.stop()

        await ctx.send("⏹️ Music stopped and queue cleared!")

    @bot.command(name="queue", aliases=["q"])
    async def show_queue(ctx):
        """Show the music queue"""
        if ctx.guild.id not in music_queues:
            await ctx.send("❌ No music queue found!")
            return

        queue = music_queues[ctx.guild.id]
        
        embed = discord.Embed(
            title="🎵 Music Queue",
            color=discord.Color.blue()
        )

        if queue.current:
            embed.add_field(
                name="🎵 Now Playing",
                value=f"**{queue.current.title}**\nRequested by: {queue.current.requester.mention if queue.current.requester else 'Unknown'}",
                inline=False
            )

        if queue.queue:
            queue_text = ""
            for i, song in enumerate(queue.queue[:10], 1):  # Show first 10 songs
                queue_text += f"{i}. **{song.title}** - {song.requester.mention if song.requester else 'Unknown'}\n"
            
            if len(queue.queue) > 10:
                queue_text += f"\n... and {len(queue.queue) - 10} more songs"
            
            embed.add_field(
                name=f"📝 Up Next ({len(queue.queue)} songs)",
                value=queue_text,
                inline=False
            )
        else:
            if not queue.current:
                embed.add_field(
                    name="📝 Queue Status",
                    value=f"Queue is empty. Use `{BOT_PREFIX}play <song>` to add songs!",
                    inline=False
                )

        await ctx.send(embed=embed)

    @bot.command(name="volume", aliases=["vol"])
    async def set_volume(ctx, volume: int):
        """Change music volume (0-100)"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel to use music commands!")
            return

        if volume < 0 or volume > 100:
            await ctx.send("❌ Volume must be between 0 and 100!")
            return

        voice_client = ctx.guild.voice_client
        if not voice_client:
            await ctx.send("❌ I'm not connected to any voice channel!")
            return

        # Update volume
        volume_decimal = volume / 100
        if ctx.guild.id in music_queues:
            music_queues[ctx.guild.id].volume = volume_decimal

        if voice_client.source:
            voice_client.source.volume = volume_decimal

        await ctx.send(f"🔊 Volume set to **{volume}%**")

    @bot.command(name="disconnect", aliases=["dc", "leave"])
    async def disconnect_music(ctx):
        """Disconnect from voice channel"""
        voice_client = ctx.guild.voice_client
        if not voice_client:
            await ctx.send("❌ I'm not connected to any voice channel!")
            return

        # Clear queue and disconnect
        if ctx.guild.id in music_queues:
            music_queues[ctx.guild.id].clear()
            del music_queues[ctx.guild.id]

        if ctx.guild.id in voice_clients:
            del voice_clients[ctx.guild.id]

        await voice_client.disconnect()
        await ctx.send("👋 Disconnected from voice channel!")

# =============================================================================
# END MUSIC PREFIX COMMANDS
# =============================================================================

# Rotating status activities
ACTIVITIES = [
    {"name": "DOTGEN.AI server 🛠️", "type": discord.ActivityType.watching},
    {"name": "for new members 👀", "type": discord.ActivityType.watching},
    {"name": "DOTGEN.AI community 👥", "type": discord.ActivityType.watching},
    {"name": f"{BOT_PREFIX} commands 💬", "type": discord.ActivityType.listening},
    {"name": "voice channels 🎤", "type": discord.ActivityType.listening},
    {"name": "DOTGEN.AI announcements 📢", "type": discord.ActivityType.watching},
    {"name": "music 🎵", "type": discord.ActivityType.listening},
    {"name": "/dotgen_ commands 🎯", "type": discord.ActivityType.listening},
]

# Global variable to track current activity index
current_activity_index = 0

async def start_rotating_status():
    """Start the rotating status task"""
    global current_activity_index
    
    async def rotate_status():
        global current_activity_index
        while True:
            try:
                activity = ACTIVITIES[current_activity_index]
                await bot.change_presence(
                    activity=discord.Activity(
                        type=activity["type"],
                        name=activity["name"]
                    ),
                    status=discord.Status.online
                )
                
                # Move to next activity
                current_activity_index = (current_activity_index + 1) % len(ACTIVITIES)
                
                # Wait 10 seconds before changing to next activity
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"Error setting rotating status: {e}")
                await asyncio.sleep(5)  # Wait 5 seconds before retrying
    
    # Create and start the background task
    bot.loop.create_task(rotate_status())

@bot.command(name="botstatus", aliases=["activity"])
@commands.has_permissions(administrator=True)
async def status_control(ctx, action="current", *, custom_status=None):
    """Control the bot's rotating status"""
    action = action.lower()
    
    try:
        if action == "current":
            # Show current status
            current_activity = ACTIVITIES[current_activity_index]
            embed = discord.Embed(
                title="🎭 Current Bot Status",
                description=f"**Activity:** {current_activity['name']}\n**Type:** {current_activity['type'].name.title()}",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            
        elif action == "list":
            # List all available activities
            embed = discord.Embed(
                title="📋 Available Status Activities",
                color=discord.Color.blue()
            )
            
            for i, activity in enumerate(ACTIVITIES):
                status_indicator = "🔸" if i == current_activity_index else "▫️"
                embed.add_field(
                    name=f"{status_indicator} {activity['type'].name.title()}",
                    value=activity['name'],
                    inline=False
                )
            
            embed.set_footer(text="🔸 = Currently active activity")
            await ctx.send(embed=embed)
            
        elif action == "stop":
            # Stop rotating and set a static status
            static_status = custom_status or "Bot is online"
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=static_status
                ),
                status=discord.Status.online
            )
            await ctx.send(f"✅ Rotating status stopped. Set to: **{static_status}**")
            
        elif action == "start":
            # Restart rotating status
            await start_rotating_status()
            await ctx.send("✅ Rotating status restarted!")
            
        elif action == "custom":
            # Set custom status
            if not custom_status:
                await ctx.send("❌ Please provide a custom status message.")
                return
            
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=custom_status
                ),
                status=discord.Status.online
            )
            
            await ctx.send(f"✅ Custom status set: **Watching** {custom_status}")
            
        else:
            await ctx.send(f"❌ Invalid action. Use: `current`, `list`, `start`, `stop`, or `custom`")
            
    except Exception as e:
        await ctx.send(f"❌ Error controlling status: {e}")

# Error handling for commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have the required permissions to use this command.")
    elif isinstance(error, commands.CommandNotFound):
        # Don't respond to unknown commands to avoid spam
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument. Use `{BOT_PREFIX}help {ctx.command}` for usage.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Invalid argument. Use `{BOT_PREFIX}help {ctx.command}` for usage.")
    else:
        await ctx.send(f"❌ An error occurred: {error}")
        print(f"Command error: {error}")

# =============================================================================
# WEBSERVER FOR 24/7 OPERATION
# =============================================================================
# This Flask webserver helps keep the bot alive when deployed to cloud platforms
# like Heroku, Railway, Render, etc. by providing HTTP endpoints that can be
# pinged by uptime monitors or the platform itself to prevent the bot from sleeping.
#
# Available endpoints:
# - GET / : Main health check with bot status info
# - GET /health : Simple health check for monitoring
# - GET /ping : Simple ping endpoint (returns "pong")
#
# The webserver runs in a separate thread so it doesn't block the Discord bot.
# =============================================================================

# Flask webserver setup (only if Flask is available)
if FLASK_AVAILABLE:
    app = Flask(__name__)

    @app.route('/')
    def home():
        """Main health check endpoint for the webserver"""
        return jsonify({
            "status": "online",
            "bot": "DOTGEN.AI Discord Bot",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "uptime": "operational",
            "message": "Bot is running and ready!",
            "endpoints": {
                "health": "/health",
                "ping": "/ping", 
                "keepalive": "/keepalive",
                "status": "/status"
            }
        })

    @app.route('/health')
    def health():
        """Health endpoint for uptime monitoring (UptimeRobot compatible)"""
        return jsonify({
            "status": "healthy",
            "uptime": "operational",
            "service": "DOTGEN.AI Bot",
            "timestamp": datetime.now().isoformat()
        })

    @app.route('/ping')
    def ping():
        """Simple ping endpoint (returns plain text)"""
        return "pong"
    
    @app.route('/keepalive')
    def keepalive():
        """Keep-alive endpoint specifically for UptimeRobot"""
        return jsonify({
            "alive": True,
            "service": "DOTGEN.AI Discord Bot",
            "timestamp": datetime.now().isoformat(),
            "message": "Service is alive and running"
        })
    
    @app.route('/status')
    def status():
        """Detailed status endpoint with bot information"""
        try:
            guild_count = len(bot.guilds) if bot.is_ready() else 0
            temp_channels = len(temp_voice_channels)
            
            return jsonify({
                "bot_status": "online" if bot.is_ready() else "starting",
                "discord_connected": bot.is_ready(),
                "guilds": guild_count,
                "temp_voice_channels": temp_channels,
                "privileged_intents": privileged_intents_available,
                "flask_available": FLASK_AVAILABLE,
                "timestamp": datetime.now().isoformat(),
                "version": "2.0",
                "service": "DOTGEN.AI Bot"
            })
        except Exception as e:
            return jsonify({
                "bot_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "service": "DOTGEN.AI Bot"
            }), 500

    def run_webserver():
        """Run the Flask webserver in a separate thread"""
        try:
            port = int(os.getenv('PORT', 8080))
            app.run(host='0.0.0.0', port=port, debug=False)
        except Exception as e:
            print(f"❌ Webserver error: {e}")

    def start_webserver():
        """Start the webserver in a background thread"""
        try:
            webserver_thread = threading.Thread(target=run_webserver, daemon=True)
            webserver_thread.start()
            print(f"🌐 DOTGEN.AI Webserver started on port {os.getenv('PORT', 8080)}")
            return True
        except Exception as e:
            print(f"❌ Failed to start webserver: {e}")
            return False
else:
    def start_webserver():
        """Dummy function when Flask is not available"""
        print("⚠️  Webserver not available (Flask not installed)")
        return False

def start_webserver():
    """Start the webserver in a background thread"""
    webserver_thread = threading.Thread(target=run_webserver, daemon=True)
    webserver_thread.start()
    print(f"🌐 DOTGEN.AI Webserver started on port {os.getenv('PORT', 8080)}")

# =============================================================================
# SLASH COMMANDS - Modern Discord commands that don't conflict with Discord
# =============================================================================

# Create guild object for slash commands
guild_obj = discord.Object(id=GUILD_ID) if GUILD_ID else None

@bot.tree.command(name="dotgen_ping", description="Check bot latency and status", guild=guild_obj)
async def slash_ping(interaction: discord.Interaction):
    """Slash command to check bot latency"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot latency: **{latency}ms**",
        color=discord.Color.green() if latency < 100 else discord.Color.orange() if latency < 200 else discord.Color.red()
    )
    await interaction.response.send_message(embed=embed, ephemeral=False)

@bot.tree.command(name="dotgen_info", description="Display bot information and features", guild=guild_obj)
async def slash_info(interaction: discord.Interaction):
    """Slash command for bot info"""
    embed = discord.Embed(
        title="🤖 DOTGEN.AI Discord Bot",
        description=f"Advanced Discord bot with dynamic voice channels and welcome system!{' (Limited Mode)' if not privileged_intents_available else ''}",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🎤 Dynamic Voice Channels",
        value="Join the 'Join to Create' channel to create role-based temporary voice channels",
        inline=False
    )
    
    # Count available commands dynamically
    prefix_commands = len(list(bot.commands))
    slash_commands = len([cmd for cmd in bot.tree.get_commands(guild=interaction.guild)])
    
    embed.add_field(
        name="⚡ Commands Available",
        value=f"**Prefix Commands:** {prefix_commands} (use `{BOT_PREFIX}help`)\n**Slash Commands:** {slash_commands} (type `/dotgen_`)",
        inline=False
    )
    
    embed.add_field(
        name="🎉 Key Features",
        value="• Auto Welcome Messages\n• Dynamic Voice Channels\n• Admin Management Tools\n• 24/7 Uptime Monitoring\n• Role-Based Access Control" + (f"\n• Music Player with Queue Support" if YOUTUBE_DL_AVAILABLE else "\n• Music Player (Install yt-dlp)"),
        inline=False
    )
    
    embed.add_field(
        name="📊 Stats",
        value=f"**Servers:** {len(bot.guilds)}\n**Active Temp Channels:** {len(temp_voice_channels)}",
        inline=True
    )
    
    embed.add_field(
        name="🔗 Quick Links",
        value=f"`{BOT_PREFIX}help` - All commands\n`{BOT_PREFIX}config` - Bot settings\n`{BOT_PREFIX}ping` - Bot status",
        inline=True
    )
    
    embed.set_footer(text="Use prefix commands (!) or slash commands (/dotgen_) for full functionality")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="dotgen_welcome", description="Send a welcome message for a member", guild=guild_obj)
@app_commands.describe(member="The member to welcome")
async def slash_welcome(interaction: discord.Interaction, member: discord.Member = None):
    """Slash command to welcome a member"""
    if not member:
        member = interaction.user
    
    # Check permissions
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ You need 'Manage Messages' permission to use this command.", ephemeral=True)
        return
    
    try:
        # Get the welcome channel
        welcome_channel = interaction.channel
        if WELCOME_CHANNEL_ID:
            welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID) or interaction.channel
        
        # Create welcome image
        welcome_image = await create_welcome_image(member)
        
        # Create a welcome embed
        welcome_msg = random.choice(WELCOME_MESSAGES).format(member=member.mention)
        embed = discord.Embed(
            title="🎉 Welcome Message!",
            description=welcome_msg,
            color=discord.Color.gold()
        )
        
        if welcome_image:
            embed.set_image(url="attachment://welcome.png")
        else:
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        embed.add_field(
            name="Account Created", 
            value=discord.utils.format_dt(member.created_at, style='R'), 
            inline=True
        )
        embed.set_footer(text=f"Welcome to {interaction.guild.name}!")
        
        # Send welcome message
        if welcome_image:
            await welcome_channel.send(file=welcome_image, embed=embed)
        else:
            await welcome_channel.send(embed=embed)
        
        if welcome_channel != interaction.channel:
            await interaction.response.send_message(f"✅ Welcome message sent to {welcome_channel.mention} for {member.mention}", ephemeral=True)
        else:
            await interaction.response.send_message("✅ Welcome message sent!", ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error sending welcome message: {e}", ephemeral=True)

@bot.tree.command(name="dotgen_announce", description="Send an anonymous announcement to a specific channel", guild=guild_obj)
@app_commands.describe(channel="The channel to send the announcement to", message="The announcement message (supports mentions)")
async def slash_announce(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    """Slash command to send anonymous announcements with proper mention support"""
    # Check permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    try:
        # Check if bot has permission to send messages in the target channel
        if not channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message(f"❌ I don't have permission to send messages in {channel.mention}", ephemeral=True)
            return
        
        # Create anonymous announcement embed
        embed = discord.Embed(
            title="📢 Server Announcement",
            description=message,
            color=discord.Color.gold()
        )
        # Remove the footer to make it completely anonymous
        embed.timestamp = discord.utils.utcnow()
        
        # Send the announcement with allowed mentions to make mentions work
        await channel.send(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(
                everyone=True,
                users=True,
                roles=True
            )
        )
        
        # Confirm to the user (this stays private)
        await interaction.response.send_message(f"✅ Anonymous announcement sent to {channel.mention}", ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error sending announcement: {e}", ephemeral=True)

@bot.tree.command(name="dotgen_config", description="Check the current bot configuration", guild=guild_obj)
async def slash_config(interaction: discord.Interaction):
    """Slash command to check bot configuration"""
    # Check permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to view configuration.", ephemeral=True)
        return
    
    try:
        embed = discord.Embed(
            title="⚙️ Configuration Status",
            description="Current bot configuration from .env file:",
            color=discord.Color.orange()
        )
        
        # Check welcome channel
        welcome_status = "❌ Not Set"
        if WELCOME_CHANNEL_ID:
            channel = bot.get_channel(WELCOME_CHANNEL_ID)
            welcome_status = f"✅ #{channel.name}" if channel else "❌ Invalid ID"
        embed.add_field(
            name="💬 Welcome Channel",
            value=welcome_status,
            inline=True
        )
        
        # Check auto-role
        auto_role_status = "❌ Not Set"
        if AUTO_ROLE_ID:
            role = interaction.guild.get_role(AUTO_ROLE_ID)
            auto_role_status = f"✅ @{role.name}" if role else "❌ Invalid ID"
        embed.add_field(
            name="🎭 Auto Role",
            value=auto_role_status,
            inline=True
        )
        
        # Check specific VC roles
        vc_role_status = "❌ Not Set (Uses ALLOWED_ROLES)"
        if SPECIFIC_VC_ROLE_IDS:
            valid_roles = []
            for role_id in SPECIFIC_VC_ROLE_IDS:
                role = interaction.guild.get_role(role_id)
                if role:
                    valid_roles.append(f"@{role.name}")
            if valid_roles:
                vc_role_status = f"✅ {', '.join(valid_roles[:3])}"
                if len(valid_roles) > 3:
                    vc_role_status += f" +{len(valid_roles) - 3} more"
            else:
                vc_role_status = "❌ Invalid role IDs"
        embed.add_field(
            name="🎤 Specific VC Roles",
            value=vc_role_status,
            inline=True
        )
        
        # Check logging configuration
        logging_config = []
        log_channels = {
            "Member Logs": MEMBER_LOG_CHANNEL_ID,
            "Role Logs": ROLE_LOG_CHANNEL_ID,
            "Message Logs": MESSAGE_LOG_CHANNEL_ID,
            "Voice Logs": VOICE_LOG_CHANNEL_ID,
            "Moderation Logs": MODERATION_LOG_CHANNEL_ID
        }
        
        for log_type, channel_id in log_channels.items():
            if channel_id:
                channel = bot.get_channel(channel_id)
                if channel:
                    logging_config.append(f"✅ {log_type}")
                else:
                    logging_config.append(f"❌ {log_type} (Invalid ID)")
            else:
                logging_config.append(f"❌ {log_type}")
        
        # Split logging config into chunks to avoid field length limit
        chunk_size = 3
        for i in range(0, len(logging_config), chunk_size):
            chunk = logging_config[i:i + chunk_size]
            field_name = f"📝 Logging Config ({i//chunk_size + 1})" if len(logging_config) > chunk_size else "📝 Logging Configuration"
            embed.add_field(
                name=field_name,
                value="\n".join(chunk),
                inline=True
            )
        
        # Other settings
        embed.add_field(
            name="🔧 Other Settings",
            value=f"**Prefix:** `{BOT_PREFIX}`\n**Voice Limit:** {MAX_VOICE_LIMIT}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error checking configuration: {e}", ephemeral=True)

@bot.tree.command(name="dotgen_help", description="Show all available commands and help information", guild=guild_obj)
@app_commands.describe(command="Optional: Get detailed help for a specific command")
async def slash_help(interaction: discord.Interaction, command: str = None):
    """Slash command for dynamic help - PRIMARY COMMAND INTERFACE"""
    if command:
        # Show help for specific command
        cmd = bot.get_command(command.lower())
        if cmd:
            embed = discord.Embed(
                title=f"📖 Help: /{cmd.name}",
                description=cmd.help or "No description available.",
                color=discord.Color.blue()
            )
            
            if cmd.aliases:
                embed.add_field(
                    name="Aliases",
                    value=", ".join([f"`/{alias}`" for alias in cmd.aliases]),
                    inline=False
                )
            
            # Add usage information
            if cmd.signature:
                embed.add_field(
                    name="Usage",
                    value=f"`/{cmd.name} {cmd.signature}`",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Usage",
                    value=f"`/{cmd.name}`",
                    inline=False
                )
                
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Command `{command}` not found. Use `/dotgen_help` to see all commands.", ephemeral=True)
        return
    
    # Generate comprehensive slash command help
    embed = discord.Embed(
        title="📖 DOTGEN.AI Bot Commands",
        description="**Complete command list - Slash commands provide the best experience!**",
        color=discord.Color.blue()
    )
    
    # Show all available slash commands
    slash_cmds = []
    for cmd in bot.tree.get_commands(guild=interaction.guild):
        cmd_info = f"`/{cmd.name}`"
        if hasattr(cmd, 'description') and cmd.description:
            desc = cmd.description
            if len(desc) > 40:  # Shortened description length
                desc = desc[:37] + "..."
            cmd_info += f" - {desc}"
        slash_cmds.append(cmd_info)
    
    if slash_cmds:
        # Split into smaller chunks to prevent field overflow
        chunks = [slash_cmds[i:i+6] for i in range(0, len(slash_cmds), 6)]  # Reduced chunk size
        for i, chunk in enumerate(chunks[:2]):  # Limit to 2 chunks only
            title = "⚡ Primary Slash Commands" if i == 0 else "⚡ More Commands"
            field_value = "\n".join(chunk)
            # Ensure field doesn't exceed 1024 characters
            if len(field_value) > 1000:
                field_value = field_value[:997] + "..."
            embed.add_field(name=title, value=field_value, inline=False)
    
    # Show essential commands prominently  
    embed.add_field(
        name="🎯 Essential Commands",
        value="`/dotgen_info` - Bot info\n`/dotgen_ping` - Bot status\n`/dotgen_config` - Configuration\n`/dotgen_welcome` - Welcome msg\n`/dotgen_announce` - Announcements" + (f"\n`/dotgen_play` - Play music\n`/dotgen_queue` - Music queue" if YOUTUBE_DL_AVAILABLE else ""),
        inline=False
    )
    
    # Show music commands if available
    if YOUTUBE_DL_AVAILABLE:
        embed.add_field(
            name="🎵 Music Commands",
            value="`/dotgen_play` - Play music\n`/dotgen_skip` - Skip song\n`/dotgen_queue` - Show queue\n`/dotgen_volume` - Set volume\n`/dotgen_shuffle` - Toggle shuffle\n`/dotgen_loop` - Toggle loop modes",
            inline=False
        )
    
    # Show prefix commands as legacy (shortened)
    prefix_commands = [cmd.name for cmd in bot.commands if cmd.name not in ['help', 'bot_info']]
    if prefix_commands:
        legacy_list = [f"`/{name}`" for name in sorted(prefix_commands)[:4]]  # Reduced to 4
        embed.add_field(
            name="🔧 Legacy Admin Commands",
            value=f"Admin commands use `{BOT_PREFIX}` prefix:\n" + " • ".join(legacy_list),
            inline=False
        )
    
    embed.add_field(
        name="💡 Tips",
        value="• Type `/` for autocomplete\n• Tab shows options\n• Slash commands validate input\n• Use `/dotgen_help <command>` for details",
        inline=False
    )
    
    embed.add_field(
        name="📊 Command Stats",
        value=f"**Slash Commands:** {len(slash_cmds)}\n**Legacy Prefix:** {len(prefix_commands)}\n**Servers:** {len(bot.guilds)}",
        inline=True
    )
    
    embed.add_field(
        name="🚀 Quick Start",
        value="1. Type `/` in any chat\n2. Look for `dotgen_` commands\n3. Use Tab for autocomplete\n4. Enjoy better UX!",
        inline=True
    )
    
    embed.set_footer(text="🌟 Slash commands are the future of Discord bots - enjoy the improved experience!")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# =============================================================================
# MUSIC SLASH COMMANDS
# =============================================================================

if YOUTUBE_DL_AVAILABLE:
    @bot.tree.command(name="dotgen_play", description="Play music from YouTube", guild=guild_obj)
    @app_commands.describe(query="Song name or YouTube URL to play")
    async def slash_play(interaction: discord.Interaction, query: str):
        """Slash command to play music"""
        await interaction.response.defer()
        
        # Check if user is in a voice channel
        if not interaction.user.voice:
            await interaction.followup.send("❌ You need to be in a voice channel to play music!", ephemeral=True)
            return

        # Join voice channel
        voice_client = await join_voice_channel_for_music(interaction)
        if not voice_client:
            return

        # Initialize music queue for guild if needed
        if interaction.guild.id not in music_queues:
            music_queues[interaction.guild.id] = MusicQueue()

        queue = music_queues[interaction.guild.id]

        try:
            # Search for the song
            await interaction.followup.send(f"🔍 Searching for: **{query}**...")
            
            # Create the audio source with enhanced error handling
            player = await YTDLSource.from_url(query, loop=bot.loop, stream=True, requester=interaction.user)
            
            # Add to queue
            queue.add_song(player)
            
            # If nothing is currently playing, start playing
            if not voice_client.is_playing():
                await play_next_song(interaction.guild.id, voice_client)
                embed = discord.Embed(
                    title="🎵 Now Playing",
                    description=f"**{player.title}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="Requested by", value=interaction.user.mention, inline=True)
                if player.duration:
                    mins, secs = divmod(player.duration, 60)
                    embed.add_field(name="Duration", value=f"{mins}:{secs:02d}", inline=True)
                if hasattr(player, 'thumbnail') and player.thumbnail:
                    embed.set_thumbnail(url=player.thumbnail)
                await interaction.edit_original_response(content=None, embed=embed)
            else:
                embed = discord.Embed(
                    title="📝 Added to Queue",
                    description=f"**{player.title}**",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Requested by", value=interaction.user.mention, inline=True)
                embed.add_field(name="Position in queue", value=str(len(queue.queue)), inline=True)
                if player.duration:
                    mins, secs = divmod(player.duration, 60)
                    embed.add_field(name="Duration", value=f"{mins}:{secs:02d}", inline=True)
                if hasattr(player, 'thumbnail') and player.thumbnail:
                    embed.set_thumbnail(url=player.thumbnail)
                await interaction.edit_original_response(content=None, embed=embed)
                
        except Exception as e:
            error_msg = str(e)
            
            # Provide user-friendly error messages and solutions
            if "Sign in to confirm you're not a bot" in error_msg or "bot" in error_msg.lower():
                embed = discord.Embed(
                    title="🤖 Bot Detection Error",
                    description="YouTube has detected automated access. Trying alternative methods...",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="💡 What's happening?",
                    value="YouTube is blocking bot access to prevent abuse.",
                    inline=False
                )
                embed.add_field(
                    name="🔧 Solutions:",
                    value="• Try searching by song name instead of URL\n• Use shorter, more specific search terms\n• Try again in a few minutes\n• Use direct YouTube links",
                    inline=False
                )
                embed.add_field(
                    name="🎵 Alternative:",
                    value="Try: `/dotgen_search <song name>` to find songs before playing",
                    inline=False
                )
                await interaction.edit_original_response(content=None, embed=embed)
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                embed = discord.Embed(
                    title="🌐 Connection Error",
                    description="Unable to connect to music sources.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="💡 Try:",
                    value="• Check if the URL is valid\n• Try a different song\n• Wait a moment and try again",
                    inline=False
                )
                await interaction.edit_original_response(content=None, embed=embed)
            elif "not found" in error_msg.lower() or "unavailable" in error_msg.lower():
                embed = discord.Embed(
                    title="🔍 Song Not Found",
                    description="The requested song could not be found or is unavailable.",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="💡 Try:",
                    value="• Check spelling of song/artist name\n• Try a more specific search\n• Use `/dotgen_search` to find available songs",
                    inline=False
                )
                await interaction.edit_original_response(content=None, embed=embed)
            else:
                # Generic error with helpful suggestions
                embed = discord.Embed(
                    title="❌ Music Error",
                    description="Unable to play the requested music.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="💡 Suggestions:",
                    value="• Try a different song or search term\n• Use `/dotgen_search` to find songs\n• Check if the URL is valid\n• Contact an admin if the problem persists",
                    inline=False
                )
                embed.add_field(
                    name="🔧 Quick fixes:",
                    value="• Search by song name instead of URL\n• Try shorter, more common song titles\n• Wait a few minutes and try again",
                    inline=False
                )
                if len(error_msg) < 500:  # Only show error if it's not too long
                    embed.add_field(name="Technical details:", value=f"`{error_msg}`", inline=False)
                await interaction.edit_original_response(content=None, embed=embed)

    @bot.tree.command(name="dotgen_skip", description="Skip the current song", guild=guild_obj)
    async def slash_skip(interaction: discord.Interaction):
        """Slash command to skip current song"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You need to be in a voice channel to use music commands!", ephemeral=True)
            return

        voice_client = interaction.guild.voice_client
        if not voice_client:
            await interaction.response.send_message("❌ I'm not playing any music!", ephemeral=True)
            return

        if interaction.guild.id not in music_queues:
            await interaction.response.send_message("❌ No music queue found!", ephemeral=True)
            return

        queue = music_queues[interaction.guild.id]
        
        if voice_client.is_playing():
            voice_client.stop()
            embed = discord.Embed(
                title="⏭️ Song Skipped",
                description="Playing next song in queue...",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ No music is currently playing!", ephemeral=True)

    @bot.tree.command(name="dotgen_stop", description="Stop music and clear queue", guild=guild_obj)
    async def slash_stop(interaction: discord.Interaction):
        """Slash command to stop music and clear queue"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You need to be in a voice channel to use music commands!", ephemeral=True)
            return

        voice_client = interaction.guild.voice_client
        if not voice_client:
            await interaction.response.send_message("❌ I'm not connected to any voice channel!", ephemeral=True)
            return

        # Clear queue and stop music
        if interaction.guild.id in music_queues:
            music_queues[interaction.guild.id].clear()

        if voice_client.is_playing():
            voice_client.stop()

        embed = discord.Embed(
            title="⏹️ Music Stopped",
            description="Queue cleared and music stopped.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="dotgen_queue", description="Show the music queue", guild=guild_obj)
    async def slash_queue(interaction: discord.Interaction):
        """Slash command to show music queue"""
        if interaction.guild.id not in music_queues:
            await interaction.response.send_message("❌ No music queue found!", ephemeral=True)
            return

        queue = music_queues[interaction.guild.id]
        
        embed = discord.Embed(
            title="🎵 Music Queue",
            color=discord.Color.blue()
        )

        if queue.current:
            embed.add_field(
                name="🎵 Now Playing",
                value=f"**{queue.current.title}**\nRequested by: {queue.current.requester.mention if queue.current.requester else 'Unknown'}",
                inline=False
            )

        if queue.queue:
            queue_text = ""
            for i, song in enumerate(queue.queue[:10], 1):  # Show first 10 songs
                queue_text += f"{i}. **{song.title}** - {song.requester.mention if song.requester else 'Unknown'}\n"
            
            if len(queue.queue) > 10:
                queue_text += f"\n... and {len(queue.queue) - 10} more songs"
            
            embed.add_field(
                name=f"📝 Up Next ({len(queue.queue)} songs)",
                value=queue_text,
                inline=False
            )
        else:
            if not queue.current:
                embed.add_field(
                    name="📝 Queue Status",
                    value="Queue is empty. Use `/dotgen_play` to add songs!",
                    inline=False
                )

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="dotgen_volume", description="Change music volume", guild=guild_obj)
    @app_commands.describe(volume="Volume level (0-100)")
    async def slash_volume(interaction: discord.Interaction, volume: int):
        """Slash command to change music volume"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You need to be in a voice channel to use music commands!", ephemeral=True)
            return

        if volume < 0 or volume > 100:
            await interaction.response.send_message("❌ Volume must be between 0 and 100!", ephemeral=True)
            return

        voice_client = interaction.guild.voice_client
        if not voice_client:
            await interaction.response.send_message("❌ I'm not connected to any voice channel!", ephemeral=True)
            return

        # Update volume
        volume_decimal = volume / 100
        if interaction.guild.id in music_queues:
            music_queues[interaction.guild.id].volume = volume_decimal

        if voice_client.source:
            voice_client.source.volume = volume_decimal

        embed = discord.Embed(
            title="🔊 Volume Changed",
            description=f"Volume set to **{volume}%**",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="dotgen_disconnect", description="Disconnect from voice channel", guild=guild_obj)
    async def slash_disconnect(interaction: discord.Interaction):
        """Slash command to disconnect from voice channel"""
        voice_client = interaction.guild.voice_client
        if not voice_client:
            await interaction.response.send_message("❌ I'm not connected to any voice channel!", ephemeral=True)
            return

        # Clear queue and disconnect
        if interaction.guild.id in music_queues:
            music_queues[interaction.guild.id].clear()
            del music_queues[interaction.guild.id]

        if interaction.guild.id in voice_clients:
            del voice_clients[interaction.guild.id]

        await voice_client.disconnect()
        
        embed = discord.Embed(
            title="👋 Disconnected",
            description="Disconnected from voice channel and cleared queue.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="dotgen_shuffle", description="Toggle shuffle mode for the queue", guild=guild_obj)
    async def slash_shuffle(interaction: discord.Interaction):
        """Slash command to toggle shuffle mode"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You need to be in a voice channel to use music commands!", ephemeral=True)
            return

        if interaction.guild.id not in music_queues:
            await interaction.response.send_message("❌ No music queue found!", ephemeral=True)
            return

        queue = music_queues[interaction.guild.id]
        queue.shuffle_enabled = not queue.shuffle_enabled
        
        if queue.shuffle_enabled:
            queue.shuffle()
            embed = discord.Embed(
                title="🔀 Shuffle Enabled",
                description="Queue has been shuffled and shuffle mode is now ON.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="🔀 Shuffle Disabled",
                description="Shuffle mode is now OFF. Songs will play in order.",
                color=discord.Color.orange()
            )
        
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="dotgen_loop", description="Toggle loop mode (current song or queue)", guild=guild_obj)
    @app_commands.describe(mode="Loop mode: 'song' for current song, 'queue' for entire queue, 'off' to disable")
    async def slash_loop(interaction: discord.Interaction, mode: str = "song"):
        """Slash command to toggle loop modes"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You need to be in a voice channel to use music commands!", ephemeral=True)
            return

        if interaction.guild.id not in music_queues:
            await interaction.response.send_message("❌ No music queue found!", ephemeral=True)
            return

        queue = music_queues[interaction.guild.id]
        mode = mode.lower()
        
        if mode == "song":
            queue.loop = True
            queue.loop_queue = False
            embed = discord.Embed(
                title="🔂 Loop Song",
                description="Current song will loop until disabled.",
                color=discord.Color.blue()
            )
        elif mode == "queue":
            queue.loop = False
            queue.loop_queue = True
            embed = discord.Embed(
                title="🔁 Loop Queue",
                description="Entire queue will loop when finished.",
                color=discord.Color.blue()
            )
        elif mode == "off":
            queue.loop = False
            queue.loop_queue = False
            embed = discord.Embed(
                title="➡️ Loop Disabled",
                description="Loop mode has been turned off.",
                color=discord.Color.orange()
            )
        else:
            await interaction.response.send_message("❌ Invalid mode! Use 'song', 'queue', or 'off'.", ephemeral=True)
            return
        
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="dotgen_previous", description="Play the previous song", guild=guild_obj)
    async def slash_previous(interaction: discord.Interaction):
        """Slash command to play previous song"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You need to be in a voice channel to use music commands!", ephemeral=True)
            return

        voice_client = interaction.guild.voice_client
        if not voice_client:
            await interaction.response.send_message("❌ I'm not connected to any voice channel!", ephemeral=True)
            return

        if interaction.guild.id not in music_queues:
            await interaction.response.send_message("❌ No music queue found!", ephemeral=True)
            return

        queue = music_queues[interaction.guild.id]
        previous_song = queue.previous()
        
        if previous_song:
            voice_client.stop()  # This will trigger the next song to play
            embed = discord.Embed(
                title="⏮️ Playing Previous",
                description=f"**{previous_song.title}**",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ No previous song in history!", ephemeral=True)

    @bot.tree.command(name="dotgen_remove", description="Remove a song from the queue", guild=guild_obj)
    @app_commands.describe(position="Position of the song to remove (1-based)")
    async def slash_remove(interaction: discord.Interaction, position: int):
        """Slash command to remove a song from queue"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You need to be in a voice channel to use music commands!", ephemeral=True)
            return

        if interaction.guild.id not in music_queues:
            await interaction.response.send_message("❌ No music queue found!", ephemeral=True)
            return

        queue = music_queues[interaction.guild.id]
        
        if position < 1 or position > len(queue.queue):
            await interaction.response.send_message(f"❌ Invalid position! Queue has {len(queue.queue)} songs.", ephemeral=True)
            return

        removed_song = queue.remove_song(position - 1)
        if removed_song:
            embed = discord.Embed(
                title="🗑️ Song Removed",
                description=f"Removed **{removed_song.title}** from position {position}",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to remove song!", ephemeral=True)

    @bot.tree.command(name="dotgen_move", description="Move a song to a different position in queue", guild=guild_obj)
    @app_commands.describe(from_pos="Current position of the song", to_pos="New position for the song")
    async def slash_move(interaction: discord.Interaction, from_pos: int, to_pos: int):
        """Slash command to move a song in the queue"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You need to be in a voice channel to use music commands!", ephemeral=True)
            return

        if interaction.guild.id not in music_queues:
            await interaction.response.send_message("❌ No music queue found!", ephemeral=True)
            return

        queue = music_queues[interaction.guild.id]
        
        if from_pos < 1 or from_pos > len(queue.queue) or to_pos < 1 or to_pos > len(queue.queue):
            await interaction.response.send_message(f"❌ Invalid positions! Queue has {len(queue.queue)} songs.", ephemeral=True)
            return

        if queue.move_song(from_pos - 1, to_pos - 1):
            embed = discord.Embed(
                title="↔️ Song Moved",
                description=f"Moved song from position {from_pos} to position {to_pos}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to move song!", ephemeral=True)

    @bot.tree.command(name="dotgen_nowplaying", description="Show currently playing song with progress", guild=guild_obj)
    async def slash_nowplaying(interaction: discord.Interaction):
        """Slash command to show now playing with detailed info"""
        voice_client = interaction.guild.voice_client
        if not voice_client or not voice_client.is_playing():
            await interaction.response.send_message("❌ Nothing is currently playing!", ephemeral=True)
            return

        if interaction.guild.id not in music_queues:
            await interaction.response.send_message("❌ No music queue found!", ephemeral=True)
            return

        queue = music_queues[interaction.guild.id]
        current = queue.current
        
        if not current:
            await interaction.response.send_message("❌ No current song information available!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{current.title}**",
            color=discord.Color.green()
        )
        
        if current.requester:
            embed.add_field(name="Requested by", value=current.requester.mention, inline=True)
        
        if current.duration:
            mins, secs = divmod(current.duration, 60)
            embed.add_field(name="Duration", value=f"{mins}:{secs:02d}", inline=True)
        
        # Queue info
        queue_info = queue.get_queue_info()
        embed.add_field(name="Volume", value=f"{queue_info['volume']}%", inline=True)
        embed.add_field(name="Queue Length", value=str(queue_info['queue_length']), inline=True)
        
        # Loop status
        loop_status = "🔂 Song" if queue.loop else "🔁 Queue" if queue.loop_queue else "➡️ Off"
        embed.add_field(name="Loop", value=loop_status, inline=True)
        embed.add_field(name="Shuffle", value="🔀 On" if queue.shuffle_enabled else "📝 Off", inline=True)
        
        if current.url:
            embed.add_field(name="Source", value=f"[YouTube Link]({current.url})", inline=False)
        
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="dotgen_search", description="Search for songs without playing immediately", guild=guild_obj)
    @app_commands.describe(query="Search query for songs")
    async def slash_search(interaction: discord.Interaction, query: str):
        """Slash command to search for songs and show results"""
        await interaction.response.defer()
        
        try:
            # Search for multiple results
            loop = asyncio.get_event_loop()
            search_query = f"ytsearch5:{query}"  # Search for 5 results
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search_query, download=False))
            
            if not data or 'entries' not in data or not data['entries']:
                await interaction.followup.send("❌ No results found for your search!")
                return
            
            embed = discord.Embed(
                title="🔍 Search Results",
                description=f"Search results for: **{query}**",
                color=discord.Color.blue()
            )
            
            for i, entry in enumerate(data['entries'][:5], 1):
                title = entry.get('title', 'Unknown Title')
                duration = entry.get('duration')
                uploader = entry.get('uploader', 'Unknown')
                
                duration_str = "Unknown"
                if duration:
                    mins, secs = divmod(duration, 60)
                    duration_str = f"{mins}:{secs:02d}"
                
                embed.add_field(
                    name=f"{i}. {title[:50]}{'...' if len(title) > 50 else ''}",
                    value=f"**Duration:** {duration_str} | **Uploader:** {uploader[:30]}",
                    inline=False
                )
            
            embed.set_footer(text="Use /dotgen_play <song name> to add songs to queue")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Search failed: {e}")

    async def join_voice_channel_for_music(interaction):
        """Join the voice channel for music commands"""
        channel = interaction.user.voice.channel
        
        # Check if bot is already connected to voice
        if interaction.guild.voice_client:
            if interaction.guild.voice_client.channel == channel:
                return interaction.guild.voice_client
            else:
                await interaction.guild.voice_client.move_to(channel)
                return interaction.guild.voice_client
        
        # Connect to voice channel
        try:
            voice_client = await channel.connect()
            voice_clients[interaction.guild.id] = voice_client
            return voice_client
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to connect to voice channel: {e}")
            return None

else:
    # Add disabled music commands when youtube-dl is not available
    @bot.tree.command(name="dotgen_play", description="Play music from YouTube (DISABLED - requires yt-dlp)", guild=guild_obj)
    async def slash_play_disabled(interaction: discord.Interaction, query: str):
        await interaction.response.send_message(
            "❌ Music functionality is disabled. Please install yt-dlp:\n```pip install yt-dlp```", 
            ephemeral=True
        )

# =============================================================================
# END MUSIC SLASH COMMANDS
# =============================================================================

# =============================================================================
# END SLASH COMMANDS
# =============================================================================

# Bot configuration
if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token:")
        print("DISCORD_TOKEN=your_bot_token_here")
        sys.exit(1)
    else:
        print("🤖 Starting DOTGEN.AI Discord Bot...")
        print("📋 Configuration loaded:")
        print(f"   - Welcome Channel ID: {WELCOME_CHANNEL_ID or 'Not set'}")
        print(f"   - Lobby Voice Channel ID: {LOBBY_VOICE_CHANNEL_ID or 'Not set'}")
        print(f"   - Voice Log Channel ID: {VOICE_LOG_CHANNEL_ID or 'Not set'}")
        print(f"   - Voice Category ID: {VOICE_CATEGORY_ID or 'Not set'}")
        print(f"   - Guild ID: {GUILD_ID or 'Not set'}")
        print(f"   - Default Role ID: {DEFAULT_ROLE_ID or 'Not set'}")
        print(f"   - Allowed Roles: {len(ALLOWED_ROLES)} role(s) configured" if ALLOWED_ROLES else "   - Allowed Roles: All users allowed")
        print(f"   - Bot Prefix: {BOT_PREFIX}")
        print(f"   - Max Voice Limit: {MAX_VOICE_LIMIT}")
        print()        
        if not privileged_intents_available:
            print("⚠️  RUNNING IN LIMITED MODE:")
            print("   - No automatic member join detection")
            print(f"   - Use {BOT_PREFIX}welcome @member for welcome messages")
            print("   - Voice channels work normally")
            print()
        
        try:
            # Start the webserver for 24/7 keepalive (if Flask is available)
            webserver_started = start_webserver()
            if webserver_started:
                print("🌐 Webserver started for 24/7 operation")
            else:
                print("⚠️  Running without webserver - bot may sleep on some cloud platforms")
            
            # Start the bot
            bot.run(TOKEN)
        except discord.errors.PrivilegedIntentsRequired:
            print("\n❌ PRIVILEGED INTENTS ERROR!")
            print("🔧 To fix this, go to:")
            print("   1. https://discord.com/developers/applications/")
            print("   2. Select your bot application")
            print("   3. Go to the 'Bot' section")
            print("   4. Enable these Privileged Gateway Intents:")
            print("      ✅ SERVER MEMBERS INTENT")
            print("      ✅ MESSAGE CONTENT INTENT")
            print("   5. Save changes and restart the bot")
            print()
            print("🆘 Alternative: The bot will automatically run in limited mode")
            print("   if privileged intents are not available.")
            sys.exit(1)
        except discord.errors.LoginFailure:
            print("\n❌ LOGIN FAILED!")
            print("🔧 Check that your bot token is correct in the .env file")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR: {e}")
            print("🔧 Please check your internet connection and try again")
            sys.exit(1)


