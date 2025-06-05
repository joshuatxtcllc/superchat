
import requests
import json
import asyncio
import websockets
from datetime import datetime
from typing import Dict, Any, Optional
from white_label_config import WhiteLabelConfig

class HubConnectionManager:
    """Manages connection to the Central Hub Dashboard"""
    
    def __init__(self, config: WhiteLabelConfig):
        self.config = config
        self.connection_status = False
        self.last_sync = None
        self.session = requests.Session()
        
        # Set up headers
        if config.connection.hub_api_key:
            self.session.headers.update({
                'X-API-Key': config.connection.hub_api_key,
                'Content-Type': 'application/json',
                'User-Agent': f"{config.connection.app_name}/{config.connection.app_version}"
            })
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Hub Dashboard"""
        try:
            if not self.config.connection.enable_hub_integration:
                return {
                    'success': False,
                    'message': 'Hub integration not enabled',
                    'status': 'disabled'
                }
            
            url = f"{self.config.connection.hub_dashboard_url}{self.config.connection.hub_connection_test_endpoint}"
            
            response = self.session.get(
                url,
                timeout=self.config.connection.connection_timeout
            )
            
            if response.status_code == 200:
                self.connection_status = True
                return {
                    'success': True,
                    'message': 'Connected to Hub Dashboard',
                    'status': 'connected',
                    'response_time': response.elapsed.total_seconds(),
                    'hub_info': response.json() if response.content else {}
                }
            else:
                return {
                    'success': False,
                    'message': f'Connection failed: {response.status_code}',
                    'status': 'failed'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': 'Connection timeout',
                'status': 'timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection error: {str(e)}',
                'status': 'error'
            }
    
    def register_app(self) -> Dict[str, Any]:
        """Register this app with the Hub Dashboard"""
        try:
            url = f"{self.config.connection.hub_dashboard_url}/api/apps/register"
            
            registration_data = {
                'app_id': self.config.connection.app_id,
                'app_name': self.config.connection.app_name,
                'app_version': self.config.connection.app_version,
                'app_type': 'multi-model-chat',
                'features': {
                    'ai_models': True,
                    'conversation_management': True,
                    'image_generation': self.config.features.enable_image_generation,
                    'file_upload': self.config.features.enable_file_upload,
                    'deep_thinking': self.config.features.enable_deep_thinking
                },
                'endpoints': {
                    'health': '/health',
                    'chat': '/api/chat',
                    'models': '/api/models'
                },
                'timestamp': datetime.now().isoformat()
            }
            
            response = self.session.post(url, json=registration_data)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'App registered successfully',
                    'registration_id': response.json().get('registration_id')
                }
            else:
                return {
                    'success': False,
                    'message': f'Registration failed: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Registration error: {str(e)}'
            }
    
    def send_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Send event to Hub Dashboard"""
        try:
            if not self.connection_status:
                return False
            
            url = f"{self.config.connection.hub_dashboard_url}{self.config.connection.hub_events_endpoint}"
            
            event_payload = {
                'app_id': self.config.connection.app_id,
                'event_type': event_type,
                'event_data': event_data,
                'timestamp': datetime.now().isoformat()
            }
            
            response = self.session.post(url, json=event_payload)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def send_conversation_event(self, conversation_id: str, message_count: int, 
                               model_used: str, response_time: float) -> bool:
        """Send conversation analytics to Hub"""
        return self.send_event('conversation', {
            'conversation_id': conversation_id,
            'message_count': message_count,
            'model_used': model_used,
            'response_time': response_time,
            'features_used': {
                'image_generation': self.config.features.enable_image_generation,
                'deep_thinking': self.config.features.enable_deep_thinking
            }
        })
    
    def send_usage_analytics(self, daily_stats: Dict[str, Any]) -> bool:
        """Send usage analytics to Hub"""
        return self.send_event('usage_analytics', daily_stats)
    
    def get_hub_configuration(self) -> Optional[Dict[str, Any]]:
        """Get configuration updates from Hub"""
        try:
            url = f"{self.config.connection.hub_dashboard_url}/api/apps/{self.config.connection.app_id}/config"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception:
            return None
    
    async def setup_websocket_connection(self):
        """Set up WebSocket connection for real-time updates"""
        if not self.config.connection.enable_real_time_sync:
            return
        
        try:
            ws_url = f"{self.config.connection.hub_websocket_url}/ws/{self.config.connection.app_id}"
            
            async with websockets.connect(
                ws_url,
                extra_headers={'X-API-Key': self.config.connection.hub_api_key}
            ) as websocket:
                await websocket.send(json.dumps({
                    'action': 'subscribe',
                    'app_id': self.config.connection.app_id
                }))
                
                async for message in websocket:
                    data = json.loads(message)
                    await self.handle_websocket_message(data)
                    
        except Exception as e:
            print(f"WebSocket connection error: {e}")
    
    async def handle_websocket_message(self, message: Dict[str, Any]):
        """Handle incoming WebSocket messages from Hub"""
        message_type = message.get('type')
        
        if message_type == 'config_update':
            # Handle configuration updates
            pass
        elif message_type == 'broadcast':
            # Handle broadcast messages
            pass
        elif message_type == 'ping':
            # Respond to ping
            pass

