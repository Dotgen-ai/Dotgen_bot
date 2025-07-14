import discord
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get role log channel ID from environment
ROLE_LOG_CHANNEL_ID = int(os.getenv('ROLE_LOG_CHANNEL_ID', 0)) or None

class RoleLogger:
    """Comprehensive role logging system for Discord servers"""
    
    def __init__(self, bot):
        self.bot = bot
        self.role_log_channel_id = ROLE_LOG_CHANNEL_ID
        self.previous_member_roles = {}  # Track previous roles for comparison
    
    def get_role_log_channel(self, guild):
        """Get the role log channel for the guild"""
        if not self.role_log_channel_id:
            return None
        
        channel = guild.get_channel(self.role_log_channel_id)
        if not channel:
            # Try to get channel from bot cache
            channel = self.bot.get_channel(self.role_log_channel_id)
        
        return channel
    
    def create_role_embed(self, action, member, role, moderator=None, reason=None):
        """Create a formatted embed for role changes"""
        
        # Determine embed color based on action
        if action == "added":
            color = discord.Color.green()
            emoji = "✅"
            title = "Role Added"
        elif action == "removed":
            color = discord.Color.red()
            emoji = "❌"
            title = "Role Removed"
        else:
            color = discord.Color.orange()
            emoji = "⚠️"
            title = "Role Changed"
        
        embed = discord.Embed(
            title=f"{emoji} {title}",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        # Member information
        embed.add_field(
            name="👤 Member",
            value=f"{member.mention}\n**Name:** {member.display_name}\n**ID:** `{member.id}`",
            inline=True
        )
        
        # Role information
        role_info = f"**Name:** {role.name}\n**ID:** `{role.id}`\n**Color:** {role.color}"
        if role.mentionable:
            role_info += "\n**Mentionable:** Yes"
        if role.hoist:
            role_info += "\n**Hoisted:** Yes"
        
        embed.add_field(
            name="🎭 Role",
            value=role_info,
            inline=True
        )
        
        # Moderator information
        if moderator:
            embed.add_field(
                name="🛡️ Moderator",
                value=f"{moderator.mention}\n**Name:** {moderator.display_name}\n**ID:** `{moderator.id}`",
                inline=True
            )
        else:
            embed.add_field(
                name="🛡️ Moderator",
                value="*System/Unknown*",
                inline=True
            )
        
        # Reason (if provided)
        if reason:
            embed.add_field(
                name="📝 Reason",
                value=reason,
                inline=False
            )
        
        # Additional context
        embed.add_field(
            name="📊 Member Info",
            value=f"**Total Roles:** {len(member.roles) - 1}\n**Joined:** {member.joined_at.strftime('%Y-%m-%d %H:%M:%S') if member.joined_at else 'Unknown'}\n**Account Created:** {member.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            inline=True
        )
        
        # Role hierarchy position
        embed.add_field(
            name="📈 Role Position",
            value=f"**Position:** {role.position}\n**Hierarchy:** {len([r for r in member.guild.roles if r.position > role.position])} roles above",
            inline=True
        )
        
        # Server information
        embed.add_field(
            name="🏠 Server",
            value=f"**Name:** {member.guild.name}\n**ID:** `{member.guild.id}`",
            inline=True
        )
        
        # Set footer
        embed.set_footer(
            text=f"Member ID: {member.id} | Role ID: {role.id}",
            icon_url=member.display_avatar.url if member.display_avatar else None
        )
        
        # Set thumbnail to member's avatar
        if member.display_avatar:
            embed.set_thumbnail(url=member.display_avatar.url)
        
        return embed
    
    def create_bulk_role_embed(self, action, members, role, moderator=None, reason=None):
        """Create embed for bulk role changes"""
        
        if action == "added":
            color = discord.Color.green()
            emoji = "✅"
            title = "Bulk Role Added"
        else:
            color = discord.Color.red()
            emoji = "❌"
            title = "Bulk Role Removed"
        
        embed = discord.Embed(
            title=f"{emoji} {title}",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        # Role information
        embed.add_field(
            name="🎭 Role",
            value=f"**Name:** {role.name}\n**ID:** `{role.id}`\n**Color:** {role.color}",
            inline=True
        )
        
        # Affected members count
        embed.add_field(
            name="👥 Affected Members",
            value=f"**Count:** {len(members)} members",
            inline=True
        )
        
        # Moderator
        if moderator:
            embed.add_field(
                name="🛡️ Moderator",
                value=f"{moderator.mention}\n**Name:** {moderator.display_name}",
                inline=True
            )
        
        # List affected members (up to 20)
        member_list = []
        for i, member in enumerate(members[:20]):
            member_list.append(f"{i+1}. {member.display_name} (`{member.id}`)")
        
        if len(members) > 20:
            member_list.append(f"... and {len(members) - 20} more members")
        
        embed.add_field(
            name="📋 Affected Members",
            value="\n".join(member_list) if member_list else "No members listed",
            inline=False
        )
        
        # Reason
        if reason:
            embed.add_field(
                name="📝 Reason",
                value=reason,
                inline=False
            )
        
        embed.set_footer(text=f"Bulk operation affecting {len(members)} members")
        
        return embed
    
    async def log_role_change(self, member, role, action, moderator=None, reason=None):
        """Log a single role change"""
        try:
            # Get the log channel
            log_channel = self.get_role_log_channel(member.guild)
            if not log_channel:
                print(f"⚠️ Role log channel not configured or not found (ID: {self.role_log_channel_id})")
                return False
            
            # Check if bot has permission to send messages
            if not log_channel.permissions_for(member.guild.me).send_messages:
                print(f"⚠️ Bot doesn't have permission to send messages in role log channel")
                return False
            
            # Create embed
            embed = self.create_role_embed(action, member, role, moderator, reason)
            
            # Send log message
            await log_channel.send(embed=embed)
            print(f"✅ Logged role {action}: {role.name} for {member.display_name}")
            return True
            
        except discord.HTTPException as e:
            print(f"❌ Failed to send role log message: {e}")
            return False
        except Exception as e:
            print(f"❌ Error logging role change: {e}")
            return False
    
    async def log_bulk_role_change(self, members, role, action, moderator=None, reason=None):
        """Log bulk role changes"""
        try:
            log_channel = self.get_role_log_channel(members[0].guild if members else None)
            if not log_channel or not members:
                return False
            
            # Create bulk embed
            embed = self.create_bulk_role_embed(action, members, role, moderator, reason)
            
            # Send log message
            await log_channel.send(embed=embed)
            print(f"✅ Logged bulk role {action}: {role.name} for {len(members)} members")
            return True
            
        except Exception as e:
            print(f"❌ Error logging bulk role change: {e}")
            return False
    
    async def log_role_update(self, before_role, after_role, moderator=None):
        """Log role property updates (name, color, permissions, etc.)"""
        try:
            # Find a guild member to get the guild (roles don't have direct guild reference)
            guild = None
            for guild_obj in self.bot.guilds:
                if before_role in guild_obj.roles:
                    guild = guild_obj
                    break
            
            if not guild:
                return False
            
            log_channel = self.get_role_log_channel(guild)
            if not log_channel:
                return False
            
            embed = discord.Embed(
                title="🔄 Role Updated",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            
            # Role basic info
            embed.add_field(
                name="🎭 Role",
                value=f"**Name:** {after_role.name}\n**ID:** `{after_role.id}`",
                inline=True
            )
            
            # Moderator
            if moderator:
                embed.add_field(
                    name="🛡️ Updated By",
                    value=f"{moderator.mention}\n**Name:** {moderator.display_name}",
                    inline=True
                )
            
            # Track changes
            changes = []
            
            if before_role.name != after_role.name:
                changes.append(f"**Name:** `{before_role.name}` → `{after_role.name}`")
            
            if before_role.color != after_role.color:
                changes.append(f"**Color:** {before_role.color} → {after_role.color}")
            
            if before_role.hoist != after_role.hoist:
                changes.append(f"**Hoisted:** {before_role.hoist} → {after_role.hoist}")
            
            if before_role.mentionable != after_role.mentionable:
                changes.append(f"**Mentionable:** {before_role.mentionable} → {after_role.mentionable}")
            
            if before_role.position != after_role.position:
                changes.append(f"**Position:** {before_role.position} → {after_role.position}")
            
            if before_role.permissions != after_role.permissions:
                # Get permission differences
                added_perms = []
                removed_perms = []
                
                for perm, value in after_role.permissions:
                    before_value = getattr(before_role.permissions, perm)
                    if value and not before_value:
                        added_perms.append(perm.replace('_', ' ').title())
                    elif not value and before_value:
                        removed_perms.append(perm.replace('_', ' ').title())
                
                if added_perms:
                    changes.append(f"**Permissions Added:** {', '.join(added_perms[:5])}")
                if removed_perms:
                    changes.append(f"**Permissions Removed:** {', '.join(removed_perms[:5])}")
            
            if changes:
                embed.add_field(
                    name="📝 Changes",
                    value="\n".join(changes),
                    inline=False
                )
            
            embed.set_footer(text=f"Role ID: {after_role.id}")
            
            await log_channel.send(embed=embed)
            return True
            
        except Exception as e:
            print(f"❌ Error logging role update: {e}")
            return False
    
    async def log_role_creation(self, role, moderator=None):
        """Log role creation"""
        try:
            log_channel = self.get_role_log_channel(role.guild)
            if not log_channel:
                return False
            
            embed = discord.Embed(
                title="➕ Role Created",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="🎭 New Role",
                value=f"**Name:** {role.name}\n**ID:** `{role.id}`\n**Color:** {role.color}\n**Position:** {role.position}",
                inline=True
            )
            
            if moderator:
                embed.add_field(
                    name="🛡️ Created By",
                    value=f"{moderator.mention}\n**Name:** {moderator.display_name}",
                    inline=True
                )
            
            # Role properties
            properties = []
            if role.hoist:
                properties.append("Hoisted")
            if role.mentionable:
                properties.append("Mentionable")
            if role.managed:
                properties.append("Managed by Integration")
            
            if properties:
                embed.add_field(
                    name="⚙️ Properties",
                    value=", ".join(properties),
                    inline=True
                )
            
            embed.set_footer(text=f"Role ID: {role.id}")
            
            await log_channel.send(embed=embed)
            return True
            
        except Exception as e:
            print(f"❌ Error logging role creation: {e}")
            return False
    
    async def log_role_deletion(self, role, moderator=None):
        """Log role deletion"""
        try:
            log_channel = self.get_role_log_channel(role.guild)
            if not log_channel:
                return False
            
            embed = discord.Embed(
                title="🗑️ Role Deleted",
                color=discord.Color.dark_red(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="🎭 Deleted Role",
                value=f"**Name:** {role.name}\n**ID:** `{role.id}`\n**Color:** {role.color}\n**Position:** {role.position}",
                inline=True
            )
            
            embed.add_field(
                name="👥 Members Affected",
                value=f"{len(role.members)} members had this role",
                inline=True
            )
            
            if moderator:
                embed.add_field(
                    name="🛡️ Deleted By",
                    value=f"{moderator.mention}\n**Name:** {moderator.display_name}",
                    inline=True
                )
            
            embed.set_footer(text=f"Role ID: {role.id}")
            
            await log_channel.send(embed=embed)
            return True
            
        except Exception as e:
            print(f"❌ Error logging role deletion: {e}")
            return False
    
    def track_member_roles(self, member):
        """Track a member's roles for comparison"""
        self.previous_member_roles[member.id] = set(role.id for role in member.roles)
    
    async def on_member_update(self, before, after):
        """Handle member update events to detect role changes"""
        # Compare roles
        before_roles = set(role.id for role in before.roles)
        after_roles = set(role.id for role in after.roles)
        
        # Find added roles
        added_role_ids = after_roles - before_roles
        for role_id in added_role_ids:
            role = after.guild.get_role(role_id)
            if role:
                # Get moderator from audit logs
                moderator = await self.get_moderator_from_audit_logs(after.guild, after, discord.AuditLogAction.member_role_update)
                await self.log_role_change(after, role, "added", moderator)
        
        # Find removed roles
        removed_role_ids = before_roles - after_roles
        for role_id in removed_role_ids:
            role = before.guild.get_role(role_id)
            if role:
                # Get moderator from audit logs
                moderator = await self.get_moderator_from_audit_logs(before.guild, before, discord.AuditLogAction.member_role_update)
                await self.log_role_change(after, role, "removed", moderator)
    
    def set_role_log_channel(self, channel_id):
        """Update the role log channel ID"""
        self.role_log_channel_id = channel_id
        
        # Update environment variable
        os.environ['ROLE_LOG_CHANNEL_ID'] = str(channel_id)
        
        # Update .env file if it exists
        env_path = '.env'
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Update or add ROLE_LOG_CHANNEL_ID line
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('ROLE_LOG_CHANNEL_ID='):
                    lines[i] = f"ROLE_LOG_CHANNEL_ID={channel_id}\n"
                    updated = True
                    break
            
            if not updated:
                lines.append(f"ROLE_LOG_CHANNEL_ID={channel_id}\n")
            
            with open(env_path, 'w') as f:
                f.writelines(lines)
        
        print(f"✅ Role log channel updated to ID: {channel_id}")

    async def get_moderator_from_audit_logs(self, guild, target_user, action_type=discord.AuditLogAction.member_role_update, limit=10, time_delta_seconds=30):
        """Get the moderator who performed an action from audit logs"""
        try:
            # Check if bot has permission to view audit logs
            if not guild.me.guild_permissions.view_audit_log:
                print(f"⚠️ Bot doesn't have permission to view audit logs in {guild.name}")
                return None
            
            # Search recent audit log entries
            cutoff_time = datetime.utcnow() - timedelta(seconds=time_delta_seconds)
            
            async for entry in guild.audit_logs(
                action=action_type,
                limit=limit,
                after=cutoff_time
            ):
                # Check if this entry matches our target user
                if entry.target and entry.target.id == target_user.id:
                    return entry.user
            
            return None
            
        except discord.Forbidden:
            print(f"⚠️ No permission to access audit logs in {guild.name}")
            return None
        except discord.HTTPException as e:
            print(f"⚠️ HTTP error accessing audit logs: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Error accessing audit logs: {e}")
            return None

# Helper functions for easy integration
async def log_role_add(role_logger, member, role, moderator=None, reason=None):
    """Helper function to log role addition"""
    return await role_logger.log_role_change(member, role, "added", moderator, reason)

async def log_role_remove(role_logger, member, role, moderator=None, reason=None):
    """Helper function to log role removal"""
    return await role_logger.log_role_change(member, role, "removed", moderator, reason)

async def log_bulk_role_add(role_logger, members, role, moderator=None, reason=None):
    """Helper function to log bulk role addition"""
    return await role_logger.log_bulk_role_change(members, role, "added", moderator, reason)

async def log_bulk_role_remove(role_logger, members, role, moderator=None, reason=None):
    """Helper function to log bulk role removal"""
    return await role_logger.log_bulk_role_change(members, role, "removed", moderator, reason)
