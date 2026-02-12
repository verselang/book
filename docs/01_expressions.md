# Expressions

Everything is an expression. This design principle sets Verse apart
from many other languages where statements and expressions are
distinct concepts. Every piece of code you write produces a value,
even constructs you might expect to be purely side-effecting. This
creates a programming model where code can be composed and combined in
ways that feel natural and predictable.

## Primary Expressions

Everything starts with primary expressions—the atomic units from which
more complex expressions are built. These include literals,
identifiers, parenthesized expressions, and the tuple construct that
provides lightweight data aggregation.

### Basic Values

Literals are source code representations of constant values. Verse provides literals for all its primitive types: integers, floats, characters, strings, booleans, and functions. Each literal type has specific syntax rules that determine what values can be expressed and how they're interpreted.

<!--versetest
Point := struct{X:float, Y:float}
Condition:logic = true
-->
<!-- 01 -->
```verse
Result := if (Condition?) then 42 else 3.14  # Integer and float literals
array{1, 2, 3}                               # Integer literals in array construction
Point{X:=0.0, Y:=1.0}                        # Float literals in object construction
```

#### Integer Literals

Integer literals represent whole numbers and can be written in two formats:

*Decimal notation* uses standard digits:

<!--versetest-->
<!-- 02 -->
```verse
Count := 42
Negative := -17
Zero := 0
Large := 9223372036854775807                # Maximum 64-bit signed integer literals
```

*Hexadecimal notation* uses the `0x` prefix followed by hex digits
(0-9, a-f, A-F):

<!--versetest-->
<!-- 03 -->
```verse
Byte := 0xFF
Address := 0x1F4A
LowercaseHex := 0xabcdef
UppercaseHex := 0xABCDEF
```

Integer literals must fit within a 64-bit signed integer range
(`-9223372036854775808` to `9223372036854775807`). At runtime,
integer values are arbitrary precision and can grow past the values
that can be written as literals. However, integers exceeding 64-bit
have limited support (e.g., cannot be used in string interpolation
or persisted).

#### Float Literals

Floating-point literals represent decimal numbers, they must include a
decimal point and in some cases the `f64` suffix.

<!--versetest-->
<!-- 04 -->
```verse
Pi := 3.14159
Half := 0.5
Explicit := 12.34f64    # Explicit bit-depth suffix
```

Scientific notation is used for very large or small numbers using exponents:

<!--versetest-->
<!-- 05 -->
```verse
Large := 1.0e10         # 10,000,000,000 (sign optional)
Small := 1.0e-5         # 0.00001
WithSign := 2.5e+3      # 2,500 (explicit + sign)
Compact := 1.5e2        # 150 (no sign defaults to +)
```

Some rules:

- Must have decimal point: `1.0` is valid, `1` is an integer
- Final decimal point without digits is invalid: `1.` is a syntax error
- All floats are 64-bit (IEEE 754 double precision); the `f64` suffix is optional
- Unary operators work as with integers: `-1.0`, `+1.0`

Float literals must fit within IEEE 754 double-precision range or produce compile-time errors:

<!--versetest-->
<!-- 06 -->
```verse
#TooBig := 1.7976931348623159e+308    # ERROR: Overflow
Maximum := 1.7976931348623158e+308    # OK: Maximum float
```



#### Character Literals

Character literals represent individual text units. Verse has two character types with different literal syntax:

`char` literals represent UTF-8 code units (single bytes, 0-255):

<!--versetest-->
<!-- 07 -->
```verse
LetterA := 'a'          # Printable ASCII character
Space := ' '
Tab := '\t'             # Escape sequence
Hex := 0o61             # Hex notation: 0oXX (97 decimal = 'a')
```

`char32` literals represent Unicode code points:

<!--versetest-->
<!-- 08 -->
```verse
Emoji := '😀'           # Non-ASCII automatically char32
Accented := 'é'
ChineseChar := '好'
HexUnicode := 0u1f600   # Hex notation: 0uXXXXX (😀)
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

Hex notation work as follows:

- `0oXX` for `char` (two hex digits, `0o00` to `0off`)
- `0uXXXXX` for `char32` (up to six hex digits, `0u00000` to `0u10ffff`)

Character literals can not be empty or have multiple characters.

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
Format(D:float, ?Decimals:int):string=""
-->
<!-- 10 -->
```verse
Name := "Alice"
Age := 30

# Simple interpolation
Message := "Hello, {Name}!"                      # "Hello, Alice!"

# Expression interpolation
Info := "Age next year: {Age + 1}"               # "Age next year: 31"

# Function calls
Score := 100
Text := "Score: {ToString(Score)}"               # "Score: 100"

# Function calls with named arguments
Distance := 5.5
Formatted := "Distance: {Format(Distance, ?Decimals:=2)}"
```

Multi-line strings can span multiple lines using interpolation braces for continuation:

<!--versetest-->
<!-- 11 -->
```verse
LongMessage := "This is a multi-line {
}string that continues across {
}multiple lines."
# Result: "This is a multi-line string that continues across multiple lines."

OtherMessage := "Another message{
}    with some empty{
}    spaces."
# Result := "Another message    with some empty    spaces."
```

Empty interpolants are ignored:

<!--versetest-->
<!-- 12 -->
```verse
Text1 := "ab{}cd"        # Same as "abcd"
Text2 := "ab{
}cd"                    # Same as "abcd" (newline ignored)
```

Special rules:

- Curly braces must be escaped: `"\{ \}"` for literal braces
- `string` is an alias for `[]char` (array of UTF-8 code units)
- Strings are sequences of UTF-8 bytes, not Unicode characters
- `"José".Length = 5` (5 bytes, not 4 characters - é takes 2 bytes)

String-array equivalence:

<!--versetest-->
<!-- 13 -->
```verse
Test1 := logic{"abc" = array{'a', 'b', 'c'}}    # True
Test2 := logic{"" = array{}}                    # True
```

Comments in strings are removed:

<!--versetest-->
<!-- 14 -->
```verse
Text1 := "abc<#comment#>def"     # Same as "abcdef"
```

#### Boolean Literals

The `logic` type has two literal values:

<!--versetest-->
<!-- 15 -->
```verse
IsReady := true
IsComplete := false
```

Boolean values are used with the query operator `?` or in comparisons:

<!--versetest
StartGame():void = {}
ShowResults():void = {}
IsReady:logic = true
IsComplete:logic = false
-->
<!-- 16 -->
```verse
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
<!-- 17 -->
```verse
# Converts <decides> expression to logic value
Success := logic{Operation[]}        # true if succeeds, false if fails
HasValue := logic{Optional?}         # true if optional has value
IsEqual := logic{X = Y}              # true if equal, false otherwise
```

The `logic{}` expression requires at least a superficial possibility of failure. Pure expressions without `<decides>` effect cause errors:

<!--versetest-->
<!-- 18 -->
```verse
# ERROR: logic{0} has no decides effect
# ERROR: logic{} is empty
Valid := logic{false?}               # OK: false? can fail
```

