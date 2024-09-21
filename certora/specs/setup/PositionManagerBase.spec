import "./PoolManagerBase.spec";
import "./StateLibrary.spec";

using PositionManagerHarness as _PositionManager;

///////////////////////////////////////// Methods /////////////////////////////////////////////

methods {
    
    // Permit2
    function _.permit(address owner, IAllowanceTransfer.PermitSingle permitSingle, bytes signature) external
        => NONDET;
    function _.permit(address owner, IAllowanceTransfer.PermitBatch permitBatch, bytes signature) external
        => NONDET;
    function _.transferFrom(address from, address to, uint160 amount, address token) external with (env e)
        => safeTransferFromCVL(e, token, from, to, amount, true) expect void;

    // Notifier
    function _.notifySubscribe(uint256 tokenId, bytes data) external with (env e) 
        => notifySubscribeCVL(e, tokenId, data) expect void;
    function _.notifyUnsubscribe(uint256 tokenId) external  with (env e) 
        => notifyUnsubscribeCVL(e, tokenId) expect void;
    function _.notifyModifyLiquidity(
        uint256 tokenId, int256 _liquidityChange, PoolManager.BalanceDelta _feesAccrued
    ) external with (env e) => notifyModifyLiquidityCVL(e, tokenId, _liquidityChange, _feesAccrued) expect void;
    function _.notifyTransfer(uint256 tokenId, address previousOwner, address newOwner) external with (env e)
        => notifyTransferCVL(e, tokenId, previousOwner, newOwner) expect void;

    // ERC721
    //  - don't care about call to ERC721TokenReceiver from safeTransfer()
    function _.onERC721Received(address, address, uint256, bytes) external 
        => NONDET;
    function _._hashTypedData(bytes32 dataHash) internal 
        => hashTypedDataEIP712(calledContract, dataHash) expect bytes32;

    // SignatureVerification
    function SignatureVerification.verify(bytes calldata signature, bytes32 hash, address claimedSigner) internal
        => verifyCVL(claimedSigner);
}

///////////////////////////////////////// Functions ////////////////////////////////////////////

// ERC721
ghost hashTypedDataEIP712(address,bytes32) returns bytes32 {
    axiom forall address self. forall bytes32 hash1. forall bytes32 hash2.
        hash1 != hash2 => hashTypedDataEIP712(self, hash1) != hashTypedDataEIP712(self, hash2);
}

// Mock notifier calls

persistent ghost uint256 ghostNotifierTokenId {
    init_state axiom ghostNotifierTokenId == 0;
}

persistent ghost int256 ghostNotifierLiquidityChange {
    init_state axiom ghostNotifierLiquidityChange == 0;
}

persistent ghost int256 ghostNotifierFeesAccrued {
    init_state axiom ghostNotifierFeesAccrued == 0;
}

persistent ghost address ghostNotifierPreviousOwner {
    init_state axiom ghostNotifierPreviousOwner == 0;
}

persistent ghost address ghostNotifierNewOwner {
    init_state axiom ghostNotifierNewOwner == 0;
}

function notifySubscribeCVL(env e, uint256 tokenId, bytes data) {
    require(data.length == 0);
    ghostNotifierTokenId = tokenId;
}

function notifyUnsubscribeCVL(env e, uint256 tokenId)  {
    ghostNotifierTokenId = tokenId;
}

function notifyModifyLiquidityCVL(env e, uint256 tokenId, int256 liquidityChange, PoolManager.BalanceDelta feesAccrued) {
    ghostNotifierTokenId = tokenId;
    ghostNotifierLiquidityChange = liquidityChange;
    ghostNotifierFeesAccrued = feesAccrued;
}

function notifyTransferCVL(env e, uint256 tokenId, address previousOwner, address newOwner) {
    ghostNotifierTokenId = tokenId;
    ghostNotifierPreviousOwner = previousOwner;
    ghostNotifierNewOwner = newOwner;
}

