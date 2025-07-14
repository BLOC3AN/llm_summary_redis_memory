import os
from src.utils.redis_client import RedisClient
from src.utils.logger import Logger
logger = Logger(__name__)
from dotenv import load_dotenv
load_dotenv()

from src.llms.openai import LLMOpenAI
llm = LLMOpenAI()
from src.memory.redis_summaryMemory import SummaryConversation

if __name__ == "__main__":
    # Initialize SummaryConversation with auto-summary capability
    summary_conversation = SummaryConversation(
        llm=llm,
        number_of_summary=10  # Auto-summary will trigger after every 10 new sessions
    )

    # Check and perform auto-summary if needed
    logger.info("🚀 Starting auto-summary check...")
    result = summary_conversation.check_and_auto_summary()

    # Log the result
    logger.info(f"Auto-summary result: {result}")

    # Print detailed information based on result status
    if result["status"] == "summary_completed":
        logger.info("✅ Auto-summary was performed successfully!")
        logger.info(f"📊 Summary data: {result.get('summary_data', {})}")
    elif result["status"] == "no_summary_needed":
        logger.info("ℹ️ No auto-summary needed at this time")
        logger.info(f"📈 New sessions count: {result.get('new_sessions_count', 0)}")
    elif result["status"] == "error":
        logger.error(f"❌ Auto-summary failed: {result.get('message', 'Unknown error')}")
    else:
        logger.warning(f"⚠️ Unexpected status: {result['status']}")

    logger.info("🏁 Auto-summary check completed")