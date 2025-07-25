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

# Bot configuration with minimal intents (no privileged intents required)
intents = discord.Intents.default()
intents.message_content = True
# Note: members and voice_states intents are disabled to avoid privileged intent requirements

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
    
    # Set bot status
    try:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name="for commands 👀"
            )
        )
        print("✅ Bot status set successfully")
    except Exception as e:
        print(f"⚠️  Could not set bot status: {e}")
    
    print("🚀 Bot is ready to use!")
    print("💡 Use !config_status to check your configuration")
    print("💡 Use !welcome @member to send welcome messages manually")

# Manual welcome command (since automatic member join detection requires privileged intents)
@bot.command(name='welcome')
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
            
    except Exception as e:
        await ctx.send(f"❌ Error sending welcome message: {e}")

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
        channel_name = f"{role_name} - {member.display_name}'s VC"
        
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
        
        embed.set_footer(text="Use !get_ids to get channel/server IDs for your .env file")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error checking configuration: {e}")

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

@bot.command(name='add_role')
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

@bot.command(name='remove_role')
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

@bot.command(name='list_roles')
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
        
        embed.set_footer(text="Use !add_role @role to add roles or !remove_role @role to remove roles")
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error listing roles: {e}")

@bot.command(name='voice_stats')
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

@bot.command(name='bot_info')
async def bot_info(ctx):
    """Display bot information and features"""
    embed = discord.Embed(
        title="🤖 Bot Information",
        description="Welcome to the XRP Discord Bot! (Limited Mode)",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🎉 Welcome System",
        value="Use `!welcome @member` to send welcome messages",
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
        value=f"`{BOT_PREFIX}setup_lobby` - Setup voice channel lobby\n`{BOT_PREFIX}cleanup_channels` - Clean empty channels\n`{BOT_PREFIX}welcome @member` - Send welcome message\n`{BOT_PREFIX}get_ids` - Get channel/server IDs\n`{BOT_PREFIX}config_status` - Check configuration\n`{BOT_PREFIX}add_role @role` - Add allowed role\n`{BOT_PREFIX}remove_role @role` - Remove allowed role\n`{BOT_PREFIX}list_roles` - List allowed roles\n`{BOT_PREFIX}voice_stats` - Voice channel statistics",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Limited Mode",
        value="To enable automatic welcome messages, enable privileged intents in Discord Developer Portal",
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
        print("🤖 Starting XRP Discord Bot (Limited Mode)...")
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
        print("⚠️  RUNNING IN LIMITED MODE:")
        print("   - No automatic member join detection")
        print("   - Use !welcome @member for welcome messages")
        print("   - Voice channels work normally")
        print()
        
        try:
            bot.run(TOKEN)
        except discord.errors.LoginFailure:
            print("\n❌ LOGIN FAILED!")
            print("🔧 Check that your bot token is correct in the .env file")
            input("Press Enter to exit...")
        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR: {e}")
            print("🔧 Please check your internet connection and try again")
            input("Press Enter to exit...")
