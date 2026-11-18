# Structs, Enums, and Unions

Structs, enums, and unions are Verse's value types. A struct groups related data with no methods and no inheritance; its fields are public and immutable by default. An enum defines a fixed set of named values, which `case` can match exhaustively. A union defines a set of named variants that can each carry a value, which `case` can match and unpack.

All three are more limited than classes by design. Reach for them when you need data rather than behaviour.

## Structs

Structs provide lightweight data containers without the object-oriented features of classes. They're value types optimized for simple data aggregation, making them perfect for mathematical types, data transfer objects, and any scenario where you need a simple bundle of related values without behavior.

Structs group related data with minimal overhead:

<!-- 01 -->
```verse
damage_type := enum:
    Physical
    Fire

vector2 := struct:
    X : float = 0.0
    Y : float = 0.0

damage_info := struct:
    Amount : int = 0
    Type : damage_type = damage_type.Physical
    IsCritical : logic = false
```

All struct fields are public and immutable by default. Structs cannot have methods, constructors, or participate in inheritance hierarchies. This simplicity makes them efficient and predictable.

### Construction

Creating struct instances uses the same archetype syntax as classes:

<!--versetest
vector2 := struct:
    X : float = 0.0
    Y : float = 0.0
-->
<!-- 02 -->
```verse
Origin := vector2{}                           # every field takes its default
PlayerPos := vector2{X := 100.0, Y := 250.0}

Origin.X = 0.0
PlayerPos.Y = 250.0
```

Since structs are value types, assigning a struct to a variable creates a copy of all its data. This differs from classes, which use reference semantics. The `<computes>` specifier below is what lets the fields of a mutable struct variable be assigned; see the [Mutability](05_mutability.md) chapter for the details.

<!--versetest
position := struct<computes>:
    X : float = 0.0

counter := class:
    var Hits : int = 0
-->
<!-- 03 -->
```verse
var Pos:position = position{X := 100.0}
Snapshot := Pos          # copies the fields
set Pos.X = 0.0
Snapshot.X = 100.0       # the copy kept the old value

Tally := counter{}
Alias := Tally           # binds the same object
set Tally.Hits = 7
Alias.Hits = 7           # the alias sees the change
```

### Comparison

Structs with all comparable fields support equality comparison:

<!--versetest
vector2 := struct:
    X : float = 0.0
    Y : float = 0.0
-->
<!-- 04 -->
```verse
Origin := vector2{}
UnitX := vector2{X := 1.0}

Origin = vector2{}   # succeeds - every field matches
Origin <> UnitX      # succeeds - the X fields differ
```

Comparison happens field by field, succeeding only if all corresponding fields are equal.

### Persistable Structs

Structs can be marked as persistable for use with Verse's persistence system:

<!--versetest
player := class<concrete><unique>{}
-->
<!-- 05 -->
```verse
player_stats := struct<persistable>:
    HighScore : int = 0
    GamesPlayed : int = 0
    WinRate : float = 0.0

# can be used in persistent storage
var PlayerData : weak_map(player, player_stats) = map{}
```

Once published, persistable structs cannot be modified, ensuring data compatibility across game updates.

### Parametric Structs

Like classes, structs can be parametric (generic). A parametric struct declares one or more type parameters, allowing the same struct definition to work with different types. This is useful when you want a lightweight value type that is reusable across different data types without defining a full class.

A parametric struct takes type parameters in its definition, just like a parametric class. The type parameter `t` can be used anywhere a concrete type would appear in field declarations, and when creating instances you provide the concrete type:

<!-- 06 -->
```verse
# a wrapper that can hold a value of any type
wrapper(t:type) := struct:
    Value : t

IntWrapped := wrapper(int){Value := 42}
StringWrapped := wrapper(string){Value := "hello"}

IntWrapped.Value = 42
StringWrapped.Value = "hello"
```

Parametric structs work naturally with parametric functions. A function can accept any instantiation of a parametric struct by using a `where` clause to capture the type parameter. Since the type parameter is preserved through instantiation, parametric structs can also be nested — here a `wrapper` holds another `wrapper` as its value:

<!--versetest
wrapper(t:type) := struct:
    Value : t
-->
<!-- 07 -->
```verse
Unwrap(W:wrapper(t) where t:type):t = W.Value

Unwrap(wrapper(int){Value := 10}) = 10
Unwrap(wrapper(float){Value := 2.0}) = 2.0

Nested := wrapper(wrapper(int)){Value := wrapper(int){Value := 11}}
Unwrap(Unwrap(Nested)) = 11
```

Parametric structs retain all the characteristics of regular structs — they are value types with public, immutable fields and no methods or inheritance. The only addition is the ability to parameterize field types. Note that parametric structs cannot be marked `<persistable>` — persistence requires concrete, fixed types that can be serialized reliably across game updates.

## Enums

Enums define types with a fixed set of named values, perfect for representing states, types, or any concept with a known, finite set of alternatives. They make code more readable by replacing magic numbers with meaningful names and provide compile-time safety by restricting values to the defined set.

An enum lists all possible values for a type:

<!-- 08 -->
```verse
game_state := enum:
    MainMenu
    Playing
    Paused
    GameOver

placeholder := enum{}  # valid but rarely useful
```

Each value in the enum becomes a named constant of that enum type. The compiler ensures that variables of an enum type can only hold one of these defined values. Enums can even be empty, as `placeholder` shows.

Enums introduce both a type and a set of values, and it is crucial to distinguish between them:

<!--versetest
assert_semantic_error(3509):
    status09 := enum:
        Active
        Inactive
    BadAssignment09:status09 = status09
-->
<!-- 09 -->
```verse
status := enum:
    Active
    Inactive

# status is the TYPE; status.Active and status.Inactive are VALUES
var CurrentStatus:status = status.Active
set CurrentStatus = status.Inactive
CurrentStatus = status.Inactive

# BadAssignment:status = status  # ERROR: cannot use a type as a value
# set CurrentStatus = status     # ERROR: cannot use a type as a value
```

You cannot use the enum type where a value is expected. This distinction prevents confusion and ensures type safety. The enum type defines what values are possible, while enum values are the actual constants you use in your code.

### Restrictions

Enums have specific syntactic requirements that keep their usage clear and unambiguous. An enum must be the direct right-hand side of a definition, and that definition must sit at module or class level rather than inside a function:

<!--versetest
assert_semantic_error(3606):
    Result10 := -enum{A, B}
assert_semantic_error(3606, 3547):
    Value10 := enum{X, Y} + 1
assert_semantic_error(3502):
    Process10():void =
        LocalEnum10 := enum{A, B}
-->
<!-- 10 -->
```verse
priority := enum:
    Low
    Medium
    High

# Result := -enum{A, B}    # ERROR: enums cannot appear inside an expression
# Value := enum{X, Y} + 1  # ERROR: same

Rank(P:priority):int =
    # LocalEnum := enum{A, B}  # ERROR: no local enum definitions
    case (P):
        priority.Low => 0
        priority.Medium => 1
        priority.High => 2

Rank(priority.High) = 2
```

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
        game_state.GameOver =>
            if (Input = "Restart"):
                set CurrentState = game_state.MainMenu

