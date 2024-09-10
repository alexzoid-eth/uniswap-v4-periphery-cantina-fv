// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.26;

// Support `optimistic_fallback` flag (https://discord.com/channels/795999272293236746/1190407175877709864)
contract Receiver {
    fallback() external payable { }
}
