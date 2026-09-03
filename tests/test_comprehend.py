import boto3
from botocore.stub import Stubber

from donor_outreach.clients.comprehend import ComprehendClient


def test_comprehend_client_detect_language():
    boto_client = boto3.client("comprehend", region_name="us-east-1")
    stubber = Stubber(boto_client)

    text = "Hola, ¿cómo estás?"
    expected_params = {"Text": text}

    stubber.add_response(
        "detect_dominant_language",
        {"Languages": [{"LanguageCode": "es", "Score": 0.98}]},
        expected_params,
    )
    stubber.activate()

    client = ComprehendClient(boto_client=boto_client)
    language_code, confidence = client.detect_language(text)

    assert language_code == "es"
    assert confidence == 0.98

    stubber.deactivate()