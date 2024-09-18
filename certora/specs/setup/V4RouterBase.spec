import "./PoolManagerBase.spec";

using V4RouterHarness as _V4Router;

methods {

    // IERC20Minimal
    function _.transferFrom(address sender, address recipient, uint256 amount) external with (env e)
        => transferFromCVL(e, calledContract, sender, recipient, amount, true) expect bool;
}