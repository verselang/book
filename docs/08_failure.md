# Failure

Most programming languages treat control flow as a matter of true or
false, yes or no, one or zero. They evaluate boolean conditions and
branch accordingly, creating a world of binary decisions that often
requires checking conditions twice - once to see if something is
possible, and again to actually do it. Verse takes a different
approach. Instead of asking "is this true?", Verse asks "does this
succeed?"

This distinction might seem subtle, but it changes how programs are
written and reasoned about. Failure isn't an error or an
exception-it's a first-class concept that drives control flow. When an
expression fails, it doesn't crash your program or throw an exception
that needs to be caught. Instead, failure is a normal, expected
outcome that your code handles gracefully through the structure of the
language itself.

Consider the simple act of accessing an array element. In traditional languages, you might write:

<!--NoCompile-->
<!-- 01 -->
```verse
if (Index < Array.length) {  # Traditional, non-Verse
    Value = Array[index]
    Process(Value)
}
```

This checks validity separately from access, creating opportunities
for bugs if the check and access become separated or if the array
changes between them. In Verse, validation and access are unified:

<!--versetest
Array:[]int = array{1,2,3}
Index:int = 1
Process(V:int):void = {}
-->
<!-- 02 -->
```verse
if (Value := Array[Index]):
    Process(Value)
```

The array access either succeeds and binds the value, or it fails and
execution moves on. There is no separate validation step, so
the check and access cannot become inconsistent, and no undefined
behavior from accessing invalid indices.

## Failable Expressions

A failable expression is one that can either succeed and produce a value, or fail and produce nothing. This isn't the same as returning null or an error code - when an expression fails, it literally produces no value at all. The computation stops at that point in that particular path of execution.

Many operations are naturally failable. Array indexing fails when the index is out of bounds. Map lookups fail when the key doesn't exist. Comparisons fail when the values aren't equal. Division fails when dividing by zero. Even simple literals can be made to fail:

<!--versetest
M()<decides>:void =
    42
    false?
    true?
<#
-->
<!-- 03 -->
```verse
42      # Always succeeds with value 42
false?  # Always fails - the query of false
true?   # Always succeeds - the query of true
```
<!-- #> -->

The query operator `?` turns any value into a failable expression. When applied to `false`, it always fails. When applied to any other value, it succeeds with that value. This simple mechanism provides immense power for controlling program flow.

You can create your own failable expressions through functions marked with the `<decides>` effect:

<!--versetest-->
<!-- 04 -->
```verse
ValidateAge(Age:int)<decides>:int =
    Age >= 0    # Fails if age is negative
    Age <= 150  # Fails if age is unrealistic
    Age         # Returns the age if both checks pass
```
<!-- ValidateAge[10] -->

This function doesn't just check conditions - it embodies them. If the age is invalid, the function fails. If it's valid, it succeeds with the age value. The validation and the value are inseparable.

## Failure Contexts

Not every part of a program can execute failable expressions. They can only appear in failure contexts--places where the language knows how to handle both success and failure. Each failure context defines what happens when expressions within it fail.

The most common failure context is the condition of an `if` expression:

<!--versetest
Name:string="Joe"
GetPlayerByName(B:string)<decides><transacts>:int = 0
GetPlayerScore(B:int)<transacts><decides>:int = 0
-->
<!-- 05 -->
```verse
if (Player := GetPlayerByName[Name], Score := GetPlayerScore[Player], Score > 100):
    Print("High scorer: {Name} with {Score} points!")
```

This `if` condition contains three potentially failable expressions. All must succeed for the body to execute. If any fails, the entire condition fails, and control moves to the `else` branch (if present) or past the `if` entirely. The beauty is that each expression can use the results of previous ones - `Score` is only computed if we successfully found the `Player`.

The `for` expression creates a failure context for each iteration:

<!--versetest
Inventory:[]int= array{1}
IsWeapon:[]int= array{1}
GetDamage(:int)<computes><decides>:int=1
-->
<!-- 06 -->
```verse
for (Item : Inventory, IsWeapon[Item], Damage := GetDamage[Item], Damage > 50):
    Print("Powerful weapon: {Item} with {Damage} damage")
```

