import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

import dashscope
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_audio_analysis():
    """测试音频分析功能"""
    try:
        # 获取 API key
        api_key = os.getenv('QWEN_API_KEY')
        if not api_key:
            print("Error: DASHSCOPE_API_KEY not found in environment variables")
            return
        print(f"api_key: {api_key}")
        # 设置 API key
        dashscope.api_key = api_key

        # 测试音频 URL
        test_audio_url = "https://dashscope.oss-cn-beijing.aliyuncs.com/audios/welcome.mp3"
        
        # 构建消息
        messages = [
            {
                "role": "user",
                "content": [
                    {"audio": test_audio_url},
                    {"text": "这段音频在说什么?"}
                ]
            }
        ]

        print("Sending request with messages:", messages)

        # 调用 API
        response = dashscope.MultiModalConversation.call(
            api_key=api_key,
            model="qwen-audio-turbo",
            messages=messages
        )

        print("\nResponse type:", type(response))
        print("\nFull response:", response)

        # 检查响应
        if hasattr(response, 'status_code'):
            print("\nStatus code:", response.status_code)
            
            if response.status_code == 200:
                if hasattr(response, 'output'):
                    print("\nOutput:", response.output)
                    if hasattr(response.output, 'choices'):
                        content = response.output.choices[0].message.content
                        print("\nContent:", content)
                    else:
                        print("No choices in output")
                else:
                    print("No output in response")
            else:
                print("Error:", getattr(response, 'message', 'Unknown error'))
        else:
            print("No status_code in response")

    except Exception as e:
        print(f"Error occurred: {type(e)}")
        print(f"Error message: {str(e)}")
        import traceback
        print("\nTraceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_audio_analysis() 