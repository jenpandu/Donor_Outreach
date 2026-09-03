from donor_outreach.clients.aws import get_client


class ComprehendClient:
    
    def __init__(self, boto_client=None):
        self._client = boto_client if boto_client is not None else get_client("comprehend")

    def detect_language(self, text: str) -> tuple[str, float]:
        """
            Detect the dominant language of the given text.

            Returns (language_code, confidence_score) for the top-scoring
            detected language — callers decide what to do with low confidence.
        """
        response = self._client.detect_dominant_language(Text=text)
        top_language = response["Languages"][0]
        return top_language["LanguageCode"], top_language["Score"]