import discord
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get message log channel ID from environment
MESSAGE_LOG_CHANNEL_ID = int(os.getenv('MESSAGE_LOG_CHANNEL_ID', 0)) or None

class MessageLogger:
    """Comprehensive message deletion and edit logging system for Discord servers"""
    
    def __init__(self, bot):
        self.bot = bot
        self.message_log_channel_id = MESSAGE_LOG_CHANNEL_ID
        self.message_cache = {}  # Cache messages for deletion tracking
        self.max_cache_size = 10000  # Maximum cached messages
    
    def get_message_log_channel(self, guild):
        """Get the message log channel for the guild"""
        if not self.message_log_channel_id:
            return None
        
        channel = guild.get_channel(self.message_log_channel_id)
        if not channel:
            # Try to get channel from bot cache
            channel = self.bot.get_channel(self.message_log_channel_id)
        
        return channel
    
    def cache_message(self, message):
        """Cache a message for deletion tracking"""
        if len(self.message_cache) >= self.max_cache_size:
            # Remove oldest entries to make space
            oldest_keys = list(self.message_cache.keys())[:1000]
            for key in oldest_keys:
                del self.message_cache[key]
        
        self.message_cache[message.id] = {
            'content': message.content,
            'author': {
                'id': message.author.id,
                'name': message.author.display_name,
                'avatar': str(message.author.display_avatar.url) if message.author.display_avatar else None,
                'bot': message.author.bot
            },
            'channel': {
                'id': message.channel.id,
                'name': message.channel.name,
                'type': str(message.channel.type)
            },
            'guild': {
                'id': message.guild.id,
                'name': message.guild.name
            } if message.guild else None,
            'timestamp': message.created_at,
            'attachments': [
                {
                    'filename': att.filename,
                    'url': att.url,
                    'size': att.size,
                    'content_type': att.content_type
                } for att in message.attachments
            ],
            'embeds': len(message.embeds),
            'mentions': {
                'users': [user.id for user in message.mentions],
                'roles': [role.id for role in message.role_mentions],
                'channels': [channel.id for channel in message.channel_mentions],
                'everyone': message.mention_everyone
            },
            'reactions': len(message.reactions),
            'pinned': message.pinned,
            'tts': message.tts,
            'edited_at': message.edited_at
        }
    
    def create_message_delete_embed(self, message_data, raw_message_id=None):
        """Create a formatted embed for message deletion"""
        
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        # Message content
        content = message_data.get('content', '') if message_data else 'Unknown content'
        if content:
            # Truncate very long messages
            if len(content) > 1024:
                content = content[:1021] + "..."
            embed.add_field(
                name="💬 Message Content",
                value=f"```{content}```" if content else "*No text content*",
                inline=False
            )
        else:
            embed.add_field(
                name="💬 Message Content",
                value="*No text content or content unavailable*",
                inline=False
            )
        
        if message_data:
            # Author information
            author_info = message_data.get('author', {})
            author_text = f"**Name:** {author_info.get('name', 'Unknown')}\n"
            author_text += f"**ID:** `{author_info.get('id', 'Unknown')}`\n"
            author_text += f"**Bot:** {'Yes' if author_info.get('bot', False) else 'No'}"
            
            embed.add_field(
                name="👤 Author",
                value=author_text,
                inline=True
            )
            
            # Channel information
            channel_info = message_data.get('channel', {})
            channel_text = f"**Name:** #{channel_info.get('name', 'Unknown')}\n"
            channel_text += f"**ID:** `{channel_info.get('id', 'Unknown')}`\n"
            channel_text += f"**Type:** {channel_info.get('type', 'Unknown')}"
            
            embed.add_field(
                name="📁 Channel",
                value=channel_text,
                inline=True
            )
            
            # Server information
            guild_info = message_data.get('guild')
            if guild_info:
                guild_text = f"**Name:** {guild_info.get('name', 'Unknown')}\n"
                guild_text += f"**ID:** `{guild_info.get('id', 'Unknown')}`"
                
                embed.add_field(
                    name="🏠 Server",
                    value=guild_text,
                    inline=True
                )
            
            # Message details
            details = []
            if message_data.get('attachments'):
                attachment_list = []
                for att in message_data['attachments'][:3]:  # Show up to 3 attachments
                    size_mb = att['size'] / (1024 * 1024)
                    attachment_list.append(f"• {att['filename']} ({size_mb:.1f}MB)")
                
                if len(message_data['attachments']) > 3:
                    attachment_list.append(f"... and {len(message_data['attachments']) - 3} more")
                
                details.append(f"**Attachments:** {len(message_data['attachments'])}\n" + "\n".join(attachment_list))
            
            if message_data.get('embeds', 0) > 0:
                details.append(f"**Embeds:** {message_data['embeds']}")
            
            if message_data.get('reactions', 0) > 0:
                details.append(f"**Reactions:** {message_data['reactions']}")
            
            mentions = message_data.get('mentions', {})
            mention_count = len(mentions.get('users', [])) + len(mentions.get('roles', [])) + len(mentions.get('channels', []))
            if mention_count > 0 or mentions.get('everyone', False):
                mention_text = f"**Mentions:** {mention_count}"
                if mentions.get('everyone'):
                    mention_text += " + @everyone"
                details.append(mention_text)
            
            if message_data.get('pinned', False):
                details.append("**Pinned:** Yes")
            
            if message_data.get('tts', False):
                details.append("**Text-to-Speech:** Yes")
            
            if message_data.get('edited_at'):
                details.append(f"**Last Edited:** {message_data['edited_at'].strftime('%Y-%m-%d %H:%M:%S')} UTC")
            
            if details:
                embed.add_field(
                    name="📋 Message Details",
                    value="\n".join(details),
                    inline=False
                )
            
            # Original timestamp
            if message_data.get('timestamp'):
                embed.add_field(
                    name="⏰ Originally Sent",
                    value=f"{message_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} UTC",
                    inline=True
                )
            
            # Set thumbnail to author's avatar
            if author_info.get('avatar'):
                embed.set_thumbnail(url=author_info['avatar'])
        else:
            # Minimal information for uncached messages
            embed.add_field(
                name="⚠️ Limited Information",
                value="This message was not cached. Only basic information is available.",
                inline=False
            )
        
        # Footer with message ID
        message_id = raw_message_id or (message_data.get('id') if message_data else 'Unknown')
        embed.set_footer(text=f"Message ID: {message_id}")
        
        return embed
    
    def create_message_edit_embed(self, before_message, after_message):
        """Create a formatted embed for message edits"""
        
        embed = discord.Embed(
            title="✏️ Message Edited",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        
        # Before content
        before_content = before_message.content or "*No text content*"
        if len(before_content) > 512:
            before_content = before_content[:509] + "..."
        
        embed.add_field(
            name="📝 Before",
            value=f"```{before_content}```",
            inline=False
        )
        
        # After content
        after_content = after_message.content or "*No text content*"
        if len(after_content) > 512:
            after_content = after_content[:509] + "..."
        
        embed.add_field(
            name="📝 After",
            value=f"```{after_content}```",
            inline=False
        )
        
        # Author information
        embed.add_field(
            name="👤 Author",
            value=f"{after_message.author.mention}\n**Name:** {after_message.author.display_name}\n**ID:** `{after_message.author.id}`",
            inline=True
        )
        
        # Channel information
        embed.add_field(
            name="📁 Channel",
            value=f"{after_message.channel.mention}\n**Name:** #{after_message.channel.name}\n**ID:** `{after_message.channel.id}`",
            inline=True
        )
        
        # Server information
        if after_message.guild:
            embed.add_field(
                name="🏠 Server",
                value=f"**Name:** {after_message.guild.name}\n**ID:** `{after_message.guild.id}`",
                inline=True
            )
        
        # Message link
        embed.add_field(
            name="🔗 Jump to Message",
            value=f"[Click here]({after_message.jump_url})",
            inline=True
        )
        
        # Edit timestamp
        embed.add_field(
            name="⏰ Edited At",
            value=f"{after_message.edited_at.strftime('%Y-%m-%d %H:%M:%S')} UTC" if after_message.edited_at else "Unknown",
            inline=True
        )
        
        # Set thumbnail to author's avatar
        if after_message.author.display_avatar:
            embed.set_thumbnail(url=after_message.author.display_avatar.url)
        
        # Footer
        embed.set_footer(text=f"Message ID: {after_message.id}")
        
        return embed
    
    def create_bulk_delete_embed(self, messages, channel):
        """Create embed for bulk message deletion"""
        
        embed = discord.Embed(
            title="🗑️ Bulk Message Deletion",
            color=discord.Color.dark_red(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📊 Summary",
            value=f"**Messages Deleted:** {len(messages)}\n**Channel:** {channel.mention}\n**Channel ID:** `{channel.id}`",
            inline=False
        )
        
        # Analyze deleted messages
        authors = {}
        total_attachments = 0
        total_embeds = 0
        
        for message in messages:
            author_id = message.author.id
            authors[author_id] = authors.get(author_id, 0) + 1
            total_attachments += len(message.attachments)
            total_embeds += len(message.embeds)
        
        # Top authors
        if authors:
            top_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)[:5]
            author_list = []
            for author_id, count in top_authors:
                try:
                    user = self.bot.get_user(author_id)
                    name = user.display_name if user else f"Unknown User ({author_id})"
                    author_list.append(f"• {name}: {count} messages")
                except:
                    author_list.append(f"• Unknown User ({author_id}): {count} messages")
            
            embed.add_field(
                name="👥 Top Authors",
                value="\n".join(author_list),
                inline=True
            )
        
        # Content statistics
        stats = []
        if total_attachments > 0:
            stats.append(f"**Attachments:** {total_attachments}")
        if total_embeds > 0:
            stats.append(f"**Embeds:** {total_embeds}")
        
        if stats:
            embed.add_field(
                name="📋 Content Stats",
                value="\n".join(stats),
                inline=True
            )
        
        # Server info
        if channel.guild:
            embed.add_field(
                name="🏠 Server",
                value=f"**Name:** {channel.guild.name}\n**ID:** `{channel.guild.id}`",
                inline=True
            )
        
        # Recent messages preview (if cached)
        preview_messages = []
        for message in messages[-5:]:  # Show last 5 messages
            content = message.content[:50] + "..." if len(message.content) > 50 else message.content
            preview_messages.append(f"• {message.author.display_name}: {content or '*No text*'}")
        
        if preview_messages:
            embed.add_field(
                name="💬 Recent Messages Preview",
                value="\n".join(preview_messages),
                inline=False
            )
        
        embed.set_footer(text=f"Bulk deletion in #{channel.name}")
        
        return embed
    
    async def log_message_delete(self, message):
        """Log a single message deletion"""
        try:
            # Get the log channel
            log_channel = self.get_message_log_channel(message.guild)
            if not log_channel:
                print(f"⚠️ Message log channel not configured or not found (ID: {self.message_log_channel_id})")
                return False
            
            # Check if bot has permission to send messages
            if not log_channel.permissions_for(message.guild.me).send_messages:
                print(f"⚠️ Bot doesn't have permission to send messages in message log channel")
                return False
            
            # Get cached message data
            message_data = self.message_cache.get(message.id)
            
            # Create embed
            embed = self.create_message_delete_embed(message_data, message.id)
            
            # Send log message
            await log_channel.send(embed=embed)
            
            # Remove from cache
            if message.id in self.message_cache:
                del self.message_cache[message.id]
            
            print(f"✅ Logged message deletion: {message.id}")
            return True
            
        except discord.HTTPException as e:
            print(f"❌ Failed to send message delete log: {e}")
            return False
        except Exception as e:
            print(f"❌ Error logging message deletion: {e}")
            return False
    
    async def log_message_edit(self, before, after):
        """Log a message edit"""
        try:
            # Skip if no actual content change
            if before.content == after.content:
                return False
            
            # Get the log channel
            log_channel = self.get_message_log_channel(after.guild)
            if not log_channel:
                return False
            
            # Check permissions
            if not log_channel.permissions_for(after.guild.me).send_messages:
                return False
            
            # Create embed
            embed = self.create_message_edit_embed(before, after)
            
            # Send log message
            await log_channel.send(embed=embed)
            
            # Update cache
            self.cache_message(after)
            
            print(f"✅ Logged message edit: {after.id}")
            return True
            
        except Exception as e:
            print(f"❌ Error logging message edit: {e}")
            return False
    
    async def log_bulk_delete(self, messages):
        """Log bulk message deletion"""
        try:
            if not messages:
                return False
            
            # Get channel from first message
            channel = messages[0].channel
            log_channel = self.get_message_log_channel(channel.guild)
            if not log_channel:
                return False
            
            # Check permissions
            if not log_channel.permissions_for(channel.guild.me).send_messages:
                return False
            
            # Create embed
            embed = self.create_bulk_delete_embed(messages, channel)
            
            # Send log message
            await log_channel.send(embed=embed)
            
            # Remove from cache
            for message in messages:
                if message.id in self.message_cache:
                    del self.message_cache[message.id]
            
            print(f"✅ Logged bulk message deletion: {len(messages)} messages")
            return True
            
        except Exception as e:
            print(f"❌ Error logging bulk message deletion: {e}")
            return False
    
    async def on_message(self, message):
        """Cache messages for deletion tracking"""
        try:
            # Don't cache bot messages or DMs
            if message.author.bot or not message.guild:
                return
            
            # Cache the message
            self.cache_message(message)
            print(f"📥 Cached message: ID={message.id}, Author={message.author.display_name}, Channel=#{message.channel.name}")
            
        except Exception as e:
            print(f"❌ Error caching message: {e}")
    
    async def on_message_delete(self, message):
        """Handle message deletion events"""
        try:
            # Don't log bot message deletions or DMs
            if message.author.bot or not message.guild:
                print(f"🤖 Skipping message deletion log (bot: {message.author.bot}, guild: {message.guild is not None})")
                return
            
            print(f"🗑️ Processing message deletion: ID={message.id}, Author={message.author.display_name}, Channel=#{message.channel.name}")
            await self.log_message_delete(message)
            
        except Exception as e:
            print(f"❌ Error in message delete handler: {e}")
    
    async def on_message_edit(self, before, after):
        """Handle message edit events"""
        try:
            # Don't log bot message edits or DMs
            if after.author.bot or not after.guild:
                return
            
            await self.log_message_edit(before, after)
            
        except Exception as e:
            print(f"❌ Error in message edit handler: {e}")
    
    async def on_bulk_message_delete(self, messages):
        """Handle bulk message deletion events"""
        try:
            # Filter out bot messages and DMs
            user_messages = [msg for msg in messages if not msg.author.bot and msg.guild]
            
            if user_messages:
                await self.log_bulk_delete(user_messages)
            
        except Exception as e:
            print(f"❌ Error in bulk message delete handler: {e}")
    
    def set_message_log_channel(self, channel_id):
        """Update the message log channel ID"""
        self.message_log_channel_id = channel_id
        
        # Update environment variable
        os.environ['MESSAGE_LOG_CHANNEL_ID'] = str(channel_id)
        
        # Update .env file if it exists
        env_path = '.env'
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Update or add MESSAGE_LOG_CHANNEL_ID line
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('MESSAGE_LOG_CHANNEL_ID='):
                    lines[i] = f"MESSAGE_LOG_CHANNEL_ID={channel_id}\n"
                    updated = True
                    break
            
            if not updated:
                lines.append(f"MESSAGE_LOG_CHANNEL_ID={channel_id}\n")
            
            with open(env_path, 'w') as f:
                f.writelines(lines)
        
        print(f"✅ Message log channel updated to ID: {channel_id}")
    
    def clear_cache(self):
        """Clear the message cache"""
        self.message_cache.clear()
        print("✅ Message cache cleared")
    
    def get_cache_stats(self):
        """Get message cache statistics"""
        return {
            'cached_messages': len(self.message_cache),
            'max_cache_size': self.max_cache_size,
            'cache_usage_percent': (len(self.message_cache) / self.max_cache_size) * 100
        }

# Helper functions for easy integration
async def log_message_deletion(message_logger, message):
    """Helper function to log message deletion"""
    return await message_logger.log_message_delete(message)

async def log_message_edit(message_logger, before, after):
    """Helper function to log message edit"""
    return await message_logger.log_message_edit(before, after)

async def log_bulk_message_deletion(message_logger, messages):
    """Helper function to log bulk message deletion"""
    return await message_logger.log_bulk_delete(messages)
