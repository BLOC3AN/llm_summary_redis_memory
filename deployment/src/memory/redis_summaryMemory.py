
from pydantic import BaseModel
from pydantic import Field
from typing import List, Dict, Any
import json
from src.utils.redis_client import RedisClient
from src.utils.logger import Logger

logger = Logger(__name__)
redis_client = RedisClient()
redis_client.debug_redis()
list_keys_memory:list[str] = redis_client.redis_client.keys(pattern="*") #type:ignore

class SummaryConversation(BaseModel):
    llm: Any = Field(...)
    max_token_limit: int = Field(default=150, description="Maximum number of tokens for the summary")
    number_of_summary: int = Field(default=10, description="Number of session keys  to generate")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_conversation(self, **kwargs):
        """
        Get conversation data for the most recent sessions
        Only get sessions that match the memory pattern to avoid including summary data
        """
        # Filter to only get memory sessions (not summary sessions)
        memory_sessions = [key for key in list_keys_memory if key.startswith('memory:')]

        # Get the most recent sessions for summary
        recent_sessions = memory_sessions[-self.number_of_summary:]

        conversation = []
        for session_id in recent_sessions:
            session_data = redis_client.get(session_id)
            if session_data:
                conversation.append(session_data)

        return conversation
    
    def get_output_schema(self, schema_path: str):
        import json
        with open(schema_path, "r") as f:
            schema = json.load(f)
        return schema['output_schema']
    
    def create_prompt(self, schema):
        conversation = [self.get_conversation()]
        """Create a conversation prompt template with memory placeholder."""
        with open("src/prompts/prompt_summary.md", "r", encoding="utf-8") as f:
            system_prompt = f.read()
        
        prompt = f"""
            {system_prompt}
            The conversation:
            {conversation}
            Follow output by output_schema JSON schema:
            {schema}
    """
        return prompt
    
    def summary_llm(self, **kwargs):
        schema = self.get_output_schema("src/MCP/schema_summary.json")
        prompt = self.create_prompt(schema)
        response = self.llm.invoke(prompt).model_dump()['content']
        response = response.strip().removeprefix("```json\n").removesuffix("```")
        
        return json.loads(response)

    def get_summary_metadata(self):
        """
        Get metadata about the last summary operation

        Returns:
            dict: Metadata containing last_summary_session_id and total_sessions_at_summary
        """
        metadata = redis_client.get("summary_metadata")
        if metadata and isinstance(metadata, str):
            return json.loads(metadata)
        return {"last_summary_session_id": None, "total_sessions_at_summary": 0}

    def save_summary_metadata(self, last_session_id, total_sessions):
        """
        Save metadata about the summary operation

        Args:
            last_session_id: The last session ID that was included in summary
            total_sessions: Total number of sessions at the time of summary
        """
        from datetime import datetime

        metadata = {
            "last_summary_session_id": last_session_id,
            "total_sessions_at_summary": total_sessions,
            "timestamp": datetime.now().isoformat()
        }
        result = redis_client.set("summary_metadata", json.dumps(metadata))
        if result:
            logger.info(f"Summary metadata saved: {metadata}")
        return result

    def count_new_sessions(self):
        """
        Count the number of new session IDs since the last summary
        Only count memory sessions, not summary sessions

        Returns:
            int: Number of new sessions since last summary
        """
        metadata = self.get_summary_metadata()

        # Only count memory sessions
        memory_sessions = [key for key in list_keys_memory if key.startswith('memory:')]
        current_total_sessions = len(memory_sessions)
        last_total_sessions = metadata.get("total_sessions_at_summary", 0)

        new_sessions_count = current_total_sessions - last_total_sessions
        logger.info(f"Current memory sessions: {current_total_sessions}, Last summary at: {last_total_sessions}, New sessions: {new_sessions_count}")

        return new_sessions_count

    def should_auto_summary(self):
        """
        Check if auto summary should be triggered based on number_of_summary threshold

        Returns:
            bool: True if auto summary should be triggered
        """
        new_sessions = self.count_new_sessions()
        should_summary = new_sessions >= self.number_of_summary

        logger.info(f"New sessions: {new_sessions}, Threshold: {self.number_of_summary}, Should summary: {should_summary}")
        return should_summary

    def save_summary(self, summary, collection="summary"):
        """
        Save summary to Redis with specified collection

        Args:
            summary: The summary data to save
            collection: The collection name (default: "summary")
        """
        # Get memory sessions only
        memory_sessions = [key for key in list_keys_memory if key.startswith('memory:')]

        # Get the latest session ID from memory sessions
        if memory_sessions:
            latest_session_id = memory_sessions[-self.number_of_summary:][-1]
        else:
            logger.error("No memory sessions found")
            return False

        # Convert summary to JSON if it's not already a string
        if not isinstance(summary, str):
            summary = json.dumps(summary)

        # Save to Redis with collection:{session_id} format
        result = redis_client.set(f"{collection}:{latest_session_id}", summary)

        if result:
            logger.info(f"Summary saved successfully to {collection}:{latest_session_id}")
            # Update metadata after successful summary save - only count memory sessions
            self.save_summary_metadata(latest_session_id, len(memory_sessions))
        else:
            logger.error(f"Failed to save summary to {collection}:{latest_session_id}")

        return result

    def auto_summary(self, collection="summary"):
        """
        Automatically perform summary if conditions are met

        Args:
            collection: The collection name for saving summary (default: "summary")

        Returns:
            dict: Result containing summary data if performed, or status message
        """
        if not self.should_auto_summary():
            return {
                "status": "no_summary_needed",
                "message": f"Not enough new sessions. Need {self.number_of_summary} new sessions to trigger auto-summary.",
                "new_sessions_count": self.count_new_sessions()
            }

        try:
            logger.info("🔄 Auto-summary triggered - performing summary...")

            # Perform the summary
            summary_data = self.summary_llm()

            # Save the summary
            save_result = self.save_summary(summary_data, collection)

            if save_result:
                logger.info("✅ Auto-summary completed successfully")
                return {
                    "status": "summary_completed",
                    "message": "Auto-summary performed successfully",
                    "summary_data": summary_data,
                    "new_sessions_processed": self.number_of_summary
                }
            else:
                logger.error("❌ Failed to save auto-summary")
                return {
                    "status": "save_failed",
                    "message": "Summary generated but failed to save",
                    "summary_data": summary_data
                }

        except Exception as e:
            logger.error(f"❌ Auto-summary failed: {e}")
            return {
                "status": "error",
                "message": f"Auto-summary failed: {str(e)}",
                "error": str(e)
            }

    def check_and_auto_summary(self, collection="summary"):
        """
        Check if auto-summary should be performed and execute if needed
        This is the main method to call for auto-summary functionality

        Args:
            collection: The collection name for saving summary (default: "summary")

        Returns:
            dict: Result of the auto-summary check and execution
        """
        logger.info("🔍 Checking if auto-summary should be triggered...")

        # Refresh the keys list to get latest session data
        global list_keys_memory
        if redis_client.redis_client:
            list_keys_memory = list(redis_client.redis_client.keys(pattern="*"))  # type: ignore
        else:
            logger.error("Redis client not available")
            return {"status": "error", "message": "Redis client not available"}

        return self.auto_summary(collection)
