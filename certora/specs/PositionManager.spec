import "./setup/PositionManagerBase.spec";
import "./Common.spec";

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

definition IS_MINT_POSITION_FUNCTION(method f) returns bool 
    = f.selector == sig:mintPosition(PoolManager.PoolKey, int24, int24, uint256, uint128, uint128, address, bytes).selector;

definition IS_BURN_POSITION_FUNCTION(method f) returns bool 
    = f.selector == sig:burnPosition(uint256, uint128, uint128, bytes).selector;

definition IS_SUBSCRIBE_FUNCTION(method f) returns bool 
    = f.selector == sig:subscribe(uint256, address, bytes).selector;

definition IS_UNSUBSCRIBE_FUNCTION(method f) returns bool 
    = f.selector == sig:unsubscribe(uint256).selector;

definition IS_SWEEP_FUNCTION(method f) returns bool 
    = f.selector == sig:sweep(PoolManager.Currency, address).selector;

//
// Sanity
//

// Check if there is at least one path to execute an external function without a revert 
use builtin rule sanity filtered { f -> f.contract == currentContract }

//
// Common
//

// Any chance that non-view function modifies state (valuable when `memory` keyword mistakenly 
//  was used instead of `storage` in setters among with event emitting)
use rule chanceNonViewFunctionModifiesState;

//
// Valid State
//

// requireValidState* functions can be used to assume a valid state in other properties

function requireValidStatePositionManagerERC721(env e) {
    requireInvariant noApprovalsForZeroAddress(e);
    requireInvariant zeroAddressHasNoBalance(e);
    requireInvariant getApprovedForExistingTokensOnly(e);
}

function requireValidStatePositionManagerEnv(env e) {

    // Assume locker with sender in isNotLocked modifier
    require(ghostLocker == e.msg.sender);

    requireValidEnvCVL(e);
    requireValidStatePositionManagerERC721(e);

    requireInvariant validNextTokenId;
    requireInvariant validPoolKeyStructure;
    requireInvariant subscriberTokenIdConsistency;

    requireInvariant noInfoForInvalidTokenIds(e);
}

function requireValidStatePositionManagerTokenId(env e, mathint tokenId) {

    requireValidStatePositionManagerEnv(e);

    requireInvariant activePositionMatchesPoolKey(e, tokenId);
    requireInvariant activePositionMatchesInitializedPoolInPoolManager(e, tokenId);
    requireInvariant activePositionsMatchesToken(e, tokenId);
    requireInvariant subscriberAddressSetWithFlag(e, tokenId);
    requireInvariant subscribersForExistingTokensOnly(e, tokenId);
    requireInvariant validPositionTicks(e, tokenId);
    requireInvariant tokenPositionIdAlignment(e, tokenId);
    requireInvariant notifierCallbacksUntouchedIfNoSubscriber(e, tokenId);
}

function requireValidStatePositionManagerPoolId(bytes25 poolId) {
    requireInvariant poolKeyMatchesInitializedPoolInPoolManager(poolId);
}

// The next token ID MUST always be greater than or equal to 1
strong invariant validNextTokenId() 
    ghostNextTokenId >= 1;

// Position information and token MUST NOT exist for token ID 0 or any future token IDs
strong invariant noInfoForInvalidTokenIds(env e)
    forall mathint tokenId. tokenId == 0 || tokenId >= ghostNextTokenId 
        => IS_EMPTY_POSITION_INFO(tokenId) && ghostERC721OwnerOf[tokenId] == 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerERC721(e);
        }
    }

// Active position ticks MUST be within the valid range defined by TickMath
strong invariant validPositionTicks(env e, mathint tokenId)
    // Position not empty
    !IS_EMPTY_POSITION_INFO(tokenId) => (
        positionInfoTickLowerCVL(tokenId) >= MIN_TICK() && positionInfoTickUpperCVL(tokenId) <= MAX_TICK() 
        && positionInfoTickLowerCVL(tokenId) < positionInfoTickUpperCVL(tokenId)
    ) {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerERC721(e);
            requireInvariant activePositionsMatchesToken(e, tokenId);
        }
    }

