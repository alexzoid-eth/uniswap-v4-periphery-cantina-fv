// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import {Currency} from "@uniswap/v4-core/src/types/Currency.sol";
import {BalanceDeltaLibrary, BalanceDelta} from "@uniswap/v4-core/src/types/BalanceDelta.sol";
import {PoolKey} from "@uniswap/v4-core/src/types/PoolKey.sol";
import {PoolId} from "@uniswap/v4-core/src/types/PoolId.sol";
import {BalanceDelta} from "@uniswap/v4-core/src/types/BalanceDelta.sol";
import {IHooks} from "@uniswap/v4-core/src/interfaces/IHooks.sol";
import {PositionInfoLibrary, PositionInfo} from "src/libraries/PositionInfoLibrary.sol";
import {Slot0, Slot0Library} from "@uniswap/v4-core/src/types/Slot0.sol";
import {CalldataDecoder} from "src/libraries/CalldataDecoder.sol";

contract HelperCVL {
    
    using CalldataDecoder for bytes;

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

    // If the upper 12 bytes are non-zero, they will be zero-ed out
    // Therefore, fromId() and toId() are not inverses of each other
    function fromId(uint256 id) external pure returns (Currency currency) {
        currency = Currency.wrap(address(uint160(id)));
    }

    function assertOnFailure(bool success) external {
        require(success);
    }

    function poolId(PositionInfo info) external pure returns (bytes25 _poolId) {
        _poolId = PositionInfoLibrary.poolId(info);
    }

    function tickLower(PositionInfo info) external pure returns (int24 _tickLower) {
        _tickLower = PositionInfoLibrary.tickLower(info);
    }

    function tickUpper(PositionInfo info) external pure returns (int24 _tickUpper) {
        _tickUpper = PositionInfoLibrary.tickUpper(info);
    }

    function hasSubscriber(PositionInfo info) external pure returns (bool _hasSubscriber) {
        _hasSubscriber = PositionInfoLibrary.hasSubscriber(info);
    }

    function slot0SqrtPriceX96(Slot0 _packed) external pure returns (uint160 _sqrtPriceX96) {
        _sqrtPriceX96 = Slot0Library.sqrtPriceX96(_packed);
    }

    function slot0Tick(Slot0 _packed) external pure returns (int24 _tick) {
        _tick = Slot0Library.tick(_packed);
    }

    function castFromBytes32ToBytes25(bytes32 val) external pure returns (bytes25 ret) {
        ret = bytes25(val);
    }

    function decodeSettleParams(bytes calldata params) external pure returns (Currency currency, uint256 amount, bool payerIsUser) {
        (currency, amount, payerIsUser) = params.decodeCurrencyUint256AndBool();
    }
}