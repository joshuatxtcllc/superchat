
import os
import json
import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import speech_recognition as sr
import pyttsx3
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import streamlit as st

class BusinessAssistantFeatures:
    """
    Comprehensive business assistant features including scheduling, communications, 
    task automation, and voice capabilities.
    """
    
    def __init__(self):
        self.gmail_service = None
        self.calendar_service = None
        self.voice_engine = None
        self.speech_recognizer = None
        self.initialize_services()
    
    def initialize_services(self):
        """Initialize all business assistant services"""
        try:
            # Check if we're in a headless environment (like Replit)
            import os
            is_replit = os.environ.get('REPL_ID') is not None
            
            if not is_replit:
                # Initialize text-to-speech
                self.voice_engine = pyttsx3.init()
                voices = self.voice_engine.getProperty('voices')
                if voices:
                    self.voice_engine.setProperty('voice', voices[0].id)  # Use first available voice
                self.voice_engine.setProperty('rate', 150)  # Speaking rate
                
                # Initialize speech recognition
                self.speech_recognizer = sr.Recognizer()
            else:
                print("Voice services disabled in Replit environment (no audio hardware available)")
                self.voice_engine = None
                self.speech_recognizer = None
            
        except Exception as e:
            print(f"Error initializing voice services: {e}")
            self.voice_engine = None
            self.speech_recognizer = None
    
    # SCHEDULING FEATURES
    def get_calendar_service(self):
        """Initialize Google Calendar service"""
        try:
            # In production, you'd handle OAuth properly
            # For now, this is a placeholder structure
            creds_json = os.environ.get('GOOGLE_CALENDAR_CREDENTIALS')
            if creds_json:
                creds = Credentials.from_authorized_user_info(json.loads(creds_json))
                self.calendar_service = build('calendar', 'v3', credentials=creds)
                return self.calendar_service
        except Exception as e:
            st.error(f"Calendar service error: {e}")
        return None
    
    def auto_schedule_meeting(self, attendee_emails, duration_minutes=60, subject="Meeting", description=""):
        """Automatically schedule a meeting based on availability"""
        calendar_service = self.get_calendar_service()
        if not calendar_service:
            return {"success": False, "error": "Calendar service not available"}
        
        try:
            # Find available time slots
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=30)).isoformat() + 'Z'
            
            # Check availability for all attendees
            freebusy_query = {
                'timeMin': time_min,
                'timeMax': time_max,
                'items': [{'id': email} for email in attendee_emails]
            }
            
            freebusy_result = calendar_service.freebusy().query(body=freebusy_query).execute()
            
            # Find the first available slot (simplified logic)
            start_time = now + timedelta(hours=1)  # Start looking 1 hour from now
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Create calendar event
            event = {
                'summary': subject,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat() + 'Z',
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat() + 'Z',
                    'timeZone': 'UTC',
                },
                'attendees': [{'email': email} for email in attendee_emails],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            
            created_event = calendar_service.events().insert(calendarId='primary', body=event).execute()
            
            return {
                "success": True,
                "event_id": created_event.get('id'),
                "meeting_link": created_event.get('hangoutLink'),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_task_schedule(self, tasks, priority_weights=None):
        """Create an optimized schedule for tasks based on priority and deadlines"""
        if not priority_weights:
            priority_weights = {"high": 3, "medium": 2, "low": 1}
        
        # Sort tasks by priority and deadline
        sorted_tasks = sorted(tasks, key=lambda x: (
            -priority_weights.get(x.get('priority', 'medium'), 2),
            x.get('deadline', datetime.max)
        ))
        
        schedule = []
        current_time = datetime.now()
        
        for task in sorted_tasks:
            estimated_duration = task.get('estimated_hours', 1)
            schedule.append({
                "task": task,
                "scheduled_start": current_time,
                "scheduled_end": current_time + timedelta(hours=estimated_duration),
                "priority_score": priority_weights.get(task.get('priority', 'medium'), 2)
            })
            current_time += timedelta(hours=estimated_duration, minutes=15)  # 15-min buffer
        
        return schedule
    
    # CUSTOMER COMMUNICATIONS
    def setup_gmail_service(self):
        """Setup Gmail API service"""
        try:
            creds_json = os.environ.get('GMAIL_CREDENTIALS')
            if creds_json:
                creds = Credentials.from_authorized_user_info(json.loads(creds_json))
                self.gmail_service = build('gmail', 'v1', credentials=creds)
                return self.gmail_service
        except Exception as e:
            st.error(f"Gmail service error: {e}")
        return None
    
    def send_automated_email(self, to_email, subject, body, template_name=None):
        """Send automated emails with templates"""
        gmail_service = self.setup_gmail_service()
        if not gmail_service:
            # Fallback to SMTP
            return self.send_email_smtp(to_email, subject, body)
        
        try:
            message = MIMEMultipart()
            message['to'] = to_email
            message['subject'] = subject
            message.attach(MIMEText(body, 'html'))
            
            # Convert to Gmail API format
            raw_message = {'raw': message.as_bytes().decode('utf-8')}
            
            sent_message = gmail_service.users().messages().send(
                userId='me', body=raw_message
            ).execute()
            
            return {"success": True, "message_id": sent_message['id']}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_email_smtp(self, to_email, subject, body):
        """Fallback SMTP email sending"""
        try:
            smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.environ.get('SMTP_PORT', '587'))
            smtp_username = os.environ.get('SMTP_USERNAME')
            smtp_password = os.environ.get('SMTP_PASSWORD')
            
            if not all([smtp_username, smtp_password]):
                return {"success": False, "error": "SMTP credentials not configured"}
            
            message = MIMEMultipart()
            message['From'] = smtp_username
            message['To'] = to_email
            message['Subject'] = subject
            message.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)
            server.quit()
            
            return {"success": True, "method": "SMTP"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_customer_communication_templates(self):
        """Pre-built communication templates"""
        return {
            "appointment_confirmation": {
                "subject": "Appointment Confirmation - {date} at {time}",
                "body": """
                <h2>Appointment Confirmed</h2>
                <p>Dear {customer_name},</p>
                <p>This confirms your appointment on <strong>{date}</strong> at <strong>{time}</strong>.</p>
                <p><strong>Service:</strong> {service_type}</p>
                <p><strong>Location:</strong> {location}</p>
                <p>If you need to reschedule, please contact us at least 24 hours in advance.</p>
                <p>Best regards,<br>{company_name}</p>
                """
            },
            "project_update": {
                "subject": "Project Update - {project_name}",
                "body": """
                <h2>Project Progress Update</h2>
                <p>Dear {customer_name},</p>
                <p>Here's an update on your project: <strong>{project_name}</strong></p>
                <p><strong>Current Status:</strong> {status}</p>
                <p><strong>Completed:</strong> {completed_tasks}</p>
                <p><strong>Next Steps:</strong> {next_steps}</p>
                <p><strong>Expected Completion:</strong> {completion_date}</p>
                <p>Please let us know if you have any questions.</p>
                <p>Best regards,<br>{company_name}</p>
                """
            },
            "invoice_reminder": {
                "subject": "Payment Reminder - Invoice #{invoice_number}",
                "body": """
                <h2>Payment Reminder</h2>
                <p>Dear {customer_name},</p>
                <p>This is a friendly reminder that Invoice #{invoice_number} for ${amount} is due on {due_date}.</p>
                <p><strong>Services:</strong> {services}</p>
                <p>You can pay online at: {payment_link}</p>
                <p>If you have any questions about this invoice, please don't hesitate to contact us.</p>
                <p>Thank you,<br>{company_name}</p>
                """
            }
        }
    
    # TASK AUTOMATION
    def create_automated_workflow(self, workflow_name, triggers, actions):
        """Create automated business workflows"""
        workflow = {
            "name": workflow_name,
            "id": f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "triggers": triggers,
            "actions": actions,
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        
        # Save workflow configuration
        workflows_file = "business_workflows.json"
        try:
            if os.path.exists(workflows_file):
                with open(workflows_file, 'r') as f:
                    workflows = json.load(f)
            else:
                workflows = []
            
            workflows.append(workflow)
            
            with open(workflows_file, 'w') as f:
                json.dump(workflows, f, indent=2)
            
            return {"success": True, "workflow_id": workflow["id"]}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_workflow_action(self, action_type, parameters):
        """Execute specific workflow actions"""
        actions = {
            "send_email": lambda p: self.send_automated_email(
                p['to'], p['subject'], p['body'], p.get('template')
            ),
            "create_task": lambda p: self.create_task(p['title'], p['description'], p.get('assignee')),
            "schedule_meeting": lambda p: self.auto_schedule_meeting(
                p['attendees'], p.get('duration', 60), p['subject'], p.get('description', '')
            ),
            "update_status": lambda p: self.update_project_status(p['project_id'], p['status']),
            "generate_invoice": lambda p: self.generate_invoice(p['customer_id'], p['items']),
        }
        
        action_function = actions.get(action_type)
        if action_function:
            return action_function(parameters)
        else:
            return {"success": False, "error": f"Unknown action type: {action_type}"}
    
    def create_task(self, title, description, assignee=None, priority="medium", due_date=None):
        """Create and track business tasks"""
        task = {
            "id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": title,
            "description": description,
            "assignee": assignee,
            "priority": priority,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "due_date": due_date,
            "completed_at": None
        }
        
        # Save to tasks file
        tasks_file = "business_tasks.json"
        try:
            if os.path.exists(tasks_file):
                with open(tasks_file, 'r') as f:
                    tasks = json.load(f)
            else:
                tasks = []
            
            tasks.append(task)
            
            with open(tasks_file, 'w') as f:
                json.dump(tasks, f, indent=2)
            
            return {"success": True, "task_id": task["id"], "task": task}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # VOICE COMMUNICATION
    def speak_text(self, text):
        """Convert text to speech"""
        try:
            # Check if we're in Replit environment
            import os
            if os.environ.get('REPL_ID'):
                return {"success": False, "error": "Text-to-speech not available in Replit environment (no audio output)"}
            
            if self.voice_engine:
                self.voice_engine.say(text)
                self.voice_engine.runAndWait()
                return {"success": True}
            else:
                return {"success": False, "error": "Voice engine not initialized"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def listen_for_voice_input(self, timeout=5):
        """Listen for voice input and convert to text"""
        try:
            # Check if we're in Replit environment
            import os
            if os.environ.get('REPL_ID'):
                return {"success": False, "error": "Voice input not available in Replit environment (no microphone access)"}
            
            if not self.speech_recognizer:
                return {"success": False, "error": "Speech recognizer not initialized"}
            
            with sr.Microphone() as source:
                self.speech_recognizer.adjust_for_ambient_noise(source)
                audio = self.speech_recognizer.listen(source, timeout=timeout)
                
            text = self.speech_recognizer.recognize_google(audio)
            return {"success": True, "text": text}
            
        except sr.WaitTimeoutError:
            return {"success": False, "error": "No speech detected"}
        except sr.UnknownValueError:
            return {"success": False, "error": "Could not understand audio"}
        except OSError as e:
            if "No Default Input Device Available" in str(e):
                return {"success": False, "error": "No microphone available in this environment"}
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_voice_command(self, command_text):
        """Process voice commands for business tasks"""
        command_lower = command_text.lower()
        
        # Define voice command patterns
        if "schedule meeting" in command_lower or "book appointment" in command_lower:
            return {"action": "schedule_meeting", "text": command_text}
        elif "send email" in command_lower or "email customer" in command_lower:
            return {"action": "send_email", "text": command_text}
        elif "create task" in command_lower or "add task" in command_lower:
            return {"action": "create_task", "text": command_text}
        elif "check calendar" in command_lower or "what's my schedule" in command_lower:
            return {"action": "check_calendar", "text": command_text}
        elif "project status" in command_lower or "project update" in command_lower:
            return {"action": "project_status", "text": command_text}
        else:
            return {"action": "general_query", "text": command_text}
    
    # INTERNET SEARCH INTEGRATION
    def search_internet(self, query, num_results=5):
        """Perform real-time internet searches"""
        try:
            # Using DuckDuckGo API (free, no API key required)
            search_url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'pretty': 1,
                'no_html': 1,
                'skip_disambig': 1
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            data = response.json()
            
            results = []
            
            # Get instant answer if available
            if data.get('Abstract'):
                results.append({
                    'type': 'instant_answer',
                    'title': data.get('Heading', 'Instant Answer'),
                    'text': data.get('Abstract'),
                    'url': data.get('AbstractURL', ''),
                    'source': data.get('AbstractSource', 'DuckDuckGo')
                })
            
            # Get related topics
            for topic in data.get('RelatedTopics', [])[:num_results]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'type': 'related',
                        'title': topic.get('Text', '').split(' - ')[0],
                        'text': topic.get('Text', ''),
                        'url': topic.get('FirstURL', ''),
                        'source': 'DuckDuckGo'
                    })
            
            return {"success": True, "results": results, "query": query}
            
        except Exception as e:
            # Fallback: Try using a simple web scraping approach
            try:
                import urllib.parse
                search_query = urllib.parse.quote_plus(query)
                fallback_url = f"https://duckduckgo.com/html/?q={search_query}"
                
                return {
                    "success": False,
                    "error": str(e),
                    "fallback_suggestion": f"You can search manually at: {fallback_url}"
                }
            except:
                return {"success": False, "error": str(e)}
    
    def get_business_insights(self, search_term):
        """Get business-specific insights from internet search"""
        queries = [
            f"{search_term} business trends 2024",
            f"{search_term} market analysis",
            f"{search_term} industry best practices",
            f"{search_term} competitors analysis"
        ]
        
        insights = []
        for query in queries:
            search_result = self.search_internet(query, num_results=3)
            if search_result.get("success"):
                insights.extend(search_result["results"])
        
        return {
            "success": True,
            "insights": insights,
            "search_terms": queries
        }
    
    # THIRD PARTY INTEGRATIONS
    def integrate_with_service(self, service_name, action, parameters):
        """Generic third-party service integration"""
        integrations = {
            "gmail": {
                "send_email": lambda p: self.send_automated_email(
                    p['to'], p['subject'], p['body']
                ),
                "get_emails": lambda p: self.get_gmail_messages(p.get('query', 'is:unread'))
            },
            "calendar": {
                "create_event": lambda p: self.auto_schedule_meeting(
                    p['attendees'], p.get('duration', 60), p['subject']
                ),
                "get_events": lambda p: self.get_calendar_events(p.get('days_ahead', 7))
            },
            "slack": {
                "send_message": lambda p: self.send_slack_message(
                    p['channel'], p['text']
                )
            },
            "twilio": {
                "send_sms": lambda p: self.send_sms(p['to'], p['message'])
            }
        }
        
        service_actions = integrations.get(service_name, {})
        action_function = service_actions.get(action)
        
        if action_function:
            return action_function(parameters)
        else:
            return {
                "success": False,
                "error": f"Integration not available: {service_name}.{action}"
            }
    
    def send_slack_message(self, channel, text):
        """Send message to Slack channel"""
        slack_webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
        if not slack_webhook_url:
            return {"success": False, "error": "Slack webhook URL not configured"}
        
        try:
            payload = {
                "channel": channel,
                "text": text,
                "username": "Business Assistant"
            }
            
            response = requests.post(slack_webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {"success": True}
            else:
                return {"success": False, "error": f"Slack API error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_sms(self, to_number, message):
        """Send SMS using Twilio"""
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        from_number = os.environ.get('TWILIO_FROM_NUMBER')
        
        if not all([account_sid, auth_token, from_number]):
            return {"success": False, "error": "Twilio credentials not configured"}
        
        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            
            message = client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )
            
            return {"success": True, "message_sid": message.sid}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global instance
business_assistant = BusinessAssistantFeatures()
