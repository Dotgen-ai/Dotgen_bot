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
        value="\n".join(sorted(general_cmds)) if general_cmds else "None available",
        inline=False
    )
    
    embed.add_field(
        name="🛠️ Admin Commands",
        value="\n".join(sorted(admin_cmds)) if admin_cmds else "None available",
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
        value="`/dotgen_help` - Complete help & command list\n`/dotgen_info` - Bot information\n`/dotgen_ping` - Check bot status\n`/dotgen_config` - View configuration\n`/dotgen_welcome` - Send welcome message",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Quick Start",
        value="1. Type `/` in chat\n2. Look for `dotgen_` commands\n3. Use `/dotgen_help` for complete list\n4. Tab completion shows all options!",
        inline=False
    )
    
    # Show limited prefix commands that still exist
    prefix_cmds = [cmd.name for cmd in bot.commands if cmd.name not in ['help', 'bot_info']]
    if prefix_cmds:
        embed.add_field(
            name="⚠️ Legacy Prefix Commands",
            value=f"Some admin commands still use `{BOT_PREFIX}` prefix, but **slash commands are recommended**.\nUse `/dotgen_help` for the complete list.",
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

# Rotating status activities
ACTIVITIES = [
    {"name": "DOTGEN.AI server 🛠️", "type": discord.ActivityType.watching},
    {"name": "for new members 👀", "type": discord.ActivityType.watching},
    {"name": "DOTGEN.AI community 👥", "type": discord.ActivityType.watching},
    {"name": f"{BOT_PREFIX} commands 💬", "type": discord.ActivityType.listening},
    {"name": "voice channels 🎤", "type": discord.ActivityType.listening},
    {"name": "DOTGEN.AI announcements 📢", "type": discord.ActivityType.watching},
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
        value="• Auto Welcome Messages\n• Dynamic Voice Channels\n• Admin Management Tools\n• 24/7 Uptime Monitoring\n• Role-Based Access Control",
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

@bot.tree.command(name="dotgen_announce", description="Send an announcement to a specific channel", guild=guild_obj)
@app_commands.describe(channel="The channel to send the announcement to", message="The announcement message")
async def slash_announce(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    """Slash command to send announcements"""
    # Check permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    try:
        # Check if bot has permission to send messages in the target channel
        if not channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message(f"❌ I don't have permission to send messages in {channel.mention}", ephemeral=True)
            return
        
        # Create announcement embed
        embed = discord.Embed(
            title="📢 Server Announcement",
            description=message,
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Announced by {interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        # Send the announcement
        await channel.send(embed=embed)
        
        # Confirm to the user
        await interaction.response.send_message(f"✅ Announcement sent to {channel.mention}", ephemeral=True)
        
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
            if len(desc) > 60:
                desc = desc[:57] + "..."
            cmd_info += f" - {desc}"
        slash_cmds.append(cmd_info)
    
    if slash_cmds:
        # Split into chunks if too many commands
        chunks = [slash_cmds[i:i+8] for i in range(0, len(slash_cmds), 8)]
        for i, chunk in enumerate(chunks[:3]):  # Show up to 3 chunks
            title = "⚡ Primary Slash Commands" if i == 0 else f"⚡ More Slash Commands ({i+1})"
            embed.add_field(name=title, value="\n".join(chunk), inline=False)
    
    # Show essential commands prominently
    embed.add_field(
        name="🎯 Most Important Commands",
        value="`/dotgen_info` - Bot information & features\n`/dotgen_ping` - Check bot status\n`/dotgen_config` - View configuration\n`/dotgen_welcome` - Send welcome message\n`/dotgen_announce` - Send announcements",
        inline=False
    )
    
    # Show prefix commands as legacy
    prefix_commands = [cmd.name for cmd in bot.commands if cmd.name not in ['help', 'bot_info']]
    if prefix_commands:
        legacy_list = [f"`/{name}`" for name in sorted(prefix_commands)[:6]]
        embed.add_field(
            name="🔧 Legacy Prefix Commands (Admin)",
            value=f"Some admin commands still use `{BOT_PREFIX}` prefix:\n" + " • ".join(legacy_list),
            inline=False
        )
    
    embed.add_field(
        name="💡 Pro Tips",
        value="• Slash commands provide autocomplete - just type `/` and start typing!\n• Tab completion shows all available options\n• Slash commands validate input automatically\n• Use `/dotgen_help <command>` for detailed help",
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
# END SLASH COMMANDS
# =============================================================================

# This is the end of the file. The bot code above this line is responsible for
# the main functionality of the DOTGEN.AI Discord bot, including dynamic voice
# channels, welcome messages, and administrative commands. The bot also includes
# a webserver for 24/7 operation on cloud platforms, and uses advanced features
# like privileged intents and rotating status messages.
