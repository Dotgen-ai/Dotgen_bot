import discord
from discord.ext import commands
from discord import app_commands
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
BOT_PREFIX = os.getenv('BOT_PREFIX', '/')
MAX_VOICE_LIMIT = int(os.getenv('MAX_VOICE_CHANNEL_LIMIT', 10))

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
    
    # Sync slash commands
    try:
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            synced = await bot.tree.sync(guild=guild)
            print(f"✅ Synced {len(synced)} slash commands to guild {GUILD_ID}")
        else:
            synced = await bot.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands globally")
    except Exception as e:
        print(f"⚠️  Failed to sync slash commands: {e}")
    
    # Check if privileged intents are working
    if privileged_intents_available:
        print("✅ Running with privileged intents - all features available")
        print("   - Automatic welcome messages: ✅ Enabled")
        print("   - Voice channels: ✅ Enabled")    
    else:        
        print("⚠️  Running in LIMITED MODE (no privileged intents)")
        print("   - Welcome messages: Use /welcome command instead of automatic detection")
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
    
    print("🚀 Bot is ready to use!")
    print("💡 Use /config_status to check your configuration")
    if not privileged_intents_available:
        print("💡 Use /welcome @member to send welcome messages manually")

# Manual welcome command (fallback for when privileged intents aren't available)
@bot.tree.command(name="welcome", description="Send a welcome message for a member")
async def manual_welcome(interaction: discord.Interaction, member: discord.Member = None):
    """Send a welcome message for a member"""
    if not member:
        member = interaction.user
    
    try:
        # Get the welcome channel from environment variable first
        welcome_channel = None
        
        if WELCOME_CHANNEL_ID:
            welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
        
        # Fallback to current channel if no specific channel ID is set
        if not welcome_channel:
            welcome_channel = interaction.channel
        
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
            embed.set_footer(text=f"Welcome to {interaction.guild.name}!")
            
            await welcome_channel.send(embed=embed)
            
            if welcome_channel != interaction.channel:
                await interaction.response.send_message(f"✅ Welcome message sent to {welcome_channel.mention} for {member.mention}", ephemeral=True)
            else:
                await interaction.response.send_message("✅ Welcome message sent!", ephemeral=True)
            
    except Exception as e:
        await interaction.response.send_message(f"❌ Error sending welcome message: {e}", ephemeral=True)

@bot.event
async def on_member_join(member):
    """Send a unique welcome message when a new member joins (only works with privileged intents)"""
    if not privileged_intents_available:
        return  # Skip if privileged intents aren't available
        
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
        
        # Check if member has required roles (if ALLOWED_ROLES is configured)
        if ALLOWED_ROLES:
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
            'role': role_name,
            'created_at': discord.utils.utcnow()
        }
        
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

# Commands for managing the bot
@bot.tree.command(name="setup_lobby", description="Setup the lobby voice channel for creating temporary channels")
@app_commands.describe(category_name="Name of the category to create the lobby in")
async def setup_lobby(interaction: discord.Interaction, category_name: str = "Voice Channels"):
    """Setup the lobby voice channel for creating temporary channels"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
        
    try:
        guild = interaction.guild
        
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
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error setting up lobby: {e}", ephemeral=True)

@bot.tree.command(name="get_ids", description="Get channel and server IDs for .env configuration")
@app_commands.describe(channel="Optional channel to get the ID for")
async def get_ids(interaction: discord.Interaction, channel: discord.TextChannel = None):
    """Get channel and server IDs for .env configuration"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
        
    try:
        guild = interaction.guild
        
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
            value=f"`{interaction.channel.id}`",
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
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error getting IDs: {e}", ephemeral=True)