// Active position MUST correspond minted token and vice versa
strong invariant activePositionsMatchesToken(env e, mathint tokenId)
    // Token exists <=> Position exists
    ghostERC721OwnerOf[tokenId] != 0 <=> !IS_EMPTY_POSITION_INFO(tokenId) {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerERC721(e);
            requireInvariant validPositionTicks(e, tokenId);
        }
    }

// Active position MUST correspond to valid pool key
strong invariant activePositionMatchesPoolKey(env e, mathint tokenId)
    // Position is not empty
    !IS_EMPTY_POSITION_INFO(tokenId) 
        // Pool key id from position info == pool key id calculated from poolKeys structure params
        => positionInfoPoolIdCVL(tokenId) == poolKeyVariablesToShortIdCVL(
                ghostPoolKeysCurrency0[positionInfoPoolIdCVL(tokenId)],
                ghostPoolKeysCurrency1[positionInfoPoolIdCVL(tokenId)],
                ghostPoolKeysFee[positionInfoPoolIdCVL(tokenId)],
                ghostPoolKeysTickSpacing[positionInfoPoolIdCVL(tokenId)],
                ghostPoolKeysHooks[positionInfoPoolIdCVL(tokenId)]
            ) {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerTokenId(e, tokenId);   
        }
        preserved mintPosition(
            PoolManager.PoolKey poolKey, 
            int24 tickLower, 
            int24 tickUpper, 
            uint256 liquidity, 
            uint128 amount0Max,
            uint128 amount1Max,
            address owner,
            bytes hookData
        ) with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerTokenId(e, tokenId);    
            // Assume a new key passed 
            require(forall bytes25 poolId. ghostPoolKeysTickSpacing[poolId] == 0);       
        }
    }

// Active position must correspond to a initialized pool in PoolManager
strong invariant activePositionMatchesInitializedPoolInPoolManager(env e, mathint tokenId)
    // Active position
    !IS_EMPTY_POSITION_INFO(tokenId)
        // PoolManager[poolId].slot0.sqrtPriceX96 != 0 means the pool is initialized
        => poolManagerSlot0SqrtPriceX96ByTokenIdCVL(tokenId) != 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerTokenId(e, tokenId);
        }
        preserved mintPosition(
            PoolManager.PoolKey poolKey, 
            int24 tickLower, 
            int24 tickUpper, 
            uint256 liquidity, 
            uint128 amount0Max,
            uint128 amount1Max,
            address owner,
            bytes hookData
        ) with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerTokenId(e, tokenId);    
            // Assume a new key passed 
            require(forall bytes25 poolId. ghostPoolKeysTickSpacing[poolId] == 0);       
        }
    } 

// Touched pool key must correspond to a initialized pool in PoolManager
strong invariant poolKeyMatchesInitializedPoolInPoolManager(bytes25 poolId)
    // On UniswapV4, the minimum tick spacing is 1, which means that if the tick spacing is 0, 
    //  the pool key has not been set.
    ghostPoolKeysTickSpacing[poolId] != 0
        // PoolManager[poolId].slot0.sqrtPriceX96 != 0 means the pool is initialized
        => poolManagerSlot0SqrtPriceX96ByShortPoolIdCVL(poolId) != 0 {
        preserved {
            requireInvariant validPoolKeyStructure;
        }
    }

// All poolKey fields must contain valid and consistent values
strong invariant validPoolKeyStructure()
    // On UniswapV4, the minimum tick spacing is 1, which means that if the tick spacing is 0, 
    //  the pool key has not been set.
    forall bytes25 poolId. ghostPoolKeysTickSpacing[poolId] != 0
        ? (// PoolManager doesn't accept invalid key params
            ghostPoolKeysCurrency0[poolId] < ghostPoolKeysCurrency1[poolId]
            && ghostPoolKeysTickSpacing[poolId] >= MIN_TICK_SPACING() 
            && ghostPoolKeysTickSpacing[poolId] <= MAX_TICK_SPACING()
            && (ghostPoolKeysFee[poolId] <= MAX_LP_FEE() || ghostPoolKeysFee[poolId] == DYNAMIC_FEE_FLAG())
        ) : (
            ghostPoolKeysCurrency0[poolId] == 0
            && ghostPoolKeysCurrency1[poolId] == 0
            && ghostPoolKeysFee[poolId] == 0
            && ghostPoolKeysHooks[poolId] == 0
        );

