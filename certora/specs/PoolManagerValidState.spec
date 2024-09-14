// The protocol fee MUST NOT exceed the maximum allowable fee (MAX_PROTOCOL_FEE)
strong invariant maxProtocolFeeLimit() forall bytes32 poolId. 
    SLOT0_UNPACK_PROTOCOL_FEE_ZERO_FOR_ONE(ghostPoolsSlot0[poolId]) <= MAX_PROTOCOL_FEE() 
        && SLOT0_UNPACK_PROTOCOL_FEE_ONE_FOR_ZERO(ghostPoolsSlot0[poolId]) <= MAX_PROTOCOL_FEE();

// The sqrtPriceX96 in slot0 MUST be within the valid range
strong invariant validSqrtPriceX96Range() forall bytes32 poolId. ghostPoolsSlot0SqrtPriceX96[poolId] != 0 => (
        ghostPoolsSlot0SqrtPriceX96[poolId] >= MIN_SQRT_PRICE() && ghostPoolsSlot0SqrtPriceX96[poolId] < MAX_SQRT_PRICE()
    );