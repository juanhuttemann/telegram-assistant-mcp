import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_service import TelegramService

async def test_all_features():
    """Comprehensive test of all TelegramService features."""
    print("🚀 Testing ALL TelegramService features...\n")
    
    service = TelegramService()
    
    # Test 1: Progress notifications with different statuses
    print("📝 Test 1: Progress notifications")
    statuses = ["working", "success", "error", "warning", "info"]
    for status in statuses:
        result = await service.send_progress(f"Testing {status} status", status)
        print(f"  ✅ {result}")
    
    # Test 2: Notifications with different priorities
    print("\n📝 Test 2: Notifications with priorities")
    priorities = ["low", "normal", "high", "urgent"]
    for priority in priorities:
        result = await service.send_notification(f"This is a {priority} priority message", priority)
        print(f"  ✅ {result}")
    
    # Test 3: Basic approval request (no waiting)
    print("\n📝 Test 3: Basic approval request")
    result = await service.send_approval_request("Restart server", "This will cause 5 seconds of downtime")
    print(f"  ✅ {result}")
    
    # Test 4: Approval request with waiting (simplified)
    print("\n📝 Test 4: Approval with waiting (30s timeout)")
    print("  👀 Please respond in Telegram with 'approve' or 'deny'")
    try:
        response = await service.send_approval_request_and_wait(
            "Clear cache files", 
            "This will free up 500MB of space",
            timeout=30
        )
        print(f"  ✅ Response: {response}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n🎉 All comprehensive tests completed!")
    print("📱 Check your Telegram for all the messages!")

if __name__ == "__main__":
    asyncio.run(test_all_features())