// The token ID in PositionManager always matches the position ID in PoolManager
strong invariant tokenPositionIdAlignment(env e, mathint tokenId) 
    poolManagerPoolPositionLiquidity(tokenId) != 0 => tokenId != 0 
    filtered { 
        // Exclude minting function as a token id doesn't exist at this time
        f -> IS_MINT_POSITION_FUNCTION(f) == false 
        } { 
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerTokenId(e, tokenId);
        }
    }

// The subscriber token ID always matches the token ID passed to notifier callbacks
strong invariant subscriberTokenIdConsistency()
    forall mathint tokenId. ghostNotifierSubscriber[tokenId] != 0
        => tokenId == ghostNotifierTokenId[ghostNotifierSubscriber[tokenId]] 
    filtered { 
        // Assume subscriber mapping was not changed 
        f -> IS_SUBSCRIBE_FUNCTION(f) == false
    }

// Notifier callbacks are not called if nobody is subscribed to the token
strong invariant notifierCallbacksUntouchedIfNoSubscriber(env e, mathint tokenId) 
    positionInfoHasSubscriberCVL(tokenId) == false => (
        ghostNotifierTokenId[ghostNotifierSubscriber[tokenId]] == 0 
        && ghostNotifierLiquidityChange[ghostNotifierSubscriber[tokenId]] == 0
        && ghostNotifierFeesAccrued[ghostNotifierSubscriber[tokenId]] == 0
        && ghostNotifierPreviousOwner[ghostNotifierSubscriber[tokenId]] == 0
        && ghostNotifierNewOwner[ghostNotifierSubscriber[tokenId]] == 0
    ) filtered { 
        // These mock contract ghost mappings do not clear on unsubscribe or token burn
        f -> IS_BURN_POSITION_FUNCTION(f) == false && IS_UNSUBSCRIBE_FUNCTION(f) == false
    } {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerTokenId(e, tokenId);
        }
    }

// A subscription flag MUST be set when a valid subscriber address is present and vice versa
strong invariant subscriberAddressSetWithFlag(env e, mathint tokenId)
    positionInfoHasSubscriberCVL(tokenId) <=> ghostNotifierSubscriber[tokenId] != 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireInvariant activePositionsMatchesToken(e, tokenId);
        }
    }

// Subscribers MUST only be set for existing token IDs
strong invariant subscribersForExistingTokensOnly(env e, mathint tokenId)
    ghostNotifierSubscriber[tokenId] != 0 
        => ghostERC721OwnerOf[tokenId] != 0 && !IS_EMPTY_POSITION_INFO(tokenId) {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireInvariant subscriberAddressSetWithFlag(e, tokenId);
        }
    }

// Approvals for the zero address as owner are not allowed
strong invariant noApprovalsForZeroAddress(env e)
    forall address spender. ghostERC721IsApprovedForAll[0][spender] == false {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerERC721(e);
        }
    }

// The zero address MUST NOT have any token balance
strong invariant zeroAddressHasNoBalance(env e)
    ghostERC721BalanceOf[0] == 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerERC721(e);        
        }
    }

// Approved tokens MUST always correspond to existing token IDs
strong invariant getApprovedForExistingTokensOnly(env e)
    forall mathint tokenId. ghostERC721GetApproved[tokenId] != 0 
        => ghostERC721OwnerOf[tokenId] != 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerERC721(e);
        }
    }

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
    satisfy(nextTokenIdBefore != nextTokenIdAfter => (ownerBefore == 0 && ownerAfter != 0));
    satisfy((ownerBefore == 0 && ownerAfter != 0) => nextTokenIdBefore != nextTokenIdAfter);
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
    satisfy((positionBefore == EMPTY_POSITION_INFO() && positionWasChanged) => (ownerBefore == 0 && ownerAfter != 0));
    satisfy((ownerBefore == 0 && ownerAfter != 0) => (positionBefore == EMPTY_POSITION_INFO() && positionWasChanged));

    // burn <=> clear position info
    assert((positionBefore != EMPTY_POSITION_INFO() && positionWasChanged) <=> (ownerBefore != 0 && ownerAfter == 0));
    satisfy((positionBefore != EMPTY_POSITION_INFO() && positionWasChanged) => (ownerBefore != 0 && ownerAfter == 0));
    satisfy((ownerBefore != 0 && ownerAfter == 0) => (positionBefore != EMPTY_POSITION_INFO() && positionWasChanged));
}

