"""Read and verify a batch identifier's root in a deployed LogAnchor contract."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

ARTIFACT_PATH = Path(__file__).parent / "artifacts" / "contracts" / "LogAnchor.sol" / "LogAnchor.json"


def get_anchor(batch_id: str, contract_address: str) -> str:
    try:
        from web3 import Web3
    except ModuleNotFoundError as error:
        raise RuntimeError("Install Python dependencies to verify blockchain anchors.") from error
    rpc_url = os.environ.get("RPC_URL")
    if not rpc_url:
        raise RuntimeError("Set the RPC_URL environment variable.")
    if not ARTIFACT_PATH.is_file():
        raise FileNotFoundError(f"Contract artifact not found: {ARTIFACT_PATH}")
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    if not web3.is_connected():
        raise ConnectionError(f"Could not connect to EVM RPC endpoint {rpc_url!r}.")
    artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    contract = web3.eth.contract(
        address=Web3.to_checksum_address(contract_address), abi=artifact["abi"]
    )
    root = contract.functions.anchors(batch_id).call().hex()
    return root if root.startswith("0x") else "0x" + root


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch_id", help="32-byte 0x-prefixed identifier")
    parser.add_argument("--contract", default=os.environ.get("CONTRACT_ADDRESS"))
    args = parser.parse_args()
    if not args.contract:
        parser.error("Specify --contract or set CONTRACT_ADDRESS.")
    root = get_anchor(args.batch_id, args.contract)
    anchored = int(root, 16) != 0
    print(json.dumps({"batch_id": args.batch_id, "anchored": anchored, "merkle_root": root}, indent=2))
    if not anchored:
        raise SystemExit(1)


if __name__ == "__main__":
    main()