# Primitive Data Types

Verse provides a rich set of primitive types that cover fundamental
programming needs. The numeric types `int`, `float`, and `rational`
handle mathematical operations, counters, and measurements. The
`logic` type represents boolean values for conditions and flags. Text
is handled through `char`, `char32`, and `string` types for character
data, player names, and messages. Two special types, `any` and `void`,
serve unique roles in the type hierarchy as the supertype of all types
and the empty type respectively.

Let's explore each primitive type in detail, starting with the numeric types that form the backbone of game logic.

## Intrinsics

*intrinsic functions* are built-in operations provided directly by the
runtime that cannot be implemented in pure Verse code. These functions
receive special compiler treatment and form the foundation for many
language features. Intrinsic functions are special because they:

- **Implemented by the runtime**: Written in C++ or other native code, not Verse
- **Cannot be replicated in Verse**: Require access to runtime internals or low-level operations
- **Receive compiler recognition**: The compiler knows about them and may optimize their use

Examples include mathematical operations like `Abs()`, collection
methods like `Find()`, and type conversions like `ToString()`.

Most intrinsic functions *cannot be referenced as first-class
values*. This means you can call them directly, but you cannot store
them in variables or pass them as function arguments:

<!--versetest-->
<!-- 01 -->
```verse
Result := Abs(-42)  # Returns 42

# Invalid: Cannot reference without calling
# F := Abs  # ERROR
# Invalid: Cannot pass as parameter
# ApplyFunction(Abs, -42)  # ERROR
```

This restriction exists because intrinsics often require special
calling conventions or optimizations that don't fit the standard
function model. If you need to pass intrinsic functionality around,
wrap it in a regular function or nested function.

## Integers

The `int` type represents integer, non-fractional values. An `int` can
contain a positive number, a negative number, or zero.  Supported
integers range from `-9,223,372,036,854,775,808` to
`9,223,372,036,854,775,807`, inclusive. Literals (numbers that can be
written as constants in code) are limited in size.

You can include `int` values within your code as literals.

<!--versetest-->
<!-- 02 -->
```verse
A :int= -42                    # civilian size
#B := 42424242424242424242424242424242424242424242424242 # scary numbers...
                               # ...can be computed but not written as literals

AnswerToTheQuestion :int= 42   # A variable that never changes
CoinsPerQuiver :int= 100       # A quiver costs this many coins
ArrowsPerQuiver :int= 15       # A quiver contains this many arrows

# Mutable variables (see Mutability chapter for details on var and set)
var Coins :int= 225           # The player currently has 225 coins
var Arrows :int= 3            # The player currently has 3 arrows
var TotalPurchases :int= 0    # Track total purchases
```

You can use the four basic math operations with integers: `+` for
addition, `-` for subtraction, `*` for multiplication, and `/` for
division.

<!--versetest
MyInt:int=10
MyHugeInt:int=1010100101
-->
<!-- 03 -->
```verse
var C :int= (-MyInt + MyHugeInt - 2) * 3   # arithmetic
set C += 1                                 # like saying, set C = C + 1
set C *= 2                                 # like saying, set C = C * 2
```

For integers, the operator `/` is failable, and the result is a
`rational` type if it succeeds.

## Rationals

The `rational` type represents exact fractions as ratios of
integers. Unlike `int` or `float`, you cannot write a `rational`
literal directly—rationals are created through integer division using
the `/` operator.

<!--versetest-->
<!-- 04 -->
```verse
X := 7 / 3    # X has type rational, representing exactly 7÷3
```

Rationals provide *exact arithmetic* without the precision loss of
floating-point numbers, making them ideal for game logic requiring
precise fractional calculations (resource distribution, turn-based
systems, probability calculations).

Integer division with `/` produces a rational value. Division by zero fails:

<!--versetest-->
<!-- 05 -->
```verse
Half := 5 / 2           # rational: exactly 5/2
Third := 10 / 3         # rational: exactly 10/3
Quarter := 1 / 4        # rational: exactly 1/4

if (not (1 / 0)):
    # Division by zero fails
```

Rationals are automatically reduced to lowest terms for equality comparisons:

<!--versetest-->
<!-- 06 -->
```verse
# All these are equal - reduced to 5/2
(5 / 2) = (10 / 4)      # true
(5 / 2) = (15 / 6)      # true
(10 / 4) = (15 / 6)     # true
```

This normalization ensures that mathematically equivalent rationals
compare as equal regardless of how they were constructed.

Negative signs are normalized to the numerator:

<!--versetest-->
<!-- 07 -->
```verse
(1 / -3) = (-1 / 3)     # true: negative moves to numerator
(-1 / -3) = (1 / 3)     # true: double negative becomes positive
```

This canonical form simplifies equality checking and ensures
consistent behavior.

An important property: *`int` is a subtype of `rational`*. This means
any integer can be used where a rational is expected:

<!--versetest-->
<!-- 08 -->
```verse
ProcessRational(X:rational):rational = X

# Can pass integers directly
ProcessRational(5) = 5/1     # 5 is implicitly 5/1 (rational)
ProcessRational(0) = 0/1     # 0 is implicitly 0/1 (rational)
```

However, you *cannot* return a rational where an int is expected—that
would be a narrowing conversion:

<!--NoCompile-->
<!-- 09 -->
```verse
# Invalid: Cannot narrow rational to int
# BadFunction(X:rational):int = X  # ERROR 3510
```

Whole number rationals equal their integer equivalents:

<!--versetest-->
<!-- 10 -->
```verse
(2 / 1) = 2             # true
2 = (2 / 1)             # true
(4 / 2) = 2             # true: 4/2 reduces to 2/1, equals 2
(9 / 3) = 3             # true: 9/3 reduces to 3/1, equals 3
```

This enables seamless mixing of integer and rational values in calculations.

Two functions convert rationals to integers:

- **`Floor`** — rounds toward negative infinity (down on number line)
- **`Ceil`** — rounds toward positive infinity (up on number line)

<!--versetest-->
<!-- 11 -->
```verse
# Positive rationals
Floor(5 / 2)= 2         # 2.5 → 2 (down)
Ceil(5 / 2) = 3         # 2.5 → 3 (up)

# Negative rationals - note direction!
Floor((-5) / 2) = -3    # -2.5 → -3 (toward negative infinity)
Ceil((-5) / 2) = -2     # -2.5 → -2 (toward positive infinity)

# With negative denominator
Floor(5 / -2) = -3      # Same as (-5)/2
Ceil(5 / -2) = -2       # Same as (-5)/2

# Both negative
Floor((-5) / -2) = 2    # 2.5 → 2
Ceil((-5) / -2) = 3     # 2.5 → 3
```

`Floor` rounds toward negative infinity, *not* toward zero. This
matches mathematical convention but differs from truncation.  When the
argument is a rational, `Floor` does not fail, but if passed a `float`
it is a `decides` function.

Rationals can be used as parameter and return types:

<!--versetest-->
<!-- 12 -->
```verse
# Function returning rational
Half(X:int)<computes><decides>:rational = X / 2

# Use the result
if (Result := Half[7]):
    Floor(Result) = 3   # 7/2 = 3.5, Floor gives 3
    Ceil(Result) = 4    # 7/2 = 3.5, Ceil gives 4
```


Because `int` is a subtype of `rational`, you *cannot* overload based
solely on these types:

<!--NoCompile-->
<!-- 13 -->
```verse
# Invalid: Cannot distinguish int from rational
# ProcessValue(X:int):void = {}
# ProcessValue(X:rational):void = {}  # Error!
```

The compiler sees `int` as more specific than `rational`, so the
signatures would be ambiguous.

Rationals excel at resource distribution and fairness calculations:

<!--versetest-->
<!-- 14 -->
```verse
# Fair resource distribution
DistributeResources(TotalGold:int, NumPlayers:int)<decides>:int =
    GoldPerPlayer := TotalGold / NumPlayers
    Floor(GoldPerPlayer)  # Each player gets whole gold pieces or we fail

# Item affordability calculation
Coins:int = 225
CoinsPerQuiver:int = 100
ArrowsPerQuiver:int = 15

if (NumberOfQuivers := Floor(Coins / CoinsPerQuiver)):
    TotalArrows:int = NumberOfQuivers * ArrowsPerQuiver
    # Player can afford 2 quivers = 30 arrows
```

## Floats

The `float` type represents all non-integer numerical values. It can
hold large values and precise fractions, such as `1.0`, `-50.5`, and
`3.14159`. A float is an IEEE 64-bit float, which means it can contain
a positive or negative number that has a decimal point in the range
`[-2^1024 + 1, … , 0, … , 2^1024 - 1]`, or has the value `NaN` (Not a
Number). The implementation differs from the IEEE standard in the
following ways:

- There is only one `NaN` value.
- `NaN` is equal to itself.
- Every number is equal to itself.
- `0` cannot be negative.

You can include float values within your code as literals:

<!--versetest-->
<!-- 15 -->
```verse
A:float = 1.0
B := 2.14
MaxHealth : float = 100.0

var C:float = A + B
C = 3.14              # succeeds
set C -= 3.14
C = 0.0               # succeeds
# C = 0              # compile error; 0 is not a `float` literal
```

You can use the four basic math operations with floats: `+` for
addition, `-` for subtraction, `*` for multiplication, and `/` for
division. There are also combined operators for doing the basic math
operations (addition, subtraction, multiplication, and division), and
updating the value of a variable:

<!--versetest-->
<!-- 16 -->
```verse
var CurrentHealth : float = 100.0
set CurrentHealth /= 2.0    # Halves the value of CurrentHealth
set CurrentHealth += 10.0   # Adds 10 to CurrentHealth
set CurrentHealth *= 1.5    # Multiplies CurrentHealth by 1.5
```

