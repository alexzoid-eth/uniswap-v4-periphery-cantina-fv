using TestERC20C as _ERC20C;

// Ghost copy of `balanceOf`

persistent ghost mapping (address => mathint) ghostERC20CBalances {
    init_state axiom forall address i. ghostERC20CBalances[i] == 0;
    axiom forall address i. ghostERC20CBalances[i] >= 0 && ghostERC20CBalances[i] <= max_uint256;
}

hook Sload uint256 val _ERC20C.balanceOf[KEY address i] {
    require(require_uint256(ghostERC20CBalances[i]) == val);
} 

hook Sstore _ERC20C.balanceOf[KEY address i] uint256 val {
    ghostERC20CBalances[i] = val;
}

// Ghost copy of `allowance`

persistent ghost mapping(address => mapping(address => mathint)) ghostERC20CAllowances {
    init_state axiom forall address key. forall address val. ghostERC20CAllowances[key][val] == 0;
    axiom forall address key. forall address val. 
        ghostERC20CAllowances[key][val] >= 0 && ghostERC20CAllowances[key][val] <= max_uint256;
}

hook Sload uint256 amount _ERC20C.allowance[KEY address key][KEY address val] {
    require(require_uint256(ghostERC20CAllowances[key][val]) == amount);
}

hook Sstore _ERC20C.allowance[KEY address key][KEY address val] uint256 amount {
    ghostERC20CAllowances[key][val] = amount;
}
