# Live Variables

!!! note "Unreleased Feature"
    Live variables have not yet been released. This chapter documents planned functionality that is not currently available.

Live variables represent a reactive programming paradigm in Verse,
enabling variables to automatically recompute their values when
dependencies change. Rather than requiring explicit callbacks or event
handlers, live variables establish dynamic relationships between data,
creating a declarative system where changes propagate naturally
through your code.

Traditional programming requires manual tracking of dependencies and
explicit updates when values change. If variable `A` depends on
variable `B`, you must remember to update `A` whenever `B` changes,
often through callback functions or observer patterns. Live variables
eliminate this bookkeeping by automatically tracking which variables
are read during evaluation and re-evaluating when those dependencies
change. This creates more maintainable code where the intent—that `A`
should always reflect some function of `B` — is expressed directly in
the code itself.

Live variables build a foundation for reactive programming constructs,
including `await`, `upon`, and `when`. Understanding live variables is
essential for working with Verse's event-driven programming model,
particularly for game development scenarios where many values must
stay synchronized.

## Live Expressions

A *live expression* establishes a dynamic relationship between a
variable and a guard. Once established, the target is automatically
re-evaluated whenever any of the guard's dependencies change, keeping
the variable in sync.

<!--versetest-->
<!-- 01-->
```verse
var X:int = 0
var Y:int = 0
set live X = Y+1  # X now tracks Y
set Y = 5         # X automatically becomes 6
```
<!--
X = 6
-->

In the above, `set live X = Y+1` is a live expression, the target is
the previously declared variable `X` and the guard is the expression
`Y+1` with a dependency on variable `Y`.

Live variables extend mutable variables (see
[Mutability](05_mutability.md)) with automated dependency tracking:
any variable read during the evaluation of the guard expression is
tracked. When any of those variables change, the guard is
re-evaluated, and the target variable updates automatically.

### Declaration Forms

Live variables can be declared in several ways, each suited to different use cases:

<!--NoCompile-->
<!-- 02-->
```verse
# Live variable declaration
var live X:int = Exp

# Live assignment to existing variable
var X:int = 0
# ... later ...
set live X = Exp

# Immutable live variable
live Y:int = Exp

# Variable with a function type (with <reads> effect)
var X: F = Exp            # Initial value computed normally
var live X: F = Exp       # Initial value tracked for dependencies

# Immutable variable with a function type (with <reads> effect)
X: F = Exp                # Initial value computed normally
live X: F = Exp           # Initial value tracked for dependencies

# Input-output variable pairs
var In->Out: F = Exp      # Initial value computed normally
var live In->Out: F = Exp # Initial value tracked for dependencies

In->Out: F = Exp          # Initial value computed normally
live In->Out: F = Exp     # Initial value tracked for dependencies
```

The most common form, `var live X = Exp`, creates a mutable variable
whose initial value comes from evaluating the guard and subsequently
updates whenever dependencies change. The guard expression can read
other variables, and those reads are tracked to establish the
dependency relationship.

The assignment form, `set live X = Exp`, converts an existing variable
into a live variable by attaching a guard. This is useful when you
need to make a variable reactive after initialization or conditionally
based on program state.

Immutable live variables, declared with just `live Y = Exp`, cannot be
directly written but still update automatically when their guard's
dependencies change. This provides a read-only reactive value, useful
for derived computations that should never be manually overridden.

When a variable's type is a function with the `<reads>` effect, the
variable becomes live through its type (assignments are filtered
through the function, and changes to the function's dependencies
trigger recalculation). The `live` keyword in the declaration
determines whether the initial expression `Exp` is also tracked for
dependencies. Without `live`, `Exp` is evaluated once; with `live`,
dependencies in `Exp` are tracked and can trigger updates before the
first assignment.

Input-output pairs create two variables where one captures raw values
and the other holds transformed values. Again, the `live` keyword
controls whether the initial expression `Exp` is tracked for
dependencies.

The following sections detail these more complex forms.

### Functions as Types

Verse allows functions to be used as types for variables. When a
function with the `<reads>` effect is used as a type, the variable
automatically becomes live, updating whenever the function's
dependencies change.