To convert an `int` to a `float`, multiply it by `1.0`: `MyFloat:=MyInt*1.0`.

## Mathematical Functions

Verse provides intrinsic mathematical functions for common numerical
operations. These functions are optimized by the runtime and work with
both `int` and `float` types.

The `Abs()` function returns the absolute value of a number—its
distance from zero without regard to sign:

<!--NoCompile-->
<!-- 17 -->
```verse
# Signatures
Abs(X:int):int
Abs(X:float):float
```

<!--versetest-->
<!-- 18 -->
```verse
Abs(5)    # Returns 5
Abs(-5)   # Returns 5
Abs(0)    # Returns 0
Abs(3.14) # Returns 3.14
```

The `Min()` and `Max()` functions return the minimum or maximum of two values:

<!--NoCompile-->
<!-- 19 -->
```verse
# Signatures
Min(A:int, B:int):int
Min(A:float, B:float):float
Max(A:int, B:int):int
Max(A:float, B:float):float
```

<!--versetest-->
<!-- 20 -->
```verse
# NaN propagates through comparison
Max(NaN, 5.0)   # Returns NaN
Min(NaN, 5.0)   # Returns NaN
Max(NaN, NaN)   # Returns NaN

# Infinity handling
Max(Inf, 100.0)    # Returns Inf
Min(-Inf, 100.0)   # Returns -Inf
Max(-Inf, -Inf)    # Returns -Inf
Min(Inf, Inf)      # Returns Inf
```

Verse provides multiple rounding functions that convert floats to integers with different rounding strategies:

<!--NoCompile-->
<!-- 21 -->
```verse
# Signatures
Floor(X:float)<reads><decides>:int   # Round down
Ceil(X:float)<reads><decides>:int    # Round up
Round(X:float)<reads><decides>:int   # Round to nearest even (IEEE-754)
Int(X:float)<reads><decides>:int     # Truncate toward zero
```

Round to nearest even (ties go to even):

<!--versetest-->
<!-- 22 -->
```verse
Round[1.5]    # Returns 2 (tie: 1.5 rounds to even 2)
Round[0.5]    # Returns 0 (tie: 0.5 rounds to even 0)
Round[2.5]    # Returns 2 (tie: 2.5 rounds to even 2)
Round[-1.5]   # Returns -2 (tie: -1.5 rounds to even -2)
Round[-0.5]   # Returns 0 (tie: -0.5 rounds to even 0)

Round[1.4]    # Returns 1 (no tie, rounds down)
Round[1.6]    # Returns 2 (no tie, rounds up)
```

