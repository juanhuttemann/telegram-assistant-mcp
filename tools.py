from mcp.types import Tool

def get_tools() -> list[Tool]:
    """Define available MCP tools."""
    return [
        Tool(
            name="notify_progress",
            description="Send progress notification to user via Telegram",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Progress message to send to user"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["started", "in_progress", "completed", "error"],
                        "description": "Status of the current task"
                    }
                },
                "required": ["message", "status"]
            }
        ),
        Tool(
            name="request_approval",
            description="Request user approval before proceeding with an action and wait for response. Users can approve, deny, or provide specific denial instructions (alternative approaches, pause requests, or request more information).",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Description of the action requiring approval"
                    },
                    "details": {
                        "type": "string",
                        "description": "Additional details about the action"
                    },
                    "wait_for_response": {
                        "type": "boolean",
                        "description": "Whether to wait for user response (default: true)",
                        "default": True
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds to wait for response (default: 300)",
                        "default": 300
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="send_notification",
            description="Send a general notification to the user",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to send to user"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "normal", "high", "urgent"],
                        "description": "Priority level of the notification",
                        "default": "normal"
                    }
                },
                "required": ["message"]
            }
        )
    ]
