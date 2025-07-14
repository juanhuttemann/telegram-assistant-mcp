# Telegram MCP Agent

🤖 **Connect your AI agents to Telegram!** This MCP server allows AI assistants to send you notifications, progress updates, and request approvals directly through Telegram.

## ✨ What Does This Do?

- 📱 **Get notified** when your AI agent is working on tasks
- 🤔 **Approve or deny** actions with 3 simple buttons (no typing needed!)
- 🔄 **Smart alternatives** - provide custom instructions when you want a different approach
- 📊 **Track progress** of long-running operations
- 🔔 **Receive alerts** with different priority levels
- ✅ **Stay in control** of what your AI agent does

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Your Telegram Bot
1. Open Telegram and find [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. **Save the bot token** - you'll need it!

### Step 2: Get Your Chat ID
1. Start a chat with your new bot
2. Send any message to it
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for `"chat":{"id":` and **copy that number**

### Step 3: Install & Configure
```bash
# Clone the project
git clone https://github.com/juanhuttemann/telegram-assistant-mcp.git
cd telegram-assistant-mcp

# Install dependencies
pip install -r requirements.txt

# Setup your credentials
cp .env.example .env
# Edit .env with your bot token and chat ID
```

### Step 4: Test It Works
```bash
python run_tests.py
```
Select option 1 for a quick test. You should receive test messages in Telegram!

## 🔧 Connect to Your AI Assistant

To use this with your AI assistant (Claude, Cursor, VS Code, etc.), add this configuration:

### For Claude Desktop
Edit your `claude_desktop_config.json` file:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "telegram-messenger": {
      "command": "python",
      "args": ["C:\\path\\to\\telegram-assistant-mcp\\mcp_telegram_tool.py"],
      "cwd": "C:\\path\\to\\telegram-assistant-mcp"
    }
  }
}
```

### For Cursor/VS Code
Add to your MCP settings:

```json
{
  "mcpServers": {
    "telegram-messenger": {
      "command": "python",
      "args": ["path/to/telegram-assistant-mcp/mcp_telegram_tool.py"],
      "cwd": "path/to/telegram-assistant-mcp"
    }
  }
}
```

**📝 Note:** Replace the path with your actual project location!

## 🎯 How Your AI Will Use This

Once connected, your AI assistant can:

1. **Send you progress updates:**
   - "🔄 **WORKING** - Installing dependencies..."
   - "✅ **SUCCESS** - Tests passed!"
   - "❌ **ERROR** - Build failed"

2. **Request approval with simple options:**
   - "🤔 **APPROVAL REQUIRED** - Delete old files?"
   - Click: ✅ Approve | ❌ Deny | 🔄 Suggest Different Approach
   - Provide custom instructions when suggesting alternatives

3. **Send notifications:**
   - "🔔 Task completed successfully!"
   - "⚠️ Warning: High memory usage detected"

## 🛠️ Available Tools

| Tool | Description | Timeout | Persistence |
|------|-------------|---------|-------------|
| `notify_progress` | Send progress updates with status emojis | Instant | No |
| `request_approval` | Ask for approval with 3 buttons + custom instructions | 30 min | Only custom instructions |
| `send_notification` | Send notifications with priority levels | Instant | No |
| `check_approval_status` | Check status of pending approval by request ID | Instant | From database |

## 🎯 Simple Approval System

When your AI requests approval, you get **3 clear options**:

### Approval Options:
- **✅ Approve** - Standard approval, proceed with the action
- **❌ Deny** - Simple denial, don't proceed  
- **🔄 Suggest Different Approach** - Provide custom instructions for alternative method

### How it Works:
1. **✅ Approve** - Immediate approval, agent proceeds
2. **❌ Deny** - Immediate denial, agent stops 
3. **🔄 Suggest Different Approach** - You type custom instructions, agent receives your specific guidance

**Workflow for Custom Instructions:**
- Click "🔄 Suggest Different Approach"  
- System asks you to type your suggestion
- You type: "do this like that" or any specific instruction
- Agent receives: "❌ User denied with custom instructions: [your text]"
- Your instruction persists across tool calls until handled

**Example Custom Instructions:**
- "Try using a different API endpoint instead"
- "Use a safer approach with backup first" 
- "Get user confirmation before proceeding"
- "Try this during off-peak hours"

## 🤖 Sample Agent Prompts

### For Testing (Use Everything):
```
You are a helpful AI assistant with Telegram integration for real-time communication and approval workflows. 

TELEGRAM COMMUNICATION REQUIREMENTS:
- Send progress updates for EVERY task using notify_progress (started, in_progress, completed, error)
- Request approval via Telegram before ANY action that: creates/modifies files, installs packages, makes API calls, changes configurations, accesses external services, or could impact the system
- Send notifications for important events, warnings, completions, and status changes
- Use different priority levels (low, normal, high, urgent) based on importance

APPROVAL WORKFLOW:
- Always explain what you want to do and why approval is needed
- Wait for user response via Telegram buttons (Approve/Deny/Suggest Different Approach)
- If denied with custom instructions, follow the user's alternative approach
- Use 30-minute timeout for realistic response times

TESTING FOCUS:
Be extremely proactive with Telegram communication - use all notification types, request approvals frequently, and demonstrate the full approval workflow including custom instruction handling. This helps test the complete Telegram MCP integration.

