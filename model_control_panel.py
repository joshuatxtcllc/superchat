import streamlit as st
from model_usage_tracker import model_usage_tracker
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

class ModelControlPanel:
    """UI for managing AI model usage, limits, and controls"""
    
    def __init__(self):
        self.tracker = model_usage_tracker
    
    def render(self):
        """Render the complete model control panel"""
        st.title("🎛️ AI Model Control Panel")
        st.markdown("*Manage AI model access, spending limits, and usage monitoring*")
        
        # Overview metrics
        self._render_overview()
        
        st.divider()
        
        # Main tabs
        tabs = st.tabs([
            "📊 Usage Dashboard",
            "🎚️ Model Controls",
            "💰 Spending Limits",
            "⚡ Circuit Breakers",
            "📈 Analytics"
        ])
        
        with tabs[0]:
            self._render_usage_dashboard()
        
        with tabs[1]:
            self._render_model_controls()
        
        with tabs[2]:
            self._render_spending_limits()
        
        with tabs[3]:
            self._render_circuit_breakers()
        
        with tabs[4]:
            self._render_analytics()
    
    def _render_overview(self):
        """Render overview metrics"""
        col1, col2, col3, col4 = st.columns(4)
        
        total_cost = self.tracker.get_total_cost()
        total_tokens = self.tracker.get_total_tokens()
        total_calls = sum(m.daily_calls for m in self.tracker.model_metrics.values())
        enabled_models = sum(1 for m in self.tracker.model_metrics.values() if m.enabled)
        
        with col1:
            st.metric("Total Daily Cost", f"${total_cost:.2f}")
        
        with col2:
            st.metric("Total Daily Tokens", f"{total_tokens:,}")
        
        with col3:
            st.metric("Total API Calls", f"{total_calls:,}")
        
        with col4:
            st.metric("Enabled Models", f"{enabled_models}/{len(self.tracker.model_metrics)}")
    
    def _render_usage_dashboard(self):
        """Render usage dashboard"""
        st.header("Current Usage by Model")
        
        # Create usage table
        usage_data = []
        for model_id, metrics in self.tracker.model_metrics.items():
            status = "✅" if metrics.enabled else "🔴"
            circuit_state = self.tracker.circuit_breakers.get(model_id, {}).get("state", "closed")
            circuit_icon = "🔵" if circuit_state == "closed" else "🔴" if circuit_state == "open" else "🟡"
            
            # Calculate usage percentages
            call_pct = (metrics.daily_calls / metrics.daily_call_limit * 100) if metrics.daily_call_limit > 0 else 0
            token_pct = ((metrics.daily_input_tokens + metrics.daily_output_tokens) / metrics.daily_token_limit * 100) if metrics.daily_token_limit > 0 else 0
            cost_pct = (metrics.daily_cost / metrics.daily_cost_limit * 100) if metrics.daily_cost_limit > 0 else 0
            
            usage_data.append({
                "Status": status,
                "Circuit": circuit_icon,
                "Model": metrics.model_name,
                "Calls": f"{metrics.daily_calls:,}",
                "Tokens": f"{metrics.daily_input_tokens + metrics.daily_output_tokens:,}",
                "Cost": f"${metrics.daily_cost:.4f}",
                "Call Limit": f"{call_pct:.0f}%" if metrics.daily_call_limit > 0 else "N/A",
                "Token Limit": f"{token_pct:.0f}%" if metrics.daily_token_limit > 0 else "N/A",
                "Cost Limit": f"{cost_pct:.0f}%" if metrics.daily_cost_limit > 0 else "N/A",
            })
        
        if usage_data:
            st.dataframe(usage_data, use_container_width=True, hide_index=True)
        
        # Quick actions
        st.subheader("Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Reset All Daily Metrics", type="secondary"):
                self.tracker.reset_daily_metrics()
                st.success("✅ All daily metrics reset!")
                st.rerun()
        
        with col2:
            if st.button("✅ Enable All Models", type="secondary"):
                for model_id in self.tracker.model_metrics.keys():
                    self.tracker.set_model_enabled(model_id, True)
                st.success("✅ All models enabled!")
                st.rerun()
        
        with col3:
            if st.button("🔴 Disable All Models", type="secondary"):
                for model_id in self.tracker.model_metrics.keys():
                    self.tracker.set_model_enabled(model_id, False)
                st.success("🔴 All models disabled!")
                st.rerun()
    
    def _render_model_controls(self):
        """Render model toggle controls"""
        st.header("Model Toggle Controls")
        st.markdown("Enable or disable specific AI models. Disabled models cannot be used for chat.")
        
        # Group models by provider
        providers = {}
        for model_id, metrics in self.tracker.model_metrics.items():
            # Determine provider from model_id
            if "gpt" in model_id:
                provider = "OpenAI"
            elif "claude" in model_id:
                provider = "Anthropic"
            elif "gemini" in model_id:
                provider = "Google"
            elif "llama" in model_id:
                provider = "Meta"
            elif "mistral" in model_id:
                provider = "Mistral"
            else:
                provider = "Other"
            
            if provider not in providers:
                providers[provider] = []
            providers[provider].append((model_id, metrics))
        
        # Render by provider
        for provider, models in sorted(providers.items()):
            st.subheader(f"🏢 {provider} Models")
            cols = st.columns(2)
            
            for idx, (model_id, metrics) in enumerate(models):
                with cols[idx % 2]:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**{metrics.model_name}**")
                            st.caption(f"Calls: {metrics.daily_calls:,} | Tokens: {metrics.daily_input_tokens + metrics.daily_output_tokens:,} | Cost: ${metrics.daily_cost:.4f}")
                        
                        with col2:
                            enabled = st.toggle(
                                "Enable",
                                value=metrics.enabled,
                                key=f"toggle_{model_id}"
                            )
                            if enabled != metrics.enabled:
                                self.tracker.set_model_enabled(model_id, enabled)
                                st.rerun()
                        
                        # Show circuit breaker status
                        circuit_state = self.tracker.circuit_breakers.get(model_id, {}).get("state", "closed")
                        if circuit_state == "open":
                            st.error("⚠️ Circuit breaker is OPEN (too many errors)")
                        elif circuit_state == "half_open":
                            st.warning("🟡 Circuit breaker is HALF-OPEN (testing)")
    
    def _render_spending_limits(self):
        """Render spending limits configuration"""
        st.header("Spending Limits Configuration")
        st.markdown("Set daily spending limits for each model. When limits are reached, the model will be blocked.")
        
        # Global limits
        st.subheader("Global Daily Limits")
        col1, col2 = st.columns(2)
        
        with col1:
            global_cost_limit = st.number_input(
                "Global Daily Cost Limit ($)",
                min_value=0.0,
                value=50.0,
                step=1.0,
                help="Maximum total spending across all models per day"
            )
        
        with col2:
            current_global_cost = self.tracker.get_total_cost()
            progress = min(current_global_cost / global_cost_limit, 1.0) if global_cost_limit > 0 else 0
            st.metric("Current Global Spend", f"${current_global_cost:.2f}")
            st.progress(progress, text=f"{progress*100:.1f}% of limit")
        
        st.divider()
        
        # Per-model limits
        st.subheader("Per-Model Daily Limits")
        
        for model_id, metrics in self.tracker.model_metrics.items():
            with st.expander(f"📊 {metrics.model_name}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    call_limit = st.number_input(
                        "Daily Call Limit",
                        min_value=0,
                        value=metrics.daily_call_limit,
                        step=10,
                        key=f"call_limit_{model_id}",
                        help="0 = unlimited"
                    )
                
                with col2:
                    token_limit = st.number_input(
                        "Daily Token Limit",
                        min_value=0,
                        value=metrics.daily_token_limit,
                        step=1000,
                        key=f"token_limit_{model_id}",
                        help="0 = unlimited"
                    )
                
                with col3:
                    cost_limit = st.number_input(
                        "Daily Cost Limit ($)",
                        min_value=0.0,
                        value=metrics.daily_cost_limit,
                        step=0.5,
                        key=f"cost_limit_{model_id}",
                        help="0 = unlimited"
                    )
                
                # Show current usage
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    call_pct = (metrics.daily_calls / call_limit * 100) if call_limit > 0 else 0
                    st.caption(f"Current: {metrics.daily_calls:,} calls ({call_pct:.1f}%)")
                
                with col2:
                    total_tokens = metrics.daily_input_tokens + metrics.daily_output_tokens
                    token_pct = (total_tokens / token_limit * 100) if token_limit > 0 else 0
                    st.caption(f"Current: {total_tokens:,} tokens ({token_pct:.1f}%)")
                
                with col3:
                    cost_pct = (metrics.daily_cost / cost_limit * 100) if cost_limit > 0 else 0
                    st.caption(f"Current: ${metrics.daily_cost:.4f} ({cost_pct:.1f}%)")
                
                if st.button(f"💾 Save Limits for {metrics.model_name}", key=f"save_{model_id}"):
                    self.tracker.set_model_limits(model_id, call_limit, token_limit, cost_limit)
                    st.success(f"✅ Limits saved for {metrics.model_name}!")
                    st.rerun()
    
    def _render_circuit_breakers(self):
        """Render circuit breaker status and controls"""
        st.header("⚡ Circuit Breakers")
        st.markdown("Circuit breakers automatically disable models experiencing repeated errors to prevent cascading failures.")
        
        st.info("""
        **How Circuit Breakers Work:**
        - **Closed (🔵)**: Model is operating normally
        - **Open (🔴)**: Model has failed multiple times and is temporarily disabled
        - **Half-Open (🟡)**: Testing if model has recovered after timeout
        
        Models automatically move from Open to Half-Open after 60 seconds, then back to Closed if successful.
        """)
        
        # Circuit breaker status table
        for model_id, metrics in self.tracker.model_metrics.items():
            circuit = self.tracker.circuit_breakers.get(model_id, {})
            state = circuit.get("state", "closed")
            error_count = circuit.get("error_count", 0)
            last_error = circuit.get("last_error")
            
            # Color code based on state
            if state == "closed":
                color = "🔵"
                state_text = "CLOSED (Normal)"
                state_color = "success"
            elif state == "open":
                color = "🔴"
                state_text = "OPEN (Blocked)"
                state_color = "error"
            else:
                color = "🟡"
                state_text = "HALF-OPEN (Testing)"
                state_color = "warning"
            
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                
                with col1:
                    st.write(f"{color} **{metrics.model_name}**")
                
                with col2:
                    if state_color == "success":
                        st.success(state_text)
                    elif state_color == "error":
                        st.error(state_text)
                    else:
                        st.warning(state_text)
                
                with col3:
                    st.caption(f"Errors: {error_count}/3")
                
                with col4:
                    if state in ["open", "half_open"]:
                        if st.button("🔄 Reset", key=f"reset_circuit_{model_id}"):
                            self.tracker.reset_circuit_breaker(model_id)
                            st.success(f"✅ Circuit breaker reset for {metrics.model_name}!")
                            st.rerun()
                
                if last_error:
                    error_time = datetime.fromisoformat(last_error)
                    st.caption(f"Last error: {error_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                st.divider()
    
    def _render_analytics(self):
        """Render usage analytics and charts"""
        st.header("📈 Usage Analytics")
        
        # Cost breakdown by model
        st.subheader("Daily Cost by Model")
        
        cost_data = {
            metrics.model_name: metrics.daily_cost
            for metrics in self.tracker.model_metrics.values()
            if metrics.daily_cost > 0
        }
        
        if cost_data:
            fig = px.pie(
                names=list(cost_data.keys()),
                values=list(cost_data.values()),
                title="Cost Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cost data available yet. Start using models to see analytics.")
        
        # Token usage by model
        st.subheader("Daily Token Usage by Model")
        
        token_data = {
            metrics.model_name: metrics.daily_input_tokens + metrics.daily_output_tokens
            for metrics in self.tracker.model_metrics.values()
            if (metrics.daily_input_tokens + metrics.daily_output_tokens) > 0
        }
        
        if token_data:
            fig = go.Figure(data=[
                go.Bar(
                    x=list(token_data.keys()),
                    y=list(token_data.values()),
                    text=[f"{v:,}" for v in token_data.values()],
                    textposition='auto',
                )
            ])
            fig.update_layout(
                title="Token Usage Comparison",
                xaxis_title="Model",
                yaxis_title="Tokens",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # API calls by model
        st.subheader("API Calls by Model")
        
        call_data = {
            metrics.model_name: metrics.daily_calls
            for metrics in self.tracker.model_metrics.values()
            if metrics.daily_calls > 0
        }
        
        if call_data:
            fig = go.Figure(data=[
                go.Bar(
                    x=list(call_data.keys()),
                    y=list(call_data.values()),
                    text=list(call_data.values()),
                    textposition='auto',
                    marker_color='lightblue'
                )
            ])
            fig.update_layout(
                title="API Call Distribution",
                xaxis_title="Model",
                yaxis_title="Number of Calls",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed metrics table
        st.subheader("Detailed Model Metrics")
        
        detailed_data = []
        for model_id, metrics in self.tracker.model_metrics.items():
            pricing = model_usage_tracker.MODEL_PRICING.get(model_id)
            if pricing:
                detailed_data.append({
                    "Model": metrics.model_name,
                    "Input Tokens": f"{metrics.daily_input_tokens:,}",
                    "Output Tokens": f"{metrics.daily_output_tokens:,}",
                    "Total Tokens": f"{metrics.daily_input_tokens + metrics.daily_output_tokens:,}",
                    "API Calls": metrics.daily_calls,
                    "Daily Cost": f"${metrics.daily_cost:.4f}",
                    "Total Cost": f"${metrics.total_cost:.2f}",
                    "Input $/1M": f"${pricing.input_cost:.2f}",
                    "Output $/1M": f"${pricing.output_cost:.2f}",
                })
        
        if detailed_data:
            st.dataframe(detailed_data, use_container_width=True, hide_index=True)

# Global instance
model_control_panel = ModelControlPanel()
