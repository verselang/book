# Structs and Enums

Structs and enums represent Verse's value-oriented type system, providing lightweight alternatives to classes for simple data aggregation and fixed sets of named values. Unlike classes with their object-oriented features, structs and enums focus on simplicity, immutability, and value semantics.

Structs bundle related data without methods or inheritance, perfect for mathematical types, configuration data, and simple records. Enums define fixed sets of named constants, replacing magic numbers with meaningful names and providing compile-time safety through exhaustive pattern matching.

Together, structs and enums complement classes and interfaces by offering simpler, more constrained type constructors optimized for specific use cases.

## Structs

Structs provide lightweight data containers without the object-oriented features of classes. They're value types optimized for simple data aggregation, making them perfect for mathematical types, data transfer objects, and any scenario where you need a simple bundle of related values without behavior.

Structs group related data with minimal overhead:

<!--NoCompile-->
<!-- 01 -->
```verse
damage_type:= enum:
    Physical
character := struct{}
vector2 := struct:
    X : float = 0.0
    Y : float = 0.0

color := struct:
    R : int = 0
    G : int = 0
    B : int = 0
    A : int = 255  # Alpha channel

damage_info := struct:
    Amount : int = 0
    Type : damage_type = damage_type.Physical
    Source : ?character = false
    IsCritical : logic = false
```

All struct fields are public and immutable by default. Structs cannot have methods, constructors, or participate in inheritance hierarchies. This simplicity makes them efficient and predictable.

### Construction

Creating struct instances uses the same archetype syntax as classes:

<!--versetest
vector2 := struct:
    X : float = 0.0
    Y : float = 0.0

color := struct:
    R : int = 0
    G : int = 0
    B : int = 0
    A : int = 255

M()<transacts>:void =
    Origin := vector2{}
    PlayerPos := vector2{X := 100.0, Y := 250.0}
    RedColor := color{R := 255}
    NewPos := PlayerPos
<#
-->
<!-- 02 -->
```verse
Origin := vector2{}  # Uses defaults: (0.0, 0.0)
PlayerPos := vector2{X := 100.0, Y := 250.0}
RedColor := color{R := 255}  # Other channels default to 0/255

# Structs are values - assignment creates a copy
NewPos := PlayerPos
# NewPos is a separate instance with the same values
```
<!-- #> -->

Since structs are value types, assigning a struct to a variable creates a copy of all its data. This differs from classes, which use reference semantics.

### Comparison

Structs with all comparable fields support equality comparison:

<!--versetest
vector3i := struct:
    X : int = 0
    Y : int = 0
    Z : int = 0

PrintMsg(S:string)<transacts>:void = {}

M()<transacts>:void =
    Origin := vector3i{}
    UnitX := vector3i{X := 1}

    if (Origin = vector3i{}):
        PrintMsg("At origin")

    if (Origin = UnitX):
        PrintMsg("Same position")
<#
-->
<!-- 03 -->
```verse
vector3i := struct:
    X : int = 0
    Y : int = 0
    Z : int = 0

Origin := vector3i{}
UnitX := vector3i{X := 1}

if (Origin = vector3i{}):  # Succeeds - all fields match
    Print("At origin")

if (Origin = UnitX):  # Fails - X fields differ
    Print("Same position")
```
<!-- #> -->

Comparison happens field by field, succeeding only if all corresponding fields are equal.

### Persistable Structs

Structs can be marked as persistable for use with Verse's persistence system:

<!--versetest
player_stats := struct<persistable>:
    HighScore : int = 0
    GamesPlayed : int = 0
    WinRate : float = 0.0

player := class<concrete><unique>{}

PlayerData : weak_map(player, player_stats) = map{}
<#
-->
<!-- 04 -->
```verse
player_stats := struct<persistable>:
    HighScore : int = 0
    GamesPlayed : int = 0
    WinRate : float = 0.0

# Can be used in persistent storage
PlayerData : weak_map(player, player_stats) = map{}
```
<!-- #> -->

Once published, persistable structs cannot be modified, ensuring data compatibility across game updates.

## Enums

Enums define types with a fixed set of named values, perfect for representing states, types, or any concept with a known, finite set of alternatives. They make code more readable by replacing magic numbers with meaningful names and provide compile-time safety by restricting values to the defined set.