// SignatureVerification.verify() summary
function verifyCVL(address claimedSigner) {
    require(claimedSigner != 0);
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

persistent ghost mapping(uint256 => uint256) ghostPositionInfo {
    init_state axiom forall uint256 tokenId. ghostPositionInfo[tokenId] == 0;
}

persistent ghost mapping (uint256 => uint8) ghostPositionInfoHasSubscriber {
    init_state axiom forall uint256 tokenId. ghostPositionInfoHasSubscriber[tokenId] == 0;
    axiom forall uint256 tokenId. ghostPositionInfoHasSubscriber[tokenId] 
        == POSITION_INFO_UNPACK_HAS_SUBSCRIBER(ghostPositionInfo[tokenId]);
}

persistent ghost mapping (uint256 => int24) ghostPositionInfoTickLower {
    init_state axiom forall uint256 tokenId. ghostPositionInfoTickLower[tokenId] == 0;
    axiom forall uint256 tokenId. ghostPositionInfoTickLower[tokenId] 
        == POSITION_INFO_UNPACK_TICK_LOWER(ghostPositionInfo[tokenId]);
}

persistent ghost mapping (uint256 => int24) ghostPositionInfoTickUpper {
    init_state axiom forall uint256 tokenId. ghostPositionInfoTickUpper[tokenId] == 0;
    axiom forall uint256 tokenId. ghostPositionInfoTickUpper[tokenId] 
        == POSITION_INFO_UNPACK_TICK_UPPER(ghostPositionInfo[tokenId]);
}

persistent ghost mapping (uint256 => mathint) ghostPositionInfoPoolId {
    init_state axiom forall uint256 tokenId. ghostPositionInfoPoolId[tokenId] == 0;
    axiom forall uint256 tokenId. ghostPositionInfoPoolId[tokenId] 
        == POSITION_INFO_UNPACK_POOL_ID(ghostPositionInfo[tokenId]);
}    

definition IS_EMPTY_POSITION_INFO(uint256 tokenId) returns bool 
    = ghostPositionInfo[tokenId] == EMPTY_POSITION_INFO();

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

definition ANY_FIELD_OF_POOLS_KEY_SET(bytes25 poolId) returns bool =
    ghostPoolKeysCurrency0[poolId] != 0 
    || ghostPoolKeysCurrency1[poolId] != 0
    || ghostPoolKeysFee[poolId] != 0
    || ghostPoolKeysTickSpacing[poolId] != 0
    || ghostPoolKeysHooks[poolId] != 0;

// poolKeys[].currency0

persistent ghost mapping(bytes25 => address) ghostPoolKeysCurrency0 {
    init_state axiom forall bytes25 poolId. ghostPoolKeysCurrency0[poolId] == 0;
}

hook Sload PoolManager.Currency val _PositionManager.poolKeys[KEY bytes25 poolId].currency0 {
    require(ghostPoolKeysCurrency0[poolId] == val);
}

hook Sstore _PositionManager.poolKeys[KEY bytes25 poolId].currency0 PoolManager.Currency val {
    ghostPoolKeysCurrency0[poolId] = val;
}

// poolKeys[].currency1

persistent ghost mapping(bytes25 => address) ghostPoolKeysCurrency1 {
    init_state axiom forall bytes25 poolId. ghostPoolKeysCurrency1[poolId] == 0;
}

hook Sload PoolManager.Currency val _PositionManager.poolKeys[KEY bytes25 poolId].currency1 {
    require(ghostPoolKeysCurrency1[poolId] == val);
}

hook Sstore _PositionManager.poolKeys[KEY bytes25 poolId].currency1 PoolManager.Currency val {
    ghostPoolKeysCurrency1[poolId] = val;
}

// poolKeys[].fee

persistent ghost mapping(bytes25 => uint24) ghostPoolKeysFee {
    init_state axiom forall bytes25 poolId. ghostPoolKeysFee[poolId] == 0;
    axiom forall bytes25 poolId. ghostPoolKeysFee[poolId] >= 0 && ghostPoolKeysFee[poolId] <= max_uint24;
}

hook Sload uint24 val _PositionManager.poolKeys[KEY bytes25 poolId].fee {
    require(require_uint24(ghostPoolKeysFee[poolId]) == val);
}

hook Sstore _PositionManager.poolKeys[KEY bytes25 poolId].fee uint24 val {
    ghostPoolKeysFee[poolId] = val;
}

// poolKeys[].tickSpacing

persistent ghost mapping(bytes25 => int24) ghostPoolKeysTickSpacing {
    init_state axiom forall bytes25 poolId. ghostPoolKeysTickSpacing[poolId] == 0;
}

hook Sload int24 val _PositionManager.poolKeys[KEY bytes25 poolId].tickSpacing {
    require(ghostPoolKeysTickSpacing[poolId] == val);
}

hook Sstore _PositionManager.poolKeys[KEY bytes25 poolId].tickSpacing int24 val {
    ghostPoolKeysTickSpacing[poolId] = val;
}

// poolKeys[].hooks

persistent ghost mapping(bytes25 => address) ghostPoolKeysHooks {
    init_state axiom forall bytes25 keyId. ghostPoolKeysHooks[keyId] == 0;
}

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

persistent ghost mapping(uint256 => address) ghostERC721OwnerOf {
    init_state axiom forall uint256 tokenId. ghostERC721OwnerOf[tokenId] == 0;
}

hook Sload address val _PositionManager._ownerOf[KEY uint256 tokenId] {
    require(ghostERC721OwnerOf[tokenId] == val);
}

hook Sstore _PositionManager._ownerOf[KEY uint256 tokenId] address val {
    ghostERC721OwnerOf[tokenId] = val;
}

// Ghost copy of `mapping(address => uint256) internal _balanceOf;`

persistent ghost mapping(address => mathint) ghostERC721BalanceOf {
    init_state axiom forall address owner. ghostERC721BalanceOf[owner] == 0;
    // Avoid overflows via uint128 limitation
    axiom forall address owner. ghostERC721BalanceOf[owner] >= 0 && ghostERC721BalanceOf[owner] <= max_uint128; 
}

hook Sload uint256 val _PositionManager._balanceOf[KEY address owner] {
    require(require_uint256(ghostERC721BalanceOf[owner]) == val);
}

hook Sstore _PositionManager._balanceOf[KEY address owner] uint256 val {
    ghostERC721BalanceOf[owner] = val;
}

// Ghost copy of `mapping(uint256 => address) public getApproved;`

persistent ghost mapping(uint256 => address) ghostERC721GetApproved {
    init_state axiom forall uint256 tokenId. ghostERC721GetApproved[tokenId] == 0;
}

hook Sload address val _PositionManager.getApproved[KEY uint256 tokenId] {
    require(ghostERC721GetApproved[tokenId] == val);
}

hook Sstore _PositionManager.getApproved[KEY uint256 tokenId] address val {
    ghostERC721GetApproved[tokenId] = val;
}

// Ghost copy of `mapping(address => mapping(address => bool)) public isApprovedForAll;`

persistent ghost mapping(address => mapping(address => bool)) ghostERC721IsApprovedForAll {
    init_state axiom forall address owner. forall address spender. ghostERC721IsApprovedForAll[owner][spender] == false;
}

hook Sload bool val _PositionManager.isApprovedForAll[KEY address owner][KEY address operator] {
    require(ghostERC721IsApprovedForAll[owner][operator] == val);
}

hook Sstore _PositionManager.isApprovedForAll[KEY address owner][KEY address operator] bool val {
    ghostERC721IsApprovedForAll[owner][operator] = val;
}

//
// Notifier
//

// Ghost copy of `mapping(uint256 tokenId => ISubscriber subscriber) public subscriber;`

persistent ghost mapping(uint256 => address) ghostNotifierSubscriber {
    init_state axiom forall uint256 tokenId. ghostNotifierSubscriber[tokenId] == 0;
}

hook Sload address val _PositionManager.subscriber[KEY uint256 tokenId] {
    require(ghostNotifierSubscriber[tokenId] == val);
}

hook Sstore _PositionManager.subscriber[KEY uint256 tokenId] address val {
    ghostNotifierSubscriber[tokenId] = val;
}

//
// UnorderedNonce
//

// Ghost copy of `mapping(address owner => mapping(uint256 word => uint256 bitmap)) public nonces;`

persistent ghost mapping(address => mapping(uint256 => mathint)) ghostNonces {
    init_state axiom forall address owner. forall uint256 word. ghostNonces[owner][word] == 0;
    // Avoid overflows via uint128 limitation
    axiom forall address owner. forall uint256 word. 
        ghostNonces[owner][word] >= 0 && ghostNonces[owner][word] <= max_uint128;
}

hook Sload uint256 val _PositionManager.nonces[KEY address owner][KEY uint256 word] {
    require(require_uint256(ghostNonces[owner][word]) == val);
}

hook Sstore _PositionManager.nonces[KEY address owner][KEY uint256 word] uint256 val {
    ghostNonces[owner][word] = val;
}