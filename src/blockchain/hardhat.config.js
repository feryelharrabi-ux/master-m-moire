require("@nomicfoundation/hardhat-ethers");

const networks = {};
if (process.env.RPC_URL && process.env.PRIVATE_KEY) {
  networks.sepolia = {
    url: process.env.RPC_URL,
    accounts: [process.env.PRIVATE_KEY],
  };
}

module.exports = {
  solidity: "0.8.20",
  networks,
  paths: {
    sources: "./contracts",
    artifacts: "./artifacts",
  },
};
