
import logging
import os
from datetime import datetime

class AppLogger:
    def __init__(self):
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Configure logging
        log_filename = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def log_user_message(self, conversation_id, message_length, model_used):
        """Log user interactions"""
        self.logger.info(f"User message - Conv: {conversation_id}, Length: {message_length}, Model: {model_used}")
    
    def log_api_call(self, model_id, success, response_time=None, error=None):
        """Log API calls"""
        if success:
            self.logger.info(f"API success - Model: {model_id}, Time: {response_time}s")
        else:
            self.logger.error(f"API error - Model: {model_id}, Error: {error}")
    
    def log_error(self, error_type, error_message, context=None):
        """Log application errors"""
        self.logger.error(f"{error_type}: {error_message} - Context: {context}")
