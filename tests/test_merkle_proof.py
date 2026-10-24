import pytest

from src.crypto.merkle_tree import MerkleTree, verify_proof


@pytest.mark.parametrize("leaf_count", [1, 2, 3, 5, 8])
def test_proofs_verify_for_odd_and_even_tree_sizes(leaf_count: int) -> None:
    leaves = [{"id": index} for index in range(leaf_count)]
    tree = MerkleTree(leaves)

    for index, leaf in enumerate(leaves):
        assert verify_proof(leaf, tree.proof(index), tree.root)


def test_proof_rejects_changed_leaf_and_root() -> None:
    tree = MerkleTree(["alpha", "beta", "gamma"])
    proof = tree.proof(1)

    assert not verify_proof("altered", proof, tree.root)
    assert not verify_proof("beta", proof, "0" * 64)


def test_empty_tree_and_out_of_range_proof_are_rejected() -> None:
    with pytest.raises(ValueError):
        MerkleTree([])
    tree = MerkleTree(["only"])
    with pytest.raises(IndexError):
        tree.proof(1)