An enum lists all possible values for a type:

<!--NoCompile-->
<!-- 05 -->
```verse
game_state := enum:
    MainMenu
    Playing
    Paused
    GameOver

damage_type := enum:
    Physical
    Fire
    Ice
    Lightning
    Poison

direction := enum:
    North
    East
    South
    West
```

Each value in the enum becomes a named constant of that enum type. The compiler ensures that variables of an enum type can only hold one of these defined values. Enums can even be empty:

<!--versetest
placeholder := enum{}
<#
-->
<!-- 06 -->
```verse
placeholder := enum{}  # Valid but rarely useful
```
<!-- #> -->

Enums introduce both a type and a set of values, and it's crucial to distinguish between them:

<!--versetest
status := enum:
    Active
    Inactive


CurrentStatus:status = status.Active
<#
-->
<!-- 07 -->
```verse
status := enum:
    Active
    Inactive

# status is the TYPE
# status.Active and status.Inactive are VALUES

CurrentStatus:status = status.Active  # OK - value of type status
```
<!-- #> -->

You cannot use the enum type where a value is expected:

<!--versetest
status := enum:
    Active
    Inactive

M()<transacts>:void =
    GoodAssignment:status = status.Active
    var CurrentStatus:status = status.Active
    set CurrentStatus = status.Inactive
<#
-->
<!-- 08 -->
```verse
# ERROR: Cannot use type as value
BadAssignment:status = status  # Compile error
set CurrentStatus = status     # Compile error

# CORRECT: Use enum values
GoodAssignment:status = status.Active  # OK
set CurrentStatus = status.Inactive    # OK
```
<!-- #> -->

This distinction prevents confusion and ensures type safety. The enum type defines what values are possible, while enum values are the actual constants you use in your code.

### Restrictions

Enums have specific syntactic requirements that keep their usage clear and unambiguous:

**Enums must be direct right-hand side of definitions:**

<!--versetest
Priority := enum:
    Low
    Medium
    High
<#
-->
<!-- 09 -->
```verse
# Valid
Priority := enum:
    Low
    Medium
    High

# Invalid - cannot use enum in expressions
Result := -enum{A, B}      # Compile error
Value := enum{X, Y} + 1    # Compile error
```
<!-- #> -->

**Enums must be module or class-level definitions:**

<!--versetest
MyEnum := enum:
    Value1
    Value2

ProcessData():void = {}
<#
-->
<!-- 10 -->
```verse
# Valid
MyEnum := enum:
    Value1
    Value2

# Invalid - cannot define local enums
ProcessData():void =
    LocalEnum := enum{A, B}  # Compile error - no local enums
```
<!-- #> -->

These restrictions ensure enums remain stable, referenceable definitions throughout your codebase rather than ephemeral local values.

### Using Enums

Enums provide type-safe alternatives to error-prone string or integer constants:

<!--versetest
game_state := enum:
    MainMenu
    Playing
    Paused
    GameOver
-->
<!-- 11 -->
```verse
var CurrentState:game_state = game_state.MainMenu

ProcessInput(Input:string):void =
    case (CurrentState):
        game_state.MainMenu =>
            if (Input = "Start"):
                set CurrentState = game_state.Playing
        game_state.Playing =>
            if (Input = "Pause"):
                set CurrentState = game_state.Paused
        game_state.Paused =>
            if (Input = "Resume"):
                set CurrentState = game_state.Playing
            else if (Input = "Quit"):
                set CurrentState = game_state.MainMenu
        game_state.GameOver =>
            if (Input = "Restart"):
                set CurrentState = game_state.MainMenu
```

The `case` expression with enums provides powerful pattern matching with exhaustiveness checking that ensures you handle all possible values correctly.

### Open vs Closed Enums

Enums can be marked as open or closed, fundamentally affecting how they can evolve and how they interact with pattern matching:

<!--NoCompile-->
<!-- 12 -->
```verse
# Closed enum - cannot add values after publication
day_of_week := enum<closed>:  # <closed> is the default
    Monday
    Tuesday
    Wednesday
    Thursday
    Friday
    Saturday
    Sunday

# Open enum - can add new values after publication
weapon_type := enum<open>:
    Sword
    Bow
    Staff
    # Can add Wand, Dagger, etc. in updates
```

