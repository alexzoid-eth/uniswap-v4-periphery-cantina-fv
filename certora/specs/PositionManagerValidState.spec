// requireValidState functions can be used to assume a valid state in other properties

function requireValidStatePositionManager() { 
    requireInvariant validNextTokenId;
    requireInvariant validPoolKeyStructure;
    requireInvariant validPositionTicks();
    requireInvariant subscriberAddressSetWithFlag;
    requireInvariant subscribersForExistingTokensOnly;
}

function requireValidStatePositionManagerERC721(env e) {
    requireInvariant noApprovalsForZeroAddress(e);
    requireInvariant zeroAddressHasNoBalance(e);
    requireInvariant getApprovedForExistingTokensOnly(e);
}

function requireValidStatePositionManagerE(env e) {

    requireValidStatePositionManager();

    requireInvariant noInfoForInvalidTokenIds(e);
    requireInvariant activePositionsMatchesToken(e);

    requireValidStatePositionManagerERC721(e);
}

function requireValidStatePositionManagerET(env e, uint256 tokenId) {
    requireInvariant ticksAlignWithSpacing(tokenId);
    requireInvariant activePositionMatchesPoolKey(e, tokenId);
    requireInvariant activePositionMatchesInitializedPoolInPoolManager(tokenId);
}

//
// PositionManager
//

// The next Ttoken ID MUST always be greater than or equal to 1
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

// All position ticks MUST be within the valid range defined by TickMath
strong invariant validPositionTicks()
    // Position not empty
    forall uint256 tokenId. ghostPositionInfo[tokenId] != 0 => (
        ghostPositionInfoTickLower[tokenId] >= MIN_TICK() && ghostPositionInfoTickUpper[tokenId] <= MAX_TICK() 
        && ghostPositionInfoTickLower[tokenId] < ghostPositionInfoTickUpper[tokenId]
    );

// Each active position MUST correspond minted token and vice versa
strong invariant activePositionsMatchesToken(env e)
    // Token exists
    forall uint256 tokenId. ghostERC721OwnerOf[tokenId] != 0 
        // Position exists
        <=> ghostPositionInfo[tokenId] != 0 {
        preserved with (env eInv) {
            requireNonZeroMsgSenderInInvCVL(e, eInv);
            requireValidStatePositionManagerERC721(e);
        }
    }

// Ticks in positions must be divisible by the pool's tick spacing
strong invariant ticksAlignWithSpacing(uint256 tokenId)
    ghostPositionInfo[tokenId] != 0 => (
        ghostPositionInfoTickLower[tokenId] 
            % ghostPoolKeysTickSpacing[to_bytes25(require_uint200(ghostPositionInfoPoolId[tokenId]))] == 0
        && ghostPositionInfoTickUpper[tokenId] 
            % ghostPoolKeysTickSpacing[to_bytes25(require_uint200(ghostPositionInfoPoolId[tokenId]))] == 0
    );

// Each active position MUST correspond to valid pool key
strong invariant activePositionMatchesPoolKey(env e, uint256 tokenId)
    // Position is not empty
    ghostPositionInfo[tokenId] != 0 
        // Pool key id from position info == pool key id calculated from poolKeys structure params
        => to_bytes25(require_uint200(ghostPositionInfoPoolId[tokenId])) == _HelperCVL.poolKeyVariablesToShortId(
                _HelperCVL.toCurrency(ghostPoolKeysCurrency0[to_bytes25(require_uint200(ghostPositionInfoPoolId[tokenId]))]),
                _HelperCVL.toCurrency(ghostPoolKeysCurrency1[to_bytes25(require_uint200(ghostPositionInfoPoolId[tokenId]))]),
                ghostPoolKeysFee[to_bytes25(require_uint200(ghostPositionInfoPoolId[tokenId]))],
                ghostPoolKeysTickSpacing[to_bytes25(require_uint200(ghostPositionInfoPoolId[tokenId]))],
                ghostPoolKeysHooks[to_bytes25(require_uint200(ghostPositionInfoPoolId[tokenId]))]
            ) {
        preserved with (env eInv) {
            requireInvariant validPositionTicks();
            requireInvariant activePositionsMatchesToken(e);
        }
    }

// Each active position must correspond to a initialized pool in PoolManager
strong invariant activePositionMatchesInitializedPoolInPoolManager(uint256 tokenId)
    // Active position
    ghostPositionInfo[tokenId] != 0
        // PoolManager[poolId].slot0.sqrtPriceX96 != 0 means the pool is initialized
        => ghostPoolsSlot0SqrtPriceX96[_HelperCVL.poolKeyVariablesToId(
                _HelperCVL.toCurrency(ghostPoolKeysCurrency0[to_bytes25(require_uint200(ghostPositionInfoPoolId[tokenId]))]),
                _HelperCVL.toCurrency(ghostPoolKeysCurrency1[to_bytes25(require_uint200(ghostPositionInfoPoolId[tokenId]))]),
                ghostPoolKeysFee[to_bytes25(require_uint200(ghostPositionInfoPoolId[tokenId]))],
                ghostPoolKeysTickSpacing[to_bytes25(require_uint200(ghostPositionInfoPoolId[tokenId]))],
                ghostPoolKeysHooks[to_bytes25(require_uint200(ghostPositionInfoPoolId[tokenId]))]
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
strong invariant subscriberAddressSetWithFlag()
    forall uint256 tokenId. ghostPositionInfoHasSubscriber[tokenId] != 0 
        <=> ghostNotifierSubscriber[tokenId] != 0;

// Subscribers MUST only be set for existing token IDs
strong invariant subscribersForExistingTokensOnly()
    forall uint256 tokenId. ghostNotifierSubscriber[tokenId] != 0 
        => ghostERC721OwnerOf[tokenId] != 0 && ghostPositionInfo[tokenId] != 0 {
        preserved {
            requireInvariant subscriberAddressSetWithFlag;
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
