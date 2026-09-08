class ToolRegistry:

    def __init__(self):
        self.tools = {}

    def register(
        self,
        name: str,
        function,
        description: str,
        parameters: dict
    ):
        if name in self.tools:
            raise ValueError(
                f"Tool '{name}' is already registered."
            )

        self.tools[name] = {
            "function": function,
            "definition": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters
                }
            }
        }

    def get_tool(self, name: str):
        tool = self.tools.get(name)

        if tool is None:
            return None

        return tool["function"]

    def get_definitions(self):
        return [
            tool["definition"]
            for tool in self.tools.values()
        ]

    def has_tool(self, name: str):
        return name in self.tools

    def list_tools(self):
        return list(self.tools.keys())