**Closed enums** (the default) commit to a fixed set of values forever. This allows the compiler to verify that case expressions handle all possibilities exhaustively. Use closed enums for truly fixed sets: days of the week, cardinal directions, fundamental game states.

**Open enums** allow new values to be added in future versions. This flexibility comes at a cost: case expressions cannot be exhaustive since future values might exist. Use open enums for extensible sets: item types, enemy types, damage types, or any content that may grow.

### Exhaustiveness

The interaction between enum types and case expressions follows sophisticated rules that prevent bugs while enabling both safety and flexibility. Understanding these rules is essential for working with enums effectively.

**Closed Enums with Full Coverage:**

When your case expression handles every value in a closed enum, no wildcard is needed:

<!--NoCompile-->
<!-- 13 -->
```verse
day := enum:
    Monday
    Tuesday
    Wednesday

# Exhaustive - all values covered
GetDayType(D:day):string =
    case (D):
        day.Monday => "Weekday"
        day.Tuesday => "Weekday"
        day.Wednesday => "Weekday"
    # No wildcard needed - all values handled
```

Adding a wildcard when all cases are covered triggers an unreachable code warning:

<!--versetest
day := enum:
    Monday
    Tuesday
    Wednesday

GetDayType(D:day):string =
    case (D):
        day.Monday => "Weekday"
        day.Tuesday => "Weekday"
        day.Wednesday => "Weekday"
<#
-->
<!-- 14 -->
```verse
# Warning: unreachable wildcard
GetDayType(D:day):string =
    case (D):
        day.Monday => "Weekday"
        day.Tuesday => "Weekday"
        day.Wednesday => "Weekday"
        _ => "Unknown"  # WARNING: unreachable - all values already matched
```
<!-- #> -->

**Closed Enums with Partial Coverage:**

If you don't match all values, you must either provide a wildcard or be in a `<decides>` context:

<!--NoCompile-->
<!-- 15 -->
```verse
day := enum:
    Monday
    Tuesday
    Wednesday
    Thursday

# With wildcard - OK
GetWeekStartWildCard(D:day):string =
    case (D):
        day.Monday => "Week start"
        _ => "Mid-week"

# Without wildcard but in <decides> context - OK
GetWeekStartDecides(D:day)<decides>:string =
    case (D):
        day.Monday => "Week start"
        # Missing other days causes failure

# Without either - COMPILE ERROR
# GetWeekStartBad(D:day):string =
#    case (D):
#        day.Monday => "Week start"
#        # ERROR: Missing cases and no wildcard
```

**Open Enums Always Require Wildcard or `<decides>`:**