// Minting increase position liquidity while burning decreases position liquidity in PoolManager
rule liquidityChangeOnMintBurn(env e, method f, calldataarg args, mathint tokenId) {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerTokenId(e, tokenId);

    // Pool Id in PoolManager
    bytes32 poolId = poolMangerPoolIdCVL(tokenId);

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
    satisfy((ownerBefore == 0 && ownerAfter != 0) => poolsPositionsLiquidityAfter >= poolsPositionsLiquidityBefore);

    // burn => decreases liquidity
    assert((ownerBefore != 0 && ownerAfter == 0) => poolsPositionsLiquidityBefore >= poolsPositionsLiquidityAfter);
    satisfy((ownerBefore != 0 && ownerAfter == 0) => poolsPositionsLiquidityBefore >= poolsPositionsLiquidityAfter);
}

// The poolKey associated with a poolId remains constant once set, and could be set only when tickspacing is zero
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
    assert(currency0Before != 0 || currency1Before != 0 || feeBefore != 0 || tickSpacingBefore != 0 || hooksBefore != 0 => (
        // It cannot be cleared
        currency0Before == currency0After 
        && currency1Before == currency1After
        && feeBefore == feeAfter
        && tickSpacingBefore == tickSpacingAfter
        && hooksBefore == hooksAfter
    ));

    // If any field was updated, tickspacing must be zero before
    assert(currency0Before != currency0After 
        || currency1Before != currency1After
        || feeBefore != feeAfter
        || tickSpacingBefore != tickSpacingAfter 
        || hooksBefore != hooksAfter => (
            tickSpacingBefore == 0
    ));

    // Find at least one path when if any field was updated, tickspacing will be zero before
    satisfy(currency0Before != currency0After 
        || currency1Before != currency1After
        || feeBefore != feeAfter
        || tickSpacingBefore != tickSpacingAfter 
        || hooksBefore != hooksAfter => (
            // When tickspacing was zero
            tickSpacingBefore == 0
    ));

    // Find at least one path when if tick staping was changed, any field could be changed as well
    satisfy(tickSpacingBefore != tickSpacingAfter => (
        currency0Before != currency0After 
        || currency1Before != currency1After
        || feeBefore != feeAfter
        || tickSpacingBefore != tickSpacingAfter 
        || hooksBefore != hooksAfter
    ));    
}

// A pool key can only be added when a new token is minted
rule poolKeyAdditionOnlyWithNewToken(env e, method f, calldataarg args, mathint tokenId) {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerTokenId(e, tokenId);

    // Pool Id in position info
    bytes25 poolId = positionInfoPoolIdCVL(tokenId);
    requireValidStatePositionManagerPoolId(poolId);

    address ownerBefore = ghostERC721OwnerOf[tokenId];

    address currency0Before = ghostPoolKeysCurrency0[poolId];
    address currency1Before = ghostPoolKeysCurrency0[poolId];
    mathint feeBefore = ghostPoolKeysFee[poolId];
    mathint tickSpacingBefore = ghostPoolKeysTickSpacing[poolId];
    address hooksBefore = ghostPoolKeysHooks[poolId];

    f(e, args);

    address ownerAfter = ghostERC721OwnerOf[tokenId];

    address currency0After = ghostPoolKeysCurrency0[poolId];
    address currency1After = ghostPoolKeysCurrency0[poolId];
    mathint feeAfter = ghostPoolKeysFee[poolId];
    mathint tickSpacingAfter = ghostPoolKeysTickSpacing[poolId];
    address hooksAfter = ghostPoolKeysHooks[poolId];

    assert((currency0Before != currency0After 
        || currency1Before != currency1After
        || feeBefore != feeAfter
        || tickSpacingBefore != tickSpacingAfter
        || hooksBefore != hooksAfter
        // Token is minted
        ) => (ownerBefore == 0 && ownerBefore == ownerAfter)
    );

    satisfy((currency0Before != currency0After 
        || currency1Before != currency1After
        || feeBefore != feeAfter
        || tickSpacingBefore != tickSpacingAfter
        || hooksBefore != hooksAfter
        // Token is minted
        ) => (ownerBefore == 0 && ownerBefore == ownerAfter)
    );
}

