import "./PoolManagerBase.spec";

using PositionManagerHarness as _PositionManager;

///////////////////////////////////////// Methods /////////////////////////////////////////////

methods {

    // External functions
    //  - assume currency can be address(0) - native, ERC20A, ERC20B or ERC20C
    function _PositionManager.sweep(PoolManager.Currency currency, address to) external with (env e) 
        => sweepCVL(e, currency, to);

    // Removed external functions
    // - modifyLiquidities(), modifyLiquiditiesWithoutUnlock() and unlockCallback() not needed as _handleAction is 
    //  no-op and summarizing unlock here would have no effect
    // - multicall() removed

    function _PositionManager.modifyLiquidities(bytes unlockData, uint256 deadline) external => NONDET DELETE;
    function _PositionManager.modifyLiquiditiesWithoutUnlock(bytes actions, bytes[] params) external => NONDET DELETE;
    function _PositionManager.unlockCallback(bytes data) external returns (bytes)  => NONDET DELETE;
    
    function _PositionManager.multicall(bytes[] data) external returns (bytes[]) => NONDET DELETE;
    
    // Notifier
    //  - link external calls to MockSubscriber
    function _.notifySubscribe(uint256, bytes data) external => DISPATCHER(true);
    function _.notifyUnsubscribe(uint256) external => DISPATCHER(true);
    function _.notifyModifyLiquidity(
        uint256, int256 _liquidityChange, PoolManager.BalanceDelta _feesAccrued
    ) external => DISPATCHER(true);
    function _.notifyTransfer(uint256, address, address) external => DISPATCHER(true);

    // ERC721
    //  - don't care about call to ERC721TokenReceiver from safeTransfer()
    function _.onERC721Received(address, address, uint256, bytes) external => NONDET;

    // IERC1271
    //  - the bytes4 magic value 0x1626ba7e
    function _.isValidSignature(bytes32 hash, bytes signature) external => ALWAYS(0x1626ba7e);
}

///////////////////////////////////////// Functions ////////////////////////////////////////////

function sweepCVL(env e, PoolManager.Currency currency, address to) {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Assume only supported in this environment currencies are passed
    requireValidCurrencyCVL(currency);

    _PositionManager.sweep(e, currency, to);
}

////////////////////////////////////////// Hooks //////////////////////////////////////////////

//
// PositionManager
//

// Ghost copy of `uint256 public nextTokenId`

persistent ghost mathint ghostNextTokenId {
    init_state axiom ghostNextTokenId == 1;
    axiom ghostNextTokenId >= 1 && ghostNextTokenId <= max_uint256;
}

hook Sload uint256 val _PositionManager.nextTokenId {
    require(require_uint256(ghostNextTokenId) == val);
}

hook Sstore _PositionManager.nextTokenId uint256 val {
    ghostNextTokenId = val;
}

// Ghost copy of `mapping(uint256 tokenId => PositionInfo info) public positionInfo`
//  - use uint256 value with .(offset 0) hook instead of PositionInfo

persistent ghost mapping(uint256 => uint256) ghostPositionInfo;

definition POSITION_INFO_UNPACK_HAS_SUBSCRIBER(uint256 val) returns mathint 
    = val & 0xFF;
definition POSITION_INFO_UNPACK_TICK_LOWER(uint256 val) returns mathint 
    = (val >> 8) & 0xFFFFFF;
definition POSITION_INFO_UNPACK_TICK_UPPER(uint256 val) returns mathint 
    = (val >> 32) & 0xFFFFFF;
definition POSITION_INFO_UNPACK_POOL_ID(uint256 val) returns mathint 
    = val & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000000000;

function positionInfoHasSubscriberCVL(uint256 tokenId) returns mathint {
    return POSITION_INFO_UNPACK_HAS_SUBSCRIBER(ghostPositionInfo[tokenId]);
}

function positionInfoTickLowerCVL(uint256 tokenId) returns mathint {
    return POSITION_INFO_UNPACK_TICK_LOWER(ghostPositionInfo[tokenId]);
}

function positionInfoTickUpperCVL(uint256 tokenId) returns mathint {
    return POSITION_INFO_UNPACK_TICK_UPPER(ghostPositionInfo[tokenId]);
}

function positionInfoPoolIdCVL(uint256 tokenId) returns mathint {
    return POSITION_INFO_UNPACK_POOL_ID(ghostPositionInfo[tokenId]);
}

hook Sload uint256 val _PositionManager.positionInfo[KEY uint256 tokenId].(offset 0) {
    require(ghostPositionInfo[tokenId] == val);
}

hook Sstore _PositionManager.positionInfo[KEY uint256 tokenId].(offset 0) uint256 val {
    ghostPositionInfo[tokenId] = val;
}

// Ghost copy of `mapping(bytes25 poolId => PoolKey poolKey) public poolKeys`

// poolKeys[].currency0

persistent ghost mapping(bytes25 => address) ghostPoolKeysCurrency0;

hook Sload PoolManager.Currency val _PositionManager.poolKeys[KEY bytes25 poolId].currency0 {
    require(ghostPoolKeysCurrency0[poolId] == val);
}

hook Sstore _PositionManager.poolKeys[KEY bytes25 poolId].currency0 PoolManager.Currency val {
    ghostPoolKeysCurrency0[poolId] = val;
}

