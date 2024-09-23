import "./ERC20.spec";
import "./TransientStorage.spec";
import "./Constants.spec";
import "./HelperCVL.spec";
import "./MathCVL.spec";
import "./TransientStateLibrary.spec";

using PoolManagerHarness as _PoolManager;

///////////////////////////////////////// Methods /////////////////////////////////////////////

methods {

    // External functions
    //  - assume valid pool key inside all external functions except initialize()
    //  - assume currency can be address(0) - native, ERC20A, ERC20B or ERC20C
    //  - assume all pools are NATIVE/ERC20B or ERC20A/ERC20B
    //  - assume hookData length is zero as we don't need 

    function _PoolManager.initialize(
        PoolManager.PoolKey key, uint160 sqrtPriceX96, bytes hookData
        ) external returns (int24) with (env e) 
        => initializeCVL(e, key, sqrtPriceX96, hookData);

    function _PoolManager.modifyLiquidity(
        PoolManager.PoolKey key, IPoolManager.ModifyLiquidityParams params, bytes hookData
    ) external returns (PoolManager.BalanceDelta, PoolManager.BalanceDelta) with (env e) 
        => modifyLiquidityCLV(e, key, params, hookData);
    
    function _PoolManager.swap(
        PoolManager.PoolKey key, IPoolManager.SwapParams params, bytes hookData
    ) external returns (PoolManager.BalanceDelta) with (env e) 
        => swapCVL(e, key, params, hookData);

    function _PoolManager.donate(
        PoolManager.PoolKey key, uint256 amount0, uint256 amount1, bytes hookData
    ) external returns (PoolManager.BalanceDelta) with (env e) 
        => donateCVL(e, key, amount0, amount1, hookData);

    function _PoolManager.sync(PoolManager.Currency currency) external with (env e) 
        => syncCVL(e, currency);

    function _PoolManager.take(PoolManager.Currency currency, address to, uint256 amount) external with (env e) 
        => takeCVL(e, currency, to, amount);

    function _PoolManager.settle() external returns (uint256) with (env e) 
        => settleCVL(e);

    function _PoolManager.settleFor(address recipient) external returns (uint256) with (env e) 
        => settleForCVL(e, recipient);

    function _PoolManager.clear(PoolManager.Currency currency, uint256 amount) external with (env e) 
        => clearCVL(e, currency, amount);

    function _PoolManager.mint(address to, uint256 id, uint256 amount) external with (env e) 
        => mintCVL(e, to, id, amount);

    function _PoolManager.burn(address from, uint256 id, uint256 amount) external with (env e) 
        => burnCVL(e, from, id, amount);

    function _PoolManager.updateDynamicLPFee(PoolManager.PoolKey key, uint24 newDynamicLPFee) external with (env e) 
        => updateDynamicLPFeeCVL(e, key, newDynamicLPFee);

    function _PoolManager.setProtocolFee(PoolManager.PoolKey key, uint24 newProtocolFee) external with (env e) 
        => setProtocolFeeCVL(e, key, newProtocolFee);

    function _PoolManager.collectProtocolFees(
        address recipient, PoolManager.Currency currency, uint256 amount
    ) external returns (uint256) with (env e) => collectProtocolFeesCVL(e, recipient, currency, amount);

    // unlock() not needed as _handleAction is no-op and summarizing unlock here would have no effect
    function _PoolManager.unlock(bytes data) external returns (bytes) => NONDET DELETE;

    // setProtocolFeeController() not needed as protocol fee controller summarized as CVL mapping
    function _PoolManager.setProtocolFeeController(address controller) external => NONDET DELETE;

    // extsload()/exttload() summarized in upper lever, should never executes
    function _PoolManager.extsload(bytes32 slot) external returns (bytes32) => NONDET DELETE;
    function _PoolManager.extsload(bytes32 startSlot, uint256 nSlots) external returns (bytes32[]) => NONDET DELETE;
    function _PoolManager.extsload(bytes32[] slots) external returns (bytes32[]) => NONDET DELETE;
    function _PoolManager.exttload(bytes32 slot) external returns (bytes32) => NONDET DELETE;
    function _PoolManager.exttload(bytes32[] slots) external returns (bytes32[]) => NONDET DELETE;

    // Use CVL mapping instead of external contract
    function ProtocolFees._fetchProtocolFee(PoolManager.PoolKey memory key) internal returns (uint24)
        => fetchProtocolFeeCVL(key);

    // Hooks are disabled 
    function Hooks.callHook(address self, bytes memory data) internal returns (bytes memory) 
        => callHookStubCVL();

    // CurrencyLibrary
    function CurrencyLibrary.transfer(PoolManager.Currency currency, address to, uint256 amount) internal with (env e) 
        => safeTransferFromCVL(e, currency, calledContract, to, amount, false);
    function CurrencyLibrary.balanceOfSelf(PoolManager.Currency currency) internal returns (uint256) with (env e) 
        => balanceOfCVL(e, currency, calledContract);
    function CurrencyLibrary.balanceOf(PoolManager.Currency currency, address owner) internal returns (uint256) with (env e) 
        => balanceOfCVL(e, currency, owner);   

    // TickMath 
    function TickMath.getTickAtSqrtPrice(uint160 sqrtPriceX96) internal returns (int24) 
        => getTickAtSqrtPriceCVL(sqrtPriceX96);
}

