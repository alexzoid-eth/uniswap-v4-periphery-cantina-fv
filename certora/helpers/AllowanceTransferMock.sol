// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import {IERC20Minimal} from "@uniswap/v4-core/src/interfaces/external/IERC20Minimal.sol";

/// @notice The permit data for a token
struct PermitDetails {
    // ERC20 token address
    address token;
    // the maximum amount allowed to spend
    uint160 amount;
    // timestamp at which a spender's token allowances become invalid
    uint48 expiration;
    // an incrementing value indexed per owner,token,and spender for each signature
    uint48 nonce;
}

/// @notice The permit message signed for a single token allowance
struct PermitSingle {
    // the permit data for a single token alownce
    PermitDetails details;
    // address permissioned on the allowed tokens
    address spender;
    // deadline on the permit signature
    uint256 sigDeadline;
}

/// @notice The permit message signed for multiple token allowances
struct PermitBatch {
    // the permit data for multiple token allowances
    PermitDetails[] details;
    // address permissioned on the allowed tokens
    address spender;
    // deadline on the permit signature
    uint256 sigDeadline;
}

// Adopted from lib/permit2/src/AllowanceTransfer.sol
contract AllowanceTransferMock {

    function permit(address owner, PermitSingle memory permitSingle, bytes calldata signature) external {
        if (owner == address(0)) revert();
    }

    function permit(address owner, PermitBatch memory permitBatch, bytes calldata signature) external {
        if (owner == address(0)) revert();
    }

    function transferFrom(address from, address to, uint160 amount, address token) external {
        IERC20Minimal(token).transferFrom(from, to, amount);
    }
}
