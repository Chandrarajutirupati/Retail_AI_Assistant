from groq import Groq

from config import GROQ_API_KEY, MODEL_NAME
from prompts import SYSTEM_PROMPT

client = Groq(api_key=GROQ_API_KEY)


def ask_llm(user_prompt, system_prompt=None):

    if system_prompt is None:
        system_prompt = SYSTEM_PROMPT

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response.choices[0].message.content