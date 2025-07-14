import asyncio
import time
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
            elif name == "check_approval_status":
                return await self._handle_check_status(arguments)
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
            
            # Poll for response with extended timeout for realistic user response times
            timeout = args.get("timeout", 1800)  # 30 minutes default
            start_time = time.time()
            check_interval = 5  # Check every 5 seconds instead of 2
            
            while time.time() - start_time < timeout:
                status = self.telegram.get_approval_status(request_id)
                
                if status['status'] == 'approved':
                    return [TextContent(type="text", text=f"✅ User approved: {args['action']}")]
                elif status['status'] == 'denied':
                    return [TextContent(type="text", text=f"❌ User denied: {args['action']}")]
                elif status['status'] == 'denied_custom':
                    # Handle custom instruction denial
                    instruction = status.get('instruction', 'Simple denial - no specific instructions provided')
                    return [TextContent(type="text", text=f"❌ User denied with custom instructions: {args['action']}\n\n{instruction}")]
                elif status['status'] == 'awaiting_custom_instruction':
                    # Still waiting for user to provide custom instruction - don't timeout yet
                    await asyncio.sleep(check_interval)
                    continue
                elif status['status'] == 'pending':
                    # Wait before checking again
                    await asyncio.sleep(check_interval)
                else:
                    # Unknown status
                    break
            
            # Timeout - but keep the request active in database for later response
            return [TextContent(type="text", text=f"⏳ Approval request is still pending for: {args['action']} (ID: {request_id})\n\nThe request remains active and you can still respond via Telegram. Use this request ID to check status later.")]
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

    async def _handle_check_status(self, args: dict[str, Any]) -> list[TextContent]:
        """Handle checking approval status by request ID."""
        request_id = args["request_id"]
        status = self.telegram.get_approval_status(request_id)
        
        if status['status'] == 'not_found':
            return [TextContent(type="text", text=f"❓ No approval request found with ID: {request_id}")]
        elif status['status'] == 'pending':
            return [TextContent(type="text", text=f"⏳ Approval request '{status.get('action', 'Unknown')}' is still pending (ID: {request_id})")]
        elif status['status'] == 'awaiting_custom_instruction':
            return [TextContent(type="text", text=f"⏳ Waiting for custom instruction for '{status.get('action', 'Unknown')}' (ID: {request_id})")]
        elif status['status'] == 'approved':
            return [TextContent(type="text", text=f"✅ Request '{status.get('action', 'Unknown')}' was approved (ID: {request_id})")]
        elif status['status'] == 'denied':
            return [TextContent(type="text", text=f"❌ Request '{status.get('action', 'Unknown')}' was denied (ID: {request_id})")]
        elif status['status'] == 'denied_custom':
            instruction = status.get('instruction', 'No specific instructions')
            return [TextContent(type="text", text=f"❌ Request '{status.get('action', 'Unknown')}' was denied with custom instructions (ID: {request_id}):\n\n{instruction}")]
        else:
            return [TextContent(type="text", text=f"❓ Unknown status '{status['status']}' for request ID: {request_id}")]
