# Operators

Operators are functions that perform actions on their operands. They provide concise syntax for common operations like arithmetic, comparison, logical operations, and assignment.

## Operator Formats

Verse operators come in three formats based on their position relative to their operands:

**Prefix Operators**

Prefix operators appear before their single operand:

- `not Expression` - Logical negation
- `-Value` - Numeric negation
- `+Value` - Numeric positive (for alignment)

**Infix Operators**

Infix operators appear between their two operands:

- `A + B` - Addition
- `A * B` - Multiplication
- `A = B` - Equality comparison
- `A and B` - Logical AND

**Postfix Operators**

Postfix operators appear after their single operand:

- `Value?` - Query operator for logic values

## Precedence

When multiple operators appear in the same expression, they are evaluated according to their precedence level. Higher precedence operators are evaluated first. Operators with the same precedence are evaluated left to right (except for assignment and unary operators which are right-associative).

The precedence levels from highest to lowest are:

| Precedence | Operators | Category | Format | Associativity | Example |
|------------|-----------|----------|--------|---------------|--|
| 11 | `.`, `[]`, `()`, `{}`, `?` (postfix) | Member access, Indexing, Call, Construction, Query | Postfix | Left | `BossDefeated?`, `Player.Respawn()`|
| 10 | `+`, `-` (unary), `not` | Unary operations | Prefix | Right | `+Score`, `-Distance`, `not HasCooldown?` |
| 9 | `*`, `/` | Multiplication, Division | Infix | Left | `Score * Multiplier` |
| 8 | `+`, `-` (binary) | Addition, Subtraction | Infix | Left | `X + Y`, `Health - Damage` |
| 7 | `=` (relational), `<>`, `<`, `<=`, `>`, `>=` | Relational comparison | Infix | Right | `Player <> Target`, `Score > 100` |
| 5 | `and` | Logical AND | Infix | Left | `HasPotion? and TryUsePotion[]` |
| 4 | `or` | Logical OR | Infix | Left | `IsAlive? or Respawn()` |
| 3 | `..` | Range | Infix | Left | `0..100`, `-15..50` |
| 2 | ~~Lambda expressions~~ | ~~Function literals~~ (not yet supported) | Special | N/A | N/A |
| 1 | `:=`, `set =` | Assignment | Infix | Right | `X := 15`, `set Y = 25` |

## Arithmetic Operators

Arithmetic operators perform mathematical operations on numeric values. They work with both `int` and `float` types, with some special behaviors for type conversion and integer division.

### Basic Arithmetic

| Operator | Operation | Types | Notes |
|----------|-----------|-------|-------|
| `+` | Addition | `int`, `float` | Also concatenates strings and arrays |
| `-` | Subtraction | `int`, `float` | Can be used as unary negation |
| `*` | Multiplication | `int`, `float` | Converts `int` to `float` when mixed |
| `/` | Division | `int` (failable), `float` | Integer division returns `rational` |

<!--versetest-->
<!-- 01 -->
```verse
# Basic arithmetic
Sum := 10 + 20      # 30
Diff := 50 - 15     # 35
Prod := 6 * 7       # 42
Quot := 20.0 / 4.0  # 5.0

# Unary operators
Negative := -42     # -42
Positive := +42     # 42 (for alignment)

# Integer division (failable, returns rational)
if (Result := 10 / 3):
    IntResult := Floor(Result)  # 3

# Type conversion through multiplication
IntValue:int = 42
FloatValue:float = IntValue * 1.0  # Converts to 42.0
```

### Compound Assignments

Compound assignment operators combine an arithmetic operation with assignment:

| Operator | Equivalent To | Types |
|----------|---------------|-------|
| `set +=` | `set X = X + Y` | `int`, `float`, `string`, `array` |
| `set -=` | `set X = X - Y` | `int`, `float` |
| `set *=` | `set X = X * Y` | `int`, `float` |
| `set /=` | `set X = X / Y` | `float` only |

<!--versetest-->
<!-- 02 -->
```verse
var Score:int = 100
set Score += 50    # Score is now 150
set Score -= 25    # Score is now 125
set Score *= 2     # Score is now 250

var Health:float = 100.0
set Health /= 2.0  # Health is now 50.0

# Note: set /= doesn't work with integers due to failable division
# var IntValue:int = 10
# set IntValue /= 2  # Compile error!
```

## Comparison Operators

Comparison operators test relationships between values and are failable expressions that succeed or fail based on the comparison result.

### Relational Operators

| Operator | Meaning | Supported Types | Example |
|----------|---------|-----------------|---------|
| `<` | Less than | `int`, `float` | `Score < 100` |
| `<=` | Less than or equal | `int`, `float` | `Health <= 0.0` |
| `>` | Greater than | `int`, `float` | `Level > 5` |
| `>=` | Greater than or equal | `int`, `float` | `Time >= MaxTime` |

