import "./setup/PositionManagerBase.spec";
import "./PoolManagerValidState.spec";

methods {

    // Not needed as _handleAction is no-op and summarizing unlock here would have no effect
    function _PositionManager.modifyLiquidities(bytes unlockData, uint256 deadline) external => NONDET DELETE;
    function _PositionManager.modifyLiquiditiesWithoutUnlock(bytes actions, bytes[] params) external => NONDET DELETE;
    function _PositionManager.unlockCallback(bytes data) external returns (bytes)  => NONDET DELETE;
    
    // External multicall() removed
    function _PositionManager.multicall(bytes[] data) external returns (bytes[]) => NONDET DELETE;

    // Removed due prover warnings
    function _PositionManager.name() external returns (string) => NONDET DELETE;
    function _PositionManager.symbol() external returns (string) => NONDET DELETE;
    function _PositionManager.DOMAIN_SEPARATOR() external returns (bytes32) => CONSTANT DELETE;

    // PoolManager summaries

    function _PoolManager.initialize(
        PoolManager.PoolKey key, uint160 sqrtPriceX96, bytes hookData
        ) external returns (int24) with (env e) 
        => initializeCVL(e, key, sqrtPriceX96, hookData);

    function _PoolManager.modifyLiquidity(
        PoolManager.PoolKey key, IPoolManager.ModifyLiquidityParams params, bytes hookData
    ) external returns (PoolManager.BalanceDelta, PoolManager.BalanceDelta) with (env e) 
        => modifyLiquidityCLV(e, key, params, hookData);

    function _PoolManager.clear(PoolManager.Currency currency, uint256 amount) external with (env e) 
        => clearCVL(e, currency, amount);

    function _PoolManager.sync(PoolManager.Currency currency) external with (env e) 
        => syncCVL(e, currency);

    function _PoolManager.take(PoolManager.Currency currency, address to, uint256 amount) external with (env e) 
        => takeCVL(e, currency, to, amount);

    function _PoolManager.settle() external returns (uint256) with (env e) 
        => settleCVL(e);

    // HelperCVL
    function _.calculatePositionKey(
        address owner, int24 tickLower, int24 tickUpper, bytes32 salt
    ) internal => calculatePositionKeyCVL(owner, tickLower, tickUpper, salt) expect bytes32 ALL;
}

use builtin rule sanity filtered { f -> f.contract == currentContract }