methods {

    // TransientStateLibrary
    //  - read values from storage hooks ghost variables directly as PoolManager's extsload()/exttload() are removed
    
    function TransientStateLibrary.currencyDelta(
        address manager,
        address target,
        PoolManager.Currency currency
    ) internal returns (int256)
        => currencyDeltaCVL(target, currency);
    /*
    function TransientStateLibrary.getSyncedReserves(
        address manager
    ) internal returns (uint256)
        => getSyncedReservesCVL();

    function TransientStateLibrary.getSyncedCurrency(
        address manager
    ) internal returns (PoolManager.Currency)
        => getSyncedCurrencyCVL();

    function TransientStateLibrary.getNonzeroDeltaCount(
        address manager
    ) internal returns (uint256)
        => getNonzeroDeltaCountCVL();

    function TransientStateLibrary.isUnlocked(
        address manager
    ) internal returns (bool)
        => isUnlockedCVL();
    */
}

function currencyDeltaCVL(address target, PoolManager.Currency currency) returns int256 {
    return ghostCurrencyDelta[target][_HelperCVL.fromCurrency(currency)];
}

/*
function getSyncedReservesCVL() returns uint256 {
    return require_uint256(ghostSyncedReserves);
}

function getSyncedCurrencyCVL() returns PoolManager.Currency {
    return _HelperCVL.toCurrency(ghostSyncedCurrency);
}

function getNonzeroDeltaCountCVL() returns uint256 {
    return require_uint256(ghostNonzeroDeltaCount);
}

function isUnlockedCVL() returns bool {
    return ghostLock;
}
*/