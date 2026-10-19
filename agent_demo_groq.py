"""
Skylark Drones AI Agent - Working Demo with Groq
"""

import asyncio
import pandas as pd
from groq import Groq
import json

# Load data once
deals_df = pd.read_excel('Deal funnel Data.xlsx')
wo_df = pd.read_excel('Work_Order_Tracker Data.xlsx')
wo_df.columns = wo_df.iloc[0]
wo_df = wo_df[1:].reset_index(drop=True)


# Tool definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_pipeline",
            "description": "Get pipeline metrics. Can filter by sector.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sector": {"type": "string", "description": "Optional sector filter"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financials",
            "description": "Get billed, collected, receivables.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_delayed_projects",
            "description": "Get delayed or not started work orders.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_sectors",
            "description": "Compare two sectors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sector1": {"type": "string"},
                    "sector2": {"type": "string"}
                },
                "required": ["sector1", "sector2"]
            }
        }
    }
]


def get_pipeline(sector=None):
    """Calculate pipeline"""
    filtered = deals_df[deals_df['Deal Status'].isin(['Open', 'Won'])]
    if sector:
        filtered = filtered[filtered['Sector/service'] == sector]
    
    valued = filtered[filtered['Masked Deal value'].notna()]
    total = valued['Masked Deal value'].astype(float).sum()
    count = len(valued)
    
    return {
        "total_pipeline": f"₹{total:,.0f}",
        "deal_count": count,
        "average": f"₹{total/count:,.0f}" if count > 0 else "N/A",
        "sector": sector or "All"
    }


def get_financials():
    """Calculate financial metrics"""
    billed = pd.to_numeric(wo_df['Billed Value in Rupees (Excl of GST.) (Masked)'], errors='coerce').sum()
    collected = pd.to_numeric(wo_df['Collected Amount in Rupees (Incl of GST.) (Masked)'], errors='coerce').sum()
    receivable = pd.to_numeric(wo_df['Amount Receivable (Masked)'], errors='coerce').sum()
    
    return {
        "billed": f"₹{billed:,.0f}",
        "collected": f"₹{collected:,.0f}",
        "receivable": f"₹{receivable:,.0f}",
        "collection_rate": f"{collected/(billed*1.18)*100:.1f}%"
    }


def get_delayed_projects():
    """Get delayed projects"""
    delayed = wo_df[wo_df['Execution Status'].isin(['Not Started', 'Pause / struck'])]
    return {
        "count": len(delayed),
        "statuses": delayed['Execution Status'].value_counts().to_dict()
    }


def compare_sectors(sector1, sector2):
    """Compare two sectors"""
    result = {}
    for sector in [sector1, sector2]:
        pipeline = get_pipeline(sector)
        wo_sector = wo_df[wo_df['Sector'] == sector]
        billed = pd.to_numeric(wo_sector['Billed Value in Rupees (Excl of GST.) (Masked)'], errors='coerce').sum()
        
        result[sector] = {
            "pipeline": pipeline["total_pipeline"],
            "deals": pipeline["deal_count"],
            "billed": f"₹{billed:,.0f}",
            "work_orders": len(wo_sector)
        }
    
    return result


def execute_tool(name, args):
    """Execute a tool"""
    if name == "get_pipeline":
        return get_pipeline(args.get("sector"))
    elif name == "get_financials":
        return get_financials()
    elif name == "get_delayed_projects":
        return get_delayed_projects()
    elif name == "compare_sectors":
        return compare_sectors(args["sector1"], args["sector2"])
    return {"error": "Unknown tool"}


SYSTEM_PROMPT = """You are a Business Intelligence Agent for Skylark Drones.

You analyze sales pipeline (Deals) and project execution (Work Orders) data.

Available sectors: Mining, Renewables, Railways, Powerline, Others, Construction, DSP, Tender

Use tools to get data. Provide executive-friendly answers with insights.

If asked about a sector that doesn't exist (like "Energy"), say you don't find it and suggest alternatives."""


def process_query(message: str):
    """Process a query through the agent"""
    client = Groq(api_key="GROQ_API_KEY")
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message}
    ]
    
    # First LLM call - using llama-3.3-70b-versatile (latest Groq model)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.1
    )
    
    assistant_msg = response.choices[0].message
    
    # Handle tool calls
    if assistant_msg.tool_calls:
        for tool_call in assistant_msg.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            
            print(f"  🔧 Calling tool: {func_name}({func_args})")
            
            result = execute_tool(func_name, func_args)
            
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [{"id": tool_call.id, "type": "function", "function": {"name": func_name, "arguments": json.dumps(func_args)}}]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
        
        # Final response
        final_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.1
        )
        
        return final_response.choices[0].message.content
    else:
        return assistant_msg.content


def main():
    """Run the agent demo"""
    print("=" * 80)
    print("SKYLARK DRONES - AI BUSINESS INTELLIGENCE AGENT")
    print("=" * 80)
    print()
    
    test_queries = [
        "What is our current pipeline?",
        "How much pipeline do we have in Mining?",
        "Which projects are delayed?",
        "How much have we billed and collected?",
        "Compare Mining and Renewables",
        "How is Energy sector performing?"  # Should handle gracefully
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"Query {i}: {query}")
        print('='*80)
        
        answer = process_query(query)
        print(f"\n{answer}")
    
    print(f"\n{'='*80}")
    print("✅ AGENT DEMO COMPLETE")
    print('='*80)


if __name__ == "__main__":
    main()
