import os
import time
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_llm(prompt, retries=3):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=400
            )

            return response.choices[0].message.content

        except Exception as e:
            if attempt < retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                return f"LLM request failed after retries: {str(e)}"


def get_embedding(text, retries=3):
    for attempt in range(retries):
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )

            return response.data[0].embedding

        except Exception as e:
            if attempt < retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                raise Exception(
                    f"Embedding request failed after retries: {str(e)}"
                )
