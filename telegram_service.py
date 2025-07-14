from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters
from config import TOKEN, CHAT_ID, STATUS_EMOJIS, PRIORITY_EMOJIS
import asyncio
import time
import sqlite3
import os

class TelegramService:
    def __init__(self):
        self.bot = Bot(token=TOKEN)
        self.chat_id = CHAT_ID
        self.approval_responses = {}
        self.app = None
        self._listening_started = False
        self.db_path = os.path.join(os.path.dirname(__file__), 'approval_responses.db')
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for approval responses."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS approval_responses (
                    request_id TEXT PRIMARY KEY,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    instruction TEXT,
                    timestamp REAL NOT NULL
                )
            ''')
            # Create index for faster lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_status 
                ON approval_responses(status)
            ''')
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
    
    def _clean_database(self):
        """Clean database - only use when explicitly needed."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self._init_database()
    
    def _save_approval_response(self, request_id: str, data: dict):
        """Save approval response to database - only for custom instructions."""
        # Only save if it's a custom instruction denial that needs to persist
        if data.get('status') in ['awaiting_custom_instruction', 'denied_custom']:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO approval_responses 
                    (request_id, action, status, instruction, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    request_id,
                    data.get('action', ''),
                    data.get('status', ''),
                    data.get('instruction', ''),
                    data.get('timestamp', time.time())
                ))
                conn.commit()
                conn.close()
            except sqlite3.Error as e:
                print(f"Database save error: {e}")
    
    def _load_approval_response(self, request_id: str) -> dict:
        """Load approval response from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM approval_responses WHERE request_id = ?', (request_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'action': row[1],
                    'status': row[2],
                    'instruction': row[3],
                    'timestamp': row[4]
                }
            return {'status': 'not_found'}
        except sqlite3.Error as e:
            print(f"Database load error: {e}")
            return {'status': 'not_found'}

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

    
    
    
    async def create_approval_request(self, action: str, details: str = "") -> str:
        """Create approval request and return request ID without waiting."""
        # Start listening if not already started
        if not self._listening_started:
            await self._ensure_listening()
        
        # Create unique request ID
        request_id = f"approval_{int(time.time() * 1000)}"
        
        # Store request in memory only - no need to save pending requests to database
        approval_data = {
            'action': action,
            'details': details,
            'status': 'pending',
            'response': None,
            'timestamp': time.time()
        }
        self.approval_responses[request_id] = approval_data
        
        # Send the approval request with inline buttons
        await self._send_approval_with_buttons(action, details, request_id)
        
        return request_id
    
    def get_approval_status(self, request_id: str) -> dict:
        """Get the current status of an approval request."""
        # First check in-memory storage
        if request_id in self.approval_responses:
            return self.approval_responses[request_id]
        
        # Then check database
        db_response = self._load_approval_response(request_id)
        if db_response['status'] != 'not_found':
            # Update in-memory cache with database data
            self.approval_responses[request_id] = db_response
            return db_response
            
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
        
        # Create simple inline keyboard with 3 clear options
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{request_id}")
            ],
            [
                InlineKeyboardButton("❌ Deny", callback_data=f"deny_{request_id}"),
                InlineKeyboardButton("🔄 Suggest Different Approach", callback_data=f"suggest_{request_id}")
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
        
        # First, check for custom instructions waiting for user input
        for request_id, approval_data in self.approval_responses.items():
            if approval_data.get('status') == 'awaiting_custom_instruction':
                # Process the custom instruction
                escaped_action = self._escape_markdown(approval_data['action'])
                escaped_instruction = self._escape_markdown(message_text)
                
                # Update the approval with custom instruction
                approval_data['status'] = 'denied_custom'
                approval_data['response'] = 'custom'
                approval_data['instruction'] = f"✏️ **CUSTOM INSTRUCTION:** {escaped_instruction}"
                # Save to database
                self._save_approval_response(request_id, approval_data)
                
                # Send confirmation message
                await self.send_notification(
                    f"✅ **CUSTOM INSTRUCTION RECEIVED**\n\n**Original Action:** {escaped_action}\n\n**Your Instruction:** {escaped_instruction}\n\n**Status:** Custom instructions provided to agent",
                    "high"
                )
                return  # Exit early since we processed the custom instruction
        
        # Parse approval responses like "approve approval_123" or "deny approval_123"
        parts = message_text.lower().split()
        if len(parts) >= 2:
            action = parts[0]  # approve or deny
            request_id = parts[1]  # approval_123
            
            if request_id in self.approval_responses:
                if action in ['approve', 'approved', 'yes', 'ok']:
                    self.approval_responses[request_id]['status'] = 'approved'
                    self.approval_responses[request_id]['response'] = 'approved'
                    # No need to save to database - immediate response
                    await self.send_notification(f"✅ Approved: {self.approval_responses[request_id]['action']}", "high")
                elif action in ['deny', 'denied', 'no']:
                    self.approval_responses[request_id]['status'] = 'denied'
                    self.approval_responses[request_id]['response'] = 'denied'
                    self.approval_responses[request_id]['instruction'] = 'Simple denial - no specific instructions provided'
                    # No need to save to database - immediate response
                    await self.send_notification(f"❌ Denied: {self.approval_responses[request_id]['action']}", "high")
        
    
    async def _handle_button_callback(self, update: Update, context):
        """Handle inline button callbacks for approval requests."""
        query = update.callback_query
        await query.answer()
        
        if query.from_user.id != self.chat_id:
            return
        
        callback_data = query.data
        
        # Parse callback data for simplified actions
        if any(callback_data.startswith(prefix) for prefix in ["approve_", "deny_", "suggest_"]):
            parts = callback_data.split("_")
            action_type = parts[0]  # approve, deny, or suggest
            request_id = "_".join(parts[1:])  # approval_123
            
            if request_id in self.approval_responses:
                if action_type == "approve":
                    self.approval_responses[request_id]['status'] = 'approved'
                    self.approval_responses[request_id]['response'] = 'approved'
                    # No need to save to database - immediate response
                    # Escape markdown in action text
                    escaped_action = self._escape_markdown(self.approval_responses[request_id]['action'])
                    await query.edit_message_text(
                        f"✅ **APPROVED**\n\n**Action:** {escaped_action}\n**Status:** Approved by user",
                        parse_mode="Markdown"
                    )
                elif action_type == "deny":
                    self.approval_responses[request_id]['status'] = 'denied'
                    self.approval_responses[request_id]['response'] = 'denied'
                    self.approval_responses[request_id]['instruction'] = 'Simple denial - no specific instructions provided'
                    # No need to save to database - immediate response
                    # Escape markdown in action text
                    escaped_action = self._escape_markdown(self.approval_responses[request_id]['action'])
                    await query.edit_message_text(
                        f"❌ **DENIED**\n\n**Action:** {escaped_action}\n**Status:** Simple denial",
                        parse_mode="Markdown"
                    )
                elif action_type == "suggest":
                    # Handle suggest different approach - wait for custom instruction
                    self.approval_responses[request_id]['status'] = 'awaiting_custom_instruction'
                    self.approval_responses[request_id]['response'] = 'awaiting_custom_instruction'
                    # Save to database - this needs to persist for custom instruction workflow
                    self._save_approval_response(request_id, self.approval_responses[request_id])
                    escaped_action = self._escape_markdown(self.approval_responses[request_id]['action'])
                    await query.edit_message_text(
                        f"🔄 **SUGGEST DIFFERENT APPROACH**\n\n**Original Action:** {escaped_action}\n\n**Please type your suggestion for a different approach in your next message.**",
                        parse_mode="Markdown"
                    )
