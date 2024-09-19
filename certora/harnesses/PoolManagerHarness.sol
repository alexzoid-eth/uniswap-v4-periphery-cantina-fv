// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.26;

import {PoolManager} from "@uniswap/v4-core/src/PoolManager.sol";
import {PoolKey} from "@uniswap/v4-core/src/types/PoolKey.sol";
import {BalanceDelta} from "@uniswap/v4-core/src/types/BalanceDelta.sol";

contract PoolManagerHarness is PoolManager {

    constructor() PoolManager() {}

    function accountPoolBalanceDeltaHarness(PoolKey memory key, BalanceDelta delta, address target) external {
        _accountDelta(key.currency0, delta.amount0(), target);
        _accountDelta(key.currency1, delta.amount1(), target);
    }
}