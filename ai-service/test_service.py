#!/usr/bin/env python3
"""
AI Service 测试脚本

测试 AI 服务的各个端点是否正常工作。

使用方法:
    python test_service.py [AI_SERVICE_URL]

默认 URL: http://localhost:8001
"""

import sys
import json
import httpx


def test_health(base_url: str) -> bool:
    """测试健康检查端点"""
    print("\n1. Testing /health endpoint...")
    try:
        response = httpx.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Status: {data['status']}")
            print(f"   ✓ Collection count: {data['collection_count']}")
            print(f"   ✓ Model: {data['model_info']['name']}")
            print(f"   ✓ Dimension: {data['model_info']['dimension']}")
            return True
        else:
            print(f"   ✗ Failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_embedding(base_url: str) -> bool:
    """测试单个嵌入生成"""
    print("\n2. Testing /embeddings endpoint...")
    try:
        response = httpx.post(
            f"{base_url}/embeddings",
            json={"text": "CNC铣刀"},
            timeout=30,
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Embedding dimension: {data['dimension']}")
            print(f"   ✓ First 5 values: {data['embedding'][:5]}")
            return True
        else:
            print(f"   ✗ Failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_batch_embedding(base_url: str) -> bool:
    """测试批量嵌入生成"""
    print("\n3. Testing /embeddings/batch endpoint...")
    try:
        texts = ["铣刀", "车刀", "钻头"]
        response = httpx.post(
            f"{base_url}/embeddings/batch",
            json={"texts": texts},
            timeout=30,
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Count: {data['count']}")
            print(f"   ✓ Dimension: {data['dimension']}")
            return True
        else:
            print(f"   ✗ Failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_vector_operations(base_url: str) -> bool:
    """测试向量操作"""
    print("\n4. Testing vector operations...")

    # 添加向量
    print("   Adding vector...")
    try:
        response = httpx.post(
            f"{base_url}/vectors/add",
            json={
                "id": "test-cutter-001",
                "text": "CNC立铣刀，直径10mm，4刃，适用于铝合金加工",
                "metadata": {
                    "name": "测试铣刀",
                    "category": "end_mill",
                    "diameter": 10.0,
                },
            },
            timeout=30,
        )
        if response.status_code != 200:
            print(f"   ✗ Add failed with status: {response.status_code}")
            return False
        print("   ✓ Vector added")

        # 搜索向量
        print("   Searching vectors...")
        response = httpx.post(
            f"{base_url}/vectors/search",
            json={
                "query": "铣刀",
                "top_k": 5,
            },
            timeout=30,
        )
        if response.status_code != 200:
            print(f"   ✗ Search failed with status: {response.status_code}")
            return False

        data = response.json()
        print(f"   ✓ Found {data['total']} results")
        if data['results']:
            print(f"   ✓ Top result: {data['results'][0]['id']} (score: {data['results'][0]['score']:.4f})")

        # 获取向量详情
        print("   Getting vector details...")
        response = httpx.get(
            f"{base_url}/vectors/test-cutter-001",
            timeout=10,
        )
        if response.status_code != 200:
            print(f"   ✗ Get failed with status: {response.status_code}")
            return False

        data = response.json()
        print(f"   ✓ Vector ID: {data['id']}")
        print(f"   ✓ Document: {data['document'][:50]}...")

        # 删除向量
        print("   Deleting vector...")
        response = httpx.delete(
            f"{base_url}/vectors/test-cutter-001",
            timeout=10,
        )
        if response.status_code != 200:
            print(f"   ✗ Delete failed with status: {response.status_code}")
            return False
        print("   ✓ Vector deleted")

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def main():
    """主测试函数"""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"

    print(f"Testing AI Service at: {base_url}")
    print("=" * 50)

    results = []
    results.append(("Health Check", test_health(base_url)))
    results.append(("Single Embedding", test_embedding(base_url)))
    results.append(("Batch Embedding", test_batch_embedding(base_url)))
    results.append(("Vector Operations", test_vector_operations(base_url)))

    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
