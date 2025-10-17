# Multi-Model Chat Interface

## Overview

This application is a Streamlit-based web interface that allows users to interact with multiple AI language models through a unified chat interface. The system supports OpenAI and Anthropic models (like GPT-4o and Claude 3.5) and implements the Model Context Protocol (MCP) for standardized model interactions. It features a model recommender that suggests the optimal AI model based on the user's specific task requirements.

**New in Latest Update (October 2025):** Comprehensive AI cost control system with per-model token tracking, spending limits, and circuit breakers to prevent unnecessary spending and protect against service failures.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

1. **Frontend Layer**: Streamlit-based web interface providing a chat-like experience
2. **Model Interaction Layer**: Handlers for different AI model providers 
3. **Model Selection Layer**: Recommendation system for selecting optimal models
4. **Cost Control Layer**: Token tracking, spending limits, and circuit breakers
5. **MCP Implementation**: Support for Model Context Protocol for standardized AI interaction
6. **Persistence Layer**: Local session storage for conversation history

### Architectural Decisions

The application uses Streamlit as the frontend framework due to its simplicity in creating data-focused web applications with Python. This choice allows for rapid development and deployment while maintaining a clean, responsive user interface without requiring extensive frontend skills.

The modular design enables easy addition of new model providers or features without significant refactoring. Each component has a clear responsibility, making the system maintainable and extensible.

## Key Components

### 1. Main Application (app.py)
- Streamlit web interface
- Manages session state
- Coordinates interactions between user and models
- Handles conversation history

### 2. Model Handler (model_handler.py)
- Manages connections to different AI model providers (OpenAI, Anthropic, Google Gemini)
- Abstracts away provider-specific API differences
- Maintains model metadata (capabilities, strengths, use cases)
- Integrates with usage tracker to enforce limits and track spending
- Respects circuit breakers and model toggles before making API calls

### 3. Model Recommender (model_recommender.py)
- Analyzes user tasks and recommends the optimal AI model
- Uses GPT-4o to evaluate task requirements and match them to model capabilities

### 4. MCP Handler (mcp_handler.py)
- Implements the Model Context Protocol
- Enables standardized communication between different models
- Provides structured context for model transitions

### 5. Utilities (utils.py)
- Handles UI styling via custom CSS
- Provides helper functions for message formatting
- Manages conversation history persistence

### 6. Conversation Starters (conversation_starters.py)
- Provides categorized suggestions to help users get started
- Demonstrates different capabilities of the system

### 7. Model Usage Tracker (model_usage_tracker.py)
- Tracks token usage, API calls, and costs per AI model
- Enforces daily limits for calls, tokens, and spending per model
- Implements circuit breakers to auto-disable failing models
- Provides model enable/disable toggles
- Calculates costs based on actual provider pricing

### 8. Model Control Panel (model_control_panel.py)
- Comprehensive UI for managing AI model usage and costs
- Real-time usage dashboard with metrics and charts
- Model-specific controls for enabling/disabling models
- Spending limit configuration (per-model and global)
- Circuit breaker status monitoring and manual reset
- Analytics with cost breakdowns and token usage visualizations

## Data Flow

1. **User Input**: The user enters a message or selects a conversation starter in the Streamlit interface
2. **Model Selection**: 
   - User can manually select a model
   - Or use the model recommender to suggest an optimal model for their task
3. **Usage Check**:
   - Model usage tracker checks if the selected model is available
   - Verifies model is enabled and within spending limits
   - Checks circuit breaker status
4. **Message Processing**:
   - The selected model processes the user's message through the model handler
   - MCP handler adds appropriate context for the model
5. **Response Generation**:
   - The model generates a response
   - MCP handler processes the response to extract structured context
6. **Usage Tracking**:
   - Token usage and cost are calculated and recorded
   - Circuit breaker state is updated based on success/failure
7. **UI Update**:
   - The response is displayed in the chat interface
   - Conversation history is updated and persisted

The system also supports a comparison mode where multiple models can process the same query simultaneously, allowing users to compare responses.

### Cost Control Features

**Per-Model Tracking:**
- Each AI model has independent usage metrics
- Tracks input tokens, output tokens, API calls, and costs separately
- Daily metrics that reset automatically

**Spending Limits:**
- Set daily limits per model for:
  - Number of API calls
  - Total tokens (input + output)
  - Cost in dollars
- Global daily cost limit across all models
- Models automatically blocked when limits are reached

**Circuit Breakers:**
- Automatically disable models experiencing repeated errors
- Three states: Closed (normal), Open (blocked), Half-Open (testing)
- Automatic recovery after timeout period
- Manual reset capability

**User Controls:**
- Toggle individual models on/off
- View real-time usage dashboard
- Configure limits through intuitive UI
- Analytics with charts showing cost distribution

## External Dependencies

### Primary Libraries
- **Streamlit**: Web interface framework
- **OpenAI Client**: For interacting with GPT models
- **Anthropic Client**: For interacting with Claude models

### API Dependencies
- Requires API keys for:
  - OpenAI services
  - Anthropic services
  - (Potentially other model providers)

### Environment Requirements
- Python 3.11+
- No database required (uses file-based storage)

## Deployment Strategy

The application is configured for deployment on Replit with:

1. **Autoscaling**: Set up for automatic scaling based on demand
2. **Port Configuration**: Using port 5000 for the Streamlit server
3. **Python Version**: Using Python 3.11
4. **Workflow Configuration**: Defined workflows for running the Streamlit server

The deployment is containerized using Nix with a stable channel, ensuring consistent environments across deployments.

### Local Development
For local development, the application requires:
1. Installing dependencies from pyproject.toml
2. Setting up API keys as environment variables
3. Running the Streamlit application with `streamlit run app.py`

### Security Considerations
- API keys should be stored as environment variables
- The application doesn't currently implement user authentication
- All conversations are stored in the session state

## Recent Updates

**October 2025 - AI Cost Control System**
- Added comprehensive per-model token usage tracking
- Implemented spending limits with configurable thresholds
- Added circuit breakers for automatic failure protection
- Created Model Control Panel for managing all AI models
- Real-time cost analytics and usage visualization

## Future Improvements

Potential enhancements to consider:
1. Enforce global daily cost limits (currently informational only)
2. Add historical usage data and trends over time
3. Implement usage alerts via email/notifications
4. Add more model providers (like Mistral, Llama, etc.)
5. Enhancing the model recommender with more sophisticated analysis
6. Implementing streaming responses for better user experience
7. Adding support for multimodal inputs (images, audio)
8. Add smoke tests for tracking system persistence