import "./PositionManagerValidState.spec";

/// @notice used to signal that an action should use the contract's entire balance of a currency
/// This value is equivalent to 1<<255, i.e. a singular 1 in the most significant bit.
definition CONTRACT_BALANCE() returns uint256 = 0x8000000000000000000000000000000000000000000000000000000000000000;

// Verifies that when settling with the CONTRACT_BALANCE flag, the action uses the contract's entire balance
rule settleUsesFullContractBalance(env e, bytes params) {

    // Assume PositionManager is in a valid state before the action
    requireValidStatePositionManagerEnv(e);

    // Decode the input parameters for the settle action
    PoolManager.Currency currency;
    uint256 amount; 
    bool payerIsUser;
    currency, amount, payerIsUser = _HelperCVL.decodeSettleParams(params);

    // Record the locker's balance before the action
    mathint lockerBalanceBefore = balanceOfCVL(e, currency, ghostLocker);

    // Execute the settle action
    handleActionSettle(e, params);

    // Record the locker's balance after the action
    mathint lockerBalanceAfter = balanceOfCVL(e, currency, ghostLocker);

    // Check the contract's balance after the settle action
    mathint posBalanceAfter = balanceOfCVL(e, currency, _PositionManager);

    // If CONTRACT_BALANCE flag was set, the contract's entire balance must be used
    assert(amount == CONTRACT_BALANCE() => posBalanceAfter == 0);

    // If CONTRACT_BALANCE flag was set, the locker's balance should remain unchanged
    assert(amount == CONTRACT_BALANCE() => lockerBalanceBefore == lockerBalanceAfter);
}
