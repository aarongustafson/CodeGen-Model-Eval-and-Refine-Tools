import os
import json
import time
import json
import uuid
from dotenv import dotenv_values
from openai import AzureOpenAI

# Load environment variables from .env file
CONFIG = dotenv_values(".env")
API_BASE = CONFIG["AZURE_OPENAI_API_BASE"]
DEPLOYMENT = CONFIG["AZURE_OPENAI_API_MODEL"]
API_VERSION = CONFIG["AZURE_OPENAI_API_VERSION"]
API_KEY = CONFIG["AZURE_OPENAI_API_KEY"]
ENDPOINT = API_BASE + "openai/deployments/" + DEPLOYMENT + "/chat/completions?api-version=" + API_VERSION
ITERATIONS = int(CONFIG["ITERATIONS_PER_PROMPT"])
TEMP = float(CONFIG["TEMPERATURE"])
TOP_P = float(CONFIG["TOP_P"])
MAX_TOKENS = int(CONFIG["MAX_TOKENS"])
SLEEP = int(CONFIG["SLEEP_TIME"])
EXTENSION = CONFIG["OUTPUT_EXTENSION"]

# headers
headers = {  
    "Content-Type": "application/json",  
    "api-key": API_KEY  
}

client = AzureOpenAI(
    azure_endpoint=API_BASE,
    api_key=API_KEY,
    api_version=API_VERSION,
)

instructions = [
  "You are an AI programming assistant.",
  "You return only code snippets with NO OTHER TEXT, code fences, etc.",
  "Assume your responses will be used in a code editor within an existing HTML document.",
  # "Your responses only include the amount of HTML required to properly and validly fulfill the request.",
  "You may include inline CSS or JavaScript, but only as much as absolutely necessary."
]

def get_code_response(system_prompt, prompt):
    print(f"Prompt: {prompt}")
    messages = [
        {
          "role": "system",
          "content": [{
            "type": "text",
            "text": " ".join(instructions)
          }]
        },
        {
          "role": "user",
          "content": [{
            "type": "text",
            "text": prompt
          }]
        }
    ]

    completion = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=TEMP,
        top_p=TOP_P,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )
  
    result = json.loads(completion.to_json())
    code = result['choices'][0]['message']['content']
    print(f"Response: {code}")
    return code

def process_prompts(test_folder, system_prompt, prefix, prompt, prompt_index):
    prompt_folder = os.path.join(test_folder, str(prompt_index))
    os.makedirs(prompt_folder, exist_ok=True)

    unique_responses = set()

    for _ in range(ITERATIONS):
        full_prompt = f"{prefix} {prompt}".strip()
        response = get_code_response(system_prompt, full_prompt)
        if response not in unique_responses:
            unique_responses.add(response)
            filename = os.path.join(prompt_folder, f"{uuid.uuid4()}.html")
            with open(filename, 'w') as response_file:
                response_file.write(response)
        time.sleep(SLEEP)  # To avoid hitting rate limits



def main():
    # Load the JSON file
    with open('tests.json', 'r') as file:
        data = json.load(file)

    for test in data['tests']:
        test_title = test['title']
        test_folder = os.path.join('output', test_title)
        os.makedirs(test_folder, exist_ok=True)

        prefix = test.get('prefix', '')

        for prompt_index, prompt in enumerate(test['prompts'], start=1):
            process_prompts(test_folder, instructions, prefix, prompt, prompt_index)

if __name__ == "__main__":
    main()