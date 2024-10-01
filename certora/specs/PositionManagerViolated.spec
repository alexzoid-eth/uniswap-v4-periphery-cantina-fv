import "./PositionManagerValidState.spec";

/// @notice used to signal that an action should use the contract's entire balance of a currency
/// This value is equivalent to 1<<255, i.e. a singular 1 in the most significant bit.
definition CONTRACT_BALANCE() returns uint256 = 0x8000000000000000000000000000000000000000000000000000000000000000;

// When settling with the CONTRACT_BALANCE flag, the action should always use the 
//  contract's entire balance of the specified currency
rule settleUsesFullContractBalance(env e, bytes params) {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerEnv(e);

    // Decode input params
    PoolManager.Currency currency;
    uint256 amount; 
    bool payerIsUser;
    currency, amount, payerIsUser = _HelperCVL.decodeSettleParams(params);

    // Actions.SETTLE
    handleActionSettle(e, params);

    // Contract's balance after successful SETTLE action
    mathint posBalanceAfter = balanceOfCVL(e, currency, _PositionManager);

    // If CONTRACT_BALANCE() flag was set when settling, contract's entire balance MUST be used
    assert(amount == CONTRACT_BALANCE() => posBalanceAfter == 0);
}