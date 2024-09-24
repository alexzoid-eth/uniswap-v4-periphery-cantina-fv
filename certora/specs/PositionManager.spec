import "./setup/PositionManagerBase.spec";
import "./PositionManagerValidState.spec";

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

    // HelperCVL
    function _.calculatePositionKey(
        address owner, int24 tickLower, int24 tickUpper, bytes32 salt
    ) internal => calculatePositionKeyCVL(owner, tickLower, tickUpper, salt) expect bytes32 ALL;
}

//
// Sanity
//

// Check if there is at least one path to execute an external function without a revert 
use builtin rule sanity filtered { f -> f.contract == currentContract }

//
// Valid State
//

// Execute invariants PositionManagerValidState
use invariant validNextTokenId;
use invariant noInfoForInvalidTokenIds;
use invariant validPositionTicks;
use invariant activePositionsMatchesToken;
use invariant activePositionMatchesPoolKey;
use invariant activePositionMatchesInitializedPoolInPoolManager;
use invariant poolKeyMatchesInitializedPoolInPoolManager;
use invariant validPoolKeyStructure;
use invariant subscriberAddressSetWithFlag;
use invariant subscribersForExistingTokensOnly;
use invariant noApprovalsForZeroAddress;
use invariant zeroAddressHasNoBalance;
use invariant getApprovedForExistingTokensOnly;

// 
// Variables Transition
//

// The nextTokenId value always increases monotonically
rule nextTokenIdMonotonicallyIncreasing(env e, method f, calldataarg args) {

    mathint before = ghostNextTokenId;

    f(e, args);

    mathint after = ghostNextTokenId;

    assert(before != after => after == before + 1);
}

// The ticks in positionInfo remain constant for a given tokenId, otherwise been cleared
rule positionTicksUnchanged(env e, method f, calldataarg args, uint256 tokenId) {

    // Active position MUST correspond minted token and vice versa
    requireInvariant activePositionsMatchesToken(e, tokenId);
    // Active position ticks MUST be within the valid range defined by TickMath
    requireInvariant validPositionTicks(e, tokenId);

    mathint tickLowerBefore = positionInfoTickLowerCVL(tokenId);
    mathint tickUpperBefore = positionInfoTickUpperCVL(tokenId);

    f(e, args);

    mathint tickLowerAfter = positionInfoTickLowerCVL(tokenId);
    mathint tickUpperAfter = positionInfoTickUpperCVL(tokenId);

    assert(tickLowerBefore != 0 || tickUpperBefore != 0 => (
        // Unchanged
        tickLowerBefore == tickLowerAfter && tickUpperBefore == tickUpperAfter
        // Position was cleared
        || IS_EMPTY_POSITION_INFO(tokenId)
    ));
}

// The poolId in positionInfo remains constant for a given tokenId, otherwise been cleared
rule positionPoolIdUnchanged(env e, method f, calldataarg args, uint256 tokenId) {

    // Active position MUST correspond minted token and vice versa
    requireInvariant activePositionsMatchesToken(e, tokenId);

    bytes25 before = positionInfoPoolIdCVL(tokenId);

    f(e, args);

    bytes25 after = positionInfoPoolIdCVL(tokenId);

    assert(before != to_bytes25(0) => (
        // Unchanged
        before == after 
        // Position was cleared
        || IS_EMPTY_POSITION_INFO(tokenId)
    ));
}

// The poolKey associated with a poolId remains constant once set
rule poolKeyImmutability(env e, method f, calldataarg args, bytes25 poolId) {

    // PookKey has a valid structure (tick spacing != 0 etc)
    requireInvariant validPoolKeyStructure;      

    // poolKeys[poolId] is clear OR associated with a valid pool in PoolManager 
    requireInvariant poolKeyMatchesInitializedPoolInPoolManager(poolId);

    address currency0Before = ghostPoolKeysCurrency0[poolId];
    address currency1Before = ghostPoolKeysCurrency0[poolId];
    mathint feeBefore = ghostPoolKeysFee[poolId];
    mathint tickSpacingBefore = ghostPoolKeysTickSpacing[poolId];
    address hooksBefore = ghostPoolKeysHooks[poolId];

    f(e, args);

    address currency0After = ghostPoolKeysCurrency0[poolId];
    address currency1After = ghostPoolKeysCurrency0[poolId];
    mathint feeAfter = ghostPoolKeysFee[poolId];
    mathint tickSpacingAfter = ghostPoolKeysTickSpacing[poolId];
    address hooksAfter = ghostPoolKeysHooks[poolId];

    // If any field was set
    assert(currency0Before != 0 
    || currency1Before != 0 
    || feeBefore != 0 
    || tickSpacingBefore != 0 
    || hooksBefore != 0 => (
        // It cannot be cleared
        currency0Before == currency0After 
        && currency1Before == currency1After
        && feeBefore == feeAfter
        && tickSpacingBefore == tickSpacingAfter
        && hooksBefore == hooksAfter
    ));
}

