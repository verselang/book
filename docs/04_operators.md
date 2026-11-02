# Operators

Operators are functions that perform actions on their operands. They provide concise syntax for common operations like arithmetic, comparison, logical operations, and assignment.

## Operator Formats

Verse operators come in three formats, distinguished by their position relative to their operands.

#### Prefix Operators

Prefix operators appear before their single operand:

- `not Expression` - Logical negation
- `-Value` - Numeric negation
- `+Value` - Numeric positive (for alignment)

#### Infix Operators

Infix operators appear between their two operands:

- `A + B` - Addition
- `A * B` - Multiplication
- `A = B` - Equality comparison
- `A and B` - Logical AND

#### Postfix Operators

Postfix operators bind to the expression on their left. While some (like `.`) appear between two elements, they are classified as postfix because they operate on the left-hand expression:

- `Value?` - Query operator for logic values
- `Object.Member` - Member access (the `.` operates on the object to its left)
- `Array[Index]` - Array indexing (the `[]` operates on the array to its left)
- `Function()` - Function call (the `()` operates on the function to its left)
- `Constructor{}` - Object construction (the `{}` operates on the type to its left)

Although `.` appears *between* `Player` and `Respawn` in `Player.Respawn()`, it is considered postfix because it binds to `Player` and selects a member from it. The right side (`Respawn`) is not a separate operand but a member selector.

## Precedence

When multiple operators appear in the same expression, Verse evaluates them according to their precedence level. Higher precedence operators evaluate first. Operators with the same precedence evaluate left to right (except for assignment and unary operators which are right-associative).

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

The `=` symbol serves two distinct purposes in Verse:
- **Relational comparison** (precedence 7): When used as an operator in expressions, `A = B` tests equality and returns a logic value
- **Assignment** (precedence 1): When used with the `set` keyword, `set X = Value` assigns a new value to an existing variable

This is different from `:=`, which always means "define and initialize" for new variables. The context determines which meaning of `=` applies.

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
10 + 20 = 30
50 - 15 = 35
6 * 7 = 42
20.0 / 4.0 = 5.0

# Unary operators
Delta := 5 - 12
-Delta = 7    # negation
+Delta = -7   # unary plus, purely for alignment

# Integer division is failable and yields a rational
9 / 3 = 3         # a rational compares equal to an int
Floor(10 / 3) = 3
not (10 / 0 = 0)  # division by zero fails rather than erroring
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
set Score += 50
Score = 150
set Score -= 25
Score = 125
set Score *= 2
Score = 250

var Health:float = 100.0
set Health /= 2.0
Health = 50.0

# Arrays can use += with both arrays and tuples
var Items:[]int = array{1, 2, 3}
set Items += array{4, 5}
set Items += (6, 7)
Items = array{1, 2, 3, 4, 5, 6, 7}

# set /= does not work with integers, because integer division is failable
# var Count:int = 10
# set Count /= 2  # Compile error!
```

### Bitwise Operations

Verse provides bitwise operations for integers through four intrinsic
functions: `BitAnd`, `BitOr`, `BitXor`, and `BitNot`. These operate on
the two's complement binary representation of integers.

<!--versetest-->
<!-- 03 -->
```verse
# Bitwise AND - sets a bit only if both inputs have it set
BitAnd(12, 10) = 8      # 1100 & 1010 = 1000
BitAnd(-1, 42) = 42     # -1 has all bits set, so it acts as the identity

# Bitwise OR - sets a bit if either input has it set
BitOr(12, 10) = 14      # 1100 | 1010 = 1110
BitOr(-1, 42) = -1      # -1 absorbs everything

# Bitwise XOR - sets a bit if the inputs differ
BitXor(12, 10) = 6      # 1100 ^ 1010 = 0110
BitXor(42, 42) = 0      # same values cancel out

