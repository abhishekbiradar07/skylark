"""
Full system test - Tests agent with Groq LLM and Monday.com integration
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from agent.agent import BiAgent

async def main():
    print("=" * 80)
    print("SKYLARK DRONES - FULL SYSTEM TEST")
    print("Testing AI Agent with Groq LLM + Monday.com Integration")
    print("=" * 80)
    print()
    
    # Initialize agent
    print("🤖 Initializing AI Agent...")
    agent = BiAgent()
    print(f"   ✓ Using model: {agent.model}")
    print()
    
    # Test queries
    test_queries = [
        "What is our current pipeline?",
        "How much pipeline do we have in Mining sector?",
        "Which projects are delayed?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"📝 Query {i}: {query}")
        print("-" * 80)
        
        try:
            result = await agent.process_query(query, conversation_id="test")
            
            print(f"💬 Answer: {result['answer']}")
            print()
            
            if result.get('metrics'):
                print("📊 Metrics:")
                for metric in result['metrics']:
                    print(f"   • {metric['label']}: {metric['value']}")
                print()
            
            if result.get('insights'):
                print("💡 Insights:")
                for insight in result['insights']:
                    print(f"   • {insight}")
                print()
            
            if result.get('data_quality'):
                print("⚠️  Data Quality:")
                for dq in result['data_quality']:
                    print(f"   • {dq}")
                print()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
        
        print("=" * 80)
        print()
    
    print("✅ SYSTEM TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(main())
