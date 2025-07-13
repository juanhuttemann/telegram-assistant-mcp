from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters
from config import TOKEN, CHAT_ID, STATUS_EMOJIS, PRIORITY_EMOJIS
import asyncio

class TelegramService:
    def __init__(self):
        self.bot = Bot(token=TOKEN)
        self.chat_id = CHAT_ID
        self.last_approval_response = None
        self.pending_approvals = {}
        self.approval_responses = {}
        self.app = None
        self._listening_started = False

    async def send_progress(self, message: str, status: str) -> str:
        """Send progress notification with status emoji."""
        emoji = STATUS_EMOJIS.get(status, "📝")
        formatted_message = f"{emoji} **{status.upper()}**\n{message}"
        
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=formatted_message,
            parse_mode="Markdown"
        )
        return f"Progress notification sent: {status} - {message}"

    async def send_approval_request(self, action: str, details: str = "") -> str:
        """Send approval request to user."""
        message = f"🤔 **APPROVAL REQUIRED**\n\n**Action:** {action}\n"
        if details:
            message += f"**Details:** {details}\n"
        message += "\nPlease respond with 'approve' or 'deny' to proceed."
        
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message,
            parse_mode="Markdown"
        )
        return f"Approval request sent for: {action}"

    async def send_notification(self, message: str, priority: str = "normal") -> str:
        """Send general notification with priority emoji."""
        emoji = PRIORITY_EMOJIS.get(priority, "📝")
        formatted_message = f"{emoji} {message}"
        
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=formatted_message
        )
        return f"Notification sent: {message}"

    async def send_approval_request_and_wait(self, action: str, details: str = "", timeout: int = 300) -> str:
        """Send approval request and wait for user response."""
        # Send the approval request
        await self.send_approval_request(action, details)
        
        # Create a unique request ID
        import time
        request_id = str(int(time.time()))
        
        # Create an event to wait for response
        response_event = asyncio.Event()
        self.pending_approvals[request_id] = {
            'event': response_event,
            'response': None,
            'action': action
        }
        
        # Start listening for messages if not already started
        if not self.app:
            await self._start_listening()
        
        try:
            # Wait for response with timeout
            await asyncio.wait_for(response_event.wait(), timeout=timeout)
            response = self.pending_approvals[request_id]['response']
            del self.pending_approvals[request_id]
            
            if response and response.lower() in ['approve', 'approved', 'yes', 'ok']:
                await self.send_notification(f"✅ Action '{action}' has been approved!", "high")
                return "approved"
            else:
                await self.send_notification(f"❌ Action '{action}' has been denied.", "high")
                return "denied"
                
        except asyncio.TimeoutError:
            del self.pending_approvals[request_id]
            await self.send_notification(f"⏰ Approval request for '{action}' timed out.", "high")
            return "timeout"
    
    async def _start_listening(self):
        """Start listening for Telegram messages."""
        self.app = Application.builder().token(TOKEN).build()
        
        # Add message handler
        self.app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, self._handle_message))
        
        # Start the application in a background task
        asyncio.create_task(self._run_bot())
    
    async def _run_bot(self):
        """Run the bot polling in background."""
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
    
    async def _handle_message(self, update: Update, context):
        """Handle incoming messages."""
        if update.effective_chat.id != self.chat_id:
            return
            
        message_text = update.message.text.lower().strip()
        
        # Find pending approval that matches
        for request_id, approval_data in list(self.pending_approvals.items()):
            if approval_data['response'] is None:
                approval_data['response'] = message_text
                approval_data['event'].set()
                break
    
    async def create_approval_request(self, action: str, details: str = "") -> str:
        """Create approval request and return request ID without waiting."""
        # Start listening if not already started
        if not self._listening_started:
            await self._ensure_listening()
        
        # Create unique request ID
        import time
        request_id = f"approval_{int(time.time() * 1000)}"
        
        # Store request
        self.approval_responses[request_id] = {
            'action': action,
            'details': details,
            'status': 'pending',
            'response': None,
            'timestamp': time.time()
        }
        
        # Send the approval request
        message = f"🤔 APPROVAL REQUIRED (ID: {request_id})\n\nAction: {action}\n"
        if details:
            message += f"Details: {details}\n"
        message += f"\nPlease respond with 'approve {request_id}' or 'deny {request_id}' to proceed."
        
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message
        )
        
        return request_id
    
    def get_approval_status(self, request_id: str) -> dict:
        """Get the current status of an approval request."""
        if request_id in self.approval_responses:
            return self.approval_responses[request_id]
        return {'status': 'not_found'}
    
    async def _ensure_listening(self):
        """Ensure we're listening for messages."""
        if not self._listening_started:
            self.app = Application.builder().token(TOKEN).build()
            self.app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, self._handle_approval_response))
            
            # Start the application in background
            asyncio.create_task(self._run_approval_bot())
            self._listening_started = True
    
    async def _run_approval_bot(self):
        """Run the approval bot in background."""
        try:
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
        except Exception as e:
            print(f"Bot error: {e}")
    
    async def _handle_approval_response(self, update: Update, context):
        """Handle approval responses."""
        if update.effective_chat.id != self.chat_id:
            return
        
        message_text = update.message.text.strip()
        
        # Parse approval responses like "approve approval_123" or "deny approval_123"
        parts = message_text.lower().split()
        if len(parts) >= 2:
            action = parts[0]  # approve or deny
            request_id = parts[1]  # approval_123
            
            if request_id in self.approval_responses:
                if action in ['approve', 'approved', 'yes', 'ok']:
                    self.approval_responses[request_id]['status'] = 'approved'
                    self.approval_responses[request_id]['response'] = 'approved'
                    await self.send_notification(f"✅ Approved: {self.approval_responses[request_id]['action']}", "high")
                elif action in ['deny', 'denied', 'no']:
                    self.approval_responses[request_id]['status'] = 'denied'
                    self.approval_responses[request_id]['response'] = 'denied'
                    await self.send_notification(f"❌ Denied: {self.approval_responses[request_id]['action']}", "high")
        
        # Also handle old-style responses for backward compatibility
        for request_id, approval_data in list(self.pending_approvals.items()):
            if approval_data['response'] is None:
                approval_data['response'] = message_text.lower()
                approval_data['event'].set()
                break
