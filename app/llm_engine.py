from openai import OpenAI

def llm_reply(system_prompt:str,client: OpenAI, messages:list,temperature)->str:
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        temperature=temperature,
        messages=messages
    )
    return response.choices[0].message.content