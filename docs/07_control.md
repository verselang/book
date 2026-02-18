# Control Flow

Every program has a natural rhythm to its execution, a sequence in
which instructions are processed and decisions are made. In Verse,
this flow is more than just a mechanical progression through lines of
code - it's a carefully orchestrated dance between different types of
expressions, each contributing to the overall behavior of your
program.

## Blocks

A code block is a fundamental organizational unit, it groups related
expressions together and creates a new scope for variables and
constants. Unlike many languages where blocks are merely syntactic
conveniences, blocks are expressions themselves, meaning they produce
values just like any other expression.

The concept of scope is crucial to understanding code blocks. When you
create a variable or constant within a block, it exists only within
that block's context. This containment ensures that your code remains
organized and that names don't accidentally conflict across different
parts of your program. Consider this function, it's body is a code
block that contains one if-then-else expression, itself
composed of three different code blocks.

<!--versetest-->
<!-- 01 -->
```verse
CalculateReward(PlayerLevel:int)<reads>:int =
    if:
        PlayerLevel > 10
        Multiplier := 2.0  # Only exists within this if block
        Base := 100
        Result := Floor[(Base+PlayerLevel) * Multiplier] # Fails on infinity
    then:
        Result  # This block extends the scope of the if
    else:
        50      # Different branch, different scope
                # Multiplier and Result don't exist here
```
<!-- CalculateReward(11) = 222 -->

Verse has a flexible syntax with three equivalent formats for
writing blocks. The spaced format is the most common, using a colon to
introduce the block and indentation to show structure:

<!--versetest
IsPlayerReady()<decides><transacts>:void = {}
StartMatch()<transacts>:void = {}
BeginCountdown()<transacts>:void = {}

M()<transacts>:void =
    if (IsPlayerReady[]):
        StartMatch()
        BeginCountdown()
<#
-->
<!-- 02 -->
```verse
if (IsPlayerReady[]):
    StartMatch()
    BeginCountdown()
```
<!-- #> -->

The multi-line braced format offers familiarity for programmers coming
from C-style languages:

<!--versetest
IsPlayerReady()<decides><transacts>:void = {}
StartMatch()<transacts>:void = {}
BeginCountdown()<transacts>:void = {}

M()<transacts>:void =
    if (IsPlayerReady[]) {
        StartMatch()
        BeginCountdown()
    }
<#
-->
<!-- 03 -->
```verse
if (IsPlayerReady[]) {
    StartMatch()
    BeginCountdown()
}
```
<!-- #> -->

For simple operations, the single-line dot format keeps code concise:

<!--versetest-->
<!-- 04 -->
```verse
HasPowerup()<computes><decides>:void={}
ApplyBoost():void={}
IncrementCounter():void={}
F():void=
    if (HasPowerup[]). ApplyBoost(); IncrementCounter()
```

Since everything is an expression, blocks themselves have values. The
value of a block is given by the last expression executed within
it. This enables elegant patterns where complex computations can be
encapsulated in blocks that seamlessly integrate with surrounding
code:

<!--versetest
CalculateScore()<computes>:int = 100
CalculateBonus(Time:float)<computes>:int = 50
CompletionTime:float = 10.0
AccuracyValue:float = 0.95

M()<transacts><decides>:void =
    FinalScore := block:
        Base := CalculateScore()
        Bonus := CalculateBonus(CompletionTime)
        Accuracy := Floor[AccuracyValue * 100.0]
        Base + Bonus + Accuracy
<#
-->
<!-- 05 -->
```verse
FinalScore := block:              # The variable has the block's value
    Base := CalculateScore()
    Bonus := CalculateBonus(CompletionTime)
    Accuracy := Floor[AccuracyValue * 100.0]
    Base + Bonus + Accuracy       # This becomes the block's value
```
<!-- #> -->


## If Expressions

The `if` expression uses success and failure to drive decisions (see
[Failure](08_failure.md) for details). When an expression in the
condition succeeds, the corresponding branch executes:

<!--versetest
player := class:
   CanJump()<computes><decides>:void={}
   Jump()<computes>:void={}
   GetEquippedWeapon()<computes><decides>:weapon=weapon{}
   Idle()<computes>:void={}

weapon:=class<computes>{
   Fire():void={}
}
ConsumeAmmo():void={}
PlayJumpSound():void={}
<#
-->
<!-- 07 -->
```verse
HandlePlayerAction(Player:player, Action:string):void =
    if (Action = "jump", Player.CanJump[]):
        Player.Jump()
        PlayJumpSound()
    else if (Action = "attack", Weapon := Player.GetEquippedWeapon[]):
        Weapon.Fire()
        ConsumeAmmo()
    else:
        # Default action
        Player.Idle()
```
<!-- #> -->

This approach allows you to chain conditions that might fail without
explicit error handling at each step.

An alternative syntax uses `then:` and `else:` keywords to explicitly
label branches:

<!--versetest-->
<!-- 08 -->
```verse
ProcessValue(Value:int):string =
    if:
        Value > 0
        Value < 100
    then:
        "Valid"
    else:
        "Out of range"

ProcessValue(50) = "Valid"
```

This syntax can improve readability when you have multiple conditions
or want to emphasize the condition-action separation. 

The condition in an `if` must contain at least one expression that can
fail. This requirement ensures `if` is used for its intended
purpose—handling uncertain outcomes:

<!--NoCompile-->
<!-- 10 -->
```verse
# Error: condition cannot fail
if (1 + 1):  # Compile error - no fallible expression
    DoSomething()

# Valid: array access can fail
if (FirstItem := Items[0]):
    Process(FirstItem)
```

Empty conditions are also not allowed—every `if` must test something.

