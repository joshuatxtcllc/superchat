import json
import re

class MCPHandler:
    """
    Handles Model Context Protocol (MCP) operations, enabling standardized
    interactions between different AI models.
    """
    
    def __init__(self):
        # MCP protocol version
        self.mcp_version = "1.0"
        
        # MCP system message template
        self.mcp_system_message = (
            "You support the Model Context Protocol (MCP) version {version}.\n\n"
            "When responding to user queries, follow these guidelines:\n"
            "1. If you're taking over from another model, review the conversation history and continue seamlessly.\n"
            "2. Clearly identify when you're unsure about something or when a different model might be better suited.\n"
            "3. When appropriate, include structured MCP context information in your response using the format below.\n\n"
            "MCP context should be enclosed in triple backticks with the mcp-json tag, like this:\n"
            "```mcp-json\n"
            "{{\n"
            "  \"protocol\": \"mcp\",\n"
            "  \"version\": \"{version}\",\n"
            "  \"context\": {{\n"
            "    \"model_assessment\": {{\n"
            "      \"confidence\": 0.8,  // confidence on a scale of 0-1\n"
            "      \"reasoning\": \"Brief explanation of model's confidence in the response\",\n"
            "      \"better_suited_models\": []  // list of models better suited (if any)\n"
            "    }},\n"
            "    \"conversation_state\": {{\n"
            "      \"topics\": [\"topic1\", \"topic2\"],  // main topics of conversation\n"
            "      \"pending_questions\": [],  // questions that still need answering\n"
            "      \"key_entities\": []  // important entities in the conversation\n"
            "    }}\n"
            "  }}\n"
            "}}\n"
            "```"
        )
    
    def prepare_messages(self, messages):
        """
        Prepares messages for API calls, adding MCP context if needed.
        """
        # Deep copy to avoid modifying original
        messages_for_api = []
        
        # Add system message with MCP instructions
        messages_for_api.append({
            "role": "system",
            "content": self.mcp_system_message.format(version=self.mcp_version)
        })
        
        # Add user and assistant messages
        for message in messages:
            if message["role"] in ["user", "assistant"]:
                messages_for_api.append({
                    "role": message["role"],
                    "content": message["content"]
                })
        
        return messages_for_api
    
    def extract_mcp_context(self, response):
        """
        Extracts MCP context from a model response if present.
        Returns the extracted context or None if not found.
        """
        # Regex pattern to match MCP context
        pattern = r"```mcp-json\s*(.*?)```"
        match = re.search(pattern, response, re.DOTALL)
        
        if match:
            try:
                # Extract and parse the JSON
                mcp_json_str = match.group(1)
                mcp_context = json.loads(mcp_json_str)
                return mcp_context
            except json.JSONDecodeError:
                return None
        
        return None