///////////////////////////////////////// Functions ////////////////////////////////////////////

// Pool helpers

function isActivePositionCVL(int24 tick0, int24 tickLower, int24 tickUpper) returns bool {
    return tick0 >= tickLower && tick0 < tickUpper;
}

function isActivePositionInPoolCVL(bytes32 poolId, int24 tickLower, int24 tickUpper) returns bool {
    return isActivePositionCVL(require_int24(ghostPoolsSlot0Tick[poolId]), tickLower, tickUpper);
}

function amountsToBalanceDeltaCVL(int128 _amount0, int128 _amount1) returns PoolManager.BalanceDelta {

    PoolManager.BalanceDelta delta;

    require(_HelperCVL.amount0(delta) == _amount0);
    require(_HelperCVL.amount1(delta) == _amount1);
    
    return delta;
}

// Hooks stub

function callHookStubCVL() returns bytes {
    bytes ret; 
    require(ret.length == 0);
    return ret;
}

function isEmptyHookDataCVL(bytes data) returns bool {
    return data.length == 0;
}

// Valid params

function requireNonZeroMsgSenderInInvCVL(env eFunc, env eInv) {
    require(eFunc.msg.sender == eInv.msg.sender);
    require(isValidEnvCVL(eFunc));
}

function requireValidEnvCVL(env e) {
    require(isValidEnvCVL(e));
}

function isValidEnvCVL(env e) returns bool {
    return (e.msg.sender != 0);
}

function isValidKeyCVL(PoolManager.PoolKey poolKey) returns bool {
    return (
        (poolKey.currency0 == NATIVE_CURRENCY() || poolKey.currency0 == ghostERC20A)
        && poolKey.currency1 == ghostERC20B
        && poolKey.tickSpacing >= MIN_TICK_SPACING() && poolKey.tickSpacing <= MAX_TICK_SPACING()
        && (poolKey.fee <= MAX_LP_FEE() || poolKey.fee == DYNAMIC_FEE_FLAG())
    );
}

function isValidTickCVL(int24 tick) returns bool {
    return (tick >= MIN_TICK() && tick <= MAX_TICK());
}

function isValidTicksCVL(int24 tickLower, int24 tickUpper) returns bool {
    return (
        tickLower < tickUpper
        && isValidTickCVL(tickLower)
        && isValidTickCVL(tickUpper)
    );
}

function isValidSwapParamsCVL(IPoolManager.SwapParams params) returns bool {
    return (
        params.amountSpecified != 0
    );
}

// Summarization for external functions 

function initializeCVL(env e, PoolManager.PoolKey key, uint160 sqrtPriceX96, bytes hookData) returns int24 {

    // Safe assumptions about environment
    require(isValidEnvCVL(e));

    // Empty hook data
    require(isEmptyHookDataCVL(hookData));

    return _PoolManager.initialize(e, key, sqrtPriceX96, hookData);
}

// Insert here a list of requirements that correlate the token amounts with liquidity delta
function modifyLiquidityAmountsConditionsCVL(
    bytes32 poolId,
    int128 currency0Amount,
    int128 currency1Amount,
    int128 currency0FeeAmount,
    int128 currency1FeeAmount,
    int256 liquidityDelta
) {
    require(liquidityDelta > 0 => currency0Amount < 0 && currency1Amount < 0);
    require(liquidityDelta < 0 => currency0Amount >= 0 && currency1Amount >= 0);
}