ProcessInput("Start")
CurrentState = game_state.Playing
ProcessInput("Pause")
CurrentState = game_state.Paused
```

The `case` expression with enums provides powerful pattern matching with exhaustiveness checking that ensures you handle all possible values correctly.

### Open vs Closed Enums

Enums can be marked as open or closed, fundamentally affecting how they can evolve and how they interact with pattern matching:

<!-- 12 -->
```verse
# closed enum - cannot add values after publication
direction := enum<closed>:  # <closed> is the default
    North
    East
    South
    West

# open enum - can add new values after publication
weapon_type := enum<open>:
    Sword
    Bow
    # Staff, Wand, Dagger, etc. can be added in updates
```

Closed enums, the default, commit to a fixed set of values forever. This allows the compiler to verify that case expressions handle all possibilities exhaustively. Use closed enums for truly fixed sets: days of the week, cardinal directions, fundamental game states.

Open enums allow new values to be added in future versions. This flexibility comes at a cost: case expressions cannot be exhaustive since future values might exist. Use open enums for extensible sets: item types, enemy types, damage types, or any content that may grow.

### Exhaustiveness

The interaction between enum types and case expressions follows sophisticated rules that prevent bugs while enabling both safety and flexibility. Understanding these rules is essential for working with enums effectively.

#### Closed Enums with Full Coverage

When your case expression handles every value in a closed enum, no wildcard is needed. Adding one anyway triggers an unreachable code warning:

<!-- 13 -->
```verse
day := enum:
    Monday
    Tuesday
    Wednesday

# exhaustive - all values covered, so no wildcard is needed
GetDayType(D:day):string =
    case (D):
        day.Monday => "Weekday"
        day.Tuesday => "Weekday"
        day.Wednesday => "Weekday"

GetDayTypeWarn(D:day):string =
    case (D):
        day.Monday => "Weekday"
        day.Tuesday => "Weekday"
        day.Wednesday => "Weekday"
        _ => "Unknown"  # WARNING: unreachable - all values already matched

GetDayType(day.Tuesday) = "Weekday"
```

#### Closed Enums with Partial Coverage

If you do not match all values, you must either provide a wildcard or be in a `<decides>` context:

<!--versetest
day := enum:
    Monday
    Tuesday
    Wednesday
assert_semantic_error(3512):
    day14 := enum:
        Monday
        Tuesday
    GetWeekStart14(D:day14):string =
        case (D):
            day14.Monday => "Week start"
-->
<!-- 14 -->
```verse
# with a wildcard - OK
GetWeekStart(D:day):string =
    case (D):
        day.Monday => "Week start"
        _ => "Mid-week"

# without a wildcard but in a <decides> context - OK
GetWeekStartOrFail(D:day)<transacts><decides>:string =
    case (D):
        day.Monday => "Week start"
        # missing other days causes failure

# GetWeekStartBad(D:day):string =  # ERROR: missing cases and no wildcard
#     case (D):
#         day.Monday => "Week start"

GetWeekStart(day.Tuesday) = "Mid-week"
GetWeekStartOrFail[day.Monday] = "Week start"
not GetWeekStartOrFail[day.Tuesday]
```

#### Open Enums Always Require a Wildcard or `<decides>`

Open enums can have new values added after publication, so they can never be exhaustive.\
This is to ensure backwards compatibility of functions using them (see also [Publishing Functions](06_functions.md#publishing-functions)):

<!--versetest
assert_semantic_error(3512):
    weapon15 := enum<open>:
        Sword
        Bow
    GetClass15(W:weapon15):string =
        case (W):
            weapon15.Sword => "Melee"
            weapon15.Bow => "Ranged"
-->
<!-- 15 -->
```verse
weapon := enum<open>:
    Sword
    Bow

# must have a wildcard - OK
GetWeaponClass(W:weapon):string =
    case (W):
        weapon.Sword => "Melee"
        weapon.Bow => "Ranged"
        _ => "Unknown"  # REQUIRED - future values may exist

# in a <decides> context without a wildcard - OK
GetWeaponClassOrFail(W:weapon)<transacts><decides>:string =
    case (W):
        weapon.Sword => "Melee"
        weapon.Bow => "Ranged"
        # can fail for unknown (future) values

# without either it is a COMPILE ERROR: open enum needs a wildcard or <decides>

GetWeaponClass(weapon.Bow) = "Ranged"
GetWeaponClassOrFail[weapon.Sword] = "Melee"
```

Even if you match all currently defined values in an open enum, you still need a wildcard or `<decides>` context because new values might be added in future versions.

#### Summary of Exhaustiveness Rules

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

The compiler actively detects unreachable cases in case expressions, helping you identify dead code and logic errors. Duplicate cases are flagged as unreachable, and so is any case that follows a wildcard:

<!--versetest
assert_semantic_error(3616):
    status16 := enum:
        Active
        Inactive
        Pending
    GetCode16(S:status16):int =
        case (S):
            status16.Active => 1
            status16.Inactive => 2
            status16.Pending => 3
            status16.Pending => 4
assert_semantic_error(3616):
    other16 := enum:
        Active
        Inactive
    First16(S:other16):int =
        case (S):
            other16.Active => 1
            _ => 0
            other16.Inactive => 2
-->
<!-- 16 -->
```verse
status := enum:
    Active
    Inactive
    Pending

GetStatusCode(S:status):int =
    case (S):
        status.Active => 1
        status.Inactive => 2
        status.Pending => 3
        # status.Pending => 4  # ERROR: unreachable - already matched above

FirstOnly(S:status):int =
    case (S):
        status.Active => 1
        _ => 0                     # the wildcard matches everything
        # status.Inactive => 2  # ERROR: unreachable - the wildcard matched first

GetStatusCode(status.Pending) = 3
FirstOnly(status.Inactive) = 0
```

These errors prevent logic bugs where you think you are handling specific cases but the code will never execute.

### The `@ignore_unreachable` Attribute

Sometimes you intentionally want unreachable cases—for testing, migration, or defensive programming. The `@ignore_unreachable` attribute suppresses unreachable warnings and errors for specific cases. It only affects cases it is applied to; other unreachable cases without the attribute still produce errors:

<!--versetest
status := enum:
    Active
    Inactive
assert_semantic_error(3616):
    status17 := enum:
        Active
        Inactive
    Process17(S:status17):int =
        case (S):
            status17.Active => 1
            status17.Inactive => 2
            @ignore_unreachable status17.Inactive => 3
            status17.Active => 4
-->
<!-- 17 -->
```verse
ProcessStatus(S:status):int =
    case (S):
        status.Active => 1
        status.Inactive => 2
        @ignore_unreachable status.Inactive => 3  # suppressed, no error
        @ignore_unreachable _ => 0                # no unreachable warning
        # status.Active => 4  # ERROR: still unreachable without the attribute

ProcessStatus(status.Inactive) = 2
```

Use `@ignore_unreachable` sparingly, primarily during refactoring or when maintaining multiple code paths for testing purposes.

### Explicit Qualification

Enumerators can collide with identifiers in parent scopes. When this happens, you can use explicit qualification to disambiguate:

<!-- 18 -->
```verse
# top level 'Start'
Start:int = 0

# the enum wants to use 'Start' as an enumerator
game_state := enum:
    (game_state:)Start  # explicit qualification avoids the collision
    Playing
    Paused

