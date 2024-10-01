# Properties

**Category**: List of properties following the categorization by [Certora](https://github.com/Certora/Tutorials/blob/master/06.Lesson_ThinkingProperties/Categorizing_Properties.pdf):

- High Level
- Valid State
- State Transition
- Variable Transition
- Unit Test

## PositionManager

### Valid State

The properties below are categorized as valid state properties, which can be used to assume a valid storage state in other high-level properties.

| Property | Description | Category |
| --- | --- | --- |
| [PMV-01](./specs/PositionManagerValidState.spec#L87) | The next token ID MUST always be greater than or equal to 1 | Valid State |
| [PMV-02](./specs/PositionManagerValidState.spec#L91) | Position information and token MUST NOT exist for token ID 0 or any future token IDs | Valid State |
| [PMV-03](./specs/PositionManagerValidState.spec#L101) | Active position ticks MUST be within the valid range defined by TickMath | Valid State |
| [PMV-04](./specs/PositionManagerValidState.spec#L115) | Active position MUST correspond minted token and vice versa | Valid State |
| [PMV-05](./specs/PositionManagerValidState.spec#L126) | Active position MUST correspond to valid pool key | Valid State |
| [PMV-06](./specs/PositionManagerValidState.spec#L159) | Active position must correspond to a initialized pool in PoolManager | Valid State |
| [PMV-07](./specs/PositionManagerValidState.spec#L186) | Touched pool key must correspond to a initialized pool in PoolManager | Valid State |
| [PMV-08](./specs/PositionManagerValidState.spec#L198) | All poolKey fields must contain valid and consistent values | Valid State |
| [PMV-09](./specs/PositionManagerValidState.spec#L215) | The token ID in PositionManager always matches the position ID in PoolManager | Valid State |
| [PMV-10](./specs/PositionManagerValidState.spec#L228) | The subscriber token ID always matches the token ID passed to notifier callbacks | Valid State |
| [PMV-11](./specs/PositionManagerValidState.spec#L237) | Notifier callbacks are not called if nobody is subscribed to the token | Valid State |
| [PMV-12](./specs/PositionManagerValidState.spec#L255) | A subscription flag MUST be set when a valid subscriber address is present and vice versa | Valid State |
| [PMV-13](./specs/PositionManagerValidState.spec#L264) | Subscribers MUST only be set for existing token IDs | Valid State |
| [PMV-14](./specs/PositionManagerValidState.spec#L274) | Approvals for the zero address as owner are not allowed | Valid State |
| [PMV-15](./specs/PositionManagerValidState.spec#L283) | The zero address MUST NOT have any token balance | Valid State |
| [PMV-16](./specs/PositionManagerValidState.spec#L292) | Approved tokens MUST always correspond to existing token IDs | Valid State |

### Variable Transition

These properties focus on how individual variables change over time:

| Property | Description | Category |
| --- | --- | --- |
| [PM-01](./specs/PositionManager.spec#L14) | The nextTokenId value always increases monotonically, incrementing by exactly 1 when a new token is minted | Variable Transition |
| [PM-02](./specs/PositionManager.spec#L26) | The ticks in positionInfo remain constant for a given tokenId unless the position is cleared, in which case they are reset to zero | Variable Transition |
| [PM-03](./specs/PositionManager.spec#L50) | The poolId in positionInfo remains constant for a given tokenId unless the position is cleared, in which case it is reset to zero | Variable Transition |
| [PM-04](./specs/PositionManager.spec#L70) | A subscriber for a tokenId can only be set to a non-zero address once, and can only be unset to zero address afterwards | Variable Transition |
| [PM-05](./specs/PositionManager.spec#L84) | Once a nonce is set (used), it remains set and cannot be cleared or reused | Variable Transition |

## State Transition

These properties describe how the overall state of the contract changes:

| Property | Description | Category |
| --- | --- | --- |
| [PM-06](./specs/PositionManager.spec#L100) | The nextTokenId is updated if and only if a new token is minted, ensuring synchronization between token creation and ID assignment | State Transition |
| [PM-07](./specs/PositionManager.spec#L121) | A new token is minted if and only if a new position is created, and burned when the position is cleared, maintaining a one-to-one relationship between tokens and positions | State Transition |
| [PM-08](./specs/PositionManager.spec#L148) | Minting a new position increases the position's liquidity in the PoolManager, while burning a position decreases its liquidity | State Transition |
| [PM-09](./specs/PositionManager.spec#L182) | The poolKey associated with a poolId remains constant once set, and can only be set when the tickspacing is zero, ensuring consistency of pool parameters | State Transition |
| [PM-10](./specs/PositionManager.spec#L244) | A pool key can only be added when a new token is minted, preventing unauthorized pool creation | State Transition |
| [PM-11](./specs/PositionManager.spec#L292) | Notifier callbacks are executed only when the token owner changes or when the position's liquidity is modified | State Transition |
| [PM-12](./specs/PositionManager.spec#L382) | The contract only initiates token receives from the pool manager, preventing unauthorized token inflows | State Transition |
| [PM-13](./specs/PositionManager.spec#L403) | The contract never receives native tokens from the pool manager, ensuring proper asset segregation | State Transition |
| [PM-14](./specs/PositionManager.spec#L423) | Pair of tokens can only be settled from the locker and must be settled for the full amount owed by the contract | State Transition |

## High Level

These properties describe important high-level behaviors of the contract:

| Property | Description | Category |
| --- | --- | --- |
| [PM-15](./specs/PositionManager.spec#L480) | Only the token owner or approved addresses can modify the liquidity of a position, ensuring proper access control | High Level |
| [PM-16](./specs/PositionManager.spec#L514) | Only the token owner or approved addresses can transfer a token, maintaining ownership integrity | High Level |
| [PM-17](./specs/PositionManager.spec#L541) | Sweep is the only way to transfer tokens outside the contract, except for interactions with the PoolManager, preventing unauthorized token outflows | High Level |

## Unit Test

These properties verify specific, isolated behaviors:

| Property | Description | Category |
| --- | --- | --- |
| [PM-18](./specs/PositionManager.spec#L582) | Closing a position affects the balance of the locker, ensuring proper settlement of assets | Unit Test |
| [PM-19](./specs/PositionManager.spec#L607) | The sweep function must successfully output the specified currency to the designated recipient | Unit Test |
| [PM-20](./specs/PositionManager.spec#L645) | Any valid nonce can be used exactly once, preventing replay attacks | Unit Test |
| [PM-21](./specs/PositionManager.spec#L664) | A nonce cannot be successfully used more than once | Unit Test |
| [PM-22](./specs/PositionManager.spec#L679) | The destination address can always receive the token during a transfer | Unit Test |
| [PM-23](./specs/PositionManager.spec#L691) | The owner always receives the newly minted token | Unit Test |