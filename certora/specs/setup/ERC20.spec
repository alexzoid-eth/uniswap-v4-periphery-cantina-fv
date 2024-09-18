// Require only usage of ERC20A, ERC20B, ERC20C or address(0) native currency

persistent ghost address ghostERC20A {
    init_state axiom ghostERC20A != NATIVE_CURRENCY() && ghostERC20A != currentContract && ghostERC20A != _PoolManager
        && ghostERC20A < ghostERC20B && ghostERC20A < ghostERC20C;
    axiom ghostERC20A != NATIVE_CURRENCY() && ghostERC20A != currentContract && ghostERC20A != _PoolManager
        && ghostERC20A < ghostERC20B && ghostERC20A < ghostERC20C;
}

persistent ghost address ghostERC20B {
    init_state axiom ghostERC20B != NATIVE_CURRENCY() && ghostERC20B != currentContract && ghostERC20B != _PoolManager
        && ghostERC20B > ghostERC20A && ghostERC20B < ghostERC20C;
    axiom ghostERC20B != NATIVE_CURRENCY() && ghostERC20B != currentContract && ghostERC20B != _PoolManager
        && ghostERC20B > ghostERC20A && ghostERC20B < ghostERC20C;
}

persistent ghost address ghostERC20C {
    init_state axiom ghostERC20C != NATIVE_CURRENCY() && ghostERC20C != currentContract && ghostERC20C != _PoolManager
        && ghostERC20C > ghostERC20A && ghostERC20C > ghostERC20B;
    axiom ghostERC20C != NATIVE_CURRENCY() && ghostERC20C != currentContract && ghostERC20C != _PoolManager
        && ghostERC20C > ghostERC20A && ghostERC20C > ghostERC20B;
}

// Support only NATIVE, ERC20A, ERC20B or ERC20C tokens
function isValidTokenCVL(address token) returns bool {
    return (token == NATIVE_CURRENCY() || token == ghostERC20A || token == ghostERC20B || token == ghostERC20C);
}

// Ghost copy of `balanceOf`

persistent ghost mapping(address => mapping(address => mathint)) ghostERC20Balances {
    init_state axiom forall address token. forall address owner. ghostERC20Balances[token][owner] == 0;
    axiom forall address token. forall address owner. ghostERC20Balances[token][owner] >= 0 
        && ghostERC20Balances[token][owner] <= max_uint256;
}

// Ghost copy of `allowance`

persistent ghost mapping(address => mapping(address => mapping(address => mathint))) ghostERC20Allowances {
    init_state axiom forall address token. forall address owner. forall address spender. 
        ghostERC20Allowances[token][owner][spender] == 0;
    axiom forall address token. forall address owner. forall address spender. 
        ghostERC20Allowances[token][owner][spender] >= 0 && ghostERC20Allowances[token][owner][spender] <= max_uint256;
}

// Balance of owner

function balanceOfCVL(env e, address token, address owner) returns uint256 {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Support only NATIVE, ERC20A, ERC20B or ERC20C currencies
    require(isValidTokenCVL(token));

    return token == NATIVE_CURRENCY() ? nativeBalances[owner] : require_uint256(ghostERC20Balances[token][owner]);
}

// Transfer tokens

function transferFromCVL(env e, address token, address from, address to, uint256 amount, bool transferFrom) returns bool {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Support only NATIVE, ERC20A, ERC20B or ERC20C currencies
    require(isValidTokenCVL(token));

    if(token == NATIVE_CURRENCY()) {
        assert(transferFrom == false, "transferFrom() not allowed from native currency");
        _HelperCVL.transferEther(e, to, amount);
    } else {
        if(transferFrom) {
            require(ghostERC20Allowances[token][from][to] >= amount);
            ghostERC20Allowances[token][from][to] = assert_uint256(ghostERC20Allowances[token][from][to] - amount);
        }

        require(ghostERC20Balances[token][from] >= amount);
        ghostERC20Balances[token][from] = assert_uint256(ghostERC20Balances[token][from] - amount);
        ghostERC20Balances[token][to] = require_uint256(ghostERC20Balances[token][to] + amount);
    }

    return true;
}

function transferFromNoRetCVL(env e, address token, address from, address to, uint256 amount, bool transferFrom) {
    transferFromCVL(e, token, from, to, amount, transferFrom);
}