// Mock of _PoolManager.modifyLiquidity() to reduce complexity
function _modifyLiquidityMockCLV(
    env e, PoolManager.PoolKey key, IPoolManager.ModifyLiquidityParams params, bytes hookData
) returns (PoolManager.BalanceDelta, PoolManager.BalanceDelta) {

    // Calculate hashed pool and position IDs
    bytes32 poolId = _HelperCVL.poolKeyToId(key);
    bytes32 positionId = _HelperCVL.positionKey(e.msg.sender, params.tickLower, params.tickUpper, params.salt);

    // Require valid range of ticks
    require(isValidTicksCVL(params.tickLower, params.tickUpper));

    // Require pool is initialized
    require(ghostPoolsSlot0SqrtPriceX96[poolId] != 0);

    // Update the position liquidity
    ghostPoolsPositionsLiquidity[poolId][positionId] = require_uint128(
        ghostPoolsPositionsLiquidity[poolId][positionId] + params.liquidityDelta
        );

    // Update the active pool liquidity
    if(isActivePositionInPoolCVL(poolId, params.tickLower, params.tickUpper)) {
        ghostPoolsLiquidity[poolId] = require_uint128(ghostPoolsLiquidity[poolId] + params.liquidityDelta);
    }
    
    // Declare random currency deltas for the caller and the provided pool hook address
    int128 amount0Principal;
    int128 amount1Principal;
    int128 amount0Fees;
    int128 amount1Fees;
    int128 amount0Hook;
    int128 amount1Hook;

    // No hooks used
    require(key.hooks == 0 => amount0Hook == 0 && amount1Hook == 0);

    // Restrict the amounts based on provided liquidity delta:
    modifyLiquidityAmountsConditionsCVL(
        poolId, amount0Principal, amount1Principal, amount0Fees, amount1Fees, params.liquidityDelta
        );

    int128 amount0Caller = require_int128(amount0Principal + amount0Fees);
    int128 amount1Caller = require_int128(amount1Principal + amount1Fees);

    // Fee shouldn't cancel out whole principal
    require(amount0Principal != 0 => amount0Caller != 0);
    require(amount1Principal != 0 => amount1Caller != 0);

    PoolManager.BalanceDelta callerDelta = amountsToBalanceDeltaCVL(amount0Caller, amount1Caller);
    PoolManager.BalanceDelta feesAccrued = amountsToBalanceDeltaCVL(amount0Fees, amount1Fees);

    // Set currency deltas for msg.sender (position owner) and pool hook
    _PoolManager.accountPoolBalanceDeltaHarness(e, key, callerDelta, e.msg.sender);
    _PoolManager.accountPoolBalanceDeltaHarness(e, key, amountsToBalanceDeltaCVL(amount0Hook, amount1Hook), key.hooks);

    return (callerDelta, feesAccrued);
}

function modifyLiquidityCLV(
    env e, PoolManager.PoolKey key, IPoolManager.ModifyLiquidityParams params, bytes hookData
    ) returns (PoolManager.BalanceDelta, PoolManager.BalanceDelta) {
    
    // Safe assumptions about environment
    require(isValidEnvCVL(e));

    // Assume pool was initialized with valid pool key
    require(isValidKeyCVL(key));

    // Empty hook data
    require(isEmptyHookDataCVL(hookData));

    PoolManager.BalanceDelta callerDelta;
    PoolManager.BalanceDelta feesAccrued;

    // Use Mock for _PoolManager.modifyLiquidity() call to reduce complexity
    callerDelta, feesAccrued = _modifyLiquidityMockCLV(e, key, params, hookData);
    
    return (callerDelta, feesAccrued);
}

// Insert here a list of requirements that correlate the token amounts for swapping
function swapAmountsConditionsCVL(
    bytes32 poolId,
    bool zeroForOne,
    int256 amountSpecified,
    int128 currency0Amount,
    int128 currency1Amount
) {
    // potential assumptions: direction of swapping: shouldn’t be getting both tokens and shouldn’t be giving both tokens
    require(true);
}

