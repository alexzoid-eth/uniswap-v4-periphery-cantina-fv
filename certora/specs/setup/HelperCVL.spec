using HelperCVL as _HelperCVL;

methods {
    
    // Link separate HelperCVL contract with helper solidity functions
    
    function _HelperCVL.fromCurrency(HelperCVL.Currency) external returns (address) envfree;
    function _HelperCVL.toCurrency(address) external returns (HelperCVL.Currency) envfree;
    function _HelperCVL.poolKeyToId(HelperCVL.PoolKey) external returns (bytes32) envfree;
    function _HelperCVL.positionKey(address,int24,int24,bytes32) external returns (bytes32) envfree;
    function _HelperCVL.amount0(HelperCVL.BalanceDelta) external returns (int128) envfree;
    function _HelperCVL.amount1(HelperCVL.BalanceDelta) external returns (int128) envfree;
    function _HelperCVL.wrapToPoolId(bytes32) external returns (HelperCVL.PoolId) envfree;
    function _HelperCVL.fromId(uint256 id) external returns (HelperCVL.Currency) envfree;
}

function poolKeyToPoolIdCVL(HelperCVL.PoolKey key) returns HelperCVL.PoolId {
    return _HelperCVL.wrapToPoolId(_HelperCVL.poolKeyToId(key));
}

function calculatePositionKeyCVL(address owner, int24 tickLower, int24 tickUpper, bytes32 salt) returns bytes32 {
    return _HelperCVL.positionKey(owner, tickLower, tickUpper, salt);
}