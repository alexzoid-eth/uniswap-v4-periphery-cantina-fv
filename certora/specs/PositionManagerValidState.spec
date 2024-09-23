import "./PoolManagerValidState.spec";

// requireValidState* functions can be used to assume a valid state in other properties

function requireValidStatePositionManagerERC721(env e) {
    requireInvariant noApprovalsForZeroAddress(e);
    requireInvariant zeroAddressHasNoBalance(e);
    requireInvariant getApprovedForExistingTokensOnly(e);
}

function requireValidStatePositionManagerPoolId(bytes25 poolId) {
    requireInvariant poolKeyMatchesInitializedPoolInPoolManager(poolId);
}

function requireValidStatePositionManagerTokenId(env e, mathint tokenId) {

    requireInvariant validNextTokenId;
    requireInvariant validPoolKeyStructure;

    requireInvariant noInfoForInvalidTokenIds(e);

    requireInvariant ticksAlignWithSpacing(e, tokenId);
    requireInvariant activePositionMatchesPoolKey(e, tokenId);
    requireInvariant activePositionMatchesInitializedPoolInPoolManager(e, tokenId);
    requireInvariant activePositionsMatchesToken(e, tokenId);
    requireInvariant subscriberAddressSetWithFlag(e, tokenId);
    requireInvariant subscribersForExistingTokensOnly(e, tokenId);
    requireInvariant validPositionTicks(e, tokenId);
    requireInvariant liquidityMatchesPositionState(e, tokenId);

    requireValidStatePositionManagerERC721(e);
}

//
// PositionManager
//

// The next token ID MUST always be greater than or equal to 1
strong invariant validNextTokenId() 
    ghostNextTokenId >= 1;

// Position information and token MUST NOT exist for token ID 0 or any future token IDs
strong invariant noInfoForInvalidTokenIds(env e)
    forall mathint tokenId. tokenId == 0 || tokenId >= ghostNextTokenId 
        => ghostPositionInfo[tokenId] == 0 && ghostERC721OwnerOf[tokenId] == 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerERC721(e);
        }
    }

// Active position ticks MUST be within the valid range defined by TickMath
strong invariant validPositionTicks(env e, mathint tokenId)
    // Position not empty
    ghostPositionInfo[tokenId] != 0 => (
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
    ghostERC721OwnerOf[tokenId] != 0 <=> ghostPositionInfo[tokenId] != 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerERC721(e);
            requireInvariant validPositionTicks(e, tokenId);
        }
    }

// @todo mintPosition violation
// Active position MUST correspond to valid pool key
strong invariant activePositionMatchesPoolKey(env e, mathint tokenId)
    // Position is not empty
    ghostPositionInfo[tokenId] != 0 
        // Pool key id from position info == pool key id calculated from poolKeys structure params
        => positionInfoPoolIdCVL(tokenId) == _HelperCVL.poolKeyVariablesToShortId(
                _HelperCVL.toCurrency(ghostPoolKeysCurrency0[positionInfoPoolIdCVL(tokenId)]),
                _HelperCVL.toCurrency(ghostPoolKeysCurrency1[positionInfoPoolIdCVL(tokenId)]),
                ghostPoolKeysFee[positionInfoPoolIdCVL(tokenId)],
                ghostPoolKeysTickSpacing[positionInfoPoolIdCVL(tokenId)],
                ghostPoolKeysHooks[positionInfoPoolIdCVL(tokenId)]
            ) {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireInvariant validPositionTicks(e, tokenId);
            requireInvariant activePositionsMatchesToken(e, tokenId);
            requireInvariant validPoolKeyStructure;         
        }
    }

// @todo mintPosition violation
// Active position must correspond to a initialized pool in PoolManager
strong invariant activePositionMatchesInitializedPoolInPoolManager(env e, mathint tokenId)
    // Active position
    ghostPositionInfo[tokenId] != 0
        // PoolManager[poolId].slot0.sqrtPriceX96 != 0 means the pool is initialized
        => ghostPoolsSlot0SqrtPriceX96[_HelperCVL.poolKeyVariablesToId(
                _HelperCVL.toCurrency(ghostPoolKeysCurrency0[positionInfoPoolIdCVL(tokenId)]),
                _HelperCVL.toCurrency(ghostPoolKeysCurrency1[positionInfoPoolIdCVL(tokenId)]),
                ghostPoolKeysFee[positionInfoPoolIdCVL(tokenId)],
                ghostPoolKeysTickSpacing[positionInfoPoolIdCVL(tokenId)],
                ghostPoolKeysHooks[positionInfoPoolIdCVL(tokenId)]
            )] != 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            // PookKey has a valid structure (tick spacing != 0 etc)
            requireInvariant validPoolKeyStructure;      
            // Token for active position exists
            requireInvariant activePositionsMatchesToken(e, tokenId);
            // Ticks in active position set
            requireInvariant validPositionTicks(e, tokenId);
        }
    } 

