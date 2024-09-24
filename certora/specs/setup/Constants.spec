// Custom

definition NATIVE_CURRENCY() returns address = 0;

// PoolManager

definition MAX_INT16() returns mathint = 2^15 - 1;
definition MIN_INT128() returns mathint = -2^127;
definition MAX_INT128() returns mathint = 2^127 - 1;

definition MIN_TICK() returns mathint = -887272;
definition MAX_TICK() returns mathint = 887272;

definition MIN_TICK_SPACING() returns mathint = 1;
definition MAX_TICK_SPACING() returns mathint = MAX_INT16();

definition MAX_LP_FEE() returns uint24 = 1000000;
definition DYNAMIC_FEE_FLAG() returns uint24 = 0x800000;

definition MAX_PROTOCOL_FEE() returns mathint = 1000;

// PositionManager

definition EMPTY_POSITION_INFO() returns uint256 = 0;