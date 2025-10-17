
import json
from datetime import datetime
from typing import Dict, List, Optional
from model_handler import ModelHandler
from mcp_handler import MCPHandler

class WorkflowAutomation:
    """
    Intelligent workflow automation for business processes
    """
    
    def __init__(self):
        self.model_handler = ModelHandler()
        self.mcp_handler = MCPHandler()
        
        # Define workflow triggers
        self.workflow_triggers = {
            'design_consultation': {
                'keywords': ['frame', 'design', 'artwork', 'style', 'color', 'material'],
                'preferred_model': 'claude-3-5-sonnet-20241022',
                'follow_up_actions': ['generate_quote', 'schedule_appointment']
            },
            'cost_analysis': {
                'keywords': ['cost', 'price', 'budget', 'estimate', 'profit'],
                'preferred_model': 'gpt-4o',
                'follow_up_actions': ['update_pricing', 'notify_sales_team']
            },
            'production_planning': {
                'keywords': ['schedule', 'production', 'timeline', 'capacity', 'workflow'],
                'preferred_model': 'claude-3-opus-20240229',
                'follow_up_actions': ['update_kanban', 'notify_production_team']
            },
            'customer_service': {
                'keywords': ['complaint', 'issue', 'problem', 'refund', 'exchange'],
                'preferred_model': 'gpt-4o',
                'follow_up_actions': ['create_ticket', 'notify_manager']
            }
        }
    
    def analyze_conversation_intent(self, messages: List[Dict]) -> Dict:
        """Analyze conversation to determine intent and workflow"""
        recent_messages = messages[-5:] if len(messages) > 5 else messages
        conversation_text = " ".join([msg.get('content', '') for msg in recent_messages])
        
        intent_scores = {}
        for workflow, config in self.workflow_triggers.items():
            score = 0
            for keyword in config['keywords']:
                score += conversation_text.lower().count(keyword.lower())
            intent_scores[workflow] = score
        
        # Get highest scoring intent
        primary_intent = max(intent_scores, key=intent_scores.get) if intent_scores else 'general'
        confidence = intent_scores.get(primary_intent, 0) / len(conversation_text.split()) * 100
        
        return {
            'intent': primary_intent,
            'confidence': min(confidence, 100),
            'recommended_model': self.workflow_triggers.get(primary_intent, {}).get('preferred_model'),
            'follow_up_actions': self.workflow_triggers.get(primary_intent, {}).get('follow_up_actions', [])
        }
    
    def suggest_model_switch(self, current_model: str, conversation_intent: Dict) -> Optional[Dict]:
        """Suggest model switch if better suited model available"""
        recommended_model = conversation_intent.get('recommended_model')
        
        if recommended_model and recommended_model != current_model and conversation_intent.get('confidence', 0) > 30:
            return {
                'suggested_model': recommended_model,
                'reason': f"Better suited for {conversation_intent['intent']} tasks",
                'confidence': conversation_intent['confidence']
            }
        return None
    
    def trigger_automated_actions(self, intent: str, conversation_data: Dict) -> List[Dict]:
        """Trigger automated follow-up actions based on intent"""
        actions = []
        follow_ups = self.workflow_triggers.get(intent, {}).get('follow_up_actions', [])
        
        for action in follow_ups:
            if action == 'generate_quote':
                actions.append({
                    'type': 'generate_quote',
                    'description': 'Generate detailed pricing quote',
                    'priority': 'high'
                })
            elif action == 'schedule_appointment':
                actions.append({
                    'type': 'schedule_appointment',
                    'description': 'Suggest appointment scheduling',
                    'priority': 'medium'
                })
            elif action == 'update_kanban':
                actions.append({
                    'type': 'update_kanban',
                    'description': 'Update production board',
                    'priority': 'high'
                })
            elif action == 'notify_production_team':
                actions.append({
                    'type': 'notification',
                    'description': 'Notify production team of changes',
                    'priority': 'medium'
                })
        
        return actions

class SmartNotificationSystem:
    """
    Intelligent notification system for business events
    """
    
    def __init__(self):
        self.notification_templates = {
            'order_ready': {
                'subject': 'Your Custom Frame is Ready!',
                'template': 'Dear {customer_name}, your beautiful custom frame for "{artwork_title}" is ready for pickup. We\'re excited for you to see the finished piece!'
            },
            'design_consultation': {
                'subject': 'Your Frame Design Consultation',
                'template': 'Hi {customer_name}, based on our AI analysis, we recommend {frame_style} with {mat_color} matting for your {artwork_type}. Estimated cost: ${estimated_cost}'
            },
            'production_delay': {
                'subject': 'Update on Your Custom Frame Order',
                'template': 'Dear {customer_name}, we wanted to update you that your order #{order_id} will be ready on {new_date} due to {reason}. Thank you for your patience.'
            }
        }
    
    def generate_smart_notification(self, event_type: str, context: Dict) -> Dict:
        """Generate intelligent notification based on context"""
        template = self.notification_templates.get(event_type)
        if not template:
            return {}
        
        try:
            message = template['template'].format(**context)
            return {
                'subject': template['subject'],
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type
            }
        except KeyError as e:
            return {'error': f'Missing context key: {e}'}

class ContextualMemorySystem:
    """
    Advanced memory system for maintaining context across conversations
    """
    
    def __init__(self):
        self.customer_contexts = {}
        self.project_contexts = {}
    
    def update_customer_context(self, customer_id: str, conversation_data: Dict):
        """Update customer context with conversation insights"""
        if customer_id not in self.customer_contexts:
            self.customer_contexts[customer_id] = {
                'preferences': {},
                'history': [],
                'projects': []
            }
        
        # Extract preferences from conversation
        preferences = self.extract_preferences(conversation_data)
        self.customer_contexts[customer_id]['preferences'].update(preferences)
        
        # Add to history
        self.customer_contexts[customer_id]['history'].append({
            'timestamp': datetime.now().isoformat(),
            'conversation_summary': conversation_data.get('summary', ''),
            'intent': conversation_data.get('intent', ''),
            'satisfaction_score': conversation_data.get('satisfaction', 0)
        })
    
    def extract_preferences(self, conversation_data: Dict) -> Dict:
        """Extract customer preferences from conversation"""
        preferences = {}
        content = conversation_data.get('content', '').lower()
        
        # Style preferences
        if 'modern' in content:
            preferences['style'] = 'modern'
        elif 'traditional' in content or 'classic' in content:
            preferences['style'] = 'traditional'
        elif 'rustic' in content:
            preferences['style'] = 'rustic'
        
        # Color preferences
        color_mentions = ['black', 'white', 'brown', 'gold', 'silver', 'wood']
        for color in color_mentions:
            if color in content:
                preferences['preferred_colors'] = preferences.get('preferred_colors', [])
                preferences['preferred_colors'].append(color)
        
        return preferences
    
    def get_customer_context(self, customer_id: str) -> Dict:
        """Get comprehensive customer context"""
        return self.customer_contexts.get(customer_id, {})