Open enums can have new values added after publication, so they can never be exhaustive.\
This is to ensure backwards compatibility of functions using them (see also [Publishing Functions](06_functions.md/#publishing-functions)):

<!--NoCompile-->
<!-- 16 -->
```verse
weapon := enum<open>:
    Sword
    Bow
    Staff

# Must have wildcard - OK
GetWeaponClassWildCard(W:weapon):string =
    case (W):
        weapon.Sword => "Melee"
        weapon.Bow => "Ranged"
        weapon.Staff => "Magic"
        _ => "Unknown"  # REQUIRED - future values may exist

# In <decides> context without wildcard - OK
GetWeaponClassDecides(W:weapon)<decides>:string =
    case (W):
        weapon.Sword => "Melee"
        weapon.Bow => "Ranged"
        weapon.Staff => "Magic"
        # Can fail for unknown (future) values

# Without either - COMPILE ERROR
# GetWeaponClassBad(W:weapon):string =
#    case (W):
#        weapon.Sword => "Melee"
#        weapon.Bow => "Ranged"
#        weapon.Staff => "Magic"
#        # ERROR: Open enum requires wildcard or <decides>
```

Even if you match all currently defined values in an open enum, you still need a wildcard or `<decides>` context because new values might be added in future versions.

**Summary of Exhaustiveness Rules:**

| Enum Type | Case Coverage | Wildcard | Context | Result |
|-----------|---------------|----------|---------|--------|
| Closed | Full | No | Any | ✓ Valid - exhaustive |
| Closed | Full | Yes | Any | ⚠ Warning - unreachable wildcard |
| Closed | Partial | Yes | Any | ✓ Valid |
| Closed | Partial | No | `<decides>` | ✓ Valid - unmatched values fail |
| Closed | Partial | No | Non-`<decides>` | ✗ Error - missing cases |
| Open | Any | Yes | Any | ✓ Valid |
| Open | Any | No | `<decides>` | ✓ Valid - unmatched values fail |
| Open | Any | No | Non-`<decides>` | ✗ Error - open enum needs wildcard |

These rules ensure that closed enums provide safety through exhaustiveness while open enums require explicit handling of unknown values.

### Unreachable Case Detection

The compiler actively detects unreachable cases in case expressions, helping you identify dead code and logic errors:

**Duplicate cases** are flagged as unreachable:

<!--versetest
status := enum:
    Active
    Inactive
    Pending

GetStatusCode(S:status):int =
    case (S):
        status.Active => 1
        status.Inactive => 2
        status.Pending => 3
<#
-->
<!-- 17 -->
```verse
status := enum:
    Active
    Inactive
    Pending

# ERROR: Duplicate case is unreachable
GetStatusCode(S:status):int =
    case (S):
        status.Active => 1
        status.Inactive => 2
        status.Pending => 3
        status.Pending => 4  # ERROR: unreachable - already matched above
```
<!-- #> -->

**Cases after wildcards** are always unreachable:

<!--versetest
status := enum:
    Active
    Inactive
    Pending

GetStatusCode(S:status):int =
    case (S):
        status.Active => 1
        _ => 0
<#
-->
<!-- 18 -->
```verse
# ERROR: Case after wildcard
GetStatusCode(S:status):int =
    case (S):
        status.Active => 1
        _ => 0  # Wildcard matches everything
        status.Inactive => 2  # ERROR: unreachable - wildcard already matched
```
<!-- #> -->

These errors prevent logic bugs where you think you're handling specific cases but the code will never execute.

### The `@ignore_unreachable` Attribute

Sometimes you intentionally want unreachable cases—for testing, migration, or defensive programming. The `@ignore_unreachable` attribute suppresses unreachable warnings and errors for specific cases:

<!--NoCompile-->
<!-- 19 -->
```verse
status := enum:
    Active
    Inactive

ProcessStatus(S:status):int =
    case (S):
        status.Active => 1
        status.Inactive => 2
        @ignore_unreachable status.Inactive => 3  # No error
        @ignore_unreachable _ => 0  # No unreachable warning
```

This attribute only affects cases it's applied to. Other unreachable cases without the attribute still produce errors:

<!--versetest
status := enum:
    Active
    Inactive

ProcessStatus(S:status):int =
    case (S):
        status.Active => 1
        status.Inactive => 2
        @ignore_unreachable status.Inactive => 3
<#
-->
<!-- 20 -->
```verse
ProcessStatus(S:status):int =
    case (S):
        status.Active => 1
        status.Inactive => 2
        @ignore_unreachable status.Inactive => 3  # Suppressed
        status.Active => 4  # ERROR: still unreachable without attribute
```
<!-- #> -->

Use `@ignore_unreachable` sparingly, primarily during refactoring or when maintaining multiple code paths for testing purposes.

### Explicit Qualification

Enumerators can collide with identifiers in parent scopes. When this happens, you can use explicit qualification to disambiguate:

<!--NoCompile-->
<!-- 21 -->
```verse
# Top level 'Start'
Start:int = 0

# Enum wants to use 'Start' as enumerator
game_state := enum:
    (game_state:)Start  # Explicit qualification avoids collision
    Playing
    Paused

# Now both are accessible
OuterStart:int = Start             # References the int
StateStart:game_state = game_state.Start  # References the enum value
```

The syntax `(enum_name:)enumerator` explicitly qualifies the enumerator, preventing conflicts with outer-scope symbols.

**Using Reserved Words as Enum Values:**

Qualification also allows you to use reserved words and keywords as enum values, which would otherwise cause errors:

<!--NoCompile-->
<!-- 22 -->
```verse
# Using reserved words as enum values
keyword_enum := enum:
    (keyword_enum:)public    # OK: reserved word qualified
    (keyword_enum:)for       # OK: keyword qualified
    (keyword_enum:)class     # OK: reserved word qualified
    Regular                  # Normal enum value

# Without qualification - errors
# bad_enum := enum:
#    public    # Error: reserved word
#    for       # Error: reserved keyword
```

This is particularly useful when modeling language constructs, access levels, or any domain where reserved words make natural value names.

**Self-Referential Enum Values:**

You can even use the enum's own name as a value when qualified:

<!--NoCompile-->
<!-- 23 -->
```verse
recursive_enum := enum:
    (recursive_enum:)recursive_enum  # OK: qualified with enum name
    OtherValue

# Without qualification - error
# bad_recursive := enum:
  #  bad_recursive  # Error: shadows the type name
```

### Attributes on Enums

Enums support custom attributes, both on the enum type itself and on individual enumerators:

<!-- TODO: this one fails with invalid access of @attribscope_enum. Needs language support. -->
<!--NoCompile-->
<!-- 24 -->
```verse
# Define my_attribute by inheriting from the attribute class
@attribscope_enum
my_attribute := class(attribute):
    MyMetaData:string = "I'm default metadata"
    # category<constructor>(Name:string)<computes> := my_attribute{}

    # Apply to enum and enumerators
@my_attribute{}
game_state := enum:
    @my_attribute{MyMetaData = "Initial"}
    MainMenu

    @my_attribute{MyMetaData = "Active"}
    Playing

    @my_attribute{MyMetaData = "Paused"}
    Paused
```

Attributes must be marked with the appropriate scopes (`@attribscope_enum` for enum types, `@attribscope_enumerator` for individual values) or the compiler will reject them. This provides metadata capabilities for reflection, serialization, or custom tooling.

### Comparison

Enum values are fully comparable, meaning they support both equality (`=`) and inequality (`<>`) operators. This makes them ideal for state tracking and conditional logic:

<!--versetest
weapon_type := enum:
    Sword
    Bow
    Staff

game_state := enum:
    MainMenu
    Playing
    Paused

PlaySwordAnimation()<transacts>:void = {}
OnStateChanged(Prev:game_state, Curr:game_state)<transacts>:void = {}

M()<transacts>:void =
    CurrentWeapon := weapon_type.Sword
    if (CurrentWeapon = weapon_type.Sword):
        PlaySwordAnimation()

    var CurrentState:game_state = game_state.MainMenu
    PreviousState := game_state.Playing
    if (CurrentState <> PreviousState):
        OnStateChanged(PreviousState, CurrentState)
<#
-->
<!-- 25 -->
```verse
CurrentWeapon := weapon_type.Sword
if (CurrentWeapon = weapon_type.Sword):
    PlaySwordAnimation()

PreviousState := game_state.Playing
if (CurrentState <> PreviousState):
    OnStateChanged(PreviousState, CurrentState)
```
<!-- #> -->

Enum values from the same enum type can be compared, while values from different enum types are always unequal:

<!--versetest
letters := enum:
    A, B, C

numbers := enum:
    One, Two, Three

Test()<decides>:letters =
    letters.A = letters.A
    letters.A <> letters.B
    letters.A <> numbers.One
    letters.A
<#
-->
<!-- 26 -->
```verse
letters := enum:
    A, B, C

numbers := enum:
    One, Two, Three

Test()<decides>:letters =
    letters.A = letters.A    # Succeeds - same value
    letters.A <> letters.B   # Succeeds - different values
    letters.A <> numbers.One # Succeeds - different enum types
```
<!-- #> -->

Because enums are comparable, they can be used as map keys, stored in sets, and used with generic functions that require comparable types:

<!--versetest
game_state := enum{
    Menu
    Playing
    Paused
    GameOver
    Debug
    }
-->
<!-- 27 -->
```verse
# Enums as map keys
StateIDs:[game_state]int = map{
    game_state.Menu => 0,
    game_state.Playing => 1,
    game_state.Paused => 2
}

# In generic functions
FindStateID(States:[]game_state, Target:game_state)<decides>:int =
    for (
        State : States, State = Target,
        ID := StateIDs[State]
    ):
        return ID
    false? # fails if state is not found
```
