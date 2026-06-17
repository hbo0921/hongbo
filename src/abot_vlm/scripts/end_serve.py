#!/usr/bin/env python
'''
Copyright (c) [Zachary]
本代码受版权法保护，未经授权禁止任何形式的复制、分发、修改等使用行为。
Author:Zachary
'''
import rospy
from abot_vlm.srv import LLMQuery, LLMQueryResponse
import os
from volcenginesdkarkruntime import Ark

pre_PROMPT = '只输出最终的答案，例如答案为1'

def handle_llm_query(req):
    '''
    处理LLM查询请求
    '''
    last_PROMPT = req.query
    
    MODEL = 'ep-20251028185048-2lgcx'
    while True:
        # 访问大模型API
        client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=os.getenv('8e8f6d34-160a-4a5e-87a1-0eadc53b8198'),
        )
        PROMPT = pre_PROMPT + last_PROMPT
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT}
                    ]
                }
            ]
        )
        result = completion.choices[0].message.content.strip()
        rospy.loginfo(f"LLM response: {result}")
        
        # 检查结果是否为数字且是个位数
        if result.isdigit() and len(result) == 1:
            return LLMQueryResponse(result)

def llm_server():
    '''
    LLM服务端
    '''
    rospy.init_node('llm_server')
    s = rospy.Service('llm_query', LLMQuery, handle_llm_query)
    rospy.loginfo("LLM server is ready to handle queries.")
    rospy.spin()

if __name__ == "__main__":
    llm_server()
