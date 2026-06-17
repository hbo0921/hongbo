#!/usr/bin/env python

#coding: utf-8
import os
from volcenginesdkarkruntime import Ark
client = Ark(
    api_key=os.environ.get("8e8f6d34-160a-4a5e-87a1-0eadc53b8198"),
    # The base URL for model invocation
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    )
completion = client.chat.completions.create(
    # 替换为你的推理接入点 ID
    model="ep-20251028192142-mqtgb", 
    messages=[
        {"role": "user", "content": "Hello"}
    ]
)
print(completion.choices[0].message)
