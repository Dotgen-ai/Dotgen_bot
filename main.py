import discord
from discord.ext import commands
import asyncio
import random
import os
from dotenv import load_dotenv

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
BOT_PREFIX = os.getenv('BOT_PREFIX', '!')
MAX_VOICE_LIMIT = int(os.getenv('MAX_VOICE_CHANNEL_LIMIT', 10))

# Parse allowed roles from environment variable
ALLOWED_ROLES = []
if os.getenv('ALLOWED_ROLES'):
    try:
        ALLOWED_ROLES = [int(role_id.strip()) for role_id in os.getenv('ALLOWED_ROLES').split(',') if role_id.strip()]
    except ValueError:
        print("⚠️  Invalid ALLOWED_ROLES format in .env file. Should be comma-separated role IDs.")

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
# Only enable privileged intents if they're available
try:
    intents.members = True
    intents.voice_states = True
except:
    print("⚠️  Privileged intents not available, some features may be limited")

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

# Store temporary voice channels for cleanup
temp_voice_channels = {}

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

@bot.event
async def on_ready():
    print(f'✅ {bot.user} has connected to Discord!')
    print(f'📊 Bot is in {len(bot.guilds)} guild(s)')
    
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
    
    # Set bot status
    try:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name="for new members 👀"
            )
        )
        print("✅ Bot status set successfully")
    except Exception as e:
        print(f"⚠️  Could not set bot status: {e}")
    
    print("🚀 Bot is ready to use!")
    print("💡 Use !config_status to check your configuration")
    print("💡 Use !get_ids to get channel IDs for your .env file")

@bot.event
async def on_member_join(member):
    """Send a unique welcome message when a new member joins"""
    try:
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
                
                # If no common channel found, use the first available text channel
                if not welcome_channel and member.guild.text_channels:
                    welcome_channel = member.guild.text_channels[0]
        
        if welcome_channel:
            # Select a random welcome message
            welcome_msg = random.choice(WELCOME_MESSAGES).format(member=member.mention)
            
            # Create a welcome embed
            embed = discord.Embed(
                title="🎉 New Member Alert!",
                description=welcome_msg,
                color=discord.Color.gold()
            )
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
            
            await welcome_channel.send(embed=embed)
            
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
            
    except Exception as e:
        print(f"Error in voice state update: {e}")

async def handle_voice_channel_creation(member, lobby_channel):
    """Create a new voice channel based on the member's highest role"""
    try:
        guild = member.guild
        
        # Get the member's highest role (excluding @everyone)
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
        
        # Store the channel for cleanup
        temp_voice_channels[new_channel.id] = {
            'channel': new_channel,
            'creator': member.id,
            'role': role_name
        }
        
        # Send a notification to welcome channel or system channel
        notification_channel = None
        if WELCOME_CHANNEL_ID:
            notification_channel = bot.get_channel(WELCOME_CHANNEL_ID)
        if not notification_channel and guild.system_channel:
            notification_channel = guild.system_channel
            
        if notification_channel:
            embed = discord.Embed(
                title="🎤 Voice Channel Created!",
                description=f"{member.mention} created a new voice channel: **{channel_name}**",
                color=highest_role.color if highest_role else discord.Color.blue()
            )
            await notification_channel.send(embed=embed, delete_after=30)
            
    except Exception as e:
        print(f"Error creating voice channel: {e}")

async def handle_voice_channel_cleanup(channel):
    """Clean up empty temporary voice channels"""
    try:
        # Check if the channel is empty
        if len(channel.members) == 0:
            channel_info = temp_voice_channels.get(channel.id)
            if channel_info:
                await channel.delete()
                del temp_voice_channels[channel.id]
                print(f"Deleted empty voice channel: {channel.name}")
                
    except Exception as e:
        print(f"Error cleaning up voice channel: {e}")

# Commands for managing the bot
@bot.command(name='setup_lobby')
@commands.has_permissions(administrator=True)
async def setup_lobby(ctx, category_name: str = "Voice Channels"):
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

