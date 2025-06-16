import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
# model = "gemini-2.5-flash-preview-04-17"
model = "gemini-2.0-flash"
# model = "gemini-2.0-flash-lite"
def messages_to_content(messages):
    """
    将消息列表转换为Gemini API所需的Content格式
    
    参数:
        messages: 列表，包含字典形式的消息，每个字典有'role'和'content'字段
    
    返回:
        list: Content对象列表
    """
    contents = []
    for message in messages:
        role = message['role']
        # 确保角色映射到Gemini API支持的角色
        if role == 'assistant':
            role = 'model'
        
        content = types.Content(
            role=role,
            parts=[types.Part.from_text(text=message['content'])]
        )
        contents.append(content)
    return contents

def llm_response(messages):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key, )

    contents = messages_to_content(messages)
    generate_content_config = types.GenerateContentConfig(
        temperature=0.65,
        top_p=0.75,
        response_mime_type="text/plain",
    )

    response = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        # print(chunk.text, end="")
        if chunk.text:
            response += chunk.text
        
    return response

if __name__ == "__main__":
    # test the llm_response function with a simple message
    print(
        llm_response([
            {'role': 'user', 
            'content': "1+1=？reply with a explanation."},
        ])
    )

# 示例消息格式转换
contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""1+1=?"""),
            ],
        ),
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text="""1 + 1 = 2
"""),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]