Each iteration attempts the failable expressions. If they all succeed, the body executes for that item. If any fails, that iteration is skipped, and the loop continues with the next item. This creates a natural filtering mechanism without explicit conditional logic.

Functions marked with `<decides>` create a failure context for their entire body:

<!--versetest
item:=struct{}
IsWeapon(i:item)<computes><decides>:void={}
GetDamage(i:item)<computes><decides>:int=0
-->
<!-- 07 -->
```verse
FindBestWeapon(Inventory:[]item)<decides>:item =
    var BestWeapon:?item = false
    var MaxDamage:int = 0

    for (Item : Inventory, IsWeapon[Item], Damage := GetDamage[Item]):
        if (Damage > MaxDamage):
            set BestWeapon = option{Item}
            set MaxDamage = Damage

    BestWeapon?  # Fails if no weapon was found
```

The function body is a failure context, allowing failable expressions throughout. The final line extracts the value from the option, failing if no weapon was found.

## Speculative Execution

When you execute code in a failure context, changes to mutable variables are provisional—they only become permanent if the entire context succeeds. Functions that modify state in failure contexts must use the `<transacts>`  or the `<writes>` effect specifier (see [Effects](13_effects.md)):

<!--NoCompile-->
<!-- 08 -->
```verse
m:=module:
    buyer := class:
        var PlayerGold:int
        AttemptPurchase(Cost:int)<transacts><decides>:void =
           set PlayerGold = PlayerGold - Cost  # Provisional change
           PlayerGold >= 0                     # Check if still valid
           # If this fails, PlayerGold reverts to original value
```

If the check fails, the subtraction is automatically rolled back. You
don't need to manually restore the original value or check conditions
before modifying state.

This transactional behavior makes complex state updates safe and
predictable. Either everything succeeds and all changes are committed,
or something fails and nothing changes.

<!--versetest
game_state := struct{}
game := class:
    var State:game_state = game_state{}
    ModifyHealth()<transacts>:void = {}
    UpdateInventory()<transacts>:void = {}
    ChargeResources()<transacts>:void = {}
    ValidateFinalState()<transacts><decides>:void = {}
    ComplexOperation()<transacts><decides>:void =
       ModifyHealth()
       UpdateInventory()
       ChargeResources()
       ValidateFinalState[]
<#
-->
<!-- 09 -->
```verse
game := class:
    var State:game_state
    ComplexOperation()<transacts><decides>:void =
       ModifyHealth()       # All these operations
       UpdateInventory()    # are provisional
       ChargeResources()    # until all succeed
       ValidateFinalState[] # If this fails, everything rolls back
```
<!-- #> -->

The `game` class has multiple methods that update the `game_state`,
before returning `ComplexOperation` validates that the object is in a
valid state, if it is not, all changes performed in the method are
rolled back.

## The Logic of Failure

Verse provides logical operators that work with failure, creating an
algebra for combining failable expressions.

The `and` operator ensures that both expression succeed.
The `not` operator inverts success and failure:

<!--versetest
Score:int=10
GetNearestEnemy()<decides><computes>:int=0
-->
<!-- 10 -->
```verse
if (not (Enemy := GetNearestEnemy[]) and Score > 0):
    Print("Coast is clear!")  # Executes when GetNearestEnemy fails
```

It is noteworthy that `Enemy` is not in scope within the `then` branch
because it is under a `not`.

The `or` operator provides alternatives:

<!--versetest
DefaultWeapon:?string=false
PrimaryWeapon()<decides><computes>:string="primary"
SecondaryWeapon()<decides><computes>:string="sword"
-->
<!-- 11 -->
```verse
Weapon := PrimaryWeapon[] or SecondaryWeapon[] or DefaultWeapon?
```

This tries each option in order, stopping at the first success. It's
not evaluating boolean conditions - it's attempting computations and
taking the first one that succeeds.

You can combine these operators to create sophisticated control flow:

<!--versetest
player := struct{}
IsAlive(P:player)<computes><decides>:void = {}
IsStunned(P:player)<computes><decides>:void = {}
HasAmmunition(P:player)<computes><decides>:void = {}
HasMeleeWeapon(P:player)<computes><decides>:void = {}
-->
<!-- 12 -->
```verse
ValidatePlayer(Player:player)<decides>:void =
    IsAlive[Player]
    not IsStunned[Player]
    HasAmmunition[Player] or HasMeleeWeapon[Player]
```

This function succeeds only if the player is alive, not stunned, and
has either ammunition or a melee weapon. Each line is a separate
failable expression that must succeed.

Another interesting use case is `not not Exp` -- it succeeds if `Exp`
succeeds but all effects of `Exp` are thrown away. This is a way to
try to see if a complex operation would succeed.

## Expressions in Decides

A subtle feature is how relational expressions behave in decides
contexts. When a comparison appears in a context that can handle
failure, it doesn't just test a condition—it produces a value,
specifically it returns its left-hand side. So `X>0` returns `X` and
`0<=X` returns `0`.  This behavior applies to all comparison operators
in decides contexts:

<!--versetest-->
<!-- 14 -->
```verse
GetIfNotEqual(X:int, Y:int)<decides>:int =
    X <> Y  # Returns X when X ≠ Y, fails when X = Y

GetIfLessOrEqual(X:int, Limit:int)<decides>:int =
    X <= Limit  # Returns X when X ≤ Limit, fails otherwise

GetIfGreaterThan(X:int, Threshold:int)<decides>:int =
    X > Threshold  # Returns X when X > Threshold, fails otherwise
```
<!--
GetIfNotEqual[1,2]
GetIfGreaterThan[11,2]
GetIfLessOrEqual[1,2]
-->

Comparison expressions of the form `A op B` return `A` when the
comparison succeeds, and fail when the comparison is false.

This creates concise validation functions that either return `Value` or fail:

<!--versetest-->
<!-- 16 -->
```verse
ValidateInRange(Value:int, LwrBnd:int, UprBnd:int)<decides>:int =
    Value >= LwrBnd and Value <= UprBnd
```
<!-- ValidateInRange[5,0,10] -->

## Option Types

The option type and failure are intimately connected. An option either
contains a value or is empty (represented by `false`). The query
operator `?` converts between options and failure:

<!--versetest-->
<!-- 18 -->
```verse
M()<decides>:void=
    MaybeValue:?int = option{42}  # An optional int
    Value := MaybeValue?          # Succeeds with 42

    Empty:?int = false            # An empty value
    Other := Empty?               # Failure
```

The `option{}` constructor works in reverse, converting failure to an empty option:

<!--versetest
RiskyComputation()<computes><decides>:int=1
-->
<!-- 19 -->
```verse
Result := option{RiskyComputation[]} # option{value} if computation succeeds
                                     # otherwise false
```
<!-- Result -->

This bidirectional conversion makes options and failure
interchangeable, allowing you to choose the most appropriate
representation for your specific use case.

The option type `?T` represents values that may or may not be present.
The question mark appears *before* the type, not after:

<!--versetest-->
<!-- 20 -->
```verse
ValidSyntax:?int = option{42}      # Correct
```
<!-- ValidSyntax? -->

The `?` prefix applies to any type:

<!--versetest
player := struct{}
-->
<!-- 21 -->
```verse
MaybeNumber:?int = option{42}
MaybeText:?string = option{"hello"}
MaybePlayer:?player = option{player{}}
```

Use the `option{}` constructor to wrap a value:

<!--versetest
RiskyComputation()<computes><decides>:int=1
-->
<!-- 22 -->
```verse
Filled:?int = option{42}
Empty:?int  = false
Result:?int = option{RiskyComputation[]}  # false if computation fails
```

Empty options and `false` are equivalent—an empty option *is* `false`:

<!--versetest-->
<!-- 23 -->
```verse
EmptyOption:?int = false
EmptyOption = false  # This comparison succeeds
```

