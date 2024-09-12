import "./PoolManagerBase.spec";

using PositionManagerHarness as _PositionManager;


methods {

    // @todo
    // - permit2.transferFrom
    // 

    // Removed external functions
    // - modifyLiquidities(), modifyLiquiditiesWithoutUnlock() and unlockCallback() not needed as _handleAction is 
    //  no-op and summarizing unlock here would have no effect
    // - multicall() temporary removed
    // - permit()/permitBatch() temporary removed

    function _PositionManager.modifyLiquidities(bytes unlockData, uint256 deadline) external 
        => NONDET DELETE;

    function _PositionManager.modifyLiquiditiesWithoutUnlock(bytes actions, bytes[] params) external
        => NONDET DELETE;

    function _PositionManager.unlockCallback(bytes data) external returns (bytes) 
        => NONDET DELETE;

    function _PositionManager.multicall(bytes[] calldata data) external returns (bytes[])
        => NONDET DELETE;

    function _PositionManager.permit(
        address owner, IAllowanceTransfer.PermitSingle permitSingle, bytes signature
    ) external returns (bytes) => NONDET DELETE;

    function _PositionManager.permitBatch(
        address owner, IAllowanceTransfer.PermitBatch _permitBatch, bytes signature
    ) external returns (bytes) => NONDET DELETE;


}