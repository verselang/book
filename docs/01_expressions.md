# Expressions

Everything in Verse is an expression: every piece of code produces a
value, including constructs that in other languages would be
statements. An `if`, a loop, a variable declaration, and a block all
evaluate to something. Because there is no statement/expression
divide, any of them can appear wherever a value is expected.

## Primary Expressions

Everything starts with primary expressions—the atomic units from which
more complex expressions are built. These include literals,
identifiers, parenthesized expressions, and the tuple construct that
provides lightweight data aggregation.

### Basic Values

Literals are source code representations of constant values.
Verse provides literals for all its primitive types: integers, floats, characters,
strings, booleans, and functions. Each type has its own literal syntax and rules
governing valid values and their interpretation at compile time.

<!--versetest
point := struct{X:float, Y:float}
Condition:logic = true
-->
<!-- 01 -->
```verse
Result := if (Condition?) then 42 else 3.14  # Integer and float literals
array{1, 2, 3}                               # Integer literals in array construction
point{X:=0.0, Y:=1.0}                        # Float literals in object construction
```

#### Integer Literals

Integer literals represent whole numbers and can be written in two
formats. Decimal notation uses standard digits, while hexadecimal
notation uses the `0x` prefix followed by hex digits (0-9, a-f, A-F):

<!--versetest-->
<!-- 02 -->
```verse
Count := 42                          # Decimal
Negative := -17
Large := 9223372036854775807         # Maximum 64-bit signed integer literal
Byte := 0xFF                         # Hexadecimal
Byte = 255
LowercaseHex := 0xabcdef             # Either case of hex digit works
LowercaseHex = 0xABCDEF
```

Integer literals must fit within a 64-bit signed integer range
(`-9223372036854775808` to `9223372036854775807`). This is a compile-time
restriction on what values you can write directly in your code.

At runtime, integer values use arbitrary precision arithmetic and can grow
beyond 64-bit limits through computation. However, integers exceeding 64-bit
range have limited support (e.g., cannot be used in string interpolation
or persisted).

#### Float Literals

Floating-point literals represent decimal numbers, they must include a
decimal point and in some cases the `f64` suffix. Scientific notation
expresses very large or small numbers using exponents:

<!--versetest-->
<!-- 03 -->
```verse
Pi := 3.14159
Explicit := 12.34f64    # Explicit bit-depth suffix
Large := 1.0e10         # 10,000,000,000 (sign optional)
Small := 1.0e-5         # 0.00001
WithSign := 2.5e+3      # 2,500 (explicit + sign)
WithSign = 2500.0
```

Float literals must include a decimal point (`1.0` is valid, but `1` is an integer). A final decimal point without digits is invalid (`1.` is a syntax error). All floats are 64-bit (IEEE 754 double precision); the `f64` suffix is optional. Unary operators work as with integers: `-1.0`, `+1.0`.

Float literals outside the IEEE 754 double-precision range produce
compile-time errors:

<!--versetest
assert_semantic_error(3554):
    TooBig := 1.7976931348623159e+308
-->
<!-- 04 -->
```verse
Maximum := 1.7976931348623158e+308    # OK: maximum finite float
# TooBig := 1.7976931348623159e+308   # Error: literal overflow
```

Runtime float arithmetic, however, follows standard IEEE 754 semantics:

<!--versetest-->
<!-- 05 -->
```verse
PosInf := 1.0 / 0.0             # Division by zero produces infinity
NegInf := -1.0 / 0.0
NegInf < -1.0e308
Overflow := 1.0e308 * 10.0      # So does overflow
Overflow = PosInf
Tiny := 1.0e-320 / 1.0e10       # Underflow gives denormals, then zero
Tiny = 0.0
```

Float operations follow IEEE 754 semantics. Operations that would
produce NaN (like `0.0 / 0.0`, `Inf - Inf`, or `Sqrt(-1.0)`) return
NaN values rather than failing. NaN propagates through arithmetic
operations. Equality is one place where Verse parts company with IEEE
754: a NaN compares equal to itself rather than to nothing at all.

That departure looks less arbitrary once you remember what equality is
for in Verse. `float` is a comparable type, so it may be used as a map
key, and a key that could not be compared equal to itself would be a key
you could never look up again. Reflexive equality is the price of
letting every comparable type serve as a key, and NaN is not exempted
from it.

<!--versetest-->
<!-- 06 -->
```verse
Nan := 0.0 / 0.0        # A value, not a failure
not (Nan < 1.0)         # NaN is unordered: neither less nor greater
Nan + 1.0 = Nan         # NaN propagates through arithmetic
Nan = Nan               # But equality succeeds, unlike IEEE 754
```

#### Character Literals

Character literals represent individual text units. Verse has two character types with different literal syntax:

