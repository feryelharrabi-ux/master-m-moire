const hre = require("hardhat");

async function main() {
  const artifact = await hre.artifacts.readArtifact("LogAnchor");
  const [deployer] = await hre.ethers.getSigners();
  const factory = new hre.ethers.ContractFactory(
    artifact.abi,
    artifact.bytecode,
    deployer
  );
  const contract = await factory.deploy();
  await contract.waitForDeployment();
  console.log(`LogAnchor deployed to ${await contract.getAddress()}`);
  console.log(`Owner: ${await contract.owner()}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});