// Can be used to assume a valid state in other properties
function requireValidStatePoolManager() { 
    requireInvariant maxProtocolFeeLimit;
}

// The protocol fee MUST NOT exceed the maximum allowable fee (MAX_PROTOCOL_FEE)
strong invariant maxProtocolFeeLimit() forall bytes32 poolId. 
    SLOT0_UNPACK_PROTOCOL_FEE_ZERO_FOR_ONE(ghostPoolsSlot0[poolId]) <= MAX_PROTOCOL_FEE() 
        && SLOT0_UNPACK_PROTOCOL_FEE_ONE_FOR_ZERO(ghostPoolsSlot0[poolId]) <= MAX_PROTOCOL_FEE();