Verse has a rich and flexible syntax which can also sometimes cause
subtle bugs. A comma gives rise to a tuple in an `option` whereas a
semicolon evaluates all values but retain only the last one:

<!--versetest-->
<!-- 24 -->
```verse
# Comma creates tuple
option{1, 2}? = (1, 2)

# Semicolon creates sequence - last value is used
option{1; 2}? = 2
```

### Unwrapping

The query operator `?` extracts values from options, failing if the option is empty:

<!--versetest-->
<!-- 25 -->
```verse
M()<decides>:void=
    MaybeValue:?int = option{42}
    Value := MaybeValue?  # Succeeds with 42

    Empty:?int = false
    Other := Empty?  # Fails - cannot unwrap empty option
```

Unwrapping is only allowed in failure contexts:

<!--versetest
MaybeInt:?int = option{42}
UseItem(I:int):void={}
ProcessItem(I:int)<computes>:?int=option{3}
Items:[]int = array{1,2,3}
-->
<!-- 26 -->
```verse
# Valid: In if condition (failure context)
if (Value := MaybeInt?):
    Print("Got {Value}")

# Valid: In for loop (failure context)
for (Item : Items, ValidItem := ProcessItem(Item)?):
    UseItem(Item)

# Valid: In <decides> function body (failure context)
GetRequired(Maybe:?int)<decides>:int =
    Maybe?  # Fails if Maybe is empty
```

### Nesting

Options can be nested to represent multiple layers of absence:

<!--versetest-->
<!-- 27 -->
```verse
# Double-nested option
Double:??int = option{option{42}}

# Single unwrap gets outer option
if (Inner := Double?):
    if (TheValue := Inner?):
        # TheValue has type int, equals 42

# Double unwrap gets the value directly
Value := Double??  # Fails if either layer is empty
```

Helper functions also work with nested options:

<!--versetest-->
<!-- 28 -->
```verse
UnpackNested(MaybeValue:??int):?int =
    if (Inner := MaybeValue?):
        Inner
    else:
        option{-1}  # Default for outer empty

DirectUnpack(MaybeValue:??int):int =
    if (Value := MaybeValue??):
        Value
    else:
        -1  # Default for any level empty
```
<!--
UnpackNested(option{option{1}})
DirectUnpack(option{option{2}})
-->

### Chained Access

The `?.` operator provides safe member access on optional values:

<!--NoCompile-->
<!-- 29 -->
```verse
entity := class:
    Name:string = "Unknown"
    Health:int = 100

MaybeEntity:?entity = option{entity{}}

# Safe field access
if (Name := MaybeEntity?.Name):
    Print("Entity: {Name}")  # Succeeds

# Safe method call
MaybeEntity?.TakeDamage(10)  # Only calls if entity present

# Chaining through multiple optionals
linked_list := class:
    Value:int = 0
    Next:?linked_list = false

Head:?linked_list = option{linked_list{Value := 1}}
SecondValue := Head?.Next?.Value  # Fails if any link is empty
```

The `?.` operator short-circuits—if the option is empty, the entire
expression fails without evaluating the member access.

### Defaulting

Use the `or` operator to provide fallback values for empty options:

<!--versetest-->
<!-- 30 -->
```verse
MaybeValue:?int = false
Value := MaybeValue? or 42  # Yields 42

# Chaining multiple options
Primary:?string = false
Secondary:?string = option{"backup"}
Default:string = "default"

Result := Primary? or Secondary? or Default
```
### Comparison

Empty options equal `false`, and filled options equal their unwrapped values when compared properly:

<!--versetest-->
<!-- 40 -->
```verse
EmptyOption:?int = false
EmptyOption = false  # Succeeds

FilledOption:?int = option{1}
FilledOption? = 1  # Succeeds - unwrap then compare
```

However, you cannot directly compare optional and non-optional values without unwrapping:

<!--versetest-->
<!-- 41 -->
```verse
Opt:?int = option{42}
Regular:int = 42

# Must unwrap to compare
if (Opt? = Regular):
    Print("Equal")
```

## Failure with Optionals

