methods {

    // Require only usage of ERC20A, ERC20B, ERC20C or address(0) native currency

    // CurrencyLibrary
    function CurrencyLibrary.transfer(PoolManager.Currency currency, address to, uint256 amount) internal with (env e) 
        => transferNotRetCVL(e, currency, to, amount);
    function CurrencyLibrary.balanceOfSelf(PoolManager.Currency currency) internal returns (uint256) with (env e) 
        => balanceOfSelfCVL(e, currency, calledContract);
    // function CurrencyLibrary.balanceOf(PoolManager.Currency currency, address owner) internal returns (uint256) with (env e) 
    //    => balanceOfCVL(e, currency, owner);   

    // IERC20Minimal
    function _.transferFrom(address sender, address recipient, uint256 amount) external with (env e)
        => transferFromCVL(e, calledContract, sender, recipient, amount) expect bool;
}

function transferCVL(env e, address currency, address to, uint256 amount) returns bool {

    bool result;

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Support only NATIVE, ERC20A, ERC20B or ERC20C currencies
    requireValidCurrencyAddressCVL(currency);

    if(currency == 0) {
        _HelperCVL.transferEther(e, to, amount);
        result = true;
    } else if(currency == _ERC20A) {
        result = _ERC20A.transfer(e, to, amount);
    } else if(currency == _ERC20B) {
        result = _ERC20B.transfer(e, to, amount);
    } else {
        result = _ERC20C.transfer(e, to, amount);
    }

    return result;
}

function transferNotRetCVL(env e, address currency, address to, uint256 amount) {
    transferCVL(e, currency, to, amount);
}

function balanceOfSelfCVL(env e, address currency, address owner) returns uint256 {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Support only NATIVE, ERC20A, ERC20B or ERC20C currencies
    requireValidCurrencyAddressCVL(currency);

    uint256 balance;

    if(currency == 0) {
        balance = nativeBalances[owner];
    } else if(currency == _ERC20A) {
        balance = _ERC20A.balanceOf(e, owner);
    } else if(currency == _ERC20B) {
        balance = _ERC20B.balanceOf(e, owner);
    } else {
        balance = _ERC20C.balanceOf(e, owner);
    }

    return balance;
}

function balanceOfCVL(env e, address currency, address owner) returns uint256 {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Support only NATIVE, ERC20A, ERC20B or ERC20C currencies
    requireValidCurrencyAddressCVL(currency);

    uint256 balance;

    if(currency == 0) {
        balance = nativeBalances[owner];
    } else if(currency == _ERC20A) {
        balance = _ERC20A.balanceOf(e, owner);
    } else if(currency == _ERC20B) {
        balance = _ERC20B.balanceOf(e, owner);
    } else {
        balance = _ERC20C.balanceOf(e, owner);
    }

    return balance;
}

function transferFromCVL(env e, address currency, address sender, address recipient, uint256 amount) returns bool {

    // Safe assumptions about environment
    requireValidEnvCVL(e);

    // Support only NATIVE, ERC20A, ERC20B or ERC20C currencies
    requireValidCurrencyAddressCVL(currency);

    if(currency == 0) {
        assert(false, "currency could not be native here");
    } else if(currency == _ERC20A) {
        _ERC20A.transferFrom(e, sender, recipient, amount);
    } else if(currency == _ERC20B) {
        _ERC20B.transferFrom(e, sender, recipient, amount);
    } else {
        _ERC20C.transferFrom(e, sender, recipient, amount);
    }

    return true;
}

function transferFromNoRetCVL(env e, address currency, address sender, address recipient, uint256 amount) {
    transferFromCVL(e, currency, sender, recipient, amount);
}