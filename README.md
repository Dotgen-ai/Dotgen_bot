# Dotgen Discord Bot

A Discord bot with unique welcome messages and dynamic voice channel creation based on user roles.

## Features

### 🎉 Welcome System
- Sends unique, randomized welcome messages when new members join
- Beautiful embed messages with member information
- Displays member count and account creation date
- Automatically finds appropriate welcome channel

### 🎤 Dynamic Voice Channels
- Creates temporary voice channels based on user roles
- Users join a "Join to Create" lobby channel
- Bot creates a new voice channel named after their highest role
- Automatic cleanup when channels become empty
- Role-based permissions for created channels

## Setup Instructions

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