# Bitwise NOT - inverts all bits: BitNot(X) = -X - 1
BitNot(0) = -1
BitNot(12) = -13        # -(12 + 1)
```

Bitwise operations work only with the `int` type, not `float` or
`rational`. They follow two's complement arithmetic, where negative
numbers are represented with the sign bit set and remaining bits
inverted plus one.

Common patterns using bitwise operations:

<!--versetest-->
<!-- 04 -->
```verse
# Check if a bit is set (test bit at position N)
Flags := 10                         # 10 = binary 1010: bits 1 and 3 set
BitAnd(Flags, 2) = 2                # Bit 1 is set (2 = binary 0010)
BitAnd(Flags, 4) = 0                # Bit 2 is clear (4 = binary 0100)

# Set a bit
BitOr(Flags, 1) = 11                # 1011: bit 0 turned on

# Clear a bit
BitAnd(Flags, BitNot(8)) = 2        # 0010: bit 3 turned off

# Toggle a bit
BitXor(Flags, 2) = 8                # 1000: bit 1 was set, so it flipped off

# Test even/odd (check if the lowest bit is set)
BitAnd(Flags, 1) = 0                # even (lowest bit clear)
```

De Morgan's laws apply to bitwise operations:

<!--versetest-->
<!-- 05 -->
```verse
# NOT(A AND B) = (NOT A) OR (NOT B)
BitNot(BitAnd(15, 9)) = BitOr(BitNot(15), BitNot(9))

# NOT(A OR B) = (NOT A) AND (NOT B)
BitNot(BitOr(15, 9)) = BitAnd(BitNot(15), BitNot(9))
```

On the Verse VM, bitwise operations support arbitrarily large integers
(bignums beyond 2^64). On the Blueprint VM, values must fit within the
64-bit signed integer range (-2^63 to 2^63-1).

### Bit Shift Operations

Verse provides bit shifts for integers through two functions:
`BitShiftLeft` and `BitShiftRight`. Each takes a value and a shift
count, and operates on the two's complement binary representation of
the value. Unlike the bitwise operations, the shifts are failable: they
fail when the shift count is negative, so they are called with square
brackets.

<!--versetest-->
<!-- 06 -->
```verse
# Shift left - moves bits toward the high end, filling with zeros
BitShiftLeft[1, 10] = 1024      # 1 << 10 = 10000000000
BitShiftLeft[3, 5] = 96         # 11 << 5 = 1100000
BitShiftLeft[1, 0] = 1          # a count of 0 leaves the value unchanged

# Shift right - moves bits toward the low end, dropping the bits shifted out
BitShiftRight[1024, 10] = 1
BitShiftRight[96, 5] = 3        # 1100000 >> 5 = 11
BitShiftRight[1, 1] = 0         # the only set bit is shifted out
```

Shifting left by `N` multiplies by 2^N, and shifting right by `N`
divides by 2^N, rounding down:

<!--versetest-->
<!-- 07 -->
```verse
BitShiftLeft[12345, 8] = 12345 * 256
BitShiftRight[12345, 3] = 1543  # 12345 / 8 = 1543.125, rounded down
```

Both shifts are arithmetic: they preserve the sign of the value. A
negative value shifted left is still `X * 2^N`. A negative value
shifted right rounds toward negative infinity, not toward zero:

<!--versetest-->
<!-- 08 -->
```verse
BitShiftLeft[-5, 2] = -20       # -5 * 4
BitShiftRight[-96, 5] = -3      # -96 / 32 = -3 exactly
BitShiftRight[-97, 5] = -4      # -97 / 32 = -3.03..., rounded down to -4
BitShiftRight[-1, 1] = -1       # -1 has all bits set, so it stays -1

# Shifting right undoes shifting left
BitShiftRight[BitShiftLeft[-12345, 8], 8] = -12345
```

Shifting right by a count at least as wide as the value shifts out
every bit, leaving only the sign: `0` for non-negative values and `-1`
for negative ones. The count can be arbitrarily large:

<!--versetest-->
<!-- 09 -->
```verse
BitShiftRight[12345, 1000] = 0
BitShiftRight[-12345, 1000] = -1
BitShiftLeft[0, 1000000000] = 0 # zero stays zero, however far it shifts
```

A negative shift count fails, for both shifts. The value itself may be
negative; only the count must be non-negative. Like any failable
expression, a shift can supply a fallback with `or`:

<!--versetest-->
<!-- 10 -->
```verse
not BitShiftLeft[5, -2]         # fails: negative count
not BitShiftRight[5, -2]        # fails: negative count
BitShiftRight[-5, 2] = -2       # succeeds: a negative value is fine

