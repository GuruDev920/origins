pragma solidity ^0.5.17;

import "../../../Openzeppelin/Initializable.sol";
import "../../Utils/AdminRole.sol";
import "../../../Interfaces/IERC20.sol";
import "../../../Interfaces/IVestingFactory.sol";
import "../../../Interfaces/ILockedFund.sol";

/**
 * @title Vesting Registry Storage Contract.
 *
 * @notice This contract is just the storage required for vesting registry.
 * It is parent of VestingRegistryProxy and VestingRegistryLogic.
 *
 * @dev Use Ownable as a parent to align storage structure for Logic and Proxy contracts.
 * */

contract VestingRegistryStorage is Initializable, AdminRole {
	///@notice the vesting factory contract
	IVestingFactory public vestingFactory;

	///@notice the Locked Fund contract
	ILockedFund public lockedFund;

	///@notice the token contract
	address public token;

	///@notice the staking contract address
	address public staking;

	///@notice fee sharing address (usually Governor Vault)
	address public feeSharing;

	///@notice the vesting owner (e.g. governance timelock address)
	address public vestingOwner;

	enum VestingType {
		TeamVesting, //MultisigVesting
		Vesting //TokenHolderVesting
	}

	///@notice Vesting details
	struct VestingDetail {
		uint256 vestingType;
		uint256 vestingCreationType;
		address vestingAddress;
	}

	///@notice A record of vesting details for a unique id
	///@dev vestings[uid] returns vesting data
	mapping(uint256 => VestingDetail) public vestings;

	///@notice A record of all unique ids for a particular token owner
	///@dev vestingsOf[tokenOwner] returns array of unique ids
	mapping(address => uint256[]) public vestingsOf;

	///@notice A record of all vesting addresses
	///@dev isVesting[address] returns if the address is a vesting address
	mapping(address => bool) public isVesting;
}
