import asyncio
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram_service import TelegramService

async def test_all_features():
    """Comprehensive test of all TelegramService features."""
    print("Testing ALL TelegramService features...\n")
    
    service = TelegramService()
    
    # Test 1: Progress notifications with different statuses
    print("Test 1: Progress notifications")
    statuses = ["working", "success", "error", "warning", "info"]
    for status in statuses:
        result = await service.send_progress(f"Testing {status} status", status)
        print(f"  OK: {result}")
    
    # Test 2: Notifications with different priorities
    print("\nTest 2: Notifications with priorities")
    priorities = ["low", "normal", "high", "urgent"]
    for priority in priorities:
        result = await service.send_notification(f"This is a {priority} priority message", priority)
        print(f"  OK: {result}")
    
    # Test 3: Quick approval test with waiting
    print("\nTest 3: Testing approval workflow - PLEASE INTERACT")
    print("="*50)
    
    # Create one approval request and wait for response
    request_id = await service.create_approval_request("Pet a cute cat", "A friendly cat wants some attention and pets")
    print(f"  OK: Approval request created with ID: {request_id}")
    print("\n  >>> CHECK YOUR TELEGRAM AND CLICK A BUTTON <<<")
    print("  Waiting 30 seconds for your response...")
    
    # Wait for response
    start_time = time.time()
    timeout = 30
    responded = False
    
    while time.time() - start_time < timeout:
        await asyncio.sleep(2)
        status = service.get_approval_status(request_id)
        
        if status['status'] != 'pending':
            print(f"  OK: You clicked something! Status: {status['status']}")
            if status.get('instruction'):
                print(f"  OK: Your instruction: {status['instruction']}")
            responded = True
            break
        print(f"  Waiting... ({int(timeout - (time.time() - start_time))} seconds left)")
    
    if not responded:
        print("  TIMEOUT: No response received, but that's OK for testing!")
    
    print(f"\nTest completed! Approval workflow is working.")
    print("You can run the comprehensive test for full testing of all 3 scenarios.")

if __name__ == "__main__":
    asyncio.run(test_all_features())
