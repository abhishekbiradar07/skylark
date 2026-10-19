"""
Monday.com GraphQL API Client
READ-ONLY operations for Skylark Drones BI Agent
"""

import httpx
import logging
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Load settings from environment
MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")
MONDAY_DEALS_BOARD_ID = os.getenv("MONDAY_DEALS_BOARD_ID")
MONDAY_WORK_ORDERS_BOARD_ID = os.getenv("MONDAY_WORK_ORDERS_BOARD_ID")
MONDAY_API_URL = os.getenv("MONDAY_API_URL", "https://api.monday.com/v2")

# GraphQL queries
QUERIES = {
    "get_board_items": """
        query GetBoardItems($board_id: [ID!]!, $limit: Int!) {
          boards(ids: $board_id) {
            id
            name
            items_page(limit: $limit) {
              cursor
              items {
                id
                name
                column_values {
                  id
                  text
                  value
                  type
                }
              }
            }
          }
        }
    """,
    "get_next_items": """
        query GetNextItems($cursor: String!, $limit: Int!) {
          next_items_page(cursor: $cursor, limit: $limit) {
            cursor
            items {
              id
              name
              column_values {
                id
                text
                value
                type
              }
            }
          }
        }
    """,
    "health_check": """
        query HealthCheck($board_id: [ID!]!) {
          boards(ids: $board_id) {
            id
            name
          }
        }
    """
}


class MondayClient:
    """Monday.com API client with GraphQL support"""
    
    def __init__(self):
        self.api_url = MONDAY_API_URL
        self.headers = {
            "Authorization": f"Bearer {MONDAY_API_TOKEN}",
            "Content-Type": "application/json"
        }
        self.deals_board_id = MONDAY_DEALS_BOARD_ID
        self.work_orders_board_id = MONDAY_WORK_ORDERS_BOARD_ID
    
    async def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query against Monday.com API"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Check for GraphQL errors
                if "errors" in data:
                    error_messages = [err.get("message", str(err)) for err in data["errors"]]
                    raise ValueError(f"GraphQL errors: {', '.join(error_messages)}")
                
                return data.get("data", {})
                
            except httpx.HTTPError as e:
                logger.error(f"Monday.com API error: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error querying Monday.com: {e}")
                raise
    
    async def get_board_items(
        self,
        board_id: str,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get items from a Monday.com board with pagination"""
        query = QUERIES["get_board_items"]
        variables = {
            "board_id": int(board_id),
            "limit": limit
        }
        
        if cursor:
            query = QUERIES["get_next_items"]
            variables = {
                "cursor": cursor,
                "limit": limit
            }
        
        result = await self.execute_query(query, variables)
        
        if cursor:
            return result.get("next_items_page", {})
        else:
            board_data = result.get("boards", [{}])[0]
            return board_data.get("items_page", {})
    
    async def get_all_board_items(self, board_id: str) -> List[Dict[str, Any]]:
        """Get ALL items from a board (handles pagination automatically)"""
        all_items = []
        cursor = None
        
        while True:
            page = await self.get_board_items(board_id, limit=100, cursor=cursor)
            items = page.get("items", [])
            
            if not items:
                break
            
            all_items.extend(items)
            cursor = page.get("cursor")
            
            if not cursor:
                break
        
        logger.info(f"Retrieved {len(all_items)} items from board {board_id}")
        return all_items
    
    async def get_deals(self) -> List[Dict[str, Any]]:
        """Get all items from the Deals board"""
        logger.info(f"Fetching all deals from board {self.deals_board_id}")
        return await self.get_all_board_items(self.deals_board_id)
    
    async def get_work_orders(self) -> List[Dict[str, Any]]:
        """Get all items from the Work Orders board"""
        logger.info(f"Fetching all work orders from board {self.work_orders_board_id}")
        return await self.get_all_board_items(self.work_orders_board_id)
    
    async def health_check(self) -> bool:
        """Check if Monday.com API is accessible"""
        try:
            query = QUERIES["health_check"]
            variables = {"board_id": int(self.deals_board_id)}
            result = await self.execute_query(query, variables)
            return "boards" in result
        except Exception as e:
            logger.error(f"Monday.com health check failed: {e}")
            return False


# Global client instance
monday_client = MondayClient()
