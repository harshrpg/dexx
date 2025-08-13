from datetime import datetime
from typing import List, Dict, Optional
import json
import redis
from app.core.singleton import Singleton
from app.core.config import settings


class MessageService(metaclass=Singleton):
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            username=settings.REDIS_UNAME,
            password=settings.REDIS_PWD,
            decode_responses=True,
        )
        self.max_context_messages = 20
        self.context_window = 5

    def save_message(
        self,
        wallet_address: str,
        session_id: str,
        content: str,
        role: str,
        metadata: Optional[Dict] = None,
    ) -> dict:
        message = {
            "content": content,
            "role": role,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "session_id": session_id,
        }

        # Save to session-specific history
        session_key = f"messages:session:{session_id}"
        session_data = self._get_session_data(session_key)
        
        # Update session data
        if not session_data:
            session_data = {
                "wallet_address": wallet_address,
                "session_id": session_id,
                "messages": [],
                "last_updated": datetime.now().isoformat(),
                "context": {
                    "last_token": None,
                    "last_chain": None,
                    "last_contract_address": None,
                    "last_token_name": None,
                    "last_action": None
                }
            }

        # Update context if metadata contains token info
        if metadata and any(key in metadata for key in ["token_symbol", "contract_address", "chain"]):
            session_data["context"].update({
                "last_token": metadata.get("token_symbol"),
                "last_chain": metadata.get("chain"),
                "last_contract_address": metadata.get("contract_address"),
                "last_token_name": metadata.get("token_name"),
                "last_action": metadata.get("action")
            })

        # Add new message
        session_data["messages"].append(message)
        session_data["last_updated"] = datetime.now().isoformat()

        # Maintain max context size
        if len(session_data["messages"]) > self.max_context_messages:
            session_data["messages"] = session_data["messages"][-self.max_context_messages:]

        # Save updated session data
        self.redis.set(session_key, json.dumps(session_data))

        # Also maintain a list of sessions for this wallet
        self.redis.sadd(f"wallet:sessions:{wallet_address}", session_id)

        return message

    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get message history for a specific session"""
        session_data = self._get_session_data(f"messages:session:{session_id}")
        return session_data.get("messages", []) if session_data else []

    def get_session_context(self, session_id: str) -> Dict:
        """Get the current context for a session"""
        session_data = self._get_session_data(f"messages:session:{session_id}")
        return session_data.get("context", {}) if session_data else {}

    def get_wallet_sessions(self, wallet_address: str) -> List[str]:
        """Get all sessions for a wallet"""
        return list(self.redis.smembers(f"wallet:sessions:{wallet_address}"))

    def get_all_wallet_messages(self, wallet_address: str) -> Dict[str, List[Dict]]:
        """Get all messages across all sessions for a wallet"""
        sessions = self.get_wallet_sessions(wallet_address)
        return {
            session_id: self.get_session_history(session_id) for session_id in sessions
        }

    def format_for_chatgpt(self, session_id: str) -> List[Dict[str, str]]:
        """Format messages for ChatGPT context with improved context handling"""
        session_data = self._get_session_data(f"messages:session:{session_id}")
        if not session_data:
            return []

        messages = session_data["messages"]
        context = session_data["context"]
        
        # Create context message if we have token context
        if context.get("last_token"):
            context_message = {
                "role": "system",
                "content": f"Current context: Token {context['last_token']} ({context['last_token_name'] or 'Unknown'}) on {context['last_chain'] or 'unknown chain'}. Contract: {context['last_contract_address'] or 'Not specified'}"
            }
            messages.insert(0, context_message)

        # Format messages for ChatGPT
        formatted_messages = []
        for msg in messages[-self.context_window:]:  # Use context window for immediate context
            formatted_msg = {
                "role": msg["role"],
                "content": msg["content"]
            }
            # Include relevant metadata in content if present
            if msg.get("metadata"):
                metadata_str = self._format_metadata(msg["metadata"])
                if metadata_str:
                    formatted_msg["content"] = f"{msg['content']}\nContext: {metadata_str}"
            formatted_messages.append(formatted_msg)

        return formatted_messages

    def _format_metadata(self, metadata: Dict) -> str:
        """Format metadata into a readable string"""
        parts = []
        if metadata.get("token_symbol"):
            parts.append(f"Token: {metadata['token_symbol']}")
        if metadata.get("chain"):
            parts.append(f"Chain: {metadata['chain']}")
        if metadata.get("action"):
            parts.append(f"Action: {metadata['action']}")
        return ", ".join(parts)

    def _get_session_data(self, key: str) -> Optional[Dict]:
        """Helper method to get session data from Redis"""
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def clear_session_history(self, session_id: str):
        """Clear message history for a specific session"""
        self.redis.delete(f"messages:session:{session_id}")

    def clear_wallet_history(self, wallet_address: str):
        """Clear all message history for a wallet"""
        sessions = self.get_wallet_sessions(wallet_address)
        for session_id in sessions:
            self.clear_session_history(session_id)
        self.redis.delete(f"wallet:sessions:{wallet_address}")