# now both are accessible
Start = 0                           # references the int
StateStart:game_state = game_state.Start  # references the enum value
StateStart <> game_state.Playing
```

The syntax `(enum_name:)enumerator` explicitly qualifies the enumerator, preventing conflicts with outer-scope symbols.

Qualification also allows you to use reserved words and keywords as enum values, which would otherwise cause errors, and you can even use the enum's own name as a value when qualified:

<!--versetest
assert_semantic_error(3532):
    bad_enum19 := enum:
        public
        Regular
assert_semantic_error(3532):
    bad_recursive19 := enum:
        bad_recursive19
        OtherValue
-->
<!-- 19 -->
```verse
keyword_enum := enum:
    (keyword_enum:)public        # OK: reserved word qualified
    (keyword_enum:)for           # OK: keyword qualified
    (keyword_enum:)keyword_enum  # OK: qualified with the enum's own name
    Regular                      # normal enum value

# without qualification each of those three is an error

keyword_enum.Regular <> keyword_enum.public
```

This is particularly useful when modeling language constructs, access levels, or any domain where reserved words make natural value names.

### Comparison

Enum values are fully comparable, meaning they support both equality (`=`) and inequality (`<>`) operators. This makes them ideal for state tracking and conditional logic. Enum values from the same enum type can be compared, while values from different enum types are always unequal:

<!--versetest
weapon_type := enum:
    Sword
    Bow

game_state := enum:
    MainMenu
    Playing
    Paused
-->
<!-- 20 -->
```verse
CurrentWeapon := weapon_type.Sword
CurrentWeapon = weapon_type.Sword     # succeeds - same value
CurrentWeapon <> weapon_type.Bow      # succeeds - different values

CurrentState := game_state.Paused
PreviousState := game_state.Playing
CurrentState <> PreviousState

CurrentState <> weapon_type.Sword     # succeeds - different enum types
```

Because enums are comparable, they can be used as map keys, stored in sets, and used with generic functions that require comparable types:

<!--versetest
game_state := enum:
    Menu
    Playing
    Paused
-->
<!-- 21 -->
```verse
# enums as map keys
StateIDs:[game_state]int = map{
    game_state.Menu => 0,
    game_state.Playing => 1,
    game_state.Paused => 2
}

# in generic functions
FindStateID(States:[]game_state, Target:game_state):int =
    for (
        State : States, State = Target,
        ID := StateIDs[State]
    ):
        return ID
    -1 # return -1 if the state is not found

FindStateID(array{game_state.Menu, game_state.Paused}, game_state.Paused) = 2
FindStateID(array{game_state.Menu}, game_state.Playing) = -1
```

## Unions

!!! note "Unreleased Feature"
    Unions have not yet been released and are not publicly available.

A union, also called a discriminated union, tagged union, or sum type, is a value type whose values are exactly one of a set of named *variants*. Each variant can carry a *payload* of its own type, and `case` can match on which variant a value holds, binding its payload as it goes.

If an enum is a list of names, a union is a list of names that can each carry data. Reach for one when a value can take several distinct shapes and each shape needs different data: a result that is either a value or an error, a tree node that is either a leaf or a branch, or an input event that is a key press, a click, or nothing.

A union lists its variants, each with a name and a payload type:

<!-- 22 -->
```verse
shape := union:
    Circle : float                   # the radius
    Rectangle : tuple(float, float)  # width and height
    Empty : void                     # no payload at all
```

Each line inside the union declares a variant as `Name : payload_type`. A variant whose payload is `void` carries no data, which makes it behave like an enum value. A variant that needs several values takes a tuple.

Unions can also be written on one line using braces:

<!-- 23 -->
```verse
outcome := union{Ok : int, Error : string}
```

Unlike struct fields, variants cannot have default values, and they cannot carry their own specifiers. A union must also have at least one variant, and variant names must be unique within it:

<!--versetest
assert_semantic_error(3619):
    empty_union := union{}
assert_semantic_error(3628, 3628):
    dupes_union := union{A : void, A : int, A : string}
assert_semantic_error(3502):
    defaulted_union := union{N : int = 0}
assert_semantic_error(3604):
    specified_union := union{N<public> : int}
assert_semantic_error(3560):
    union{Bare : void}
assert_semantic_error(3606):
    Negated := -union{Empty : void}
assert_semantic_error(3502):
    MakeLocal():void =
        local_union := union{V : void}
assert_semantic_error(3502):
    holder := class:
        inner_union := union{A : void}
assert_semantic_error(3514):
    Self := union{N : int}
assert_semantic_error(3514):
    keyword_union := union{union : int}
-->
<!-- 24 -->
```verse
color := union:
    Named : string
    RGB : tuple(int, int, int)

# empty := union{}                    # ERROR: a union needs at least one variant
# dupes := union{A : void, A : int}   # ERROR: duplicate variant name
# defaulted := union{N : int = 0}     # ERROR: variants cannot have default values
# specified := union{N<public> : int} # ERROR: variants inherit visibility from the union
```

Unions follow the placement rules for enums (see [Restrictions](#restrictions)) with one difference: unlike an enum, a union cannot be defined inside a class either, only at module level. Reserved words such as `Self` cannot be used as union or variant names.

### Union Construction

You create a union value by calling one of its variants with a payload. The variant is always qualified by the union's name:

<!--versetest
shape := union:
    Circle : float
    Rectangle : tuple(float, float)
    Empty : void
assert_semantic_error(3547):
    module_union := union{V : void}
    Inferred := module_union.V()
-->
<!-- 25 -->
```verse
Ball : shape = shape.Circle(2.0)
Door : shape = shape.Rectangle(1.0, 2.0)  # a tuple payload takes its elements as arguments
Nothing : shape = shape.Empty()           # a void payload still needs the parentheses
```

At module scope a union value needs an explicit type, such as `Ball : shape`; inside a function the type can be inferred.

The payload must match the variant's declared type. Passing a value of the wrong type is a compile error:

<!--versetest
assert_semantic_error(3509):
    payload_union := union{N : int}
    Bad : payload_union = payload_union.N("string")
-->
<!-- 26 -->
```verse
id := union:
    Number : int
    Name : string

PlayerID : id = id.Number(42)
# BadID : id = id.Number("Alice")  # ERROR: Number expects an int payload
```

A union has no implicit conversion from its payload types. A plain `int` is not an `id`, even though `id` has an `int` variant; you always name the variant you mean:

<!--versetest
assert_semantic_error(3509):
    count_union := union:
        X : int
    Bad : count_union = 1
-->
<!-- 27 -->
```verse
counter := union:
    Count : int

Five : counter = counter.Count(5)
# NotFive : counter = 5  # ERROR: an int is not a counter
```

This is one place unions differ from enums. `status.Active` is an enum value, but `shape.Empty` without parentheses is not a `shape`: `shape.Empty()` is a `shape`, while `shape.Empty` on its own is a variant constructor (see [First-Class Variant Constructors](#first-class-variant-constructors)).

Like structs, unions are value types: assigning one copies it, and a `var` union variable can be reassigned with `set`.

### Pattern Matching

The `case` expression is how you get data back out of a union. Each *arm* of the `case` (a pattern, `=>`, and an expression) names a variant and describes what to do with its payload. The arm that matches the value's variant runs, with the payload bound to whatever names the pattern introduces:

<!--versetest
shape := union:
    Circle : float
    Rectangle : tuple(float, float)
    Empty : void
-->
<!-- 28 -->
```verse
Area(S:shape):float =
    case (S):
        shape.Circle(Radius : float) => 3.0 * Radius * Radius
        shape.Rectangle(Width : float, Height : float) => Width * Height
        shape.Empty() => 0.0

