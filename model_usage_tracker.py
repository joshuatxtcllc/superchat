import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional
import logging

@dataclass
class ModelPricing:
    """Pricing information for AI models (per 1M tokens)"""
    input_cost: float
    output_cost: float
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate total cost based on token usage"""
        return (input_tokens * self.input_cost / 1_000_000) + (output_tokens * self.output_cost / 1_000_000)

@dataclass
class ModelUsageMetrics:
    """Track usage metrics for a specific model"""
    model_id: str
    model_name: str
    enabled: bool = True
    total_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost: float = 0.0
    last_used: str = ""
    
    # Limits
    daily_call_limit: int = 0  # 0 = unlimited
    daily_token_limit: int = 0  # 0 = unlimited
    daily_cost_limit: float = 0.0  # 0 = unlimited
    
    # Current daily usage (reset daily)
    daily_calls: int = 0
    daily_input_tokens: int = 0
    daily_output_tokens: int = 0
    daily_cost: float = 0.0
    last_reset: str = ""

@dataclass
class CircuitBreakerSettings:
    """Circuit breaker settings for automatic model failover"""
    enabled: bool = True
    error_threshold: int = 3  # Number of consecutive errors before opening circuit
    timeout_seconds: int = 60  # Time before attempting to close circuit
    fallback_models: List[str] = field(default_factory=list)  # Models to use if primary fails

class ModelUsageTracker:
    """Enhanced usage tracking system with per-model metrics, limits, and circuit breakers"""
    
    # Model pricing (approximate, per 1M tokens)
    MODEL_PRICING = {
        "gpt-4o": ModelPricing(input_cost=5.00, output_cost=15.00),
        "gpt-4o-mini": ModelPricing(input_cost=0.15, output_cost=0.60),
        "gpt-3.5-turbo": ModelPricing(input_cost=0.50, output_cost=1.50),
        "claude-3-5-sonnet-20241022": ModelPricing(input_cost=3.00, output_cost=15.00),
        "claude-3-haiku-20240307": ModelPricing(input_cost=0.25, output_cost=1.25),
        "claude-3-sonnet-20240229": ModelPricing(input_cost=3.00, output_cost=15.00),
        "claude-3-opus-20240229": ModelPricing(input_cost=15.00, output_cost=75.00),
        "gemini-pro": ModelPricing(input_cost=0.50, output_cost=1.50),
        "gemini-pro-vision": ModelPricing(input_cost=0.50, output_cost=1.50),
        "llama-3-70b-chat": ModelPricing(input_cost=0.88, output_cost=0.88),
        "mistral-large-latest": ModelPricing(input_cost=4.00, output_cost=12.00),
    }
    
    def __init__(self):
        self.metrics_file = "model_usage_metrics.json"
        self.circuit_breaker_file = "circuit_breaker_state.json"
        self.log_file = "model_usage_tracker.log"
        
        # Setup logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.model_metrics: Dict[str, ModelUsageMetrics] = self.load_metrics()
        self.circuit_breakers: Dict[str, Dict] = self.load_circuit_breaker_state()
        
        # Initialize metrics for all known models
        self._initialize_model_metrics()
    
    def _initialize_model_metrics(self):
        """Initialize metrics for all models if they don't exist"""
        model_names = {
            "gpt-4o": "GPT-4o",
            "gpt-4o-mini": "GPT-4o Mini",
            "gpt-3.5-turbo": "GPT-3.5 Turbo",
            "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
            "claude-3-haiku-20240307": "Claude 3 Haiku",
            "claude-3-sonnet-20240229": "Claude 3 Sonnet",
            "claude-3-opus-20240229": "Claude 3 Opus",
            "gemini-pro": "Gemini Pro",
            "gemini-pro-vision": "Gemini Pro Vision",
            "llama-3-70b-chat": "Llama 3 70B",
            "mistral-large-latest": "Mistral Large",
        }
        
        for model_id, model_name in model_names.items():
            if model_id not in self.model_metrics:
                self.model_metrics[model_id] = ModelUsageMetrics(
                    model_id=model_id,
                    model_name=model_name,
                    enabled=True,
                    last_reset=datetime.now().isoformat()
                )
            
            if model_id not in self.circuit_breakers:
                self.circuit_breakers[model_id] = {
                    "state": "closed",  # closed, open, half_open
                    "error_count": 0,
                    "last_error": None,
                    "opened_at": None
                }
    
    def load_metrics(self) -> Dict[str, ModelUsageMetrics]:
        """Load model usage metrics from file"""
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    return {
                        model_id: ModelUsageMetrics(**metrics)
                        for model_id, metrics in data.items()
                    }
        except Exception as e:
            self.logger.error(f"Error loading metrics: {e}")
        return {}
    
    def load_circuit_breaker_state(self) -> Dict:
        """Load circuit breaker state from file"""
        try:
            if os.path.exists(self.circuit_breaker_file):
                with open(self.circuit_breaker_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading circuit breaker state: {e}")
        return {}
    
    def save_metrics(self):
        """Save model usage metrics to file"""
        try:
            data = {
                model_id: asdict(metrics)
                for model_id, metrics in self.model_metrics.items()
            }
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")
    
    def save_circuit_breaker_state(self):
        """Save circuit breaker state to file"""
        try:
            with open(self.circuit_breaker_file, 'w') as f:
                json.dump(self.circuit_breakers, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving circuit breaker state: {e}")
    
    def is_model_available(self, model_id: str) -> tuple[bool, str]:
        """Check if a model is available for use"""
        if model_id not in self.model_metrics:
            return False, f"Model {model_id} not found"
        
        metrics = self.model_metrics[model_id]
        
        # Check if model is enabled
        if not metrics.enabled:
            return False, f"Model {metrics.model_name} is disabled"
        
        # Check circuit breaker
        circuit_state = self.circuit_breakers.get(model_id, {})
        if circuit_state.get("state") == "open":
            # Check if timeout has passed
            opened_at = circuit_state.get("opened_at")
            if opened_at:
                opened_time = datetime.fromisoformat(opened_at)
                if datetime.now() - opened_time < timedelta(seconds=60):
                    return False, f"Model {metrics.model_name} circuit breaker is open (too many errors)"
                else:
                    # Move to half-open state
                    self.circuit_breakers[model_id]["state"] = "half_open"
                    self.save_circuit_breaker_state()
        
        # Check daily limits
        if metrics.daily_call_limit > 0 and metrics.daily_calls >= metrics.daily_call_limit:
            return False, f"Model {metrics.model_name} has reached daily call limit ({metrics.daily_call_limit})"
        
        if metrics.daily_token_limit > 0 and (metrics.daily_input_tokens + metrics.daily_output_tokens) >= metrics.daily_token_limit:
            return False, f"Model {metrics.model_name} has reached daily token limit ({metrics.daily_token_limit:,})"
        
        if metrics.daily_cost_limit > 0 and metrics.daily_cost >= metrics.daily_cost_limit:
            return False, f"Model {metrics.model_name} has reached daily cost limit (${metrics.daily_cost_limit:.2f})"
        
        return True, "Available"
    
    def track_usage(self, model_id: str, input_tokens: int, output_tokens: int, success: bool = True):
        """Track usage for a model"""
        if model_id not in self.model_metrics:
            self.logger.warning(f"Tracking usage for unknown model: {model_id}")
            return
        
        metrics = self.model_metrics[model_id]
        
        # Calculate cost
        pricing = self.MODEL_PRICING.get(model_id, ModelPricing(input_cost=0.0, output_cost=0.0))
        cost = pricing.calculate_cost(input_tokens, output_tokens)
        
        # Update metrics
        metrics.total_calls += 1
        metrics.input_tokens += input_tokens
        metrics.output_tokens += output_tokens
        metrics.total_cost += cost
        metrics.last_used = datetime.now().isoformat()
        
        # Update daily metrics
        metrics.daily_calls += 1
        metrics.daily_input_tokens += input_tokens
        metrics.daily_output_tokens += output_tokens
        metrics.daily_cost += cost
        
        # Update circuit breaker
        if success:
            # Reset error count on success
            if self.circuit_breakers[model_id]["state"] == "half_open":
                # Success in half-open state, close the circuit
                self.circuit_breakers[model_id]["state"] = "closed"
                self.circuit_breakers[model_id]["error_count"] = 0
                self.logger.info(f"Circuit breaker closed for {model_id}")
            else:
                self.circuit_breakers[model_id]["error_count"] = 0
        else:
            # Increment error count on failure
            self.circuit_breakers[model_id]["error_count"] += 1
            self.circuit_breakers[model_id]["last_error"] = datetime.now().isoformat()
            
            # Open circuit if threshold exceeded
            if self.circuit_breakers[model_id]["error_count"] >= 3:
                self.circuit_breakers[model_id]["state"] = "open"
                self.circuit_breakers[model_id]["opened_at"] = datetime.now().isoformat()
                self.logger.warning(f"Circuit breaker opened for {model_id} due to repeated errors")
        
        self.save_metrics()
        self.save_circuit_breaker_state()
        
        self.logger.info(f"Tracked usage for {model_id}: {input_tokens} input, {output_tokens} output, ${cost:.4f}")
    
    def reset_daily_metrics(self, model_id: Optional[str] = None):
        """Reset daily metrics for one or all models"""
        if model_id:
            if model_id in self.model_metrics:
                metrics = self.model_metrics[model_id]
                metrics.daily_calls = 0
                metrics.daily_input_tokens = 0
                metrics.daily_output_tokens = 0
                metrics.daily_cost = 0.0
                metrics.last_reset = datetime.now().isoformat()
                self.logger.info(f"Reset daily metrics for {model_id}")
        else:
            for metrics in self.model_metrics.values():
                metrics.daily_calls = 0
                metrics.daily_input_tokens = 0
                metrics.daily_output_tokens = 0
                metrics.daily_cost = 0.0
                metrics.last_reset = datetime.now().isoformat()
            self.logger.info("Reset daily metrics for all models")
        
        self.save_metrics()
    
    def set_model_enabled(self, model_id: str, enabled: bool):
        """Enable or disable a specific model"""
        if model_id in self.model_metrics:
            self.model_metrics[model_id].enabled = enabled
            self.save_metrics()
            self.logger.info(f"Model {model_id} {'enabled' if enabled else 'disabled'}")
    
    def set_model_limits(self, model_id: str, call_limit: int = 0, token_limit: int = 0, cost_limit: float = 0.0):
        """Set usage limits for a specific model"""
        if model_id in self.model_metrics:
            metrics = self.model_metrics[model_id]
            metrics.daily_call_limit = call_limit
            metrics.daily_token_limit = token_limit
            metrics.daily_cost_limit = cost_limit
            self.save_metrics()
            self.logger.info(f"Updated limits for {model_id}: calls={call_limit}, tokens={token_limit}, cost=${cost_limit}")
    
    def get_total_cost(self) -> float:
        """Get total cost across all models"""
        return sum(metrics.daily_cost for metrics in self.model_metrics.values())
    
    def get_total_tokens(self) -> int:
        """Get total tokens used across all models"""
        return sum(metrics.daily_input_tokens + metrics.daily_output_tokens for metrics in self.model_metrics.values())
    
    def get_usage_summary(self) -> Dict:
        """Get comprehensive usage summary"""
        return {
            "total_daily_cost": self.get_total_cost(),
            "total_daily_tokens": self.get_total_tokens(),
            "total_daily_calls": sum(m.daily_calls for m in self.model_metrics.values()),
            "models": {
                model_id: {
                    "name": metrics.model_name,
                    "enabled": metrics.enabled,
                    "daily_calls": metrics.daily_calls,
                    "daily_tokens": metrics.daily_input_tokens + metrics.daily_output_tokens,
                    "daily_cost": metrics.daily_cost,
                    "circuit_state": self.circuit_breakers.get(model_id, {}).get("state", "closed"),
                    "limits": {
                        "calls": metrics.daily_call_limit,
                        "tokens": metrics.daily_token_limit,
                        "cost": metrics.daily_cost_limit
                    }
                }
                for model_id, metrics in self.model_metrics.items()
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_circuit_breaker(self, model_id: str):
        """Manually reset a circuit breaker"""
        if model_id in self.circuit_breakers:
            self.circuit_breakers[model_id] = {
                "state": "closed",
                "error_count": 0,
                "last_error": None,
                "opened_at": None
            }
            self.save_circuit_breaker_state()
            self.logger.info(f"Circuit breaker manually reset for {model_id}")

# Global instance
model_usage_tracker = ModelUsageTracker()
