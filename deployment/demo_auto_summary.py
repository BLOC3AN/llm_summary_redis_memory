#!/usr/bin/env python3
"""
Demo script to show auto-summary functionality
This script simulates adding new sessions and triggering auto-summary
"""

import os
import sys
import json
import time
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

from src.utils.redis_client import RedisClient
from src.utils.logger import Logger
from src.llms.openai import LLMOpenAI
from src.memory.redis_summaryMemory import SummaryConversation

logger = Logger(__name__)

def add_demo_session(session_id, user_message, assistant_message):
    """Add a demo session to Redis"""
    redis_client = RedisClient()
    
    session_data = {
        "messages": [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "session_id": session_id
    }
    
    key = f"memory:{session_id}"
    result = redis_client.set(key, json.dumps(session_data))
    
    if result:
        logger.info(f"✅ Added demo session: {key}")
    else:
        logger.error(f"❌ Failed to add demo session: {key}")
    
    return result

def demo_auto_summary():
    """Demonstrate auto-summary functionality"""
    logger.info("🎬 Starting auto-summary demo...")
    
    # Initialize auto-summary with threshold of 3 for demo
    llm = LLMOpenAI()
    summary_conv = SummaryConversation(llm=llm, number_of_summary=3)
    
    # Check current status
    logger.info("📊 Checking current status...")
    result = summary_conv.check_and_auto_summary()
    logger.info(f"Initial status: {result['status']}")
    
    # Add some demo sessions
    demo_sessions = [
        {
            "session_id": f"demo_session_1_{int(time.time())}",
            "user_message": "Tôi muốn đặt dịch vụ dọn dẹp nhà cửa",
            "assistant_message": "Chào bạn! Tôi sẽ giúp bạn đặt dịch vụ dọn dẹp. Bạn có thể cho tôi biết địa chỉ và thời gian mong muốn không?"
        },
        {
            "session_id": f"demo_session_2_{int(time.time())}",
            "user_message": "Địa chỉ: 123 Nguyễn Văn Linh, Q7. Thời gian: 9h sáng mai",
            "assistant_message": "Đã ghi nhận. Dịch vụ dọn dẹp tại 123 Nguyễn Văn Linh, Q7 vào 9h sáng mai. Phí dịch vụ là 200,000 VND. Bạn có đồng ý không?"
        },
        {
            "session_id": f"demo_session_3_{int(time.time())}",
            "user_message": "Đồng ý. Tôi sẽ thanh toán bằng tiền mặt",
            "assistant_message": "Tuyệt vời! Đã xác nhận đặt lịch dọn dẹp. Nhân viên sẽ đến đúng giờ. Cảm ơn bạn đã sử dụng dịch vụ!"
        }
    ]
    
    logger.info(f"🎭 Adding {len(demo_sessions)} demo sessions...")
    
    for i, session in enumerate(demo_sessions, 1):
        logger.info(f"➕ Adding session {i}/{len(demo_sessions)}")
        add_demo_session(
            session["session_id"],
            session["user_message"], 
            session["assistant_message"]
        )
        
        # Check auto-summary after each session
        logger.info(f"🔍 Checking auto-summary after session {i}...")
        result = summary_conv.check_and_auto_summary()
        
        if result["status"] == "summary_completed":
            logger.info("🎉 Auto-summary was triggered!")
            logger.info(f"📋 Summary: {result.get('summary_data', {}).get('summary', {}).get('summary_detail', 'N/A')}")
            break
        elif result["status"] == "no_summary_needed":
            logger.info(f"⏳ Not enough sessions yet. Current: {result.get('new_sessions_count', 0)}/3")
        else:
            logger.warning(f"⚠️ Unexpected status: {result['status']}")
        
        # Small delay between sessions
        time.sleep(1)
    
    logger.info("🏁 Demo completed!")

def cleanup_demo_sessions():
    """Clean up demo sessions"""
    logger.info("🧹 Cleaning up demo sessions...")
    
    redis_client = RedisClient()
    demo_keys = redis_client.redis_client.keys("memory:demo_session_*")
    
    for key in demo_keys:
        redis_client.redis_client.delete(key)
        logger.info(f"🗑️ Deleted: {key}")
    
    logger.info("✅ Cleanup completed")

def main():
    """Main demo function"""
    try:
        demo_auto_summary()
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise
    finally:
        # Ask user if they want to cleanup
        cleanup = input("\n🤔 Do you want to cleanup demo sessions? (y/n): ").lower().strip()
        if cleanup in ['y', 'yes']:
            cleanup_demo_sessions()
        else:
            logger.info("ℹ️ Demo sessions left in Redis for inspection")

if __name__ == "__main__":
    main()