// Change the havoc statements here that will dictate how the pool state changes
function updatePoolStateOnSwapCVL(
    bytes32 poolId,
    bool zeroForOne,
    uint160 sqrtPriceLimitX96,
    int128 currency0Amount,
    int128 currency1Amount 
) {
    /*
    Alternatively, one can declare a random variable and assign:
        int24 newTick;  poolTick[poolId] = newTick;
        uint160 newSqrtPrice;  poolTick[poolId] = newSqrtPrice;
        uint128 newLiquidity;  liquidityPerPool[poolId] = newLiquidity;
    */

    havoc ghostPoolsSlot0Tick assuming forall bytes32 poolIdA.
        (poolIdA != poolId => ghostPoolsSlot0Tick@new[poolIdA] == ghostPoolsSlot0Tick@old[poolIdA]);
    
    havoc ghostPoolsSlot0SqrtPriceX96 assuming forall bytes32 poolIdA.
        (poolIdA != poolId => ghostPoolsSlot0SqrtPriceX96@new[poolIdA] == ghostPoolsSlot0SqrtPriceX96@old[poolIdA]);

    havoc ghostPoolsLiquidity assuming forall bytes32 poolIdA.
        (poolIdA != poolId => ghostPoolsLiquidity@new[poolIdA] == ghostPoolsLiquidity@old[poolIdA]);
}

// Mock of _PoolManager.swap() to reduce complexity
function _swapMockCVL(
    env e, PoolManager.PoolKey key, IPoolManager.SwapParams params, bytes hookData
    ) returns PoolManager.BalanceDelta {
    
    // Require nonzero amount specified
    require(isValidSwapParamsCVL(params));

    // Calculate hashed pool and position IDs.
    bytes32 poolId = _HelperCVL.poolKeyToId(key);
    
    // Declare random currency deltas for the caller and the provided pool hook address.
    int128 amount0Swapper;
    int128 amount1Swapper;
    int128 amount0Hook;
    int128 amount1Hook;
    int128 amount0Principal = require_int128(amount0Swapper + amount0Hook);
    int128 amount1Principal = require_int128(amount1Swapper + amount1Hook);

    // No hooks used
    require(key.hooks == 0 => amount0Hook == 0 && amount1Hook == 0);

    // Restrict the amounts based on provided swap details
    swapAmountsConditionsCVL(poolId, params.zeroForOne, params.amountSpecified, amount0Principal, amount1Principal);

    // Update the pool state post-swap
    updatePoolStateOnSwapCVL(poolId, params.zeroForOne, params.sqrtPriceLimitX96, amount0Principal, amount1Principal);

    PoolManager.BalanceDelta swapDelta;
    swapDelta = amountsToBalanceDeltaCVL(amount0Swapper, amount1Swapper);

    // Set currency deltas for msg.sender (position owner) and pool hook
    _PoolManager.accountPoolBalanceDeltaHarness(e, key, swapDelta, e.msg.sender);
    _PoolManager.accountPoolBalanceDeltaHarness(e, key, amountsToBalanceDeltaCVL(amount0Hook, amount1Hook), key.hooks);

    return swapDelta;
}

function swapCVL(
    env e, PoolManager.PoolKey key, IPoolManager.SwapParams params, bytes hookData
    ) returns PoolManager.BalanceDelta {
    
    PoolManager.BalanceDelta delta;

    // Safe assumptions about environment
    require(isValidEnvCVL(e));

    // Assume pool was initialized with valid pool key
    require(isValidKeyCVL(key));
    
    // Empty hook data
    require(isEmptyHookDataCVL(hookData));

    // Use mock instead of _PoolManager.swap() to reduce complexity
    delta = _swapMockCVL(e, key, params, hookData);

    return delta;
}

function donateCVL(
    env e, PoolManager.PoolKey key, uint256 amount0, uint256 amount1, bytes hookData
    ) returns PoolManager.BalanceDelta {

    // Safe assumptions about environment
    require(isValidEnvCVL(e));

    // Assume pool was initialized with valid pool key
    require(isValidKeyCVL(key));
    
    // Empty hook data
    require(isEmptyHookDataCVL(hookData));

    return _PoolManager.donate(e, key, amount0, amount1, hookData);
}

function syncCVL(env e, PoolManager.Currency currency) {

    // Safe assumptions about environment
    require(isValidEnvCVL(e));

    // Assume only supported in this environment currencies are passed
    require(isValidTokenCVL(currency));

    _PoolManager.sync(e, currency);
}

function takeCVL(env e, PoolManager.Currency currency, address to, uint256 amount) {

    // Safe assumptions about environment
    require(isValidEnvCVL(e));

    // Assume only supported in this environment currencies are passed
    require(isValidTokenCVL(currency));

    _PoolManager.take(e, currency, to, amount);
}

