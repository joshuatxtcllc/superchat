import os
import json
from datetime import datetime
from database import DatabaseManager
from model_handler import ModelHandler
from model_recommender import ModelRecommender

class FramingBusinessAI:
    """
    AI Integration for Custom Art Framing Business
    Connects Designer, POS, HUB, Art Tracker, and Production systems
    """
    
    def __init__(self):
        self.db = DatabaseManager()
        self.model_handler = ModelHandler()
        self.model_recommender = ModelRecommender()
        
        # Business-specific model routing
        self.business_models = {
            'design_consultation': 'claude-3-5-sonnet-20241022',  # Best for creative discussions
            'customer_service': 'gpt-4o',  # Excellent for customer interactions
            'order_processing': 'gpt-4o-mini',  # Fast for structured data
            'production_planning': 'claude-3-opus-20240229',  # Complex scheduling
            'cost_analysis': 'gpt-4o',  # Financial calculations
            'quality_control': 'claude-3-5-sonnet-20241022',  # Detail-oriented
            'inventory_management': 'gpt-4o-mini',  # Quick data processing
            'customer_notifications': 'claude-3-haiku-20240307'  # Fast, friendly messages
        }
    
    def process_design_request(self, customer_data, artwork_description, preferences):
        """
        Handle custom framing design requests
        Routes to Claude 3.5 Sonnet for creative consultation
        """
        design_prompt = f"""
        Customer Profile: {customer_data.get('name', 'Customer')}
        Artwork: {artwork_description}
        Preferences: {preferences}
        Budget: ${customer_data.get('budget', 'Not specified')}
        
        Provide detailed framing recommendations including:
        1. Frame material and style suggestions
        2. Matting options and colors
        3. Glass type recommendations
        4. Estimated pricing breakdown
        5. Alternative options within budget
        """
        
        model_id = self.business_models['design_consultation']
        response = self.model_handler.get_response([
            {"role": "system", "content": "You are an expert custom framing consultant with 20+ years experience."},
            {"role": "user", "content": design_prompt}
        ], model_id)
        
        # Log to database for tracking
        self.db.log_model_usage(
            user_id=customer_data.get('customer_id'),
            model_id=model_id,
            model_name="Claude 3.5 Sonnet",
            task_type="design_consultation"
        )
        
        return response
    
    def process_order(self, order_data):
        """
        Process incoming orders with AI validation and cost calculation
        Routes to GPT-4o for structured processing
        """
        order_prompt = f"""
        Order Details: {json.dumps(order_data, indent=2)}
        
        Validate this framing order and provide:
        1. Order validation (missing information, conflicts)
        2. Material cost calculation
        3. Labor time estimate
        4. Profit margin analysis
        5. Production priority recommendation
        6. Suggested upsell opportunities
        
        Respond in JSON format for integration with POS system.
        """
        
        model_id = self.business_models['order_processing']
        response = self.model_handler.get_response([
            {"role": "system", "content": "You are an order processing specialist for a custom framing business."},
            {"role": "user", "content": order_prompt}
        ], model_id)
        
        # Save to database
        order_id = order_data.get('order_id', 'unknown')
        self.db.save_conversation(
            conversation_id=f"order_{order_id}",
            title=f"Order Processing - {order_id}"
        )
        
        return response
    
    def optimize_production_schedule(self, current_orders, workshop_capacity, material_availability):
        """
        Optimize production scheduling for the kanban board
        Routes to Claude 3 Opus for complex scheduling
        """
        schedule_prompt = f"""
        Current Orders: {json.dumps(current_orders, indent=2)}
        Workshop Capacity: {workshop_capacity}
        Material Availability: {json.dumps(material_availability, indent=2)}
        
        Create an optimized production schedule considering:
        1. Order priorities and deadlines
        2. Material availability constraints
        3. Workshop capacity and worker skills
        4. Profit margin optimization
        5. Customer satisfaction impact
        
        Provide kanban board updates and timeline adjustments.
        """
        
        model_id = self.business_models['production_planning']
        response = self.model_handler.get_response([
            {"role": "system", "content": "You are a production planning expert for custom manufacturing."},
            {"role": "user", "content": schedule_prompt}
        ], model_id)
        
        return response
    
    def generate_customer_notifications(self, order_status, customer_info):
        """
        Generate personalized customer notifications
        Routes to Claude 3 Haiku for fast, friendly messages
        """
        notification_prompt = f"""
        Customer: {customer_info.get('name')}
        Order: {order_status.get('order_id')}
        Status: {order_status.get('current_status')}
        Expected Completion: {order_status.get('estimated_completion')}
        
        Generate a friendly, professional update message that:
        1. Updates customer on current progress
        2. Confirms next steps
        3. Addresses any potential concerns
        4. Maintains excitement about the finished piece
        
        Keep it concise and warm.
        """
        
        model_id = self.business_models['customer_notifications']
        response = self.model_handler.get_response([
            {"role": "system", "content": "You are a friendly customer service representative for a high-end framing shop."},
            {"role": "user", "content": notification_prompt}
        ], model_id)
        
        return response
    
    def analyze_profit_and_sales(self, sales_data, cost_data, timeframe):
        """
        Comprehensive business analytics and profit tracking
        Routes to GPT-4o for financial analysis
        """
        analysis_prompt = f"""
        Sales Data: {json.dumps(sales_data, indent=2)}
        Cost Data: {json.dumps(cost_data, indent=2)}
        Timeframe: {timeframe}
        
        Provide comprehensive business analysis including:
        1. Profit margin analysis by product category
        2. Cost trend identification
        3. Revenue optimization recommendations
        4. Inventory turnover analysis
        5. Customer lifetime value insights
        6. Seasonal trend analysis
        7. Pricing strategy recommendations
        
        Include actionable insights for business growth.
        """
        
        model_id = self.business_models['cost_analysis']
        response = self.model_handler.get_response([
            {"role": "system", "content": "You are a business analyst specializing in custom manufacturing and retail operations."},
            {"role": "user", "content": analysis_prompt}
        ], model_id)
        
        return response
    
    def quality_control_assessment(self, work_photos, quality_standards):
        """
        AI-powered quality control for finished pieces
        Routes to Claude 3.5 Sonnet for detailed analysis
        """
        qc_prompt = f"""
        Quality Standards: {json.dumps(quality_standards, indent=2)}
        
        Assess the finished framing work against our quality standards:
        1. Frame joint quality and alignment
        2. Matting precision and cleanliness
        3. Glass clarity and placement
        4. Overall presentation quality
        5. Areas needing improvement
        6. Customer satisfaction prediction
        
        Provide specific feedback for continuous improvement.
        """
        
        model_id = self.business_models['quality_control']
        response = self.model_handler.get_response([
            {"role": "system", "content": "You are a master craftsman and quality control expert for custom framing."},
            {"role": "user", "content": qc_prompt}
        ], model_id)
        
        return response
    
    def get_business_insights(self, days=30):
        """
        Get AI usage analytics specific to business operations
        """
        analytics = self.db.get_model_analytics(days=days)
        
        # Business-specific insights
        insights = {
            'total_ai_interactions': sum(data['total_uses'] for data in analytics.values()),
            'cost_per_interaction': sum(data['total_cost'] for data in analytics.values()) / max(1, sum(data['total_uses'] for data in analytics.values())),
            'most_used_features': sorted(analytics.items(), key=lambda x: x[1]['total_uses'], reverse=True),
            'efficiency_metrics': {
                model: data['avg_response_time'] for model, data in analytics.items()
            }
        }
        
        return insights