@bot.tree.command(name="config_status", description="Check the current configuration status")
async def config_status(interaction: discord.Interaction):
    """Check the current configuration status"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
        
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
            role = interaction.guild.get_role(DEFAULT_ROLE_ID)
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
                role = interaction.guild.get_role(role_id)
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
        
        embed.set_footer(text="Use /get_ids to get channel/server IDs for your .env file")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error checking configuration: {e}", ephemeral=True)

@bot.tree.command(name="bot_info", description="Display bot information and features")
async def bot_info(interaction: discord.Interaction):
    """Display bot information and features"""
    embed = discord.Embed(
        title="🤖 Bot Information",
        description=f"Welcome to the XRP Discord Bot!{' (Limited Mode)' if not privileged_intents_available else ''}",
        color=discord.Color.blue()
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
            value="Use `/welcome @member` to send welcome messages",
            inline=False
        )
    
    embed.add_field(
        name="🎤 Dynamic Voice Channels",
        value="Join the 'Join to Create' channel to create role-based temporary voice channels",
        inline=False
    )
    
    embed.add_field(        name="📊 Stats",
        value=f"**Servers:** {len(bot.guilds)}\n**Temp Channels:** {len(temp_voice_channels)}",
        inline=True
    )
    
    admin_commands = [
        "`/setup_lobby` - Setup voice channel lobby",
        "`/cleanup_channels` - Clean empty channels",
        "`/welcome @member` - Send welcome message",
        "`/get_ids` - Get channel/server IDs",
        "`/config_status` - Check configuration",
        "`/add_role @role` - Add allowed role",
        "`/remove_role @role` - Remove allowed role",
        "`/list_roles` - List allowed roles",
        "`/voice_stats` - Voice channel statistics",
        "`/send_message` - Send message to any channel",
        "`/announce` - Send announcement to multiple channels",
        "`/echo` - Make bot repeat a message",        "`/forward_message` - Forward message between channels",
        "`/copy_last_message` - Copy recent messages",
        "`/mirror_channel` - Set up automatic mirroring",
        "`/get_message_id` - Get message IDs for forwarding"
    ]
    
    embed.add_field(
        name="🛠️ Admin Commands",
        value="\n".join(admin_commands),
        inline=False
    )
    
    if not privileged_intents_available:
        embed.add_field(
            name="⚠️ Limited Mode",
            value="To enable automatic welcome messages, enable privileged intents in Discord Developer Portal",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="add_role", description="Add a role to the allowed roles list for voice channel creation")
@app_commands.describe(role="The role to add to the allowed list")
async def add_allowed_role(interaction: discord.Interaction, role: discord.Role):
    """Add a role to the allowed roles list for voice channel creation"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
        
    try:
        global ALLOWED_ROLES
        
        if role.id in ALLOWED_ROLES:
            await interaction.response.send_message(f"❌ Role @{role.name} is already in the allowed roles list.", ephemeral=True)
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
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error adding role: {e}", ephemeral=True)

@bot.tree.command(name="remove_role", description="Remove a role from the allowed roles list for voice channel creation")
@app_commands.describe(role="The role to remove from the allowed list")
async def remove_allowed_role(interaction: discord.Interaction, role: discord.Role):
    """Remove a role from the allowed roles list for voice channel creation"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
        
    try:
        global ALLOWED_ROLES
        
        if role.id not in ALLOWED_ROLES:
            await interaction.response.send_message(f"❌ Role @{role.name} is not in the allowed roles list.", ephemeral=True)
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
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error removing role: {e}", ephemeral=True)

@bot.tree.command(name="list_roles", description="List all allowed roles for voice channel creation")
async def list_allowed_roles(interaction: discord.Interaction):
    """List all allowed roles for voice channel creation"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
        
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
                role = interaction.guild.get_role(role_id)
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
        
        embed.set_footer(text="Use /add_role @role to add roles or /remove_role @role to remove roles")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error listing roles: {e}", ephemeral=True)

@bot.tree.command(name="voice_stats", description="Show voice channel statistics")
async def voice_stats(interaction: discord.Interaction):
    """Show voice channel statistics"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
        
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
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error getting stats: {e}", ephemeral=True)

@bot.tree.command(name="cleanup_channels", description="Clean up all empty temporary voice channels")
async def cleanup_channels(interaction: discord.Interaction):
    """Clean up all empty temporary voice channels"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
        
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
    
    await interaction.response.send_message(f"✅ Cleaned up {cleaned} empty voice channels.", ephemeral=True)

