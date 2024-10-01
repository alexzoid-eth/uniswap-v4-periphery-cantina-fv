import "./setup/PositionManagerBase.spec";

methods {

    // Not needed as _handleAction is no-op and summarizing unlock here would have no effect
    function modifyLiquidities(bytes unlockData, uint256 deadline) external => NONDET DELETE;
    function modifyLiquiditiesWithoutUnlock(bytes actions, bytes[] params) external => NONDET DELETE;
    function unlockCallback(bytes data) external returns (bytes)  => NONDET DELETE;
    
    // External multicall() removed
    function multicall(bytes[] data) external returns (bytes[]) => NONDET DELETE;

    // Removed due prover warnings
    function name() external returns (string) => NONDET DELETE;
    function symbol() external returns (string) => NONDET DELETE;
    function DOMAIN_SEPARATOR() external returns (bytes32) => CONSTANT DELETE;

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

    // Reserved constants in _mapRecipient()
    require(_PositionManager != 1 && _PositionManager != 2);

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