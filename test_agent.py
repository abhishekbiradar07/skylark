"""
Test the AI Agent directly
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from agent.agent import agent


async def test_agent():
    """Test the agent with sample queries"""
    
    print("=" * 80)
    print("SKYLARK DRONES - AI AGENT TEST")
    print("=" * 80)
    print()
    
    test_queries = [
        "What is our current pipeline?",
        "How much pipeline do we have in Mining?",
        "Which projects are delayed?",
        "How much have we billed and collected?",
        "Compare Mining and Renewables sectors"
    ]
    
    conversation_id = "test-session"
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"Query {i}: {query}")
        print('='*80)
        
        result = await agent.process_query(query, conversation_id)
        
        print(f"\n📝 Answer:")
        print(result["answer"])
        
        if result.get("metrics"):
            print(f"\n📊 Metrics:")
            for metric in result["metrics"]:
                print(f"  • {metric['label']}: {metric['value']}")
        
        if result.get("insights"):
            print(f"\n💡 Insights:")
            for insight in result["insights"]:
                print(f"  • {insight}")
        
        if result.get("data_quality"):
            print(f"\n⚠️  Data Quality:")
            for issue in result["data_quality"]:
                print(f"  • {issue}")
        
        if result.get("tool_calls"):
            print(f"\n🔧 Tools Used: {', '.join(result['tool_calls'])}")
    
    print(f"\n{'='*80}")
    print("✅ AGENT TEST COMPLETE")
    print('='*80)


if __name__ == "__main__":
    asyncio.run(test_agent())
