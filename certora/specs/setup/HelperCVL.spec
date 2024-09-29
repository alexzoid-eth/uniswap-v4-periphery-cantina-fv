using HelperCVL as _HelperCVL;

methods {
    
    // Link separate HelperCVL contract with helper solidity functions
    
    function _HelperCVL.fromCurrency(HelperCVL.Currency) external returns (address) envfree;
    function _HelperCVL.toCurrency(address) external returns (HelperCVL.Currency) envfree;
    function _HelperCVL.amount0(HelperCVL.BalanceDelta) external returns (int128) envfree;
    function _HelperCVL.amount1(HelperCVL.BalanceDelta) external returns (int128) envfree;
    function _HelperCVL.wrapToPoolId(bytes32) external returns (HelperCVL.PoolId) envfree;
    function _HelperCVL.fromId(uint256 id) external returns (HelperCVL.Currency) envfree;
    function _HelperCVL.assertOnFailure(bool success) external envfree;
    function _HelperCVL.poolId(PositionManagerHarness.PositionInfo info) external returns (bytes25) envfree;
    function _HelperCVL.tickLower(PositionManagerHarness.PositionInfo info) external returns (int24) envfree;
    function _HelperCVL.tickUpper(PositionManagerHarness.PositionInfo info) external returns (int24) envfree;
    function _HelperCVL.hasSubscriber(PositionManagerHarness.PositionInfo info) external returns (bool) envfree;
    function _HelperCVL.slot0SqrtPriceX96(PoolManager.Slot0 _packed) external returns (uint160) envfree;
    function _HelperCVL.slot0Tick(PoolManager.Slot0 _packed) external returns (int24) envfree;
    function _HelperCVL.castFromBytes32ToBytes25(bytes32 val) external returns (bytes25) envfree;

    function _.toId(PoolManager.PoolKey memory poolKey) internal
        => poolKeyToPoolIdCVL(poolKey) expect PoolManager.PoolId ALL;
}

// Make a single mathint from two addresses
definition hashIntCVL(address user, address token) returns mathint 
    = (to_mathint(user) * 2^160 + to_mathint(token));

function poolKeyVariablesToIdCVL(address currency0, address currency1, uint24 fee, int24 tickSpacing, address hooks) returns bytes32 {
    return keccak256(currency0, currency1, fee, tickSpacing, hooks);
}

function poolKeyVariablesToShortIdCVL(address currency0, address currency1, uint24 fee, int24 tickSpacing, address hooks) returns bytes25 {
    return _HelperCVL.castFromBytes32ToBytes25(poolKeyVariablesToIdCVL(currency0, currency1, fee, tickSpacing, hooks));
}

function poolKeyToIdCVL(HelperCVL.PoolKey key) returns bytes32 {
    return poolKeyVariablesToIdCVL(
        _HelperCVL.fromCurrency(key.currency0), 
        _HelperCVL.fromCurrency(key.currency1), 
        key.fee, 
        key.tickSpacing, 
        key.hooks
        ); 
}

function poolKeyToPoolIdCVL(HelperCVL.PoolKey key) returns HelperCVL.PoolId {
    return _HelperCVL.wrapToPoolId(poolKeyToIdCVL(key));
}

function calculatePositionKeyCVL(address owner, int24 tickLower, int24 tickUpper, bytes32 salt) returns bytes32 {
    return keccak256(owner, tickLower, tickUpper, salt);
}

function positionInfoHasSubscriberCVL(mathint tokenId) returns bool {
    return _HelperCVL.hasSubscriber(ghostPositionInfo[tokenId]);
}

function positionInfoTickLowerCVL(mathint tokenId) returns int24 {
    return _HelperCVL.tickLower(ghostPositionInfo[tokenId]);
}

function positionInfoTickUpperCVL(mathint tokenId) returns int24 {
    return _HelperCVL.tickUpper(ghostPositionInfo[tokenId]);
}

function positionInfoPoolIdCVL(mathint tokenId) returns bytes25 {
    return _HelperCVL.poolId(ghostPositionInfo[tokenId]);
}

function poolMangerPoolIdCVL(mathint tokenId) returns bytes32 {
    return poolKeyVariablesToIdCVL(
        ghostPoolKeysCurrency0[positionInfoPoolIdCVL(tokenId)],
        ghostPoolKeysCurrency1[positionInfoPoolIdCVL(tokenId)],
        ghostPoolKeysFee[positionInfoPoolIdCVL(tokenId)],
        ghostPoolKeysTickSpacing[positionInfoPoolIdCVL(tokenId)],
        ghostPoolKeysHooks[positionInfoPoolIdCVL(tokenId)]
    );
}

function poolManagerSlot0SqrtPriceX96CVL(bytes32 poolId) returns uint160 {
    return _HelperCVL.slot0SqrtPriceX96(ghostPoolsSlot0[poolId]);
}

function poolManagerSlot0SqrtPriceX96ByShortPoolIdCVL(bytes25 shortPoolId) returns uint160 {

    bytes32 poolId = poolKeyVariablesToIdCVL(
        ghostPoolKeysCurrency0[shortPoolId],
        ghostPoolKeysCurrency1[shortPoolId],
        ghostPoolKeysFee[shortPoolId],
        ghostPoolKeysTickSpacing[shortPoolId],
        ghostPoolKeysHooks[shortPoolId]
    );

    return poolManagerSlot0SqrtPriceX96CVL(poolId);
}

function poolManagerSlot0SqrtPriceX96ByTokenIdCVL(mathint tokenId) returns uint160 {
    return poolManagerSlot0SqrtPriceX96ByShortPoolIdCVL(positionInfoPoolIdCVL(tokenId));
}

function poolManagerSlot0Tick(bytes32 poolId) returns int24 {
    return _HelperCVL.slot0Tick(ghostPoolsSlot0[poolId]);
}

function poolManagerPoolPositionLiquidity(mathint tokenId) returns mathint {

    bytes32 poolId = poolMangerPoolIdCVL(tokenId);

    bytes32 positionId = calculatePositionKeyCVL(
        _PositionManager, 
        positionInfoTickLowerCVL(tokenId), 
        positionInfoTickUpperCVL(tokenId), 
        to_bytes32(require_uint256(tokenId))
        );
    
    return ghostPoolsPositionsLiquidity[poolId][positionId];
}