`char` literals represent UTF-8 code units (single bytes, 0-255):

<!--versetest-->
<!-- 07 -->
```verse
LetterA := 'a'          # Printable ASCII character
Tab := '\t'             # Escape sequence
LetterA = 0o61          # 0oXX is hexadecimal notation (0x61 = 97 = 'a')
```

`char32` literals represent Unicode code points:

<!--versetest-->
<!-- 08 -->
```verse
Emoji := '😀'           # Non-ASCII automatically char32
Accented := 'é'
Emoji = 0u1f600         # 0uXXXXXX is hexadecimal notation
```

Type inference from literals:

- ASCII characters (`U+0000` to `U+007F`): `'a'` has type `char`
- Non-ASCII characters: `'😀'` has type `char32`
- No implicit conversion between `char` and `char32`

Escape sequences work in both `char` and strings:

| Escape | Meaning | Codepoint |
|--------|---------|-----------|
| `\t`   | Tab     | U+0009 |
| `\n`   | Newline | U+000A |
| `\r`   | Carriage return | U+000D |
| `\"`   | Double quote | U+0022 |
| `\'`   | Single quote | U+0027 |
| `\\`   | Backslash | U+005C |
| `\{`   | Left brace (string interpolation) | U+007B |
| `\}`   | Right brace (string interpolation) | U+007D |
| `\<`   | Less than | U+003C |
| `\>`   | Greater than | U+003E |
| `\&`   | Ampersand | U+0026 |
| `\#`   | Hash      | U+0023 |
| `\~`   | Tilde     | U+007E |

Numeric character notation works as follows:

- `0oXX` for `char` (hexadecimal notation, `0o00` to `0oFF` for values 0-255)
- `0uXXXXXX` for `char32` (hexadecimal notation, `0u000000` to `0u10ffff`)

Character literals cannot be empty or contain multiple characters.

#### String Literals

String literals represent text sequences and support interpolation for embedding expressions. Basic strings use double quotes:

<!--versetest-->
<!-- 09 -->
```verse
Greeting := "Hello, World!"
Empty := ""
WithEscapes := "Line 1\nLine 2\tTabbed"
```

String interpolation embeds expressions using curly braces:

<!--versetest
Format(D:float, ?Decimals:int)<computes>:string=""
-->
<!-- 10 -->
```verse
Name := "Alice"
Message := "Hello, {Name}!"
Message = "Hello, Alice!"

Age := 30
Info := "Age next year: {Age + 1}"                      # Any expression
Info = "Age next year: 31"

Formatted := "Distance: {Format(5.5, ?Decimals := 2)}"  # Call with named argument
```

Multi-line strings can span multiple lines using interpolation braces
for continuation. Whatever follows the closing brace, leading spaces
included, is kept verbatim:

<!--versetest-->
<!-- 11 -->
```verse
LongMessage := "This is a multi-line {
}string that continues across {
}multiple lines."
LongMessage = "This is a multi-line string that continues across multiple lines."
```

The compiler ignores empty interpolants:

<!--versetest-->
<!-- 12 -->
```verse
Text1 := "ab{}cd"
Text1 = "abcd"
Text2 := "ab{
}cd"                    # A newline inside an interpolant disappears too
Text2 = "abcd"
```

Curly braces must be escaped (`"\{ \}"`) to appear as literal characters in strings. The `string` type is an alias for `[]char` (array of UTF-8 code units). Since UTF-8 code units are single bytes, strings are byte sequences rather than Unicode character sequences. For example, `"José".Length` returns `5` (5 code units/bytes, not 4 characters, since é takes 2 code units).

String-array equivalence:

<!--versetest-->
<!-- 13 -->
```verse
"abc" = array{'a', 'b', 'c'}
"" = array{}
```

The compiler removes comments from strings:

<!--versetest-->
<!-- 14 -->
```verse
Text := "abc<#comment#>def"
Text = "abcdef"
```

#### Boolean Literals

The `logic` type has two literal values. Use boolean values with the
query operator `?` or in comparisons:

<!--versetest
StartGame():void = {}
ShowResults():void = {}
-->
<!-- 15 -->
```verse
IsReady := true
IsComplete := false

if (IsReady?):
    StartGame()

if (IsComplete = true):
    ShowResults()
```

The `logic{}` expression creates boolean values from failable expressions (see [Failure](08_failure.md) for details on failable expressions):

<!--versetest
Operation()<computes><decides>:void = {}
Optional:?int = option{1}
X:int = 1
Y:int = 1
-->
<!-- 16 -->
```verse
Success := logic{Operation[]}        # True if succeeds, false if fails
HasValue := logic{Optional?}         # True if optional has value
IsEqual := logic{X = Y}              # True if equal, false otherwise
Success = true
IsEqual = true
```

