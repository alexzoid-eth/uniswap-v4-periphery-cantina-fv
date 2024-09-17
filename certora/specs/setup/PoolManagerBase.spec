import "./HooksTestERC20A.spec";
import "./HooksTestERC20B.spec";
import "./HooksTestERC20C.spec";
import "./ERC20.spec";
import "./TransientStorage.spec";
import "./Constants.spec";
import "./HelperCVL.spec";
import "./MathCVL.spec";
import "./TransientStateLibrary.spec";

using PoolManager as _PoolManager;

///////////////////////////////////////// Methods /////////////////////////////////////////////

methods {

    // Hooks are disabled 
    function Hooks.callHook(address self, bytes memory data) internal returns (bytes memory) 
        => callHookCVL();

    // SqrtPriceMath 
    //  - don't care about return values as too much complexity
    function SqrtPriceMath.getAmount0Delta(
        uint160 sqrtRatioAX96, uint160 sqrtRatioBX96, uint128 liquidity, bool roundUp
    ) internal returns (uint256) => NONDET;
    function SqrtPriceMath.getAmount1Delta(
        uint160 sqrtRatioAX96, uint160 sqrtRatioBX96, uint128 liquidity, bool roundUp
    ) internal returns (uint256) => NONDET;
        
    // TickMath 
    //  - don't care about return values as too much complexity
    function TickMath.getSqrtPriceAtTick(int24 tick) internal returns (uint160)
        => NONDET;
    function TickMath.getTickAtSqrtPrice(uint160 sqrtPriceX96) internal returns (int24) 
        => getTickAtSqrtPriceCVL(sqrtPriceX96);
}

///////////////////////////////////////// Functions ////////////////////////////////////////////

// Hooks.callHook() stub
function callHookCVL() returns bytes {
    bytes ret; 
    require(ret.length == 0);
    return ret;
}

// Require valid input parameters of tested functions
function requireValidEnvCVL(env e) {
    require(e.msg.sender != 0);
    require(e.block.timestamp != 0);
}

// Support only NATIVE, ERC20A, ERC20B or ERC20C currencies
function requireValidCurrencyAddressCVL(address currency) {
    require(currency == NATIVE_CURRENCY() || currency == _ERC20A || currency == _ERC20B || currency == _ERC20C);
}

// Support only NATIVE/ERC20B or ERC20A/ERC20B pools
function isValidPoolCurrencyCVL(address currency) returns bool {
    return (currency == NATIVE_CURRENCY() || currency == _ERC20A || currency == _ERC20B);
}

function isValidCurrencyCVL(address currency) returns bool {
    return (isValidPoolCurrencyCVL(currency) || currency == _ERC20C);
}

function requireValidCurrencyCVL(PoolManager.Currency currency) {
    require(isValidCurrencyCVL(currency));
}

function requireValidKeyCVL(PoolManager.PoolKey poolKey) {
    require((_ERC20A > 0 && _ERC20A < _ERC20B)
        && (poolKey.currency0 == NATIVE_CURRENCY() || poolKey.currency0 == _ERC20A)
        && (poolKey.currency1 == _ERC20B)
        && (poolKey.tickSpacing >= MIN_TICK_SPACING() && poolKey.tickSpacing <= MAX_TICK_SPACING())
        && (poolKey.fee <= MAX_LP_FEE() || poolKey.fee == DYNAMIC_FEE_FLAG())
    );
}

function requireTicksLimitationCVL(IPoolManager.ModifyLiquidityParams params) {
    require(params.tickLower < params.tickUpper);
    require(params.tickLower >= CUSTOM_TICK_MIN() && params.tickLower <= CUSTOM_TICK_MAX());
    require(params.tickUpper >= CUSTOM_TICK_MIN() && params.tickUpper <= CUSTOM_TICK_MAX());
}

// Summarization for external functions 

function modifyLiquidityCLV(
    env e, PoolManager.PoolKey key, IPoolManager.ModifyLiquidityParams params, bytes hookData
    ) returns (PoolManager.BalanceDelta, PoolManager.BalanceDelta) {
    
    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Assume pool was initialized with valid pool key
    requireValidKeyCVL(key);

    PoolManager.BalanceDelta callerDelta;
    PoolManager.BalanceDelta feesAccrued;
    callerDelta, feesAccrued = _PoolManager.modifyLiquidity(e, key, params, hookData);
    return (callerDelta, feesAccrued);
}

