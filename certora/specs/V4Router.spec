import "./setup/V4RouterBase.spec";
import "./PoolManagerValidState.spec";

methods {

    // Not needed as _handleAction is no-op and summarizing unlock here would have no effect
    function _V4Router.unlockCallback(bytes data) external returns (bytes) => NONDET DELETE;
}

//
// Sanity
//

// Check if there is at least one path to execute an external function without a revert 
use builtin rule sanity filtered { f -> f.contract == currentContract }