def get_conversation_starters():
    """
    Returns a dictionary of conversation starters organized by category.
    """
    return {
        "General Assistance": [
            "Can you help me understand what Model Context Protocol (MCP) is?",
            "What are the key differences between OpenAI and Anthropic models?",
            "I need help with a writing task, which model would be best?",
            "How can I use MCP to optimize my AI conversations?",
            "Can you explain the strengths and weaknesses of different AI models?"
        ],
        "Coding & Technical": [
            "I need help debugging this Python code snippet.",
            "Which model is best for helping me learn JavaScript?",
            "Can you explain how to build a REST API?",
            "Help me understand Docker containers.",
            "I want to optimize my SQL queries, which model should I use?"
        ],
        "Creative Writing": [
            "Help me brainstorm ideas for a science fiction story.",
            "I need assistance writing a persuasive essay about climate change.",
            "Can you help me craft a professional email to a potential client?",
            "Which model is best for creative writing assistance?",
            "I want to create marketing copy for my new product."
        ],
        "Research & Analysis": [
            "I need to analyze the pros and cons of different renewable energy sources.",
            "Help me understand the latest developments in machine learning.",
            "Which model is best for in-depth research assistance?",
            "I want to compare different investment strategies.",
            "Can you help me evaluate sources for my academic paper?"
        ],
        "Problem Solving": [
            "I'm trying to decide between two job offers. Can you help me analyze them?",
            "Which model is best for complex reasoning tasks?",
            "Help me create a study plan for my upcoming exams.",
            "I need to develop a business strategy for my startup.",
            "Can you help me troubleshoot issues with my home network?"
        ],
        "Model Exploration": [
            "Show me what GPT-4o is capable of.",
            "Demonstrate the reasoning abilities of Claude 3.5 Sonnet.",
            "What types of tasks is Claude 3 Opus best at?",
            "Compare the coding abilities of different models.",
            "What are the latest improvements in AI language models?"
        ],
        "Tech & Development": [
            "Explain the concept of machine learning in simple terms",
            "What are the key differences between frontend and backend development?",
            "How do APIs work and why are they important?",
            "What are some best practices for writing clean code?",
            "Can you explain what cloud computing is?",
            "Analyze my screen capture and help me improve my workflow",
            "Review this screenshot of my code and suggest improvements"
        ],
    }