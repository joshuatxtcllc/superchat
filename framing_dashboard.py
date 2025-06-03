import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from framing_business_integration import FramingBusinessAI, SystemIntegrations

# Page configuration for framing business dashboard
st.set_page_config(
    page_title="ArtFrame AI Hub",
    page_icon="🖼️",
    layout="wide"
)

# Initialize AI system
if 'framing_ai' not in st.session_state:
    st.session_state.framing_ai = FramingBusinessAI()

framing_ai = st.session_state.framing_ai

st.title("🖼️ ArtFrame AI Business Hub")
st.markdown("**AI-Powered Custom Framing Operations Center**")

# Sidebar for business modules
with st.sidebar:
    st.header("Business Modules")
    
    module = st.selectbox("Select Module", [
        "Design Consultation",
        "Order Processing", 
        "Production Planning",
        "Customer Notifications",
        "Quality Control",
        "Business Analytics",
        "AI Usage Dashboard"
    ])

if module == "Design Consultation":
    st.header("🎨 AI Design Consultation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customer Information")
        customer_name = st.text_input("Customer Name")
        customer_budget = st.number_input("Budget ($)", min_value=0, value=200)
        customer_id = st.text_input("Customer ID", value=f"CUST{datetime.now().strftime('%m%d%H%M')}")
        
        st.subheader("Artwork Details")
        artwork_description = st.text_area("Artwork Description", 
            placeholder="e.g., Original oil painting, 16x20 inches, abstract modern art")
        artwork_value = st.number_input("Artwork Value ($)", min_value=0, value=500)
        
    with col2:
        st.subheader("Customer Preferences")
        style_preference = st.selectbox("Style Preference", 
            ["Traditional", "Modern", "Contemporary", "Rustic", "Minimalist", "Ornate"])
        color_preference = st.text_input("Color Preferences", 
            placeholder="e.g., warm tones, neutral colors, bold contrasts")
        protection_level = st.selectbox("Protection Level", 
            ["Standard", "Museum Quality", "Archival", "UV Protection"])
        
        special_requirements = st.text_area("Special Requirements",
            placeholder="e.g., non-reflective glass, specific dimensions, mounting preferences")
    
    if st.button("Generate Design Recommendation", type="primary"):
        if artwork_description and customer_name:
            with st.spinner("AI is analyzing artwork and generating custom framing recommendations..."):
                customer_data = {
                    'name': customer_name,
                    'budget': customer_budget,
                    'customer_id': customer_id
                }
                
                preferences = f"Style: {style_preference}, Colors: {color_preference}, Protection: {protection_level}"
                if special_requirements:
                    preferences += f", Special: {special_requirements}"
                
                recommendation = framing_ai.process_design_request(
                    customer_data, artwork_description, preferences
                )
                
                st.success("Design Recommendation Generated!")
                st.markdown("### 🎯 AI Recommendation")
                st.markdown(recommendation)
                
                # Save to session for order processing
                st.session_state.current_design = {
                    'customer_data': customer_data,
                    'artwork': artwork_description,
                    'preferences': preferences,
                    'recommendation': recommendation
                }

