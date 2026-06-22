import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("/root/sameer_ai_manager/.env")

OPENAI_KEY=os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

def ask_ai(prompt):

    try:

        r=client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role":"system",
                    "content":"You are Sameer AI Autonomous Bot Factory. Reply concise and technical."
                },
                {
                    "role":"user",
                    "content":prompt
                }
            ],
            temperature=0.2
        )

        return r.choices[0].message.content

    except Exception as e:
        return f"AI_ERROR: {e}"

if __name__=="__main__":

    q="Test reply only SAMEER_AI_BRAIN_OK"

    print(ask_ai(q))
