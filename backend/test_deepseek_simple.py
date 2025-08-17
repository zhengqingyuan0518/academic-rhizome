# test_deepseek_simple.py
# 放在 backend/ 目录下，直接运行测试

import os
import sys

# 设置你的API密钥（临时测试用）
API_KEY = "sk-94c18ee1ad00439bb8afd253a2d88f48"  # 替换为你的实际密钥

def test_with_requests():
    """使用requests测试DeepSeek API"""
    print("🧪 测试1: 使用requests库")
    
    import requests
    import json
    
    # url = "https://api.deepseek.com"
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello, say hi"}
        ],
        "max_tokens": 50
    }
    
    try:
        print(f"📡 发送请求到: {url}")
        print(f"🔑 使用密钥: {API_KEY[:10]}...")
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📊 状态码: {response.status_code}")
        print(f"📝 响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"✅ 成功! AI回复: {content}")
            return True
        else:
            print(f"❌ 失败! 状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def test_with_openai():
    """使用OpenAI库测试DeepSeek API"""
    print("\n🧪 测试2: 使用OpenAI库")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        print("📡 使用OpenAI客户端发送请求...")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello, say hi"}
            ],
            max_tokens=50
        )
        
        content = response.choices[0].message.content
        print(f"✅ 成功! AI回复: {content}")
        return True
        
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def test_cypher_generation():
    """测试Cypher语句生成"""
    print("\n🧪 测试3: Cypher语句生成")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        system_prompt = """你是一个Neo4j Cypher查询生成助手。根据用户的自然语言描述，生成相应的Cypher语句。
        
规则：
1. 只返回有效的Cypher语句
2. 对于学者，使用标签 :Scholar，属性包括 name, affiliation
3. 创建节点时使用MERGE而不是CREATE

示例：
输入："添加一个学者张三，来自清华大学"
输出：MERGE (s:Scholar {name: "张三", affiliation: "清华大学"}) RETURN s"""
        
        user_input = "添加一个教授，姓名是李四，任教于北京大学"
        
        print(f"🎯 测试输入: {user_input}")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            max_tokens=200,
            temperature=0.1
        )
        
        cypher = response.choices[0].message.content.strip()
        print(f"✅ 生成的Cypher: {cypher}")
        
        # 验证是否包含关键词
        if any(keyword in cypher.upper() for keyword in ['MERGE', 'MATCH', 'RETURN']):
            print("✅ Cypher语句验证通过!")
            return True
        else:
            print("❌ 生成的不是有效的Cypher语句")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def main():
    print("🚀 DeepSeek API 完整测试")
    print("=" * 50)
    
    if not API_KEY or API_KEY == "sk-你的真实API密钥":
        print("❌ 请先设置你的真实API密钥!")
        print("修改脚本中的 API_KEY 变量")
        return
    
    # 依次执行测试
    test1 = test_with_requests()
    test2 = test_with_openai()
    test3 = test_cypher_generation()
    
    print("\n" + "=" * 50)
    print("📊 测试总结:")
    print(f"requests测试: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"OpenAI库测试: {'✅ 通过' if test2 else '❌ 失败'}")
    print(f"Cypher生成测试: {'✅ 通过' if test3 else '❌ 失败'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 所有测试通过! DeepSeek API工作正常!")
    else:
        print("\n😞 部分测试失败，需要进一步排查")

if __name__ == "__main__":
    main()