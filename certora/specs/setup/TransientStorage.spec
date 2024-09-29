//
// PoolManager.CurrencyDelta
//

methods {
    // Summarize slot computing with CVL mapping
    function CurrencyDelta._computeSlot(address target, PoolManager.Currency currency) internal returns (bytes32)
        => computeSlotCVL(target, currency);
}

persistent ghost mapping (address => mapping(address => int256)) ghostCurrencyDelta;

ghost address _ghostLastTarget;
ghost address _ghostLastCurrency;
ghost bytes32 _ghostLastSlot;

function computeSlotCVL(address target, address currency) returns bytes32 {
    _ghostLastTarget = target;
    _ghostLastCurrency = currency;
    _ghostLastSlot = keccak256(target, currency);
    return _ghostLastSlot;
}

//
// PoolManager.CurrencyReserves
//

definition CURRENCY_SLOT() returns uint256 = 0x27e098c505d44ec3574004bca052aabf76bd35004c182099d8c575fb238593b9;
definition RESERVES_OF_SLOT() returns uint256 = 0x1e0745a7db1623981f0b2a5d4232364c00787266eb75ad546f190e6cebe9bd95;

persistent ghost address ghostSyncedCurrency;
persistent ghost mathint ghostSyncedReserves {
    axiom ghostSyncedReserves >= 0 && ghostSyncedReserves <= max_uint256;
}

//
// PoolManager.Lock
//

definition IS_UNLOCKED_SLOT() returns uint256 = 0xc090fc4683624cfc3884e9d8de5eca132f2d0ec062aff75d43c0465d5ceeab23;

persistent ghost bool ghostLock;

//
// PoolManager.NonzeroDeltaCount
//

definition NONZERO_DELTA_COUNT_SLOT() returns uint256 = 0x7d4b3164c6e45b97e7d87b7125a44c5828d005af88f9d751cfd78729c5d99a0b;

persistent ghost mathint ghostNonzeroDeltaCount {
    axiom ghostNonzeroDeltaCount >= 0 && ghostNonzeroDeltaCount <= max_uint256;
}

//
// PositionManager.Locker
//

definition LOCKED_BY_SLOT() returns uint256 = 0x0aedd6bde10e3aa2adec092b02a3e3e805795516cda41f27aa145b8f300af87a;

persistent ghost address ghostLocker {
    init_state axiom ghostLocker == 0;
    axiom ghostLocker != _PoolManager && ghostLocker != _PositionManager;
}

persistent ghost bool ghostLockerSet {
    init_state axiom ghostLockerSet == false;
}


//
// Global hooks
//

hook ALL_TSTORE(uint256 addr, uint256 val) {
    if(executingContract == _PoolManager) {
        if(to_bytes32(addr) == _ghostLastSlot) {
            ghostCurrencyDelta[_ghostLastTarget][_ghostLastCurrency] = require_int256(val);
        } else if (addr == CURRENCY_SLOT()) {
            ghostSyncedCurrency = require_address(to_bytes32(val));
        } else if (addr == RESERVES_OF_SLOT()) {
            ghostSyncedReserves = val;
        } else if(addr == IS_UNLOCKED_SLOT()) {
            ghostLock = require_uint8(val) > 0 ? true : false;
        } else if (addr == NONZERO_DELTA_COUNT_SLOT()) {
            ghostNonzeroDeltaCount = val;
        }  
    } else { // PositionManager
        if(addr == LOCKED_BY_SLOT()) {
            ghostLockerSet = (val != 0);
            if(ghostLockerSet) {
                ghostLocker = require_address(to_bytes32(val));
            } 
        }
    }
}

hook ALL_TLOAD(uint256 addr) uint256 val {
    if(executingContract == _PoolManager) {
        if(to_bytes32(addr) == _ghostLastSlot) {
            require(ghostCurrencyDelta[_ghostLastTarget][_ghostLastCurrency] == require_int256(val));
        } else if (addr == CURRENCY_SLOT()) {
            require(ghostSyncedCurrency == require_address(to_bytes32(val)));
        } else if (addr == RESERVES_OF_SLOT()) {
            require(require_uint256(ghostSyncedReserves) == val);
        } else if(addr == IS_UNLOCKED_SLOT()) {
            require(require_uint8(val) > 0 ? ghostLock == true : ghostLock == false);
        } else if (addr == NONZERO_DELTA_COUNT_SLOT()) {
            require(require_uint256(ghostNonzeroDeltaCount) == val);
        } 
    } else { // PositionManager
        if(addr == LOCKED_BY_SLOT()) {
            require(ghostLocker == require_address(to_bytes32(val)));
        }
    }
}