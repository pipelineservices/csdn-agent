# planner.py
from models.shared import LLMClient


class Planner:
    """
    Planner decides what the user wants (intent classification)
    and returns a simple intent label the orchestrator can route.
    """

    def __init__(self):
        self.llm = LLMClient()

    def classify_intent(self, query: str) -> str:
        """
        Classify the type of question coming from the user.
        Categories:
            - network
            - cloud
            - jira
            - security
            - smalltalk
        """

        system_msg = {
            "role": "system",
            "content": (
                "You are an intent classification model. "
                "Classify the user's request into one of these buckets: "
                "network, cloud, jira, security, or smalltalk. "
                "Respond with only one word."
            ),
        }

        user_msg = {
            "role": "user",
            "content": query
        }

        messages = [system_msg, user_msg]

        # LLMClient.chat() already returns response.content
        raw = self.llm.chat(messages).strip().lower()

        # Safety normalization
        cleaned = raw.split()[0]  # take first word if extra text comes
        return cleaned
