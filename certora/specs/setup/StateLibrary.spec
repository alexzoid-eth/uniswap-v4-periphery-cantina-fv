methods {
    // StateLibrary
    //  - read values from storage hooks ghost variables directly as PoolManager's extsload() is removed
    
    // PositionManager use StateLibrary.getPositionLiquidity() only
    function StateLibrary.getPositionLiquidity(
        address manager,
        PoolManager.PoolId poolId,
        bytes32 positionKey
    ) internal returns (uint128) => getPositionLiquidityCVL(poolId, positionKey);
}

function getPositionLiquidityCVL(PoolManager.PoolId poolId, bytes32 positionKey) returns uint128 {
    return require_uint128(ghostPoolsPositionsLiquidity[poolId][positionKey]);
}