def create_hub_connection(config: WhiteLabelConfig) -> HubConnectionManager:
    """Factory function to create Hub connection manager"""
    return HubConnectionManager(config)
import requests
import json
import time
from datetime import datetime

class HubConnectionManager:
    """Manages connections to the Central Hub Dashboard"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        
    def test_connection(self):
        """Test connection to the Hub Dashboard"""
        if not self.config.connection.enable_hub_integration:
            return {
                "success": False,
                "message": "Hub integration is disabled"
            }
            
        if not self.config.connection.hub_dashboard_url:
            return {
                "success": False,
                "message": "Hub Dashboard URL not configured"
            }
            
        if not self.config.connection.hub_api_key:
            return {
                "success": False,
                "message": "Hub API key not configured"
            }
        
        try:
            # Test connection endpoint
            test_url = f"{self.config.connection.hub_dashboard_url.rstrip('/')}/api/health"
            
            headers = {
                "X-API-Key": self.config.connection.hub_api_key,
                "Content-Type": "application/json"
            }
            
            start_time = time.time()
            response = self.session.get(
                test_url,
                headers=headers,
                timeout=self.config.connection.connection_timeout
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Hub connection successful",
                    "response_time": response_time,
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "message": f"Hub returned status {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "Could not connect to Hub Dashboard. Check the URL."
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "Connection to Hub Dashboard timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection error: {str(e)}"
            }
    
    def register_app(self):
        """Register this app instance with the Hub"""
        if not self.test_connection()['success']:
            return {
                "success": False,
                "message": "Cannot register - Hub connection failed"
            }
        
        try:
            register_url = f"{self.config.connection.hub_dashboard_url.rstrip('/')}/api/apps/register"
            
            headers = {
                "X-API-Key": self.config.connection.hub_api_key,
                "Content-Type": "application/json"
            }
            
            app_data = {
                "app_id": self.config.connection.app_id,
                "app_name": self.config.branding.app_title,
                "company_name": self.config.branding.company_name,
                "registration_time": datetime.now().isoformat(),
                "features": {
                    "model_comparison": self.config.features.enable_model_comparison,
                    "image_generation": self.config.features.enable_image_generation,
                    "file_upload": self.config.features.enable_file_upload
                }
            }
            
            response = self.session.post(
                register_url,
                headers=headers,
                json=app_data,
                timeout=self.config.connection.connection_timeout
            )
            
            if response.status_code in [200, 201]:
                data = response.json() if response.content else {}
                return {
                    "success": True,
                    "message": "App registered successfully",
                    "registration_id": data.get("registration_id", "unknown")
                }
            else:
                return {
                    "success": False,
                    "message": f"Registration failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Registration error: {str(e)}"
            }
    
    def send_analytics_event(self, event_type, event_data):
        """Send an analytics event to the Hub"""
        if not self.config.connection.enable_hub_integration:
            return False
            
        try:
            events_url = f"{self.config.connection.hub_dashboard_url.rstrip('/')}/api/events"
            
            headers = {
                "X-API-Key": self.config.connection.hub_api_key,
                "Content-Type": "application/json"
            }
            
            event_payload = {
                "app_id": self.config.connection.app_id,
                "event_type": event_type,
                "event_data": event_data,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(
                events_url,
                headers=headers,
                json=event_payload,
                timeout=5  # Short timeout for analytics
            )
            
            return response.status_code in [200, 201, 202]
            
        except:
            # Silently fail for analytics
            return False
