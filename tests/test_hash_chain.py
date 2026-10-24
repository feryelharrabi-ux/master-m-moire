from src.crypto.hash_chain import GENESIS_HASH, HashChain


def test_chain_appends_and_verifies() -> None:
    chain = HashChain()
    first = chain.append({"message": "started"}, timestamp="2025-01-01T00:00:00Z")
    second = chain.append({"message": "finished"}, timestamp="2025-01-01T00:00:01Z")

    assert first.previous_hash == GENESIS_HASH
    assert second.previous_hash == first.hash
    assert chain.verify()
    assert HashChain(chain.to_list()).verify()


def test_chain_detects_event_tampering() -> None:
    chain = HashChain()
    chain.append({"message": "original"}, timestamp="2025-01-01T00:00:00Z")
    entries = chain.to_list()
    entries[0]["event"]["message"] = "changed"

    assert not HashChain(entries).verify()


def test_chain_detects_reordered_or_missing_entries() -> None:
    chain = HashChain()
    for index in range(3):
        chain.append({"index": index}, timestamp=f"2025-01-01T00:00:0{index}Z")

    assert not HashChain([chain.to_list()[1], chain.to_list()[0]]).verify()
    assert not HashChain([chain.to_list()[0], chain.to_list()[2]]).verify()