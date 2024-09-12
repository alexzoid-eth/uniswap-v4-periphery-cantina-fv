using TestERC20B as _ERC20B;

// Ghost copy of `balanceOf`

persistent ghost mapping (address => mathint) ghostERC20BBalances {
    init_state axiom forall address i. ghostERC20BBalances[i] == 0;
    axiom forall address i. ghostERC20BBalances[i] >= 0 && ghostERC20BBalances[i] <= max_uint256;
}

hook Sload uint256 val _ERC20B.balanceOf[KEY address i] {
    require(require_uint256(ghostERC20BBalances[i]) == val);
} 

hook Sstore _ERC20B.balanceOf[KEY address i] uint256 val {
    ghostERC20BBalances[i] = val;
}

// Ghost copy of `allowance`

persistent ghost mapping(address => mapping(address => mathint)) ghostERC20BAllowances {
    init_state axiom forall address key. forall address val. ghostERC20BAllowances[key][val] == 0;
    axiom forall address key. forall address val. 
        ghostERC20BAllowances[key][val] >= 0 && ghostERC20BAllowances[key][val] <= max_uint256;
}

hook Sload uint256 amount _ERC20B.allowance[KEY address key][KEY address val] {
    require(require_uint256(ghostERC20BAllowances[key][val]) == amount);
}

hook Sstore _ERC20B.allowance[KEY address key][KEY address val] uint256 amount {
    ghostERC20BAllowances[key][val] = amount;
}