function settleCVL(env e) returns uint256 {

    // Safe assumptions about environment
    require(isValidEnvCVL(e));

    return _PoolManager.settle(e);
}

function settleForCVL(env e, address recipient) returns uint256 {

    // Safe assumptions about environment
    require(isValidEnvCVL(e));

    return _PoolManager.settleFor(e, recipient);
}

function clearCVL(env e, PoolManager.Currency currency, uint256 amount) {

    // Safe assumptions about environment
    require(isValidEnvCVL(e));

    // Assume only supported in this environment currencies are passed
    require(isValidTokenCVL(currency));

    _PoolManager.clear(e, currency, amount);
}

function mintCVL(env e, address to, uint256 id, uint256 amount) {

    // Safe assumptions about environment
    require(isValidEnvCVL(e));

    // Assume only supported in this environment currencies are passed
    require(isValidTokenCVL(_HelperCVL.fromId(id)));

    _PoolManager.mint(e, to, id, amount);
}

function burnCVL(env e, address from, uint256 id, uint256 amount) {

    // Safe assumptions about environment
    require(isValidEnvCVL(e));

    // Assume only supported in this environment currencies are passed
    require(isValidTokenCVL(_HelperCVL.fromId(id)));

    _PoolManager.burn(e, from, id, amount);
}

function updateDynamicLPFeeCVL(env e, PoolManager.PoolKey key, uint24 newDynamicLPFee) {

    // Safe assumptions about environment
    require(isValidEnvCVL(e));

    // Assume pool was initialized with valid pool key
    require(isValidKeyCVL(key));

    _PoolManager.updateDynamicLPFee(e, key, newDynamicLPFee);
}

function setProtocolFeeCVL(env e, PoolManager.PoolKey key, uint24 newProtocolFee) {

    // Safe assumptions about environment
    require(isValidEnvCVL(e));

    // Assume pool was initialized with valid pool key
    require(isValidKeyCVL(key));

    _PoolManager.setProtocolFee(e, key, newProtocolFee);
}

function collectProtocolFeesCVL(env e, address recipient, PoolManager.Currency currency, uint256 amount) returns uint256 {

    // Safe assumptions about environment
    require(isValidEnvCVL(e));

    // Assume only supported in this environment currencies are passed
    require(isValidTokenCVL(currency));

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

// Mock of TickMath.getTickAtSqrtPrice() to reduce complexity
function getTickAtSqrtPriceCVL(uint160 sqrtPriceX96) returns int24 {

    int24 tick;
    require(isValidTickCVL(tick));

    return tick;
}

////////////////////////////////////////// Hooks //////////////////////////////////////////////

//
// PoolManager
//

// _pools[].slot0

persistent ghost mapping (bytes32 => uint256) ghostPoolsSlot0 {
    init_state axiom forall bytes32 id. ghostPoolsSlot0[id] == 0;
}

persistent ghost mapping (bytes32 => mathint) ghostPoolsSlot0SqrtPriceX96 {
    init_state axiom forall bytes32 id. ghostPoolsSlot0SqrtPriceX96[id] == 0;
}

persistent ghost mapping (bytes32 => mathint) ghostPoolsSlot0Tick {
    init_state axiom forall bytes32 id. ghostPoolsSlot0Tick[id] == 0;
}

persistent ghost mapping (bytes32 => mathint) ghostPoolsSlot0ProtocolFeeZeroForOne {
    init_state axiom forall bytes32 id. ghostPoolsSlot0ProtocolFeeZeroForOne[id] == 0;
}

persistent ghost mapping (bytes32 => mathint) ghostPoolsSlot0ProtocolFeeOneForZero {
    init_state axiom forall bytes32 id. ghostPoolsSlot0ProtocolFeeOneForZero[id] == 0;
}

persistent ghost mapping (bytes32 => mathint) ghostPoolsSlot0LpFee {
    init_state axiom forall bytes32 id. ghostPoolsSlot0LpFee[id] == 0;
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
    init_state axiom forall bytes32 i. ghostPoolsLiquidity[i] == 0;
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
    init_state axiom forall bytes32 i. forall bytes32 j. ghostPoolsPositionsLiquidity[i][j] == 0;
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

//
// ProtocolFees
//

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

//
// ERC6909
//

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