# Integration points for your existing systems
class SystemIntegrations:
    """
    Integration helpers for connecting with existing business systems
    """
    
    @staticmethod
    def designer_integration(framing_ai, design_request):
        """Connect with your Designer system"""
        return framing_ai.process_design_request(
            design_request['customer_data'],
            design_request['artwork_description'],
            design_request['preferences']
        )
    
    @staticmethod
    def pos_integration(framing_ai, order_data):
        """Connect with your POS system"""
        return framing_ai.process_order(order_data)
    
    @staticmethod
    def hub_integration(framing_ai, hub_data):
        """Connect with your HUB system for analytics"""
        return framing_ai.analyze_profit_and_sales(
            hub_data['sales_data'],
            hub_data['cost_data'],
            hub_data['timeframe']
        )
    
    @staticmethod
    def tracker_integration(framing_ai, tracking_data):
        """Connect with your Art Tracker system"""
        return framing_ai.generate_customer_notifications(
            tracking_data['order_status'],
            tracking_data['customer_info']
        )
    
    @staticmethod
    def kanban_integration(framing_ai, production_data):
        """Connect with your Production Kanban system"""
        return framing_ai.optimize_production_schedule(
            production_data['current_orders'],
            production_data['workshop_capacity'],
            production_data['material_availability']
        )

# Example usage for your business
def example_business_workflow():
    """
    Example of how to use the AI system in your framing business
    """
    ai_system = FramingBusinessAI()
    
    # 1. Design Consultation
    design_request = {
        'customer_data': {'name': 'John Smith', 'budget': 300, 'customer_id': 'CUST001'},
        'artwork_description': 'Original oil painting, 16x20 inches, landscape scene',
        'preferences': 'Traditional style, warm colors, museum-quality protection'
    }
    design_recommendation = ai_system.process_design_request(
        design_request['customer_data'],
        design_request['artwork_description'],
        design_request['preferences']
    )
    
    # 2. Order Processing
    order_data = {
        'order_id': 'ORD001',
        'customer_id': 'CUST001',
        'frame_type': 'Hardwood Cherry',
        'mat_color': 'Cream',
        'glass_type': 'Museum UV',
        'rush_order': False
    }
    order_analysis = ai_system.process_order(order_data)
    
    # 3. Production Scheduling
    production_data = {
        'current_orders': [order_data],
        'workshop_capacity': {'daily_frames': 5, 'staff_available': 2},
        'material_availability': {'cherry_frames': 10, 'museum_glass': 5}
    }
    schedule_optimization = ai_system.optimize_production_schedule(
        production_data['current_orders'],
        production_data['workshop_capacity'],
        production_data['material_availability']
    )
    
    return {
        'design': design_recommendation,
        'order': order_analysis,
        'schedule': schedule_optimization
    }