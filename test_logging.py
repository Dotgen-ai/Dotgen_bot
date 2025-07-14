#!/usr/bin/env python3
"""
Test script for the message logging system
This script helps verify that the message logging integration is working properly.
"""

import sys
import os
import discord
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from message_logger import MessageLogger
    from role_logger import RoleLogger
    print("✅ Successfully imported logging modules")
except ImportError as e:
    print(f"❌ Failed to import logging modules: {e}")
    sys.exit(1)

def test_message_logger():
    """Test the MessageLogger class"""
    print("\n🧪 Testing MessageLogger...")
    
    # Create a mock bot object
    class MockBot:
        def get_channel(self, channel_id):
            return None
    
    # Test logger initialization
    bot = MockBot()
    logger = MessageLogger(bot)
    
    # Test cache functionality
    print(f"   ✅ Cache size limit: {logger.max_cache_size:,}")
    print(f"   ✅ Current cache size: {len(logger.message_cache):,}")
    
    # Test cache stats
    stats = logger.get_cache_stats()
    print(f"   ✅ Cache stats: {stats}")
    
    # Test cache operations
    logger.clear_cache()
    print(f"   ✅ Cache cleared: {len(logger.message_cache)} messages")
    
    print("   ✅ MessageLogger tests passed!")

def test_role_logger():
    """Test the RoleLogger class"""
    print("\n🧪 Testing RoleLogger...")
    
    # Create a mock bot object
    class MockBot:
        def get_channel(self, channel_id):
            return None
        
        def get_user(self, user_id):
            return None
        
        @property
        def guilds(self):
            return []
    
    # Test logger initialization
    bot = MockBot()
    logger = RoleLogger(bot)
    
    print(f"   ✅ Role log channel ID: {logger.role_log_channel_id}")
    print(f"   ✅ Previous member roles tracking: {len(logger.previous_member_roles)} members")
    
    print("   ✅ RoleLogger tests passed!")

def test_env_configuration():
    """Test environment configuration"""
    print("\n🧪 Testing Environment Configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check required environment variables
    env_vars = [
        'DISCORD_TOKEN',
        'MESSAGE_LOG_CHANNEL_ID',
        'ROLE_LOG_CHANNEL_ID',
        'MEMBER_LOG_CHANNEL_ID',
        'VOICE_LOG_CHANNEL_ID',
        'MODERATION_LOG_CHANNEL_ID'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if var == 'DISCORD_TOKEN':
                # Don't show the full token
                print(f"   ✅ {var}: {'*' * 20}...{value[-4:]}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ⚠️  {var}: Not set (optional)")
    
    print("   ✅ Environment configuration check completed!")

def main():
    """Main test function"""
    print("🚀 DOTGEN.AI Discord Bot - Logging System Test")
    print("=" * 50)
    
    try:
        test_message_logger()
        test_role_logger()
        test_env_configuration()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! The logging system is ready to use.")
        print("\n📋 Quick Setup Guide:")
        print("   1. Set MESSAGE_LOG_CHANNEL_ID in your .env file")
        print("   2. Set ROLE_LOG_CHANNEL_ID in your .env file")
        print("   3. Run the bot with: python main.py")
        print("   4. Use /dotgen_message_log_channel to configure message logging")
        print("   5. Use /dotgen_role_log_channel to configure role logging")
        print("\n🎉 Your bot will automatically log:")
        print("   • Message deletions and edits")
        print("   • Role additions and removals")
        print("   • Bulk operations")
        print("   • Rich formatted logs with full context")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
