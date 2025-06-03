"""
Hub API Endpoints for Custom Framing Business
Add these endpoints to your existing Hub app
"""

from flask import Flask, request, jsonify
from framing_business_integration import FramingBusinessAI
import uuid
from datetime import datetime

# Initialize your AI system
framing_ai = FramingBusinessAI()

app = Flask(__name__)

# DESIGN CONSULTATION ENDPOINT
@app.route('/api/ai/design', methods=['POST'])
def design_consultation():
    """
    Designer app sends design requests here
    Returns AI-generated framing recommendations
    """
    try:
        data = request.json
        
        customer_data = {
            'name': data.get('customer_name'),
            'budget': data.get('budget', 0),
            'customer_id': data.get('customer_id', f"CUST{datetime.now().strftime('%m%d%H%M')}")
        }
        
        artwork_description = data.get('artwork_description', '')
        preferences = data.get('preferences', '')
        
        # Get AI recommendation
        recommendation = framing_ai.process_design_request(
            customer_data, artwork_description, preferences
        )
        
        return jsonify({
            'success': True,
            'design_recommendation': recommendation,
            'customer_id': customer_data['customer_id'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_message': 'Design consultation temporarily unavailable. Please proceed with manual consultation.'
        }), 500

# ORDER PROCESSING ENDPOINT
@app.route('/api/ai/order', methods=['POST'])
def process_order():
    """
    POS app sends order data for validation and cost analysis
    Returns validation results and pricing
    """
    try:
        order_data = request.json
        
        # Add timestamp if not present
        if 'timestamp' not in order_data:
            order_data['timestamp'] = datetime.now().isoformat()
        
        # Generate order ID if not present
        if 'order_id' not in order_data:
            order_data['order_id'] = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Get AI analysis
        analysis = framing_ai.process_order(order_data)
        
        return jsonify({
            'success': True,
            'order_id': order_data['order_id'],
            'validation_result': analysis,
            'processed_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_message': 'Order processing AI unavailable. Please proceed with manual validation.'
        }), 500

# PRODUCTION PLANNING ENDPOINT
@app.route('/api/ai/production', methods=['POST'])
def production_planning():
    """
    Kanban board requests production optimization
    Returns optimized schedule and resource allocation
    """
    try:
        data = request.json
        
        current_orders = data.get('current_orders', [])
        workshop_capacity = data.get('workshop_capacity', {})
        material_availability = data.get('material_availability', {})
        
        # Get AI optimization
        schedule = framing_ai.optimize_production_schedule(
            current_orders, workshop_capacity, material_availability
        )
        
        return jsonify({
            'success': True,
            'optimized_schedule': schedule,
            'generated_at': datetime.now().isoformat(),
            'orders_processed': len(current_orders)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_message': 'Production planning AI unavailable. Please use manual scheduling.'
        }), 500

# CUSTOMER NOTIFICATIONS ENDPOINT
@app.route('/api/ai/notifications', methods=['POST'])
def customer_notifications():
    """
    Art Tracker requests customer notification messages
    Returns personalized customer communications
    """
    try:
        data = request.json
        
        order_status = data.get('order_status', {})
        customer_info = data.get('customer_info', {})
        
        # Get AI-generated message
        notification = framing_ai.generate_customer_notifications(
            order_status, customer_info
        )
        
        return jsonify({
            'success': True,
            'notification_message': notification,
            'order_id': order_status.get('order_id'),
            'customer_name': customer_info.get('name'),
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_message': f"Hello {customer_info.get('name', 'Valued Customer')}, your order is being processed. We'll update you soon!"
        }), 500

# QUALITY CONTROL ENDPOINT
@app.route('/api/ai/quality', methods=['POST'])
def quality_control():
    """
    Quality control assessment for finished pieces
    Returns detailed quality analysis
    """
    try:
        data = request.json
        
        work_photos = data.get('work_photos', [])
        quality_standards = data.get('quality_standards', {})
        
        # Get AI quality assessment
        assessment = framing_ai.quality_control_assessment(work_photos, quality_standards)
        
        return jsonify({
            'success': True,
            'quality_assessment': assessment,
            'assessed_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_message': 'Quality control AI unavailable. Please proceed with manual inspection.'
        }), 500

# BUSINESS ANALYTICS ENDPOINT
@app.route('/api/ai/analytics', methods=['POST'])
def business_analytics():
    """
    Hub requests comprehensive business analysis
    Returns profit analysis and business insights
    """
    try:
        data = request.json
        
        sales_data = data.get('sales_data', {})
        cost_data = data.get('cost_data', {})
        timeframe = data.get('timeframe', 'Last 30 days')
        
        # Get AI analysis
        analysis = framing_ai.analyze_profit_and_sales(sales_data, cost_data, timeframe)
        
        return jsonify({
            'success': True,
            'business_analysis': analysis,
            'timeframe': timeframe,
            'analyzed_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_message': 'Business analytics AI unavailable. Please review data manually.'
        }), 500

# AI USAGE ANALYTICS ENDPOINT
@app.route('/api/ai/usage', methods=['GET'])
def ai_usage_analytics():
    """
    Get AI system usage statistics and costs
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        # Get usage insights
        insights = framing_ai.get_business_insights(days=days)
        
        return jsonify({
            'success': True,
            'usage_insights': insights,
            'timeframe_days': days,
            'retrieved_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# HEALTH CHECK ENDPOINT
@app.route('/api/ai/health', methods=['GET'])
def health_check():
    """
    Check if AI services are operational
    """
    try:
        # Test basic AI functionality
        test_response = framing_ai.model_handler.get_response([
            {"role": "user", "content": "Test message"}
        ], "gpt-4o-mini")
        
        return jsonify({
            'status': 'healthy',
            'ai_services': 'operational',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'degraded',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

if __name__ == '__main__':
    app.run(debug=True, port=5001)