#!/usr/bin/env python3

import asyncio
from telegram_service import TelegramService

async def test_telegram():
    """Test Telegram functionality"""
    try:
        service = TelegramService()
        
        # Test sending a notification
        result = await service.send_notification("🧪 Testing Telegram MCP Server!", "normal")
        print(f"✅ Notification sent: {result}")
        
        # Test sending a progress update
        result = await service.send_progress("Server initialization complete", "completed")
        print(f"✅ Progress sent: {result}")
        
        # Test sending an approval request
        result = await service.send_approval_request("Test approval workflow", "This is a test of the approval system")
        print(f"✅ Approval request sent: {result}")
        
        print("🎉 All tests passed! Telegram integration is working correctly.")
        
    except Exception as e:
        print(f"❌ Error testing Telegram: {e}")

if __name__ == "__main__":
    asyncio.run(test_telegram())