function swapCVL(
    env e, PoolManager.PoolKey key, IPoolManager.SwapParams params, bytes hookData
    ) returns PoolManager.BalanceDelta {
    
    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Assume pool was initialized with valid pool key
    requireValidKeyCVL(key);
    
    return _PoolManager.swap(e, key, params, hookData);
}

function donateCVL(
    env e, PoolManager.PoolKey key, uint256 amount0, uint256 amount1, bytes hookData
    ) returns PoolManager.BalanceDelta {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Assume pool was initialized with valid pool key
    requireValidKeyCVL(key);
    
    return _PoolManager.donate(e, key, amount0, amount1, hookData);
}

function syncCVL(env e, PoolManager.Currency currency) {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Assume only supported in this environment currencies are passed
    requireValidCurrencyCVL(currency);

    _PoolManager.sync(e, currency);
}

function takeCVL(env e, PoolManager.Currency currency, address to, uint256 amount) {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Assume only supported in this environment currencies are passed
    requireValidCurrencyCVL(currency);

    _PoolManager.take(e, currency, to, amount);
}

function settleCVL(env e) returns uint256 {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    return _PoolManager.settle(e);
}

function settleForCVL(env e, address recipient) returns uint256 {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    return _PoolManager.settleFor(e, recipient);
}

function clearCVL(env e, PoolManager.Currency currency, uint256 amount) {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Assume only supported in this environment currencies are passed
    requireValidCurrencyCVL(currency);

    _PoolManager.clear(e, currency, amount);
}

function mintCVL(env e, address to, uint256 id, uint256 amount) {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Assume only supported in this environment currencies are passed
    requireValidCurrencyCVL(_HelperCVL.fromId(id));

    _PoolManager.mint(e, to, id, amount);
}

function burnCVL(env e, address from, uint256 id, uint256 amount) {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Assume only supported in this environment currencies are passed
    requireValidCurrencyCVL(_HelperCVL.fromId(id));

    _PoolManager.burn(e, from, id, amount);
}

function updateDynamicLPFeeCVL(env e, PoolManager.PoolKey key, uint24 newDynamicLPFee) {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Assume pool was initialized with valid pool key
    requireValidKeyCVL(key);

    _PoolManager.updateDynamicLPFee(e, key, newDynamicLPFee);
}

function setProtocolFeeCVL(env e, PoolManager.PoolKey key, uint24 newProtocolFee) {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Assume pool was initialized with valid pool key
    requireValidKeyCVL(key);

    _PoolManager.setProtocolFee(e, key, newProtocolFee);
}

function collectProtocolFeesCVL(env e, address recipient, PoolManager.Currency currency, uint256 amount) returns uint256 {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Assume only supported in this environment currencies are passed
    requireValidCurrencyCVL(currency);

    return _PoolManager.collectProtocolFees(e, recipient, currency, amount);
}

// ProtocolFeeController summarization as CVL mapping

persistent ghost mapping (bytes32 => uint24) ghostPoolFees {
    axiom forall bytes32 i. ghostPoolFees[i] <= 1000; // less than 0.1%
}

function fetchProtocolFeeCVL(PoolManager.PoolKey key) returns uint24 {
    return ghostPoolFees[poolKeyToPoolIdCVL(key)];
}

// TickMath

function getTickAtSqrtPriceCVL(uint160 sqrtPriceX96) returns int24 {

    int24 tick;

    require(sqrtPriceX96 >= MIN_SQRT_PRICE() && sqrtPriceX96 < MAX_SQRT_PRICE());
    require(_HelperCVL.getAbsTick(tick) <= MAX_TICK());

    return tick;
}

////////////////////////////////////////// Hooks //////////////////////////////////////////////

//
// Ghost copy of `mapping(PoolId id => Pool.State) internal _pools;`
//

// _pools[].slot0

persistent ghost mapping (bytes32 => uint256) ghostPoolsSlot0 {
    init_state axiom forall bytes32 id. ghostPoolsSlot0[id] == 0;
}

