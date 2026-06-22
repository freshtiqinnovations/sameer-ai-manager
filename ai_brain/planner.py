from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv("/root/sameer_ai_manager/.env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RULES=open("/root/sameer_ai_manager/ai_brain/master_rules.txt").read()

def ai_plan(prompt):
    r=client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL","gpt-5.5"),
        messages=[
            {"role":"system","content":RULES},
            {"role":"user","content":prompt}
        ],
        temperature=0.7
    )

    return r.choices[0].message.content

if __name__=="__main__":
    while True:
        q=input("AI> ")
        print(ai_plan(q))