// Notifier callbacks execute only when token owner or liquidity change
rule notifierCallbacksOnlyOnOwnerOrLiquidityChange(env e, method f, calldataarg args, mathint tokenId) {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerTokenId(e, tokenId);

    bytes32 poolId = poolMangerPoolIdCVL(tokenId);

    mathint poolsLiquidityBefore = ghostPoolsLiquidity[poolId];

    address subscriberBefore = ghostNotifierSubscriber[tokenId];
    mathint tokenIdBefore = ghostNotifierTokenId[subscriberBefore];
    int256 liquidityChangeBefore = ghostNotifierLiquidityChange[subscriberBefore];
    int256 feesAccruedBefore = ghostNotifierFeesAccrued[subscriberBefore];
    address previousOwnerBefore = ghostNotifierPreviousOwner[subscriberBefore];
    address newOwnerBefore = ghostNotifierNewOwner[subscriberBefore];

    address ownerBefore = ghostERC721OwnerOf[tokenId];

    f(e, args);

    mathint poolsLiquidityAfter = ghostPoolsLiquidity[poolId];

    address subscriberAfter = ghostNotifierSubscriber[tokenId];
    mathint tokenIdAfter = ghostNotifierTokenId[subscriberAfter];
    int256 liquidityChangeAfter = ghostNotifierLiquidityChange[subscriberAfter];
    int256 feesAccruedAfter = ghostNotifierFeesAccrued[subscriberAfter];
    address previousOwnerAfter = ghostNotifierPreviousOwner[subscriberAfter];
    address newOwnerAfter = ghostNotifierNewOwner[subscriberAfter];

    address ownerAfter = ghostERC721OwnerOf[tokenId];

    // Token transfer
    assert((subscriberBefore == subscriberAfter && positionInfoHasSubscriberCVL(tokenId)) => (
        ownerBefore != ownerAfter <=> (previousOwnerBefore != previousOwnerAfter && newOwnerBefore != newOwnerAfter)
    ));
    satisfy((subscriberBefore == subscriberAfter && positionInfoHasSubscriberCVL(tokenId)) => (
        ownerBefore != ownerAfter => (previousOwnerBefore != previousOwnerAfter && newOwnerBefore != newOwnerAfter)
    ));

    // Modify liquidity
    assert((subscriberBefore == subscriberAfter && positionInfoHasSubscriberCVL(tokenId)) => (
        poolsLiquidityBefore != poolsLiquidityAfter <=> liquidityChangeBefore != liquidityChangeAfter
    ));
    satisfy((subscriberBefore == subscriberAfter && positionInfoHasSubscriberCVL(tokenId)) => (
        poolsLiquidityBefore != poolsLiquidityAfter => liquidityChangeBefore != liquidityChangeAfter
    ));

    // Token transfer
    assert((subscriberBefore == subscriberAfter && positionInfoHasSubscriberCVL(tokenId) && ownerBefore != ownerAfter) 
       => (poolsLiquidityBefore == poolsLiquidityAfter
        && liquidityChangeBefore == liquidityChangeAfter
        && feesAccruedBefore == feesAccruedAfter
        && previousOwnerAfter == ownerBefore
        && newOwnerAfter == ownerAfter
        ));
    satisfy((subscriberBefore == subscriberAfter && positionInfoHasSubscriberCVL(tokenId) && ownerBefore != ownerAfter) 
       => (poolsLiquidityBefore == poolsLiquidityAfter
        && liquidityChangeBefore == liquidityChangeAfter
        && feesAccruedBefore == feesAccruedAfter
        && previousOwnerAfter == ownerBefore
        && newOwnerAfter == ownerAfter
        ));

    // Modify liquidity
    assert((subscriberBefore == subscriberAfter && positionInfoHasSubscriberCVL(tokenId) && poolsLiquidityBefore != poolsLiquidityAfter) 
        => ((liquidityChangeAfter < 0 
                ? liquidityChangeAfter == poolsLiquidityBefore - poolsLiquidityAfter 
                : liquidityChangeAfter == poolsLiquidityAfter - poolsLiquidityBefore
            ) && previousOwnerBefore == previousOwnerAfter
            && newOwnerBefore == newOwnerAfter
        ));
    satisfy((subscriberBefore == subscriberAfter && positionInfoHasSubscriberCVL(tokenId) && poolsLiquidityBefore != poolsLiquidityAfter) 
        => ((liquidityChangeAfter < 0 
                ? liquidityChangeAfter == poolsLiquidityBefore - poolsLiquidityAfter 
                : liquidityChangeAfter == poolsLiquidityAfter - poolsLiquidityBefore
            ) && previousOwnerBefore == previousOwnerAfter
            && newOwnerBefore == newOwnerAfter
        ));
}

