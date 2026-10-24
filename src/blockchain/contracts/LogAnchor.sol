// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LogAnchor {
    address public immutable owner;
    mapping(bytes32 => bytes32) public anchors;

    event BatchAnchored(bytes32 indexed batchId, bytes32 merkleRoot, address indexed submitter);

    error NotOwner();
    error EmptyIdentifier();
    error EmptyRoot();
    error AlreadyAnchored(bytes32 batchId);

    constructor() {
        owner = msg.sender;
    }

    function anchorBatch(bytes32 batchId, bytes32 merkleRoot) external {
        if (msg.sender != owner) revert NotOwner();
        if (batchId == bytes32(0)) revert EmptyIdentifier();
        if (merkleRoot == bytes32(0)) revert EmptyRoot();
        if (anchors[batchId] != bytes32(0)) revert AlreadyAnchored(batchId);

        anchors[batchId] = merkleRoot;
        emit BatchAnchored(batchId, merkleRoot, msg.sender);
    }
}