// A subscriber for a tokenId can only be set to a non-zero address once or unset to zero
rule subscriberImmutability(env e, method f, calldataarg args, uint256 tokenId) {

    address before = ghostNotifierSubscriber[tokenId];

    f(e, args);

    address after = ghostNotifierSubscriber[tokenId];

    assert(before != after => (
        before == 0 || after == 0
    ));
}

// Once a nonce is set (used), it cannot be cleared
rule noncePermanence(env e, method f, calldataarg args, address owner, uint256 word) {

    mathint before = ghostNonces[owner][word];

    f(e, args);

    mathint after = ghostNonces[owner][word];

    assert(before != 0 => after != 0);
}

//
// State transition
// 

// nextTokenId updated if and only if a new token is minted
rule nextTokenIdSyncWithMint(env e, method f, calldataarg args) {

    mathint nextTokenIdBefore = ghostNextTokenId;

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerTokenId(e, nextTokenIdBefore);

    address ownerBefore = ghostERC721OwnerOf[nextTokenIdBefore];

    f(e, args);

    mathint nextTokenIdAfter = ghostNextTokenId;
    address ownerAfter = ghostERC721OwnerOf[nextTokenIdBefore];

    // next token increased <=> new token minted
    assert(nextTokenIdBefore != nextTokenIdAfter <=> (ownerBefore == 0 && ownerAfter != 0));
}

// A new token is minted if and only if a new position is created, and burned when position is cleared
rule tokenMintBurnPositionSync(env e, method f, calldataarg args) {

    mathint tokenId = ghostNextTokenId;

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerTokenId(e, tokenId);

    uint256 positionBefore = ghostPositionInfo[tokenId];
    address ownerBefore = ghostERC721OwnerOf[tokenId];

    f(e, args);

    bool positionWasChanged = positionBefore != ghostPositionInfo[tokenId];
    address ownerAfter = ghostERC721OwnerOf[tokenId];

    // mint <=> create position info
    assert((positionBefore == EMPTY_POSITION_INFO() && positionWasChanged) <=> (ownerBefore == 0 && ownerAfter != 0));

    // burn <=> clear position info
    assert((positionBefore != EMPTY_POSITION_INFO() && positionWasChanged) <=> (ownerBefore != 0 && ownerAfter == 0));
}

// Minting increase position liquidity while burning decreases position liquidity in PoolManager
rule liquidityChangeOnMintBurn(env e, method f, calldataarg args, mathint tokenId) {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerTokenId(e, tokenId);

    // Pool Id in PoolManager
    bytes32 poolId = poolKeyVariablesToIdCVL(
        ghostPoolKeysCurrency0[positionInfoPoolIdCVL(tokenId)],
        ghostPoolKeysCurrency1[positionInfoPoolIdCVL(tokenId)],
        ghostPoolKeysFee[positionInfoPoolIdCVL(tokenId)],
        ghostPoolKeysTickSpacing[positionInfoPoolIdCVL(tokenId)],
        ghostPoolKeysHooks[positionInfoPoolIdCVL(tokenId)]
    );

    // Position Id in PoolManager
    bytes32 positionId = calculatePositionKeyCVL(
        _PositionManager, 
        positionInfoTickLowerCVL(tokenId), 
        positionInfoTickUpperCVL(tokenId), 
        to_bytes32(require_uint256(tokenId))
        );

    address ownerBefore = ghostERC721OwnerOf[tokenId];
    mathint poolsPositionsLiquidityBefore = ghostPoolsPositionsLiquidity[poolId][positionId];

    f(e, args);

    address ownerAfter = ghostERC721OwnerOf[tokenId];
    mathint poolsPositionsLiquidityAfter = ghostPoolsPositionsLiquidity[poolId][positionId];

    // mint => increases liquidity
    assert((ownerBefore == 0 && ownerAfter != 0) => poolsPositionsLiquidityAfter >= poolsPositionsLiquidityBefore);

    // burn => decreases liquidity
    assert((ownerBefore != 0 && ownerAfter == 0) => poolsPositionsLiquidityBefore >= poolsPositionsLiquidityAfter);
}

//
// Unit Tests
//

// Any valid nonce can be used once
rule nonceUniqueUsage(env e, uint256 nonce) {

    // Bypass revert when msg.sender doesn't have enough native tokens
    require(e.msg.value == 0);

    // Clear all nonces 
    require(forall address owner. forall uint256 word. ghostNonces[owner][word] == 0);

    revokeNonce@withrevert(e, nonce);
    bool reverted = lastReverted;

    // Must executes successfully
    assert(!reverted);

    // Once must set
    satisfy(forall address owner. forall uint256 word. ghostNonces[owner][word] != 0);
}

// A nonce cannot be successfully used more than once
rule nonceSingleUse(env e, uint256 nonce) {

    // Clear all nonces 
    require(forall address owner. forall uint256 word. ghostNonces[owner][word] == 0);

    revokeNonce@withrevert(e, nonce);
    bool reverted1 = lastReverted;

    revokeNonce@withrevert(e, nonce);
    bool reverted2 = lastReverted;

    assert(!reverted1 => reverted2);
}