elif module == "Order Processing":
    st.header("📋 AI Order Processing & Validation")
    
    if 'current_design' in st.session_state:
        st.info(f"Processing order for: {st.session_state.current_design['customer_data']['name']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Order Details")
        order_id = st.text_input("Order ID", value=f"ORD{datetime.now().strftime('%Y%m%d%H%M')}")
        frame_material = st.selectbox("Frame Material", 
            ["Hardwood Oak", "Hardwood Cherry", "Aluminum Silver", "Aluminum Black", "Ornate Gold", "Modern Steel"])
        frame_width = st.selectbox("Frame Width", ["1 inch", "1.5 inch", "2 inch", "2.5 inch", "3 inch"])
        
        mat_style = st.selectbox("Mat Style", ["Single Mat", "Double Mat", "Triple Mat", "No Mat"])
        mat_color = st.text_input("Mat Color", value="Cream")
        
    with col2:
        st.subheader("Technical Specifications")
        glass_type = st.selectbox("Glass Type", 
            ["Standard Glass", "Non-Glare Glass", "UV Protection", "Museum Glass", "Acrylic"])
        backing_type = st.selectbox("Backing", ["Standard", "Acid-Free", "Museum Board"])
        
        rush_order = st.checkbox("Rush Order (+50% fee)")
        delivery_method = st.selectbox("Delivery", ["Pickup", "Local Delivery", "Shipping"])
        
        notes = st.text_area("Special Instructions")
    
    if st.button("Process Order with AI Validation", type="primary"):
        order_data = {
            'order_id': order_id,
            'customer_id': st.session_state.get('current_design', {}).get('customer_data', {}).get('customer_id', 'UNKNOWN'),
            'frame_material': frame_material,
            'frame_width': frame_width,
            'mat_style': mat_style,
            'mat_color': mat_color,
            'glass_type': glass_type,
            'backing_type': backing_type,
            'rush_order': rush_order,
            'delivery_method': delivery_method,
            'notes': notes,
            'timestamp': datetime.now().isoformat()
        }
        
        with st.spinner("AI is validating order and calculating costs..."):
            order_analysis = framing_ai.process_order(order_data)
            
            st.success("Order Processed Successfully!")
            st.markdown("### 💰 AI Cost Analysis & Validation")
            st.markdown(order_analysis)

elif module == "Production Planning":
    st.header("🏭 AI Production Scheduling")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Orders")
        # Simulate current orders
        current_orders = [
            {'order_id': 'ORD001', 'priority': 'High', 'deadline': '2024-01-15', 'complexity': 'Medium'},
            {'order_id': 'ORD002', 'priority': 'Normal', 'deadline': '2024-01-18', 'complexity': 'High'},
            {'order_id': 'ORD003', 'priority': 'Low', 'deadline': '2024-01-20', 'complexity': 'Low'}
        ]
        
        for order in current_orders:
            with st.expander(f"Order {order['order_id']} - {order['priority']} Priority"):
                st.write(f"Deadline: {order['deadline']}")
                st.write(f"Complexity: {order['complexity']}")
        
        st.subheader("Workshop Capacity")
        daily_capacity = st.number_input("Daily Frame Capacity", value=5)
        staff_available = st.number_input("Staff Available", value=2)
        overtime_available = st.checkbox("Overtime Available")
        
    with col2:
        st.subheader("Material Inventory")
        materials = {
            'Hardwood Frames': st.number_input("Hardwood Frames", value=15),
            'Aluminum Frames': st.number_input("Aluminum Frames", value=8),
            'Museum Glass': st.number_input("Museum Glass Sheets", value=12),
            'Standard Glass': st.number_input("Standard Glass Sheets", value=25),
            'Mat Board': st.number_input("Mat Board Sheets", value=50)
        }
        
        st.subheader("Equipment Status")
        equipment_status = {
            'Mat Cutter': st.selectbox("Mat Cutter", ["Available", "In Use", "Maintenance"]),
            'Glass Cutter': st.selectbox("Glass Cutter", ["Available", "In Use", "Maintenance"]),
            'Frame Saw': st.selectbox("Frame Saw", ["Available", "In Use", "Maintenance"])
        }
    
    if st.button("Generate AI Production Schedule", type="primary"):
        workshop_capacity = {
            'daily_frames': daily_capacity,
            'staff_available': staff_available,
            'overtime_available': overtime_available,
            'equipment_status': equipment_status
        }
        
        with st.spinner("AI is optimizing production schedule..."):
            schedule = framing_ai.optimize_production_schedule(
                current_orders, workshop_capacity, materials
            )
            
            st.success("Production Schedule Optimized!")
            st.markdown("### 📅 AI-Optimized Schedule")
            st.markdown(schedule)

