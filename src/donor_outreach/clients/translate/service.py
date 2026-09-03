from donor_outreach.clients.aws import get_client

class TranslateClient:

    def  __init__(self, boto_client=None):
        self._client = boto_client if boto_client is not None else get_client("translate")

    def translate_text(self, text: str, src_lang: str, trg_lang: str) -> str:
        response = self._client.translate_text(
            Text=text,
            SourceLanguageCode = src_lang,
            TargetLanguageCode= trg_lang
        )
        return response["TranslatedText"]