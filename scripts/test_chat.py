#!/usr/bin/env python3
"""
Test LLM chat functionality.

Usage:
    python scripts/test_chat.py
    
Make sure the server is running: ./start_server.sh
"""

import requests
import json

API_BASE = "http://localhost:8000"


def test_chat(question: str):
    """Test chat endpoint."""
    print(f"\n{'='*60}")
    print(f"🤔 Question: {question}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            json={
                "question": question,
                "top_k": 5,
                "use_rag": True
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n💡 Answer:\n{data['answer']}\n")
            
            if data.get('sources'):
                print(f"\n📚 Sources ({len(data['sources'])}):")
                for i, src in enumerate(data['sources'], 1):
                    cutter = src.get('cutter', {})
                    name = cutter.get('name', 'Unknown') if isinstance(cutter, dict) else str(cutter)[:50]
                    score = src.get('relevance_score', 0)
                    print(f"  {i}. {name} (score: {score:.2f})")
            
            print(f"\n📊 Model: {data.get('model', 'N/A')} | Provider: {data.get('provider', 'N/A')}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running on http://localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_recommendation():
    """Test tool recommendation endpoint."""
    print(f"\n{'='*60}")
    print(f"🛠️  Tool Recommendation Request")
    print(f"{'='*60}")
    
    request_data = {
        "workpiece_material": "stainless_steel",
        "operation": "finishing",
        "machine_type": "3-axis"
    }
    
    print(f"\n📋 Parameters:")
    print(f"  Material: {request_data['workpiece_material']}")
    print(f"  Operation: {request_data['operation']}")
    print(f"  Machine: {request_data['machine_type']}")
    
    try:
        response = requests.post(
            f"{API_BASE}/recommend/tool",
            json=request_data,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n💡 Recommendation:\n{data['recommendation']}\n")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all tests."""
    print("\n🧪 Testing CNC Tooling Knowledge Base - LLM Features")
    print(f"API Base: {API_BASE}\n")
    
    # Test questions
    questions = [
        "不锈钢精加工推荐什么刀具？",
        "What's the best tool for aluminum milling?",
        "钛合金加工的切削参数怎么设置？",
    ]
    
    for q in questions:
        test_chat(q)
    
    # Test recommendation
    test_recommendation()
    
    print(f"\n{'='*60}")
    print("✅ Tests completed!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
