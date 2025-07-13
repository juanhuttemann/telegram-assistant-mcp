#!/usr/bin/env python3

import asyncio
from telegram_service import TelegramService

async def test_new_approval():
    """Test the new approval system"""
    try:
        service = TelegramService()
        
        print("📱 Creating approval request...")
        
        # Create approval request (non-blocking)
        request_id = await service.create_approval_request(
            action="Delete production database", 
            details="This will permanently delete the production database. Cannot be undone!"
        )
        
        print(f"✅ Approval request created with ID: {request_id}")
        print("📝 Please respond in Telegram with: approve {request_id} or deny {request_id}")
        print("🕐 Waiting for your response (60 seconds timeout)...")
        
        # Poll for response
        import time
        start_time = time.time()
        timeout = 60
        
        while time.time() - start_time < timeout:
            status = service.get_approval_status(request_id)
            
            if status['status'] == 'approved':
                print("🎉 Request was APPROVED!")
                return
            elif status['status'] == 'denied':
                print("❌ Request was DENIED!")
                return
            elif status['status'] == 'pending':
                print(f"⏳ Still waiting... ({int(time.time() - start_time)}s elapsed)")
                await asyncio.sleep(3)
            else:
                print(f"❓ Unknown status: {status}")
                break
        
        print("⏰ Request timed out!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_new_approval())
