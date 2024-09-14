// Custom

definition CUSTOM_MIN_TICK_SPACING() returns int24 = 1;
definition CUSTOM_MAX_TICK_SPACING() returns int24 = 2;

definition CUSTOM_TICK_MIN() returns int24 = -72;
definition CUSTOM_TICK_MAX() returns int24 = 72;

// PoolManager

definition MAX_INT16() returns mathint = 2^15 - 1;
definition MIN_INT128() returns mathint = -2^127;
definition MAX_INT128() returns mathint = 2^127 - 1;

definition MIN_TICK() returns int24 = require_int24(-887272);
definition MAX_TICK() returns int24 = require_int24(887272);

definition MIN_TICK_SPACING() returns int24 = 1;
definition MAX_TICK_SPACING() returns int24 = require_int24(MAX_INT16());

definition MAX_LP_FEE() returns uint24 = 1000000;
definition DYNAMIC_FEE_FLAG() returns uint24 = 0x800000;

definition MAX_PROTOCOL_FEE() returns mathint = 1000;

definition MIN_SQRT_PRICE() returns mathint = 4295128739;
definition MAX_SQRT_PRICE() returns mathint = 1461446703485210103287273052203988822378723970342;