"""Anchor a JSONL event batch's Merkle root in a deployed LogAnchor contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from src.crypto.hash_chain import canonical_json
from src.crypto.merkle_tree import MerkleTree

ARTIFACT_PATH = Path(__file__).parent / "artifacts" / "contracts" / "LogAnchor.sol" / "LogAnchor.json"


def load_events(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as stream:
        events = [json.loads(line) for line in stream if line.strip()]
    if not events:
        raise ValueError("Cannot anchor an empty event batch.")
    return events


def anchor_batch(path: Path, contract_address: str) -> tuple[str, str]:
    try:
        from web3 import Web3
    except ModuleNotFoundError as error:
        raise RuntimeError("Install Python dependencies to use blockchain anchoring.") from error
    rpc_url = os.environ.get("RPC_URL")
    private_key = os.environ.get("PRIVATE_KEY")
    if not rpc_url or not private_key:
        raise RuntimeError("Set both RPC_URL and PRIVATE_KEY environment variables.")
    if not ARTIFACT_PATH.is_file():
        raise FileNotFoundError(f"Contract artifact not found: {ARTIFACT_PATH}")

    events = load_events(path)
    root = MerkleTree(events).root
    batch_digest = hashlib.sha256(
        canonical_json(events).encode("utf-8")
    ).hexdigest()
    batch_id = "0x" + batch_digest
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    if not web3.is_connected():
        raise ConnectionError(f"Could not connect to EVM RPC endpoint {rpc_url!r}.")
    account = web3.eth.account.from_key(private_key)
    artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    contract = web3.eth.contract(
        address=Web3.to_checksum_address(contract_address), abi=artifact["abi"]
    )
    transaction = contract.functions.anchorBatch(batch_id, "0x" + root).build_transaction(
        {
            "from": account.address,
            "nonce": web3.eth.get_transaction_count(account.address),
            "chainId": web3.eth.chain_id,
            "gas": 150_000,
            "gasPrice": web3.eth.gas_price,
        }
    )
    signed = account.sign_transaction(transaction)
    raw_transaction = getattr(signed, "raw_transaction", None)
    if raw_transaction is None:
        raw_transaction = signed.rawTransaction
    tx_hash = web3.eth.send_raw_transaction(raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status != 1:
        raise RuntimeError(f"Anchor transaction failed: {tx_hash.hex()}")
    return batch_id, tx_hash.hex()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON Lines event batch")
    parser.add_argument("--contract", default=os.environ.get("CONTRACT_ADDRESS"))
    args = parser.parse_args()
    if not args.contract:
        parser.error("Specify --contract or set CONTRACT_ADDRESS.")
    batch_id, tx_hash = anchor_batch(args.input, args.contract)
    print(json.dumps({"batch_id": batch_id, "transaction_hash": tx_hash}, indent=2))


if __name__ == "__main__":
    main()