// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import {Currency} from "@uniswap/v4-core/src/types/Currency.sol";
import {BalanceDeltaLibrary, BalanceDelta} from "@uniswap/v4-core/src/types/BalanceDelta.sol";
import {PoolKey} from "@uniswap/v4-core/src/types/PoolKey.sol";
import {PoolId} from "@uniswap/v4-core/src/types/PoolId.sol";
import {BalanceDelta} from "@uniswap/v4-core/src/types/BalanceDelta.sol";
import {IHooks} from "@uniswap/v4-core/src/interfaces/IHooks.sol";

contract HelperCVL {
    
    function wrapToPoolId(bytes32 _id) external pure returns (PoolId) {
        return PoolId.wrap(_id);
    }

    function fromCurrency(Currency currency) external pure returns (address) {
        return Currency.unwrap(currency);
    }

    function toCurrency(address token) external pure returns (Currency) {
        return Currency.wrap(token);
    }

    function amount0(BalanceDelta balanceDelta) external pure returns (int128) {
        return BalanceDeltaLibrary.amount0(balanceDelta);
    }

    function amount1(BalanceDelta balanceDelta) external pure returns (int128) {
        return BalanceDeltaLibrary.amount1(balanceDelta);
    }

    function poolKeyToId(PoolKey memory poolKey) external pure returns (bytes32) {
        return keccak256(abi.encode(poolKey));
    }

    function poolKeyVariablesToId(
        Currency currency0,
        Currency currency1,
        uint24 fee,
        int24 tickSpacing,
        IHooks hooks
    ) public pure returns (bytes32) {
        PoolKey memory poolKey = PoolKey({
            currency0: currency0,
            currency1: currency1,
            fee: fee,
            tickSpacing: tickSpacing,
            hooks: hooks
        });
        return keccak256(abi.encode(poolKey));
    }

    function poolKeyVariablesToShortId(
        Currency currency0,
        Currency currency1,
        uint24 fee,
        int24 tickSpacing,
        IHooks hooks
    ) external pure returns (bytes25) {
        return bytes25(uint200(uint256(poolKeyVariablesToId(currency0, currency1, fee, tickSpacing, hooks))));
    }
    
    function positionKey(address owner, int24 tickLower, int24 tickUpper, bytes32 salt) external pure returns (bytes32) {
        return keccak256(abi.encodePacked(owner, tickLower, tickUpper, salt));
    }

    // If the upper 12 bytes are non-zero, they will be zero-ed out
    // Therefore, fromId() and toId() are not inverses of each other
    function fromId(uint256 id) external pure returns (Currency) {
        return Currency.wrap(address(uint160(id)));
    }

    function transferEther(address payable to, uint256 amount) external {
        (bool success, ) = to.call{value: amount}(""); 
        require(success);
    }

    function assertOnFailure(bool success) external {
        require(success);
    }
}