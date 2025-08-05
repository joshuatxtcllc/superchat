
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class UserPreference:
    key: str
    value: Any
    last_updated: str
    confidence: float = 1.0

@dataclass
class ConversationSummary:
    conversation_id: str
    summary: str
    key_topics: List[str]
    important_decisions: List[str]
    created_at: str
    message_count: int

@dataclass
class ProjectContext:
    project_id: str
    name: str
    description: str
    related_conversations: List[str]
    key_files: List[str]
    tech_stack: List[str]
    created_at: str
    last_updated: str

class ContextManager:
    def __init__(self, storage_dir: str = "context_storage"):
        self.storage_dir = storage_dir
        self.ensure_storage_dirs()
        
    def ensure_storage_dirs(self):
        """Create storage directories if they don't exist"""
        dirs = [
            self.storage_dir,
            f"{self.storage_dir}/preferences",
            f"{self.storage_dir}/summaries", 
            f"{self.storage_dir}/projects"
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def extract_user_preferences(self, messages: List[Dict]) -> List[UserPreference]:
        """Extract user preferences from conversation"""
        preferences = []
        
        # Look for preference indicators in messages
        preference_patterns = {
            "programming_language": ["prefer", "like", "use", "working with"],
            "code_style": ["style", "format", "convention"],
            "communication_style": ["explain", "simple", "detailed", "technical"],
            "project_type": ["building", "working on", "developing"]
        }
        
        for message in messages:
            if message["role"] == "user":
                content = message["content"].lower()
                
                for pref_type, patterns in preference_patterns.items():
                    for pattern in patterns:
                        if pattern in content:
                            # Extract the preference value (simplified)
                            pref_value = self._extract_preference_value(content, pattern)
                            if pref_value:
                                preferences.append(UserPreference(
                                    key=pref_type,
                                    value=pref_value,
                                    last_updated=message.get("timestamp", ""),
                                    confidence=0.7
                                ))
        
        return preferences
    
    def _extract_preference_value(self, content: str, pattern: str) -> Optional[str]:
        """Extract preference value from content (simplified implementation)"""
        # This is a basic implementation - could be enhanced with NLP
        words = content.split()
        try:
            pattern_index = next(i for i, word in enumerate(words) if pattern in word)
            # Get the next few words as the preference value
            if pattern_index + 1 < len(words):
                return " ".join(words[pattern_index + 1:pattern_index + 3])
        except StopIteration:
            pass
        return None
    
    def generate_conversation_summary(self, messages: List[Dict], model_handler) -> ConversationSummary:
        """Generate an intelligent summary of the conversation"""
        if len(messages) < 3:
            return None
            
        # Prepare conversation text for summarization
        conversation_text = ""
        for msg in messages[-10:]:  # Last 10 messages
            role = "User" if msg["role"] == "user" else "Assistant"
            conversation_text += f"{role}: {msg['content']}\n"
        
        # Create summarization prompt
        summary_prompt = f"""
        Please analyze this conversation and provide:
        1. A concise summary (2-3 sentences)
        2. Key topics discussed (comma-separated)
        3. Important decisions or conclusions reached
        
        Conversation:
        {conversation_text}
        
        Format your response as JSON:
        {{
            "summary": "Brief summary here",
            "key_topics": ["topic1", "topic2", "topic3"],
            "important_decisions": ["decision1", "decision2"]
        }}
        """
        
        try:
            # Use the model handler to generate summary
            summary_response = model_handler.get_response(
                [{"role": "user", "content": summary_prompt}],
                "gpt-4o-mini"  # Use smaller model for efficiency
            )
            
            # Parse the JSON response
            summary_data = json.loads(summary_response.strip())
            
            return ConversationSummary(
                conversation_id=f"conv_{int(datetime.now().timestamp())}",
                summary=summary_data.get("summary", ""),
                key_topics=summary_data.get("key_topics", []),
                important_decisions=summary_data.get("important_decisions", []),
                created_at=datetime.now().isoformat(),
                message_count=len(messages)
            )
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None
    
    def save_user_preferences(self, user_id: str, preferences: List[UserPreference]):
        """Save user preferences to storage"""
        pref_file = f"{self.storage_dir}/preferences/{user_id}.json"
        
        # Load existing preferences
        existing_prefs = {}
        if os.path.exists(pref_file):
            with open(pref_file, 'r') as f:
                existing_prefs = json.load(f)
        
        # Update with new preferences
        for pref in preferences:
            existing_prefs[pref.key] = asdict(pref)
        
        # Save updated preferences
        with open(pref_file, 'w') as f:
            json.dump(existing_prefs, f, indent=2)
    
    def load_user_preferences(self, user_id: str) -> Dict[str, UserPreference]:
        """Load user preferences from storage"""
        pref_file = f"{self.storage_dir}/preferences/{user_id}.json"
        
        if not os.path.exists(pref_file):
            return {}
        
        with open(pref_file, 'r') as f:
            prefs_data = json.load(f)
        
        preferences = {}
        for key, data in prefs_data.items():
            preferences[key] = UserPreference(**data)
        
        return preferences
    
    def save_conversation_summary(self, summary: ConversationSummary):
        """Save conversation summary"""
        summary_file = f"{self.storage_dir}/summaries/{summary.conversation_id}.json"
        with open(summary_file, 'w') as f:
            json.dump(asdict(summary), f, indent=2)
    
    def find_related_conversations(self, current_topics: List[str], limit: int = 5) -> List[ConversationSummary]:
        """Find conversations related to current topics"""
        related = []
        summary_dir = f"{self.storage_dir}/summaries"
        
        if not os.path.exists(summary_dir):
            return related
        
        for filename in os.listdir(summary_dir):
            if filename.endswith('.json'):
                with open(f"{summary_dir}/{filename}", 'r') as f:
                    summary_data = json.load(f)
                    summary = ConversationSummary(**summary_data)
                    
                    # Calculate topic overlap
                    overlap = len(set(current_topics) & set(summary.key_topics))
                    if overlap > 0:
                        related.append((summary, overlap))
        
        # Sort by relevance and return top results
        related.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in related[:limit]]
    
    def get_context_for_conversation(self, user_id: str, current_topics: List[str] = None) -> Dict[str, Any]:
        """Get relevant context for a new conversation"""
        context = {
            "user_preferences": self.load_user_preferences(user_id),
            "related_conversations": [],
            "suggested_topics": []
        }
        
        if current_topics:
            context["related_conversations"] = self.find_related_conversations(current_topics)
        
        return context
    
    def create_context_prompt(self, context: Dict[str, Any]) -> str:
        """Create a context prompt to include in AI requests"""
        prompt_parts = []
        
        # Add user preferences
        if context["user_preferences"]:
            prefs = []
            for pref in context["user_preferences"].values():
                prefs.append(f"{pref.key}: {pref.value}")
            
            prompt_parts.append(f"User preferences: {', '.join(prefs)}")
        
        # Add related conversation context
        if context["related_conversations"]:
            summaries = []
            for conv in context["related_conversations"][:3]:  # Top 3 most relevant
                summaries.append(f"Previous discussion: {conv.summary}")
            
            prompt_parts.append(f"Related context: {' | '.join(summaries)}")
        
        if prompt_parts:
            return f"\n[Context: {' | '.join(prompt_parts)}]\n"
        
        return ""
