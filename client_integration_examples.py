"""
Client-Side Integration Examples
How your existing apps connect to the Hub AI endpoints
"""

import requests
import json
from datetime import datetime

class DesignerAppIntegration:
    """
    Integration code for your Designer app
    """
    
    def __init__(self, hub_base_url="http://your-hub-app.com"):
        self.hub_url = hub_base_url
    
    def get_ai_design_recommendation(self, customer_name, artwork_description, 
                                   style_preferences, budget, customer_id=None):
        """
        Call this from your Designer app when customer needs framing consultation
        """
        endpoint = f"{self.hub_url}/api/ai/design"
        
        payload = {
            'customer_name': customer_name,
            'artwork_description': artwork_description,
            'preferences': style_preferences,
            'budget': budget,
            'customer_id': customer_id
        }
        
        try:
            response = requests.post(endpoint, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'recommendation': result['design_recommendation'],
                    'customer_id': result['customer_id']
                }
            else:
                return {
                    'success': False,
                    'error': 'AI service unavailable',
                    'fallback': 'Please proceed with manual consultation'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout',
                'fallback': 'AI taking too long, proceed manually'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'fallback': 'Manual consultation recommended'
            }

class POSAppIntegration:
    """
    Integration code for your POS app
    """
    
    def __init__(self, hub_base_url="http://your-hub-app.com"):
        self.hub_url = hub_base_url
    
    def validate_order_with_ai(self, order_data):
        """
        Call this from your POS app during order entry
        """
        endpoint = f"{self.hub_url}/api/ai/order"
        
        try:
            response = requests.post(endpoint, json=order_data, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'valid': True,
                    'analysis': result['validation_result'],
                    'order_id': result['order_id']
                }
            else:
                return {
                    'valid': True,  # Default to valid if AI unavailable
                    'analysis': 'AI validation unavailable - order processed manually',
                    'order_id': order_data.get('order_id')
                }
                
        except Exception as e:
            return {
                'valid': True,
                'analysis': f'Validation error: {str(e)} - proceeding with manual process',
                'order_id': order_data.get('order_id')
            }

class KanbanAppIntegration:
    """
    Integration code for your Kanban production board
    """
    
    def __init__(self, hub_base_url="http://your-hub-app.com"):
        self.hub_url = hub_base_url
    
    def optimize_production_schedule(self, current_orders, workshop_capacity, materials):
        """
        Call this when you need to optimize production scheduling
        """
        endpoint = f"{self.hub_url}/api/ai/production"
        
        payload = {
            'current_orders': current_orders,
            'workshop_capacity': workshop_capacity,
            'material_availability': materials
        }
        
        try:
            response = requests.post(endpoint, json=payload, timeout=45)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'schedule': result['optimized_schedule'],
                    'orders_processed': result['orders_processed']
                }
            else:
                return {
                    'success': False,
                    'schedule': 'AI optimization unavailable - use current schedule',
                    'orders_processed': len(current_orders)
                }
                
        except Exception as e:
            return {
                'success': False,
                'schedule': f'Optimization error: {str(e)} - manual scheduling required',
                'orders_processed': len(current_orders)
            }

class ArtTrackerIntegration:
    """
    Integration code for your Art Tracker app
    """
    
    def __init__(self, hub_base_url="http://your-hub-app.com"):
        self.hub_url = hub_base_url
    
    def generate_customer_notification(self, order_id, current_status, 
                                     estimated_completion, customer_name, 
                                     customer_email=None, customer_phone=None):
        """
        Call this when order status changes and customer needs notification
        """
        endpoint = f"{self.hub_url}/api/ai/notifications"
        
        payload = {
            'order_status': {
                'order_id': order_id,
                'current_status': current_status,
                'estimated_completion': estimated_completion
            },
            'customer_info': {
                'name': customer_name,
                'email': customer_email,
                'phone': customer_phone
            }
        }
        
        try:
            response = requests.post(endpoint, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'message': result['notification_message'],
                    'customer': customer_name
                }
            else:
                return {
                    'success': False,
                    'message': f"Hello {customer_name}, your order {order_id} status: {current_status}",
                    'customer': customer_name
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Hello {customer_name}, your order is being processed. We'll update you soon!",
                'customer': customer_name
            }

# EXAMPLE USAGE IN YOUR EXISTING APPS