// Initiates tokens receive from pool manager only
rule initiatesTokensReceiveFromPoolManagerOnly(env e, method f, calldataarg args) {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerEnv(e);

    // Assume only ERC20B token is available
    require(forall address token. forall address user. token != ghostERC20B => ghostERC20Balances[token][user] == 0);

    mathint posBefore = ghostERC20Balances[ghostERC20B][_PositionManager];
    mathint pmBefore = ghostERC20Balances[ghostERC20B][_PoolManager];

    f(e, args);

    mathint posAfter = ghostERC20Balances[ghostERC20B][_PositionManager];
    mathint pmAfter = ghostERC20Balances[ghostERC20B][_PoolManager];

    assert(posAfter > posBefore => (posAfter - posBefore == pmBefore - pmAfter));
    satisfy(posAfter > posBefore => (posAfter - posBefore == pmBefore - pmAfter));
}

// Never receive native tokens from pool manager
rule neverReceiveNativeTokensFromPoolManager(env e, method f, calldataarg args) {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerEnv(e);

    // Assume native tokens were not sent by user
    require(e.msg.value == 0);

    mathint posNativeBefore = nativeBalances[_PositionManager];
    mathint pmNativeBefore = nativeBalances[_PoolManager];

    f(e, args);

    mathint posNativeAfter = nativeBalances[_PositionManager];
    mathint pmNativeAfter = nativeBalances[_PoolManager];

    assert(posNativeAfter > posNativeBefore => pmNativeBefore == pmNativeAfter);
}

// Pair of tokens settles from locker only and in full amount owed by this contract
rule pairOfTokensSettlesFromLockerOnlyAndInFullAmount(env e, method f, calldataarg args) {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerEnv(e);

    // Assume only native, ERC20A and ERC20B currencies are available

    mathint aFullDebt = getFullDebt(e, _HelperCVL.toCurrency(ghostERC20A)); 
    mathint bFullDebt = getFullDebt(e, _HelperCVL.toCurrency(ghostERC20B)); 
    mathint nativeFullDebt = getFullDebt(e, _HelperCVL.toCurrency(NATIVE_CURRENCY())); 

    mathint aLockerBefore = ghostERC20Balances[ghostERC20A][ghostLocker];
    mathint bLockerBefore = ghostERC20Balances[ghostERC20B][ghostLocker];
    mathint nativeLockerBefore = nativeBalances[ghostLocker];

    mathint aPmBefore = ghostERC20Balances[ghostERC20A][_PoolManager];
    mathint bPmBefore = ghostERC20Balances[ghostERC20B][_PoolManager];
    mathint nativePmBefore = nativeBalances[_PoolManager];

    f(e, args);

    mathint aLockerAfter = ghostERC20Balances[ghostERC20A][ghostLocker];
    mathint bLockerAfter = ghostERC20Balances[ghostERC20B][ghostLocker];
    mathint nativeLockerAfter = nativeBalances[ghostLocker];

    mathint aPmAfter = ghostERC20Balances[ghostERC20A][_PoolManager];
    mathint bPmAfter = ghostERC20Balances[ghostERC20B][_PoolManager];
    mathint nativePmAfter = nativeBalances[_PoolManager];

    bool aGet = aPmAfter > aPmBefore;
    bool bGet = bPmAfter > bPmBefore;
    bool nativeGet = nativePmAfter > nativePmBefore;

    mathint aDelta = aGet ? aPmAfter - aPmBefore : 0;
    mathint bDelta = bGet ? bPmAfter - bPmBefore : 0;
    mathint nativeDelta = nativeGet ? nativePmAfter - nativePmBefore : 0;

    // PoolManager receives amounts of two tokens
    bool anyTwoGet = aGet && bGet || aGet && nativeGet && bGet && nativeGet;

    assert(anyTwoGet => (
        (aGet => ((aLockerBefore - aLockerAfter == aDelta) && (aDelta == aFullDebt)))
        && (bGet => ((bLockerBefore - bLockerAfter == bDelta) && bDelta == bFullDebt))
        && (nativeGet => ((nativeLockerBefore - nativeLockerAfter == nativeDelta) && nativeDelta == nativeFullDebt))
    ));
    satisfy(anyTwoGet => (
        (aGet => ((aLockerBefore - aLockerAfter == aDelta) && (aDelta == aFullDebt)))
        && (bGet => ((bLockerBefore - bLockerAfter == bDelta) && bDelta == bFullDebt))
        && (nativeGet => ((nativeLockerBefore - nativeLockerAfter == nativeDelta) && nativeDelta == nativeFullDebt))
    ));
}