persistent ghost mapping (bytes32 => mathint) ghostPoolsSlot0SqrtPriceX96 {
    init_state axiom forall bytes32 id. ghostPoolsSlot0SqrtPriceX96[id] == 0;
    axiom forall bytes32 id. ghostPoolsSlot0SqrtPriceX96[id] == SLOT0_UNPACK_SQRT_PRICE_X96(ghostPoolsSlot0[id]);
}

persistent ghost mapping (bytes32 => mathint) ghostPoolsSlot0Tick {
    init_state axiom forall bytes32 id. ghostPoolsSlot0Tick[id] == 0;
    axiom forall bytes32 id. ghostPoolsSlot0Tick[id] == SLOT0_UNPACK_TICK(ghostPoolsSlot0[id]);
}

persistent ghost mapping (bytes32 => mathint) ghostPoolsSlot0ProtocolFeeZeroForOne {
    init_state axiom forall bytes32 id. ghostPoolsSlot0ProtocolFeeZeroForOne[id] == 0;
    axiom forall bytes32 id. ghostPoolsSlot0ProtocolFeeZeroForOne[id] == SLOT0_UNPACK_PROTOCOL_FEE_ZERO_FOR_ONE(ghostPoolsSlot0[id]);
}

persistent ghost mapping (bytes32 => mathint) ghostPoolsSlot0ProtocolFeeOneForZero {
    init_state axiom forall bytes32 id. ghostPoolsSlot0ProtocolFeeOneForZero[id] == 0;
    axiom forall bytes32 id. ghostPoolsSlot0ProtocolFeeOneForZero[id] == SLOT0_UNPACK_PROTOCOL_FEE_ONE_FOR_ZERO(ghostPoolsSlot0[id]);
}

persistent ghost mapping (bytes32 => mathint) ghostPoolsSlot0LpFee {
    init_state axiom forall bytes32 id. ghostPoolsSlot0LpFee[id] == 0;
    axiom forall bytes32 id. ghostPoolsSlot0LpFee[id] == SLOT0_UNPACK_PROTOCOL_LP_FEE(ghostPoolsSlot0[id]);
}

definition SLOT0_UNPACK_SQRT_PRICE_X96(uint256 val) returns mathint 
    = val & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;
definition SLOT0_UNPACK_TICK(uint256 val) returns mathint 
    = (val >> 160) & 0xFFFFFF;
definition SLOT0_UNPACK_PROTOCOL_FEE_ZERO_FOR_ONE(uint256 val) returns mathint 
    = (val >> 184) & 0xFFF;
definition SLOT0_UNPACK_PROTOCOL_FEE_ONE_FOR_ZERO(uint256 val) returns mathint 
    = (val >> 196) & 0xFFF;
definition SLOT0_UNPACK_PROTOCOL_LP_FEE(uint256 val) returns mathint 
    = (val >> 208) & 0xFFFFFF;

function slot0SqrtPriceX96CVL(bytes32 poolId) returns mathint {
    return SLOT0_UNPACK_SQRT_PRICE_X96(ghostPoolsSlot0[poolId]);
}

function slot0TickCVL(bytes32 poolId) returns mathint {
    return SLOT0_UNPACK_TICK(ghostPoolsSlot0[poolId]);
}

function slot0ProtocolFeeZeroForOneCVL(bytes32 poolId) returns mathint {
    return SLOT0_UNPACK_PROTOCOL_FEE_ZERO_FOR_ONE(ghostPoolsSlot0[poolId]);
}

function slot0ProtocolFeeOneForZeroCVL(bytes32 poolId) returns mathint {
    return SLOT0_UNPACK_PROTOCOL_FEE_ONE_FOR_ZERO(ghostPoolsSlot0[poolId]);
}

function Slot0LpFeeCVL(bytes32 poolId) returns mathint {
    return SLOT0_UNPACK_PROTOCOL_LP_FEE(ghostPoolsSlot0[poolId]);
}

// Use `.(offset 0)` instead of `.slot0` to bypass bytes32 to uint256 conversion limitation 
hook Sload uint256 val _PoolManager._pools[KEY PoolManager.PoolId i].(offset 0) {
    require(ghostPoolsSlot0[i] == val);
} 

