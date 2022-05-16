from app.crypto import base64_decode
from app.message_processor import MessageProcessor

processor = MessageProcessor()


def test_encryption_without_key():
    message = b"Encrypt me"
    processor.shared_secret = None
    token = processor.process_outbound(message=message)
    assert token == message


def test_encryption_with_no_associated_data():
    processor.shared_secret = "My super secret"
    token = processor.process_outbound(message="Encrypt me")
    # print(token)
    assert token is not None


def test_encryption_with_associated_data():
    associated_data = b"jdoe"
    processor.shared_secret = "My super secret"
    token = processor.process_outbound(
        message="Encrypt me", associated_data=associated_data
    )
    # print(token)
    assert token is not None
    associated_data_from_token = base64_decode(token.split(".")[0])
    assert associated_data_from_token == associated_data
