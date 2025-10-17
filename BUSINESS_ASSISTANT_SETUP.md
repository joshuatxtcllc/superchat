
# Business Assistant Features Setup Guide

This guide will help you configure all the business assistant features including auto-scheduling, customer communications, task automation, and voice communication.

## 🎯 Core Features Available

### 1. Auto-Scheduling System
- **Calendar Integration** with Google Calendar
- **Smart Meeting Scheduling** based on availability  
- **Automated Appointment Booking** for customers
- **Task Scheduling and Deadline Management**

### 2. Customer Communications Hub  
- **Email Automation** via Gmail API or SMTP
- **SMS Notifications** with Twilio integration
- **Pre-built Templates** for common communications
- **Customer Inquiry Routing** and response automation

### 3. Task Automation Engine
- **Workflow Creation** with custom triggers and actions
- **Document Generation** and processing
- **Invoice and Estimate Automation** 
- **Project Milestone Tracking**

### 4. Natural Voice Communication
- **Text-to-Speech** for AI responses
- **Voice-to-Text** input for hands-free operation
- **Voice Commands** for common business tasks
- **Audio Meeting Summaries**

### 5. Real-Time Internet Search
- **DuckDuckGo Integration** for web searches
- **Business Intelligence** gathering
- **Market Research** automation
- **Competitor Analysis** tools

### 6. Third-Party Integrations
- **Gmail API** for email management
- **Google Calendar** for scheduling  
- **Twilio** for SMS communications
- **Slack** for team notifications

## 🔧 Environment Variables Setup

Add these to your Replit Secrets:

### Gmail Integration
```
GMAIL_CREDENTIALS={"installed":{"client_id":"your_client_id","client_secret":"your_client_secret","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token"}}
```

### Google Calendar Integration  
```
GOOGLE_CALENDAR_CREDENTIALS={"installed":{"client_id":"your_client_id","client_secret":"your_client_secret","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token"}}
```

### SMTP Email (Alternative to Gmail API)
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com  
SMTP_PASSWORD=your_app_password
```

### Twilio SMS Integration
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890
```

### Slack Integration
```  
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## 🚀 Quick Start Guide

### 1. Enable Basic Features
1. Go to the Business Assistant section in the sidebar
2. Start with **Communications** - set up SMTP email first
3. Test email sending with the built-in templates

### 2. Add Voice Features
1. Voice features work out-of-the-box for basic functionality
2. For advanced features, ensure microphone permissions are granted
3. Test text-to-speech in the Voice Assistant panel

### 3. Set Up Internet Search
1. Internet search works immediately with DuckDuckGo
2. No API keys required for basic search functionality
3. Test with business-related queries

### 4. Configure Advanced Integrations
1. Set up Gmail API credentials for advanced email features
2. Configure Google Calendar for auto-scheduling
3. Add Twilio for SMS notifications

## 📋 Feature Usage Examples

### Auto-Scheduling
```python
# Schedule a meeting automatically
result = business_assistant.auto_schedule_meeting(
    attendee_emails=['client@example.com', 'team@example.com'],
    duration_minutes=60,
    subject='Project Kickoff Meeting',
    description='Initial project discussion and planning'
)
```

### Email Automation  
```python
# Send automated email with template
result = business_assistant.send_automated_email(
    to_email='customer@example.com',
    subject='Project Update - Your Home Renovation',
    body=project_update_template,
    template_name='project_update'
)
```

### Task Automation
```python
# Create automated workflow
workflow = business_assistant.create_automated_workflow(
    workflow_name='New Customer Onboarding',
    triggers=[{'type': 'email_received', 'pattern': 'new customer'}],
    actions=[
        {'type': 'send_email', 'template': 'welcome'},
        {'type': 'create_task', 'title': 'Setup customer account'},
        {'type': 'schedule_meeting', 'subject': 'Welcome call'}
    ]
)
```

### Voice Commands
```python
# Process voice input
voice_result = business_assistant.listen_for_voice_input()
if voice_result.get('success'):
    command = business_assistant.process_voice_command(voice_result['text'])
    # Execute the appropriate action
```

### Internet Search
```python
# Search for business insights
insights = business_assistant.get_business_insights('construction market trends')
# Returns market analysis, competitor info, and industry best practices
```

## 🎨 UI Access

All features are accessible through the Business Assistant sidebar menu:

- **📅 Scheduling Hub** - Auto-scheduling and calendar management
- **📧 Communications** - Email templates and SMS messaging  
- **🤖 Task Automation** - Workflow creation and task management
- **🎙️ Voice Assistant** - Voice input/output and commands
- **🔍 Internet Search** - Real-time web search and business intelligence

## 🔒 Security Notes

1. **API Keys**: Store all credentials in Replit Secrets, never in code
2. **OAuth**: Use proper OAuth flows for Google services in production
3. **Data Privacy**: Ensure customer data is handled according to privacy laws
4. **Rate Limiting**: Be mindful of API rate limits for third-party services

## 🆘 Troubleshooting

### Voice Features Not Working
- Check microphone permissions in browser
- Ensure `pyaudio` is properly installed
- Test with simple text-to-speech first

### Email Not Sending  
- Verify SMTP credentials in Secrets
- Check Gmail "App Passwords" if using Gmail SMTP
- Test with a simple email first

### Calendar Integration Issues
- Ensure proper OAuth setup for Google Calendar
- Check API quotas and permissions
- Verify credentials format in Secrets

### Search Not Working
- DuckDuckGo search should work without setup
- Check internet connectivity
- Try simpler search queries first

## 📞 Support

For additional help:
1. Check the error messages in the app
2. Review the console logs for detailed errors  
3. Test individual components separately
4. Verify all environment variables are set correctly

---

**Ready to transform your business with AI assistance!** 🚀
