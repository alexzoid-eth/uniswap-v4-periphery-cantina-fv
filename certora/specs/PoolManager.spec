import "./setup/PoolManagerBase.spec";
import "./PoolManagerValidState.spec";

use builtin rule sanity filtered { f -> f.contract == currentContract }