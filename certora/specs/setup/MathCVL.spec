// Math CVL helpers are designed to optimize Prover time

methods {

    function _.mulDiv(uint256 a, uint256 b, uint256 denominator) internal
        => mulDivDownCVL(a, b, denominator) expect uint256 ALL;
    function _.mulDivRoundingUp(uint256 a, uint256 b, uint256 denominator) internal 
        => mulDivUpCVL(a,b,denominator) expect uint256 ALL;
    function _.divRoundingUp(uint256 x, uint256 y) internal
        => divUpCVL(x, y) expect uint256 ALL;
}

function divUpCVL(uint256 x, uint256 y) returns uint256 {
    assert(y !=0, "divUp error: cannot divide by zero");
    return require_uint256((x + y - 1) / y);
}

function mulDivDownCVL(uint256 x, uint256 y, uint256 z) returns uint256 {
    assert(z !=0, "mulDivDown error: cannot divide by zero");
    return require_uint256(x * y / z);
}

function mulDivUpCVL(uint256 x, uint256 y, uint256 z) returns uint256 {
    assert(z !=0, "mulDivDown error: cannot divide by zero");
    return require_uint256((x * y + z - 1) / z);
}