(BitShiftLeft[5, -2] or 7) = 7  # falls back to 7
```

Bit shifts work only with the `int` type, not `float` or `rational`.

Shifts combine naturally with the bitwise operations for building masks
and packing several small fields into one integer:

<!--versetest-->
<!-- 11 -->
```verse
# Build a mask for bit N
Bit3 := BitShiftLeft[1, 3]      # 8 = binary 1000
Flags := 10                     # 10 = binary 1010
BitAnd(Flags, Bit3) = 8         # bit 3 is set

# Pack two 4-bit fields into one value
Packed := BitOr(BitShiftLeft[5, 4], 10)
Packed = 90                     # 0101 1010

# Unpack them again
BitAnd(BitShiftRight[Packed, 4], 15) = 5    # high field
BitAnd(Packed, 15) = 10                     # low field
```

Integers in Verse are arbitrary precision, so shifting left grows the
result beyond 64 bits rather than wrapping around:

<!--versetest-->
<!-- 12 -->
```verse
BitShiftLeft[1, 64] = (9223372036854775807 + 1) * 2  # 2^64
BitShiftRight[BitShiftLeft[1, 200], 200] = 1
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
ShowMenu():void={}
UnlockAchievement():void={}
game_state := enum{Playing, Paused}
Score:int = 1500
HighScore:int = 1000
Health:float = 0.0
CurrentState:game_state = game_state.Paused
Level:int = 15
-->
<!-- 13 -->
```verse
# Numeric comparisons
if (Score > HighScore):
    Print("New high score!")

if (Health <= 0.0):
    HandlePlayerDeath()

# Enums, and every other comparable type, support = and <>
if (CurrentState <> game_state.Playing):
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

Comparisons between different types still compile, but they always fail:

<!--versetest-->
<!-- 14 -->
```verse
not (0 = 0.0)   # int is never equal to float
not ("5" = 5)   # string is never equal to int
```

## Logical Operators

Logical operators work with failable expressions and control the flow of success and failure.

### Query Operator (`?`)

The query operator checks if a `logic` value is `true` (see [Failure](08_failure.md#failable-expressions) for how `?` works with other types):

<!--versetest
StartGame():void={}
-->
<!-- 15 -->
```verse
IsReady:logic = true

if (IsReady?):
    StartGame()

# `IsReady?` is equivalent to comparing against true
IsReady = true
```

### Not Operator

The `not` operator negates the success or failure of an expression:

<!--versetest
ContinuePlaying()<computes>:void={}
-->
<!-- 16 -->
```verse
IsGameOver:logic = false

if (not IsGameOver?):
    ContinuePlaying()

# The effects of a failing expression are rolled back
var X:int = 0
if (not (set X = 5, IsGameOver?)):
    X = 0  # the assignment was undone when IsGameOver? failed
```

### And Operator

The `and` operator succeeds only if both operands succeed:

<!--versetest
EnterRoom()<computes>:void={}
ProcessResult()<computes>:void={}
HasKey:?int = option{1}
DoorUnlocked:?int = option{1}
QuickCheck()<computes><decides>:void = {}
ExpensiveCheck()<computes><decides>:void = {}
-->
<!-- 17 -->
```verse
if (HasKey? and DoorUnlocked?):
    EnterRoom()

# Short-circuit evaluation - second operand not evaluated if first fails
if (QuickCheck[] and ExpensiveCheck[]):
    ProcessResult()
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
<!-- 18 -->
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

When initializing constants and variables, both `=` and `:=` can be used if an explicit type is provided. For type inference (no type annotation), you must use `:=`.

