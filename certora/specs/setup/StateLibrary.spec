methods {
    // StateLibrary (PositionManager use it)
    //  - read values from storage hooks ghost variables directly as PoolManager's extsload() is removed
    
    function StateLibrary.getPositionLiquidity(
        address manager,
        PoolManager.PoolId poolId,
        bytes32 positionKey
    ) internal returns (uint128) => getPositionLiquidityCVL(poolId, positionKey);

    /*
    function StateLibrary.getSlot0(
        address manager,
        PoolManager.PoolId poolId
    ) internal returns (uint160, int24, uint24, uint24) => getSlot0CVL(poolId);

    function StateLibrary.getTickInfo(
        address manager,
        PoolManager.PoolId poolId,
        int24 tick
    ) internal returns (uint128, int128, uint256, uint256) => getTickInfoCVL(poolId, tick);

    function StateLibrary.getTickLiquidity(
        address manager,
        PoolManager.PoolId poolId,
        int24 tick
    ) internal returns (uint128, int128) => getTickLiquidityCVL(poolId, tick);

    function StateLibrary.getTickFeeGrowthOutside(
        address manager,
        PoolManager.PoolId poolId,
        int24 tick
    ) internal returns (uint256, uint256) => getTickFeeGrowthOutsideCVL(poolId, tick);

    function StateLibrary.getFeeGrowthGlobals(
        address manager,
        PoolManager.PoolId poolId
    ) internal returns (uint256, uint256) => getFeeGrowthGlobalsCVL(poolId);

    function StateLibrary.getLiquidity(
        address manager,
        PoolManager.PoolId poolId
    ) internal returns (uint128) => getLiquidityCVL(poolId);

    function StateLibrary.getTickBitmap(
        address manager,
        PoolManager.PoolId poolId,
        int16 wordPos
    ) internal returns (uint256) => getTickBitmapCVL(poolId, wordPos);

    function StateLibrary.getPositionInfo(
        address manager,
        PoolManager.PoolId poolId,
        bytes32 positionKey
    ) internal returns (uint128, uint256, uint256) => getPositionInfoCVL(poolId, positionKey);
    */
}

function getPositionLiquidityCVL(PoolManager.PoolId poolId, bytes32 positionKey) returns uint128 {
    return require_uint128(ghostPoolsPositionsLiquidity[poolId][positionKey]);
}
/*
function getSlot0CVL(PoolManager.PoolId poolId) returns (uint160, int24, uint24, uint24) {
    return (
        require_uint160(slot0SqrtPriceX96CVL(poolId)),
        require_int24(slot0TickCVL(poolId)),
        require_uint24(slot0ProtocolFeeZeroForOneCVL(poolId)),
        require_uint24(Slot0LpFeeCVL(poolId))
    );
}

function getTickInfoCVL(PoolManager.PoolId poolId, int24 tick) returns (uint128, int128, uint256, uint256) {
    return (
        require_uint128(ghostPoolsTicksLiquidityGross[poolId][tick]),
        require_int128(ghostPoolsTicksLiquidityNet[poolId][tick]),
        require_uint256(ghostPoolsTicksFeeGrowthOutside0X128[poolId][tick]),
        require_uint256(ghostPoolsTicksFeeGrowthOutside1X128[poolId][tick])
    );
}

function getTickLiquidityCVL(PoolManager.PoolId poolId, int24 tick) returns (uint128, int128) {
    return (
        require_uint128(ghostPoolsTicksLiquidityGross[poolId][tick]),
        require_int128(ghostPoolsTicksLiquidityNet[poolId][tick])
    );
}

function getTickFeeGrowthOutsideCVL(PoolManager.PoolId poolId, int24 tick) returns (uint256, uint256) {
    return (
        require_uint256(ghostPoolsTicksFeeGrowthOutside0X128[poolId][tick]),
        require_uint256(ghostPoolsTicksFeeGrowthOutside1X128[poolId][tick])
    );
}

function getFeeGrowthGlobalsCVL(PoolManager.PoolId poolId) returns (uint256, uint256) {
    return (
        require_uint256(ghostPoolsFeeGrowthGlobal0X128[poolId]),
        require_uint256(ghostPoolsFeeGrowthGlobal1X128[poolId])
    );
}

function getLiquidityCVL(PoolManager.PoolId poolId) returns uint128 {
    return require_uint128(ghostPoolsLiquidity[poolId]);
}

function getTickBitmapCVL(PoolManager.PoolId poolId, int16 wordPos) returns uint256 {
    return require_uint256(ghostPoolsTickBitmap[poolId][wordPos]);
}

function getPositionInfoCVL(PoolManager.PoolId poolId, bytes32 positionKey) returns (uint128, uint256, uint256) {
    return (
        require_uint128(ghostPoolsPositionsLiquidity[poolId][positionKey]),
        require_uint256(ghostPoolsPositionsFeeGrowthInside0LastX128[poolId][positionKey]),
        require_uint256(ghostPoolsPositionsFeeGrowthInside1LastX128[poolId][positionKey])
    );
}
*/