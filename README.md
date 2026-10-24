# Log Integrity AI & Blockchain

A research prototype for parsing log lines, protecting event batches with a
SHA-256 hash chain and Merkle tree, simulating log tampering, and evaluating
simple anomaly-detection models. Blockchain anchoring is optional and requires
an EVM network.

## Requirements

- Python 3.10 or newer
- Node.js 18 or newer only for the optional Solidity deployment
- Optional: install the packages in `src/blockchain/package.json` and configure
  an EVM RPC endpoint and private key to deploy or verify an anchor

Install Python dependencies from this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the tests:

```powershell
python -m pytest
```

## Input data

Put one log line per row in `data/raw/`. The parser supports common timestamp,
severity, component, and message patterns; unrecognized lines are retained as
messages. Parsed events are JSON Lines. A small example:

```powershell
python -m src.parsing.drain_parser data/raw/example.log --output data/parsed/events.jsonl
```

Create grouped windows and train a baseline:

```powershell
python -m src.parsing.sequence_builder data/parsed/events.jsonl --output data/parsed/sequences.jsonl
python -m src.ai.train_baselines data/parsed/events.jsonl --output data/parsed/baseline_metrics.json
```

The baseline trainer expects event objects to contain a binary `label` (`0` for
normal and `1` for tampered). The attack helpers label injected or modified
records, but labels for deleted or reordered events must be assigned for the
chosen evaluation task. Do not interpret results from an unlabelled data set as
model validation.

## Integrity and attack demonstrations

`src.crypto.hash_chain.HashChain` and `src.crypto.merkle_tree.MerkleTree` provide
the local integrity primitives. `src.crypto.signature` uses Ed25519 keys from
the `cryptography` package. Attack modules only mutate in-memory demo events;
they do not access external systems or files unless a caller explicitly saves
the returned data.

Run the cryptographic timing demonstration:

```powershell
python -m src.experiments.run_crypto_eval
```

## Optional EVM anchoring

From `src/blockchain/`, install dependencies and compile the contract:

```powershell
npm install
npx hardhat compile
```

Set `RPC_URL` and `PRIVATE_KEY` in the environment, then deploy:

```powershell
npx hardhat run deploy.js --network <network-name>
```

Copy the resulting address to `CONTRACT_ADDRESS`. Prepare an event JSONL file,
then anchor its Merkle root (the submitting key must be the contract deployer):

```powershell
python -m src.blockchain.anchor_batch data/parsed/events.jsonl --contract $env:CONTRACT_ADDRESS
python -m src.blockchain.verify_anchor <batch-id> --contract $env:CONTRACT_ADDRESS
```

The contract stores a batch identifier and root only. It does not store log
contents, and an on-chain root proves only that a value was anchored; it does
not establish that the original logs were truthful.

## Configuration and limitations

`config.yaml` contains example paths and model settings. The parser is a
lightweight Drain-style template normalizer, not the full Drain3 clustering
implementation. The LSTM script is optional and requires TensorFlow. The
experiment scripts are reproducible local demonstrations, not production
benchmarks. Keep private signing keys and RPC credentials out of source
control.
