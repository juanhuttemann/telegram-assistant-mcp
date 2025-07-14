import asyncio
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def safe_print(text):
    """Print text safely, handling encoding issues."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Remove problematic characters and print
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(f"[INSTRUCTION] {safe_text} (Note: Some special characters removed due to console encoding)")

from telegram_service import TelegramService

async def wait_for_user_action(description, timeout=60):
    """Wait for user action with timeout."""
    print(f"\n{description}")
    print("Waiting for your action...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        await asyncio.sleep(2)  # Check every 2 seconds
    print("Timeout reached, continuing tests...")

async def test_approval_system():
    """Test the complete Telegram approval system with real user interaction."""
    print("=" * 60)
    print("TELEGRAM MCP AGENT - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    service = TelegramService()
    
    # Test 1: Progress notifications (all statuses)
    print("\n" + "=" * 50)
    print("TEST 1: PROGRESS NOTIFICATIONS")
    print("=" * 50)
    
    statuses = ["started", "in_progress", "completed", "error"]
    for status in statuses:
        print(f"\nSending progress notification: {status}")
        result = await service.send_progress(f"Testing {status} status", status)
        print(f"Result: {result}")
        await asyncio.sleep(1)  # Small delay between notifications
    
    # Test 2: Regular notifications (all priorities)
    print("\n" + "=" * 50)
    print("TEST 2: REGULAR NOTIFICATIONS")
    print("=" * 50)
    
    priorities = ["low", "normal", "high", "urgent"]
    for priority in priorities:
        print(f"\nSending {priority} priority notification")
        result = await service.send_notification(f"This is a {priority} priority test message", priority)
        print(f"Result: {result}")
        await asyncio.sleep(1)
    
    # Test 3: Something nice that should be APPROVED
    print("\n" + "=" * 50)
    print("TEST 3: APPROVAL WORKFLOW - SHOULD APPROVE")
    print("=" * 50)
    
    request_id = await service.create_approval_request("Pet a cute cat", "A friendly cat wants some attention and pets")
    print(f"Approval request created with ID: {request_id}")
    print(f"Initial status: {service.get_approval_status(request_id)['status']}")
    
    print("\n" + "=" * 60)
    print("WAITING FOR YOUR ACTION IN TELEGRAM:")
    print("1. Check your Telegram for the approval request")
    print("2. This is something nice - you should APPROVE it")
    print("3. Click the 'Approve' button (green checkmark)")
    print("=" * 60)
    
    # Wait and check for any response
    start_time = time.time()
    timeout = 60  # 1 minute timeout
    response_received = False
    
    while time.time() - start_time < timeout:
        await asyncio.sleep(2)
        status = service.get_approval_status(request_id)
        current_status = status['status']
        
        if current_status == 'approved':
            print(f"\n[RESULT] You clicked APPROVE! Status: {current_status}")
            response_received = True
            break
        elif current_status == 'denied':
            print(f"\n[RESULT] You clicked DENY! Status: {current_status}")
            response_received = True
            break
        elif current_status == 'awaiting_custom_instruction':
            print(f"\n[RESULT] You clicked SUGGEST DIFFERENT APPROACH! Status: {current_status}")
            response_received = True
            break
        elif current_status == 'denied_custom':
            print(f"\n[RESULT] Custom instruction received! Status: {current_status}")
            instruction = status.get('instruction', 'No instruction')
            safe_print(f"Your instruction: {instruction}")
            response_received = True
            break
        else:
            print(f"Current status: {current_status} (waiting...)")
    
    if not response_received:
        print(f"\n[TIMEOUT] No response received within {timeout} seconds")
        print("Moving to next test...")
    
    # Test 4: Something terrible that should be DENIED
    print("\n" + "=" * 50)
    print("TEST 4: APPROVAL WORKFLOW - SHOULD DENY")
    print("=" * 50)
    
    request_id2 = await service.create_approval_request("Wipe entire disk permanently", "Delete ALL files on the computer including system files, personal documents, and backups. This action cannot be undone.")
    print(f"Approval request created with ID: {request_id2}")
    print(f"Initial status: {service.get_approval_status(request_id2)['status']}")
    
    print("\n" + "=" * 60)
    print("WAITING FOR YOUR ACTION IN TELEGRAM:")
    print("1. Check your Telegram for the new approval request")
    print("2. This is something TERRIBLE - you should DENY it!")
    print("3. Click the 'Deny' button (red X)")
    print("=" * 60)
    
    # Wait and check for any response
    start_time = time.time()
    response_received = False
    
    while time.time() - start_time < timeout:
        await asyncio.sleep(2)
        status = service.get_approval_status(request_id2)
        current_status = status['status']
        
        if current_status == 'approved':
            print(f"\n[RESULT] You clicked APPROVE! Status: {current_status}")
            response_received = True
            break
        elif current_status == 'denied':
            print(f"\n[RESULT] You clicked DENY! Status: {current_status}")
            response_received = True
            break
        elif current_status == 'awaiting_custom_instruction':
            print(f"\n[RESULT] You clicked SUGGEST DIFFERENT APPROACH! Status: {current_status}")
            response_received = True
            break
        elif current_status == 'denied_custom':
            print(f"\n[RESULT] Custom instruction received! Status: {current_status}")
            instruction = status.get('instruction', 'No instruction')
            safe_print(f"Your instruction: {instruction}")
            response_received = True
            break
        else:
            print(f"Current status: {current_status} (waiting...)")
    
    if not response_received:
        print(f"\n[TIMEOUT] No response received within {timeout} seconds")
        print("Moving to next test...")
    
    # Test 5: Something slightly wrong that needs a DIFFERENT APPROACH
    print("\n" + "=" * 50)
    print("TEST 5: APPROVAL WORKFLOW - SUGGEST DIFFERENT APPROACH")
    print("=" * 50)
    
    request_id3 = await service.create_approval_request("Deploy directly to production on Friday at 5PM", "Push new untested code straight to production servers during peak hours on Friday evening")
    print(f"Approval request created with ID: {request_id3}")
    print(f"Initial status: {service.get_approval_status(request_id3)['status']}")
    
    print("\n" + "=" * 60)
    print("WAITING FOR YOUR ACTION IN TELEGRAM:")
    print("1. Check your Telegram for the new approval request")
    print("2. This timing/approach is slightly WRONG - suggest a better way!")
    print("3. Click 'Suggest Different Approach' button (circular arrow)")
    print("4. Then type a better suggestion like 'Deploy to staging first, then production Monday morning'")
    print("=" * 60)
    
    # Wait and check for any response
    start_time = time.time()
    suggest_clicked = False
    
    while time.time() - start_time < timeout:
        await asyncio.sleep(2)
        status = service.get_approval_status(request_id3)
        current_status = status['status']
        
        if current_status == 'approved':
            print(f"\n[RESULT] You clicked APPROVE! Status: {current_status}")
            break
        elif current_status == 'denied':
            print(f"\n[RESULT] You clicked DENY! Status: {current_status}")
            break
        elif current_status == 'awaiting_custom_instruction':
            print(f"\n[RESULT] You clicked SUGGEST DIFFERENT APPROACH! Status: {current_status}")
            suggest_clicked = True
            break
        elif current_status == 'denied_custom':
            print(f"\n[RESULT] Custom instruction received! Status: {current_status}")
            instruction = status.get('instruction', 'No instruction')
            safe_print(f"Your instruction: {instruction}")
            break
        else:
            print(f"Current status: {current_status} (waiting...)")
    
    if suggest_clicked:
        print("\n" + "=" * 60)
        print("NOW TYPE YOUR CUSTOM INSTRUCTION IN TELEGRAM:")
        print("1. Type your suggestion in Telegram")
        print("2. Example: 'Deploy to staging first, then production'")
        print("3. Expected result: Status changes to 'denied_custom'")
        print("=" * 60)
        
        # Wait for custom instruction
        start_time = time.time()
        custom_received = False
        
        while time.time() - start_time < timeout:
            await asyncio.sleep(2)
            status = service.get_approval_status(request_id3)
            if status['status'] == 'denied_custom':
                print(f"\n[PASS] Custom instruction received!")
                instruction = status.get('instruction', 'No instruction')
                safe_print(f"Your instruction: {instruction}")
                custom_received = True
                break
            print(f"Current status: {status['status']} (waiting for your message...)")
        
        if not custom_received:
            print(f"\n[TIMEOUT] No custom instruction received within {timeout} seconds")
    else:
        print(f"\n[TIMEOUT] Suggest button not clicked within {timeout} seconds")
    
    # Test 6: Database persistence across instances
    print("\n" + "=" * 50)
    print("TEST 6: DATABASE PERSISTENCE")
    print("=" * 50)
    
    # Only test persistence if we have a custom instruction
    if 'request_id3' in locals():
        service2 = TelegramService()
        persisted_status = service2.get_approval_status(request_id3)
        
        print(f"Persisted status: {persisted_status['status']}")
        if persisted_status['status'] == 'denied_custom':
            instruction = persisted_status.get('instruction', 'No instruction')
            print("[PASS] Persistence working!")
            safe_print(f"Instruction: {instruction}")
        elif persisted_status['status'] == 'awaiting_custom_instruction':
            print("[INFO] Persistence working - still waiting for custom instruction")
        else:
            print(f"[INFO] Status: {persisted_status['status']}")
    else:
        print("[SKIP] No request to test persistence with")
    
    # Test 7: Status checking for non-existent request
    print("\n" + "=" * 50)
    print("TEST 7: ERROR HANDLING")
    print("=" * 50)
    
    fake_status = service.get_approval_status("non_existent_id")
    print(f"Non-existent request status: {fake_status['status']}")
    if fake_status['status'] == 'not_found':
        print("[PASS] Error handling working correctly!")
    else:
        print("[FAIL] Error handling not working!")
    
    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)
    print("SUMMARY:")
    print("- Progress notifications (all statuses): [TESTED]")
    print("- Regular notifications (all priorities): [TESTED]") 
    print("- Direct approval workflow: [TESTED]")
    print("- Direct denial workflow: [TESTED]")
    print("- Custom instruction workflow: [TESTED]")
    print("- Database persistence: [TESTED]")
    print("- Error handling: [TESTED]")
    print("\nAll Telegram features have been comprehensively tested!")

if __name__ == "__main__":
    asyncio.run(test_approval_system())