Combining decides functions with optional return types, creates a system with
multiple layers of failure. This pattern enables expressing complex conditions
concisely while maintaining clarity.

A function can fail at two levels:

- *Function-level failure*: The entire function fails using `<decides>`
- *Value-level failure*: The function succeeds but returns an empty option

<!--versetest
player := string
IsActive(S:string)<transacts><decides>:string=""
LookupPlayer(S:string)<transacts><decides>:string="player"
-->
<!-- 42 -->
```verse
FindEligiblePlayer(Name:string)<decides>:?player =
    Name <> ""           # Layer 1: Fail if name is empty
    Player := LookupPlayer[Name]  # Layer 1: Fail if player not found
    option{IsActive[Player]}      # Layer 2: Empty option if player inactive
```
<!-- FindEligiblePlayer["Someone"] -->

This function has three possible outcomes:

- *Function fails*: Empty name or player not found
- *Function succeeds with empty option*: Player found but inactive
- *Function succeeds with filled option*: Player found and active

Calling this function demonstrates the layered failure:

<!--versetest
FindEligiblePlayer(S:string)<transacts><decides>:?string=option{S}
-->
<!-- 43 -->
```verse
# Function-level failure
Result1 := FindEligiblePlayer[""]  # Fails, Result1 never assigned

# Function succeeds, returns empty option
if (Player := FindEligiblePlayer["InactiveUser"]?):
    # Won't execute - function succeeds but ? query fails
else:
    # Executes here

# Function succeeds, returns filled option
if (Player := FindEligiblePlayer["ActiveUser"]?):
    # Executes with Player bound to the active player
```

This pattern is particularly powerful for validation with different failure modes:

<!--versetest-->
<!-- 44 -->
```verse
ValidateScore(Score:int)<decides>:?int =
    Score >= 0           # Layer 1: Reject negative scores (invalid input)
    option{Score <= 100} # Layer 2: Reject high scores (out of range)
```

The distinction between function-level and value-level failure lets
you express different kinds of errors. Function-level failure
typically means "this operation couldn't complete" while value-level
failure means "the operation completed but the result doesn't meet the
expected criteria."

## Casts as Decides

Type casting in Verse is integrated into the failure system. A dynamic cast
behaves just like a `<decides>` function call and similarly uses bracket
syntax. For example `Type[value]` attempts to cast `value`'s type to `Type` and
fails if unsuccessful.

<!-- TODO: link to chapter 10?  -->
This is also works with user defined types which must specify `<castable>`:

<!--versetest
component := class<castable>:
    Name:string = "Component"

physics_component := class<castable>(component):
    Velocity:float = 0.0

TryGetPhysics(Comp:component)<decides>:physics_component =
    physics_component[Comp]
<#
-->
<!-- 48 -->
```verse
component := class<castable>:
    Name:string = "Component"

physics_component := class<castable>(component):
    Velocity:float = 0.0

# Casting as a decides operation
TryGetPhysics(Comp:component)<decides>:physics_component =
    physics_component[Comp]  # Succeeds if Comp is actually a physics_component
```
<!-- #> -->

This makes type-based dispatch easily expressible:

<!--versetest
component := class<castable>:
    Name:string = "Component"
physics_component := class<castable>(component):
    Velocity:float = 0.0
render_component := class<castable>(component):
    Renderer:string = "RayTrace"
UpdatePhysics(P:physics_component):void={}
UpdateRendering(R:render_component):void={}
UpdateGeneric(G:component):void={}
-->
<!-- 49 -->
```verse
ProcessComponent(Comp:component):void =
    if (Physics := physics_component[Comp]):
        UpdatePhysics(Physics)
    else if (Render := render_component[Comp]):
        UpdateRendering(Render)
    else:
        # Unknown component type
        UpdateGeneric(Comp)
```
<!-- ProcessComponent(component{}) -->

The cast itself is the condition—no separate type checking needed. When the cast succeeds, you have both confirmed the type and obtained a properly-typed reference.

You can chain casts with other decides operations:

