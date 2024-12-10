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



大家好我是杨景园，接下来我会从四个方面说下这个项目：
1. 首先第一部分我会讲下这个项目是干嘛的
2. 第二部分我会讲下这个项目的技术实现，使用的模型，技术栈，以及项目架构
3. 第三部分我会进行一个整体使用流程演示
4. 第四部分我会讲述下在这段时间深度使用AI编码的感受

首先AI智囊，顾名思义ai知识口袋，是一个整合AI技术，帮助用户进行知识管理，高效学习计划的一个产品。

核心功能主要包含三大模块： 知识管理，学习计划，AI助手。
1. 知识管理：用户可以管理手册，笔记，分类，标签，附件。



四：总结
    这个项目基本70%代码都是cursor写的，我负责的主要工作就是技术选项，方案制定，以及项目的架构设计，代码的review。通过这次的深度使用尼，我有很多的使用感受
    1. AI编码给我们开发人员带来了很大的挑战，说挑战不如说是一种机遇，因为我是前端开发，虽然之前学习多次nodejs，python，sql，mongodb，但是用到的地方很少，实战经验很少，总是感觉自己学的很浅。有了AI编码首先降低了学习的门槛，提高了知识储备，不用深究各种语言API的细节，可以快速上手。  之前不能做的，现在都可以做了，有了任何的想法，都可以快速实现。所以不断学习扩展知识广度，才能知道怎么更好更快的与AI进行交互。
    
    2. cursor使用很方便，但是也有很多局限性，会吞掉一些代码，会经常出现错误，，有时候需要前后端联调，才能知道哪里出错了。通过不断的学习使用磨合，利用AI的优势， 我也总结出了一些cursor的使用技巧。比如如何拆分任务，分布执行，什么时候需要详细的propmt，什么时候只需要给一个简短的需求。
    
    3. 之前总是觉得使用AI编程，会让开发人员很难再去介入，切换出来。其实不然，AI编程可以让我们更专注于技术方案，业务逻辑，更专注于思考，更专注于解决问题，而不是纠结于代码的实现。也很容进行切换开发，不使用AI那就是自己的项目，使用那就是人机协同的项目。