<!--versetest-->
<!-- 03 FAILURE
  Line 8: Script Error 3547: Expected a type, got function identifier instead.
  Line 8: Script Error 3601: Data definitions at this scope must be initialized with a value.
-->
```verse
var Mult:int = 2

Multiply(Arg: int)<reads>:int = Arg * Mult

var X : Multiply

set X = 10        # X gets 20
set Mult = 1      # X gets 10
```
<!--
X = 10
-->

In this example, `Multiply` serves dual roles: it's both a function
and a type for variable `X`.

**As a type:** When you declare `var X : Multiply`, several things happen:

- The storage type of `X` becomes `int` (the function's return type)
- Values assigned to `X` must be `int` (the function's parameter type)
- Each assignment passes through the function: `set X = 10` calls `Multiply(10)` and stores the result

**As a live expression:** Because `Multiply` has a `<reads>` effect
(it reads mutable variable `Mult`), the variable declaration becomes a
live expression with `Multiply` as its guard. This creates two ways
the value changes:

1. **Direct assignment:** `set X = 10` filters the value through `Multiply`, storing 20
2. **Dependency updates:** `set Mult = 1` triggers recalculation, updating `X` to 10

This pattern elegantly combines transformation (every write is
filtered) with reactivity (changes to dependencies trigger updates).

### Input-Output Variables

Input-output variable pairs capture both raw input values and their
transformed outputs. The syntax `var In->Out:F=Exp` creates two
related variables where `Out` is the writable variable and `In`
automatically stores the untransformed value before it passes through
function `F`.

This pattern elegantly handles common game scenarios where values must
stay within dynamic constraints. Consider health that must remain
within bounds:

<!--NoCompile-->
<!-- 04-->
```verse
clamp := class:
    var Lower:int = 0
    var Upper:int = 100
    Evaluate(Value:int)<reads>:int =
        if (Value < Upper) then:
           if (Value > Lower) then Value else Lower
        else:
           Upper

Clamp := clamp{}
var BaseHealth->Health: Clamp.Evaluate = 50

# Health = 50 (clamped to [0, 100])
set Health = 75      # BaseHealth = 75, Health = 75
set Health = 120     # BaseHealth = 120, Health = 100 (clamped)
set Clamp.Upper = 60 # BaseHealth = 120, Health = 60 (reclamped)
```

When you write to `Health`, two things happen:

 1. The raw value is stored in `BaseHealth`
 2. The value is passed through `Clamp.Evaluate`, and the result is stored in `Health`

Because `Clamp.Evaluate` has a `<reads>` effect (it reads the mutable
variables `Lower` and `Upper`), this becomes a live expression. When
the constraints change, `Health` is automatically recalculated from
`BaseHealth`.

**How It Works**

The declaration `var BaseHealth->Health: Clamp.Evaluate = 50` creates a live expression where:

- `BaseHealth` stores the raw input value (read-only from external perspective)
- `Health` stores the clamped value (read-write)
- `Clamp.Evaluate` is the transformation function with a `<reads>` effect

The object `Clamp` is an instance of class `clamp` with mutable bounds `Lower` and `Upper`. Because `Evaluate` reads these mutable variables, changes to them trigger recalculation:

- `set Health=75` — The value passes through unchanged, so both `BaseHealth` and `Health` become 75
- `set Health=120` — Exceeds `Upper`, so `BaseHealth` becomes 120 but `Health` becomes 100
- `set Clamp.Upper=60` — The constraint changes, triggering recalculation: `Health` updates to 60 while `BaseHealth` remains 120

Using an instance method like `Clamp.Evaluate` allows multiple
independent clamps in the same context, each with its own dynamic
bounds.

**Access Control**

The scope of input and output variables can be controlled
independently by adding access specifiers: for example `var
In<private>->Out<public>:t` makes the base value private while
exposing the constrained value publicly.

### Restricted Effects and Stability

Live variable guards cannot have `<writes>` or `<allocates>`
effects. This fundamental restriction prevents side effects during
guard evaluation, which Verse must be able to perform freely whenever
dependencies change.

<!--NoCompile-->
<!-- 05-->
```verse
# ERROR: guard cannot write
var X:int = 0
var GlobalCounter:int = 0
set live X = block:
    set GlobalCounter += 1  # Not allowed!
    GlobalCounter
```

Live variables with interdependencies can form cycles. When target
expressions use idempotent operations and values are comparable, these
cycles can naturally converge to fixed points.

<!--versetest-->
<!-- 06-->
```verse
var X:int = 2
var Y:int = 2

set live X = if (Y < 0) then 0 else Y - 1
set live Y = if (X < 0) then 0 else X - 1

# Evaluates as: X=1, Y=0, X=-1, Y=0 (stable)
```
<!--
X=-1
Y=0
-->

If the type of the variable is comparable, the guards are re-evaluated
until values stabilize. In this example, `X` decrements to -1, `Y`
clamps to 0, and `X` would recompute but produces -1 again, so the
system stabilizes.

However, cycles without proper termination conditions can
diverge. Verse cannot prevent all divergence—care must be taken when
designing interdependent live variables.

This has a subtle implication: since any variable might become live
after creation, reading any variable must be assumed to potentially
trigger guard evaluation and, in the worst case, trigger a cycle. The
effect system accounts for this: the `<writes>` effect implies
`<diverges>` because any write might trigger cyclic live variable
evaluation. The following illustrates a cyclic definition when `X` is
larger than 0:

<!--NoCompile-->
<!-- 07-->
```verse
var X:int = 0
var live Y:int = if (X>0) then X+1 else 0

set live X = Y
set X = 1  # Error! Cyclic evaluation
```

### Tracking Dependencies

Live variables track dependencies dynamically at runtime, not statically from source code. A variable becomes a dependency only when it's actually read during evaluation, not merely when it appears in the guard expression:

1. *Runtime tracking:* Dependencies are determined by which variables are actually accessed during each evaluation
2. *Transitive tracking:* Dependencies include variables read in called functions
3. *Dynamic changes:* The dependency set can change from one evaluation to the next

Consider this example:

<!--NoCompile-->
<!-- 08-->
```verse
var X:int = 1
var Y:int = 2
var Z:int = 3

SomeFun(Value:int):int =
   if(Value > 0) then X else Y

var live W:int = SomeFun(Z)   # W is 1, Dependencies: {Z, X}
set Z = 0                     # W is 2, Dependencies: {Z, Y}
```

Initially, `SomeFun(Z)` reads `Z` (which is 3) and evaluates the `then` branch, reading `X`, yielding `W=1` with dependencies `{Z, X}`.

After `set Z=0`, the change to `Z` triggers re-evaluation. Now
`SomeFun(Z)` reads `Z` (which is 0) and evaluates the `else` branch,
reading `Y`. This results in `W=2` with new dependencies `{Z, Y}`.

Notice how `Y` became a dependency only when the execution path
changed. If `X` is subsequently modified, `W` will *not* update
because `X` is no longer in the dependency set. This dynamic tracking
ensures that live variables only react to changes that actually affect
their current value.

### Turning Off Liveness

A live variable established through its guard (not its type) can be
turned off by a subsequent regular assignment.

<!--versetest-->
<!-- 09-->
```verse
var X:int = 0
var Y:int = 5
set live X = Y  # X is now live, tracking Y

set Y = 10      # X becomes 10
set X = 20      # X is now a regular variable again
set Y = 15      # X remains 20 (no longer tracking Y)
```
<!--
X=20
-->

This allows temporary reactive behavior that can be disabled when no
longer needed. However, variables that are live through their type
expression remain live permanently—their reactive behavior is
intrinsic to their type.

## Reactive Constructs

Live variables form the foundation for three reactive constructs that
handle asynchronous events without explicit callbacks: `await`,
`upon`, and `when`.

### The await Expression

The `await` expression suspends execution until a target expression
succeeds, providing a synchronization primitive for asynchronous
programming.

<!--versetest
-->
<!-- 10-->
```verse
F()<suspends>:void =
    var X:int = 0

    OldX := X # copy the old value

    # Suspend until X changes from OldX (0)
    await{X <> OldX}
    Print("X changed to: {X}")
```

The target expression is evaluated immediately. If it fails, the
task suspends. Verse tracks which variables were read during
evaluation. Whenever those variables change, the guard is re-evaluated.
If it succeeds, execution resumes immediately.

The practical implications are that you can write code that naturally
expresses "wait for this condition" without manually managing event
handlers or callback registration. The code suspends at the await
point and resumes exactly when the condition becomes true.

<!--versetest
int_ref := class:
    var Contents:int = 0

TestAwait()<transacts><suspends>:void =
    X:int_ref=int_ref{}
    Y:int_ref=int_ref{}
    # Wait for a specific condition
    await{X.Contents > 10}
    set Y.Contents = X.Contents * 2
<#
-->
<!-- 11 -->
```verse
# Wait for a specific condition
await{X.Contents > 10}
set Y.Contents = X.Contents * 2
```
<!-- #>-->

The guard expression must have effects `<reads><computes><decides>`
(see [Effects](13_effects.md))—it can read and compute but cannot
write or allocate. This ensures re-evaluation is side-effect free.

### The upon Expression

The `upon` expression provides one-shot reactive behavior: when a
condition becomes true, execute some code once. Unlike `await`, which
resumes the current task, `upon` creates a new concurrent task that
runs when triggered.

<!--versetest-->
<!-- 12-->
```verse
var Health:int = 100
var IsDead:logic = false

upon(Health <= 0):
    set IsDead = true
    Print("Player died!")

set Health = 50  # Nothing happens
set Health = 0   # Triggers: prints "Player died!"
set Health = -10 # Nothing happens (already triggered once)
```

The `upon` expression evaluates its guard immediately and records the variables read. It then yields a `task(t)` where `t` is the result type of the body, representing the pending reactive behavior. When dependencies change, the guard is re-evaluated. If it succeeds, the body executes once in a new concurrent task, and the upon completes.

This one-shot behavior makes `upon` perfect for state transitions and event notifications. When a threshold is crossed, when a resource becomes available, when a timer expires—these scenarios naturally map to `upon`'s "fire once when condition becomes true" semantics.

The body must have the `<transacts>` effect (see [Effects](13_effects.md)), allowing it to read and write variables (including other live variables), with execution guaranteed to be atomic with respect to notifications.

### The when Expression

The `when` expression provides continuous reactive behavior: every time a condition is true, execute some code. This creates a persistent observer that runs whenever its guard succeeds.

<!--verstest-->
<!-- 13 FAILURE
  Line 6: Verse compiler error V3560: Expected definition but found macro invocation.
  Line 10: Verse compiler error V3560: Expected definition but found assignment.
  Line 11: Verse compiler error V3560: Expected definition but found assignment.
  Line 12: Verse compiler error V3560: Expected definition but found assignment.
  Line 3: Verse compiler error V3502: Module-scoped `var` must have `weak_map` type.
  Line 4: Verse compiler error V3502: Module-scoped `var` must have `weak_map` type.
-->
```verse
var Score:int = 0
var DisplayedScore:int = 0

when(Score):
    set DisplayedScore = Score
    Print("Score updated to: {Score}")

set Score = 100  # Triggers: prints "Score updated to: 100"
set Score = 100  # No trigger (value unchanged)
set Score = 200  # Triggers: prints "Score updated to: 200"
```

The `when` expression evaluates its guard immediately. If the guard succeeds, the body executes. Then it records the variables read by the guard and yields a `task(void)`. Whenever dependencies change and the guard succeeds, the body executes again, creating a continuous observation loop.

This makes `when` ideal for maintaining derived state and responding to ongoing changes. Synchronizing UI with game state, updating AI behavior based on player actions, or maintaining consistency between related variables all benefit from `when`'s persistent reactivity.

<!--versetest-->
<!-- 14-->
```verse
var X:int = 2
var Y:int = 2

when(Y):
    Z := if (Y < 0) then 0 else Y - 1
    if (Z <> X):
        set X = Z

when(X):
    Z := if (X < 0) then 0 else X - 1
    if (Z <> Y):
        set Y = Z

# These when expressions will stabilize at X = -1, Y = 0
```

The body executes with the `<transacts>` effect, and the when immediately re-registers after each execution, creating the continuous observation pattern.

### Cancellation

All three reactive constructs—`await`, `upon`, and `when`—return a `task` that can be canceled, allowing dynamic control over reactive behavior.

<!--versetest-->
<!-- 15 FAILURE
  Line 10: Script Error 3512: This invocation calls a function that has the 'suspends' effect, which is not allowed by its context.
-->
```verse
var X:int = 0
var Y:int = 0

Task := upon(X > 5):
    set Y = X

Task.Cancel()  # Cancels the reactive behavior
set X = 10     # Y remains 0
```

Canceling a task immediately removes all dependency tracking and prevents the associated code from running. This provides fine-grained control over the lifecycle of reactive behaviors, allowing you to enable and disable observations based on game state or user actions.

## The batch Expression

The `batch` expression groups multiple variable updates together, delaying notifications until the entire group completes. This prevents intermediate states from triggering reactive behaviors and ensures observers see consistent snapshots of related changes.

<!--versetest-->
<!-- 16-->
```verse
var X:int = 0
var Y:int = 0

when(X > 1 and Y < 10):
    Print("Fired!") # Never prints

when(X):
    Print("X Changed to {X}!") # Prints once

batch:
    set X = 2   
    set Y = 10
    set X += 5
    Print("Inside batch")

Print("After batch")

# Output order:
# -"Inside batch"
# -"X Changed to 7!"
# -"After batch"
```

Inside a `batch` block, variable updates occur immediately but notifications to awaiting tasks and reactive constructs are deferred. When the batch completes, all pending notifications fire in the order their triggers occurred, but observers see the final consistent state rather than intermediate values.

If the same notification occurs twice, only the first of them will be delivered.

Batch expressions nest: notifications are delayed until all enclosing batches complete. This composability ensures that no matter how deeply nested your code, you can guarantee atomic updates of related variables.

The body of a batch must not have the `<suspends>` effect—all operations must complete immediately. This ensures batch blocks have well-defined boundaries and can't leave the system in an inconsistent state by suspending mid-update.

## Issues and Patterns

### API Design

Any variable appearing in the public interface of a class or module
can be made live by external code, potentially violating class
invariants. To avoid this, one could limit the exposure of mutable
variables or at least use access modifiers to control this:

<!--versetest-->
<!-- 17 FAILURE
  Line 4: Script Error 3509: This variable expects to be initialized with a value of type int, but this initializer is an incompatible value of type type{_(:float)<reads>:float}.
  Line 4: Script Error 3509: `live` requires a `comparable` right-hand side.  This right-hand side is of type type{_(:float)<reads>:float}.
  Line 4: Script Error 3641: Attributes on var only allowed inside a module or a class
  Line 4: Script Error 3594: Access level private is only allowed inside classes and interfaces.
-->
```verse
var<private> live X<public>:int = Exp
```

Here `X` is publicly visible for reading but can only be updated by
the class itself. This prevents external code from attaching arbitrary guards that might break the class's
invariants.

### Failures and Liveness

Live variable updates and reactive construct triggers are integrated
in the failure semantics of Verse.  When there is a failure, live
variable updates are rolled back and their notifications are
suppressed.

<!--versetest-->
<!-- 18-->
```verse
var X:int = 0
var Y:int = 0

if:
    set live X = Y + 5  # Establishes live relationship
    false?          # Transaction fails

upon(X):
    Print("{X}") # Does not print when Y changes

# Live relationship was not established
set Y = 10  # X remains 0
```

This ensures that reactive behaviors only observe committed changes,
maintaining consistency even in the presence of speculative execution
and failure.

### Derived Synchronization

A common pattern is for multiple UI elements to reflect the same 
game state, `when` provides automatic synchronization:

<!--versetest-->
<!-- 19-->
```verse
var PlayerScore:int = 0
var DisplayedScore:int = 0
var ScoreText:string = ""

when(PlayerScore):
    set DisplayedScore = PlayerScore
    set ScoreText = "Score: {PlayerScore}"
```

Every change to `PlayerScore` automatically updates both the numeric
display value and the formatted text, keeping the UI consistent
without manual coordination.

### Conditional Reactivity

Live variables can track different sources based on conditions:

<!--versetest-->
<!-- 20 FAILURE
  Line 10: Script Error 3513: Expected an expression that can fail in the 'if' condition clause
-->
```verse
var UseAlternate:logic = false
var PrimaryValue:int = 10
var AlternateValue:int = 20
var CurrentValue:int = 0

set live CurrentValue =
    if (UseAlternate) then AlternateValue else PrimaryValue

# CurrentValue = 10
set UseAlternate = true
# CurrentValue = 20
set AlternateValue = 30
# CurrentValue = 30
set PrimaryValue = 15
# CurrentValue = 30 (still tracking AlternateValue)
```

The dependency tracking is dynamic: when the condition changes, the
set of tracked variables changes accordingly, allowing flexible
reactive routing.

### Resource Loading

Use `upon` for one-time initialization when resources become available:

<!--versetest-->
<!-- 21 FAILURE
resource_manager := class:
    var TextureLoaded:logic = false
    var ModelLoaded:logic = false

    Initialize()<suspends>:void = {}
-->
<!-- 21 FAILURE
  Line 8: Verse compiler error V3502: Type definitions are not yet implemented outside of a module scope.
-->
```verse
resource_manager := class:
    var TextureLoaded:logic = false
    var ModelLoaded:logic = false

    Initialize()<suspends>:void =
        upon(TextureLoaded and ModelLoaded):
            Print("All resources loaded, starting game")
            StartGame()
```

This pattern eliminates manual tracking of loading state. When both
resources finish loading, the game starts automatically.

### Modifier Stack (Under Consideration)

**The design of modifier_stack has not been finalized; material presented here is likely to change.**

Game development often requires applying multiple modifiers to a single value. For instance, a player's health might need to be
clamped to a valid range, temporarily boosted by a health potion and automatically recomputed when dependencies change.

The `modifier_stack` pattern provides a composable solution using live variables and function-as-type, allowing ordered transformations that automatically update when any modifier's dependencies change.

The modifier stack consists of three components:

1. **`modifier_ifc(t)`** - An interface for modifiers that transform values of type `t`
2. **`modifier_stack(t)`** - A container that orders and composes modifiers
3. **Live variable** - Uses `modifier_stack.Evaluate` as its type for automatic reactivity

When you assign to a live variable with a modifier stack type, the value flows through each modifier in position order, and the final result is stored. Because `modifier_stack.Evaluate` has the `<reads>` effect, changes to any modifier's dependencies (or adding/removing modifiers) trigger automatic recalculation.

The public API is as follows:

<!--NoCompile-->
<!-- 22-->
```verse
modifier_ifc(t : type) := interface:
   Evaluate(Value:t)<reads> : t

modifier_stack(t:type) := class:
   # Insert a Modifier at Position; return a cancelable used to remove the Modifier.
   AddModifier<final>(Modifier:modifier_ifc(t), Position:rational)<transacts>: cancelable

   # Returns the input Value evaluated against each modifier in the stack in position order.
   Evaluate<final>(Value:t)<reads> : t
```

The `AddModifier` method returns a `cancelable` which can be used to remove the inserted modifier. Removing a modifier triggers recalculation of any live variable associated with this stack.

For example, consider the following which creates a live variable `Health` filtered through a modifier stack containing a magic potion modifier that doubles the input value:

<!--NoCompile-->
<!-- 23-->
```verse
HealthStack := modifier_stack(float){}
HealthStack.AddModifier(magic_potion{Value:=2.0})
var RawHealth -> Health : HealthStack.Evaluate = 10.0
# RawHealth = 10.0, Health = 20.0
```

The variable automatically recomputes when the multiplier changes or when modifiers are added to the stack.

In more detail, this example demonstrates two modifiers working together: a `magic_potion` that multiplies health, and a `clamp` that bounds values within a range.

<!--NoCompile-->
<!-- 24-->
```verse
# Define modifier implementations
magic_potion := class(modifier_ifc(float)):
   var Value:float
   Evaluate<override>(Arg:float)<reads>:float = Arg * Value

clamp := class(modifier_ifc(float)):
   var Low:float
   var High:float
   Evaluate<override>(Arg:float)<reads>:float =
       if (Arg<Low) then Low else { if (Arg>High) then High else Arg }

# Create instances
Potion := magic_potion{ Value:= 2.0 }
Clamp := clamp{Low:=1.0, High:= 12.0 }

# Build the modifier stack
HealthStack := modifier_stack(float){}
RevokePotion := HealthStack.AddModifier(Potion, 0.0)  # Apply first (position 0.0)
HealthStack.AddModifier(Clamp, 1.0)                   # Apply second (position 1.0)

# Create live variable with modifier stack
var Health : HealthStack.Evaluate = 5.0  # 5.0 * 2.0 = 10.0 (then clamped to [1.0, 12.0])
set Potion.Value = 3.0                   # 5.0 * 3.0 = 15.0 (clamped to 12.0)
RevokePotion.Cancel()                    # 5.0 (no potion, just clamp to [1.0, 12.0])
```

The value flows through modifiers in position order:

1. **Initial:** 5.0 → Potion (×2.0) → 10.0 → Clamp → 10.0
2. **After changing `Potion.Value`:** 5.0 → Potion (×3.0) → 15.0 → Clamp → 12.0
3. **After removing potion:** 5.0 → Clamp → 5.0

There are plans to enforce via the compiler that: each modifier instance can only be added to one stack, and 
each stack instance can be associated with one variable.  This will enable future features
where modifier stacks maintain state specific to their associated live variable.

### Common Errors

**Unnecessary Live Declarations**

Defining a live variable with no dependencies that can change is unnecessary and misleading:

<!--NoCompile-->
<!-- 25-->
```verse
var live X:int = 10    # X is 10 and will never change
set live X = 20        # X is 20 and will never change
```

In both cases, `X` does not update automatically, so the program
behaves identically without the `live` keyword. The `live` annotation
falsely suggests reactive behavior where none exists.

**Missing Mutable Dependencies**

Similarly, a live variable that only depends on immutable values will never update:

<!--NoCompile-->
<!-- 26-->
```verse
X:int = 10
var live Y = X+1    # Y is 11 and will never change
```

Since `X` is immutable, `Y` has no mutable dependencies and will
remain at 11 forever. The `live` declaration is pointless.

**Function-as-Type Confusion**

A subtle error occurs when trying to make a variable live through a
function type:

<!--NoCompile-->
<!-- 27-->
```verse
var Mult:int = 10

Multiply(Value:int):type{_(:int):int} =
    Fun(Arg:int):int = Value * Arg
    Fun

var X:Multiply(Mult) = 10    # X = 100

set Mult = 20                 # X is still 100 (not live!)
```

This code is mistaken. The programmer likely thought that
`Multiply(Mult)` would make `X` live because the expression has a
`<reads>` effect (it reads `Mult`) and returns a function type
`int->int`.

**The error:** For a variable to be live through its type, the
*returned function itself* must have the `<reads>` effect, not the
expression that produces the function.

To see why, consider this equivalent transformation:

<!--NoCompile-->
<!-- 28-->
```verse
MFun = Multiply(Mult)
var X:MFun = 10
```

Now it's clear that `X` is not live—`MFun` is just a function value
with type `int->int`, and that function does not have a `<reads>`
effect.

**The correct approach:** Use the pattern where the function used as a
type directly has the `<reads>` effect:

<!--NoCompile-->
<!-- 29-->
```verse
var Mult:int = 10

Multiply(Arg:int)<reads>:int = Arg * Mult

var X:Multiply = 10    # X = 100
set Mult = 20          # X = 200 (now live!)
```

Here `Multiply` itself has `<reads>`, so using it as a type makes `X` live.

If the same function has to be reused with different variables as
dependent, one can package it in an object as shown earlier.

## Evolution 

When publishing a new version of a system, it is allowed to remove
`live` from a variable definition. This forward compatibility
guarantee means that reactive behavior is an implementation detail
that can be optimized away without breaking client code.

Converting a regular variable to a live variable in a new version is
generally safe if the computed value matches what the previous version
maintained manually. However, if external code depends on being able
to set arbitrary values, this could break expectations.

The ability to cancel reactive constructs provides an important
upgrade path: code that creates `when` or `upon` observers can later
be modified to cancel them under different conditions without breaking
existing behavior.
