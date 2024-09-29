// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import {PositionManager, PositionInfo, IPoolManager, IAllowanceTransfer} from "src/PositionManager.sol";
import {Currency} from "@uniswap/v4-core/src/types/Currency.sol";
import {PoolKey} from "@uniswap/v4-core/src/types/PoolKey.sol";

contract PositionManagerHarness is PositionManager {

    constructor(IPoolManager _poolManager, IAllowanceTransfer _permit2, uint256 _unsubscribeGasLimit) 
        PositionManager(_poolManager, _permit2, _unsubscribeGasLimit) { }

    function increaseLiquidity(
        uint256 tokenId,
        uint256 liquidity,
        uint128 amount0Max,
        uint128 amount1Max,
        bytes calldata hookData
    ) external payable {
        // uint256 action = Actions.INCREASE_LIQUIDITY;
        _increase(tokenId, liquidity, amount0Max, amount1Max, hookData);               
    }

    function decreaseLiquidity(
        uint256 tokenId,
        uint256 liquidity,
        uint128 amount0Min,
        uint128 amount1Min,
        bytes calldata hookData
    ) external payable {
        // uint256 action = Actions.DECREASE_LIQUIDITY;
        _decrease(tokenId, liquidity, amount0Min, amount1Min, hookData);             
    }

    function mintPosition(
        PoolKey calldata poolKey,
        int24 tickLower,
        int24 tickUpper,
        uint256 liquidity,
        uint128 amount0Max,
        uint128 amount1Max,
        address owner,
        bytes calldata hookData
    )  external payable {
        // uint256 action = Actions.MINT_POSITION;
        _mint(poolKey, tickLower, tickUpper, liquidity, amount0Max, amount1Max, _mapRecipient(owner), hookData);            
    }

    function burnPosition(
        uint256 tokenId,
        uint128 amount0Min,
        uint128 amount1Min,
        bytes calldata hookData
    ) external payable {
        // uint256 action = Actions.BURN_POSITION;
        _burn(tokenId, amount0Min, amount1Min, hookData);
    }

    function settlePair(Currency currency0, Currency currency1) external payable {
        // uint256 action = Actions.SETTLE_PAIR;
        _settlePair(currency0, currency1);
    }

    function takePair(Currency currency0, Currency currency1, address to) external payable {
        // uint256 action = Actions.TAKE_PAIR;
        _takePair(currency0, currency1, to);
    }

    function settle(Currency currency, uint256 amount, bool payerIsUser) external payable {
        // uint256 action = Actions.SETTLE;
        _settle(currency, _mapPayer(payerIsUser), _mapSettleAmount(amount, currency));
    }

    function take(Currency currency, address recipient, uint256 amount) external payable {
        // uint256 action = Actions.TAKE;
         _take(currency, _mapRecipient(recipient), _mapTakeAmount(amount, currency));
    }

    function close(Currency currency) external payable {
        // uint256 action = Actions.CLOSE_CURRENCY;
        _close(currency);
    }

    function clearOrTake(Currency currency, uint256 amountMax) external payable {
        // uint256 action = Actions.CLEAR_OR_TAKE;
        _clearOrTake(currency, amountMax);
    }

    function sweep(Currency currency, address to) external payable {
        // uint256 action = Actions.SWEEP;
        _sweep(currency, _mapRecipient(to));
    }

    function getFullDebt(Currency currency) external view returns (uint256 amount) {
        amount = _getFullDebt(currency);
    }
}