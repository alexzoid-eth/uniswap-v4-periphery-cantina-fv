// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;
import {TestERC20} from "@uniswap/v4-core/src/test/TestERC20.sol";

contract TestERC20B is TestERC20 {
    constructor() TestERC20(1000000 * 1e6) {}
}