<!--versetest
component := class<castable>:
    Name:string = "Component"
physics_component := class<castable>(component):
    Velocity:float = 0.0
render_component := class<castable>(component):
    Renderer:string = "RayTrace"
UpdatePhysics(P:physics_component):void=return
UpdateRendering(R:render_component):void=return
UpdateGeneric(G:component):void=return
entity := class:
    GetComponent()<transacts><decides>:component=
        component{}
IsActive(c:component)<transacts><decides>:logic=true
-->
<!-- 50 -->
```verse
GetActivePhysicsComponent(Entity:entity)<decides>:physics_component =
    Comp := Entity.GetComponent[]  # Fails if no component
    Physics := physics_component[Comp]  # Fails if not physics
    IsActive[Physics]  # Fails if inactive
    Physics
```

Each step must succeed for the function to return a value. This creates self-documenting validation chains where type requirements are explicit.

Casts work with the `or` combinator for fallback types:

<!--versetest
component := class<castable>:
    Name:string = "Component"
physics_component := class<castable>(component):
    Velocity:float = 0.0
trigger_component := class<castable>(component):
    Trigger:float = 0.0
scripted_component := class<castable>(component):
    Scripted:string = "Something"
UpdatePhysics(P:physics_component):void=return
UpdateGeneric(G:component):void=return
entity := class:
    GetComponent()<transacts><decides>:component=
        component{}
IsActive(c:component)<transacts><decides>:logic=true
GetInteractable(Entity:entity)<decides><transacts>:component =
    physics_component[Entity] or
    trigger_component[Entity] or
    scripted_component[Entity]
<#
-->
<!-- 51 -->
```verse
GetInteractable(Entity:entity)<decides>:component =
    physics_component[Entity] or
    trigger_component[Entity] or
    scripted_component[Entity]
```
<!--
#>
GetInteractable[entity{}]
-->

This tries each cast in order, returning the first successful one. It's type-safe because all options share the common `component` base type.



## Idioms and Patterns

As you work with failure, certain patterns emerge that solve common problems elegantly.

The validation chain pattern uses sequential failures to ensure all conditions are met:

<!--versetest
action := struct{}
player := struct{}
location := struct{}
GetActingPlayer(A:action)<transacts><decides>:player = player{}
IsValidTurn(P:player)<computes><decides>:void = {}
HasRequiredResources(P:player, A:action)<computes><decides>:void = {}
GetTargetLocation(A:action)<transacts><decides>:location = location{}
IsValidLocation(L:location)<computes><decides>:void = {}
ExecuteAction(A:action)<transacts><decides>:void = {}
-->
<!-- 62 -->
```verse
ProcessAction(Action:action)<decides>:void =
    Player := GetActingPlayer[Action]
    IsValidTurn[Player]
    HasRequiredResources[Player, Action]
    Location := GetTargetLocation[Action]
    IsValidLocation[Location]
    ExecuteAction[Action]
```

Each line must succeed for execution to continue. This creates self-documenting code where preconditions are explicit and checked in order.

The first-success pattern tries alternatives until one works:

<!--versetest
location := struct{}
path := struct{}
DirectPath(S:location, E:location)<transacts><decides>:path = path{}
PathAroundObstacles(S:location, E:location)<transacts><decides>:path = path{}
ComplexPathfinding(S:location, E:location)<transacts><decides>:path = path{}
-->
<!-- 63 -->
```verse
FindPath(Start:location, End:location)<decides>:path =
    DirectPath[Start, End] or
    PathAroundObstacles[Start, End] or
    ComplexPathfinding[Start, End]
```

This naturally expresses trying simple solutions before complex ones.

The filtering pattern uses failure to select items:

<!--versetest
enemy := struct{}
GetLevel(E:enemy)<computes><decides>:int = 10
-->
<!-- 64 -->
```verse
GetEliteEnemies(Enemies:[]enemy):[]enemy =
    for (Enemy : Enemies, Level := GetLevel[Enemy], Level >= 10):
        Enemy
```

Only enemies that have a level and whose level is at least 10 are included in the result.

