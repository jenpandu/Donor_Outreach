import boto3
from botocore.stub import Stubber

from donor_outreach.clients.translate import TranslateClient


def test_translate_client_translate_text():
    boto_client = boto3.client("translate", region_name="us-east-1")
    stubber = Stubber(boto_client)

    expected_params = {
        "Text": "Hello",
        "SourceLanguageCode": "en",
        "TargetLanguageCode": "es",
    }
    stubber.add_response(
        "translate_text",
        {"TranslatedText": "Hola", "SourceLanguageCode": "en", "TargetLanguageCode": "es"},
        expected_params,
    )
    stubber.activate()

    client = TranslateClient(boto_client=boto_client)
    result = client.translate_text(text="Hello", src_lang="en", trg_lang="es")

    assert result == "Hola"
    stubber.deactivate()