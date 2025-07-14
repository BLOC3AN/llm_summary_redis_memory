#!/usr/bin/env python3
"""
Scheduler service for automatic Redis summary execution
Runs continuously and checks for auto-summary at specified intervals
"""

import time
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append('/app')

from src.utils.logger import Logger
from src.llms.openai import LLMOpenAI
from src.memory.redis_summaryMemory import SummaryConversation

def main():
    """Main scheduler loop"""
    logger = Logger('scheduler')
    
    # Get configuration from environment
    interval = int(os.getenv('SCHEDULE_INTERVAL', 3600))  # Default: 1 hour
    number_of_summary = int(os.getenv('NUMBER_OF_SUMMARY', 10))  # Default: 10 sessions
    
    logger.info(f"🚀 Redis Summary Scheduler started")
    logger.info(f"⏰ Check interval: {interval} seconds ({interval/60:.1f} minutes)")
    logger.info(f"📊 Summary threshold: {number_of_summary} sessions")
    
    # Initialize LLM and summary conversation
    try:
        llm = LLMOpenAI()
        logger.info("✅ LLM initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize LLM: {e}")
        return
    
    # Main scheduler loop
    while True:
        try:
            logger.info("🔍 Running scheduled auto-summary check...")
            
            # Create summary conversation instance
            summary_conv = SummaryConversation(
                llm=llm, 
                number_of_summary=number_of_summary
            )
            
            # Check and perform auto-summary if needed
            result = summary_conv.check_and_auto_summary()
            
            # Log result based on status
            if result["status"] == "summary_completed":
                logger.info("🎉 Auto-summary completed successfully!")
                logger.info(f"📋 Sessions processed: {result.get('new_sessions_processed', 'N/A')}")
            elif result["status"] == "no_summary_needed":
                logger.info("ℹ️ No auto-summary needed")
                logger.info(f"📈 New sessions: {result.get('new_sessions_count', 0)}/{number_of_summary}")
            elif result["status"] == "error":
                logger.error(f"❌ Auto-summary failed: {result.get('message', 'Unknown error')}")
            else:
                logger.warning(f"⚠️ Unexpected status: {result['status']}")
                
        except Exception as e:
            logger.error(f"❌ Scheduled check failed: {e}")
        
        # Sleep until next check
        logger.info(f"⏰ Next check in {interval} seconds ({interval/60:.1f} minutes)...")
        time.sleep(interval)

if __name__ == "__main__":
    main()