def designer_app_example():
    """
    Example: How to use AI in your Designer app
    """
    designer = DesignerAppIntegration("http://localhost:5001")  # Your Hub URL
    
    # When customer requests design consultation
    result = designer.get_ai_design_recommendation(
        customer_name="John Smith",
        artwork_description="Original oil painting, 16x20 inches, landscape scene",
        style_preferences="Traditional style, warm colors, museum-quality protection",
        budget=300
    )
    
    if result['success']:
        # Display AI recommendation in your Designer UI
        print("AI Recommendation:")
        print(result['recommendation'])
        # Save customer_id for future reference
        customer_id = result['customer_id']
    else:
        # Fall back to manual process
        print("Manual consultation required:")
        print(result['fallback'])

def pos_app_example():
    """
    Example: How to use AI in your POS app
    """
    pos = POSAppIntegration("http://localhost:5001")
    
    # When processing an order
    order_data = {
        'customer_name': 'John Smith',
        'frame_material': 'Hardwood Cherry',
        'frame_width': '2 inch',
        'mat_style': 'Double Mat',
        'mat_color': 'Cream',
        'glass_type': 'Museum Glass',
        'rush_order': False,
        'delivery_method': 'Pickup'
    }
    
    validation = pos.validate_order_with_ai(order_data)
    
    if validation['valid']:
        print("Order validated:")
        print(validation['analysis'])
        # Proceed with order processing
    else:
        print("Order validation failed - manual review required")

def kanban_app_example():
    """
    Example: How to use AI in your Kanban board
    """
    kanban = KanbanAppIntegration("http://localhost:5001")
    
    # Current production data
    current_orders = [
        {'order_id': 'ORD001', 'priority': 'High', 'complexity': 'Medium', 'deadline': '2024-01-15'},
        {'order_id': 'ORD002', 'priority': 'Normal', 'complexity': 'High', 'deadline': '2024-01-18'}
    ]
    
    workshop_capacity = {
        'daily_frames': 5,
        'staff_available': 2,
        'overtime_available': True
    }
    
    materials = {
        'Hardwood Frames': 15,
        'Museum Glass': 12,
        'Mat Board': 50
    }
    
    optimization = kanban.optimize_production_schedule(current_orders, workshop_capacity, materials)
    
    if optimization['success']:
        print("Optimized Schedule:")
        print(optimization['schedule'])
        # Update your Kanban board with optimized schedule
    else:
        print("Using current schedule - AI optimization unavailable")

def art_tracker_example():
    """
    Example: How to use AI in your Art Tracker
    """
    tracker = ArtTrackerIntegration("http://localhost:5001")
    
    # When order status changes
    notification = tracker.generate_customer_notification(
        order_id="ORD001",
        current_status="In Production",
        estimated_completion="January 15, 2024",
        customer_name="John Smith",
        customer_email="john@email.com"
    )
    
    if notification['success']:
        print("Customer notification ready:")
        print(notification['message'])
        # Send via email/SMS through your existing notification system
    else:
        print("Fallback notification:")
        print(notification['message'])

# CONFIGURATION CLASS
class AIIntegrationConfig:
    """
    Configuration for all your app integrations
    """
    
    def __init__(self):
        self.hub_base_url = "http://localhost:5001"  # Change to your Hub URL
        self.timeout_settings = {
            'design': 30,      # Design consultations can take longer
            'order': 20,       # Order validation should be quick
            'production': 45,  # Production optimization is complex
            'notifications': 15 # Notifications should be fast
        }
        self.fallback_enabled = True
        self.retry_attempts = 2
    
    def get_endpoint_url(self, service):
        """Get full URL for a specific service"""
        endpoints = {
            'design': f"{self.hub_base_url}/api/ai/design",
            'order': f"{self.hub_base_url}/api/ai/order",
            'production': f"{self.hub_base_url}/api/ai/production",
            'notifications': f"{self.hub_base_url}/api/ai/notifications",
            'quality': f"{self.hub_base_url}/api/ai/quality",
            'analytics': f"{self.hub_base_url}/api/ai/analytics",
            'health': f"{self.hub_base_url}/api/ai/health"
        }
        return endpoints.get(service)
    
    def check_ai_health(self):
        """Check if AI services are operational before making requests"""
        try:
            response = requests.get(self.get_endpoint_url('health'), timeout=5)
            return response.status_code == 200
        except:
            return False