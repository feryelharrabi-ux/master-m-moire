from src.crypto.signature import generate_key_pair, sign_message, verify_signature


def test_ed25519_signature_verifies_and_detects_changes() -> None:
    private_key, public_key = generate_key_pair()
    signature = sign_message(private_key, "batch-root")

    assert verify_signature(public_key, "batch-root", signature)
    assert not verify_signature(public_key, "changed-root", signature)
    assert not verify_signature(public_key, "batch-root", "not-base64!")