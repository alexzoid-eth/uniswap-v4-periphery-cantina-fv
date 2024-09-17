import "./setup/PositionManagerBase.spec";
import "./PoolManagerValidState.spec";

use builtin rule sanity filtered { f -> f.contract == currentContract }