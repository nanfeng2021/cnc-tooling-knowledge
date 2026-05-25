#!/usr/bin/env python3
"""
AI Service 版本选择助手

帮助用户根据需求选择合适的 AI 服务版本。

使用方法:
    python choose_version.py
"""

import sys


def get_user_requirements():
    """获取用户需求"""
    print("AI Service 版本选择助手")
    print("=" * 50)
    print()

    # 1. 环境类型
    print("1. 您的部署环境是什么？")
    print("   [1] 开发/测试环境")
    print("   [2] 生产环境（资源充足）")
    print("   [3] 生产环境（资源受限）")
    print("   [4] 边缘计算/嵌入式设备")
    env_choice = input("请选择 (1-4): ").strip()

    # 2. 资源限制
    print()
    print("2. 您的资源限制如何？")
    print("   [1] 无限制（>4GB 内存，充足磁盘）")
    print("   [2] 中等限制（2-4GB 内存）")
    print("   [3] 严格限制（<2GB 内存）")
    resource_choice = input("请选择 (1-3): ").strip()

    # 3. 精度要求
    print()
    print("3. 您对嵌入精度的要求？")
    print("   [1] 最高精度（开发/测试）")
    print("   [2] 高精度（生产环境）")
    print("   [3] 一般精度（资源受限）")
    precision_choice = input("请选择 (1-3): ").strip()

    return env_choice, resource_choice, precision_choice


def recommend_version(env_choice, resource_choice, precision_choice):
    """根据需求推荐版本"""
    # 计算得分
    scores = {
        "standard": 0,
        "onnx": 0,
        "fastembed": 0
    }

    # 环境类型得分
    if env_choice == "1":  # 开发/测试
        scores["standard"] += 3
        scores["onnx"] += 2
        scores["fastembed"] += 1
    elif env_choice == "2":  # 生产环境（资源充足）
        scores["standard"] += 2
        scores["onnx"] += 3
        scores["fastembed"] += 2
    elif env_choice == "3":  # 生产环境（资源受限）
        scores["standard"] += 1
        scores["onnx"] += 2
        scores["fastembed"] += 3
    elif env_choice == "4":  # 边缘计算
        scores["standard"] += 0
        scores["onnx"] += 1
        scores["fastembed"] += 3

    # 资源限制得分
    if resource_choice == "1":  # 无限制
        scores["standard"] += 3
        scores["onnx"] += 2
        scores["fastembed"] += 1
    elif resource_choice == "2":  # 中等限制
        scores["standard"] += 1
        scores["onnx"] += 3
        scores["fastembed"] += 2
    elif resource_choice == "3":  # 严格限制
        scores["standard"] += 0
        scores["onnx"] += 1
        scores["fastembed"] += 3

    # 精度要求得分
    if precision_choice == "1":  # 最高精度
        scores["standard"] += 3
        scores["onnx"] += 2
        scores["fastembed"] += 1
    elif precision_choice == "2":  # 高精度
        scores["standard"] += 2
        scores["onnx"] += 3
        scores["fastembed"] += 2
    elif precision_choice == "3":  # 一般精度
        scores["standard"] += 1
        scores["onnx"] += 2
        scores["fastembed"] += 3

    # 找到最高分
    max_score = max(scores.values())
    recommended = [k for k, v in scores.items() if v == max_score][0]

    return recommended, scores


def get_version_info(version):
    """获取版本信息"""
    info = {
        "standard": {
            "name": "标准版 (PyTorch)",
            "image_size": "~3 GB",
            "dockerfile": "Dockerfile",
            "requirements": "requirements.txt",
            "app": "app.py",
            "pros": ["最高精度", "支持所有模型", "便于调试"],
            "cons": ["镜像最大", "资源消耗最高", "启动最慢"],
            "command": "docker build -f Dockerfile -t cnc-ai-service:standard ."
        },
        "onnx": {
            "name": "ONNX版",
            "image_size": "~1.5 GB",
            "dockerfile": "Dockerfile.lite",
            "requirements": "requirements-lite.txt",
            "app": "app_onnx.py",
            "pros": ["镜像适中", "性能平衡", "支持模型优化"],
            "cons": ["需要模型导出", "精度略低于标准版"],
            "command": "docker build -f Dockerfile.lite -t cnc-ai-service:onnx ."
        },
        "fastembed": {
            "name": "FastEmbed版",
            "image_size": "~500 MB",
            "dockerfile": "Dockerfile.fastembed",
            "requirements": "requirements-fastembed.txt",
            "app": "app_fastembed.py",
            "pros": ["镜像最小", "启动最快", "资源消耗最低"],
            "cons": ["模型选择有限", "精度略低"],
            "command": "docker build -f Dockerfile.fastembed -t cnc-ai-service:fastembed ."
        }
    }
    return info[version]


def main():
    """主函数"""
    try:
        # 获取用户需求
        env_choice, resource_choice, precision_choice = get_user_requirements()

        # 推荐版本
        recommended, scores = recommend_version(env_choice, resource_choice, precision_choice)
        version_info = get_version_info(recommended)

        # 显示结果
        print()
        print("=" * 50)
        print("推荐结果")
        print("=" * 50)
        print()
        print(f"推荐版本: {version_info['name']}")
        print(f"镜像大小: {version_info['image_size']}")
        print()

        print("版本详情:")
        print(f"  Dockerfile: {version_info['dockerfile']}")
        print(f"  依赖文件: {version_info['requirements']}")
        print(f"  应用代码: {version_info['app']}")
        print()

        print("优点:")
        for pro in version_info['pros']:
            print(f"  ✓ {pro}")
        print()

        print("缺点:")
        for con in version_info['cons']:
            print(f"  ✗ {con}")
        print()

        print("构建命令:")
        print(f"  {version_info['command']}")
        print()

        print("运行命令:")
        if recommended == "fastembed":
            print("  docker-compose -f docker-compose.fastembed.yml up -d")
        else:
            print("  docker-compose up -d")
        print()

        # 显示所有版本得分
        print("版本得分对比:")
        for version, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            info = get_version_info(version)
            print(f"  {info['name']}: {score} 分")
        print()

        # 提供详细文档链接
        print("详细文档:")
        print("  - 版本对比: ai-service/AI_SERVICE_VARIANTS.md")
        print("  - 选择指南: ai-service/VERSION_SELECTION_GUIDE.md")
        print("  - 优化总结: AI_SERVICE_OPTIMIZATION_SUMMARY.md")
        print()

    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()