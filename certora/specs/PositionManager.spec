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
use invariant ticksAlignWithSpacing;
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

// @todo nonces