//
// High-Level
//

// Only the owner or approved addresses can modify liquidity
rule onlyTokenOwnerOrApprovedCanModifyLiquidity(env e, method f, calldataarg args, mathint tokenId) {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerTokenId(e, tokenId);

    address owner = ghostERC721OwnerOf[tokenId];
    address spender = ghostLocker;
    address approved = ghostERC721GetApproved[tokenId];
    bool approvedForAll = ghostERC721IsApprovedForAll[owner][spender];

    bytes32 poolId = poolMangerPoolIdCVL(tokenId);
    bytes32 positionId = calculatePositionKeyCVL(
        _PositionManager, 
        positionInfoTickLowerCVL(tokenId), 
        positionInfoTickUpperCVL(tokenId), 
        to_bytes32(require_uint256(tokenId))
        );

    mathint poolsPositionsLiquidityBefore = ghostPoolsPositionsLiquidity[poolId][positionId];

    f(e, args);

    mathint poolsPositionsLiquidityAfter = ghostPoolsPositionsLiquidity[poolId][positionId];

    assert((poolsPositionsLiquidityBefore != poolsPositionsLiquidityAfter) && owner != 0
        => (spender == owner || spender == approved || approvedForAll)
    );

    satisfy(poolsPositionsLiquidityAfter != poolsPositionsLiquidityAfter && owner != 0
        <=> (spender == owner || spender == approved || approvedForAll)
    );
}

// Only the owner or approved addresses can transfer token
rule onlyTokenOwnerOrApprovedCanTransferToken(env e, method f, calldataarg args, mathint tokenId) {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerTokenId(e, tokenId);

    bytes32 poolId = poolMangerPoolIdCVL(tokenId);

    address ownerBefore = ghostERC721OwnerOf[tokenId];

    address spender = e.msg.sender;
    address approved = ghostERC721GetApproved[tokenId];
    bool approvedForAll = ghostERC721IsApprovedForAll[ownerBefore][spender];

    f(e, args);

    address ownerAfter = ghostERC721OwnerOf[tokenId];

    assert((ownerBefore != ownerAfter) && ownerBefore != 0 && ownerAfter != 0
        => (spender == ownerBefore || spender == approved || approvedForAll)
    );

    satisfy((ownerBefore != ownerAfter) && ownerBefore != 0 && ownerAfter != 0
        <=> (spender == ownerBefore || spender == approved || approvedForAll)
    );
}