Area(shape.Circle(1.0)) = 3.0
Area(shape.Rectangle(2.0, 3.0)) = 6.0
Area(shape.Empty()) = 0.0
```

`shape.Circle(Radius : float)` matches any `Circle` and binds its payload to `Radius`. `shape.Empty()` matches the `void` variant, which has nothing to bind. The arm must use parentheses here as well; a bare `shape.Empty` is not a pattern.

#### Pattern Forms

The payload position of an arm accepts several kinds of pattern:

<!--versetest
input_event := union:
    Key : string
    Click : tuple(int, int)
    Idle : void
-->
<!-- 29 -->
```verse
Describe(E:input_event):string =
    case (E):
        input_event.Key("Escape") => "quit"                     # value: matches only this payload
        input_event.Key(Name : string) => "key {Name}"          # binding: matches any Key
        input_event.Click(0, Y : int) => "left edge at {Y}"     # mixed: value and binding together
        input_event.Click(X : int, Y : int) => "click {X},{Y}"  # destructuring a tuple payload
        input_event.Idle() => "idle"

Describe(input_event.Key("Escape")) = "quit"
Describe(input_event.Key("W")) = "key W"
Describe(input_event.Click(0, 7)) = "left edge at 7"
Describe(input_event.Click(3, 4)) = "click 3,4"
```

| Pattern | Example | Matches |
|---------|---------|---------|
| Void | `input_event.Idle()` | The variant, which has no payload |
| Value | `input_event.Key("Escape")` | The variant, only when the payload equals the value |
| Binding | `input_event.Key(Name : string)` | The variant with any payload, binding it to `Name` |
| Destructuring | `input_event.Click(X : int, Y : int)` | The variant with any tuple payload, binding each element |
| Whole-tuple binding | `input_event.Click(Pos : tuple(int, int))` | The variant with any tuple payload, bound as one tuple |
| Mixed | `input_event.Click(0, Y : int)` | The variant, when the value elements match, binding the rest |
| Bind-and-match | `input_event.Key(Name := "W")` | The variant, when the payload equals the value, binding it |

Value patterns are compared with `=`, so any comparable payload works, including structs:

<!--versetest
point := struct:
    X : int
    Y : int
-->
<!-- 30 -->
```verse
marker := union:
    At : point
    Hidden : void

IsOrigin(M:marker):logic =
    case (M):
        marker.At(point{X := 0, Y := 0}) => true
        _ => false

IsOrigin(marker.At(point{X := 0, Y := 0})) = true
IsOrigin(marker.At(point{X := 1, Y := 0})) = false
```

A bind-and-match pattern both checks and binds. `X := 9` only matches a payload equal to `9`, and when it does, `X` holds it. With a type annotation, write the value after the type: `S : string = "Hello"`. A non-matching value falls through to the next arm:

<!--versetest
tagged := union:
    N : int
    SN : tuple(string, int)
-->
<!-- 31 -->
```verse
Classify(T:tagged):int =
    case (T):
        tagged.N(X := 9) => X
        tagged.N(Other : int) => Other + 10
        tagged.SN(S : string = "Hello", Number : int) => Number
        tagged.SN(Rest : tuple(string, int)) => 0

Classify(tagged.N(9)) = 9
Classify(tagged.N(5)) = 15
Classify(tagged.SN("Hello", 3)) = 3
Classify(tagged.SN("Bye", 3)) = 0
```

#### Pattern Rules

The pattern's shape must match the variant's payload type. Binding a `tuple(int, int)` against an `int` payload, a three-element tuple against a two-element one, or anything at all against a `void` payload is a compile error:

<!--versetest
assert_semantic_error(3509):
    shape_a := union{N : int, V : void}
    ReadA(U:shape_a):void =
        case (U):
            shape_a.N(A : int, B : int) =>
            _ =>
assert_semantic_error(3509):
    shape_b := union{V : void}
    ReadB(U:shape_b):void =
        case (U):
            shape_b.V(L : logic) =>
assert_semantic_error(3509):
    shape_c := union{SN : tuple(string, int), V : void}
    ReadC(U:shape_c):void =
        case (U):
            shape_c.SN(S : string, L : logic) =>
            _ =>
-->
<!-- 32 -->
```verse
reading := union:
    Value : int
    Pair : tuple(string, int)
    Missing : void

Read(R:reading):int =
    case (R):
        reading.Value(N : int) => N
        # reading.Value(A : int, B : int) => A  # ERROR: Value's payload is an int, not a tuple
        reading.Pair(Label : string, N : int) => N
        # reading.Pair(S : string, L : logic) => 0  # ERROR: the second element is an int
        reading.Missing() => 0
        # reading.Missing(L : logic) => 0  # ERROR: a void payload binds nothing

Read(reading.Pair("depth", 12)) = 12
```

Each arm introduces its own bindings, so the same name can be reused from arm to arm, even with different types. Within a single arm, each name must be unique, and a binding cannot shadow a definition from an enclosing scope:

<!--versetest
assert_semantic_error(3532):
    twice_union := union{SN : tuple(string, int), N : int}
    BindTwice(U:twice_union):void =
        case (U):
            twice_union.SN(X : string, X : int) =>
            _ =>
assert_semantic_error(3532):
    shadow_union := union{SN : tuple(string, int), N : int}
    Outer : string = "outer"
    Shadow(U:shadow_union):void =
        case (U):
            shadow_union.SN(Outer : string, Number : int) =>
            _ =>
-->
<!-- 33 -->
```verse
value := union:
    I : int
    S : string
    Pair : tuple(string, int)

Title : string = "untitled"

Show(V:value):string =
    case (V):
        value.I(X : int) => "int"
        value.S(X : string) => X  # X is a string in this arm
        value.Pair(X : string, Count : int) => X
        # value.Pair(X : string, X : int) => X          # ERROR: X is bound twice in one arm
        # value.Pair(Title : string, Count : int) => "" # ERROR: Title shadows the definition above

Show(value.S("hi")) = "hi"
```

An arm can only name variants of the union being matched. Enum values and the variants of other unions are not valid patterns:

<!--versetest
assert_semantic_error(3618):
    first_union := union{AN : int}
    second_union := union{BN : int}
    Mismatch(U:first_union):void =
        case (U):
            second_union.BN(X : int) =>
assert_semantic_error(3620, 3618):
    pattern_enum := enum{A, B}
    pattern_union := union{V : void}
    EnumArm(U:pattern_union):void =
        case (U):
            pattern_enum.A =>
            _ =>
-->
<!-- 34 -->
```verse
fruit := union:
    Apple : void
    Banana : void

fruit_enum := enum:
    Apple
    Banana

IsApple(F:fruit):logic =
    case (F):
        fruit.Apple() => true
        # fruit_enum.Apple => true  # ERROR: an enum value is not a fruit variant
        _ => false