### Equality Operators

| Operator | Meaning | Supported Types | Example |
|----------|---------|-----------------|---------|
| `=` | Equal to | All comparable types | `Name = "Player1"` |
| `<>` | Not equal | All comparable types | `State <> idle` |

<!--versetest
HandlePlayerDeath():void={}
EnableAdminMode():void={}
ShowMenu():void={}
UnlockAchievement():void={}
GameState := enum{Playing, Paused}
Score:int = 1500
HighScore:int = 1000
Health:float = 0.0
PlayerName:string = "Admin"
CurrentState:GameState = GameState.Paused
Level:int = 15
-->
<!-- 03 -->
```verse
# Numeric comparisons
if (Score > HighScore):
    Print("New high score!")

if (Health <= 0.0):
    HandlePlayerDeath()

# Example with other comparable types
if (PlayerName = "Admin"):
    EnableAdminMode()

if (CurrentState <> GameState.Playing):
    ShowMenu()

# Comparison in complex expressions
if (Level >= 10 and Score > 1000):
    UnlockAchievement()
```

The following types support equality comparison operations (`=` and `<>`):

- Numeric types: `int`, `float`, `rational`
- Boolean: `logic`
- Text: `string`, `char`, `char32`
- Enumerations: All `enum` types
- Collections: `array`, `map`, `tuple`, `option` (if elements are comparable)
- Structs: If all fields are comparable
- Unique classes: Classes marked with `<unique>` (identity equality only)

Comparisons between different types generally fail:

<!--versetest
assert:
    not (0 = 0.0)  # Fails: int vs float
    not ("5" = 5)  # Fails: string vs int
<#
-->
<!-- 04 -->
```verse
0 = 0.0  # Fails: int vs float
"5" = 5  # Fails: string vs int
```
<!-- #> -->

## Logical Operators

Logical operators work with failable expressions and control the flow of success and failure.

### Query Operator (`?`)