The transaction pattern groups related changes:

<!--versetest
player := class:
    var Inventory:[]item = array{}
item := struct{}
RemoveItem(P:player, I:item)<transacts><decides>:void = {}
AddItem(P:player, I:item)<transacts>:void = {}
ValidateTrade(P1:player, P2:player)<computes><decides>:void = {}

TradeItems(PlayerA:player, PlayerB:player, ItemA:item, ItemB:item)<transacts><decides>:void =
    RemoveItem[PlayerA, ItemA]
    RemoveItem[PlayerB, ItemB]
    AddItem(PlayerA, ItemB)
    AddItem(PlayerB, ItemA)
    ValidateTrade[PlayerA, PlayerB]
<#
-->
<!-- 65 -->
```verse
TradeItems(var PlayerA:player, var PlayerB:player, ItemA:item, ItemB:item)<transacts><decides>:void =
    RemoveItem(PlayerA, ItemA)
    RemoveItem(PlayerB, ItemB)
    AddItem(PlayerA, ItemB)
    AddItem(PlayerB, ItemA)
    ValidateTrade[PlayerA, PlayerB]
```
<!-- #> -->

Either the entire trade succeeds, or nothing changes.

**Optional Indexing**

When working with optional containers, you can access their contents
using specialized query syntax that combines optional checking with
element access.  Optional tuples support direct element access through
the query operator:

<!--versetest-->
<!-- 58 -->
```verse
MaybePair:?tuple(int, string) = option{(42, "answer")}

# Access first element
if (FirstValue := MaybePair?(0)):
    # FirstValue is 42 (type: int)
    Print("First: {FirstValue}")

# Access second element
if (SecondValue := MaybePair?(1)):
    # SecondValue is "answer" (type: string)
    Print("Second: {SecondValue}")
```

The syntax `Option?(index)` simultaneously:

- Queries whether the option is non-empty
- Accesses the tuple element at the given index
- Binds the element value if both succeed

**Composition and Call Chains**

Decides functions compose naturally, allowing complex operations to be
built from simple, reusable pieces. When a decides function calls
another decides function, failures propagate automatically.

<!--versetest-->
<!-- 52 -->
```verse
ValidatePositive(X:int)<decides>:int =
    X > 0

Double(X:int)<decides>:int =
    Validated := ValidatePositive[X]  # Fails if X ≤ 0
    Validated * 2
```
<!-- Double[2] -->

If `ValidatePositive` fails, `Double` fails immediately. The validated value flows through the chain.

**Preserving failure context:**

When calling decides functions in non-decides contexts, you must handle failure explicitly:

<!--versetest
FindPlayer(Name:string)<transacts><decides>:string=Name
GetDefaultPlayer():string="Default"
UsePlayer(P:string):void=return
-->
<!-- 57 -->
```verse
# This won't compile - ProcessPlayer doesn't have <decides>
# BadProcessPlayer(Name:string):void =
#    Player := FindPlayer[Name]  # ERROR: Unhandled failure

# Handle with if
ProcessPlayerWithIf(Name:string):void =
    if (Player := FindPlayer[Name]):
        UsePlayer(Player)

# Handle with or
ProcessPlayerWithOr(Name:string):void =
    Player := FindPlayer[Name] or GetDefaultPlayer()
    UsePlayer(Player)
```
<!--
PlayerOne := "PlayerOne"
ProcessPlayerWithIf(PlayerOne)
ProcessPlayerWithOr(PlayerOne)
-->

Understanding composition helps you build complex validation logic
from simple, testable pieces.

## Runtime Errors

While failure (`<decides>`) represents normal control flow with
transactional rollback, *runtime errors* represent unrecoverable
conditions that terminate execution. Runtime errors propagate up the
call stack, bypassing normal failure handling, and cannot be caught or
recovered within Verse code.

The `Err()` function explicitly triggers a runtime error with an optional message:

<!--versetest-->
<!-- 66 -->
```verse
ValidateInput(Value:int):int =
    if (Value < 0):
        Err("Negative values not allowed")
    Value
```

