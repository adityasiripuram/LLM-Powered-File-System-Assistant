"""
llm_file_assistant.py

LLM tool-calling integration with fs_tools.
"""

import json
import openai
from fs_tools import read_file, list_files, write_file, search_in_file

openai.api_key = "YOUR_API_KEY"


tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a resume file and extract text",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string"},
                    "extension": {"type": "string"}
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": "Search for a keyword in a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "keyword": {"type": "string"}
                },
                "required": ["filepath", "keyword"]
            }
        }
    }
]


def call_llm(user_query: str):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_query}],
        tools=tools,
        tool_choice="auto"
    )

    message = response["choices"][0]["message"]

    if message.get("tool_calls"):
        tool_call = message["tool_calls"][0]
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])

        # Dispatch tool
        if function_name == "read_file":
            result = read_file(**arguments)
        elif function_name == "list_files":
            result = list_files(**arguments)
        elif function_name == "search_in_file":
            result = search_in_file(**arguments)
        else:
            result = {"error": "Unknown function"}

        return result

    return message["content"]


if __name__ == "__main__":
    while True:
        query = input("User: ")
        result = call_llm(query)
        print("Assistant:", json.dumps(result, indent=2))
        