Your goal is to be helpful while showcasing all Telegram features through natural workflow integration.
```

### For Production (Balanced):
```
KEEP ME UPDATED VIA TELEGRAM: Send me progress updates for long tasks, ask for my approval before risky actions (like deleting files, deploying, or spending money), and notify me when important things happen. Use the Telegram tools to stay in touch!
```

### For Critical Systems (Maximum Safety):
```
TELEGRAM APPROVAL REQUIRED: Ask for my approval via Telegram before ANY file modification, system change, API call, or potentially impactful action. Send detailed progress updates and notify me immediately of any errors or warnings. Safety first!
```

**Pick the style that matches your needs!**

## 🧪 Testing

The project includes comprehensive tests to verify all Telegram MCP functionality. All tests are located in the `tests/` directory.

### Available Tests

#### 1. **Basic Feature Test** (`test_all_features.py`)
Quick test of core functionality - suitable for development and basic verification.

**What it tests:**
- Progress notifications (all status types)
- Regular notifications (all priority levels)  
- One approval request with 30-second timeout:
  - ✅ **"Pet a cute cat"** (test any button you want)

**How to run:**
```bash
cd telegram-assistant-mcp
python tests/test_all_features.py
```

**Expected outcome:**
- Several notification messages appear in your Telegram
- One approval request appears
- Test waits 30 seconds for you to click any button
- Test completes regardless of your response (~40 seconds total)

#### 2. **Interactive Approval Test** (`test_telegram_service.py`)
Comprehensive test requiring manual interaction - tests the complete approval workflow.

**What it tests:**
- All notification types with realistic scenarios
- Complete 3-button approval workflow:
  - ✅ **Approve** scenario: "Pet a cute cat"
  - ❌ **Deny** scenario: "Wipe entire disk permanently" 
  - 🔄 **Suggest Different Approach**: "Deploy directly to production on Friday at 5PM"
- Custom instruction workflow
- Database persistence across service instances
- Error handling

**How to run:**
```bash
cd telegram-assistant-mcp
python tests/test_telegram_service.py
```

**What to expect:**
1. **Automatic tests** (progress + regular notifications)
2. **Manual interaction required** - you'll see prompts like:
   ```
   ============================================================
   WAITING FOR YOUR ACTION IN TELEGRAM:
   1. Check your Telegram for the approval request
   2. This is something nice - you should APPROVE it
   3. Click the 'Approve' button (green checkmark)
   ============================================================
   ```
3. **Three approval scenarios** - each waits 60 seconds for your response
4. **Database persistence verification**
5. **Complete test takes ~5 minutes** (depending on your response time)

### Testing Instructions

#### Before Running Tests

1. **Ensure your bot is configured:**
   ```bash
   # Check your .env file has:
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

2. **Make sure you can receive messages:**
   - Start a chat with your bot in Telegram
   - Send `/start` or any message to activate the chat

#### During Interactive Tests

**For the "Pet a cute cat" request:**
- Click ✅ **Approve** (this tests direct approval)

**For the "Wipe entire disk permanently" request:**
- Click ❌ **Deny** (this tests direct denial)

**For the "Deploy directly to production on Friday at 5PM" request:**
- Click 🔄 **Suggest Different Approach** 
- When prompted, type a better suggestion like:
  - "Deploy to staging first, then production Monday morning"
  - "Run tests before deploying"
  - "Deploy during maintenance window"

#### Test Results

**Success indicators:**
- `[PASS]` messages for each test phase
- `[RESULT]` messages showing detected actions
- Database persistence working message
- No `[FAIL]` or `[TIMEOUT]` messages

**Common issues:**
- `[TIMEOUT]` - You didn't respond within 60 seconds
- `[FAIL]` - Technical issue (check your bot token/chat ID)
- Unicode errors - Usually harmless display issues on Windows

### Quick Test Runner

Use the interactive test runner for easy test selection:

```bash
cd telegram-assistant-mcp
python run_tests.py
```

This gives you options to:
- Run basic test only (quick, automated)
- Run interactive test only (comprehensive, manual)
- Run all tests
- Exit

### Automated Testing

For CI/CD or automated testing, use the basic feature test:

```bash
# Quick automated test (no user interaction)
python tests/test_all_features.py

# Check if service initializes correctly
python -c "from telegram_service import TelegramService; TelegramService(); print('OK')"
```

### Test Database

- Tests use the same `approval_responses.db` as production
- Database is cleaned on each service initialization
- Custom instructions are persisted between test runs
- You can safely delete the `.db` file to reset test state

## 🐛 Troubleshooting

### Common Issues

1. **"TELEGRAM_BOT_TOKEN environment variable is required"**
   - Make sure you've set the environment variable correctly
   - Verify the token is valid and not expired

2. **"TELEGRAM_CHAT_ID environment variable is required"**
   - Ensure you've set the TELEGRAM_CHAT_ID environment variable
   - Make sure the chat ID is a valid integer (no quotes in the value)

3. **"TELEGRAM_CHAT_ID must be a valid integer"**
   - The chat ID should be numeric only (e.g., 123456789)
   - Remove any quotes or special characters from the chat ID

4. **"Chat not found" error**
   - Ensure you've started a conversation with your bot
   - Verify the chat ID is correct

5. **Import errors**
   - Run `pip install -r requirements.txt` to install dependencies
   - Check your Python version (3.8+ required)

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For support, please open an issue on the project repository or contact the maintainers.