When a runtime error occurs, execution unwinds through the call stack,
terminating the current operation:

<!--versetest
Log(Message:string)<transacts>:void = {}
-->
<!-- 68 -->
```verse
DeepFunction()<transacts>:int =
    Log("C")
    Err("Fatal error")  # Runtime error here
    Log("D")            # Never executes
    return 1

MiddleFunction():int =
    Log("B")
    Result := DeepFunction()  # Error propagates through here
    Log("E")                  # Never executes
    return Result

TopFunction():void =
    Log("A")
    Value := MiddleFunction()  # Error propagates to here
    Log("F")                   # Never executes

# Execution order: A, B, C, then terminates
# Output: "ABC"
```

The runtime error propagates immediately, bypassing all subsequent code in the call chain.

Runtime errors propagate through asynchronous operations, terminating spawned tasks:

<!--versetest
Log(Message:string)<transacts>:void = {}
WaitTicks(Count:int)<suspends>:void = {}
-->
<!-- 69 -->
```verse
AsyncOperation()<suspends>:int =
    Log("Start")
    WaitTicks(1)
    Err("Async error")  # Runtime error during async execution
    WaitTicks(1)        # Never executes
    return 1

KickOff()<suspends>:void=
    # Error propagates out of spawned task
    spawn{ AsyncOperation() }

```

When a spawned task encounters a runtime error, that specific task
terminates. The runtime error does not automatically propagate to the
spawning context.

## Living with Failure

Verse's approach to failure has roots in logic programming, where
computations search for solutions rather than executing steps. When a
path fails, the computation backtracks and tries alternatives. This
non-deterministic model, while powerful, can be hard to reason about
in its full generality.  Verse tames this power by making failure
contexts explicit and limiting backtracking to specific
constructs. You get the benefits of logic programming - declarative
code, automatic search, elegant handling of alternatives - without the
complexity of full unification and unbounded backtracking.

Consider a simple logic puzzle solver:

<!--versetest
constraint := struct{}
solution := struct{}
InitialState()<transacts>:solution = solution{}
ApplyConstraint(S:solution, C:constraint)<transacts>:void = {}
ValidateSolution(S:solution)<computes><decides>:void = {}

SolvePuzzle(Constraints:[]constraint)<decides>:solution =
    var State:solution = InitialState()
    for (Constraint : Constraints):
        ApplyConstraint(State, Constraint)
    ValidateSolution[State]
    State
<#
-->
<!-- 73 -->
```verse
SolvePuzzle(Constraints:[]constraint)<decides>:solution =
    var State:solution = InitialState()
    for (Constraint : Constraints):
        ApplyConstraint(State, Constraint)
    ValidateSolution[State]
    State
```
<!-- #> -->

If any constraint can't be satisfied, the entire attempt fails. In a full logic programming language, this might trigger complex backtracking. In Verse, the failure model is simpler and more predictable while still being expressive enough for most problems.

Working effectively with failure in Verse requires a shift in mindset. Instead of thinking about error conditions that need to be avoided, think about success conditions that need to be met. Instead of defensive programming that checks everything before acting, write optimistic code that attempts operations and handles failure gracefully.

This perspective makes code more readable and intent more clear. When you see a function marked with `<decides>`, you know it represents a computation that might not have a result. When you see expressions in sequence within a failure context, you know they represent conditions that must all be met. When you see the `or` operator, you know it represents alternatives to try.

Failure in Verse isn't something to be feared or avoided - it's a tool to be embraced. It makes programs safer by eliminating certain categories of bugs. It makes code clearer by unifying validation and action. It makes complex operations simpler by providing automatic rollback. Most importantly, it aligns the way we write programs with the way we think about actions and decisions in the real world.

As you write more Verse code, you'll find that failure becomes second nature. You'll reach for failable expressions naturally when expressing conditions. You'll structure your functions to fail early when preconditions aren't met. You'll compose failures to create sophisticated control flow without nested conditionals. And you'll appreciate how this different way of thinking about control flow leads to code that is both more robust and more expressive than traditional approaches.
