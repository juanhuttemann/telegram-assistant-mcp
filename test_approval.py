#!/usr/bin/env python3

import asyncio
from telegram_service import TelegramService

async def test_approval_waiting():
    """Test approval waiting functionality"""
    try:
        service = TelegramService()
        
        print("📱 Sending approval request to Telegram...")
        print("🕐 Waiting for your response...")
        
        # Send approval request and wait for response
        result = await service.send_approval_request_and_wait(
            action="Delete important file system.db", 
            details="This action will permanently delete the system database. This cannot be undone.",
            timeout=60  # 1 minute timeout for testing
        )
        
        print(f"✅ Result: {result}")
        
        if result == "approved":
            print("🎉 Action was approved by user!")
        elif result == "denied":
            print("❌ Action was denied by user.")
        else:
            print("⏰ Request timed out - no response received.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing approval waiting functionality...")
    print("📝 Please respond with 'approve' or 'deny' when you receive the Telegram message.")
    asyncio.run(test_approval_waiting())