hook Sstore _PoolManager._pools[KEY PoolManager.PoolId i].(offset 0) uint256 val {
    ghostPoolsSlot0[i] = val;
}

// _pools[].feeGrowthGlobal0X128

persistent ghost mapping (bytes32 => mathint) ghostPoolsFeeGrowthGlobal0X128 {
    axiom forall bytes32 i. ghostPoolsFeeGrowthGlobal0X128[i] >= 0 && ghostPoolsFeeGrowthGlobal0X128[i] <= max_uint256;
}

hook Sload uint256 val _PoolManager._pools[KEY PoolManager.PoolId i].feeGrowthGlobal0X128 {
    require(require_uint256(ghostPoolsFeeGrowthGlobal0X128[i]) == val);
} 

hook Sstore _PoolManager._pools[KEY PoolManager.PoolId i].feeGrowthGlobal0X128 uint256 val {
    ghostPoolsFeeGrowthGlobal0X128[i] = val;
}

// _pools[].feeGrowthGlobal1X128

persistent ghost mapping (bytes32 => mathint) ghostPoolsFeeGrowthGlobal1X128 {
    axiom forall bytes32 i. ghostPoolsFeeGrowthGlobal1X128[i] >= 0 && ghostPoolsFeeGrowthGlobal1X128[i] <= max_uint256;
}

hook Sload uint256 val _PoolManager._pools[KEY PoolManager.PoolId i].feeGrowthGlobal1X128 {
    require(require_uint256(ghostPoolsFeeGrowthGlobal1X128[i]) == val);
} 

hook Sstore _PoolManager._pools[KEY PoolManager.PoolId i].feeGrowthGlobal1X128 uint256 val {
    ghostPoolsFeeGrowthGlobal1X128[i] = val;
}

// _pools[].liquidity

persistent ghost mapping (bytes32 => mathint) ghostPoolsLiquidity {
    axiom forall bytes32 i. ghostPoolsLiquidity[i] >= 0 && ghostPoolsLiquidity[i] <= max_uint128;
}

hook Sload uint128 val _PoolManager._pools[KEY PoolManager.PoolId i].liquidity {
    require(require_uint128(ghostPoolsLiquidity[i]) == val);
} 

hook Sstore _PoolManager._pools[KEY PoolManager.PoolId i].liquidity uint128 val {
    ghostPoolsLiquidity[i] = val;
}

// _pools[].ticks[].liquidityGross

persistent ghost mapping (bytes32 => mapping(int24 => mathint)) ghostPoolsTicksLiquidityGross {
    axiom forall bytes32 i. forall int24 j. 
        ghostPoolsTicksLiquidityGross[i][j] >= 0 && ghostPoolsTicksLiquidityGross[i][j] <= max_uint128;
}

hook Sload uint128 val _PoolManager._pools[KEY PoolManager.PoolId i].ticks[KEY int24 j].liquidityGross {
    require(require_uint128(ghostPoolsTicksLiquidityGross[i][j]) == val);
} 

hook Sstore _PoolManager._pools[KEY PoolManager.PoolId i].ticks[KEY int24 j].liquidityGross uint128 val {
    ghostPoolsTicksLiquidityGross[i][j] = val;
}

// _pools[].ticks[].liquidityNet

persistent ghost mapping (bytes32 => mapping(int24 => mathint)) ghostPoolsTicksLiquidityNet {
    axiom forall bytes32 i. forall int24 j. 
        ghostPoolsTicksLiquidityNet[i][j] >= MIN_INT128() && ghostPoolsTicksLiquidityNet[i][j] <= MAX_INT128();
}

hook Sload int128 val _PoolManager._pools[KEY PoolManager.PoolId i].ticks[KEY int24 j].liquidityNet {
    require(require_int128(ghostPoolsTicksLiquidityNet[i][j]) == val);
} 

hook Sstore _PoolManager._pools[KEY PoolManager.PoolId i].ticks[KEY int24 j].liquidityNet int128 val {
    ghostPoolsTicksLiquidityNet[i][j] = val;
}

// _pools[].ticks[].feeGrowthOutside0X128