The `logic{}` expression requires at least a superficial possibility of failure. Pure expressions without `<decides>` effect cause errors:

<!--versetest
assert_semantic_error(3513, 3547):
    Bad18a := logic{0}
assert_semantic_error(3660):
    Bad18b := logic{}
-->
<!-- 17 -->
```verse
# ERROR: logic{0} has no decides effect
# ERROR: logic{} is empty
Valid := logic{false?}               # OK: false? can fail
```

Multiple expressions inside `logic{}` can be separated by semicolons or commas (see [Semicolons vs Commas](#semicolons-vs-commas) for details).

#### Path Literals

Path literals identify modules and packages using a hierarchical naming scheme:

<!--NoCompile-->
<!-- 18 -->
```verse
/Verse.org/Verse                    # Standard library path
/YourGame/Player/Inventory          # Custom module path
/user@example.com/MyModule          # Personal namespace
```

Path syntax follows specific rules:

- Starts with `/`
- Contains label (alphanumeric, `.`, `-`)
- Identifiers must start with letter or `_`

The Modules chapter covers path literals in detail.

### Identifiers and References

Identifiers serve as references to values, whether they are constants,
variables, functions, or types. An identifier begins with a letter
(A-Z, a-z) or an underscore (`_`), and its subsequent characters are
letters, digits (0-9), or underscores. The single underscore `_` is
reserved and cannot be used as an identifier.

Identifiers are case-sensitive and use only ASCII characters—Unicode
characters are not supported in identifiers.

<!--versetest
GetValue()<computes>:int = 1
Counter:int = 2
my_class := class{}
_private:int = 3
variable123:int = 4
assert_semantic_error(3549):
    HyphenName()<computes>:void =
        my-variable := 3
assert_semantic_error(3514):
    UnderscoreName()<computes>:void =
        _ := 3
-->
<!-- 19 -->
```verse
int               # Reference to the int type
GetValue          # Reference to a function
Counter           # Reference to a variable
my_class          # Reference to a class
_private          # Leading underscore allowed
variable123       # Digits allowed after first character

# Invalid identifiers:
# 123invalid      # Error: cannot start with a digit
# my-variable     # Error: a hyphen reads as subtraction
# café            # Error: Unicode not supported
# _               # Error: single underscore is reserved
```

The language does not syntactically distinguish between different kinds
of identifiers (types, functions, variables)—the context determines how
each identifier is used.

An identifier may also end in a quoted part, written in single quotes
directly after the name: `name'…'`. The quoted part can hold any
printable ASCII character, spaces and punctuation included, except a
single or double quote, a backslash, a curly brace, or the comment
delimiters `<#` and `#>`. It is part of the name, so `Count` and
`Count'max'` are two unrelated identifiers. Quoted names work for every
kind of definition, including functions, extension methods, constants,
classes and fields:

<!--versetest
assert_syntax_error(3100){"a'b'c'(X:int):int = X"}
-->
<!-- 20 -->
```verse
_'~'(Value:int):int = -Value - 1        # a function
(Value:int)._'~'():int = -Value - 1     # an extension method
Count'max':int = 99                     # a constant
F'a b'(X:int):int = X + 1               # a space inside the quotes

_'~'(5) = -6
5._'~'() = -6
Count'max' = 99
F'a b'(1) = 2

# a'b'c'(X:int):int = X                 # Error: quotes cannot nest
```

Quoted names exist mainly to name operators. The function behind `A + B`
is called `operator'+'`, and the one behind `-A` is `prefix'-'`; the
Operators chapter shows how to define them for your own types. A name
like `_'+'` is just an ordinary function that happens to contain a plus
sign, and defining it has no effect on the `+` operator. Most names of the
form `operator'…'`, `prefix'…'` and `postfix'…'` are reserved, and
defining one is error 3514.

### Parentheses and Grouping

Parentheses serve dual purposes: they group expressions to control
evaluation order, and they create tuple expressions. A parenthesized
expression simply evaluates to the value of its contents, allowing you
to override the default operator precedence or improve readability:

<!--versetest
A:int = 1
B:int = 2
C:int = 3
X:int = 5
Y:int = 10
Positive:string = "positive"
Negative:string = "negative"
-->
<!-- 21 -->
```verse
(A + B) * C = 9   # Group addition before multiplication: (1+2)*3, not 1+(2*3)
if (X > 0 and Y > 0) then Positive else Negative
```

### Tuples

Tuples provide a way to group two or more values with little
ceremony. The syntax distinguishes between parentheses used for
grouping and those used for tuple construction through the presence of
commas. Tuples themselves are accessed using function-call syntax with
a single integer argument:

<!--versetest-->
<!-- 22 -->
```verse
Point := (10, 20)           # Two-element tuple
Mixed := (1, "hello", true) # Mixed-type tuple
Point(0) = 10               # Access first element
Point(1) = 20               # Access second element
```

Write tuple types as follows:

<!--versetest-->
<!-- 23 -->
```verse
Pair:tuple(int,int) = (10, 20)
Record:tuple(int,string,logic) = (42, "hello", true)
```

While the compiler accepts single-element tuple types like `tuple(int)`,
there is currently no syntax to construct a single-element tuple value.

## Postfix Operations

Postfix operations are operations that follow their operand and can be
chained together. This creates a left-to-right reading order that
feels natural and allows for intuitive composition.

### Member Access

The dot operator provides access to members of objects, modules, and
other structured values. Member access expressions evaluate to the
value of the specified member:

<!--versetest
shapes := module:
    Area<public>(Width:int, Height:int)<computes>:int = Width * Height
point := struct{X:float, Y:float}
hero := class{Name:string, Position:point}
-->
<!-- 24 -->
```verse
Player := hero{Name := "Ada", Position := point{X := 1.0, Y := 2.0}}
Player.Name = "Ada"             # Field of a class
Player.Position.Y = 2.0         # Field of a nested struct
shapes.Area(3, 4) = 12          # Function of a module
```

Member access can be chained, creating paths through nested structures:

<!--versetest
item := class{Name:string = "Sword"}
inventory := class{Items:[]item = array{item{}}}
player := class{Inventory:inventory = inventory{}}
game := class{Players:[]player = array{player{}}}
-->
<!-- 25 -->
```verse
Game := game{}
Game.Players[0].Inventory.Items[0].Name = "Sword"
```

### Computed Access

Square brackets provide computed access to elements, whether for
arrays, maps, or other indexable structures. Verse evaluates the expression within
brackets to determine which element to access:

<!--versetest
ComputeIndex()<computes>:int = 0
Values:[]int = array{1, 2, 3}
Lookup:[string]int = map{"key" => 42}
Grid:[][]int = array{array{1, 2}, array{3, 4}}
-->
<!-- 26 -->
```verse
Values[0] = 1               # Array indexing
Lookup["key"] = 42          # Map lookup
Grid[1][0] = 3              # Nested indexing
Values[ComputeIndex()] = 1  # Dynamic index computation
```

The square bracket syntax `Func[]` is **required** for calling
functions that may fail (those with the `<decides>` effect). Use regular
parentheses `Func()` for functions that always succeed. Array
indexing also uses `[]` because it can fail when the index is out of bounds.

<!-- 27 -->
```verse
GetValue()<transacts><decides>:int = 42
GetData():int = 7

# [] is required: GetValue can fail
if (X := GetValue[]):
    Print("Got: {X}")

# () is required: GetData always succeeds
Y := GetData()
```

### Function Calls

Function calls use parentheses with comma-separated arguments. The
language treats function calls as expressions that evaluate to the
function's return value:

<!--versetest
Root(X:int)<computes>:int = X
Larger(A:int, B:int)<computes>:int = if (A > B) then A else B
Initialize()<computes>:void = {}
GetData()<computes>:int = 42
Transform()<computes>:int = 10
Combine(X:int, Y:int)<computes><decides>:int = X + Y
-->
<!-- 28 -->
```verse
Root(16) = 16                       # Single argument
Larger(5, 10) = 10                  # Multiple arguments
Initialize()                        # No arguments
Combine[GetData(), Transform()] = 52 # Nested calls, outer call may fail
```

## Object Construction

Object construction uses a distinctive brace syntax to indicates the
creation of a new instance. The syntax requires explicit field
initialization using the `:=` operator:

<!--versetest
point := struct{ X:int, Y:int }
player := struct{Name:string, Level:int, Health:int}
config := struct { MaxPlayers:int, Difficulty:string, EnablePvP:logic }
-->
<!-- 29 -->
```verse
point{X:=10, Y:=20}
player{Name:="Hero", Level:=1, Health:=100}
config{
    MaxPlayers := 16,
    EnablePvP := true,
    Difficulty := "normal"
}
```

The use of `:=` for field initialization reinforces that these are
binding operations—you're binding values to fields at construction
time. Object constructors can be nested, creating complex
initialization expressions:

<!--versetest
point:=struct{ X:int, Y:int}
inventory:=struct{Capacity:int}
player:=struct{ Position:point, Inventory:inventory}
config:=struct{Difficulty:string}
game_state:=struct{Player:player, Settings:config}
-->
<!-- 30 -->
```verse
Game := game_state{
    Player := player{
        Position := point{X:=0, Y:=0},
        Inventory := inventory{Capacity:=20}
    },
    Settings := config{Difficulty:="hard"}
}
Game.Player.Inventory.Capacity = 20
```

## Control Flow as Expressions

One of Verse's distinctive features is that control flow constructs
are expressions, not statements. This means that if-expressions,
loops, and case expressions all produce values that can be used in
larger expressions.

### Conditional

The if-then-else construct is an expression that evaluates to one of
two values based on a condition:

<!--versetest
ComputeA()<computes>:int=1
ComputeB()<computes>:int=1
X:int = 5
Condition:logic = true
-->
<!-- 31 -->
```verse
Result := if (X > 0) then "positive" else "negative"
Result = "positive"
Value := if (Condition?) then ComputeA() else ComputeB()
```

The else clause can be omitted, though this affects the type of the
expression. Verse supports multiple syntactic forms for
if-expressions, including parenthesized conditions and indented
bodies:

<!--versetest
Condition:logic = true
Value1:int = 42
Value2:int = 100
-->
<!-- 32 -->
```verse
# Standard form
if (Condition?) then Value1 else Value2

# Indented form
if:
    Condition?
then:
    Value1
else:
    Value2
```

### For

For expressions iterate over collections and produce values. The basic
form iterates over elements:

<!--versetest
Process(Item:int)<computes>:void={}
Collection:[]int = array{1, 2, 3}
-->
<!-- 33 -->
```verse
for (Item : Collection) { Process(Item) }

Doubled := for (Item : Collection) { Item * 2 }
Doubled = array{2, 4, 6}      # A for expression evaluates to an array
```

An extended form provides access to both index and item--in the case
of a `Map`, indices are not limited to integers:

<!--versetest
Collection:[]int = array{1, 2, 3}
-->
<!-- 34 -->
```verse
for (Index -> Item : Collection) {
    Print("Item at {Index} is {Item}")
}
```

Since for expressions are themselves expressions, they produce array
values and compose with other expressions. Verse evaluates the body of a for
expression for each successful iteration, and these evaluations determine
the value of the expression as a whole.

### Loop

Loop expressions provide indefinite iteration, continuing until
explicitly terminated through failure or other control flow:

<!--versetest
GetNext()<computes>:int=1
Done(Value:int)<computes><decides>:void={}
Process(Value:int)<computes>:void={}
-->
<!-- 35 -->
```verse
loop {
    Value := GetNext()
    if (Done[Value]) then break
    Process(Value)
}
```

The loop construct can use indented syntax for clarity.

A loop expression produces a value of type `true`, regardless of what
expressions appear in its body. This value has no practical use—loops are typically used for their side effects rather than their return value.

<!-- 36 -->
```verse
var Count:int = 0

Result := loop:          # Result has type 'true'
    set Count += 1
    if (Count >= 3):
        break
Count = 3
```

### Case

Case expressions provide multi-way branching based on value matching:

<!--versetest
color := enum:
    Red
    Yellow
    Green
    Other
Color:color = color.Red
-->
<!-- 37 -->
```verse
Description := case(Color) {
    color.Red => "Danger",
    color.Yellow => "Warning",
    color.Green => "Safe",
    _ => "Unknown"
}
Description = "Danger"
```

The `_` pattern serves as a catch-all, ensuring the case expression is
exhaustive. Case expressions evaluate to the value of the matched
branch, making them useful for value computation as well as control
flow.

## Binary Operations

Binary expressions follow a carefully designed precedence hierarchy
that balances mathematical conventions with programming practicality.

### Assignment and Binding

At the lowest precedence level, assignment operators bind values to
identifiers. The `:=` operator creates immutable bindings, while `set
=` performs mutable assignment:

<!--versetest-->
<!-- 38 -->
```verse
X := 42           # Immutable binding
Y := X * 2        # Binding to computed value
Y = 84
Z := W := 10      # Right-associative chaining
Z = W
```

Assignment operators are right-associative, meaning that `a := b := c`
groups as `a := (b := c)`. This allows for natural chaining of
assignments while maintaining clarity about evaluation order.

Compound assignments provide shorthand for common update patterns:

<!--versetest-->
<!-- 39 -->
```verse
var Total:int = 3
set Total += 1        # Equivalent to: set Total = Total + 1
set Total *= 2        # Equivalent to: set Total = Total * 2
Total = 8
```

Compound assignment operators evaluate the left-hand side expression only once, which is observable when the expression has side effects:

<!-- 40 -->
```verse
var Values:[]int = array{10, 20, 30}
var Index:int = 0

# Each call returns one more than the last
Inc():int =
    set Index += 1
    Index

# Inc() runs once, so this reads and writes Values[1]
set Values[Inc()] += 1
```
<!--versetest
Index = 1
Values[1] = 21
-->

In the compound assignment `set Values[Inc()] += 1`, Verse calls the function `Inc()`
once to determine the index, then reads that location,
increments it, and stores the result back. Had it expanded to
`set Values[Inc()] = Values[Inc()] + 1`, the two calls would have named
different elements.

### Range Expressions

The range operator (`..`) creates integer ranges for iteration in
`for` loops. Ranges are **inclusive on both ends** and can only appear
directly in for loop iteration clauses, where they must be bound with
`:=` rather than `:`. The bounds themselves can be any integer
expressions:

<!--versetest-->
<!-- 41 -->
```verse
Count := 4
Squares := for (I := 1..Count - 1) { I * I }
Squares = array{1, 4, 9}
```

Ranges are not first-class values. They cannot be stored in variables
or used outside of `for` loop iteration clauses. See the [Range
Operator Restrictions](07_control.md#for-expressions)
section for details.

### Logical Operations

Logical operators combine boolean values with short-circuit
evaluation. Their result is either success or failure. Verse uses
keyword operators (`and`, `or`, `not`) rather than symbols, improving
readability:

<!--versetest
Quadrant()<computes>:void = {}
Validated:logic = true
UseDefault()<computes><decides>:void = {}
Ready()<computes><decides>:void = {}
Wait()<computes>:void = {}
X:int = 5
Y:int = 10
-->
<!-- 42 -->
```verse
if (X > 0 and Y > 0) then Quadrant()
Chosen := logic{Validated? or UseDefault[]}
if (not Ready[]) then Wait()
```

The precedence ensures that `and` binds tighter than `or`, matching
mathematical logic conventions, the `logic{}` expression turns success
or failure into a value:

<!--versetest-->
<!-- 43 -->
```verse
# Evaluates as: (true and true) or (false and false)
Grouped := logic{true? and true? or false? and false?}
Grouped = true      # Would be false if the operators grouped left to right
```

Variable bindings do not escape from logical operations.
When you use `:=` inside `and`, `or`, or `not` expressions, those
bindings are only evaluated for short-circuit control flow and are **not**
accessible afterward. A binding made directly by an `if`, on the other
hand, is visible in the body of that `if`:

<!--versetest
assert_semantic_error(3506, 3506):
    EscapingBind()<computes><decides>:void =
        Pair:[]int = array{10, 20}
        if ((X := Pair[0]) and (Y := Pair[1])):
            Z := X + Y
-->
<!-- 44 -->
```verse
Pair:[]int = array{10, 20}

# ERROR: X and Y are unknown identifiers in the body
# if ((X := Pair[0]) and (Y := Pair[1])):
#     Z := X + Y

# OK: a simple if binding is accessible
if (First := Pair[0]):
    First = 10
```

### Comparison Operations

Comparison operators also either succeed or fail and can be chained
for range checking:

<!--versetest
InRange()<computes>:void={}
Value:int = 50
X:int = 75
Minimum:int = 0
Maximum:int = 100
A:int = 5
B:int = 10
-->
<!-- 45 -->
```verse
if (0 <= Value <= 100) then InRange()
IsValid := logic{X > Minimum and X < Maximum}
IsValid = true
Different := logic{A <> B}
Different = true
```

All comparison operators have the same precedence and evaluate
left-to-right. Crucially, comparison operators return their left
operand when the comparison succeeds, and comparison chains have special
syntax that checks all adjacent pairs.

<!--versetest-->
<!-- 46 -->
```verse
Left := 0 < 10
Left = 0                  # A comparison returns its left operand

Value := 50
0 <= Value <= 100         # Chain checks BOTH 0 <= Value and Value <= 100
not (10 <= Value <= 40)   # And fails when either half fails
```

Verse does **not** evaluate the comparison chain `A <= B <= C` as `(A <= B) <= C`.
Instead, it is special syntax that checks both `A <= B` **and** `B <= C`, while
returning the leftmost operand (`A`) on success. This enables natural
mathematical notation for ranges without requiring `and` operators.

### Arithmetic Operations

Arithmetic operations follow standard mathematical precedence, with
multiplication and division binding tighter than addition and
subtraction:

<!--versetest
A:int = 1
B:int = 2
C:int = 3
-->
<!-- 47 -->
```verse
Result := A + B * C          # Multiplication first
Result = 7
Average := (A + B + C) / 2   # Parentheses override precedence
Average = 3
```

Integer division by zero fails and has the `<decides>` effect.
When dividing integers, `X / Y` can fail if `Y` is `0`, allowing you to handle
this case safely. Note that dividing two integers yields a `rational`,
not an `int`, so the quotient cannot be assigned to an `int` variable:

<!--versetest
X:int = 10
Y:int = 0
assert:
    not(Result := X / Y)
-->
<!-- 48 -->
```verse
if (Result := X / Y):
    Print("Division succeeded")
else:
    Print("Cannot divide by zero")
```

Float division by zero does not fail; it returns infinity according to
IEEE 754 floating-point semantics.

Unary operators have the highest precedence among arithmetic operations:

<!--versetest
Flag:logic = true
Value:int = 1
X:int = 1
Y:int = 2
-->
<!-- 49 -->
```verse
Negative := -Value
Inverted := logic{not Flag?}
Result := -X * Y    # Unary minus applies to X only
Result = -2
```

## Set Expressions

While Verse emphasizes immutability, practical programming sometimes
requires mutation. Set expressions provide mutation of variables and
fields:

<!--versetest
counter := class { var Count:int = 0 }
-->
<!-- 50 -->
```verse
var Health:int = 0
var Slots:[]int = array{0, 0}
var Scores:[string]int = map{"Ana" => 0}
Hero := counter{}

set Health = 10         # Variable assignment
set Hero.Count = 5      # Field assignment
set Slots[0] = 99       # Array element assignment
set Scores["Ana"] = 3   # Map entry assignment
Health = 10
Hero.Count = 5
Slots[0] = 99
Scores["Ana"] = 3
```

Set expressions are themselves expressions that **return the value being
assigned** (the right-hand side). For example, `set Obj.Field = Value`
returns `Value`, not `Obj`. This allows chaining assignments:

<!-- 51 -->
```verse
var X:int = 0
var Y:int = 0

set Y = set X = 5  # Both X and Y become 5
```
<!--versetest
X = 5
Y = 5
-->

Though set expressions have a value, they are typically used for their side
effects. The left-hand side must be a valid LValue—something that can be
assigned to.

Verse supports complex LValues, allowing updates deep within data structures:

<!--versetest
item := class{Name:string = "Sword"}
inventory := class{var Items:[]item = array{item{}}}
player := class{Inventory:inventory = inventory{}}
game := class{Players:[]player = array{player{}}}
-->
<!-- 52 -->
```verse
Game := game{}
set Game.Players[0].Inventory.Items[0] = item{Name := "Axe"}
Game.Players[0].Inventory.Items[0].Name = "Axe"
```

## Semicolons vs Commas

Verse uses semicolons and commas as separators in various contexts,
but they have fundamentally different semantics in most
situations. Understanding when each is appropriate is essential for
writing correct Verse code.

Semicolons within parentheses create *sequences*: they evaluate expressions in order and return the value of the last expression.

<!--versetest
assert_semantic_error(3560, 3547):
    Result49 := 1; 2
-->
<!-- 53 -->
```verse
Sequence := (1; 2; 3)     # Evaluates 1, then 2, then 3
Sequence = 3              # And returns the last one
# Sequence := 1; 2        # ERROR: parentheses are required
```

Commas within parentheses create *tuples*: they group multiple values into a single composite value.

<!--versetest
assert_semantic_error(3560, 3547):
    Result50 := 1, 2
-->
<!-- 54 -->
```verse
Tuple := (1, 2, 3)        # Creates a tuple of three elements
Tuple = (1, 2, 3)         # Type is tuple(int, int, int)
# Tuple := 1, 2           # ERROR: parentheses are required
```

### Context-Specific Behavior

In expression contexts (like assignments), semicolons and commas require
parentheses to create sequences and tuples. The distinction is clear when
comparing parenthesized expressions, and it applies to function return
values as well:

<!--versetest-->
<!-- 55 -->
```verse
GetInt():int = (1.0; 2)                    # Sequence: returns 2 (int)
GetTuple():tuple(float, int) = (1.0, 2)    # Tuple: returns (1.0, 2)
GetInt() = 2
GetTuple() = (1.0, 2)
```

Semicolons in argument position create a *sequence that executes
before the call*, with only the last value passed as the argument. This
pattern enables side effects in argument position:

<!--versetest
Process(X:int)<computes>:void={}
LogEvent(S:string)<computes>:int=1
MultiplyByTen(X:int)<computes>:int = X * 10
-->
<!-- 56 -->
```verse
Process(LogEvent("called"); 42)   # Logs "called", then calls Process(42)

Result := MultiplyByTen(2; 3)     # Discards 2, then calls MultiplyByTen(3)
Result = 30
```

Commas separate distinct arguments in the standard way:

<!--versetest
Add(A:int, B:int)<computes>:int = A + B
-->
<!-- 57 -->
```verse
Sum := Add(10, 20)                # Two separate arguments
Sum = 30
```

Semicolons are *not allowed* in parameter lists - you must use commas:

<!--versetest
assert_semantic_error(3540):
    InvalidFunc(A:int; B:int):void = {}
-->
<!-- 58 -->
```verse
ValidFunc(A:int, B:int):void = {}     # VALID: comma-separated parameters
# InvalidFunc(A:int; B:int):void = {} # ERROR: semicolon in parameters
```

### In Specific Scopes

Within block expressions (braces), semicolons and commas are interchangeable as separators between definitions:

<!--versetest-->
<!-- 59 -->
```verse
# In block scope, all three separators work:
block:
    X:int = 0; Y:int = 0      # Semicolon separator

block:
    X:int = 0, Y:int = 0      # Comma separator

block:
    X:int = 0                 # Newline separator (most common)
    Y:int = 0
```

In `logic{}` constructor - both semicolons and commas work, but with
different semantics based on the construct's behavior:

<!--versetest-->
<!-- 60 -->
```verse
# Both evaluate all expressions and return logic value
Result1 := logic{true?; true?}    # Sequence of queries
Result2 := logic{true?, true?}    # Also valid
Result1 = Result2
```

In `option{}` constructor - follows the standard sequence vs tuple rule:

<!--versetest-->
<!-- 61 -->
```verse
Option1 := option{1; 2}?          # Semicolon: sequence, wraps last value
Option1 = 2
Option2 := option{1, 2}?          # Comma: tuple, wraps the tuple
Option2 = (1, 2)
```

In `for` expressions - semicolon typically separates the iteration
clause from filter conditions, while commas separate multiple
conditions. The two cannot be mixed in one clause list: a semicolon
regroups the list, which moves the range out of generator position and
is rejected.

<!--versetest
assert_semantic_error(3552, 3509, 3509):
    MixedClauses()<computes>:void =
        Vals := for (X := 1..3, X <> 2; X <> 3) { X }
-->
<!-- 62 -->
```verse
Odd := for (X := 1..3; X <> 2) { X }    # Semicolon separates iteration from filter
Odd = array{1, 3}
Same := for (X := 1..3, X <> 2) { X }   # Comma means the same thing here
Same = Odd
# for (X := 1..3, X <> 2; X <> 3)       # ERROR: cannot mix separators
```

In `array{}` constructors, you can separate elements with commas **or**
semicolons (but not mixed):

<!--versetest
assert_semantic_error(3547):
    MixedArray61 := array{1, 2; 3}
-->
<!-- 63 -->
```verse
CommaArray := array{1, 2, 3}       # Commas work
SemiArray := array{1; 2; 3}        # Semicolons also work
# MixedArray := array{1, 2; 3}     # ERROR: cannot mix separators
```

### Newlines as Separators

In addition to semicolons and commas, **newlines** can serve as
separators in compound expressions and blocks. Newlines behave like
semicolons - they create sequences:

<!--versetest-->
<!-- 64 -->
```verse
Lines := (
    1
    2
    3
)
Lines = 3        # Same as (1; 2; 3)
```

## Compound and Block Expressions

Compound expressions, delimited by braces, group multiple expressions
into a single expression. The value of a compound expression is the
value of its last sub-expression:

<!--versetest
ComputeIntermediate()<computes>:int=3
CalculateAdjustment(Base:int)<computes>:int=3
-->
<!-- 65 -->
```verse
Result := {
    Temp := ComputeIntermediate()
    Adjustment := CalculateAdjustment(Temp)
    Temp + Adjustment
}
Result = 6
```

Compound expressions create new scopes for variables, allowing local bindings that do not affect the enclosing scope:

<!--versetest-->
<!-- 66 -->
```verse
block:
    X := 10    # Local to this block
    Y := 20
    X + Y
               # X and Y no longer accessible
```

You can separate expressions within a compound using semicolons, commas,
or newlines. Semicolons and newlines create sequences (returning the
last value), while commas create tuples. See [Semicolons vs
Commas](#semicolons-vs-commas) for the complete
rules:

<!--versetest
A:int = 1
B:int = 2
C:int = 3
-->
<!-- 67 -->
```verse
Semi := { A; B; C }   # Semicolon separation (returns C)
Comma := { A, B, C }  # Comma separation (returns tuple (A, B, C))
Lines := {            # Newline separation (returns C)
    A
    B
    C
}
Semi = Lines
Comma = (A, B, C)
```

## Array Expressions

Array expressions create array values using the `array` keyword
followed by elements in braces:

<!--versetest-->
<!-- 68 -->
```verse
NumArray := array{1, 2, 3, 4, 5}
Empty := array{}
Mixed := array{1, "two", 3.0}  # Element type is comparable, their common supertype
```

You can also construct arrays using indented syntax for clarity with
longer lists:

<!--versetest-->
<!-- 69 -->
```verse
Colors := array:
    "red"
    "green"
    "blue"
    "yellow"
```
