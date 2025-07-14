import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_service import TelegramService

async def test_enhanced_denial_system():
    """Test the new enhanced denial system with multiple options."""
    print("Testing Enhanced Denial System...")
    
    service = TelegramService()
    
    # Test 1: Create approval request with enhanced buttons
    print("\nTest 1: Creating approval request with enhanced denial options...")
    request_id = await service.create_approval_request(
        "Delete old database backups",
        "This will permanently remove backups older than 6 months to free up 10GB of storage space"
    )
    print(f"Request created with ID: {request_id}")
    print("Check Telegram - you should see 5 buttons:")
    print("  - Approve")
    print("  - Deny") 
    print("  - Deny & Suggest Alternative")
    print("  - Deny & Pause")
    print("  - Deny & Need More Info")
    
    # Test 2: Check status polling
    print("\nTest 2: Monitoring approval status...")
    print("Try different denial options in Telegram to see the enhanced workflow!")
    
    # Monitor for 60 seconds to see responses
    import time
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < 60:
        status = service.get_approval_status(request_id)
        
        if status['status'] != last_status:
            print(f"\nStatus changed to: {status['status']}")
            if 'instruction' in status:
                print(f"Instruction: {status['instruction']}")
            last_status = status['status']
            
            # If we got a final response, break
            if status['status'] != 'pending':
                break
                
        await asyncio.sleep(2)
    
    final_status = service.get_approval_status(request_id)
    print(f"\nFinal status: {final_status}")
    
    print("\nEnhanced denial system test completed!")
    print("The new system provides much more context about WHY something was denied")
    print("and WHAT the agent should do instead!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_denial_system())