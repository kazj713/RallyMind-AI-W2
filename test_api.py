"""
API 测试脚本
"""

import requests
import time
import sys


def test_health_check():
    """测试健康检查端点"""
    print("测试健康检查端点...")
    try:
        response = requests.get("http://localhost:8000/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ 健康检查通过")
        return True
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False


def test_readiness_check():
    """测试就绪检查端点"""
    print("测试就绪检查端点...")
    try:
        response = requests.get("http://localhost:8000/readiness")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        print("✅ 就绪检查通过")
        return True
    except Exception as e:
        print(f"❌ 就绪检查失败: {e}")
        return False


def main():
    print("=" * 50)
    print("API 端点测试")
    print("=" * 50)
    
    # 等待服务启动
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                break
        except:
            if i < max_retries - 1:
                print(f"等待服务启动... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print("❌ 服务启动超时")
                sys.exit(1)
    
    # 运行测试
    tests = [
        test_health_check,
        test_readiness_check,
    ]
    
    results = []
    for test in tests:
        results.append(test())
        time.sleep(0.5)
    
    # 总结
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"测试结果: {passed}/{total} 通过")
    
    if all(results):
        print("✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
