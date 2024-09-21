import "./setup/PoolManagerBase.spec";
import "./PoolManagerValidState.spec";

methods {

    // External functions
    //  - assume valid pool key inside all external functions except initialize()
    //  - assume currency can be address(0) - native, ERC20A, ERC20B or ERC20C
    //  - assume all pools are NATIVE/ERC20B or ERC20A/ERC20B
    //  - assume hookData length is zero as we don't need 

    function _PoolManager.modifyLiquidity(
        PoolManager.PoolKey key, IPoolManager.ModifyLiquidityParams params, bytes hookData
    ) external returns (PoolManager.BalanceDelta, PoolManager.BalanceDelta) with (env e) 
        => modifyLiquidityCLV(e, key, params, hookData);
    
    function _PoolManager.swap(
        PoolManager.PoolKey key, IPoolManager.SwapParams params, bytes hookData
    ) external returns (PoolManager.BalanceDelta) with (env e) 
        => swapCVL(e, key, params, hookData);

    function _PoolManager.donate(
        PoolManager.PoolKey key, uint256 amount0, uint256 amount1, bytes hookData
    ) external returns (PoolManager.BalanceDelta) with (env e) 
        => donateCVL(e, key, amount0, amount1, hookData);

    function _PoolManager.sync(PoolManager.Currency currency) external with (env e) 
        => syncCVL(e, currency);

    function _PoolManager.take(PoolManager.Currency currency, address to, uint256 amount) external with (env e) 
        => takeCVL(e, currency, to, amount);

    function _PoolManager.settle() external returns (uint256) with (env e) 
        => settleCVL(e);

    function _PoolManager.settleFor(address recipient) external returns (uint256) with (env e) 
        => settleForCVL(e, recipient);

    function _PoolManager.clear(PoolManager.Currency currency, uint256 amount) external with (env e) 
        => clearCVL(e, currency, amount);

    function _PoolManager.mint(address to, uint256 id, uint256 amount) external with (env e) 
        => mintCVL(e, to, id, amount);

    function _PoolManager.burn(address from, uint256 id, uint256 amount) external with (env e) 
        => burnCVL(e, from, id, amount);

    function _PoolManager.updateDynamicLPFee(PoolManager.PoolKey key, uint24 newDynamicLPFee) external with (env e) 
        => updateDynamicLPFeeCVL(e, key, newDynamicLPFee);

    function _PoolManager.setProtocolFee(PoolManager.PoolKey key, uint24 newProtocolFee) external with (env e) 
        => setProtocolFeeCVL(e, key, newProtocolFee);

    function _PoolManager.collectProtocolFees(
        address recipient, PoolManager.Currency currency, uint256 amount
    ) external returns (uint256) with (env e) => collectProtocolFeesCVL(e, recipient, currency, amount);

    // unlock() not needed as _handleAction is no-op and summarizing unlock here would have no effect
    function _PoolManager.unlock(bytes data) external returns (bytes) => NONDET DELETE;

    // setProtocolFeeController() not needed as protocol fee controller summarized as CVL mapping
    function _PoolManager.setProtocolFeeController(address controller) external => NONDET DELETE;
}

// PoolManagerValidState
use invariant maxProtocolFeeLimit;
use invariant validSqrtPriceX96Range;