// poolKeys[].currency1

persistent ghost mapping(bytes25 => address) ghostPoolKeysCurrency1;

hook Sload PoolManager.Currency val _PositionManager.poolKeys[KEY bytes25 poolId].currency1 {
    require(ghostPoolKeysCurrency1[poolId] == val);
}

hook Sstore _PositionManager.poolKeys[KEY bytes25 poolId].currency1 PoolManager.Currency val {
    ghostPoolKeysCurrency1[poolId] = val;
}

// poolKeys[].fee

persistent ghost mapping(bytes25 => mathint) ghostPoolKeysFee {
    axiom forall bytes25 poolId. ghostPoolKeysFee[poolId] >= 0 && ghostPoolKeysFee[poolId] <= max_uint24;
}

hook Sload uint24 val _PositionManager.poolKeys[KEY bytes25 poolId].fee {
    require(require_uint24(ghostPoolKeysFee[poolId]) == val);
}

hook Sstore _PositionManager.poolKeys[KEY bytes25 poolId].fee uint24 val {
    ghostPoolKeysFee[poolId] = val;
}

// poolKeys[].tickSpacing

persistent ghost mapping(bytes25 => int24) ghostPoolKeysTickSpacing;

hook Sload int24 val _PositionManager.poolKeys[KEY bytes25 poolId].tickSpacing {
    require(ghostPoolKeysTickSpacing[poolId] == val);
}

hook Sstore _PositionManager.poolKeys[KEY bytes25 poolId].tickSpacing int24 val {
    ghostPoolKeysTickSpacing[poolId] = val;
}

// poolKeys[].hooks

persistent ghost mapping(bytes25 => address) ghostPoolKeysHooks;

hook Sload address val _PositionManager.poolKeys[KEY bytes25 poolId].hooks {
    require(ghostPoolKeysHooks[poolId] == val);
}

hook Sstore _PositionManager.poolKeys[KEY bytes25 poolId].hooks address val {
    ghostPoolKeysHooks[poolId] = val;
}

// 
// ERC721
// 

// Ghost copy of `mapping(uint256 => address) internal _ownerOf;`

persistent ghost mapping(uint256 => address) ghostERC721OwnerOf;

hook Sload address val _PositionManager._ownerOf[KEY uint256 tokenId] {
    require(ghostERC721OwnerOf[tokenId] == val);
}

hook Sstore _PositionManager._ownerOf[KEY uint256 tokenId] address val {
    ghostERC721OwnerOf[tokenId] = val;
}

// Ghost copy of `mapping(address => uint256) internal _balanceOf;`

persistent ghost mapping(address => mathint) ghostERC721BalanceOf {
    axiom forall address owner. ghostERC721BalanceOf[owner] >= 0 && ghostERC721BalanceOf[owner] <= max_uint256;
}

hook Sload uint256 val _PositionManager._balanceOf[KEY address owner] {
    require(require_uint256(ghostERC721BalanceOf[owner]) == val);
}

hook Sstore _PositionManager._balanceOf[KEY address owner] uint256 val {
    ghostERC721BalanceOf[owner] = val;
}

// Ghost copy of `mapping(uint256 => address) public getApproved;`

persistent ghost mapping(uint256 => address) ghostERC721GetApproved;

hook Sload address val _PositionManager.getApproved[KEY uint256 tokenId] {
    require(ghostERC721GetApproved[tokenId] == val);
}

hook Sstore _PositionManager.getApproved[KEY uint256 tokenId] address val {
    ghostERC721GetApproved[tokenId] = val;
}

// Ghost copy of `mapping(address => mapping(address => bool)) public isApprovedForAll;`

persistent ghost mapping(address => mapping(address => bool)) ghostERC721IsApprovedForAll;

hook Sload bool val _PositionManager.isApprovedForAll[KEY address owner][KEY address operator] {
    require(ghostERC721IsApprovedForAll[owner][operator] == val);
}

hook Sstore _PositionManager.isApprovedForAll[KEY address owner][KEY address operator] bool val {
    ghostERC721IsApprovedForAll[owner][operator] = val;
}

//
// UnorderedNonce
//

// Ghost copy of `mapping(address owner => mapping(uint256 word => uint256 bitmap)) public nonces;`

persistent ghost mapping(address => mapping(uint256 => mathint)) ghostNonces {
    axiom forall address owner. forall uint256 word. 
        ghostNonces[owner][word] >= 0 && ghostNonces[owner][word] <= max_uint256;
}

hook Sload uint256 val _PositionManager.nonces[KEY address owner][KEY uint256 word] {
    require(require_uint256(ghostNonces[owner][word]) == val);
}

hook Sstore _PositionManager.nonces[KEY address owner][KEY uint256 word] uint256 val {
    ghostNonces[owner][word] = val;
}

//
// Notifier
//

// Ghost copy of `mapping(uint256 tokenId => ISubscriber subscriber) public subscriber;`

persistent ghost mapping(uint256 => address) ghostNotifierSubscriber;

hook Sload address val _PositionManager.subscriber[KEY uint256 tokenId] {
    require(ghostNotifierSubscriber[tokenId] == val);
}

hook Sstore _PositionManager.subscriber[KEY uint256 tokenId] address val {
    ghostNotifierSubscriber[tokenId] = val;
}