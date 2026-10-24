from src.crypto.hash_chain import HashChain
from src.crypto.merkle_tree import MerkleTree
from src.crypto.signature import generate_key_pair, sign_message
from src.crypto.verifier import verify_integrity


def test_verifier_combines_chain_merkle_and_signature_checks() -> None:
    event = {"message": "service started"}
    chain = HashChain()
    chain.append(event, timestamp="2025-01-01T00:00:00Z")
    tree = MerkleTree([event, {"message": "request handled"}])
    private_key, public_key = generate_key_pair()
    message = tree.root
    signature = sign_message(private_key, message)

    result = verify_integrity(
        chain,
        leaf=event,
        proof=tree.proof(0),
        merkle_root=tree.root,
        public_key=public_key,
        message=message,
        signature=signature,
    )

    assert result == {
        "chain_valid": True,
        "merkle_valid": True,
        "signature_valid": True,
        "valid": True,
    }


def test_verifier_reports_each_failed_check() -> None:
    chain = HashChain()
    chain.append({"message": "original"}, timestamp="2025-01-01T00:00:00Z")
    entries = chain.to_list()
    entries[0]["event"]["message"] = "modified"

    result = verify_integrity(HashChain(entries))

    assert result == {"chain_valid": False, "valid": False}