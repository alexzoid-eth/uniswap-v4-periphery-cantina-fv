// Support hooks testing

// @todo use CVL implementation of MockHooks

// Disabled in optimisation purpose. To enable:
//  - add file "lib/v4-core/src/test/MockHooks.sol" into conf
//  - import this file in PoolManagerBase.spec
//  - remove _PoolManager.callHook summarisation in PoolManagerBase.spec

using MockHooks as _MockHooks;

methods {
    
    function _.beforeInitialize(
        address sender, PoolManager.PoolKey key, uint160 sqrtPriceX96, bytes hookData
    ) external with (env e) => beforeInitializeCVL(e, sender, key, sqrtPriceX96, hookData) expect bytes4;
    
    function _.afterInitialize(
        address sender, PoolManager.PoolKey key, uint160 sqrtPriceX96, int24 tick, bytes hookData
    ) external with (env e) => afterInitializeCVL(e, sender, key, sqrtPriceX96, tick, hookData) expect bytes4;
    
    function _.beforeAddLiquidity(
        address sender, PoolManager.PoolKey key, IPoolManager.ModifyLiquidityParams params, bytes hookData
    ) external with (env e) => beforeAddLiquidityCVL(e, sender, key, params, hookData) expect bytes4;
    
    function _.afterAddLiquidity(
        address sender, 
        PoolManager.PoolKey key, 
        IPoolManager.ModifyLiquidityParams params, 
        PoolManager.BalanceDelta delta, 
        PoolManager.BalanceDelta feesAccrued, 
        bytes hookData
    ) external with (env e) => afterAddLiquidityCVL(
        e, sender, key, params, delta, feesAccrued, hookData) expect (bytes4, PoolManager.BalanceDelta
    );
    
    function _.beforeRemoveLiquidity(
        address sender, PoolManager.PoolKey key, IPoolManager.ModifyLiquidityParams params, bytes hookData
    ) external with (env e) => beforeRemoveLiquidityCVL(e, sender, key, params, hookData) expect bytes4;
    
    function _.afterRemoveLiquidity(
        address sender, 
        PoolManager.PoolKey key, 
        IPoolManager.ModifyLiquidityParams params, 
        PoolManager.BalanceDelta delta, 
        PoolManager.BalanceDelta feesAccrued, 
        bytes hookData
    ) external with (env e) => afterRemoveLiquidityCVL(
        e, sender, key, params, delta, feesAccrued, hookData
    ) expect (bytes4, PoolManager.BalanceDelta);
    
    function _.beforeSwap(
        address sender, PoolManager.PoolKey key, IPoolManager.SwapParams params, bytes hookData
    ) external with (env e) => beforeSwapCVL(
        e, sender, key, params, hookData
    ) expect (bytes4, PoolManager.BeforeSwapDelta, uint24);
    
    function _.afterSwap(address sender, PoolManager.PoolKey key, IPoolManager.SwapParams params, PoolManager.BalanceDelta delta, bytes hookData) external with (env e)
        => afterSwapCVL(e, sender, key, params, delta, hookData) expect (bytes4, int128);
    
    function _.beforeDonate(
        address sender, PoolManager.PoolKey key, uint256 amount0, uint256 amount1, bytes hookData
    ) external with (env e) => beforeDonateCVL(e, sender, key, amount0, amount1, hookData) expect bytes4;
    
    function _.afterDonate(
        address sender, PoolManager.PoolKey key, uint256 amount0, uint256 amount1, bytes hookData
    ) external with (env e) => afterDonateCVL(e, sender, key, amount0, amount1, hookData) expect bytes4;
}

function beforeInitializeCVL(
        env e, address sender, PoolManager.PoolKey key, uint160 sqrtPriceX96, bytes hookData
    ) returns bytes4 {
    return _MockHooks.beforeInitialize(e, sender, key, sqrtPriceX96, hookData);
}

function afterInitializeCVL(
        env e, address sender, PoolManager.PoolKey key, uint160 sqrtPriceX96, int24 tick, bytes hookData
    ) returns bytes4 {
    return _MockHooks.afterInitialize(e, sender, key, sqrtPriceX96, tick, hookData);
}

function beforeAddLiquidityCVL(
        env e, address sender, PoolManager.PoolKey key, IPoolManager.ModifyLiquidityParams params, bytes hookData
    ) returns bytes4 {
    return _MockHooks.beforeAddLiquidity(e, sender, key, params, hookData);
}

function afterAddLiquidityCVL(
        env e, 
        address sender, 
        PoolManager.PoolKey key, 
        IPoolManager.ModifyLiquidityParams params, 
        PoolManager.BalanceDelta delta, 
        PoolManager.BalanceDelta feesAccrued, 
        bytes hookData
    ) returns (bytes4, PoolManager.BalanceDelta) {
    bytes4 selector; PoolManager.BalanceDelta retDelta;
    selector, retDelta = _MockHooks.afterAddLiquidity(e, sender, key, params, delta, feesAccrued, hookData);
    return (selector, retDelta);
}

function beforeRemoveLiquidityCVL(
        env e, address sender, PoolManager.PoolKey key, IPoolManager.ModifyLiquidityParams params, bytes hookData
    ) returns bytes4 {
    return _MockHooks.beforeRemoveLiquidity(e, sender, key, params, hookData);
}

function afterRemoveLiquidityCVL(
        env e, 
        address sender, 
        PoolManager.PoolKey key, 
        IPoolManager.ModifyLiquidityParams params, 
        PoolManager.BalanceDelta delta, 
        PoolManager.BalanceDelta feesAccrued, 
        bytes hookData
    ) returns (bytes4, PoolManager.BalanceDelta) {
    bytes4 selector; PoolManager.BalanceDelta retDelta;
    selector, retDelta = _MockHooks.afterRemoveLiquidity(e, sender, key, params, delta, feesAccrued, hookData);
    return (selector, retDelta);
}

function beforeSwapCVL(
        env e, address sender, PoolManager.PoolKey key, IPoolManager.SwapParams params, bytes hookData
    ) returns (bytes4, PoolManager.BeforeSwapDelta, uint24) {
    bytes4 selector; PoolManager.BeforeSwapDelta retDelta; uint24 retLpFee;
    selector, retDelta, retLpFee = _MockHooks.beforeSwap(e, sender, key, params, hookData);
    return (selector, retDelta, retLpFee);
}

function afterSwapCVL(
        env e, 
        address sender, 
        PoolManager.PoolKey key, 
        IPoolManager.SwapParams params, 
        PoolManager.BalanceDelta delta, 
        bytes hookData
    ) returns (bytes4, int128) {
    bytes4 selector; int128 retDelta;
    selector, retDelta = _MockHooks.afterSwap(e, sender, key, params, delta, hookData);
    return (selector, retDelta);
}

function beforeDonateCVL(
        env e, address sender, PoolManager.PoolKey key, uint256 amount0, uint256 amount1, bytes hookData
    ) returns bytes4 {
    return _MockHooks.beforeDonate(e, sender, key, amount0, amount1, hookData);
}

function afterDonateCVL(
        env e, address sender, PoolManager.PoolKey key, uint256 amount0, uint256 amount1, bytes hookData
    ) returns bytes4 {
    return _MockHooks.afterDonate(e, sender, key, amount0, amount1, hookData);
}