import asyncio
from typing import Any
from mcp.types import TextContent
from telegram.error import TelegramError
from telegram_service import TelegramService

class ToolHandler:
    def __init__(self):
        self.telegram = TelegramService()

    async def handle_tool_call(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Route tool calls to appropriate handlers."""
        try:
            if name == "notify_progress":
                return await self._handle_progress(arguments)
            elif name == "request_approval":
                return await self._handle_approval(arguments)
            elif name == "send_notification":
                return await self._handle_notification(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except TelegramError as e:
            return [TextContent(type="text", text=f"Telegram error: {str(e)}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_progress(self, args: dict[str, Any]) -> list[TextContent]:
        """Handle progress notification."""
        result = await self.telegram.send_progress(
            message=args["message"],
            status=args["status"]
        )
        return [TextContent(type="text", text=result)]

    async def _handle_approval(self, args: dict[str, Any]) -> list[TextContent]:
        """Handle approval request and wait for response."""
        # Check if we should wait for response
        wait_for_response = args.get("wait_for_response", True)
        
        if wait_for_response:
            # Create approval request and return request ID
            request_id = await self.telegram.create_approval_request(
                action=args["action"],
                details=args.get("details", "")
            )
            
            # Poll for response with timeout
            timeout = args.get("timeout", 300)
            import time
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                status = self.telegram.get_approval_status(request_id)
                
                if status['status'] == 'approved':
                    return [TextContent(type="text", text=f"✅ User approved: {args['action']}")]
                elif status['status'] == 'denied':
                    return [TextContent(type="text", text=f"❌ User denied: {args['action']}")]
                elif status['status'] == 'pending':
                    # Wait a bit before checking again
                    await asyncio.sleep(2)
                else:
                    break
            
            # Timeout
            return [TextContent(type="text", text=f"⏰ Approval request timed out for: {args['action']} (ID: {request_id})")]
        else:
            # Just send the request without waiting
            request_id = await self.telegram.create_approval_request(
                action=args["action"],
                details=args.get("details", "")
            )
            return [TextContent(type="text", text=f"Approval request sent (ID: {request_id})")]

    async def _handle_notification(self, args: dict[str, Any]) -> list[TextContent]:
        """Handle general notification."""
        result = await self.telegram.send_notification(
            message=args["message"],
            priority=args.get("priority", "normal")
        )
        return [TextContent(type="text", text=result)]
