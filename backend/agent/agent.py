"""
AI Agent Orchestrator for Skylark Drones BI Agent
Handles natural language queries and tool execution
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

from .tools import AVAILABLE_TOOLS, execute_tool
from .prompts import SYSTEM_PROMPT

load_dotenv()

logger = logging.getLogger(__name__)


class BiAgent:
    """Business Intelligence Agent with LLM and tool execution"""
    
    def __init__(self):
        # Use Groq API (OpenAI-compatible)
        api_key = os.getenv("GROQ_API_KEY", os.getenv("LLM_API_KEY"))
        base_url = "https://api.groq.com/openai/v1"
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        # Use Groq's production model
        self.model = "openai/gpt-oss-120b"
        self.conversation_history: Dict[str, List[Dict]] = {}
    
    async def process_query(
        self,
        user_message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the agent
        
        Args:
            user_message: User's natural language question
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dict with answer, metrics, insights, and data quality info
        """
        logger.info(f"Processing query: {user_message[:100]}...")
        
        # Get or create conversation history
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        history = self.conversation_history[conversation_id]
        
        # Add user message
        history.append({
            "role": "user",
            "content": user_message
        })
        
        # Prepare messages for LLM
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history[-10:]  # Keep last 10 messages for context
        ]
        
        # Call LLM with function calling
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=AVAILABLE_TOOLS,
            tool_choice="auto",
            temperature=0.1  # Low temperature for factual responses
        )
        
        assistant_message = response.choices[0].message
        
        # Handle tool calls
        tool_results = []
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"Executing tool: {function_name} with args: {function_args}")
                
                # Execute tool
                result = await execute_tool(function_name, function_args)
                tool_results.append({
                    "tool": function_name,
                    "result": result
                })
                
                # Add tool response to history
                history.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call.model_dump()]
                })
                history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
            
            # Get final response after tool execution
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                *history[-10:]
            ]
            
            final_response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1
            )
            
            answer = final_response.choices[0].message.content
        else:
            answer = assistant_message.content
        
        # Add assistant response to history
        history.append({
            "role": "assistant",
            "content": answer
        })
        
        # Extract structured data from tool results
        metrics = []
        insights = []
        data_quality = []
        charts = []
        
        for tool_result in tool_results:
            result_data = tool_result["result"]
            
            # Extract metrics
            if "metrics" in result_data:
                metrics.extend(result_data["metrics"])
            
            # Extract insights
            if "insights" in result_data:
                insights.extend(result_data["insights"])
            
            # Extract data quality
            if "data_quality" in result_data:
                data_quality.extend(result_data["data_quality"])
            
            # Extract chart data
            if "chart_data" in result_data:
                charts.append(result_data["chart_data"])
        
        return {
            "answer": answer,
            "metrics": metrics,
            "insights": insights,
            "data_quality": data_quality,
            "charts": charts,
            "tool_calls": [t["tool"] for t in tool_results]
        }
    
    def clear_conversation(self, conversation_id: str):
        """Clear conversation history"""
        if conversation_id in self.conversation_history:
            del self.conversation_history[conversation_id]


# Global agent instance
agent = BiAgent()
