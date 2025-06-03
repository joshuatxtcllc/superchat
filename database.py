import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSON

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    preferences = Column(JSON, default={})

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)  # Allow anonymous users
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, default={})

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    conversation_id = Column(String, index=True)
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    model_used = Column(String, nullable=True)
    model_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    mcp_context = Column(JSON, nullable=True)
    token_count = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=True)

class ModelUsage(Base):
    __tablename__ = "model_usage"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)
    model_id = Column(String)
    model_name = Column(String)
    task_type = Column(String, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=True)
    success = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cost_estimate = Column(Float, nullable=True)

class ModelRecommendation(Base):
    __tablename__ = "model_recommendations"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)
    task_description = Column(Text)
    recommended_model = Column(String)
    explanation = Column(Text)
    alternative_models = Column(JSON, default=[])
    user_accepted = Column(Boolean, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatabaseManager:
    """Manages database operations for the chat interface"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        create_tables()
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def save_conversation(self, conversation_id, user_id=None, title="New Conversation"):
        """Save or update a conversation"""
        session = self.get_session()
        try:
            conversation = session.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if conversation:
                conversation.updated_at = datetime.utcnow()
                conversation.title = title
            else:
                conversation = Conversation(
                    id=conversation_id,
                    user_id=user_id,
                    title=title
                )
                session.add(conversation)
            
            session.commit()
            return conversation
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_message(self, message_id, conversation_id, role, content, 
                    model_used=None, model_id=None, mcp_context=None, 
                    token_count=None, response_time=None):
        """Save a message to the database"""
        session = self.get_session()
        try:
            message = Message(
                id=message_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
                model_used=model_used,
                model_id=model_id,
                mcp_context=mcp_context,
                token_count=token_count,
                response_time=response_time
            )
            session.add(message)
            session.commit()
            return message
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_conversation_messages(self, conversation_id):
        """Get all messages for a conversation"""
        session = self.get_session()
        try:
            messages = session.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp).all()
            
            return [{
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'model': msg.model_used,
                'model_id': msg.model_id,
                'timestamp': msg.timestamp.strftime("%I:%M %p, %B %d"),
                'mcp_context': msg.mcp_context
            } for msg in messages]
        finally:
            session.close()
    
    def get_user_conversations(self, user_id=None):
        """Get all conversations for a user"""
        session = self.get_session()
        try:
            query = session.query(Conversation).filter(
                Conversation.is_active == True
            )
            if user_id:
                query = query.filter(Conversation.user_id == user_id)
            else:
                query = query.filter(Conversation.user_id.is_(None))
            
            conversations = query.order_by(Conversation.updated_at.desc()).all()
            
            return [{
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.strftime("%B %d, %Y"),
                'updated_at': conv.updated_at.strftime("%B %d, %Y")
            } for conv in conversations]
        finally:
            session.close()
    
    def log_model_usage(self, user_id, model_id, model_name, task_type=None, 
                       tokens_used=None, response_time=None, success=True, cost_estimate=None):
        """Log model usage for analytics"""
        session = self.get_session()
        try:
            import uuid
            usage = ModelUsage(
                id=str(uuid.uuid4()),
                user_id=user_id,
                model_id=model_id,
                model_name=model_name,
                task_type=task_type,
                tokens_used=tokens_used,
                response_time=response_time,
                success=success,
                cost_estimate=cost_estimate
            )
            session.add(usage)
            session.commit()
            return usage
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_recommendation(self, user_id, task_description, recommended_model, 
                          explanation, alternative_models, user_accepted=None):
        """Save model recommendation data"""
        session = self.get_session()
        try:
            import uuid
            recommendation = ModelRecommendation(
                id=str(uuid.uuid4()),
                user_id=user_id,
                task_description=task_description,
                recommended_model=recommended_model,
                explanation=explanation,
                alternative_models=alternative_models,
                user_accepted=user_accepted
            )
            session.add(recommendation)
            session.commit()
            return recommendation
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_model_analytics(self, user_id=None, days=30):
        """Get model usage analytics"""
        session = self.get_session()
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = session.query(ModelUsage).filter(
                ModelUsage.timestamp >= cutoff_date
            )
            if user_id:
                query = query.filter(ModelUsage.user_id == user_id)
            
            usage_data = query.all()
            
            # Aggregate statistics
            stats = {}
            for usage in usage_data:
                model = usage.model_name
                if model not in stats:
                    stats[model] = {
                        'total_uses': 0,
                        'total_tokens': 0,
                        'avg_response_time': 0,
                        'success_rate': 0,
                        'total_cost': 0
                    }
                
                stats[model]['total_uses'] += 1
                if usage.tokens_used:
                    stats[model]['total_tokens'] += usage.tokens_used
                if usage.response_time:
                    stats[model]['avg_response_time'] += usage.response_time
                if usage.cost_estimate:
                    stats[model]['total_cost'] += usage.cost_estimate
                if usage.success:
                    stats[model]['success_rate'] += 1
            
            # Calculate averages
            for model, data in stats.items():
                if data['total_uses'] > 0:
                    data['avg_response_time'] = data['avg_response_time'] / data['total_uses']
                    data['success_rate'] = (data['success_rate'] / data['total_uses']) * 100
            
            return stats
        finally:
            session.close()