Multiple expressions inside `logic{}` can be separated by semicolons or commas (see [Semicolons vs Commas](#semicolons-vs-commas-sequences-and-tuples) for details):

<!--versetest-->
<!-- 19 -->
```verse
Result1 := logic{true?; true?}       # Semicolon separator
Result2 := logic{true?, true?}       # Comma separator
```

#### Path Literals

Path literals identify modules and packages using a hierarchical naming scheme:

<!--NoCompile-->
<!-- 21 -->
```verse
/Verse.org/Verse                    # Standard library path
/YourGame/Player/Inventory          # Custom module path
/user@example.com/MyModule          # Personal namespace
```

Path syntax follows specific rules:

- Starts with `/`
- Contains label (alphanumeric, `.`, `-`)
- Optional version after `@`
- Identifiers must start with letter or `_`

Path literals are covered in detail in the Modules chapter.

### Identifiers and References

Identifiers serve as references to values, whether they're constants,
variables, functions, or types. The language doesn't syntactically
distinguish between these different kinds of identifiers:

<!--NoCompile-->
<!-- 22 -->
```verse
int               # Reference to the int type
GetValue          # Reference to a function
Counter           # Reference to a variable
my_class          # Reference to a class
```

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
<!-- 23 -->
```verse
(A + B) * C       # Group addition before multiplication
if (X > 0 and Y > 0) then Positive else Negative
```

### Tuples

Tuples provide a way to group two or more values with little
ceremony. The syntax distinguishes between parentheses used for
grouping and those used for tuple construction through the presence of
commas:

<!--versetest
X:int = 5
Y:int = 10
-->
<!-- 24 -->
```verse
(X, Y)            # Two-element tuple
(1, "hello", true) # Mixed-type tuple
```

Tuples can be accessed using function-call syntax with a single integer argument:

<!--versetest-->
<!-- 25 -->
```verse
point := (10, 20)
x := point(0)     # Access first element
y := point(1)     # Access second element
```

Tuple types are written:

<!--versetest
GetPoint():tuple(int,int) = (10, 20)
GetData():tuple(int,string,logic) = (42, "hello", true)
<#
-->
<!-- 26 -->
```verse
tuple(int,int)
tuple(int,string,logic)
```
<!-- #> -->

While the type of an unary element can be accepted by the compiler,
`tuple(int)`, there is currently no syntax to write a tuple of one element.

## Postfix Operations

Postfix operations are operations that follow their operand and can be
chained together. This creates a left-to-right reading order that
feels natural and allows for intuitive composition.

### Member Access

The dot operator provides access to members of objects, modules, and
other structured values. Member access expressions evaluate to the
value of the specified member:

<!--NoCompile-->
<!-- 27 -->
```verse
Player.Health           # Access field
Config.MaxPlayers       # Access nested value
math.Sqrt(16.0)         # Access module function
Point.X                 # Access struct field
```
<!-- math.Sqrt may not compile ... I don't really care to fix it. -->

Member access can be chained, creating paths through nested structures:

<!--versetest
item := class{Name:string = "Sword"}
inventory := class{Items:[]item = array{item{}}}
player_type := class{Inventory:inventory = inventory{}}
game := class{Players:[]player_type = array{player_type{}}}
M()<decides>:void =
    Game:game = game{}
    Game.Players[0].Inventory.Items[0].Name
<#
-->
<!-- 28 -->
```verse
Game.Players[0].Inventory.Items[0].Name
```
<!-- #> -->

### Computed Access

Square brackets provide computed access to elements, whether for
arrays, maps, or other indexable structures. The expression within
brackets is evaluated to determine which element to access:

<!--versetest
ComputeIndex():int = 0
M()<decides>:void =
    Array:[]int = array{1, 2, 3}
    Map:[string]int = map{"key" => 42}
    Matrix:[][]int = array{array{1, 2}, array{3, 4}}
    Row:int = 0
    Col:int = 1
    Data:[]int = array{10, 20, 30}
    Array[0]
    Map["key"]
    Matrix[Row][Col]
    Data[ComputeIndex()]
<#
-->
<!-- 29 -->
```verse
Array[0]                # Array indexing
Map["key"]              # Map lookup
Matrix[Row][Col]        # Nested indexing
Data[ComputeIndex()]    # Dynamic index computation
```
<!-- #> -->

The function call syntax with square brackets, `Func[]` is equivalent
to `Func()` for functions that may fail. Array indexing can fail, if
the index is out of bounds, and thus uses `[]`.

### Function Calls

Function calls use parentheses with comma-separated arguments. The
language treats function calls as expressions that evaluate to the
function's return value:

<!--versetest
Sqrt(X:int):float = 4.0
MaxOf(A:int, B:int):int = if (A > B) then A else B
Initialize():void = {}
GetData():int = 42
Transform():int = 10
Process(X:int, Y:int)<decides>:void = {}
M()<decides>:void =
    A:int = 5
    B:int = 10
    Sqrt(16)
    MaxOf(A, B)
    Initialize()
    Process[GetData(), Transform()]
<#
-->
<!-- 30 -->
```verse
Sqrt(16)                        # Single argument
MaxOf(A, B)                     # Multiple arguments
Initialize()                    # No arguments
Process[GetData(), Transform()] # Nested calls, outer call may fail
```
<!-- #> -->

## Object Construction

Object construction uses a distinctive brace syntax to indicates the
creation of a new instance. The syntax requires explicit field
initialization using the `:=` operator:

<!--versetest
point := struct{ X:int, Y:int }
player := struct{Name:string, Level:int, Health:int}
config := struct { MaxPlayers:int, Difficulty:string, EnablePvP:logic }
-->
<!-- 31 -->
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
<!-- 32 -->
```verse
Game := game_state{
    Player := player{
        Position := point{X:=0, Y:=0},
        Inventory := inventory{Capacity:=20}
    },
    Settings := config{Difficulty:="hard"}
}
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
ComputeA():int=1
ComputeB():int=1
X:int = 5
Condition:logic = true
-->
<!-- 33 -->
```verse
Result := if (X > 0) then "positive" else "negative"
Value := if (Condition=true) then ComputeA() else ComputeB()
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
<!-- 34 -->
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
Process(Item:int):void={}
Collection:[]int = array{1, 2, 3}
-->
<!-- 35 -->
```verse
for (Item : Collection) { Process(Item) }
```

An extended form provides access to both index and item--in the case
of a `Map`, indices are not limited to integers:

<!--versetest
Collection:[]int = array{1, 2, 3}
-->
<!-- 36 -->
```verse
for (Index -> Item : Collection) {
    Print("Item at {Index} is {Item}")
}
```

Since for expressions are themseleves expressions, they produce array
values and compose with other expressions. The body of a for
expression is evaluated for each successful iteration, and the
expression as a whole has a value determined by these evaluations.

### Loop

Loop expressions provide indefinite iteration, continuing until
explicitly terminated through failure or other control flow:

<!--versetest
GetNext():int=1
Done(Value:int)<computes><decides>:void={}
Process(Value:int):void={}
M():void=
    loop {
        Value := GetNext()
        if (Done[Value]) then break
        Process(Value)
    }
<#
-->
<!-- 37 -->
```verse
loop {
    Value := GetNext()
    if (Done[Value]) then break
    Process(Value)
}
```
<!-- #> -->

The loop construct can use indented syntax for clarity.

<!-- # TODO What is the value of a loop? -->

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
<!-- 38 -->
```verse
Description := case(Color) {
    color.Red => "Danger",
    color.Yellow => "Warning",
    color.Green => "Safe",
    _ => "Unknown"
}
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
<!-- 39 -->
```verse
X := 42           # Immutable binding
Y := X * 2        # Binding to computed value
Z := W := 10      # Right-associative chaining
```

Assignment operators are right-associative, meaning that `a := b := c`
groups as `a := (b := c)`. This allows for natural chaining of
assignments while maintaining clarity about evaluation order.

Compound assignments provide shorthand for common update patterns:

<!--versetest
F()<transacts>:void=
    var Counter :int = 0
    var Total :int = 0
    Factor:=2
    set Counter += 1
    set Total *= Factor
<#
-->
<!-- 40 -->
```verse
set Counter += 1      # Equivalent to: set Counter = Counter + 1
set Total *= Factor   # Equivalent to: set Total = Total * Factor
```
<!-- #> -->

### Range Expressions

The range operator (`..`) creates integer ranges for iteration in
`for` loops. Ranges are **inclusive on both ends** and can only appear
directly in for loop iteration clauses:

<!--versetest
End()<computes>:int=10
Count:int=10
Start:int=1
Process(I:int):void={}
F():void=
    for (I := 1..10):
        for (J := I..(I+10)):
            for (K:= J..End()) {}
<#
-->
<!-- 41 -->
```verse
1..10             # Range from 1 to 10 (inclusive)
Start..End        # Variable-defined range
for (I := 0..Count):  # Must use := syntax, not :
    Process(I)
```
<!-- #> -->

Ranges are not first-class values. They cannot be stored in variables
or used outside of `for` loop iteration clauses. See the [Range
Operator Restrictions](07_control.md#range-operator-restrictions)
section for details.

### Logical Operations

Logical operators combine boolean values with short-circuit
evaluation. Their result is either success or failure. Verse uses
keyword operators (`and`, `or`, `not`) rather than symbols, improving
readability:

<!--versetest
ProcessQuadrant()<computes>:void = {}
Validated:logic= true
UseDefault()<computes><decides>:void = {}
IsReady()<computes><decides>:void = {}
Wait()<computes>:void = {}
M()<transacts>:void =
    X:int = 5
    Y:int = 10
    if (X > 0 and Y > 0) then ProcessQuadrant()
    Result := logic{Validated? or UseDefault[]}
    if (not IsReady[]) then Wait()
<#
-->
<!-- 42 -->
```verse
if (X > 0 and Y > 0) then ProcessQuadrant()
Result := logic{Validated? or UseDefault[]}
if (not IsReady[]) then Wait()
```
<!-- #> -->

The precedence ensures that `and` binds tighter than `or`, matching
mathematical logic conventions, the `logic{}` expression turns succes
or failure into a value:

<!--NoCompile-->
<!-- 43 -->
```verse
# Evaluates as: (ExpA and ExpB) or (ExpC and ExpD)
Condition := logic{ExpA and ExpB or ExpC and ExpD}
```

### Comparison Operations

Comparison operators also either succeed or fail and can be chained
for range checking:

<!--versetest
InRange():void={}
Value:int = 50
X:int = 75
Minimum:int = 0
Maximum:int = 100
A:int = 5
B:int = 10
-->
<!-- 44 -->
```verse
if (0 <= Value <= 100) then InRange()
IsValid := logic{X > Minimum and X < Maximum}
Same := logic{A = B}
Different := logic{A <> B}
```

All comparison operators have the same precedence and are evaluated
left-to-right, allowing natural mathematical notation for range
checks.

### Arithmetic Operations

Arithmetic operations follow standard mathematical precedence, with
multiplication and division binding tighter than addition and
subtraction:

<!--versetest
A:int = 1
B:int = 2
C:int = 3
-->
<!-- 45 -->
```verse
Result := A + B * C      # Multiplication first
Average := (A + B) / 2   # Parentheses override precedence
```

Unary operators have the highest precedence among arithmetic operations:

<!--versetest
Flag:logic = true
Value:int = 1
X:int = 1
Y:int = 2
-->
<!-- 46 -->
```verse
Negative := -Value
Inverted := logic{not Flag=true}
Result := -X * Y    # Unary minus applies to x only
```

## Set Expressions

While Verse emphasizes immutability, practical programming sometimes
requires mutation. Set expressions provide mutation of variables and
fields:

<!--versetest
c := class { var Field:int = 0 }
GetObj()<transacts>:c = c{}
GetArr()<transacts>:[]int = array{1}
GetMap()<transacts>:[string]string = map{ "hi" => "hp" }
Element:int = 5
Value:int = 100
Index:int = 0
Key:string = "key"
MappedValue:string = "value"
F()<transacts><decides>:void=
    var X:int = 0
    var Obj:c = GetObj()
    var Arr:[]int = GetArr()
    var Map:[string]string = GetMap()
    set X = 10
    set Obj.Field = Value
    set Arr[Index] = Element
    set Map[Key] = MappedValue
<#
-->
<!-- 47 -->
```verse
set X = 10                    # Variable assignment
set Obj.Field = Value         # Field assignment
set Arr[Index] = Element      # Array element assignment
set Map[Key] = MappedValue    # Map entry assignment
```
<!-- #> -->
```

Set expressions are themselves expressions, though they're typically
used for their side effects rather than their value. The left-hand
side must be a valid LValue—something that can be assigned to.

Complex LValues are supported, allowing updates deep within data structures:

<!--versetest
item := class{Name:string = "Item"}
inventory := class{var Items:[]item = array{item{}}}
player := class{var Inventory:inventory = inventory{}}
game := class{var Players:[]player = array{player{}}}
M()<transacts><decides>:void =
    Game:game = game{}
    CurrentPlayer:int = 0
    Slot:int = 0
    NewItem:item = item{}
    set Game.Players[CurrentPlayer].Inventory.Items[Slot] = NewItem
<#
-->
<!-- 48 -->
```verse
set Game.Players[CurrentPlayer].Inventory.Items[Slot] = NewItem
```
<!-- #> -->
```

## Semicolons vs Commas

Verse uses semicolons and commas as separators in various contexts,
but they have fundamentally different semantics in most
situations. Understanding when each is appropriate is essential for
writing correct Verse code.

**Semicolons** create *sequences* - they evaluate expressions in order and return the value of the last expression:

<!--versetest-->
<!-- 49 -->
```verse
Result := (1; 2; 3)     # Evaluates 1, then 2, then 3; returns 3
# Result = 3 (type: int)
```

**Commas** create *tuples* - they group multiple values into a single
composite value:

<!--versetest-->
<!-- 50 -->
```verse
Result := (1, 2, 3)     # Creates a tuple of three elements
# Result = (1, 2, 3) (type: tuple(int, int, int))
```

### Context-Specific Behavior

The semicolon-versus-comma distinction is most visible in
parenthesized expressions:

<!--versetest-->
<!-- 51 -->
```verse
# Semicolon: sequence (returns last value)
X := (0; 1)              # X = 1, type is int

# Comma: tuple (groups values)
Y := (0, 1)              # Y = (0, 1), type is tuple(int, int)
```

This applies to function return values as well:

<!--versetest-->
<!-- 52 -->
```verse
GetInt():int = (1.0; 2)                    # Returns 2 (int)
GetTuple():tuple(float, int) = (1.0, 2)    # Returns (1.0, 2)
```

Semicolons in argument position create a *sequence that executes
before the call*, with only the last value passed as the argument:

<!--versetest
Process(X:int):void={}
LogEvent(S:string):int=1
-->
<!-- 53 -->
```verse
# Semicolon executes side effects, then passes last value
Process(LogEvent("called"); 42)   # Logs "called", then calls Process(42)

# Equivalent to:
LogEvent("called")
Process(42)
```

This pattern enables side effects in argument position:

<!--versetest
MultiplyByTen(X:int):int = X * 10
-->
<!-- 54 -->
```verse
Result := MultiplyByTen(2; 3)     # Evaluates 2 (discards it), calls Multiply(3)
Result = 30
```

Commas separate distinct arguments in the standard way:

<!--versetest
Add(A:int, B:int):int = A + B
F():void=
    Sum := Add(10, 20)
<#
-->
<!-- 55 -->
```verse
Sum := Add(10, 20)                # Two separate arguments
# Sum = 30
```
<!-- #> -->

Semicolons are *not allowed* in parameter lists - you must use commas:

<!--versetest-->
<!-- 56 -->
```verse
# VALID: Comma-separated parameters
ValidFunc(A:int, B:int):void = {}

# INVALID: Semicolon in parameters
# InvalidFunc(A:int; B:int):void = {}
```

### In Specific Scopes

At the top level of a module, semicolons and commas are *interchangeable* - both simply separate definitions:

<!--NoCompile-->
<!-- 57 -->
```verse
# Both valid and equivalent
X:int = 0; Y:int = 0
X:int = 0, Y:int = 0
```

In `logic{}` constructor - both semicolons and commas work, but with
different semantics based on the construct's behavior:

<!--versetest-->
<!-- 58 -->
```verse
# Both evaluate all expressions and return logic value
Result1 := logic{true?; true?}    # Sequence of queries
Result2 := logic{true?, true?}    # Also valid
```

In `option{}` constructor - follows the standard sequence vs tuple rule:

<!--versetest-->
<!-- 59 -->
```verse
# Semicolon: sequence, wraps last value
Option1 := option{1; 2}?          # 2

# Comma: tuple, wraps the tuple
Option2 := option{1, 2}?          # (1, 2)
```

In `for` expressions - semicolon typically separates the iteration clause from filter conditions, while commas separate multiple conditions:

<!--versetest-->
<!-- 60 -->
```verse
# Semicolon separates iteration from filter
for (X := 1..3; X <> 2) { X }

# Comma separates multiple filter conditions
for (X := 1..3, X <> 2) { X }      # Same meaning in this context
```

In `array{}` constructor - use commas to separate elements:

<!--versetest-->
<!-- 61 -->
```verse
Numbers := array{1, 2, 3}          # Array of three elements
```

### Newlines as Separators

In addition to semicolons and commas, **newlines** can serve as
separators in compound expressions and blocks. Newlines behave like
semicolons - they create sequences:

<!--versetest-->
<!-- 62 -->
```verse
# These are equivalent:
Result1 := (1; 2; 3)

Result2 := (
    1
    2
    3
)
# Both return 3
```

## Compound and Block Expressions

Compound expressions, delimited by braces, group multiple expressions
into a single expression. The value of a compound expression is the
value of its last sub-expression:

<!--versetest
ComputeIntermediate():int=3
CalculateAdjustment(o:int):int=3
-->
<!-- 63 -->
```verse
Result := {
    Temp := ComputeIntermediate()
    Adjustment := CalculateAdjustment(Temp)
    Temp + Adjustment
}
```

Compound expressions create new scopes for variables, allowing local bindings that don't affect the enclosing scope:

<!--versetest-->
<!-- 64 -->
```verse
block:
    X := 10    # Local to this block
    Y := 20
    X + Y
               # X and Y no longer accessible
```

Expressions within a compound can be separated by semicolons, commas,
or newlines. Semicolons and newlines create sequences (returning the
last value), while commas create tuples. See [Semicolons vs
Commas](#semicolons-vs-commas-sequences-and-tuples) for the complete
rules:

<!--versetest
A:int = 1
B:int = 2
C:int = 3
M():void =
    X := { A; B; C }
    Y := { A, B, C }
    Z := {
        A
        B
        C
    }
<#
-->
<!-- 65 -->
```verse
{ A; B; C }           # Semicolon separation (returns C)
{ A, B, C }           # Comma separation (returns tuple (A, B, C))
{                     # Newline separation (returns C)
    A
    B
    C
}
```
<!-- #> -->

## Array Expressions

Array expressions create array values using the `array` keyword
followed by elements in braces:

<!--versetest-->
<!-- 66 -->
```verse
Numbers := array{1, 2, 3, 4, 5}
Empty := array{}
Mixed := array{1, "two", 3.0}  # Mixed types if allowed
```

Arrays can also be constructed using indented syntax for clarity with
longer lists:

<!--versetest-->
<!-- 67 -->
```verse
Colors := array:
    "red"
    "green"
    "blue"
    "yellow"
```
