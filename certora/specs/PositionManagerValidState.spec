import "./PoolManagerValidState.spec";

// requireValidState functions can be used to assume a valid state in other properties

function requireValidStatePositionManager() { 
    requireInvariant validNextTokenId;
    requireInvariant validPoolKeyStructure;
}

function requireValidStatePositionManagerERC721(env e) {
    requireInvariant noApprovalsForZeroAddress(e);
    requireInvariant zeroAddressHasNoBalance(e);
    requireInvariant getApprovedForExistingTokensOnly(e);
}

function requireValidStatePositionManagerToken(env e, uint256 tokenId) {

    requireValidStatePositionManager();
    requireValidStatePositionManagerERC721(e);

    requireInvariant ticksAlignWithSpacing(e, tokenId);
    requireInvariant activePositionMatchesPoolKey(e, tokenId);
    requireInvariant activePositionMatchesInitializedPoolInPoolManager(e, tokenId);
    requireInvariant subscriberAddressSetWithFlag(e, tokenId);
    requireInvariant subscribersForExistingTokensOnly(e, tokenId);
    requireInvariant validPositionTicks(e, tokenId);
    requireInvariant activePositionsMatchesToken(e, tokenId);
    requireInvariant noInfoForInvalidTokenIds(e);
}

function requireValidStatePositionManagerP(bytes25 poolId) {
    requireInvariant poolKeyMatchesInitializedPoolInPoolManager(poolId);
}

//
// PositionManager
//

// The next token ID MUST always be greater than or equal to 1
strong invariant validNextTokenId() 
    ghostNextTokenId >= 1;

// Position information and token MUST NOT exist for token ID 0 or any future token IDs
strong invariant noInfoForInvalidTokenIds(env e)
    forall uint256 tokenId. tokenId == 0 || tokenId >= ghostNextTokenId 
        => ghostPositionInfo[tokenId] == 0 && ghostERC721OwnerOf[tokenId] == 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerERC721(e);
        }
    }

// Active position ticks MUST be within the valid range defined by TickMath
strong invariant validPositionTicks(env e, uint256 tokenId)
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
strong invariant activePositionsMatchesToken(env e, uint256 tokenId)
    // Token exists <=> Position exists
    ghostERC721OwnerOf[tokenId] != 0 <=> ghostPositionInfo[tokenId] != 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerERC721(e);
            requireInvariant validPositionTicks(e, tokenId);
        }
    }

// Ticks in positions must be divisible by the pool's tick spacing
strong invariant ticksAlignWithSpacing(env e, uint256 tokenId)
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
        }
    } 

// Active position MUST correspond to valid pool key
strong invariant activePositionMatchesPoolKey(env e, uint256 tokenId)
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

// Active position must correspond to a initialized pool in PoolManager
strong invariant activePositionMatchesInitializedPoolInPoolManager(env e, uint256 tokenId)
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
// Notifier
//

// A subscription flag MUST be set when a valid subscriber address is present and vice versa
strong invariant subscriberAddressSetWithFlag(env e, uint256 tokenId)
    positionInfoHasSubscriberCVL(tokenId) <=> ghostNotifierSubscriber[tokenId] != 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireInvariant activePositionsMatchesToken(e, tokenId);
        }
    }

// Subscribers MUST only be set for existing token IDs
strong invariant subscribersForExistingTokensOnly(env e, uint256 tokenId)
    ghostNotifierSubscriber[tokenId] != 0 
        => ghostERC721OwnerOf[tokenId] != 0 && ghostPositionInfo[tokenId] != 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireInvariant subscriberAddressSetWithFlag(e, tokenId);
        }
    }

// 
// ERC721
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
    forall uint256 tokenId. ghostERC721GetApproved[tokenId] != 0 
        => ghostERC721OwnerOf[tokenId] != 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerERC721(e);
        }
    }