@bot.tree.command(name="send_message", description="Send a message from the bot to any channel")
@app_commands.describe(
    channel="The channel to send the message to",
    message="The message content to send",
    embed_title="Optional: Title for an embed message",
    embed_color="Optional: Color for embed (red, green, blue, orange, purple, gold)"
)
async def send_message(
    interaction: discord.Interaction, 
    channel: discord.TextChannel, 
    message: str,
    embed_title: str = None,
    embed_color: str = None
):
    """Send a message from the bot to any channel"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    try:
        # Check if bot has permission to send messages in the target channel
        if not channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message(f"❌ I don't have permission to send messages in {channel.mention}", ephemeral=True)
            return
        
        # If embed parameters are provided, create an embed
        if embed_title or embed_color:
            # Set embed color
            color_map = {
                "red": discord.Color.red(),
                "green": discord.Color.green(),
                "blue": discord.Color.blue(),
                "orange": discord.Color.orange(),
                "purple": discord.Color.purple(),
                "gold": discord.Color.gold(),
                "yellow": discord.Color.yellow(),
                "dark_blue": discord.Color.dark_blue(),
                "dark_green": discord.Color.dark_green(),
                "dark_red": discord.Color.dark_red()
            }
            
            selected_color = color_map.get(embed_color.lower() if embed_color else "", discord.Color.blue())
            
            embed = discord.Embed(
                title=embed_title or "📢 Announcement",
                description=message,
                color=selected_color
            )
            embed.set_footer(text=f"Sent by {interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            
            await channel.send(embed=embed)
            await interaction.response.send_message(f"✅ Embed message sent to {channel.mention}", ephemeral=True)
        else:
            # Send regular message
            await channel.send(message)
            await interaction.response.send_message(f"✅ Message sent to {channel.mention}", ephemeral=True)
            
    except Exception as e:
        await interaction.response.send_message(f"❌ Error sending message: {e}", ephemeral=True)

@bot.tree.command(name="announce", description="Send an announcement to multiple channels")
@app_commands.describe(
    message="The announcement message",
    channels="Channels to send to (mention them, e.g., #general #announcements)",
    embed_title="Optional: Title for the announcement embed",
    ping_role="Optional: Role to ping in the announcement"
)
async def announce(
    interaction: discord.Interaction,
    message: str,
    channels: str = None,
    embed_title: str = None,
    ping_role: discord.Role = None
):
    """Send an announcement to multiple channels"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    try:
        # Parse channel mentions or use default announcement channels
        target_channels = []
        
        if channels:
            # Extract channel IDs from mentions
            import re
            channel_ids = re.findall(r'<#(\d+)>', channels)
            for channel_id in channel_ids:
                channel = interaction.guild.get_channel(int(channel_id))
                if channel and isinstance(channel, discord.TextChannel):
                    target_channels.append(channel)
        
        # If no channels specified, look for common announcement channels
        if not target_channels:
            for channel in interaction.guild.text_channels:
                if channel.name.lower() in ['announcements', 'announcement', 'general', 'news']:
                    target_channels.append(channel)
        
        # If still no channels found, use current channel
        if not target_channels:
            target_channels = [interaction.channel]
        
        # Create announcement embed
        embed = discord.Embed(
            title=embed_title or "📢 Server Announcement",
            description=message,
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Announced by {interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        # Add role ping if specified
        content = ping_role.mention if ping_role else None
        
        sent_count = 0
        failed_channels = []
        
        for channel in target_channels:
            try:
                if channel.permissions_for(interaction.guild.me).send_messages:
                    await channel.send(content=content, embed=embed)
                    sent_count += 1
                else:
                    failed_channels.append(channel.name)
            except Exception as e:
                failed_channels.append(f"{channel.name} (Error: {str(e)[:50]})")
        
        # Send response
        response_msg = f"✅ Announcement sent to {sent_count} channel(s)"
        if failed_channels:
            response_msg += f"\n⚠️ Failed to send to: {', '.join(failed_channels)}"
        
        await interaction.response.send_message(response_msg, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error sending announcement: {e}", ephemeral=True)

@bot.tree.command(name="echo", description="Make the bot repeat a message in the current channel")
@app_commands.describe(
    message="The message for the bot to say",
    delete_original="Whether to delete your command message (default: True)"
)
async def echo(interaction: discord.Interaction, message: str, delete_original: bool = True):
    """Make the bot repeat a message in the current channel"""
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ You need 'Manage Messages' permission to use this command.", ephemeral=True)
        return
    
    try:
        # Send the message
        await interaction.response.send_message(message)
        
        # If delete_original is False, send a confirmation
        if not delete_original:
            await interaction.followup.send("✅ Message sent!", ephemeral=True)
            
    except Exception as e:
        await interaction.response.send_message(f"❌ Error sending message: {e}", ephemeral=True)

@bot.tree.command(name="forward_message", description="Forward a message from one channel to another")
@app_commands.describe(
    source_channel="The channel to get the message from",
    message_id="The ID of the message to forward",
    target_channel="The channel to forward the message to",
    add_source_info="Whether to add info about the original source (default: True)"
)
async def forward_message(
    interaction: discord.Interaction,
    source_channel: discord.TextChannel,
    message_id: str,
    target_channel: discord.TextChannel,
    add_source_info: bool = True
):
    """Forward a specific message from one channel to another"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    try:
        # Check if bot has permission to read source channel
        if not source_channel.permissions_for(interaction.guild.me).read_messages:
            await interaction.response.send_message(f"❌ I don't have permission to read messages in {source_channel.mention}", ephemeral=True)
            return
            
        # Check if bot has permission to send to target channel
        if not target_channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message(f"❌ I don't have permission to send messages in {target_channel.mention}", ephemeral=True)
            return
        
        # Get the message to forward
        try:
            message = await source_channel.fetch_message(int(message_id))
        except ValueError:
            await interaction.response.send_message("❌ Invalid message ID. Make sure it's a valid number.", ephemeral=True)
            return
        except discord.NotFound:
            await interaction.response.send_message(f"❌ Message not found in {source_channel.mention}. Check the message ID.", ephemeral=True)
            return
        
        # Create forwarded message
        if message.embeds:
            # If original message has embeds, forward them
            for embed in message.embeds:
                if add_source_info:
                    # Add source information to the embed
                    if embed.footer.text:
                        embed.set_footer(text=f"{embed.footer.text} • Forwarded from #{source_channel.name}")
                    else:
                        embed.set_footer(text=f"Forwarded from #{source_channel.name}")
                
                await target_channel.send(embed=embed)
        
        # Forward text content if exists
        if message.content:
            content = message.content
            
            if add_source_info:
                content += f"\n\n*— Forwarded from {source_channel.mention}*"
            
            await target_channel.send(content)
        
        # Forward attachments if any
        if message.attachments:
            attachment_info = f"📎 **Attachments from {source_channel.mention}:**\n"
            for attachment in message.attachments:
                attachment_info += f"• [{attachment.filename}]({attachment.url})\n"
            await target_channel.send(attachment_info)
        
        await interaction.response.send_message(
            f"✅ Message forwarded from {source_channel.mention} to {target_channel.mention}", 
            ephemeral=True
        )
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error forwarding message: {e}", ephemeral=True)

@bot.tree.command(name="copy_last_message", description="Copy the last message from one channel to another")
@app_commands.describe(
    source_channel="The channel to copy the last message from",
    target_channel="The channel to copy the message to",
    message_count="Number of recent messages to copy (default: 1, max: 5)"
)
async def copy_last_message(
    interaction: discord.Interaction,
    source_channel: discord.TextChannel,
    target_channel: discord.TextChannel,
    message_count: int = 1
):
    """Copy the last message(s) from one channel to another"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    if message_count > 5:
        await interaction.response.send_message("❌ You can only copy up to 5 messages at once.", ephemeral=True)
        return
    
    try:
        # Check permissions
        if not source_channel.permissions_for(interaction.guild.me).read_messages:
            await interaction.response.send_message(f"❌ I don't have permission to read messages in {source_channel.mention}", ephemeral=True)
            return
            
        if not target_channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message(f"❌ I don't have permission to send messages in {target_channel.mention}", ephemeral=True)
            return
        
        # Get recent messages
        messages = []
        async for message in source_channel.history(limit=message_count):
            if not message.author.bot or message.author == interaction.guild.me:  # Skip other bots but allow our own bot
                messages.append(message)
            if len(messages) >= message_count:
                break
        
        if not messages:
            await interaction.response.send_message(f"❌ No recent messages found in {source_channel.mention}", ephemeral=True)
            return
        
        # Copy messages (reverse to maintain chronological order)
        copied_count = 0
        for message in reversed(messages):
            # Copy embeds
            if message.embeds:
                for embed in message.embeds:
                    # Add source info
                    embed.set_footer(text=f"Copied from #{source_channel.name} • {message.created_at.strftime('%m/%d/%Y %H:%M')}")
                    await target_channel.send(embed=embed)
                    copied_count += 1
            
            # Copy text content
            if message.content:
                content = message.content + f"\n\n*— Copied from {source_channel.mention}*"
                await target_channel.send(content)
                copied_count += 1
            
            # Copy attachments info
            if message.attachments:
                attachment_info = f"📎 **Attachments from {source_channel.mention}:**\n"
                for attachment in message.attachments:
                    attachment_info += f"• [{attachment.filename}]({attachment.url})\n"
                await target_channel.send(attachment_info)
        
        await interaction.response.send_message(
            f"✅ Copied {len(messages)} message(s) from {source_channel.mention} to {target_channel.mention}",
            ephemeral=True
        )
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error copying messages: {e}", ephemeral=True)

@bot.tree.command(name="mirror_channel", description="Set up automatic message mirroring between two channels")
@app_commands.describe(
    source_channel="The channel to mirror from",
    target_channel="The channel to mirror to",
    enable="Enable or disable mirroring (True/False)"
)
async def mirror_channel(
    interaction: discord.Interaction,
    source_channel: discord.TextChannel,
    target_channel: discord.TextChannel,
    enable: bool
):
    """Set up automatic message mirroring between two channels"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    try:
        # Initialize mirror settings if not exists
        if not hasattr(bot, 'channel_mirrors'):
            bot.channel_mirrors = {}
        
        if enable:
            # Check permissions
            if not source_channel.permissions_for(interaction.guild.me).read_messages:
                await interaction.response.send_message(f"❌ I don't have permission to read messages in {source_channel.mention}", ephemeral=True)
                return
                
            if not target_channel.permissions_for(interaction.guild.me).send_messages:
                await interaction.response.send_message(f"❌ I don't have permission to send messages in {target_channel.mention}", ephemeral=True)
                return
            
            bot.channel_mirrors[source_channel.id] = target_channel.id
            await interaction.response.send_message(
                f"✅ Mirroring enabled: {source_channel.mention} → {target_channel.mention}",
                ephemeral=True
            )
        else:
            if source_channel.id in bot.channel_mirrors:
                del bot.channel_mirrors[source_channel.id]
                await interaction.response.send_message(
                    f"✅ Mirroring disabled for {source_channel.mention}",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"❌ No mirroring was set up for {source_channel.mention}",
                    ephemeral=True
                )
                
    except Exception as e:
        await interaction.response.send_message(f"❌ Error setting up mirroring: {e}", ephemeral=True)

# Event listener for automatic message mirroring
@bot.event
async def on_message(message):
    """Handle automatic message mirroring"""
    # Skip if message is from a bot (prevent loops)
    if message.author.bot:
        return
    
    # Check if this channel has mirroring enabled
    if hasattr(bot, 'channel_mirrors') and message.channel.id in bot.channel_mirrors:
        target_channel_id = bot.channel_mirrors[message.channel.id]
        target_channel = bot.get_channel(target_channel_id)
        
        if target_channel:
            try:
                # Mirror the message
                content = message.content
                if content:
                    content += f"\n\n*— Mirrored from {message.channel.mention}*"
                    await target_channel.send(content)
                
                # Mirror embeds
                for embed in message.embeds:
                    embed.set_footer(text=f"Mirrored from #{message.channel.name}")
                    await target_channel.send(embed=embed)
                
                # Mirror attachments info
                if message.attachments:
                    attachment_info = f"📎 **Attachments from {message.channel.mention}:**\n"
                    for attachment in message.attachments:
                        attachment_info += f"• [{attachment.filename}]({attachment.url})\n"
                    await target_channel.send(attachment_info)
                    
            except Exception as e:
                print(f"Error mirroring message: {e}")

@bot.tree.command(name="get_message_id", description="Get the message ID of recent messages in a channel")
@app_commands.describe(
    channel="The channel to get message IDs from (default: current channel)",
    count="Number of recent messages to show IDs for (default: 5, max: 10)"
)
async def get_message_id(
    interaction: discord.Interaction,
    channel: discord.TextChannel = None,
    count: int = 5
):
    """Get message IDs from recent messages for easy forwarding"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    if count > 10:
        await interaction.response.send_message("❌ You can only get up to 10 message IDs at once.", ephemeral=True)
        return
    
    target_channel = channel or interaction.channel
    
    try:
        # Check permissions
        if not target_channel.permissions_for(interaction.guild.me).read_messages:
            await interaction.response.send_message(f"❌ I don't have permission to read messages in {target_channel.mention}", ephemeral=True)
            return
        
        # Get recent messages
        messages = []
        async for message in target_channel.history(limit=count):
            messages.append(message)
        
        if not messages:
            await interaction.response.send_message(f"❌ No messages found in {target_channel.mention}", ephemeral=True)
            return
        
        # Create embed with message IDs
        embed = discord.Embed(
            title=f"📋 Recent Message IDs from #{target_channel.name}",
            description="Use these IDs with `/forward_message` command",
            color=discord.Color.blue()
        )
        
        for i, message in enumerate(messages[:count], 1):
            author_name = message.author.display_name
            content_preview = message.content[:50] + "..." if len(message.content) > 50 else message.content
            if not content_preview and message.embeds:
                content_preview = "[Embed Message]"
            elif not content_preview and message.attachments:
                content_preview = f"[{len(message.attachments)} Attachment(s)]"
            elif not content_preview:
                content_preview = "[Empty Message]"
            
            embed.add_field(
                name=f"#{i} - {author_name}",
                value=f"**ID:** `{message.id}`\n**Content:** {content_preview}",
                inline=False
            )
        
        embed.set_footer(text=f"Copy the ID number and use with /forward_message")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error getting message IDs: {e}", ephemeral=True)

# Rotating status activities
ACTIVITIES = [
    {"name": "helping the server 🛠️", "type": discord.ActivityType.playing},
    {"name": "for new members 👀", "type": discord.ActivityType.watching},
    {"name": "server members 👥", "type": discord.ActivityType.watching},
    {"name": "slash commands 💬", "type": discord.ActivityType.listening},
    {"name": "voice channels 🎤", "type": discord.ActivityType.listening},
    {"name": "announcements 📢", "type": discord.ActivityType.watching},
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
            input("Press Enter to exit...")
        except discord.errors.LoginFailure:
            print("\n❌ LOGIN FAILED!")
            print("🔧 Check that your bot token is correct in the .env file")
            input("Press Enter to exit...")
        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR: {e}")
            print("🔧 Please check your internet connection and try again")
            input("Press Enter to exit...")