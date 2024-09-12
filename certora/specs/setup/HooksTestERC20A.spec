using TestERC20A as _ERC20A;


// Ghost copy of `balanceOf`

persistent ghost mapping (address => mathint) ghostERC20ABalances {
    init_state axiom forall address i. ghostERC20ABalances[i] == 0;
    axiom forall address i. ghostERC20ABalances[i] >= 0 && ghostERC20ABalances[i] <= max_uint256;
}

hook Sload uint256 val _ERC20A.balanceOf[KEY address i] {
    require(require_uint256(ghostERC20ABalances[i]) == val);
} 

hook Sstore _ERC20A.balanceOf[KEY address i] uint256 val {
    ghostERC20ABalances[i] = val;
}

// Ghost copy of `allowance`

persistent ghost mapping(address => mapping(address => mathint)) ghostERC20AAllowances {
    init_state axiom forall address key. forall address val. ghostERC20AAllowances[key][val] == 0;
    axiom forall address key. forall address val. 
        ghostERC20AAllowances[key][val] >= 0 && ghostERC20AAllowances[key][val] <= max_uint256;
}

hook Sload uint256 amount _ERC20A.allowance[KEY address key][KEY address val] {
    require(require_uint256(ghostERC20AAllowances[key][val]) == amount);
}

hook Sstore _ERC20A.allowance[KEY address key][KEY address val] uint256 amount {
    ghostERC20AAllowances[key][val] = amount;
}