IsApple(fruit.Apple()) = true
```

#### Nested Payloads

A variant's payload can itself be a union. A value pattern can reach inside the nested union, but binding inside a nested variant pattern is not yet supported. To bind a nested payload, bind the inner union and use a second `case`:

<!--versetest
assert_semantic_error(3509):
    inner_union := union{N : int, S : string}
    outer_union := union{U : inner_union, V : void}
    NestedBind(W:outer_union):void =
        case (W):
            outer_union.U(inner_union.N(Number : int)) =>
            _ =>
-->
<!-- 35 -->
```verse
inner := union:
    N : int
    S : string

outer := union:
    Wrapped : inner
    Nothing : void

Unwrap(O:outer):int =
    case (O):
        outer.Wrapped(inner.N(0)) => -1             # OK: nested value pattern
        # outer.Wrapped(inner.N(X : int)) => X      # ERROR: nested bindings are not yet supported
        outer.Wrapped(I : inner) =>
            case (I):
                inner.N(X : int) => X
                inner.S(Text : string) => 0
        outer.Nothing() => 0

Unwrap(outer.Wrapped(inner.N(0))) = -1
Unwrap(outer.Wrapped(inner.N(7))) = 7
```

### Open vs Closed Unions

Like enums, unions are `<closed>` by default, and can be marked `<open>` to allow new variants to be added after publication:

<!-- 36 -->
```verse
# closed union - the set of variants is fixed once published
direction := union<closed>:  # <closed> is the default
    Toward : float
    Away : float

# open union - new variants can be added in later versions
pickup := union<open>:
    Coins : int
    Health : float
```

### Union Exhaustiveness

Unions follow the same exhaustiveness rules as enums (see [Exhaustiveness](#exhaustiveness)). A `case` over a closed union must cover every variant, or have a wildcard, or be in a `<decides>` context. A `case` over an open union always needs a wildcard or a `<decides>` context. When every variant of a closed union is covered, a wildcard is unreachable:

<!--versetest
direction := union:
    Toward : float
    Away : float
-->
<!-- 37 -->
```verse
Signed(D:direction):float =
    case (D):
        direction.Toward(Speed : float) => Speed
        direction.Away(Speed : float) => -Speed

SignedWarn(D:direction):float =
    case (D):
        direction.Toward(Speed : float) => Speed
        direction.Away(Speed : float) => -Speed
        _ => 0.0  # WARNING: unreachable - every variant is already matched

Signed(direction.Away(2.0)) = -2.0
```

The one difference from enums is what counts as covering a variant. Only void, binding, whole-tuple binding, and destructuring patterns cover a whole variant. Value, mixed, and bind-and-match patterns only cover some payloads, so a later arm for the same variant is still reachable, and a `case` in which some variant is matched only by these patterns is not exhaustive:

<!--versetest
assert_semantic_error(3512):
    partial_union := union{N : int, V : void}
    Partial(U:partial_union):void =
        case (U):
            partial_union.N(2) =>
            partial_union.V() =>
assert_semantic_error(3512):
    open_union := union<open>{A : int, B : int}
    NoWildcard(U:open_union):void =
        case (U):
            open_union.A(X : int) =>
            open_union.B(X : int) =>
-->
<!-- 38 -->
```verse
score := union:
    Points : int
    Forfeit : void

Label(S:score):string =
    case (S):
        score.Points(0) => "none"
        score.Points(N : int) => "{N} points"  # still needed - Points(0) only covers 0
        score.Forfeit() => "forfeit"

# LabelBad(S:score):string =  # ERROR: missing cases - Points(0) does not cover every Points
#     case (S):
#         score.Points(0) => "none"
#         score.Forfeit() => "forfeit"

Label(score.Points(3)) = "3 points"
```

### Unreachable Arms

The compiler flags arms that can never run. That includes duplicate arms, a second wildcard, and a value pattern that follows a binding pattern for the same variant, since the binding has already matched every payload. As with enums, `@ignore_unreachable` suppresses the error for a repeated arm (see [The `@ignore_unreachable` Attribute](#the-ignore_unreachable-attribute)):

<!--versetest
assert_semantic_error(3616):
    after_binding := union{V : void, S : string, N : int}
    ValueAfter(U:after_binding):void =
        case (U):
            after_binding.S(String : string) =>
            after_binding.S("Hello") =>
            _ =>
assert_semantic_error(3616):
    two_wildcards := union{P : void, Number : int}
    Wildcards(U:two_wildcards):void =
        case (U):
            two_wildcards.P() =>
            _ =>
            _ =>
-->
<!-- 39 -->
```verse
chat_message := union:
    Text : string
    Ping : void

Reply(M:chat_message):string =
    case (M):
        chat_message.Text("hello") => "hi!"   # OK: value before binding
        chat_message.Text(T : string) => T
        # chat_message.Text("bye") => "later" # ERROR: unreachable - Text(T) matched every Text
        chat_message.Ping() => "pong"
        @ignore_unreachable chat_message.Ping() => "again"  # suppressed, no error

Reply(chat_message.Text("hello")) = "hi!"
Reply(chat_message.Text("yo")) = "yo"
```

Put specific value patterns before the general binding pattern for the same variant.

### Recursive Unions

A variant's payload can refer to the union being defined. The compiler does not require a non-recursive variant, but without one no value of the union can ever be built, so give every recursive union at least one:

<!-- 40 -->
```verse
peano := union:
    Zero : void
    Succ : peano

ToInt(N:peano):int =
    case (N):
        peano.Zero() => 0
        peano.Succ(Prev : peano) => ToInt(Prev) + 1

Three : peano = peano.Succ(peano.Succ(peano.Succ(peano.Zero())))
ToInt(Three) = 3
```

The recursion can also go through another type, which makes unions a natural fit for trees and other recursive data:

<!-- 41 -->
```verse
int_tree := union:
    Empty : void
    Leaf : int
    Node : tree_node

tree_node := struct:
    Left : int_tree
    Value : int
    Right : int_tree

Sum(T:int_tree):int =
    case (T):
        int_tree.Empty() => 0
        int_tree.Leaf(Number : int) => Number
        int_tree.Node(N : tree_node) => N.Value + Sum(N.Left) + Sum(N.Right)

OneLeaf : int_tree = int_tree.Leaf(1)
Tree : int_tree = int_tree.Node(tree_node{Left := OneLeaf, Value := 2, Right := int_tree.Empty()})
Sum(Tree) = 3
```

### Union Comparison

A union is comparable when every variant's payload type is comparable. Two values of the same union are equal when they hold the same variant and their payloads are equal:

<!--versetest
shape := union:
    Circle : float
    Rectangle : tuple(float, float)
    Empty : void
-->
<!-- 42 -->
```verse
shape.Circle(1.0) = shape.Circle(1.0)      # succeeds - same variant, same payload
shape.Circle(1.0) <> shape.Circle(2.0)     # succeeds - payloads differ
shape.Empty() = shape.Empty()
```

Variants are distinct even when they share a payload type. Values from different unions are always unequal, even when the unions are defined identically, and a union value is never equal to an enum value:

<!-- 43 -->
```verse
side := union:
    Left : string
    Right : string

other_side := union:
    Left : string
    Right : string

side_enum := enum:
    Left
    Right

