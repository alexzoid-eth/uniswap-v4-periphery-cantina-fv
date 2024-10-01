import "./PositionManagerValidState.spec";

//
// Sanity
//

// Check if there is at least one path to execute an external function without a revert 
use builtin rule sanity filtered { f -> f.contract == currentContract }

// 
// Variables Transition
//

// PM-01 The nextTokenId value always increases monotonically
rule nextTokenIdMonotonicallyIncreasing(env e, method f, calldataarg args) {

    mathint before = ghostNextTokenId;

    f(e, args);

    mathint after = ghostNextTokenId;

    assert(before != after => after == before + 1);
}

// PM-02 The ticks in positionInfo remain constant for a given tokenId, otherwise been cleared
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

// PM-03 The poolId in positionInfo remains constant for a given tokenId, otherwise been cleared
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

// PM-04 A subscriber for a tokenId can only be set to a non-zero address once or unset to zero
rule subscriberImmutability(env e, method f, calldataarg args, uint256 tokenId) {

    address before = ghostNotifierSubscriber[tokenId];

    f(e, args);

    address after = ghostNotifierSubscriber[tokenId];

    assert(before != after => (
        before == 0 || after == 0
    ));
}

// PM-05 Once a nonce is set (used), it cannot be cleared
rule noncePermanence(env e, method f, calldataarg args, address owner, uint256 word) {

    mathint before = ghostNonces[owner][word];

    f(e, args);

    mathint after = ghostNonces[owner][word];

    assert(before != 0 => after != 0);
}

//
// State transition
// 

// PM-06 nextTokenId updated if and only if a new token is minted
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

// PM-07 A new token is minted if and only if a new position is created, and burned when position is cleared
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

// PM-08 Minting increase position liquidity while burning decreases position liquidity in PoolManager
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

// PM-09 The poolKey associated with a poolId remains constant once set, and could be set only when tickspacing is zero
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

// PM-10 A pool key can only be added when a new token is minted
rule poolKeyAdditionOnlyWithNewToken(env e, method f, calldataarg args, mathint tokenId) {

    // Assume PositionManager valid state invariants 
    require(tokenId == ghostNextTokenId);
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
        ) => (ownerBefore == 0 && ownerBefore != ownerAfter)
    );

    satisfy((currency0Before != currency0After 
        || currency1Before != currency1After
        || feeBefore != feeAfter
        || tickSpacingBefore != tickSpacingAfter
        || hooksBefore != hooksAfter
        // Token is minted
        ) => (ownerBefore == 0 && ownerBefore != ownerAfter)
    );
}

// PM-11 Notifier callbacks execute only when token owner or liquidity change
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

    // Initialize ghosts in notifier mocks with zeros 
    require(subscriberBefore == 0 
        && tokenIdBefore == 0 
        && liquidityChangeBefore == 0 
        && feesAccruedBefore == 0 
        && previousOwnerBefore == 0 
        && newOwnerBefore == 0
        );
    
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

    // Modify liquidity (1 wei rounding is accepted)
    assert((subscriberBefore == subscriberAfter && positionInfoHasSubscriberCVL(tokenId) && liquidityChangeAfter != -1) => (
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

// PM-12 Initiates tokens receive from pool manager only
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

// PM-13 Never receive native tokens from pool manager
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

// PM-14 Pair of tokens settles from locker only and in full amount owed by this contract
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

// PM-15 Only the owner or approved addresses can modify liquidity
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

// PM-16 Only the owner or approved addresses can transfer token
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

// PM-17 Sweep is the only way to transfer tokens outside except PoolManager
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

// PM-18 Ensures closing position affects the balance of the locker
rule closeAffectBalanceOfLocker(env e, address token) {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerEnv(e);

    // Assume native tokens were sent in function call
    require(nativeBalances[_PositionManager] == 0);

    int256 deltaBefore = ghostCurrencyDelta[_PositionManager][token];

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

// PM-19 Sweep must output currency
rule sweepMustOutputCurrency(env e, address token, address to) {

    // Assume PositionManager valid state invariants 
    requireValidStatePositionManagerEnv(e);

    // Assume only ERC20B token or native currencies are available
    require(token == NATIVE_CURRENCY() || token == ghostERC20B);

    // Assume native tokens already in PositionManager
    require(e.msg.value == 0);

    // _mapRecipient()
    require(to == 1 => to == e.msg.sender);

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

// PM-20 Any valid nonce can be used once
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

// PM-21 A nonce cannot be successfully used more than once
rule nonceSingleUse(env e, uint256 nonce) {

    // Clear all nonces 
    require(forall address owner. forall uint256 word. ghostNonces[owner][word] == 0);

    revokeNonce@withrevert(e, nonce);
    bool reverted1 = lastReverted;

    revokeNonce@withrevert(e, nonce);
    bool reverted2 = lastReverted;

    assert(!reverted1 => reverted2);
}