<!--versetest-->
<!-- 19 -->
```verse
# Constant initialization with explicit types - both = and := work
MaxHealth:int = 100
PlayerName:string := "Hero"

# Variable initialization with explicit types - both = and := work
var CurrentHealth:int = 100
var Score:int := 0

# Type inference requires := (no type annotation)
AutoTyped := 42  # Inferred as int

# Note: var requires explicit type - var X := value is not allowed
```

The `set =` operator updates variable values:

<!--versetest
vector3:=struct{X:float, Y:float, Z:float}
-->
<!-- 20 -->
```verse
var Points:int = 0
set Points = 100

var Position:vector3 = vector3{X := 0.0, Y := 0.0, Z := 0.0}
set Position = vector3{X := 10.0, Y := 20.0, Z := 0.0}
```

## Special Operators

### Indexing

The square bracket operator is used for multiple purposes in Verse:

1. Indexing arrays, maps, and strings to access their elements
2. Calling functions which may fail

<!--versetest
Damage(Base:int, ?Bonus:int = 0)<computes><decides>:int = Base + Bonus
-->
<!-- 21 -->
```verse
# Array indexing (failable)
Scores := array{10, 20, 30}
Scores[1] = 20
not (Scores[9] = 0)  # out of bounds fails

# Map lookup (failable)
Ranks := map{"Alice" => 100, "Bob" => 85}
Ranks["Alice"] = 100

# String indexing (failable), yielding a char
Name:string = "Verse"
Name[0] = 'V'

# Calling a function that can fail
Damage[10] = 10                # optional argument omitted
Damage[10, ?Bonus := 5] = 15   # named argument
```

### Member Access

The dot operator accesses fields and methods of objects:

<!--versetest-->
<!-- 22 -->
```verse
weapon := class<computes>{Damage:float = 25.0}
player := class<computes>{Weapon:weapon = weapon{}, GetName()<computes>:string = "Hero"}

Player := player{}
Player.GetName() = "Hero"    # method call
Player.Weapon.Damage = 25.0  # member access chains left to right
```

### Range

The range operator creates ranges for iteration:

<!--versetest-->
<!-- 23 -->
```verse
# Ranges are inclusive at both ends
Indices := for (I := 0..4) { I }
Indices = array{0, 1, 2, 3, 4}
```

### Object Construction

Verse provides multiple syntaxes for constructing objects. All of the following are equivalent:

<!--versetest-->
<!-- 24 -->
```verse
point := struct{X:int = 0, Y:int = 0}

# Curly braces with commas
Point1 := point{X := 10, Y := 20}

# Curly braces with semicolons
Point2 := point{X := 10; Y := 20}

# Curly braces with newlines - no separator needed
Point3 := point{
    X := 10
    Y := 20  # a trailing comma here would be an error
}

# Colon syntax with newlines and no braces
Point4 := point:
    X := 10
    Y := 20

Point1 = Point2
Point2 = Point3
Point3 = Point4

# Dot syntax for a single field, the rest take their defaults
Point5 := point . X := 10
Point5 = point{X := 10, Y := 0}
```

### Tuple Access

Round braces when used with a single argument after a tuple expression, accesses tuple elements:

<!--versetest-->
<!-- 25 -->
```verse
MyTuple := (10, 20, 30)
MyTuple(0) = 10
MyTuple(2) = 30
```

## Type Conversions

Verse has limited implicit type conversion. Most conversions must be explicit:

<!--versetest-->
<!-- 26 -->
```verse
# No implicit int to float conversion
Count:int = 42
# Ratio:float = Count        # Error!
Ratio:float = Count * 1.0    # OK: explicit conversion
Ratio = 42.0

# No implicit numeric to string conversion
Score:int = 100
# Message:string = "Score: " + Score  # Error!
Message:string = "Score: {Score}"     # OK: string interpolation
Message = "Score: 100"
```

When operators work with mixed types, specific rules apply:

<!--versetest-->
<!-- 27 -->
```verse
# int and float mix under *, and the result is a float
5 * 2.0 = 10.0
Result:float = 5 * 2.0

# but they do not mix under + or -
# 5 + 2.0  # Error: no operator'+' overload takes (int, float)
```