elif module == "Customer Notifications":
    st.header("📱 AI Customer Communication")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Order Status Update")
        order_id = st.text_input("Order ID", value="ORD001")
        current_status = st.selectbox("Current Status", [
            "Order Received", "In Design", "Materials Ordered", "In Production", 
            "Quality Check", "Ready for Pickup", "Completed"
        ])
        estimated_completion = st.date_input("Estimated Completion")
        
        st.subheader("Customer Information")
        customer_name = st.text_input("Customer Name", value="John Smith")
        customer_email = st.text_input("Customer Email")
        customer_phone = st.text_input("Customer Phone")
        preferred_contact = st.selectbox("Preferred Contact", ["Email", "SMS", "Phone"])
        
    with col2:
        st.subheader("Additional Details")
        special_notes = st.text_area("Special Notes", 
            placeholder="Any specific updates or issues to communicate")
        
        notification_type = st.selectbox("Notification Type", [
            "Status Update", "Delay Notification", "Ready for Pickup", 
            "Delivery Scheduled", "Follow-up"
        ])
        
        urgency = st.selectbox("Urgency Level", ["Normal", "High", "Urgent"])
    
    if st.button("Generate AI Notification", type="primary"):
        order_status = {
            'order_id': order_id,
            'current_status': current_status,
            'estimated_completion': estimated_completion.strftime("%B %d, %Y"),
            'special_notes': special_notes,
            'notification_type': notification_type
        }
        
        customer_info = {
            'name': customer_name,
            'email': customer_email,
            'phone': customer_phone,
            'preferred_contact': preferred_contact
        }
        
        with st.spinner("AI is crafting personalized customer message..."):
            notification = framing_ai.generate_customer_notifications(order_status, customer_info)
            
            st.success("Customer Notification Generated!")
            st.markdown("### 💬 AI-Generated Message")
            st.markdown(notification)
            
            # Show delivery options
            st.markdown("### 📤 Send Notification")
            if customer_email and preferred_contact in ["Email", "Both"]:
                st.button(f"Send Email to {customer_email}")
            if customer_phone and preferred_contact in ["SMS", "Phone", "Both"]:
                st.button(f"Send SMS to {customer_phone}")

elif module == "Business Analytics":
    st.header("📊 AI Business Intelligence")
    
    # Sample data for demonstration
    sales_data = {
        'total_revenue': 15000,
        'orders_completed': 45,
        'average_order_value': 333.33,
        'top_products': ['Museum Quality Frames', 'Double Mat Designs', 'UV Protection Glass'],
        'monthly_growth': 12.5
    }
    
    cost_data = {
        'material_costs': 8000,
        'labor_costs': 4500,
        'overhead': 1500,
        'ai_costs': 150
    }
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"${sales_data['total_revenue']:,}", 
                 delta=f"+{sales_data['monthly_growth']}%")
    
    with col2:
        st.metric("Orders Completed", sales_data['orders_completed'], delta="+8")
    
    with col3:
        st.metric("Avg Order Value", f"${sales_data['average_order_value']:.2f}", delta="+$25")
    
    with col4:
        profit = sales_data['total_revenue'] - sum(cost_data.values())
        st.metric("Net Profit", f"${profit:,}", delta="+15%")
    
    if st.button("Generate AI Business Analysis", type="primary"):
        with st.spinner("AI is analyzing business performance..."):
            analysis = framing_ai.analyze_profit_and_sales(sales_data, cost_data, "Last 30 days")
            
            st.success("Business Analysis Complete!")
            st.markdown("### 🧠 AI Business Insights")
            st.markdown(analysis)

elif module == "AI Usage Dashboard":
    st.header("🤖 AI System Analytics")
    
    # Get AI usage insights
    insights = framing_ai.get_business_insights(days=30)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total AI Interactions", insights['total_ai_interactions'])
    
    with col2:
        st.metric("Cost per Interaction", f"${insights['cost_per_interaction']:.3f}")
    
    with col3:
        avg_efficiency = sum(insights['efficiency_metrics'].values()) / len(insights['efficiency_metrics']) if insights['efficiency_metrics'] else 0
        st.metric("Avg Response Time", f"{avg_efficiency:.2f}s")
    
    # Most used features chart
    if insights['most_used_features']:
        feature_names = [feature[0] for feature in insights['most_used_features']]
        feature_usage = [feature[1]['total_uses'] for feature in insights['most_used_features']]
        
        fig = px.bar(x=feature_names, y=feature_usage, 
                    title="Most Used AI Features",
                    labels={'x': 'AI Feature', 'y': 'Usage Count'})
        st.plotly_chart(fig, use_container_width=True)

# Integration instructions
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 System Integrations")
st.sidebar.markdown("""
**Connect your existing systems:**
- Designer → Design Consultation
- POS → Order Processing  
- Hub → Business Analytics
- Art Tracker → Customer Notifications
- Kanban → Production Planning
""")