The query operator checks if a `logic` value is `true` (see [Failure](08_failure.md#failable-expressions) for how `?` works with other types):

<!--versetest
StartGame():void={}
-->
<!-- 05 -->
```verse
var IsReady:logic = true

if (IsReady?):
    StartGame()

# Equivalent to:
if (IsReady = true):
    StartGame()
```

### Not Operator

The `not` operator negates the success or failure of an expression:

<!--versetest
ContinuePlaying()<computes>:void={}
-->
<!-- 06 -->
```verse
if (not IsGameOver?):
    ContinuePlaying()

# Effects are not committed with not
var X:int = 0
if (not (set X = 5, IsGameOver?)):
    # X is still 0 here, even though the assignment "tried" to happen
    Print("X is {X}")  # Prints "X is 0"
```

### And Operator

The `and` operator succeeds only if both operands succeed:

<!--versetest
EnterRoom()<computes>:void={}
AllowQuestAccess()<computes>:void={}
HasKey:?int = option{1}
DoorUnlocked:?int = option{1}
player := class{Level:int = 10, HasItem:logic = true}
Player:player = player{}
-->
<!-- 07 -->
```verse
if (HasKey? and DoorUnlocked?):
    EnterRoom()

# Both expressions must succeed
if (Player.Level > 5 and Player.HasItem?):
    AllowQuestAccess()
```

### Or Operator

The `or` operator succeeds if at least one operand succeeds:

<!--versetest
OpenDoor()<computes>:void={}
ProcessResult()<computes>:void={}
HasKeyCard:?int = false
HasMasterKey:?int = option{1}
QuickCheck()<computes><decides>:void = {}
ExpensiveCheck()<computes><decides>:void = {}
-->
<!-- 08 -->
```verse
if (HasKeyCard? or HasMasterKey?):
    OpenDoor()

# Short-circuit evaluation - second operand not evaluated if first succeeds
if (QuickCheck[] or ExpensiveCheck[]):
    ProcessResult()
```

### Truth Table

Consider two expressions `P` and `Q` which may either succeed or fail, the following table shows the result of logical operators applied to them:

| Expression P | Expression Q | P and Q | P or Q | not P |
|--------------|--------------|---------|---------|-------|
| Succeeds | Succeeds | Succeeds (Q's value) | Succeeds (P's value) | Fails |
| Succeeds | Fails | Fails | Succeeds (P's value) | Fails |
| Fails | Succeeds | Fails | Succeeds (Q's value) | Succeeds |
| Fails | Fails | Fails | Fails | Succeeds |

## Assignment and Initialization

The `:=` operator initializes constants and variables:

<!--versetest-->
<!-- 09 -->
```verse
# Constant initialization (immutable)
MaxHealth:int = 100
PlayerName:string = "Hero"

# Variable initialization (mutable)
var CurrentHealth:int = 100
var Score:int = 0

# Type inference
AutoTyped := 42  # Inferred as int
```

The `set =` operator updates variable values:

<!--verse
vector3:=struct{X:float, Y:float, Z:float}
-->
<!-- 10 -->
```verse
var Points:int = 0
set Points = 100

var Position:vector3 = vector3{X := 0.0, Y := 0.0, Z := 0.0}
set Position = vector3{X := 10.0, Y := 20.0, Z := 0.0}
```

## Special Operators

### Indexing

The square bracket operator is used for multiple purposes in Verse:

1. **Array/Map indexing** - Access elements in collections
2. **Function calls** - Call functions which may fail
3. **Computed member access** - Access object members dynamically

<!--verse
MyFunction1(X:int, Y:int)<decides>:void={}
MyFunction2(?X:int=0, ?Y:int=0)<decides>:void={}
F(Arg1:int,Arg2:int)<decides>:void=
-->
<!-- 11 -->
```verse
# Array indexing (failable)
MyArray := array{10, 20, 30}
if (Element := MyArray[1]):
    Print("Element at index 1: {Element}")  # Prints 20

# Map lookup (failable)
Scores:[string]int = map{"Alice" => 100, "Bob" => 85}
if (AliceScore := Scores["Alice"]):
    Print("Alice's score: {AliceScore}")

# String indexing (failable)
Name:string = "Verse"
if (FirstChar := Name[0]):
    Print("First character: {FirstChar}")  # Prints 'V'

# Function call that can fail
Result1 := MyFunction1[Arg1, Arg2]          # Can fail
Result2 := MyFunction2[?X:=Arg1, ?Y:=Arg2]  # Named arguments
EmptyCall := MyFunction2[]                  # and optional values
```

### Member Access

The dot operator accesses fields and methods of objects:

<!--versetest
player := class{Health:float = 100.0, GetName()<computes>:string = "Hero"}
vector3 := struct{X:float, Y:float, Z:float}
config_settings := struct{MaxPlayers:int = 10}
config := struct{Settings:config_settings = config_settings{}}
object_type := class{
    FirstMethod()<transacts>:object_type = object_type{}
    SecondMethod()<computes>:void = {}
}
Player:player = player{}
MyVector:vector3 = vector3{X:=1.0, Y:=2.0, Z:=3.0}
Config:config = config{}
MyObject:object_type = object_type{}
-->
<!-- 12 -->
```verse
Player.Health
Player.GetName()
MyVector.X
Config.Settings.MaxPlayers

# Line continuation supported after dot
LongExpression := MyObject.FirstMethod().
                           SecondMethod()
```

### Range

The range operator creates ranges for iteration:

<!--versetest-->
<!-- 13 -->
```verse
# Inclusive range
for (I := 0..4):
    Print("{I}")  # Prints 0, 1, 2, 3, 4
```

### Object Construction

Curly braces are used to construct objects when placed after a type:

<!--versetest
point:=struct{X:int, Y:int}
player_data:=struct{Name:string,Level:int,Health:float}
game_config:=struct{MaxPlayers:int,EnablePvP:logic}
-->
<!-- 14 -->
```verse
# Object construction with type name
Point := point{X:= 10, Y:= 20}

# Fields can be separated by commas or newlines
Player := player_data {
    Name := "Hero"
    Level := 5
    Health := 100.0
}

# Trailing commas are not allowed
Config := game_config{
    MaxPlayers := 100,
    EnablePvP := true # ,  -- comma not allowed here
}
```

### Tuple Access

Round braces when used with a single argument after a tuple expression, accesses tuple elements:

<!--versetest-->
<!-- 15 -->
```verse
MyTuple := (10, 20, 30)
FirstElement := MyTuple(0)  # Access first element
SecondElement := MyTuple(1)  # Access second element
```

## Type Conversions

Verse has limited implicit type conversion. Most conversions must be explicit:

<!--versetest-->
<!-- 16 -->
```verse
# No implicit int to float conversion
MyInt:int = 42
# MyFloat:float = MyInt  # Error!
MyFloat:float = MyInt * 1.0  # OK: explicit conversion

# No implicit numeric to string conversion
Score:int = 100
# Message:string = "Score: " + Score  # Error!
Message:string = "Score: {Score}"  # OK: string interpolation
```

When operators work with mixed types, specific rules apply:

<!--versetest-->
<!-- 17 -->
```verse
# int * float -> float
Result := 5 * 2.0  # Result is 10.0 (float)

# Comparisons must be same type
if (5 = 5):     # OK
if (5.0 = 5.0): # OK
# if (5 = 5.0):   # Error: different types
```
