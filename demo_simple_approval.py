import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_service import TelegramService

async def demo_simple_approval():
    """Demonstrate the simple, clean approval system."""
    print("🎯 Demonstrating Simple Approval System\n")
    
    service = TelegramService()
    
    # Send a progress update
    await service.send_progress("Preparing for deployment", "working")
    
    # Send a simple approval request and wait for response
    print("📤 Sending approval request...")
    print("💬 Please respond in Telegram with 'approve' or 'deny'")
    print("⏰ Waiting for your response (60 seconds)...\n")
    
    response = await service.send_approval_request_and_wait(
        "Deploy to production", 
        "Deploy version 2.1.0 with new features",
        timeout=60
    )
    
    if response == "approved":
        await service.send_progress("Deployment started", "working")
        await service.send_progress("Deployment completed successfully", "success")
        await service.send_notification("🎉 Production deployment successful!", "high")
    elif response == "denied":
        await service.send_notification("❌ Deployment cancelled by user", "high")
    else:
        await service.send_notification("⏰ Deployment timed out - no response", "high")
    
    print(f"🏁 Demo completed with response: {response}")

if __name__ == "__main__":
    asyncio.run(demo_simple_approval())