@bot.command(name='get_ids')
@commands.has_permissions(administrator=True)
async def get_ids(ctx, channel_mention=None):
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
        if channel_mention:
            try:
                # Try to convert the mention to a channel
                channel = await commands.TextChannelConverter().convert(ctx, channel_mention)
                embed.add_field(
                    name="🔗 Mentioned Channel ID",
                    value=f"`{channel.id}`",
                    inline=True
                )
            except:
                pass
        
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

@bot.command(name='config_status')
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
        
        # Other settings
        embed.add_field(
            name="🔧 Other Settings",
            value=f"**Prefix:** `{BOT_PREFIX}`\n**Voice Limit:** {MAX_VOICE_LIMIT}",
            inline=True
        )
        
        embed.set_footer(text="Use !get_ids to get channel/server IDs for your .env file")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error checking configuration: {e}")

@bot.command(name='welcome_test')
@commands.has_permissions(administrator=True)
async def test_welcome(ctx, member: discord.Member = None):
    """Test the welcome message system"""
    if not member:
        member = ctx.author
    
    # Simulate the welcome event
    await on_member_join(member)
    await ctx.send(f"✅ Sent test welcome message for {member.mention}")

@bot.command(name='cleanup_channels')
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

@bot.command(name='bot_info')
async def bot_info(ctx):
    """Display bot information and features"""
    embed = discord.Embed(
        title="🤖 Bot Information",
        description="Welcome to the XRP Discord Bot!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🎉 Welcome System",
        value="Sends unique welcome messages when new members join",
        inline=False
    )
    
    embed.add_field(
        name="🎤 Dynamic Voice Channels",
        value="Join the 'Join to Create' channel to create role-based temporary voice channels",
        inline=False
    )
    
    embed.add_field(
        name="📊 Stats",
        value=f"**Servers:** {len(bot.guilds)}\n**Temp Channels:** {len(temp_voice_channels)}",
        inline=True
    )
    
    embed.add_field(
        name="🛠️ Admin Commands",
        value=f"`{BOT_PREFIX}setup_lobby` - Setup voice channel lobby\n`{BOT_PREFIX}cleanup_channels` - Clean empty channels\n`{BOT_PREFIX}welcome_test` - Test welcome message\n`{BOT_PREFIX}get_ids` - Get channel/server IDs\n`{BOT_PREFIX}config_status` - Check configuration",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore unknown commands
    else:
        await ctx.send(f"❌ An error occurred: {error}")

# Run the bot
if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token:")
        print("DISCORD_TOKEN=your_bot_token_here")
        input("Press Enter to exit...")
    else:
        print("🤖 Starting XRP Discord Bot...")
        print("📋 Configuration loaded:")
        print(f"   - Welcome Channel ID: {WELCOME_CHANNEL_ID or 'Not set'}")
        print(f"   - Lobby Voice Channel ID: {LOBBY_VOICE_CHANNEL_ID or 'Not set'}")
        print(f"   - Voice Category ID: {VOICE_CATEGORY_ID or 'Not set'}")
        print(f"   - Guild ID: {GUILD_ID or 'Not set'}")
        print(f"   - Default Role ID: {DEFAULT_ROLE_ID or 'Not set'}")
        print(f"   - Bot Prefix: {BOT_PREFIX}")
        print(f"   - Max Voice Limit: {MAX_VOICE_LIMIT}")
        print()
        
        try:
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
            print("🆘 Alternative: You can try running with limited features by")
            print("   commenting out the privileged intents in the code.")
            input("Press Enter to exit...")
        except discord.errors.LoginFailure:
            print("\n❌ LOGIN FAILED!")
            print("🔧 Check that your bot token is correct in the .env file")
            print("   The token should look like: MTM3Mzg3NTk5MTI1NjEwNDk4MA.GP03SZ.eO1PyMnSEFB_vCAw24sbofAdlVQGcYvmL3hTRQ")
            input("Press Enter to exit...")
        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR: {e}")
            print("🔧 Please check your internet connection and try again")
            input("Press Enter to exit...")