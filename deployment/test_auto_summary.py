#!/usr/bin/env python3
"""
Test script for auto-summary functionality
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

from src.utils.redis_client import RedisClient
from src.utils.logger import Logger
from src.llms.openai import LLMOpenAI
from src.memory.redis_summaryMemory import SummaryConversation

logger = Logger(__name__)

def test_metadata_operations():
    """Test metadata save and retrieve operations"""
    logger.info("🧪 Testing metadata operations...")
    
    llm = LLMOpenAI()
    summary_conv = SummaryConversation(llm=llm, number_of_summary=5)
    
    # Test saving metadata
    result = summary_conv.save_summary_metadata("test_session_123", 15)
    assert result, "Failed to save metadata"
    logger.info("✅ Metadata save test passed")
    
    # Test retrieving metadata
    metadata = summary_conv.get_summary_metadata()
    assert metadata["last_summary_session_id"] == "test_session_123"
    assert metadata["total_sessions_at_summary"] == 15
    logger.info("✅ Metadata retrieve test passed")
    
    return True

def test_session_counting():
    """Test new session counting logic"""
    logger.info("🧪 Testing session counting...")
    
    llm = LLMOpenAI()
    summary_conv = SummaryConversation(llm=llm, number_of_summary=3)
    
    # Get current count
    new_sessions = summary_conv.count_new_sessions()
    logger.info(f"📊 Current new sessions count: {new_sessions}")
    
    # Test should_auto_summary logic
    should_summary = summary_conv.should_auto_summary()
    logger.info(f"🤔 Should auto-summary: {should_summary}")
    
    return True

def test_auto_summary_check():
    """Test the auto-summary check without actually performing summary"""
    logger.info("🧪 Testing auto-summary check...")
    
    llm = LLMOpenAI()
    summary_conv = SummaryConversation(llm=llm, number_of_summary=100)  # High threshold to avoid actual summary
    
    result = summary_conv.auto_summary()
    logger.info(f"📋 Auto-summary check result: {result}")
    
    assert "status" in result
    assert "message" in result
    logger.info("✅ Auto-summary check test passed")
    
    return True

def test_redis_connection():
    """Test Redis connection and basic operations"""
    logger.info("🧪 Testing Redis connection...")
    
    redis_client = RedisClient()
    
    # Test connection
    assert redis_client.redis_client is not None, "Redis client not connected"
    
    # Test basic operations
    test_key = "test_auto_summary_key"
    test_value = "test_value"
    
    # Set and get
    set_result = redis_client.set(test_key, test_value)
    assert set_result, "Failed to set test key"
    
    get_result = redis_client.get(test_key)
    assert get_result == test_value, f"Expected {test_value}, got {get_result}"
    
    logger.info("✅ Redis connection test passed")
    return True

def simulate_new_sessions(count=5):
    """Simulate adding new sessions to Redis for testing"""
    logger.info(f"🎭 Simulating {count} new sessions...")
    
    redis_client = RedisClient()
    
    for i in range(count):
        session_id = f"test_session_{i}_{os.getpid()}"
        session_data = {
            "messages": [
                {"role": "user", "content": f"Test message {i}"},
                {"role": "assistant", "content": f"Test response {i}"}
            ],
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        result = redis_client.set(f"memory:{session_id}", json.dumps(session_data))
        if result:
            logger.info(f"✅ Created test session: memory:{session_id}")
        else:
            logger.error(f"❌ Failed to create test session: memory:{session_id}")
    
    return True

def cleanup_test_data():
    """Clean up test data from Redis"""
    logger.info("🧹 Cleaning up test data...")
    
    redis_client = RedisClient()
    
    # Clean up test sessions
    test_keys = redis_client.redis_client.keys("memory:test_session_*")
    for key in test_keys:
        redis_client.redis_client.delete(key)
        logger.info(f"🗑️ Deleted test key: {key}")
    
    # Clean up test metadata
    redis_client.redis_client.delete("test_auto_summary_key")
    
    logger.info("✅ Cleanup completed")

def main():
    """Run all tests"""
    logger.info("🚀 Starting auto-summary tests...")
    
    try:
        # Test Redis connection first
        test_redis_connection()
        
        # Test metadata operations
        test_metadata_operations()
        
        # Test session counting
        test_session_counting()
        
        # Test auto-summary check
        test_auto_summary_check()
        
        # Simulate some new sessions for testing
        simulate_new_sessions(3)
        
        logger.info("✅ All tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
    
    finally:
        # Clean up
        cleanup_test_data()

if __name__ == "__main__":
    main()