// @todo mintPosition violation
// Ticks in positions must be divisible by the pool's tick spacing
strong invariant ticksAlignWithSpacing(env e, mathint tokenId)
    ghostPositionInfo[tokenId] != 0 => (
        ghostPoolKeysTickSpacing[positionInfoPoolIdCVL(tokenId)] != 0
        && positionInfoTickLowerCVL(tokenId) % ghostPoolKeysTickSpacing[positionInfoPoolIdCVL(tokenId)] == 0
        && positionInfoTickUpperCVL(tokenId) % ghostPoolKeysTickSpacing[positionInfoPoolIdCVL(tokenId)] == 0
    ) {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            // Pool exists in PoolManager
            requireInvariant activePositionMatchesInitializedPoolInPoolManager(e, tokenId);   
            // PookKey has a valid structure (tick spacing != 0 etc)
            requireInvariant validPoolKeyStructure;      
            // Ticks in active position set
            requireInvariant validPositionTicks(e, tokenId);   
            // Token for active position exists
            requireInvariant activePositionsMatchesToken(e, tokenId);
        }
    } 

// Touched pool key must correspond to a initialized pool in PoolManager
strong invariant poolKeyMatchesInitializedPoolInPoolManager(bytes25 poolId)
    // Any field of pool key touched
    ANY_FIELD_OF_POOLS_KEY_SET(poolId)
        // PoolManager[poolId].slot0.sqrtPriceX96 != 0 means the pool is initialized
        => ghostPoolsSlot0SqrtPriceX96[_HelperCVL.poolKeyVariablesToId(
                _HelperCVL.toCurrency(ghostPoolKeysCurrency0[poolId]),
                _HelperCVL.toCurrency(ghostPoolKeysCurrency1[poolId]),
                ghostPoolKeysFee[poolId],
                ghostPoolKeysTickSpacing[poolId],
                ghostPoolKeysHooks[poolId]
            )] != 0;

// All poolKey fields must contain valid and consistent values
strong invariant validPoolKeyStructure()
    // Any of poolKeys structure fields set
    forall bytes25 poolId. ANY_FIELD_OF_POOLS_KEY_SET(poolId) 
        => (
            // PoolManager doesn't accept invalid key params
            ghostPoolKeysCurrency0[poolId] < ghostPoolKeysCurrency1[poolId]
            && ghostPoolKeysTickSpacing[poolId] >= MIN_TICK_SPACING() && ghostPoolKeysTickSpacing[poolId] <= MAX_TICK_SPACING()
            && (ghostPoolKeysFee[poolId] <= MAX_LP_FEE() || ghostPoolKeysFee[poolId] == DYNAMIC_FEE_FLAG())
        );

//
// PositionManager.Notifier
//

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
        => ghostERC721OwnerOf[tokenId] != 0 && ghostPositionInfo[tokenId] != 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireInvariant subscriberAddressSetWithFlag(e, tokenId);
        }
    }

//
// PositionManager.ERC721
//

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
// PositionManager - PoolManager
//

// Active positions have nonzero liquidity, inactive positions have zero liquidity in PoolManager
strong invariant liquidityMatchesPositionState(env e, mathint tokenId)
    // Active position
    ghostPositionInfo[tokenId] != 0 ? (
        ghostPoolsPositionsLiquidity[_HelperCVL.poolKeyVariablesToId(
            _HelperCVL.toCurrency(ghostPoolKeysCurrency0[positionInfoPoolIdCVL(tokenId)]),
            _HelperCVL.toCurrency(ghostPoolKeysCurrency1[positionInfoPoolIdCVL(tokenId)]),
            ghostPoolKeysFee[positionInfoPoolIdCVL(tokenId)],
            ghostPoolKeysTickSpacing[positionInfoPoolIdCVL(tokenId)],
            ghostPoolKeysHooks[positionInfoPoolIdCVL(tokenId)]
        )][_HelperCVL.positionKey(
        _PositionManager, 
        positionInfoTickLowerCVL(tokenId), 
        positionInfoTickUpperCVL(tokenId), 
        to_bytes32(require_uint256(tokenId))
        )] >= 0
    // Non-exist position
    ) : (
        ghostPoolsPositionsLiquidity[_HelperCVL.poolKeyVariablesToId(
            _HelperCVL.toCurrency(ghostPoolKeysCurrency0[positionInfoPoolIdCVL(tokenId)]),
            _HelperCVL.toCurrency(ghostPoolKeysCurrency1[positionInfoPoolIdCVL(tokenId)]),
            ghostPoolKeysFee[positionInfoPoolIdCVL(tokenId)],
            ghostPoolKeysTickSpacing[positionInfoPoolIdCVL(tokenId)],
            ghostPoolKeysHooks[positionInfoPoolIdCVL(tokenId)]
        )][_HelperCVL.positionKey(
        _PositionManager, 
        positionInfoTickLowerCVL(tokenId), 
        positionInfoTickUpperCVL(tokenId), 
        to_bytes32(require_uint256(tokenId))
        )] == 0
    ) {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerERC721(e);
            requireInvariant validPositionTicks(e, tokenId); 
        }
    }