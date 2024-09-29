// Any chance that non-view function modifies state (valuable when `memory` keyword mistakenly 
//  was used instead of `storage` in setters among with event emitting)
rule chanceNonViewFunctionModifiesState(env e, method f, calldataarg args) 
    filtered { f -> !f.isView && !f.isPure } {

    storage before = lastStorage;

    f(e, args);

    storage after = lastStorage;

    satisfy(before != after);
}