// Sweep is the only way to transfer tokens outside except PoolManager
rule sweepOnlyWayToTransferTokensOutsideExceptPoolManager(env e, method f, calldataarg args)
    // Skip sweep() call
    filtered { f -> IS_SWEEP_FUNCTION(f) == false } {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerEnv(e);

    // Assume only ERC20B token is available
    require(forall address token. forall address user. token != ghostERC20B => ghostERC20Balances[token][user] == 0);
    
    // Assume native tokens already in PositionManager
    require(e.msg.value == 0);

    mathint posBefore = ghostERC20Balances[ghostERC20B][_PositionManager];
    mathint pmBefore = ghostERC20Balances[ghostERC20B][_PoolManager];

    mathint posNativeBefore = nativeBalances[_PositionManager];
    mathint pmNativeBefore = nativeBalances[_PoolManager];

    f(e, args);

    mathint posAfter = ghostERC20Balances[ghostERC20B][_PositionManager];
    mathint pmAfter = ghostERC20Balances[ghostERC20B][_PoolManager];

    mathint posNativeAfter = nativeBalances[_PositionManager];
    mathint pmNativeAfter = nativeBalances[_PoolManager];

    // If tokens sent out from PositionManager, only PoolManager can receive them
    assert(posBefore > posAfter => (pmAfter - pmBefore == posBefore - posAfter));
    satisfy(posBefore > posAfter => (pmAfter - pmBefore == posBefore - posAfter));

    // If NATIVE tokens sent out from PositionManager, only PoolManager can receive them
    assert(posNativeBefore > posNativeAfter => (pmNativeAfter - pmNativeBefore == posNativeBefore - posNativeAfter));
    satisfy(posNativeBefore > posNativeAfter => (pmNativeAfter - pmNativeBefore == posNativeBefore - posNativeAfter));
}

//
// Unit Tests
//

// Ensures currency delta is zero after calling closing position
rule zeroDeltaAfterClose(env e, address token) {
    
    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerEnv(e);

    close(e, _HelperCVL.toCurrency(token));

    mathint deltaAfter = ghostCurrencyDelta[token][_PositionManager];

    assert(deltaAfter == 0);
    satisfy(deltaAfter == 0);
}

// Ensures closing position affects the balance of the locker
rule closeAffectBalanceOfLocker(env e, address token) {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerEnv(e);

    // Assume native tokens were sent in function call
    require(nativeBalances[_PositionManager] == 0);

    int256 deltaBefore = ghostCurrencyDelta[token][_PositionManager];
    mathint balanceBefore = token == NATIVE_CURRENCY() ? nativeBalances[ghostLocker] : ghostERC20Balances[token][ghostLocker];

    close(e, _HelperCVL.toCurrency(token));

    mathint balanceAfter = token == NATIVE_CURRENCY() 
        // The rest of sent tokens can be sweeped back to locker
        ? nativeBalances[ghostLocker] + nativeBalances[_PositionManager]
        : ghostERC20Balances[token][ghostLocker]
        ;

    assert(deltaBefore < 0 ? balanceAfter < balanceBefore : balanceAfter >= balanceBefore);
    satisfy(deltaBefore < 0 ? balanceAfter < balanceBefore : balanceAfter >= balanceBefore);
}

// Sweep must output currency
rule sweepMustOutputCurrency(env e, address token, address to) {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerEnv(e);

    // Assume only ERC20B token or native currencies are available
    require(token == NATIVE_CURRENCY() || token == ghostERC20B);

    // Assume native tokens already in PositionManager
    require(e.msg.value == 0);

    mathint posBefore = ghostERC20Balances[ghostERC20B][_PositionManager];
    mathint toBefore = ghostERC20Balances[ghostERC20B][to];

    mathint posNativeBefore = nativeBalances[_PositionManager];
    mathint toNativeBefore = nativeBalances[to];

    sweep(e, _HelperCVL.toCurrency(token), to);

    mathint posAfter = ghostERC20Balances[ghostERC20B][_PositionManager];
    mathint toAfter = ghostERC20Balances[ghostERC20B][to];

    mathint posNativeAfter = nativeBalances[_PositionManager];
    mathint toNativeAfter = nativeBalances[to];

    // Tokens
    assert(toAfter - toBefore >= 0 => (toAfter - toBefore == posBefore - posAfter));
    satisfy(toAfter - toBefore >= 0 => (toAfter - toBefore == posBefore - posAfter));

    // Native
    assert(toNativeAfter >= toNativeBefore => (toNativeAfter - toNativeBefore == posNativeBefore - posNativeAfter));
    satisfy(toNativeAfter >= toNativeBefore => (toNativeAfter - toNativeBefore == posNativeBefore - posNativeAfter));
}

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
