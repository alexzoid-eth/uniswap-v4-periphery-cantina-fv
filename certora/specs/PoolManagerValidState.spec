strong invariant slot0ProtocolFeeIsValid() forall bytes32 poolId. 
    SLOT0_UNPACK_PROTOCOL_FEE_ZERO_FOR_ONE(ghostPoolsSlot0[poolId]) <= MAX_PROTOCOL_FEE() 
        && SLOT0_UNPACK_PROTOCOL_FEE_ONE_FOR_ZERO(ghostPoolsSlot0[poolId]) <= MAX_PROTOCOL_FEE();