The "round to nearest even" strategy (also called banker's rounding)
avoids bias when rounding many tie values.

Some additional mathematical functions:

<!--versetest-->
<!-- 23 -->
```verse
# Signature
# Sqrt(X:float):float

# Negative inputs return NaN
Sqrt(-1.0)    # Returns NaN

# Special values
Sqrt(Inf)     # Returns Inf
Sqrt(NaN)     # Returns NaN

# Signature
# Pow(Base:float, Exponent:float):float

Pow(2.0, 3.0)     # Returns 8.0 (2³)
Pow(10.0, 2.0)    # Returns 100.0
Pow(4.0, 0.5)     # Returns 2.0 (square root)
Pow(2.0, -1.0)    # Returns 0.5 (reciprocal)

# Special cases
Pow(0.0, 0.0)     # Returns 1.0 (by convention)
Pow(NaN, 0.0)     # Returns 1.0 (0 exponent always 1)
Pow(1.0, NaN)     # Returns 1.0 (1 to any power is 1)

# Exp(X:float):float

Exp(0.0)      # Returns 1.0
Exp(1.0)      # Returns 2.718... (e)
Exp(-1.0)     # Returns 0.368... (1/e)

# Special values
Exp(-Inf)     # Returns 0.0
Exp(Inf)      # Returns Inf
Exp(NaN)      # Returns NaN

# Signature
# Ln(X:float):float

Ln(1.0)       # Returns 0.0
# Ln(2.718...)     # Returns 1.0 (ln(e) = 1)
Ln(10.0)      # Returns 2.302...

# Invalid inputs
Ln(-1.0)      # Returns NaN (negative)
Ln(0.0)       # Returns -Inf (log of zero)

# Special values
Ln(Inf)       # Returns Inf
Ln(NaN)       # Returns NaN

# Signature
# Log(Base:float, Value:float):float

Log(10.0, 100.0)   # Returns 2.0 (log₁₀(100) = 2)
Log(2.0, 8.0)      # Returns 3.0 (log₂(8) = 3)
Log(2.0, 2.0)      # Returns 1.0 (logₙ(n) = 1)
```

Verse provides standard trigonometric functions operating on radians:

<!--versetest-->
<!-- 27 -->
```verse
# Signatures
# Sin(Angle:float):float
# Cos(Angle:float):float
# Tan(Angle:float):float

# Common angles (using PiFloat constant)
Sin(0.0)              # Returns 0.0
Sin(PiFloat / 2.0)    # Returns 1.0
Sin(PiFloat)          # Returns 0.0
Sin(-PiFloat / 2.0)   # Returns -1.0

Cos(0.0)              # Returns 1.0
Cos(PiFloat / 2.0)    # Returns 0.0
Cos(PiFloat)          # Returns -1.0

Tan(0.0)              # Returns 0.0
Tan(PiFloat / 4.0)    # Returns 1.0
Tan(-PiFloat / 4.0)   # Returns -1.0

# Special values
Sin(NaN)              # Returns NaN
Sin(Inf)              # Returns NaN

# Signatures
# ArcSin(X:float):float   # Returns angle in [-π/2, π/2]
# ArcCos(X:float):float   # Returns angle in [0, π]
# ArcTan(X:float):float   # Returns angle in [-π/2, π/2]
# ArcTan(Y:float, X:float):float  # Two-argument arctangent

# Inverse relationships
ArcSin(0.0)    # Returns 0.0
ArcSin(1.0)    # Returns π/2
ArcSin(-1.0)   # Returns -π/2

ArcCos(1.0)    # Returns 0.0
ArcCos(0.0)    # Returns π/2
ArcCos(-1.0)   # Returns π

ArcTan(0.0)    # Returns 0.0
ArcTan(1.0)    # Returns π/4
ArcTan(-1.0)   # Returns -π/4

# Verify inverse relationship
Angle := PiFloat / 6.0  # 30 degrees
Sin(ArcSin(Sin(Angle))) = Sin(Angle)  # True

# ArcTan(Y, X) returns angle of point (X, Y) from origin
ArcTan(1.0, 1.0)     # Returns π/4 (45 degrees)
ArcTan(1.0, 0.0)     # Returns π/2 (90 degrees)
ArcTan(0.0, 1.0)     # Returns 0.0 (0 degrees)
ArcTan(1.0, -1.0)    # Returns 3π/4 (135 degrees)
ArcTan(-1.0, -1.0)   # Returns -3π/4 (-135 degrees)
```

Hyperbolic functions are analogs of trigonometric functions for
hyperbolas. They are useful in physics simulations, catenary curves,
and certain mathematical models.

<!--versetest-->
<!-- 28 -->
```verse
# Signatures
# Sinh(X:float):float    # Hyperbolic sine
# Cosh(X:float):float    # Hyperbolic cosine
# Tanh(X:float):float    # Hyperbolic tangent
# ArSinh(X:float):float  # Inverse hyperbolic sine
# ArCosh(X:float):float  # Inverse hyperbolic cosine
# ArTanh(X:float):float  # Inverse hyperbolic tangent

Sinh(0.0)     # Returns 0.0
Sinh(1.0)     # Returns 1.175...
Cosh(0.0)     # Returns 1.0
Cosh(1.0)     # Returns 1.543...
Tanh(0.0)     # Returns 0.0
Tanh(1.0)     # Returns 0.761...

# Special values
Sinh(-Inf)    # Returns -Inf
Sinh(Inf)     # Returns Inf
Cosh(-Inf)    # Returns Inf
Cosh(Inf)     # Returns Inf
Tanh(-Inf)    # Returns -1.0
Tanh(Inf)     # Returns 1.0

ArSinh(0.0)   # Returns 0.0
ArCosh(1.0)   # Returns 0.0
ArTanh(0.0)   # Returns 0.0

# Special values
ArSinh(-Inf)  # Returns -Inf
ArSinh(Inf)   # Returns Inf
ArCosh(Inf)   # Returns Inf
ArCosh(-1.0)  # Returns NaN (domain error)
```

For integer division with remainder, Verse provides `Mod` and
`Quotient`. Both functions are failable—they fail when the divisor is
zero.

<!--versetest-->
<!-- 29 -->
```verse
# Signatures
# Mod(Dividend:int, Divisor:int)<decides>:int
# Quotient(Dividend:int, Divisor:int)<decides>:int

# Positive operands
Mod[15, 4]      # Returns 3
Quotient[15, 4] # Returns 3
# Relationship: 15 = 3*4 + 3

# Negative dividend
Mod[-15, 4]      # Returns 1
Quotient[-15, 4] # Returns -4
# Relationship: -15 = -4*4 + 1

# Negative divisor
Mod[-1, -2]      # Returns 1
Quotient[-1, -2] # Returns 1

# Division by zero fails
if (not Mod[10, 0]):
    Print("Cannot mod by zero")
if (not Quotient[10, 0]):
    Print("Cannot divide by zero")
```

The modulo result always satisfies:

<!--NoCompile-->
<!-- 30 -->
```verse
Dividend = Quotient[Dividend, Divisor] * Divisor + Mod[Dividend, Divisor]
```

The sign of the result follows specific rules:

- `Mod` result has the same sign as the divisor (Euclidean division)
- `Quotient` adjusts accordingly to maintain the identity

There are also some utility functions:

<!--versetest-->
<!-- 31 -->
```verse
# Signatures
# Sgn(X:int):int
# Sgn(X:float):float

Sgn(10)       # Returns 1
Sgn(0)        # Returns 0
Sgn(-5)       # Returns -1

Sgn(3.14)     # Returns 1.0
Sgn(0.0)      # Returns 0.0
Sgn(-2.71)    # Returns -1.0

# Special float values
Sgn(Inf)      # Returns 1.0
Sgn(-Inf)     # Returns -1.0
Sgn(NaN)      # Returns NaN
```

Lerp interpolates between two values:

<!--versetest-->
<!-- 32 -->
```verse
# Signature
# Lerp(From:float, To:float, Parameter:float):float

Lerp(0.0, 10.0, 0.0)    # Returns 0.0 (0% = From)
Lerp(0.0, 10.0, 0.5)    # Returns 5.0 (50%)
Lerp(0.0, 10.0, 1.0)    # Returns 10.0 (100% = To)
Lerp(0.0, 10.0, 2.0)    # Returns 20.0 (extrapolation)
Lerp(10.0, 20.0, 0.3)   # Returns 13.0

# Works with negative ranges
Lerp(-10.0, 10.0, 0.5)  # Returns 0.0
```

The formula is: `From + Parameter * (To - From)`

`IsFinite` checks if a float is finite and suceeds if the value
is not NaN, Inf, or -Inf. And fails otherwise:

<!--versetest-->
<!-- 33 -->
```verse
# Method on float values
# X.IsFinite()<computes><decides>:float

(5.0).IsFinite[]      # succeeds
(0.0).IsFinite[]      # succeeds
(-100.0).IsFinite[]   # succeeds

(Inf).IsFinite[]  # fails
(-Inf).IsFinite[] # fails
(NaN).IsFinite[]  # fails

# Returns the same number if succeeds
(15.16).IsFinite[] = 15.16 # succeeds, both are equal

# Useful for validation
# SafeCalculation(X:float, Y:float)<decides>:float =
#     X.IsFinite[] and Y.IsFinite[]
#     Result := X / Y
#     Result.IsFinite[]
#     Result
```

Verse provides constants for common mathematical values:

<!--versetest-->
<!-- 34 -->
```verse
PiFloat # 3.14159265358979323846...
Inf     # Positive infinity
-Inf    # Negative infinity (negation of Inf)
NaN     # Not a Number
```

## Booleans

The `logic` type represents the Boolean values `true` and `false`.

<!--versetest-->
<!-- 35 -->
```verse
A:logic = true
B := false

# A = B          # fails
A?                # succeeds
# B?             # fails

true?             # succeeds
# false?         # fails
```

The `logic` type only supports query operations and comparison
operations.  Query expressions use the query operator `?` to check if
a logic value is true and fail if the logic value is `false`.  For
comparison operations, use the failable operator `=` to test if two
logic values are the same, and `<>` to test for inequality.

Many programming languages find it idiomatic to use a type like
`logic` to signal the success or failure of an operation. In Verse, we
use success and failure instead for that purpose, whenever
possible. The conditional only executes the `then` branch if the guard
succeeds:

<!--verse
ShowTargetLockedIcon():void={}
F(TargetLocked:?int):void={
-->
<!-- 36 -->
```verse
if (TargetLocked?):
    ShowTargetLockedIcon()
```
<!-- } -->

To convert an expression that has the `<decides>` effect to `true` on
success or `false` on failure, use `logic{ exp }`:

<!--verse
using{ /Verse.org/Random }
F(Frequency:int)<decides>:void={
-->
<!-- 37 -->
```verse
GotIt := logic{GetRandomInt(0, Frequency) <> 0}   # if success
GotIt?                                            # then this succeeds
GotIt = false                                     # and this fails
not GotIt?                                        # and this fails too
```
<!-- } -->

## Characters and Strings

Text is represented in terms of characters and strings.  A `char` is a
single **UTF-8 code unit** (not a full Unicode code point). A string
is therefore an array of characters, written as `[]char`. For
convenience, the type alias `string` is provided for `[]char`:

<!--versetest-->
<!-- 38 -->
```verse
MyName :string = "Joseph"
MyAlterEgo := "José"
```

UTF-8 is used as the character encoding scheme. Each UTF-8 code unit
is one byte. A Unicode code point may require between one and four
code units. Code points with lower values use fewer bytes, while
higher values require more.

For example:

- `"a"` requires one byte (`{0o61}`),
- `"á"` requires two bytes (`{0oC3}{0oA1}`),
- `"🐈"` (cat emoji) requires four bytes (`{0u1f408}`).

Thus, strings are sequences of code units, not necessarily sequences
of Unicode characters in the abstract sense.

Because strings are arrays of `char`, you can index into them with
`[]`. Indexing has the `<decides>` effect: it succeeds when the index
is valid and fails otherwise.

<!--versetest
MyName:string="J"
-->
<!-- 39 -->
```verse
TheLetterJ := MyName[0]     # succeeds
TheLetterJ = 'J'            # succeeds
# MyName[100]               # fails
```

The length of a string is the number of UTF-8 code units it contains,
accessed via `.Length`. Note that this is *not the same as the number
of Unicode characters*:

<!--versetest-->
<!-- 40 -->
```verse
"José".Length = 5           # succeeds; 5 UTF-8 code units
"Jose".Length = 4           # succeeds; 4 UTF-8 code units
```

Because `string` is just `[]char`, strings declared as `var` can be mutated:

<!--versetest-->
<!-- 41 -->
```verse
var OuterSpaceFriend :string = "Glorblex"
set OuterSpaceFriend[0] = 'F'
```

Strings can be concatenated using the `+` operator:

<!--versetest
MyName:string="Joe"
MyAlterEgo:string="Jak"
-->
<!-- 42 -->
```verse
MyAttemptAtFormatting := "My name is " + MyName + " but my alter ego is " + MyAlterEgo + "."
```

Verse also supports string interpolation for more readable formatting:

<!--versetest
MyName:string="3"
MyAlterEgo:string="asdsa"
-->
<!-- 43 -->
```verse
Formatting := "My name is {MyName} but my alter ego is {MyAlterEgo}."
```

Interpolation works for any value that has a `ToString()` function in scope.

Literal characters are written with single quotes. The type depends on
whether the character falls within the ASCII range (`U+0000`–`U+007F`)
or not:

- `'e'` has type `char`,
- `'é'` has type `char32`.

<!--versetest-->
<!-- 44 -->
```verse
A :char = 'e'                       # ok
B :char32 = 'é'                     # ok
# C :char = 'é'                     # error: type of 'é' is char32
# D :char32 = 'e'                   # error: type of 'e' is char
```

Character literals can also be written using numeric escape sequences:

<!--versetest-->
<!-- 45 -->
```verse
E :char = 0o65                      # ok; same as 'e'
F :char32 = 0u00E9                  # ok; same as 'é'
```

- `char` represents a single UTF-8 code unit (one byte, `0oXX`).
- `char32` represents a full Unicode code point (`0uXXXXX`).

Hex notation:

- `0oXX` for `char`: two hex digits (0o00 to 0off)
- `0uXXXXX` for `char32`: up to six hex digits (0u00000 to 0u10ffff)

Unlike some languages, Verse does not allow implicit conversion between characters and integers.

**Character escape sequences** work in both character and string literals:

| Escape | Meaning | Codepoint |
|--------|---------|-----------|
| `\t` | Tab | U+0009 |
| `\n` | Newline | U+000A |
| `\r` | Carriage return | U+000D |
| `\"` | Double quote | U+0022 |
| `\'` | Single quote | U+0027 |
| `\\` | Backslash | U+005C |
| `\{` | Left brace | U+007B |
| `\}` | Right brace | U+007D |
| `\<` | Less than | U+003C |
| `\>` | Greater than | U+003E |
| `\&` | Ampersand | U+0026 |
| `\#` | Hash/pound | U+0023 |
| `\~` | Tilde | U+007E |

Examples:

<!--versetest-->
<!-- 46 -->
```verse
Tab := '\t'
Newline := '\n'
Quote := '\"'
Brace := '\{'
```

Strings can be compared using the failable operators `=` (equality)
and `<>` (inequality). Comparison is done by code point, and is case
sensitive.  Equality depends on exact code unit sequences, not visual
appearance. Unicode allows multiple encodings for the same abstract
character. For example, `"é"` may appear as the single code point
`{0u00E9}`, or as the two-code-point sequence `"e"` (`{0u0065}`) plus
a combining accent (`{0u0301}`). These two strings look the same, but
they are not equal in Verse.

Checking whether a player has selected the correct item:

<!--versetest-->
<!-- 47 -->
```verse
ExpectedItemInternalName :string = "RedPotion"
SelectedItemInternalName :string = "BluePotion"

if (SelectedItemInternalName = ExpectedItemInternalName):
    true
else:
    false
```

Padding a timer with leading zeros:

<!--versetest-->
<!-- 48 -->
```verse
SecondsLeft :int = 30
SecondsString :string = ToString(SecondsLeft)    # convert int to string

var Combined :string = "Time Remaining: "
if (SecondsString.Length > 2):
    set Combined += "99"               # clamp to maximum
else if (SecondsString.Length < 2):
    set Combined += "0{SecondsString}" # pad with zero
else:
    set Combined += SecondsString
```

String interpolation supports complex expressions, not just simple variables:

<!--versetest
Format(D:float, ?Decimals:int):string=""
-->
<!-- 49 -->
```verse
# Expression interpolation
Age := 30
Message := "Next year: {Age + 1}"

# Function calls with named arguments
Distance := 5.5
Formatted := "Distance: {Format(Distance, ?Decimals:=2)}"
```

Strings can span multiple lines using interpolation braces for continuation:

<!--versetest-->
<!-- 50 -->
```verse
LongMessage := "This is a multi-line {
}string that continues across {
}multiple lines."

# Attention to whitespace:
AnotherMessage := "This is another {
}  multi-line message with     {
    # This comment is ignored
}    many spaces."
```

Empty interpolants `{}` are ignored, which is useful for line
continuation without adding content.

Since `string` is `[]char`, strings and character arrays can be compared:

<!--versetest-->
<!-- 51 -->
```verse
"abc" = array{'a', 'b', 'c'}    # Succeeds
"" = array{}                     # Succeeds - empty string equals empty array
```

Block comments within strings are removed during parsing:

<!--versetest-->
<!-- 52 -->
```verse
Text := "abc<#this comment is removed#>def"    # Same as "abcdef"
```

### ToString()

The `ToString()` function converts values to their string
representations. It's polymorphic—multiple overloads exist for
different types:

<!--NoCompile-->
<!-- 53 -->
```verse
# Signatures
ToString(X:int):string
ToString(X:float):string
ToString(X:char):string
ToString(X:string):string  # Identity function
```

String interpolation implicitly calls `ToString()` on embedded values:

<!--versetest-->
<!-- 54 -->
```verse
Age := 25
Score := 98.5

# These are equivalent:
Message1 := "Age: " + ToString(Age) + ", Score: " + ToString(Score)
Message2 := "Age: {Age}, Score: {Score}"
# Both produce: "Age: 25, Score: 98.5"
```

This makes `ToString()` essential for formatting output, even when you
don't call it directly.

`ToString()` only works on primitive types. User-defined classes and
structs don't have automatic string conversion.

### ToDiagnostic()

The `ToDiagnostic()` function converts values to diagnostic string
representations, useful for debugging and logging. While similar to
`ToString()`, it may provide more detailed or implementation-specific
information:

<!--versetest
SomeValue:int=1
-->
<!-- 55 -->
```verse
# Usage (exact signature depends on type)
DiagnosticText := ToDiagnostic(SomeValue)
```

`ToDiagnostic()` is primarily used for debugging output rather than
user-facing strings. The exact format it produces may vary between VM
implementations and is not guaranteed to be stable across versions.

## Type type

The `type` type is a *metatype* - a type whose values are themselves
types. Every Verse type can be used as a value of type `type`. This
enables powerful generic programming through parametric functions,
where types are parameters that can be passed around and constrained.

You can create variables and parameters that hold type values:

<!--versetest-->
<!-- 75 -->
```verse
# Variable holding a type value
IntType:type = int
StringType:type = string
# Function that takes a type as parameter
CreateDefault(t:type):?t = false
# Usage
X:?int = CreateDefault(int)      # T = int, returns false
Y:?string = CreateDefault(string)  # T = string, returns false
```

All Verse types can be type values:


<!-- TODO the following does not compile-->

<!--NoCompile-->
<!-- 76 -->
```verse
# Primitives
PrimitiveType:type = int

# User-defined types
MyClass := class {}
ClassType:type = MyClass

MyStruct := struct {Value:int}
StructType:type = MyStruct

# Collection types
ArrayType:type = []int
MapType:type = [string]int
TupleType:type = tuple(int, string)
OptionType:type = ?int

# Function types
FuncType:type = int->string

# Parametric types
generic_class(t:type) := class {Data:t}
ParametricType:type = generic_class(int)

# Metatypes
SubtypeValue:type = subtype(MyClass)

# Type literals
TypeLiteralValue:type = type{_(:int):string}
```

This universality makes `type` the foundation for Verse's generic
programming - any type can be abstracted over.

### Type Parameters

The most common use of `type` is in **where clauses** to create
parametric (generic) functions:

<!--versetest-->
<!-- 77 -->
```verse
# Identity function - works with any type
Identity(X:t where t:type):t = X

# Usage - type parameter inferred
Identity(42)        # t = int
Identity("hello")   # t = string
Identity(true)      # t = logic
```

The `where t:type` constraint means "`t` can be any Verse type." The
type system infers `t` from the argument and ensures type safety
throughout the function.

While `where t:type` accepts any type, you can use more specific
constraints like `subtype` to limit which types are valid:

<!--NoCompile-->
<!-- 78 -->
```verse
# Only accepts types that are subtypes of comparable
Sort(Items:[]t where t:subtype(comparable)):[]t =
    # Can use comparison operations because t is comparable
    ...
```

For comprehensive documentation on parametric functions, see the
Functions chapter.

### Type as First-Class Values

Unlike many languages where types only exist at compile time, Verse
treats types as *first-class values* that can be computed, stored, and
manipulated:

<!-- 79 -->
```verse
# Function that returns a type value
GetTypeForSize(Size:int):type =
    if (Size <= 8):
        int
    else:
        string

# Store type in data structure
TypeRegistry:[string]type = map{
    "Integer" => int,
    "Text" => string,
    "Flag" => logic
}
```

**Passing types between functions:**

<!--NoCompile-->
<!-- 80 -->
```verse
# Helper function that takes a type parameter
CreateArray(ElementType:type, Size:int):[]ElementType =
    # This pattern works in some contexts
    ...

# Function that uses the helper
MakeIntArray():[]int =
    CreateArray(int, 10)
```

### Returning Options of Type Parameters

A common pattern is to have functions return `?t` where `t` is a type
parameter, allowing the function to work with any type while
potentially failing:

<!--NoCompile-->
<!-- 81 -->
```verse
# Function that might produce a value of any type
MaybeValue(T:type, Condition:logic):?T =
    if (Condition?):
        # Cannot construct T generically, return failure
        false
    else:
        false

# Specific usage
X:?int = MaybeValue(int, false)  # Returns false as ?int
```

This pattern is particularly useful for generic containers and factory
functions that may or may not be able to produce a value.

### Type Constraints

The `type` constraint in where clauses is the most permissive - it
accepts any Verse type. For more specific requirements, Verse provides
additional constraints:

<!-- 82 -->
```verse
# Most permissive: any type
Generic(X:t where t:type):t = X

# More specific: must be subtype of comparable
RequiresComparison(X:t where t:subtype(comparable))<decides>:void =
    X = X  # Can use = because t is comparable

# Even more specific: must be exact subtype
RequiresExactType(X:t, Y:u where t:type, u:subtype(t)):t =
    X  # Y is guaranteed to be compatible with t
```

The type system enforces these constraints at compile time, preventing
invalid type usage.

### Limitations

While `type` enables powerful abstractions, there are some limitations:

**Cannot construct arbitrary types generically:**

<!--NoCompile-->
<!-- 83 -->
```verse
# Cannot do this - no way to construct a value of arbitrary type t
# MakeValue(T:type):T = ???  # What would this return for T=int? T=string?
```

**Cannot inspect type structure at runtime:**

<!-- 84 -->
```verse
# Cannot do this - no runtime type introspection
# GetFieldNames(T:type):[]string = ???
```

**Type parameters must be inferred or explicit:**

<!--NoCompile-->
<!-- 85 -->
```verse
# Type parameter must be determinable from usage
Identity(X:t where t:type):t = X

# OK: t inferred from argument
Identity(42)

# ERROR: t cannot be inferred from no arguments
# MakeDefault(where t:type):t = ???
```

## Any

The `any` type is the *supertype of all types*. Every type in the
language is a subtype of `any`. Because of this, `any` itself supports
very few operations: whatever functionality `any` provides must also
be implemented by every other type. In practice, there is very little
you can do directly with values of type `any`. Still, it is important
to understand the type, because it sometimes arises when working with
code that mixes different kinds of values, or when the type checker
has no more precise type to assign.

One way `any` appears is when combining values that do not share a
more specific supertype. For example:

<!-- 86 -->
```verse
Letters := enum:
    A
    B
    C

letter := class:
    Value : char
    Main(Arg : int) : void =
        X := if (Arg > 0) then:
            Letters.A
        else:
            letter{Value := 'D'}
```

In this example, `X` is assigned either a value of type `Letters` or
of type `letter`. Since these two types are unrelated, the compiler
assigns `X` the type `any`, which is their lowest common supertype.

A more useful role for `any` is as the type of a parameter that is
required syntactically but not actually used. This pattern can arise
when implementing interfaces that require a certain method signature.

<!-- 87 -->
```verse
FirstInt(X:int, :any) : int = X
```

Here, the second parameter is ignored. Because it can be any value of
any type, it is given the type `any`.

In more general code, the same idea can be expressed using *parametric
types*, making the function flexible while still precise:

<!-- 88 -->
```verse
First(X:t, :any where t:type) : t = X
```

This version works for any type `t`, returning a value of type `t`
while discarding the unused argument of type `any`.

## Void

The `void` type represents the absence of a meaningful result and is
used in places where no result is returned. Technically, `void` is
a function that accepts any value and evaluates to `false`.

This design allows a function with return type `void` to have a body
that evaluates to any type, while ensuring that callers cannot use
the result. The value produced by the body is passed to `void`, which
discards it and returns `false`.

A function whose purpose is to perform an effect, rather than compute
a value, has return type `void`.

<!-- 89 -->
```verse
LogMessage(Msg:string) : void =
    Print(Msg)
```

Here, `LogMessage` performs an action (printing) but does not return a
result. The `void` return type makes that explicit.