persistent ghost mapping (bytes32 => mapping(int24 => mathint)) ghostPoolsTicksFeeGrowthOutside0X128 {
    axiom forall bytes32 i. forall int24 j. 
        ghostPoolsTicksFeeGrowthOutside0X128[i][j] >= 0 && ghostPoolsTicksFeeGrowthOutside0X128[i][j] <= max_uint256;
}

hook Sload uint256 val _PoolManager._pools[KEY PoolManager.PoolId i].ticks[KEY int24 j].feeGrowthOutside0X128 {
    require(require_uint256(ghostPoolsTicksFeeGrowthOutside0X128[i][j]) == val);
} 

hook Sstore _PoolManager._pools[KEY PoolManager.PoolId i].ticks[KEY int24 j].feeGrowthOutside0X128 uint256 val {
    ghostPoolsTicksFeeGrowthOutside0X128[i][j] = val;
}

// _pools[].ticks[].feeGrowthOutside1X128

persistent ghost mapping (bytes32 => mapping(int24 => mathint)) ghostPoolsTicksFeeGrowthOutside1X128 {
    axiom forall bytes32 i. forall int24 j. 
        ghostPoolsTicksFeeGrowthOutside1X128[i][j] >= 0 && ghostPoolsTicksFeeGrowthOutside1X128[i][j] <= max_uint256;
}

hook Sload uint256 val _PoolManager._pools[KEY PoolManager.PoolId i].ticks[KEY int24 j].feeGrowthOutside1X128 {
    require(require_uint256(ghostPoolsTicksFeeGrowthOutside1X128[i][j]) == val);
} 

hook Sstore _PoolManager._pools[KEY PoolManager.PoolId i].ticks[KEY int24 j].feeGrowthOutside1X128 uint256 val {
    ghostPoolsTicksFeeGrowthOutside1X128[i][j] = val;
}

// _pools[].tickBitmap[]

persistent ghost mapping (bytes32 => mapping(int16 => mathint)) ghostPoolsTickBitmap {
    axiom forall bytes32 i. forall int16 j. ghostPoolsTickBitmap[i][j] >= 0 && ghostPoolsTickBitmap[i][j] <= max_uint256;
}

hook Sload uint256 val _PoolManager._pools[KEY PoolManager.PoolId i].tickBitmap[KEY int16 j] {
    require(require_uint256(ghostPoolsTickBitmap[i][j]) == val);
} 

hook Sstore _PoolManager._pools[KEY PoolManager.PoolId i].tickBitmap[KEY int16 j] uint256 val {
    ghostPoolsTickBitmap[i][j] = val;
}

// _pools[].positions[].liquidity

persistent ghost mapping (bytes32 => mapping(bytes32 => mathint)) ghostPoolsPositionsLiquidity {
    axiom forall bytes32 i. forall bytes32 j. 
        ghostPoolsPositionsLiquidity[i][j] >= 0 && ghostPoolsPositionsLiquidity[i][j] <= max_uint128;
}

hook Sload uint128 val _PoolManager._pools[KEY PoolManager.PoolId i].positions[KEY bytes32 j].liquidity {
    require(require_uint128(ghostPoolsPositionsLiquidity[i][j]) == val);
} 

hook Sstore _PoolManager._pools[KEY PoolManager.PoolId i].positions[KEY bytes32 j].liquidity uint128 val {
    ghostPoolsPositionsLiquidity[i][j] = val;
}

// _pools[].positions[].feeGrowthInside0LastX128

persistent ghost mapping (bytes32 => mapping(bytes32 => mathint)) ghostPoolsPositionsFeeGrowthInside0LastX128 {
    axiom forall bytes32 i. forall bytes32 j. 
        ghostPoolsPositionsFeeGrowthInside0LastX128[i][j] >= 0 
        && ghostPoolsPositionsFeeGrowthInside0LastX128[i][j] <= max_uint256;
}

hook Sload uint256 val _PoolManager._pools[KEY PoolManager.PoolId i].positions[KEY bytes32 j].feeGrowthInside0LastX128 {
    require(require_uint256(ghostPoolsPositionsFeeGrowthInside0LastX128[i][j]) == val);
} 

hook Sstore _PoolManager._pools[KEY PoolManager.PoolId i].positions[KEY bytes32 j].feeGrowthInside0LastX128 uint256 val {
    ghostPoolsPositionsFeeGrowthInside0LastX128[i][j] = val;
}