side.Left("x") <> side.Right("x")       # succeeds - different variants
side.Left("x") <> other_side.Left("x")  # succeeds - different unions
side.Left("x") <> side_enum.Left        # succeeds - a union value is never an enum value
```

If any variant carries a non-comparable payload, such as a regular class, the whole union is non-comparable. It cannot be compared with `=` or used as a map key:

<!--versetest
assert_semantic_error(3509, 3512):
    plain_class := class{}
    mixed_union := union{N : int, C : plain_class}
    Compared : logic = logic{mixed_union.C(plain_class{}) = mixed_union.N(42)}
-->
<!-- 44 -->
```verse
widget := class{}

slot := union:
    Count : int
    Item : widget

S : slot = slot.Count(1)
# S = slot.Count(1)  # ERROR: slot is not comparable because widget is not
```

Comparable unions can be used wherever a comparable type is required, including map keys and generic functions constrained to `comparable`:

<!--versetest
shape := union:
    Circle : float
    Rectangle : tuple(float, float)
    Empty : void
-->
<!-- 45 -->
```verse
Costs : [shape]int = map{
    shape.Circle(1.0) => 10,
    shape.Empty() => 0
}

Costs[shape.Circle(1.0)] = 10
not Costs[shape.Circle(2.0)]

Same(X:t, Y:t where t:subtype(comparable))<computes><decides>:void = X = Y
Same[shape.Empty(), shape.Empty()]
```

### First-Class Variant Constructors

A variant used without call parentheses is a *variant constructor*: a function that takes the variant's payload and returns a union value. You can store it and call it later, just like a function:

<!-- 46 -->
```verse
id := union:
    Number : int
    Name : string

MakeIDs(Values:[]int):[]id =
    MakeNumber := id.Number    # a function of type int->id
    for (Value : Values):
        MakeNumber(Value)

MakeIDs(array{1, 2}) = array{id.Number(1), id.Number(2)}
```

As with any module-scope definition, a variant constructor bound at module scope needs its type written out:

<!--versetest
id := union:
    Number : int
    Name : string
assert_semantic_error(3547):
    ctor_union := union{S : string}
    MakeS := ctor_union.S
-->
<!-- 47 -->
```verse
# MakeName := id.Name  # ERROR: module-scope definitions need an explicit type
MakeName : type{_(:string):id} = id.Name
MakeName("Alice") = id.Name("Alice")
```

A variant constructor is a function, not a union value. You cannot compare it to a union value or `case` over it; call it first:

<!--versetest
assert_semantic_error(3509):
    make_union := union{N : int}
    CompareCtor()<decides>:void =
        Make := make_union.N
        Make = make_union.N(5)
-->
<!-- 48 -->
```verse
counter := union:
    Count : int

IsSix(Make:int->counter):logic =
    # Make = counter.Count(6)  # ERROR: a variant constructor is not a counter
    case (Make(6)):
        counter.Count(6) => true
        counter.Count(Other : int) => false

IsSix(counter.Count) = true
```

### Variant Qualification

As with enums, variant names can collide with identifiers in an enclosing scope. Qualifying the variant with the union's own name resolves the collision:

<!-- 49 -->
```verse
# top level 'S'
S : string = ""

some_union := union:
    (some_union:)S : string  # explicit qualification avoids the collision
    V : void
    N : int

S = ""                                     # references the string
Value : some_union = some_union.S("hello") # references the variant
```

### Union Specifiers

Unions accept access specifiers, such as `<public>` and `<internal>`, to control their visibility. Variants cannot carry their own access specifiers; they always share the visibility of their union.

Unions also accept the effect specifiers `<computes>` and `<converges>`, but not both at once. As with structs, the effect applies to construction: it becomes the effect of the union's variant constructors (see [Effects on Data Types](13_effects.md#effects-on-data-types)). Unlike structs, unions cannot be `<transacts>`, and like structs they cannot be `<decides>`:

<!--versetest
assert_semantic_error(3593, 3593, 3593):
    owner := module:
        u<internal> := union{N : int}
    other := module:
        Main():void =
            U : owner.u = owner.u.N(1)
assert_semantic_error(3596):
    decides_union := union<decides>{N : int}
assert_semantic_error(3596):
    transacts_union := union<transacts>{N : int}
assert_semantic_error(3565):
    both_union := union<computes><converges>{N : int}
assert_semantic_error(3509):
    weak_union := union<computes>{N : int}
    WrongEffect():void =
        C : type{_(:int)<converges>:weak_union} = weak_union.N
-->
<!-- 50 -->
```verse
pure_value := union<computes>:
    I : int
    F : float

MakeValue():pure_value =
    Make : type{_(:int)<computes>:pure_value} = pure_value.I  # OK: the constructor is <computes>
    Make(1)

# bad := union<decides>{N : int}              # ERROR: unions cannot be <decides>
# both := union<computes><converges>{N : int} # ERROR: pick one effect
```

### Persistable Unions

Unions can be marked `<persistable>` so they can be used in persistent data (see [Persistable Types](17_persistable.md)). Every variant's payload must also be persistable:

<!--versetest
assert_semantic_error(3662):
    plain_class := class:
        Number : int = 4
    saved_union := union<persistable>{V : void, C : plain_class}
    holder := class<persistable><final>:
        U : saved_union = saved_union.V()
-->
<!-- 51 -->
```verse
rank := union<persistable>:
    Unranked : void
    Tier : int

player_record := class<persistable><final>:
    Rank : rank = rank.Unranked()

# bad := union<persistable>{Item : widget}  # ERROR: widget (above) is not persistable
```

### Parametric Unions

Like structs and classes, unions can be parametric. A parametric union declares one or more type parameters that can be used in its variants' payload types:

<!--NoCompile-->
<!-- 52 -->
```verse
maybe(t:type) := union:
    Some : t
    None : void

either(l:type, r:type) := union:
    Left : l
    Right : r
```

Verse's option type `?t` already covers what `maybe` does; it is used here because it is the smallest useful parametric union.

Write the type arguments out, both when constructing a value and in `case` arms:

<!--versetest
maybe(t:type) := union:
    Some : t
    None : void
either(l:type, r:type) := union:
    Left : l
    Right : r
-->
<!--NoCompile-->
<!-- 53 -->
```verse
GetOr(M:maybe(int), Default:int):int =
    case (M):
        maybe(int).Some(X : int) => X
        maybe(int).None() => Default

GetOr(maybe(int).Some(5), 0) = 5
GetOr(maybe(int).None(), 0) = 0

Describe(E:either(int, string)):string =
    case (E):
        either(int, string).Left(N : int) => "number"
        either(int, string).Right(S : string) => S

Describe(either(int, string).Right("text")) = "text"
```

The parametric union is not a type until it is given its type arguments, and it must be given exactly as many as it declares:

<!--versetest
assert_semantic_error(3547):
    bare_maybe(t:type) := union{Some : t, None : void}
    Bare(X:bare_maybe):void = {}
assert_semantic_error(3509):
    extra_maybe(t:type) := union{Some : t, None : void}
    Extra(X:extra_maybe(int, string)):void = {}
assert_semantic_error(3509):
    value_maybe(t:type) := union{Some : t, None : void}
    NotAType(X:value_maybe(5)):void = {}
-->
<!--NoCompile-->
<!-- 54 -->
```verse
maybe(t:type) := union:
    Some : t
    None : void

