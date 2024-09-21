import "./setup/V4RouterBase.spec";
import "./PoolManagerValidState.spec";

methods {

    // Not needed as _handleAction is no-op and summarizing unlock here would have no effect
    function _V4Router.unlockCallback(bytes data) external returns (bytes) => NONDET DELETE;

    // PoolManager summaries
    
    function _PoolManager.swap(
        PoolManager.PoolKey key, IPoolManager.SwapParams params, bytes hookData
    ) external returns (PoolManager.BalanceDelta) with (env e) 
        => swapCVL(e, key, params, hookData);

    function _PoolManager.sync(PoolManager.Currency currency) external with (env e) 
        => syncCVL(e, currency);

    function _PoolManager.take(PoolManager.Currency currency, address to, uint256 amount) external with (env e) 
        => takeCVL(e, currency, to, amount);

    function _PoolManager.settle() external returns (uint256) with (env e) 
        => settleCVL(e);
}

// Check if there is at least one path to execute an external function without a revert 
use builtin rule sanity filtered { f -> f.contract == currentContract }

// Execute invariants from PoolManagerValidState
use invariant maxProtocolFeeLimit;
use invariant validSqrtPriceX96Range;
