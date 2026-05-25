#!/usr/bin/env python3
"""
AI Service 多版本测试脚本

测试所有 AI 服务版本的功能。

使用方法:
    python test_all_versions.py
"""

import sys
import time
import httpx
import subprocess
import signal
import os
from pathlib import Path


def test_version(version_name, dockerfile, port=8001):
    """测试单个版本"""
    print(f"\n{'='*60}")
    print(f"测试版本: {version_name}")
    print(f"{'='*60}")

    # 构建镜像
    print(f"\n1. 构建镜像...")
    build_cmd = f"docker build -f {dockerfile} -t cnc-ai-service-test:{version_name} ."
    print(f"   命令: {build_cmd}")

    try:
        result = subprocess.run(
            build_cmd.split(),
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            print(f"   ✗ 构建失败: {result.stderr}")
            return False
        print("   ✓ 镜像构建成功")
    except subprocess.TimeoutExpired:
        print("   ✗ 构建超时")
        return False
    except Exception as e:
        print(f"   ✗ 构建错误: {e}")
        return False

    # 运行容器
    print(f"\n2. 启动容器...")
    container_name = f"cnc-ai-test-{version_name}"
    run_cmd = f"docker run -d --name {container_name} -p {port}:8001 cnc-ai-service-test:{version_name}"
    print(f"   命令: {run_cmd}")

    try:
        result = subprocess.run(
            run_cmd.split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"   ✗ 启动失败: {result.stderr}")
            return False
        print("   ✓ 容器启动成功")
    except Exception as e:
        print(f"   ✗ 启动错误: {e}")
        return False

    # 等待服务启动
    print(f"\n3. 等待服务启动...")
    time.sleep(10)

    # 测试健康检查
    print(f"\n4. 测试健康检查...")
    try:
        response = httpx.get(f"http://localhost:{port}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 状态: {data['status']}")
            print(f"   ✓ 模型: {data['model_info']['name']}")
            print(f"   ✓ 维度: {data['model_info']['dimension']}")
            print(f"   ✓ 后端: {data['model_info']['backend']}")
        else:
            print(f"   ✗ 健康检查失败: {response.status_code}")
            cleanup_container(container_name)
            return False
    except Exception as e:
        print(f"   ✗ 健康检查错误: {e}")
        cleanup_container(container_name)
        return False

    # 测试嵌入生成
    print(f"\n5. 测试嵌入生成...")
    try:
        response = httpx.post(
            f"http://localhost:{port}/embeddings",
            json={"text": "CNC铣刀测试"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 嵌入维度: {data['dimension']}")
            print(f"   ✓ 前5个值: {data['embedding'][:5]}")
        else:
            print(f"   ✗ 嵌入生成失败: {response.status_code}")
            cleanup_container(container_name)
            return False
    except Exception as e:
        print(f"   ✗ 嵌入生成错误: {e}")
        cleanup_container(container_name)
        return False

    # 测试向量操作
    print(f"\n6. 测试向量操作...")
    try:
        # 添加向量
        response = httpx.post(
            f"http://localhost:{port}/vectors/add",
            json={
                "id": "test-001",
                "text": "测试向量",
                "metadata": {"test": True}
            },
            timeout=30
        )
        if response.status_code == 200:
            print("   ✓ 向量添加成功")
        else:
            print(f"   ✗ 向量添加失败: {response.status_code}")
            cleanup_container(container_name)
            return False

        # 搜索向量
        response = httpx.post(
            f"http://localhost:{port}/vectors/search",
            json={"query": "测试", "top_k": 5},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 搜索成功，找到 {data['total']} 个结果")
        else:
            print(f"   ✗ 搜索失败: {response.status_code}")
            cleanup_container(container_name)
            return False

    except Exception as e:
        print(f"   ✗ 向量操作错误: {e}")
        cleanup_container(container_name)
        return False

    # 获取镜像大小
    print(f"\n7. 获取镜像大小...")
    try:
        result = subprocess.run(
            f"docker images cnc-ai-service-test:{version_name} --format '{{{{.Size}}}}'".split(),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            size = result.stdout.strip()
            print(f"   ✓ 镜像大小: {size}")
        else:
            print("   ✗ 无法获取镜像大小")
    except Exception as e:
        print(f"   ✗ 获取镜像大小错误: {e}")

    # 清理
    print(f"\n8. 清理资源...")
    cleanup_container(container_name)

    print(f"\n✓ 版本 {version_name} 测试通过!")
    return True


def cleanup_container(container_name):
    """清理容器"""
    try:
        subprocess.run(
            f"docker stop {container_name}".split(),
            capture_output=True,
            timeout=30
        )
        subprocess.run(
            f"docker rm {container_name}".split(),
            capture_output=True,
            timeout=30
        )
        print("   ✓ 容器已清理")
    except Exception as e:
        print(f"   ✗ 清理错误: {e}")


def main():
    """主函数"""
    print("AI Service 多版本测试")
    print("=" * 60)

    # 测试版本列表
    versions = [
        ("standard", "Dockerfile", 8001),
        ("onnx", "Dockerfile.lite", 8002),
        ("fastembed", "Dockerfile.fastembed", 8003),
    ]

    results = []

    for version_name, dockerfile, port in versions:
        try:
            success = test_version(version_name, dockerfile, port)
            results.append((version_name, success))
        except KeyboardInterrupt:
            print("\n测试被中断")
            sys.exit(1)
        except Exception as e:
            print(f"\n测试 {version_name} 时出错: {e}")
            results.append((version_name, False))

    # 显示测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    all_passed = True
    for version_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {version_name}: {status}")
        if not success:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("所有版本测试通过!")
        return 0
    else:
        print("部分版本测试失败!")
        return 1


if __name__ == "__main__":
    sys.exit(main())