Count : maybe(int) = maybe(int).Some(1)
# Bare(X:maybe):void = {}                # ERROR: maybe needs a type argument
# Extra(X:maybe(int, string)):void = {}  # ERROR: maybe takes one type argument
# NotAType(X:maybe(5)):void = {}         # ERROR: the argument must be a type
```

Everything else works the same as for regular unions. Parametric unions support every pattern form, follow the same exhaustiveness rules, can be `<open>`, can be recursive, and are comparable (and so usable as map keys) when their payload types are. For example:

<!--versetest
maybe(t:type) := union:
    Some : t
    None : void
-->
<!--NoCompile-->
<!-- 55 -->
```verse
chain(t:type) := union:
    Value : t
    Link : chain(t)
    Empty : void

Depth(C:chain(int)):int =
    case (C):
        chain(int).Link(Inner : chain(int)) => Depth(Inner) + 1
        _ => 0

Twice : chain(int) = chain(int).Link(chain(int).Link(chain(int).Value(9)))
Depth(Twice) = 2

maybe(int).Some(1) = maybe(int).Some(1)
maybe(int).Some(1) <> maybe(int).Some(2)
Lookup : [maybe(int)]string = map{maybe(int).Some(1) => "one", maybe(int).None() => "none"}
Lookup[maybe(int).None()] = "none"
```

Instantiations can be nested, and instantiated variant constructors are first-class like any other: `maybe(string).Some` is a function from `string` to `maybe(string)`:

<!--versetest
maybe(t:type) := union:
    Some : t
    None : void
either(l:type, r:type) := union:
    Left : l
    Right : r
-->
<!--NoCompile-->
<!-- 56 -->
```verse
Deep : maybe(either(int, string)) = maybe(either(int, string)).Some(either(int, string).Left(5))

Greet():maybe(string) =
    MakeSome := maybe(string).Some
    MakeSome("hi")

Greet() = maybe(string).Some("hi")
```

#### Variance

Different instantiations of a parametric union are different types, but one can still be a subtype of another. A type `A` is a subtype of `B` when a value of type `A` can be used anywhere a `B` is expected; `int` is a subtype of `rational`, for example. Whether that carries over to `maybe(int)` and `maybe(rational)` depends on where the variants use the type parameter. The rules are the same as for parametric classes (see [Covariant](10_classes_interfaces.md#covariant), [Contravariant](10_classes_interfaces.md#contravariant), [Invariant](10_classes_interfaces.md#invariant), and [Bivariant](10_classes_interfaces.md#bivariant)).

When the type parameter is used directly as a payload, as in `maybe`, the union is *covariant*: `maybe(int)` is a subtype of `maybe(rational)`. That is safe because every value a `maybe(int)` can hold, a `Some` with an `int` or a `None`, is also a valid `maybe(rational)`. The reverse does not hold:

<!--versetest
assert_semantic_error(3509):
    co_maybe(t:type) := union{Some : t, None : void}
    Narrowed : co_maybe(int) = co_maybe(rational).None()
assert_semantic_error(3509):
    other_maybe(t:type) := union{Some : t, None : void}
    Unrelated : other_maybe(int) = other_maybe(string).Some("hi")
-->
<!--NoCompile-->
<!-- 57 -->
```verse
maybe(t:type) := union:
    Some : t
    None : void

Widened : maybe(rational) = maybe(int).Some(1)       # OK: maybe(int) is a maybe(rational)
# Narrowed : maybe(int) = maybe(rational).None()     # ERROR: not every maybe(rational) is a maybe(int)
# Unrelated : maybe(int) = maybe(string).Some("hi")  # ERROR: string is not an int
```

Variance belongs to the union as a whole, not to individual values: even `maybe(rational).None()`, which carries no `rational`, is not a `maybe(int)`.

When the type parameter is only used as a function parameter inside a payload, the union is *contravariant*, and the direction flips. A function that accepts any `rational` can be called with any `int`, so a `handler(rational)` can be used wherever a `handler(int)` is expected. A function that only accepts `int` could not be given `1/2`, so the reverse fails:

<!--versetest
assert_semantic_error(3509):
    contra_handler(t:type) := union{Handle : t->int}
    IntOnly(P:int):int = 0
    Bad : contra_handler(rational) = contra_handler(int).Handle(IntOnly)
-->
<!--NoCompile-->
<!-- 58 -->
```verse
handler(t:type) := union:
    Handle : t->int

AnyNumber(P:rational):int = 0
IntOnly(P:int):int = P

ForInts : handler(int) = handler(rational).Handle(AnyNumber)  # OK: the direction flips
# ForRationals : handler(rational) = handler(int).Handle(IntOnly)  # ERROR: IntOnly cannot accept every rational
```

When the type parameter is used in both positions, as in `Apply : t->t`, the union is *invariant*: different instantiations are never subtypes of each other. An `int->int` function cannot accept every `rational`, and a `rational->rational` function might return `1/2`, which is not an `int`:

<!--versetest
assert_semantic_error(3509):
    inv_transform(t:type) := union{Apply : t->t}
    Double(P:int):int = P
    Bad : inv_transform(rational) = inv_transform(int).Apply(Double)
assert_semantic_error(3509):
    inv_transform2(t:type) := union{Apply : t->t}
    Same(P:rational):rational = P
    Bad : inv_transform2(int) = inv_transform2(rational).Apply(Same)
-->
<!--NoCompile-->
<!-- 59 -->
```verse
transform(t:type) := union:
    Apply : t->t

Double(P:int):int = P * 2
IntTransform : transform(int) = transform(int).Apply(Double)
# Wider : transform(rational) = IntTransform  # ERROR: invariant - no subtyping either way
```

A type parameter that no variant uses makes the union *bivariant*: every instantiation holds exactly the same values, so any instantiation can be used as any other. Compare `marker` with `maybe`. `maybe` uses `t` in `Some`, so the whole union, including its `None`, is covariant. `marker` never uses `t` at all:

<!--NoCompile-->
<!-- 60 -->
```verse
marker(t:type) := union:
    Flag : void

Flagged : marker(int) = marker(string).Flag()  # OK: no variant uses t
```

#### Mixing Instantiations

Variance also decides the type of an `if` or an array that mixes instantiations. For a covariant union, the result is the narrowest instantiation both fit into: `maybe(int)` and `maybe(rational)` give `maybe(rational)`. Likewise, both `maybe(int)` and `maybe(string)` values fit in a `[]maybe(comparable)`. For a contravariant union the direction flips: `handler(int)` and `handler(rational)` give `handler(int)`. Different instantiations of an invariant union have no common instantiation, since neither is a subtype of the other:

<!--versetest
maybe(t:type) := union:
    Some : t
    None : void
assert_semantic_error(3509):
    mix_maybe(t:type) := union{Some : t, None : void}
    Mixed : []mix_maybe(int) = array{mix_maybe(int).Some(1), mix_maybe(string).Some("hi")}
-->
<!--NoCompile-->
<!-- 61 -->
```verse
Pick(Z:logic):maybe(rational) =
    if (Z?) then maybe(int).Some(3) else maybe(rational).None()

Values : []maybe(comparable) = array{maybe(int).Some(1), maybe(string).Some("hi")}
# Ints : []maybe(int) = array{maybe(int).Some(1), maybe(string).Some("hi")}  # ERROR: a string is not an int

