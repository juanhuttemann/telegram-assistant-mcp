from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters
from config import TOKEN, CHAT_ID, STATUS_EMOJIS, PRIORITY_EMOJIS
import asyncio
import time

class TelegramService:
    def __init__(self):
        self.bot = Bot(token=TOKEN)
        self.chat_id = CHAT_ID
        self.pending_approvals = {}
        self.approval_responses = {}
        self.app = None
        self._listening_started = False
    
    def _escape_markdown(self, text: str) -> str:
        """Escape markdown characters to prevent parsing errors."""
        return text.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')

    async def send_progress(self, message: str, status: str) -> str:
        """Send progress notification with status emoji."""
        emoji = STATUS_EMOJIS.get(status, "📝")
        # Escape markdown characters in user message and status to prevent parsing errors
        escaped_message = self._escape_markdown(message)
        escaped_status = self._escape_markdown(status.upper())
        formatted_message = f"{emoji} **{escaped_status}**\n{escaped_message}"
        
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=formatted_message,
            parse_mode="Markdown"
        )
        return f"Progress notification sent: {status} - {message}"


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
        # Create a unique request ID
        request_id = str(int(time.time()))
        
        # Send approval request with buttons
        await self._send_approval_with_buttons(action, details, request_id)
        
        # Create an event to wait for response
        response_event = asyncio.Event()
        self.pending_approvals[request_id] = {
            'event': response_event,
            'response': None,
            'action': action
        }
        
        # Start listening for messages if not already started
        if not self._listening_started:
            await self._ensure_listening()
        
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
        request_id = f"approval_{int(time.time() * 1000)}"
        
        # Store request
        self.approval_responses[request_id] = {
            'action': action,
            'details': details,
            'status': 'pending',
            'response': None,
            'timestamp': time.time()
        }
        
        # Send the approval request with inline buttons
        await self._send_approval_with_buttons(action, details, request_id)
        
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
            self.app.add_handler(CallbackQueryHandler(self._handle_button_callback))
            
            # Start the application in background
            asyncio.create_task(self._run_bot())
            self._listening_started = True
    
    async def _run_bot(self):
        """Run the bot polling in background."""
        try:
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
        except Exception as e:
            print(f"Bot error: {e}")
    
    async def _send_approval_with_buttons(self, action: str, details: str, request_id: str):
        """Send approval request with inline buttons."""
        # Escape markdown characters in user input
        escaped_action = self._escape_markdown(action)
        escaped_details = self._escape_markdown(details) if details else ""
        
        message = f"🤔 **APPROVAL REQUIRED**\n\n**Action:** {escaped_action}\n"
        if escaped_details:
            message += f"**Details:** {escaped_details}\n"
        
        # Create inline keyboard with approve/deny buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{request_id}"),
                InlineKeyboardButton("❌ Deny", callback_data=f"deny_{request_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
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
    
    async def _handle_button_callback(self, update: Update, context):
        """Handle inline button callbacks for approval requests."""
        query = update.callback_query
        await query.answer()
        
        if query.from_user.id != self.chat_id:
            return
        
        callback_data = query.data
        
        # Parse callback data like "approve_approval_123" or "deny_approval_123"
        if callback_data.startswith("approve_") or callback_data.startswith("deny_"):
            action = callback_data.split("_")[0]  # approve or deny
            request_id = "_".join(callback_data.split("_")[1:])  # approval_123
            
            if request_id in self.approval_responses:
                if action == "approve":
                    self.approval_responses[request_id]['status'] = 'approved'
                    self.approval_responses[request_id]['response'] = 'approved'
                    # Escape markdown in action text
                    escaped_action = self._escape_markdown(self.approval_responses[request_id]['action'])
                    await query.edit_message_text(
                        f"✅ **APPROVED**\n\n**Action:** {escaped_action}\n**Status:** Approved by user",
                        parse_mode="Markdown"
                    )
                elif action == "deny":
                    self.approval_responses[request_id]['status'] = 'denied'
                    self.approval_responses[request_id]['response'] = 'denied'
                    # Escape markdown in action text
                    escaped_action = self._escape_markdown(self.approval_responses[request_id]['action'])
                    await query.edit_message_text(
                        f"❌ **DENIED**\n\n**Action:** {escaped_action}\n**Status:** Denied by user",
                        parse_mode="Markdown"
                    )
