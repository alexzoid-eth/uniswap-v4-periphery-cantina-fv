import "./PoolManagerBase.spec";
import "./TransientStateLibrary.spec";

using V4RouterHarness as _V4Router;

methods {

    // Removed external functions
    // - unlockCallback() not needed as _handleAction is no-op and summarizing unlock here would have no effect
    function _V4Router.unlockCallback(bytes data) external returns (bytes) => NONDET DELETE;
}