If any expression in the condition fails, control flow proceeds to the
`else` branch if present. Any effects performed while evaluating the
condition are automatically rolled back (see
[Failure](08_failure.md#speculative-execution) for details):

<!--versetest
GetPlayerScore()<decides><computes>:int=1
-->
<!-- 11 -->
```verse
var Counter:int = 0

if:
    set Counter = Counter + 1  # Provisional change
    Score := GetPlayerScore[]  # Might fail
    Score > 100
then:
    # Counter was incremented
else:
    # Counter rolled back to original value - increment undone!
```

This speculative execution makes conditional logic safer—you can
perform operations optimistically, knowing they'll be reversed if
subsequent conditions fail.

Variables defined in the condition are available in the `then` branch
but not in the `else` branch:

<!--NoCompile-->
<!-- 12 -->
```verse
if:
    Player := FindPlayer[Name]  # Define Player
then:
    AwardBonus(Player)  # OK - Player available
else:
    Penalize(Player)  # Compile error
```

This scoping reflects the logical flow: in the `else` branch, the
condition failed, so any variables bound during the condition might
not have meaningful values.

Since `if` is an expression, it produces a value. When all branches
return compatible types, the `if` can be used anywhere a value is
expected:

<!--versetest
IsCritical:logic= false
BaseDamage:int=0
Health:int=0
-->
<!-- 13 -->
```verse
Damage := if (IsCritical?):
    BaseDamage * 2
else:
    BaseDamage

# Ternary-style
Status := if (Health > 50). "Healthy" else. "Wounded"
```

When branches have incompatible types, the result is widened to `any`:

<!--versetest
UseNumber:logic=false
-->
<!-- 14 -->
```verse
# Different types in branches yields any
Result:any = if (UseNumber?) then 42 else "text"
```

All branches must produce a value for the `if` to be used as an
expression.

## Case Expressions

When you need to make decisions based on multiple possible values, the
`case` expression provides clear, readable branching:

<!--versetest-->
<!-- 15 -->
```verse
GetWeaponDamage(WeaponType:string):float =
    case(WeaponType):
        "sword"  => 50.0
        "bow"    => 35.0
        "staff"  => 40.0
        "dagger" => 25.0
        _        => 10.0  # Default damage for unknown weapons

GetWeaponDamage("sword") = 50.0
```

The `case` expression is used when you have discrete values to match
against, making your intent clearer than a series of `if-else`
conditions.

Case expressions work with specific types that support direct value
comparison:

- **Primitives**: `int`, `logic`, `char`
- **Strings**: `string`
- **Enums**: Both open and closed enums
- **Refinement types**: Custom types with constraints

They do not work on `float`, objects and tuples because these types
either don't have well-defined equality (`float` with `NaN`), lack value
semantics (classes are references), or have structural complexity
(tuples).

**Exhaustiveness Checking with Enums.** `case` with `enum` are checked
for exhaustiveness.  For closed enums where all values are known, the
compiler verifies you've handled all cases:

<!--versetest
direction := enum:
    North
    South
    East
    West

GetVector(Dir:direction):tuple(int, int) =
    case (Dir):
        direction.North => (0, 1)
        direction.South => (0, -1)
        direction.East => (1, 0)
        direction.West => (-1, 0)
<#
-->
<!-- 17 -->
```verse
# Exhaustive - no wildcard needed
GetVector(Dir:direction):tuple(int, int) =
    case (Dir):
        direction.North => (0, 1)
        direction.South => (0, -1)
        direction.East => (1, 0)
        direction.West => (-1, 0)

GetVector(direction.North) = (0, 1)
```
<!-- #> -->

If you add a wildcard when all cases are covered, you'll get a warning
that the wildcard is unreachable:

<!--versetest
direction := enum:
    North
    South
    East
    West

GetVectorWithUnreachable(Dir:direction):tuple(int, int) =
    case (Dir):
        direction.North => (0, 1)
        direction.South => (0, -1)
        direction.East => (1, 0)
        direction.West => (-1, 0)
        _ => (0, 0)
<#
-->
<!-- 18 -->
```verse
    case (Dir):
        direction.North => (0, 1)
        direction.South => (0, -1)
        direction.East => (1, 0)
        direction.West => (-1, 0)
        _ => (0, 0)  # Warning: all cases already covered
```
<!-- #> -->

Incomplete case coverage is allowed in a `<decides>` context:

<!--versetest
direction := enum{  North, South, East, West}

GetPrimaryDirection2(Dir:direction)<decides>:string =
    case (Dir):
        direction.North => "Primary"
        # Other directions cause function to fail
<#
-->
<!-- 19 -->
```verse
# Without wildcard in <decides> context - OK
GetPrimaryDirection2(Dir:direction)<decides>:string =
    case (Dir):
        direction.North => "Primary"
        # Other directions cause function to fail
```
<!-- #> -->

Open enums can have values added after publication, so they can never
be exhaustive. They always require either a wildcard or a `<decides>`
context.

## Loop Expressions

The `loop` expression creates an infinite loop that continues until
explicitly broken:

<!--versetest
UpdatePlayerPositions():void={}
CheckCollisions():void={}
RenderFrame():void={}
GameOver()<decides>:void={}
<#
-->
<!-- 22 -->
```verse
GameLoop():void =
    loop:
        UpdatePlayerPositions()
        CheckCollisions()
        RenderFrame()
        if (GameOver[]). break
```
<!-- #> -->

The `break` expression exits the loop entirely, terminating iteration.
`break` has "bottom" type—a type that represents a computation that
never returns normally. Since the bottom type is a subtype of all
other types, `break` can be used in any type context:

<!--versetest
ShouldExit()<computes><decides>:void={}
ComputeValue()<computes>:int=1
-->
<!-- 55 -->
```verse
var X:int = 0
loop:
    if (ShouldExit[]):
        break
    else:
        set X = ComputeValue()
    # break is compatible in the control flow
```

This allows `break` to be used flexibly in expressions where a value
is expected, since the compiler knows that path never produces a
value.

**Loop Return Value:** The loop expression itself produces a value of type
`true` (the top type), regardless of what expressions appear in its body.
This return value is rarely useful in practice—loops are typically used for
their side effects.

When `break` appears in nested loops, it exits only the innermost
enclosing loop:

<!-- Stuck in the interpreter -->
<!--NoCompile-->
<!-- 57 -->
```verse
var Outer:int = 0
var Inner:int = 0
loop:
    set Outer += 1
    loop:
        set Inner += 1
        if (Inner = 5):
            break        # Exits inner loop
    if (Outer = 10):
        break            # Exits outer loop
```

The following restrictions apply. The `break` statement must appear in
a code block, not as part of a complex expression.  A loop must
contain at least one non-break statement. Finally, using `break`
outside a `loop` produces an error:

<!--NoCompile-->
<!-- 58 -->
```verse
ProcessData():void =
   if (ShouldStop[]):
           break      # Error
```
## For Expressions

The `for` expression iterates over collections, ranges, and other
iterable types, providing a more structured approach to repetition:

<!--versetest
player:=class{}
GetScore(P:player):int=100
<#
-->
<!-- 23 -->
```verse
CalculateTotalScore(Players:[]player)<transacts>:int =
    var Total:int = 0
    for (Player : Players):
        PlayerScore := GetScore(Player)
        set Total += PlayerScore
    Total
```
<!-- #> -->

While it may look familiar from earlier imperative languages, `for` is
best thought of as a functional construct that combines iteration,
filtering with speculative execution, and construction of a collection
of results.

<!--versetest-->
<!-- 223 -->
```verse
Values:[]float= array{1.0, 10.1, 100.2}
Result := 
   for:
      V : Values
      V >= 10.0
      R := Floor[V]
   do:
      R*2.0

Result = array{20.0, 200.0}
```

The above is written with an alternative multi-clause syntax using the
`do:` keyword to  separate the iteration specification  from the body.
The `for` iterates  over the `Values` array,  discarding values smaller
than 10  and rounding down  numbers. It  returns an array  of floats.
The `Floor` function is defined as `decides` --if it were to fail that
iterate would be discarded.

There is another alternative syntax: the single-line dot syntax for
simple operations:

<!--versetest
Values:[]int = array{1, 2, 3}
DoSomething(V:int):void = {}

M():void =
    for (V : Values). DoSomething(V)
<#
-->
<!-- 26 -->
```verse
# Single-line dot style
for (V : Values). DoSomething(V)
```
<!-- #> -->

**Index and Value Pairs:**

When iterating arrays, you can access both the index and the value
using the pair syntax `Index -> Value`:

<!--versetest
player:=struct{ Name:string }
<#
-->
<!-- 28 -->
```verse
PrintRoster(Players:[]player):void =
    for (Index -> Player : Players):
        Print("Player {Index}: {Player.Name}")
```
<!-- #> -->

The index is zero-based, matching Verse's array indexing convention.

**Defining Variables in For Clauses:**

The for loop allows you to define intermediate variables that can be
used in subsequent filters or the loop body:

<!--versetest-->
<!-- 29 -->
```verse
# Define Y based on X
Doubled := for (X := 1..5, Y := X * 2):
    Y  # Returns array{2, 4, 6, 8, 10}

# Combine with filtering
SafeDivision := for (X := -3..3, X <> 0, Y := Floor[10.0 / (X*1.0)]):
    Y  # Skips X=0, returns array{-3, -5, -10, 10, 5, 3}
```

These intermediate variables are scoped to the iteration and can
reference earlier variables in the same clause.

**Multiple Filters:**

You can chain multiple filter conditions using comma-separated
expressions. Each filter must be failable, and if any fails, that
iteration is skipped:

<!--versetest-->
<!-- 30 -->
```verse
# Multiple independent filters
Filtered := for (X := 1..10, X <> 3, X <> 7):
    X  # Returns array{1, 2, 4, 5, 6, 8, 9, 10}

# Filters with intermediate variables
Complex := for (X := 1..5, X <> 2, Y := X * 2, Y < 10):
    Y  # Only includes values where X≠2 and Y<10
```

Each filter condition is evaluated in order, and iteration continues
only if all conditions succeed.

**Iterating Over Maps:**

Maps can be iterated over in two ways: values only, or key-value pairs
using the pair syntax:

<!--versetest-->
<!-- 31 -->
```verse
# Iterate over values only
Scores:[int]int = map{1 => 100, 2 => 200, 3 => 150}
TopScores := for (Score : Scores):
    Score  # Returns array{100, 200, 150}

# Iterate over key-value pairs
PlayerScores:[string]int = map{"Alice" => 100, "Bob" => 200}
for (PlayerName -> Score : PlayerScores):
    Print("{PlayerName} scored {Score}")
```

Maps preserve insertion order, so iteration order matches the order in
which keys were added to the map.

**String Iteration:**

Strings can be iterated character by character:

<!--NoCompile-->
<!-- 32 -->
```verse
CountVowels(Text:string):int =
    var Count:int = 0
    for (Char : Text):
        if (Char = 'a' or Char = 'e' or Char = 'i' or Char = 'o' or Char = 'u'):
            set Count += 1
    Count
```

**Nested Iteration (Cartesian Products):**

Multiple iteration sources create nested loops, producing the cartesian product:

<!--NoCompile-->
<!-- 33 -->
```verse
PrintGrid():void =
    for (X := 1..3, Y := 1..3):
        Print("({X}, {Y})")
    # Produces: (1,1), (1,2), (1,3), (2,1), (2,2), (2,3), (3,1), (3,2), (3,3)
```

**Filtering with Failure:**

Verse's `for` expressions are particularly powerful when they leverage
failure contexts, as they can naturally filter:

<!--versetest
player:=struct{ Name:string }
GetScore(P:player)<computes>:int=0
<#
-->
<!-- 34 -->
```verse
GetHighScorers(Players:[]player):[]player =
    for (Player : Players, Score := GetScore(Player), Score > 1000):
        Player  # Only players with score > 1000 are included
```
<!-- #> -->

When any expression in the iteration header fails, that iteration is
skipped. This allows elegant filtering without explicit `if`
statements:

<!--versetest
item:=struct{Price:float}
<#
-->
<!-- 35 -->
```verse
# Filter items under budget and apply transformation
AffordableItems(Items:[]item, Budget:float):[]float =
    for (Item : Items, Item.Price <= Budget):
        Item.Price * 1.1  # Apply 10% markup
```
<!-- #> -->

**For as an Expression:**

Like other control flow constructs, `for` is an expression. When the body produces values, `for` collects them into an array:

<!--versetest
player:=struct{Name:string}
<#
-->
<!-- 36 -->
```verse
# Collect player names
GetNames(Players:[]player):[]string =
    for (Player : Players):
        Player.Name  # Each iteration produces a string
```
<!-- #> -->

This makes `for` a powerful tool for transforming collections without
explicit accumulator variables.

**Breaking from For Loops:**

The `break` statement cannot exit `for` loops early.

<!-- TODO EXPLAIN AND GIVE ALTERNATIVES -->

**Note on Continue:**

Unlike many languages, Verse does not currently support a `continue`
statement to skip to the next iteration. Instead, use conditional
logic or failure-based filtering to achieve similar results:

<!--versetest
item:=struct{IsValid:logic}
ProcessItem(I:item):void={}
<#
-->
<!-- 38 -->
```verse
# Instead of continue, use conditional blocks
ProcessItems(Items:[]item):void =
    for (Item : Items):
        if (Item.IsValid?):
            ProcessItem(Item)
        # No continue needed - just structure with conditions

# Or use failure-based filtering in the header
ProcessValidItems(Items:[]item):void =
    for (Item : Items, Item.IsValid?):
        ProcessItem(Item)  # Only valid items reach here
```
<!-- #> -->


**Range Iteration.** The range operator `..` provides numeric
iteration over integer sequences. Ranges are inclusive on both ends:

<!--versetest-->
<!-- 27 -->
```verse
# Iterates: 1, 2, 3, 4, 5 (both bounds included)
for (I := 1..5):
    Print("Count: {I}")

# Single element range
for (I := 42..42):
    Print("Answer: {I}")  # Prints once: "Answer: 42"

# Empty range (start > end produces no iterations)
for (I := 5..1):
    Print("Never executes")  # Loop body never runs
```

The `..` operator is always inclusive. There is no exclusive range
syntax.

Range bounds are evaluated in a specific order, and side effects occur
predictably:

1. **Left bound evaluated first**, then right bound
2. **Both bounds always evaluated**, even if the range is empty
3. **Side effects happen in order**, regardless of whether iterations occur

While you cannot store ranges as values, you can create arrays using
for expressions:

<!--versetest-->
<!-- 47 -->
```verse
# This works because for produces an array, not because ranges are storable
DoubledNumbers:[]int = for (I := 1..5){ I * 2 }

# Can then iterate over the array normally
for (N : DoubledNumbers):
    Print("{N}")
```

The range exists only during the for expression evaluation; the
resulting array is what gets stored.

**Restrictions.** The for loop has several important restrictions:

1. **Iteration source must be iterable:** Only ranges (`1..10`),
   arrays, maps, and strings can be iterated. 

2. **Filters must be failable:** Filter conditions must contain at
   least one expression that can fail. 

3. **Cannot redefine iteration variables:** You cannot redefine the
   iteration variable in the same clause.

4. **Cannot define mutable variables:** Using `var` to declare
   variables in the for clause is not allowed.

The range operator `..` has strict limitations that distinguish it
from other iterable types. Ranges are *not first-class values*—they
exist solely as syntactic sugar within for loop iteration clauses.
Ranges cannot be used in some contexts where you might expect them to
work:

<!--NoCompile-->
<!-- 40 -->
```verse
# ERROR: Cannot store range in variable
MyRange := 1..10
for (I := MyRange):

# ERROR: Cannot pass range to function
ProcessRange(1..10)

# ERROR: Cannot use range as standalone expression
Result := 1..10

# ERROR: Cannot put range in array
Ranges := array{1..10}

# ERROR: Cannot index range
Value := (1..10)(5)

# ERROR: Cannot access members on range
Length := (1..10).Length
```

Ranges work exclusively with the `int` type. Other numeric types,
booleans, types, or objects are not supported.

## Return Statements

The `return` statement provides explicit early exits from functions,
allowing you to terminate execution and return a value before reaching
the end of the function body:

<!--versetest
ValidateInput(Value:int):string =
    if (Value < 0):
        return "Error: Negative value"

    if (Value > 1000):
        return "Error: Value too large"

    "Valid"
<#
-->
<!-- 48 -->
```verse
ValidateInput(Value:int):string =
    if (Value < 0):
        return "Error: Negative value"

    if (Value > 1000):
        return "Error: Value too large"

    "Valid"     # Implicit return
```
<!-- #> -->

Return statements can only appear in specific positions within your
code—they must be in "tail position," meaning they must be the last
operation performed before control exits a scope. This restriction
ensures predictable control flow:

<!--versetest
GetOrder(:int)<transacts><decides>:order=order{}
order := class<allocates>{ IsValid()<decides>:logic=false }
<#
-->
<!-- 49 -->
```verse
# Valid: return is last operation
ProcessOrder(OrderId:int)<transacts>:string =
    if (Order := GetOrder[OrderId]):
        if (Order.IsValid[]):
            return "Processed"
    "Invalid order"

# Valid: return in both branches
GetStatus(Value:int):string =
    if (Value > 0):
        return "Positive"
    else:
        return "Non-positive"
```
<!-- #> -->

Verse functions implicitly return the value of their last expression,
so `return` is only needed for early exits:

<!--versetest
CalculateBonus(Score:int):int={
    if(Score<100)then{return 0}
    Score*10
}
<#
-->
<!-- 51 -->
```verse
# Implicit return
GetValue():int = 42  # Returns 42

# Explicit early return
GetDiscount(Price:float):float =
    if (Price < 10.0):
        return 0.0  # Early exit with no discount

    Price * 0.1  # Implicit return with 10% discount
```
<!-- #> -->

In functions with the `<decides>` effect, `return` allows you to
provide successful values from early exits, while still allowing other
paths to fail:

<!--versetest
config:=struct{MaxRetries:int}
GetConfig()<transacts><decides>:config=config{MaxRetries:=3}
AttemptOperation(Retry:int)<computes><decides>:string="success"
<#
-->
<!-- 52 -->
```verse
RetryableOperation()<transacts>:string =
    if (Config := GetConfig[]):
        for (Retry := 1..Config.MaxRetries):
            if (Result := AttemptOperation[Retry]):
                return Result  # Success - exit immediately
    "Failed" # All retries exhausted
```
<!-- #> -->

This pattern is common for search operations where you want to return
immediately upon finding a match, but fail if no match is found.

## Defer Statements

The `defer` statement schedules code to run just before successfully
exiting the current scope. This makes it invaluable for cleanup
operations like closing files, releasing resources, or logging:

<!--versetest
OpenFile(P:string)<computes>:?int=false
CloseFile(P:int)<computes>:void={}
ReadFile(P:int)<computes>:?string=false
ProcessContents(P:string)<computes><decides>:void={}
SaveResults()<computes><decides>:void={}
<#
-->
<!-- 61 -->
```verse
ProcessFile(FileName:string)<transacts><decides>:void =
    File := OpenFile(FileName)?
    defer:
        CloseFile(File)  # Runs on success or early exit

    Contents := ReadFile(File)?
    ProcessContents[Contents]
    SaveResults[]
```
<!-- #> -->

Deferred code executes when the scope exits successfully or through
explicit control flow like `return`:

<!--versetest
OpenConnection():int=0
CloseConnection(Id:int):void={}
Query(Id:int)<decides>:string="result"
ProcessResult(R:string):void={}
<#
-->
<!-- 62 -->
```verse
ProcessQuery()<transacts>:void =
    ConnId := OpenConnection()
    defer:
        CloseConnection(ConnId)  # Cleanup always needed

    for (Attempt := 1..5):
        if (Result := Query[ConnId]):
            ProcessResult(Result)
            return  # defer executes after return being called

    # defer executes before leaving the function scope on success
```
<!-- #> -->

This is a subtle but crucial point: if a function fails due to
speculative execution, deferred code does **not** execute. This is
because failure triggers a rollback that undoes all effects, including
the scheduling of defer blocks:

<!--versetest
AcquireResource()<transacts><decides>:int=0
ReleaseResource(Id:int)<transacts>:void={}
RiskyOperation(Id:int)<transacts><decides>:void={}
<#
-->
<!-- 63 -->
```verse
ExampleWithFailure()<transacts><decides>:void =
    ResourceId := AcquireResource[]
    defer:
        ReleaseResource(ResourceId) # Scheduled...

    RiskyOperation[ResourceId] # This fails!
    # defer does NOT run - entire scope was speculative and rolled back
```
<!-- #> -->

When the `RiskyOperation` fails, the entire function also fails, and
speculative execution undoes everything—including the defer
registration. The resource cleanup never happens because the resource
acquisition itself is rolled back.

This behavior ensures consistency: if a function fails, it's as if it
never ran, including any cleanup code that was scheduled.

**Execution Order:**

When multiple `defer`s exist in the same scope, they execute in
reverse order of definition (last-in, first-out), mimicking the
stack-based cleanup of nested resources:

<!--versetest
OpenDatabase()<transacts>:int=0
CloseDatabase(Id:int)<transacts>:void={}
BeginTransaction(Id:int)<decides><transacts>:int=0
CommitTransaction(Id:int)<transacts>:void={}
DoWork()<transacts><decides>:void={}
<#
-->
<!-- 64 -->
```verse
DatabaseTransaction()<transacts><decides>:void =
    DbId := OpenDatabase()
    defer:
        CloseDatabase(DbId)  # Executes second (outer resource)

    TxnId := BeginTransaction[DbId]
    defer:
        CommitTransaction(TxnId)  # Executes first (inner resource)

    DoWork[]  # Work happens with both resources active
    # Defers execute: CommitTransaction, then CloseDatabase
```
<!-- #> -->

**Defers and Async Cancellation:**

Deferred code also executes when async operations are cancelled, such
as when a `race` completes or a `spawn` is interrupted:

<!--NoCompile-->
<!-- 65 -->
```verse
ProcessWithTimeout()<suspends><transacts>:void =
    race:
        block:
            Resource := AcquireResource()
            defer:
                ReleaseResource(Resource)  # Runs if cancelled

            LongRunningTask(Resource)

        block:
            Sleep(10.0)  # Timeout
    # If timeout wins, first block is cancelled and defer runs
```

This ensures cleanup happens even when concurrency control interrupts your code.

**Nested Defers:**

Defer statements can be nested within other defer blocks, creating a
cascade of cleanup operations:

<!--versetest
Log(S:string)<transacts>:void={}
<#
-->
<!-- 66 -->
```verse
ProcessWithCleanup():void =
    Log("A")
    defer:
        Log("B")
        defer:
            Log("inner")  # Runs after B
        Log("C")
    Log("D")
    # Output: A D B C inner
```
<!-- #> -->

The execution order follows the LIFO principle at each nesting
level—inner defers execute after the outer defer's code, maintaining
the stack-like cleanup order.

**Defers in Control Flow:**

Defers work correctly within all control flow constructs:

<!--versetest
Log(S:string)<transacts>:void={}
<#
-->
<!-- 67 -->
```verse
ProcessLoop():void =
    for (I := 0..2):
        Log("Start")
        defer:
            Log("Cleanup")  # Runs after each iteration
        Log("End")
    # Output: Start End Cleanup Start End Cleanup Start End Cleanup

ProcessWithIf(Condition:logic):void =
    if (Condition?):
        defer:
            Log("Then cleanup")
        Log("Then body")
    else:
        defer:
            Log("Else cleanup")
        Log("Else body")
```
<!-- #> -->

Each control flow path executes its own defers independently.

**Defer Restrictions.** The defer statement has important restrictions
to ensure predictable behavior:

1. **Cannot be empty:** Defer blocks must contain at least one
   expression:

2. **Cannot be used as expression:** Defer cannot be used in positions
   where a value is expected.

3. **Cannot cross boundaries:** Defer blocks cannot contain `return`,
   `break`, or other control flow that would exit the defer's scope.

4. **Cannot fail:** Expressions in defer blocks cannot fail.

5. **Cannot suspend directly:** Defer blocks cannot contain suspend
   expressions, but they can use `branch` or `spawn` for
   fire-and-forget async operations.

## Profiling

Understanding how your code performs is crucial for optimization, and
the `profile` expression measures execution time:

<!--versetest-->
<!-- 73 -->
```verse
OptimizedCalculation():float =
    profile("Complex Math"):
        var Result:float = 0.0
        for (I := 1..1000000):
            set Result += Sin(I*1.0) * Cos(I*1.0)
        Result
```

The profile expression wraps around the code you want to measure,
logging the execution time to the output. You can add descriptive tags
to organize your profiling output, making it easier to identify
bottlenecks in complex systems.

Profile expressions pass through their results transparently, meaning
you can wrap them around any expression without changing the program's
behavior:

<!--versetest
BaseDamage:float = 50.0
GetMultiplier()<computes>:float = 1.5
GetCriticalBonus()<computes>:float = 2.0

M():void =
    PlayerDamage := profile("Damage Calculation"):
        BaseDamage * GetMultiplier() * GetCriticalBonus()
<#
-->
<!-- 74 -->
```verse
PlayerDamage := profile("Damage Calculation"):
    BaseDamage * GetMultiplier() * GetCriticalBonus()
```
<!-- #> -->

