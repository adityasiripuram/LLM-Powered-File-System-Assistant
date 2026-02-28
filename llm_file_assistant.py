"""
llm_file_assistant.py
Azure OpenAI LLM integration with tool calling.
"""

import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
from fs_tools import read_file, list_files, write_file, search_in_file

# -------------------------
# Load Environment Variables
# -------------------------

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")


# -------------------------
# Tool Definitions
# -------------------------

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
                "required": ["filepath"],
            },
        },
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
                    "extension": {"type": "string"},
                },
                "required": ["directory"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": "Search for keyword in file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "keyword": {"type": "string"},
                },
                "required": ["filepath", "keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["filepath", "content"],
            },
        },
    },
]


# -------------------------
# Tool Dispatcher
# -------------------------

def execute_tool(function_name, arguments):
    if function_name == "read_file":
        return read_file(**arguments)
    elif function_name == "list_files":
        return list_files(**arguments)
    elif function_name == "search_in_file":
        return search_in_file(**arguments)
    elif function_name == "write_file":
        return write_file(**arguments)
    else:
        return {"error": "Unknown function"}


# -------------------------
# Agent Loop
# -------------------------

# def run_agent(user_query: str):
#     messages = [{"role": "user", "content": user_query}]

#     while True:
#         response = client.chat.completions.create(
#             model=DEPLOYMENT_NAME,  # Azure requires deployment name
#             messages=messages,
#             tools=tools,
#             tool_choice="auto",
#         )

#         message = response.choices[0].message

#         if message.tool_calls:
#             tool_call = message.tool_calls[0]
#             function_name = tool_call.function.name
#             arguments = json.loads(tool_call.function.arguments)

#             print(f"\n🔧 Tool Called: {function_name}")
#             print(f"📥 Arguments: {arguments}")

#             result = execute_tool(function_name, arguments)

#             messages.append(message)
#             messages.append(
#                 {
#                     "role": "tool",
#                     "tool_call_id": tool_call.id,
#                     "content": json.dumps(result),
#                 }
#             )
#         else:
#             return message.content

def run_agent(user_query: str):
    messages = [{"role": "user", "content": user_query}]

    while True:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message

        # If model wants to call tools
        if message.tool_calls:

            # Append assistant message first
            messages.append(message)

            # Handle ALL tool calls (not just first)
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                print(f"\n🔧 Tool Called: {function_name}")
                print(f"📥 Arguments: {arguments}")

                result = execute_tool(function_name, arguments)

                # Append tool response
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

        else:
            return message.content
# -------------------------
# CLI Interface
# -------------------------

if __name__ == "__main__":
    print("📂 Azure LLM File Assistant Ready (type 'exit' to quit)\n")

    while True:
        query = input("User: ")
        if query.lower() == "exit":
            break

        try:
            result = run_agent(query)
            print("\n🤖 Assistant:")
            print(result)
            print("\n" + "-" * 50)
        except Exception as e:
            print("Error:", str(e))