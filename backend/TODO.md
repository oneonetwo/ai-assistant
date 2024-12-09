1. 整理分析收录笔记的时候，添加创建手册按钮
2. 创建笔记可以上传附件，附件可以下载
3. 创建完成，弹窗可以回助手和查看笔记详情页
4， 新建计划页面，需要进行及联操作。先进行分类，。然后标签，状态，具体的手册
5.

现在需要对带有音频文件的聊天进行处理。 
处理的demo如下：
“”“
# URL
        import dashscope
        
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
            model="qwen-audio-turbo-latest",
            messages=messages
        )
"""
1. 模型使用 model="qwen-audio-turbo-latest",  api_key使用  QWEN_API_KEY ，只能通过dashscope.MultiModalConversation.call的方式调用阿里的模型处理
2. 处理方式跟图片聊天的的处理方式一样，但是不使用流式，参数跟带有图片的聊天也一样
3. 参数如下： file是链接。 跟图片的处理逻辑一样，需要写入文件表中，
{
    "message": "请帮我分析这个文件：\n",
    "file": "https://ai-assistant-wen.oss-cn-beijing.aliyuncs.com/chat/uploads/1733743740083-432259e5-4813-4eec-814f-24b5eab51e62.mp3",
    "file_name": "28-WebComponent：像搭积木一样构建Web应用_For_vip_user_001.mp3",
    "file_type": "audio/mpeg",
    "system_prompt": "你是一个专业的文件分析助手"
}
1. 请开发这个接口