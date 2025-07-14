# 📝 Message Logging System Documentation

## Overview
The DOTGEN.AI Discord Bot now includes a comprehensive message logging system that automatically tracks and logs message deletions, edits, and bulk operations to a designated channel.

## Features

### 🗑️ Message Deletion Logging
- **Complete Content Capture**: Logs the full content of deleted messages
- **Author Information**: Displays author name, ID, avatar, and bot status
- **Channel Context**: Shows which channel the message was deleted from
- **Timestamp Tracking**: Records when the message was originally sent
- **Attachment Details**: Logs attachment filenames, sizes, and types
- **Rich Formatting**: Color-coded embeds with comprehensive metadata

### ✏️ Message Edit Logging
- **Before/After Comparison**: Shows original and edited content side-by-side
- **Author Tracking**: Records who edited the message
- **Direct Links**: Provides jump links to edited messages
- **Timestamp Information**: Shows when the edit occurred
- **Context Preservation**: Maintains channel and server information

### 🗂️ Bulk Deletion Logging
- **Summary Statistics**: Shows total deleted messages and affected authors
- **Author Analysis**: Lists top authors by message count
- **Content Statistics**: Tracks attachments and embeds in bulk deletions
- **Recent Messages Preview**: Shows preview of recently deleted messages
- **Performance Optimized**: Efficiently handles large bulk deletions

## Configuration

### Environment Variables
Add to your `.env` file:
```env
# Message logging channel
MESSAGE_LOG_CHANNEL_ID=your_channel_id_here
```

### Slash Commands
- `/dotgen_message_log_channel` - Configure or view message log channel
- `/dotgen_clear_message_cache` - Clear message cache (admin only)

## Message Cache System

### How It Works
- **Automatic Caching**: All messages are automatically cached when sent
- **Memory Management**: Automatically clears old cache entries to prevent memory issues
- **Configurable Size**: Default cache size of 10,000 messages
- **Bot Message Filtering**: Doesn't cache bot messages or DMs

### Cache Benefits
- **Full Content Recovery**: Deleted messages retain complete content and metadata
- **Attachment Information**: Preserves attachment details even after deletion
- **Performance**: Fast lookup for recently deleted messages
- **Reliability**: Works even when Discord's audit log is limited

## Log Format Examples

### Message Deletion Log
```
🗑️ Message Deleted

💬 Message Content
```
Hello everyone! This is a test message.
```

👤 Author                    📁 Channel                   🏠 Server
Name: TestUser               Name: #general               Name: My Server
ID: 123456789               ID: 987654321               ID: 555666777
Bot: No                     Type: TextChannel

📋 Message Details
Attachments: 1
• screenshot.png (2.3MB)
Mentions: 2
Reactions: 3
Originally Sent: 2025-01-15 14:30:22 UTC

Message ID: 1234567890123456789
```

### Message Edit Log
```
✏️ Message Edited

📝 Before
```
This is the original message.
```

📝 After
```
This is the edited message with new content.
```

👤 Author                    📁 Channel                   🔗 Jump to Message
@TestUser                    #general                     [Click here](link)
Name: TestUser               Name: #general
ID: 123456789               ID: 987654321

🏠 Server                    ⏰ Edited At
Name: My Server              2025-01-15 14:35:45 UTC
ID: 555666777

Message ID: 1234567890123456789
```

### Bulk Deletion Log
```
🗑️ Bulk Message Deletion

📊 Summary
Messages Deleted: 25 messages
Channel: #general
Channel ID: 987654321

👥 Top Authors                📋 Content Stats
• User1: 10 messages         Attachments: 5
• User2: 8 messages          Embeds: 2
• User3: 4 messages
• User4: 2 messages
• User5: 1 messages

🏠 Server
Name: My Server
ID: 555666777

💬 Recent Messages Preview
• User1: Hello everyone, how are you doing today?
• User2: I'm doing great, thanks for asking!
• User3: Same here, beautiful weather outside...
• User1: Yes, perfect day for a walk in the park
• User4: Anyone want to play some games later?

Bulk deletion in #general
```

## Technical Details

### Event Handlers
- `on_message`: Caches messages for deletion tracking
- `on_message_delete`: Logs individual message deletions
- `on_message_edit`: Logs message edits with before/after comparison
- `on_bulk_message_delete`: Logs bulk deletion operations

### Performance Considerations
- **Memory Efficient**: Automatic cache management prevents memory leaks
- **Async Operations**: Non-blocking logging operations
- **Error Handling**: Graceful error handling with fallbacks
- **Permission Checks**: Verifies bot permissions before logging

### Privacy and Security
- **No Bot Messages**: Doesn't log bot messages to reduce noise
- **No DMs**: Respects privacy by not logging direct messages
- **Permission Aware**: Only logs in channels where bot has permissions
- **Configurable**: Can be enabled/disabled per server

## Integration with Existing Systems

### Role Logging Integration
- Works alongside the role logging system
- Shared configuration in `.env` file
- Consistent embed formatting and color schemes
- Unified slash command structure

### Event Handler Compatibility
- Maintains `bot.process_commands()` for command functionality
- Non-interfering with existing bot operations
- Error isolation prevents system-wide failures

## Best Practices

### Channel Setup
1. Create a dedicated `#message-logs` channel
2. Restrict access to administrators only
3. Set proper channel permissions for the bot
4. Consider separate channels for different log types

### Maintenance
1. Monitor cache usage with `/dotgen_clear_message_cache`
2. Regularly check log channel for important information
3. Adjust cache size if needed for high-traffic servers
4. Review logs for moderation insights

### Moderation Usage
1. Use logs to investigate deleted messages
2. Track message edit patterns for abuse detection
3. Analyze bulk deletions for context
4. Reference logs in moderation decisions

## Troubleshooting

### Common Issues
1. **No logs appearing**: Check MESSAGE_LOG_CHANNEL_ID in .env
2. **Missing content**: Message wasn't cached (sent before bot started)
3. **Permission errors**: Ensure bot can send messages in log channel
4. **Memory issues**: Clear cache with `/dotgen_clear_message_cache`

### Configuration Verification
Run the test script to verify setup:
```bash
python test_logging.py
```

## Files Structure
```
📁 Discord Bot
├── 📄 main.py (main bot file with event handlers)
├── 📄 message_logger.py (message logging system)
├── 📄 role_logger.py (role logging system)
├── 📄 test_logging.py (test script)
├── 📄 .env (configuration file)
└── 📄 requirements.txt (dependencies)
```

This message logging system provides comprehensive tracking of all message-related activities while maintaining performance, privacy, and ease of use.
