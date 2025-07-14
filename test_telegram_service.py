import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_service import TelegramService

async def test_approval_system():
    """Test the simplified approval system."""
    print("Testing TelegramService approval system...")
    
    service = TelegramService()
    
    # Test 1: Send progress notification
    print("\nTest 1: Sending progress notification...")
    result = await service.send_progress("Starting deployment process", "started")
    print(f"Result: {result}")
    
    # Test 2: Send regular notification
    print("\nTest 2: Sending regular notification...")
    result = await service.send_notification("This is a test notification", "normal")
    print(f"Result: {result}")
    
    # Test 3: Send approval request (simplified version)
    print("\nTest 3: Sending approval request...")
    result = await service.create_approval_request("Deploy to production", "Version 1.2.3 with critical bug fixes")
    print(f"Result: Approval request created with ID: {result}")
    
    # Test 4: Test the approval system that waits for response
    print("\nTest 4: Testing approval system with wait...")
    print("This will send an approval request and wait for your response...")
    print("Please respond in Telegram with 'approve' or 'deny'")
    
    try:
        response = await service.send_approval_request_and_wait(
            "Delete old backup files", 
            "This will free up 2GB of space",
            timeout=60  # 1 minute timeout for testing
        )
        print(f"Approval response received: {response}")
    except Exception as e:
        print(f"Error during approval test: {e}")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(test_approval_system())
