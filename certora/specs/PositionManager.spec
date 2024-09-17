import "./setup/PositionManagerBase.spec";
import "./PoolManagerValidState.spec";

methods {

    // PoolManager summaries

    function ProtocolFees._fetchProtocolFee(PoolManager.PoolKey memory key) internal returns (uint24)
        => fetchProtocolFeeCVL(key);

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
}

use builtin rule sanity filtered { f -> f.contract == currentContract }