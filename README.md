# Telegram MCP Agent

🤖 **Connect your AI agents to Telegram!** This MCP server allows AI assistants to send you notifications, progress updates, and request approvals directly through Telegram.

## ✨ What Does This Do?

- 📱 **Get notified** when your AI agent is working on tasks
- 🤔 **Approve or deny** actions before they happen
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
git clone https://github.com/your-repo/telegram-mcp-agent.git
cd telegram-mcp-agent

# Install dependencies
pip install -r requirements.txt

# Setup your credentials
cp .env.example .env
# Edit .env with your bot token and chat ID
```

### Step 4: Test It Works
```bash
python test_telegram_service.py
```
You should receive test messages in Telegram!

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
      "args": ["C:\\path\\to\\telegram-mcp-agent\\mcp_telegram_tool.py"],
      "cwd": "C:\\path\\to\\telegram-mcp-agent"
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
      "args": ["path/to/telegram-mcp-agent/mcp_telegram_tool.py"],
      "cwd": "path/to/telegram-mcp-agent"
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

2. **Request approval before actions:**
   - "🤔 **APPROVAL REQUIRED** - Delete old files?"
   - You reply: "approve" or "deny"

3. **Send notifications:**
   - "🔔 Task completed successfully!"
   - "⚠️ Warning: High memory usage detected"

## 🛠️ Available Tools

| Tool | Description | Example |
|------|-------------|----------|
| `notify_progress` | Send progress updates with status | "🔄 **WORKING** - Processing data..." |
| `request_approval` | Ask for user approval | "🤔 **APPROVAL REQUIRED** - Deploy to production?" |
| `send_notification` | Send general notifications | "🔔 Task completed successfully!" |

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