// _pools[].positions[].feeGrowthInside1LastX128

persistent ghost mapping (bytes32 => mapping(bytes32 => mathint)) ghostPoolsPositionsFeeGrowthInside1LastX128 {
    axiom forall bytes32 i. forall bytes32 j. 
        ghostPoolsPositionsFeeGrowthInside1LastX128[i][j] >= 0 
        && ghostPoolsPositionsFeeGrowthInside1LastX128[i][j] <= max_uint256;
}

hook Sload uint256 val _PoolManager._pools[KEY PoolManager.PoolId i].positions[KEY bytes32 j].feeGrowthInside1LastX128 {
    require(require_uint256(ghostPoolsPositionsFeeGrowthInside1LastX128[i][j]) == val);
} 

hook Sstore _PoolManager._pools[KEY PoolManager.PoolId i].positions[KEY bytes32 j].feeGrowthInside1LastX128 uint256 val {
    ghostPoolsPositionsFeeGrowthInside1LastX128[i][j] = val;
}

// Ghost copy of `mapping(Currency currency => uint256 amount) public protocolFeesAccrued;`

persistent ghost mapping (address => mathint) ghostProtocolFeesAccrued {
    axiom forall PoolManager.Currency i. ghostProtocolFeesAccrued[i] >= 0 && ghostProtocolFeesAccrued[i] <= max_uint256;
}

hook Sload uint256 val _PoolManager.protocolFeesAccrued[KEY PoolManager.Currency i] {
    require(require_uint256(ghostProtocolFeesAccrued[i]) == val);
} 

hook Sstore _PoolManager.protocolFeesAccrued[KEY PoolManager.Currency i] uint256 val {
    ghostProtocolFeesAccrued[i] = val;
}

// Ghost copy of `IProtocolFeeController public protocolFeeController`

persistent ghost address ghostProtocolFeeController;

hook Sload address val _PoolManager.protocolFeeController {
    require(ghostProtocolFeeController == val);
} 

hook Sstore _PoolManager.protocolFeeController address val {
    ghostProtocolFeeController = val;
}

// Ghost copy of `mapping(address owner => mapping(address operator => bool isOperator)) public isOperator;`

persistent ghost mapping (address => mapping(address => bool)) ghostERC6909IsOperator;

hook Sload bool val _PoolManager.isOperator[KEY address owner][KEY address operator] {
    require(ghostERC6909IsOperator[owner][operator] == val);
} 

hook Sstore _PoolManager.isOperator[KEY address owner][KEY address operator] bool val {
    ghostERC6909IsOperator[owner][operator] = val;
}

// Ghost copy of `mapping(address owner => mapping(uint256 id => uint256 balance)) public balanceOf;`

persistent ghost mapping (address => mapping(uint256 => mathint)) ghostERC6909BalanceOf {
    axiom forall address owner. forall uint256 id. 
        ghostERC6909BalanceOf[owner][id] >= 0 && ghostERC6909BalanceOf[owner][id] <= max_uint256;
}

hook Sload uint256 val _PoolManager.balanceOf[KEY address owner][KEY uint256 id] {
    require(require_uint256(ghostERC6909BalanceOf[owner][id]) == val);
} 

hook Sstore _PoolManager.balanceOf[KEY address owner][KEY uint256 id] uint256 val {
    ghostERC6909BalanceOf[owner][id] = val;
}

// Ghost copy of `mapping(address owner => mapping(address spender => mapping(uint256 id => uint256 amount))) public allowance;`

persistent ghost mapping (address => mapping(address => mapping(uint256 => mathint))) ghostERC6909Allowance {
    axiom forall address owner. forall address spender. forall uint256 id. 
        ghostERC6909Allowance[owner][spender][id] >= 0 && ghostERC6909Allowance[owner][spender][id] <= max_uint256;
}

hook Sload uint256 val _PoolManager.allowance[KEY address owner][KEY address spender][KEY uint256 id] {
    require(require_uint256(ghostERC6909Allowance[owner][spender][id]) == val);
} 

hook Sstore _PoolManager.allowance[KEY address owner][KEY address spender][KEY uint256 id] uint256 val {
    ghostERC6909Allowance[owner][spender][id] = val;
}