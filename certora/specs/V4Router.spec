import "./setup/V4RouterBase.spec";
import "./PoolManagerValidState.spec";

use builtin rule sanity filtered { f -> f.contract == currentContract }

use invariant validSqrtPriceX96Range;