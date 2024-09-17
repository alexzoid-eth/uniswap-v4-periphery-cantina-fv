// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import {V4Router} from "src/V4Router.sol";
import {ReentrancyLock} from "src/base/ReentrancyLock.sol";
import {IV4Router} from "src/interfaces/IV4Router.sol";
import {ERC20} from "solmate/src/tokens/ERC20.sol";
import {SafeTransferLib} from "solmate/src/utils/SafeTransferLib.sol";
import {PositionConfig} from "src/libraries/PositionConfig.sol";
import {IPoolManager} from "@uniswap/v4-core/src/interfaces/IPoolManager.sol";
import {Currency, CurrencyLibrary} from "@uniswap/v4-core/src/types/Currency.sol";
import {BipsLibrary} from "@uniswap/v4-core/src/libraries/BipsLibrary.sol";
import {IAllowanceTransfer} from "permit2/src/interfaces/IAllowanceTransfer.sol";

contract V4RouterHarness is V4Router, ReentrancyLock {
    using CurrencyLibrary for Currency;
    using SafeTransferLib for ERC20;
    using BipsLibrary for uint256;

    constructor(IPoolManager _poolManager) V4Router(_poolManager) {}

    function swapExactIn(IV4Router.ExactInputParams calldata params) external payable isNotLocked {
        // uint256 action = Actions.SWAP_EXACT_IN;
        _swapExactInput(params);
    }

    function swapExactInSingle(IV4Router.ExactInputSingleParams calldata params) external payable isNotLocked {
        // uint256 action = Actions.SWAP_EXACT_IN_SINGLE;
        _swapExactInputSingle(params);
    }

    function swapExactOut(IV4Router.ExactOutputParams calldata params) external payable isNotLocked {
        // uint256 action = Actions.SWAP_EXACT_OUT;
        _swapExactOutput(params);
    }

    function swapExactOutSingle(IV4Router.ExactOutputSingleParams calldata params) external payable isNotLocked {
        // uint256 action = Actions.SWAP_EXACT_OUT_SINGLE;
        _swapExactOutputSingle(params);
    }

    function settleTakePair(Currency settleCurrency, Currency takeCurrency) external payable isNotLocked {
        // uint256 action = Actions.SETTLE_TAKE_PAIR;
        _settle(settleCurrency, msgSender(), _getFullDebt(settleCurrency));
        _take(takeCurrency, msgSender(), _getFullCredit(takeCurrency));
    }

    function settleAll(Currency currency, uint256 maxAmount) external payable isNotLocked {
        // uint256 action = Actions.SETTLE_ALL;
        uint256 amount = _getFullDebt(currency);
        if (amount > maxAmount) revert V4TooMuchRequested(maxAmount, amount);
        _settle(currency, msgSender(), amount);
    }

    function takeAll(Currency currency, uint256 minAmount) external payable isNotLocked {
        // uint256 action = Actions.TAKE_ALL;
        uint256 amount = _getFullCredit(currency);
        if (amount < minAmount) revert V4TooLittleReceived(minAmount, amount);
        _take(currency, msgSender(), amount);
    }

    function settle(Currency currency, uint256 amount, bool payerIsUser) external payable isNotLocked {
        // uint256 action = Actions.SETTLE;
        _settle(currency, _mapPayer(payerIsUser), _mapSettleAmount(amount, currency));
    }

    function take(Currency currency, address recipient, uint256 amount) external payable isNotLocked {
        // uint256 action = Actions.TAKE;
        _take(currency, _mapRecipient(recipient), _mapTakeAmount(amount, currency));
    }

    function takePortion(Currency currency, address recipient, uint256 bips) external payable isNotLocked {
        // uint256 action = Actions.TAKE_PORTION;
        _take(currency, _mapRecipient(recipient), _getFullCredit(currency).calculatePortion(bips));
    }

    // Override from DeltaResolver.sol
    function _pay(Currency currency, address payer, uint256 amount) internal override {
        if (payer == address(this)) {
            currency.transfer(address(poolManager), amount);
        } else {
            ERC20(Currency.unwrap(currency)).transferFrom(payer, address(poolManager), amount);
        }
    }

    // Override from BaseActionsRouter.sol
    function msgSender() public view override returns (address sender) {
        sender = _getLocker();
    }
}