import json

from groq import Groq

from config import Config

from FunctionCalling.ToolRegistry import (
    TOOL_REGISTRY
)


class FunctionCallingManager:

    def __init__(self):

        print(
            "Function Calling Manager Initialized"
        )

        if not Config.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=Config.GROQ_API_KEY
        )

        self.model = Config.GROQ_MODEL

        self.tools = [

            {
                "type": "function",
                "function": {
                    "name": "search_documents",
                    "description": (
                        "Search the uploaded RAGX "
                        "documents for information "
                        "relevant to the user's question."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": (
                                    "The question or "
                                    "information to search "
                                    "for in the documents."
                                )
                            }
                        },
                        "required": [
                            "query"
                        ]
                    }
                }
            }

        ]

    def run(self, user_query):

        if not user_query or not user_query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        messages = [
            {
                "role": "user",
                "content": user_query
            }
        ]

        response = (
            self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
        )

        message = response.choices[0].message

        if not message.tool_calls:

            return {
                "tool_called": False,
                "answer": message.content
            }

        messages.append(message)

        for tool_call in message.tool_calls:

            function_name = (
                tool_call.function.name
            )

            arguments = json.loads(
                tool_call.function.arguments
            )

            print()
            print(
                "=" * 60
            )
            print(
                "TOOL REQUESTED BY LLM"
            )
            print(
                "=" * 60
            )

            print(
                "Function :",
                function_name
            )

            print(
                "Arguments:",
                arguments
            )

            tool = TOOL_REGISTRY.get(
                function_name
            )

            if tool is None:

                raise ValueError(
                    f"Unknown tool requested: "
                    f"{function_name}"
                )

            result = tool(
                **arguments
            )

            print(
                "\nTool executed successfully."
            )

            print(
                "Result count:",
                len(result)
                if isinstance(result, list)
                else 1
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": (
                        tool_call.id
                    ),
                    "content": json.dumps(
                        result,
                        ensure_ascii=False
                    )
                }
            )

        final_response = (
            self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools
            )
        )

        final_message = (
            final_response
            .choices[0]
            .message
        )

        return {
            "tool_called": True,
            "answer": final_message.content,
            "tool_results": result
        }