IsThree(M:maybe(rational)):logic =
    case (M):
        maybe(rational).Some(X : rational) => logic{X = 3}
        maybe(rational).None() => false

IsThree(Pick(true)) = true
```

#### Matching Instantiations

A `case` arm may name a *wider* instantiation than the value's type. Every `maybe(int)` is also a `maybe(any)`, so a `maybe(any).Some` arm applies to every `Some`, and the arms still count toward exhaustiveness. This is handy when the arms only care which variant they see, as in `IsSet` below.

An arm may not name a *narrower* instantiation. If `M` is a `maybe(comparable)`, its `Some` might hold an `int` or a `string`, and deciding whether a `maybe(int).Some` arm applies would mean checking the payload's type at run time, which `case` does not do. For the same reason, a binding must accept the payload's whole type, and an arm cannot name an unrelated instantiation:

<!--versetest
maybe(t:type) := union:
    Some : t
    None : void
assert_semantic_error(3618):
    narrow_maybe(t:type) := union{Some : t, None : void}
    Narrow(U:narrow_maybe(comparable)):void =
        case (U):
            narrow_maybe(int).Some(N : int) =>
            narrow_maybe(int).None() =>
assert_semantic_error(3509):
    bind_maybe(t:type) := union{Some : t, None : void}
    BindNarrow(U:bind_maybe(comparable)):void =
        case (U):
            bind_maybe(comparable).Some(N : int) =>
            bind_maybe(comparable).None() =>
assert_semantic_error(3618):
    wrong_maybe(t:type) := union{Some : t, None : void}
    Wrong(U:wrong_maybe(int)):void =
        case (U):
            wrong_maybe(string).Some(S : string) =>
            wrong_maybe(string).None() =>
-->
<!--NoCompile-->
<!-- 62 -->
```verse
IsSet(M:maybe(int)):logic =
    case (M):
        maybe(any).Some(X : any) => true    # OK: wider instantiation, still exhaustive
        # maybe(string).Some(S : string) => true  # ERROR: maybe(string) is unrelated to maybe(int)
        maybe(any).None() => false

Narrow(M:maybe(comparable)):int =
    case (M):
        # maybe(int).Some(N : int) => N            # ERROR: narrower than maybe(comparable)
        # maybe(comparable).Some(N : int) => N     # ERROR: the payload may not be an int
        maybe(comparable).Some(X : comparable) => 1
        maybe(comparable).None() => 0

IsSet(maybe(int).Some(5)) = true
```

#### Overloading

The compiler must be able to choose exactly one overload for any argument, so two overloads that take different instantiations of the same parametric union are only allowed if no value could belong to both. With `just`, whose only variant is `Some : t`, `just(int)` and `just(string)` have no values in common, but every `int` is also a `rational`, so `just(int)` and `just(rational)` overlap:

<!--versetest
assert_semantic_error(3532):
    one_of(t:type) := union{Some : t}
    Use(X:one_of(int)):void = {}
    Use(X:one_of(rational)):void = {}
assert_semantic_error(3532):
    opt(t:type) := union{Some : t, None : void}
    Use(X:opt(int)):void = {}
    Use(X:opt(string)):void = {}
-->
<!--NoCompile-->
<!-- 63 -->
```verse
just(t:type) := union:
    Some : t

Describe(X:just(int)):string = "int"
Describe(X:just(string)):string = "string"   # OK: no value is both

# Describe(X:just(rational)):string = "rational"  # ERROR: overlaps just(int), since every int is a rational

Describe(just(string).Some("a")) = "string"
```

`maybe(int)` and `maybe(string)` cannot be overloaded, even though `int` and `string` don't overlap. `None` doesn't use `t`, so it belongs to every instantiation, and both parameter types contain it. This is about which values the types share; statically, `maybe(rational).None()` is still not a `maybe(int)`, as shown under [Variance](#variance). Different unions never overlap, even when they have the same shape.

#### Specifiers and Restrictions

Specifiers on a parametric union apply to every instantiation: access specifiers, `<open>` and `<closed>`, and effect specifiers alike:

<!--versetest
assert_semantic_error(3593, 3593, 3593):
    owner := module:
        box<internal>(t:type) := union{Some : t, None : void}
    other := module:
        Main():void =
            U : owner.box(int) = owner.box(int).Some(1)
assert_semantic_error(3512):
    open_box(t:type) := union<open>{Some : t, None : void}
    Covered(U:open_box(int)):void =
        case (U):
            open_box(int).Some(X : int) =>
            open_box(int).None() =>
-->
<!--NoCompile-->
<!-- 64 -->
```verse
library := module:
    box<public>(t:type) := union<computes>:
        Some : t
        None : void

    open_box<public>(t:type) := union<open>:
        Some : t
        None : void

    Get(B:open_box(int)):int =
        case (B):
            open_box(int).Some(X : int) => X
            _ => 0      # REQUIRED - open in every instantiation

    MakeBox():box(int) =
        Make : type{_(:int)<computes>:box(int)} = box(int).Some  # has the union's <computes> effect
        Make(1)

user := module:
    MakeFull():library.box(int) = library.box(int).Some(1)
```

Parametric unions follow the same placement rules as regular unions, so they cannot be defined locally either. Like parametric structs, they cannot be marked `<persistable>`, because persistence requires concrete, fixed types:

<!--versetest
assert_semantic_error(3502):
    saved(t:type) := union<persistable>:
        Count : int
        Nothing : void
assert_semantic_error(3502):
    MakeLocal():void =
        local_maybe(t:type) := union{Some : t, None : void}
-->
<!--NoCompile-->
<!-- 65 -->
```verse
# saved(t:type) := union<persistable>:  # ERROR: parametric unions cannot be persistable
#     Count : int
#     Nothing : void
```

### Union Evolution

Once a union is published, its definition becomes a contract with code that depends on it. The rules follow those for enums (see [Code Evolution](18_evolution.md#enums)): a closed union's variants are fixed, in number and in order, while an open union may gain variants and reorder them:

| Change | Closed union | Open union |
|--------|--------------|------------|
| Add a variant | ✗ Not allowed (could break exhaustive `case` expressions) | ✓ Allowed |
| Remove a variant | ✗ Not allowed | ✗ Not allowed |
| Rename a variant | ✗ Not allowed (a removal plus an addition) | ✗ Not allowed (a removal plus an addition) |
| Reorder variants | ✗ Not allowed | ✓ Allowed |
| Change a variant's payload type | ✗ Not allowed | ⚠ Currently accepted by the compiler - avoid |
| Change `<closed>` to `<open>` | ✗ Not allowed | — |
| Change `<open>` to `<closed>` | — | ✓ Allowed |

The compiler currently accepts a changed payload type on an open union, but the change breaks existing code all the same: a `case` arm such as `A(X : int)` no longer matches once `A` carries a `string`, and persisted values of the old type no longer fit. Treat payload types as fixed for open unions too.

Compatibility checking does not yet handle parametric unions (even an unchanged parametric union is currently reported as incompatible), so the table describes non-parametric unions only.

Use closed unions when the set of shapes is inherently fixed, like `maybe` or a binary tree. Use open unions for sets that will grow, like event or message types, and accept that every `case` over them needs a fallback.
