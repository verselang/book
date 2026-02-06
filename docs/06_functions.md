# Functions

Functions are reusable code blocks that perform actions and produce
outputs based on inputs. Think of them as abstractions for behaviors,
much like ordering food from a menu at a restaurant. When you order,
you tell the waiter what you want from the menu, such as
`OrderFood("Ramen")`. You don't need to know how the kitchen prepares
your dish, but you expect to receive food after ordering. This
abstraction is what makes functions powerful - you define the
instructions once and reuse them in different contexts throughout your
code.

<!-- TODO: We say "logic" a lot but we currently don't have it. Should
that be toned down?  My current idea is to have some subsection early
on that will explain the difference between MaxVerse and
ShipVerse. -->

## Parameters

Functions can accept any number of parameters, from none at all to as
many as needed. The syntax follows a straightforward pattern where
each parameter has an identifier and a type, separated by commas:

<!-- 01 -->
```verse
ProcessData(Name:string, Age:int, Score:float):string =
    "{Name} is {Age} years old with a score of {Score}"
```

For functions with many parameters or optional configuration, Verse
supports named and default parameters.

### Named Parameters

Named parameters with defaults make functions more flexible and
ergonomic. They allow you to:

- Specify arguments by name rather than position
- Provide default values for optional parameters
- Call functions with only the arguments you need
- Add new optional parameters without breaking existing code

Named parameters are declared with a `?` prefix and called with the
name and a `:=` followed by a value:

<!--versetest-->
<!-- 02 -->
```verse
# A function with named parameters
Greet(?Name:string, ?Greeting:string):string = "{Greeting} {Name}!"

# A call with named arguments 
Greet(?Name := "Alice", ?Greeting := "Hello") 
```

Named parameters with default values are truly optional:

<!--versetest-->
<!-- 03 -->
```verse
# Named parameters with defaults
Log(Message:string, ?Level:int=1, ?Color:string="white"):string =
    "[Level {Level}] {Message} ({Color})"

# Call with all defaults
Log("Starting")                          # Returns "[Level 1] Starting (white)"

# Call with some arguments
Log("Warning", ?Level:=2)                # Returns "[Level 2] Warning (white)"

# Call with arguments in any order
Log("Error", ?Color:="red", ?Level:= 3)  # Returns "[Level 3] Error (red)"
```

After the first named parameter, all subsequent parameters must also be named:

<!--NoCompile-->
<!-- 04 -->
```verse
Invalid: named followed by positional
Invalid(? Named:int, Positional:string):void = {}  # ERROR
```

When calling functions with named parameters, you must use the
`?Name:=Value` syntax. All parameters without default must be specified.
Positional arguments come first:

<!--NoCompile-->
<!-- 07 -->
```verse
Configure(Required:int, ?Option1:string, ?Option2:logic):void = { }

# Valid
Configure(42, ?Option1:="test", ?Option2:=true)

# Invalid: named arg before positional
# Configure(?Option1:="test", 42, ?Option2:=true)  # ERROR
```

Default values are evaluated in the function's defining scope; they
can reference:

  - Module-level definitions
  - Class or interface members
  - Earlier parameters

<!--NoCompile-->
<!-- 09 -->
```verse
# Module-level definition
ModuleTimeout:int = 30

# Access module-level definition
Connect(?Host:string, ?Timeout:int = ModuleTimeout):void =...

# Access member definition
game_config := class:
    DefaultLives:int = 3

    StartGame(?Lives:int = DefaultLives):void =...

# Access earlier parameter
CreateRange(?Start:int, ?End:int = Start + 10):[]int =...
```

Default values work with overridden members in class hierarchies:

<!--NoCompile-->
<!-- 13 -->
```verse
base_game := class:
    DefaultSpeed:float = 1.0

    Move(?Speed:float = DefaultSpeed):void =...
    # Uses DefaultSpeed from current instance

fast_game := class(base_game):
    DefaultSpeed<override>:float = 2.0

base_game{}.Move()         # Uses 1.0   
fast_game{}.Move()         # Uses 2.0 (overridden value)
```

Named and default parameters interact with the type system.  A
function with default parameters is a subtype of the same function
without those parameters:

<!--versetest-->
<!-- 14 -->
```verse
Process(?Required:int, ?Optional:int = 0):int = Required + Optional

# Can assign to type without optional parameter
F1:type{_(?Required:int):int} = Process
F1(?Required := 5)                          # Returns 5 (uses default)

# Can assign to type with optional parameter
F2:type{_(?Required:int, ?Optional:int):int} = Process
F2(?Required := 5, ?Optional := 3)          # Returns 8

# Can even assign to type with no parameters (all have defaults)
DefaultAll(?A:int = 1, ?B:int = 2):int = A + B
F3:type{_():int} = DefaultAll
F3()                                        # Returns 3
```

Function types preserve named parameter names:

<!--versetest-->
<!-- 15 -->
```verse
Calculate(?Amount:float, ?Rate:float):float = Amount * Rate

# Valid: names match
F1:type{_(?Amount:float, ?Rate:float):float} = Calculate

# Invalid: different names
# F2:type{_(?Value:float, ?Factor:float):float} = Calculate  # ERROR
```

Function types do not include default values:

<!--versetest-->
<!-- 16 -->
```verse
F1(?X:int=1):int = X

F2:type{_(?X:int=99):int} = F1    # F1 and F2 are of the same type
```

Named parameters participate in function overload resolution:

<!--versetest-->
<!-- 17 -->
```verse
Process(Value:int):string = "One parameter"
Process(Value:int, ?Option:string):string = "Two parameters"
Process(Value:int, ?Option1:string, ?Option2:logic):string = "Three parameters"

Process(42)                                        # Calls first overload
Process(42, ?Option := "test")                     # Calls second overload
Process(42, ?Option1 := "test", ?Option2 := true)  # Calls third overload
```

The compiler selects the overload that matches the provided
arguments. Named parameters make overload resolution more precise
since names must match exactly.

Named parameters have specific rules for *overload distinctness* that
differ from positional parameters. Two function signatures are
considered **indistinct** (cannot overload) if they could be called
with the same arguments.

**Order doesn't matter for named parameters:** Named parameters are
matched by name, not position, so reordering doesn't create
distinctness:

<!--NoCompile-->
<!-- 18 -->
```verse
# Not distinct - same parameters, different order
F(?Y:int, ?X:int):int = X + Y
F(?X:int, ?Y:int):int = X - Y  # ERROR
```

**Defaults don't create distinctness:** The presence or absence of
default values doesn't make signatures distinct if the parameter names
are the same:

<!--NoCompile-->
<!-- 19 -->
```verse
# Same parameter name with/without default
F(?X:int=42):int = X
F(?X:int):int = X  # ERROR
```

**The all-defaults rule:** If all parameters in both overloads have
default values, the signatures are indistinct because both can be
called with no arguments:

<!--NoCompile-->
<!-- 20 -->
```verse
# ERROR Both can be called as F()
# F(?X:int=42):int = X
# F(?Y:int=42):int = Y         # ERROR

# ERROR Both callable with no args
# F(?X:int=42):int = X
# F(?X:float=3.14):float = X  # ERROR
```

**Different parameter names are distinct:** Functions with different
named parameter names can overload:

<!--versetest-->
<!-- 22 -->
```verse
# Valid: Different names
F(?X:int):int = X
F(?Y:int):int = Y  # OK - distinct parameter names
```

**Named vs positional parameters are distinct:** A named parameter is
distinct from a positional parameter, even with the same name and
type:

<!--versetest-->
<!-- 23 -->
```verse
# Valid: Named vs positional
F(?X:int):int = X
F(X:int):int = X  # OK
```

**At least one required parameter must differ:** If the set of
required (no default) named parameters differs, the overloads are
distinct:

<!--versetest-->
<!-- 24 -->
```verse
# Valid: First requires ?Y, second doesn't
F(?Y:int, ?X:int=42):int = X
F(?X:int):int = X  # OK - different required parameter set
```

**Positional parameters create distinctness:** Different positional
parameter types make signatures distinct, even if named parameters are
the same:

<!-- 25 -->
```verse
# Valid: Different positional parameter types
F(Arg:float, ?X:int):int = X
F(Arg:int, ?X:int):int = X  # OK
```

**Superset of calls:** If one signature can handle all the calls that
another can, they're indistinct:

<!--NoCompile-->
<!-- 26 -->
```verse
# ERROR 3532: First can handle all calls to second
# F(?Y:int=42, ?X:int=42):int = X
# F(?X:int):int = X  # ERROR - can call first as F(?X := 10)
```

### Tuple as Arguments

Tuples can be used to provide positional arguments. However, you
cannot mix a pre-constructed tuple variable with additional named
arguments:

<!--versetest-->
<!-- 28 -->
```verse
Calculate(A:int, B:int, ?C:int = 0):int = A + B + C

# Valid: tuple provides positional arguments
Args:tuple(int, int) = (1, 2)
Calculate(Args)  # Returns 3

# Valid: all arguments provided directly
Calculate(1, 2, ?C := 5)  # Returns 8

# Invalid: cannot mix tuple variable with named arguments
# Calculate(Args, ?C := 5)  # ERROR
```

Functions can destructure tuple parameters directly in the parameter
list, allowing you to extract tuple elements inline without manual
indexing:

<!--versetest-->
<!-- 29 -->
```verse
# Destructure tuple parameter in place
Func(A:int, (B:int, C:int), D:int):int =
    A + B + C + D

Func(1, (2, 3), 4)        # Direct tuple literal - returns 10
X := (2, 3)
Func(1, X, 4)             # Tuple variable - returns 10
Y := (1, (2, 3), 4)
Func(Y)                   # Entire argument list as tuple - returns 10
```

The parameter `(B:int, C:int)` destructures the tuple, giving direct
access to `B` and `C` instead of requiring `Tuple(0)` and `Tuple(1)`
indexing.

Tuples can be destructured to arbitrary depth:

<!--versetest-->
<!-- 30 -->
```verse
# Simple nesting
H(A:int, (B:int, (C:int, D:int)), E:int):int =
    A + B + C + D + E

H(1, (2, (3, 4)), 5)              # Returns 15
T := (2, (3, 4))
H(1, T, 5)                        # Returns 15
T2 := (1, (2, (3, 4)), 5)
H(T2)                             # Returns 15
```

You can mix destructured tuple parameters with regular tuple
parameters that aren't destructured:

<!--versetest-->
<!-- 31 -->
```verse
# Destructured form - access elements directly
F(A:int, (B:int, C:int), D:int):int =
    A + B + C + D

# Non-destructured form - use tuple indexing
G(A:int, T:tuple(int, int), D:int):int =
    A + T(0) + T(1) + D

# Both work identically
F(1, (2, 3), 4)  # Returns 10
G(1, (2, 3), 4)  # Returns 10
```

Choose destructured form when you need direct access to individual
elements, and non-destructured when you need to pass the tuple as a
whole to other functions.

Tuple parameters can contain named/optional parameters, allowing for
flexible APIs that combine structural decomposition with optional
values:

<!--versetest-->
<!-- 32 -->
```verse
# Named parameter inside nested tuple
SumValues(A:int, (X:int, (Y:int, (?Z:int = 0)))):int =
    A + X + Y + Z

# Can provide Z explicitly
SumValues(1, (2, (3, (?Z := 4))))  # Returns 10

# Can omit Z to use default
SumValues((1, (2, (3))))           # Returns 6
```

A tuple can contain multiple named parameters, and they can be
specified in any order:

<!--versetest-->
<!-- 33 -->
```verse
ProcessData(Base:int, (Items:[]int, ?Scale:int = 1, ?Offset:int = 0)):int =
    if (First := Items[0]):
        First * Scale + Offset + Base
    else:
        Base

Data := array{100, 200}

ProcessData(10, Data)                              # Uses defaults: 110
ProcessData(10, (Data, ?Scale := 2))               # 210
ProcessData(10, (Data, ?Offset := 5))              # 115
ProcessData(10, (Data, ?Scale := 2, ?Offset := 5)) # 215
ProcessData(10, (Data, ?Offset := 5, ?Scale := 2)) # 215 (order doesn't matter)
```

When a tuple parameter contains **only** named parameters (no
positional parameters), you must provide an empty tuple `()` even when
using all defaults:

<!--versetest-->
<!-- 34 -->
```verse
# Tuple with only named parameters
Configure(Base:int, (?Width:int = 10, ?Height:int = 20)):int =
    Base + Width + Height

# Must provide empty tuple when using all defaults
Configure(5, ())  # Returns 35

# Cannot omit the tuple entirely
# Configure(5)  # ERROR - tuple parameter required
```

This is a known limitation in the current implementation. When the
tuple contains at least one positional parameter, this restriction
doesn't apply.

Refined types with `where` clauses are not allowed in destructured
tuple parameters:

<!-- 35 -->
```verse
# ERROR 3624: Refined types not supported in tuple destructuring
# H(A:int, ((B:int where B > 0), C:int), D:int):int =
#     A + B + C + D
```

This restriction applies to the types within the tuple
destructuring. Regular parameter refinements outside tuples work
normally.

### Flattening and Unflattening

Verse provides automatic conversion between tuples and multiple
arguments at function call sites, enabling flexible calling
conventions without explicit packing or unpacking.

*Flattening:* A function expecting multiple parameters can be called
with a single tuple. In the following, the tuple `Args` is
automatically unpacked into the `Add` function's parameters:

<!--versetest-->
<!-- 36 -->
```verse
Add(X:int, Y:int):int= X + Y
Args:= (3, 5)
Add(Args)       # Returns 8 - tuple automatically flattened
```

*Unflattening:* A function expecting a single tuple parameter can be
called with flattened arguments.  The individual arguments of the call
to `F` are automatically packed into the tuple parameter:

<!--versetest-->
<!-- 37 -->
```verse
F(P:tuple(int, int)):int = P(0) + P(1)

F(3, 5)  # Returns 8 - args automatically packed into tuple
```

The empty tuple has the same flattening behavior:

<!--versetest-->
<!-- 39 -->
```verse
F(X:tuple()):int = 42

F(())   # Explicit empty tuple
F()     # No arguments - automatically creates empty tuple
```

### Evaluation Order

Arguments are evaluated in a specific order to maintain predictable behavior:

1. *Positional arguments*: Left to right in the call
2. *Named arguments*: Left to right as encountered in the call
3. *Default values*: Filled in for omitted parameters, left to right
   in parameter order

If named arguments appear in a different order than parameters, the
compiler uses temporary variables to preserve the evaluation order you
specified:

<!--versetest-->
<!-- 40 -->
```verse
Process(A:int, ?B:int, ?C:int, ?D:int):string =
    "{A}, {B}, {C}, {D}"

# Call with reordered named args
Process(1, ?D := 4, ?B := 2, ?C := 3)

# Evaluation order: 1, 4, 2, 3 (as written)
# But passed to function in parameter order: 1, 2, 3, 4
```

This ensures that side effects in argument expressions happen in the
order you write them, not in parameter order.

## Extension Methods

Extension methods allow you to add new methods to existing types
without modifying their original definitions. This powerful feature
enables you to extend any type in Verse—including built-in types like
`int`, `string`, arrays, and maps—with custom functionality while
maintaining clean separation between different concerns.

Extension methods are particularly valuable when:

- You want to add domain-specific operations to built-in types
- You need to extend types from libraries you don't control
- You're building fluent or builder-style APIs
- You want to organize related functionality separately from type definitions

Extension methods use a special syntax where the extended type appears
in parentheses before the method name:

<!--versetest-->
<!-- 41 -->
```verse
# Extend int with a custom method
(Value:int).Double()<computes>:int = Value * 2

# Call the extension method using dot notation
X := 5
Y := X.Double()  # Returns 10

# Can also call on literals
Z := 7.Double()  # Returns 14
```

The type in parentheses can be any Verse type: primitives, tuples,
classes, interfaces, arrays, maps, or structs.

Extending primitives:

<!--versetest-->
<!-- 42 -->
```verse
(N:int).IsEven()<decides>:void = N = 0 or Mod[N,2] = 0
(S:string).FirstChar()<decides>:char = S[0]

42.IsEven[]           # Returns true
"Hello".FirstChar[]   # Returns 'H'
```

Extending tuples:

<!--versetest-->
<!-- 43 -->
```verse
# Extend a specific tuple type (Note: Sqrt is <reads>)
(Point:tuple(int, int)).Distance()<reads>:float =
    Sqrt( (Point(0) * Point(0) + Point(1) * Point(1)) * 1.0)

(3, 4).Distance()  # Returns 5.0
```

Extending arrays:

<!--versetest-->
<!-- 44 -->
```verse
(Numbers:[]int).Sum()<transacts>:int =
    var Total:int = 0
    for (N:Numbers):
        set Total += N
    Total

array{1, 2, 3, 4, 5}.Sum()  # Returns 15
```

Extending maps:

<!--versetest-->
<!-- 45 -->
```verse
(M:[int]string).Keys()<computes>:[]int =
    for (Key->X:M):
        Key

map{1=>"a", 2=>"b", 3=>"c"}.Keys()  # Returns array{1, 2, 3}
```

Extending classes:

<!--verse-->
<!--246-->
```verse
player := class:
    Name:string
    var Score:int
```
<!-- -->

<!--versetest
player := class:
    Name:string
    var Score:int
-->
<!-- 46 -->
```verse
# Add method to existing class
(P:player).AddScore(Points:int):void =
    set P.Score += Points

Player1 := player{Name := "Alice", Score := 100}
Player1.AddScore(50)  # Score becomes 150
```

Extension methods support all parameter features including named and
default parameters:


<!--NoCompile-->
<!-- 47 -->
```verse
#(Text:string).Pad(?Left:int = 0, ?Right:int = 0):string = ...

"Hello".Pad(?Left:=5)               # "     Hello"
"Hello".Pad(?Right:=5)              # "Hello     "
"Hello".Pad(?Left:= 2, ?Right:=3)   # "  Hello   "
```

<!-- the above should compile it is a bug. TODO: report it.-->

### Overloading

You can define multiple extension methods with the same name for
different types:

<!--versetest-->
<!-- 48 -->
```verse
# Overloaded Extension method for different types
(N:int).Format():string = "int:{N}"
(B:logic).Format():string = if (B?) {"logic:true"} else {"logic:false"}

42.Format()      # Returns "int:42"
true.Format()    # Returns "logic:true"
```

The compiler selects the appropriate overload based on the receiver type.

### On the Empty Tuple

The empty tuple `tuple()` represents the unit type and can have
extension methods:

<!--versetest-->
<!-- 49 -->
```verse
(Unit:tuple()).GetMagicNumber():int = 42

().GetMagicNumber()  # Returns 42
```

This can be useful for creating namespace-like groupings of functions.

### Rules

**Must be called**: Extension methods cannot be referenced as
first-class values without calling them:

<!--versetest-->
<!-- 50 -->
```verse
(N:int).Double():int = N * 2

# Valid: calling the method
X := 5.Double()

# Invalid: referencing without calling
# F := 5.Double  # ERROR
```

**Conflicts with Class Methods:** Extension methods cannot have the
same signature as methods defined directly in classes or interfaces:

<!-- 51 -->
```verse
player := class:
    Health():int = 100

# Invalid: Conflicts with class method
# (P:player).Health():int = 50  # ERROR
```

This prevents ambiguity and ensures that class methods always take precedence.

**Scope and Visibility:** Extension methods are scoped like regular
functions. They're only visible where they're defined or imported:

<!--NoCompile-->
<!-- 52 -->
```verse
# In module A
utils := module:
    (S:string).Reverse<public>():string =
        # Implementation

# In module B
using { utils }

"Hello".Reverse()  # Available after importing
```

**Extension Methods in Class Scope:** Extension methods can be defined
inside classes and access class members:

<!--versetest
game_manager := class:
    Multiplier:int = 10

    (Score:int).ScaledScore()<computes>:int =
        Score * Multiplier  # Accesses class field

    ProcessScore(Value:int)<computes>:int =
        Value.ScaledScore()  # Uses extension method

M()<transacts>:void={
GM := game_manager{}
GM.ProcessScore(5)  # Returns 50
}
<# 
-->
<!-- 53 -->
```verse
game_manager := class:
    Multiplier:int = 10

    (Score:int).ScaledScore()<computes>:int =
        Score * Multiplier  # Accesses class field

    ProcessScore(Value:int)<computes>:int =
        Value.ScaledScore()  # Uses extension method

GM := game_manager{}
GM.ProcessScore(5)  # Returns 50
```
<!-- #> -->

This creates a lexical closure where the extension method can
reference the enclosing class's members.

**Tuple Argument Conversion:** When an extension method has multiple parameters, you can pass a tuple to provide all arguments at once:

<!--verse
point := class<allocates>:
    X:int
    Y:int

(P:point).Translate(DX:int, DY:int)<allocates>:point =
    point{X := P.X + DX, Y := P.Y + DY}

M()<transacts>:void={
Origin := point{X := 0, Y := 0}
Delta := (5, 10)
NewPoint := Origin.Translate(Delta)  # Tuple expands to two arguments
} <#
-->
<!-- 54 -->
```verse
point := class:
    X:int
    Y:int

(P:point).Translate(DX:int, DY:int)<allocates>:point =
    point{X := P.X + DX, Y := P.Y + DY}

Origin := point{X := 0, Y := 0}
Delta := (5, 10)
NewPoint := Origin.Translate(Delta)  # Tuple expands to two arguments
```
<!-- #> -->

This works when the tuple type matches the parameter list.

## Lambdas

**Note:** Lambda expressions with the `=>` operator are not yet
supported in the current version of Verse. For creating function
values and closures, use nested functions instead (see the Nested
Functions section below).

Functions are first-class values; they can be stored in variables,
passed as parameters, and returned from other functions. This enables
powerful functional programming patterns including higher-order
functions, callbacks, and composable operations. Currently, these
capabilities are provided through nested functions rather than lambda
expressions.

### Types, Variance and Effects

Function types follow specific subtyping rules based on *variance*:

- *Parameters are contravariant*: A function accepting more general
  types can substitute for one accepting specific types.

- *Returns are covariant*: A function returning more specific types
  can substitute for one returning general types.

<!--verse-->
<!--264-->
```verse
animal := class:
    Name:string

dog := class(animal):
    Breed:string
```
<!-- -->

<!--versetest
animal := class:
    Name:string

dog := class(animal):
    Breed:string
-->
<!-- 64 -->
```verse 
# Functions with different parameter/return types
F1(X:animal):dog = dog{Name := X.Name, Breed := "Unknown"}
F2(X:dog):animal = X     # Returns supertype
F3(X:dog):dog = X

# Function type accepting dog, returning animal
var ProcessDog:type{_(:dog):animal} = F1  #############TODO

# Valid: F1 accepts animal (more general), returns dog (more specific)
set ProcessDog = F1  # OK: tuple(animal)->dog <: tuple(dog)->animal

# Valid: F3 accepts dog, returns dog (more specific than animal)
set ProcessDog = F3  # OK: tuple(dog)->dog <: tuple(dog)->animal

# Invalid: F2 returns animal but parameter is not contravariant enough
# ProcessDog = F2  # ERROR: tuple(dog)->animal </: tuple(dog)->animal
#                  # (same parameters, same return - no variance issue here)
```

Effects are part of the function type. A function with fewer effects
can be used where a function with more effects is expected - effects
are **covariant** (fewer effects = subtype):

<!--versetest
using{/Verse.org/Concurrency}
-->
<!-- 65 -->
```verse
Pure():int = 42
Transactional()<transacts>:int = 42
Suspendable()<suspends>:int = 42

# Functions expecting specific effects
UsePure(F():int):int = F()
UseTransactional(F()<transacts>:int):int = F()
UseSuspendable(F()<suspends>:int):task(int) = spawn{ F() }

UsePure(Pure)                    # OK
UseTransactional(Transactional)  # OK
UseSuspendable(Suspendable)      # OK

# Covariance: fewer effects can substitute for more effects
UseTransactional(Pure)           # OK: ():int <: ()<transacts>:int

# Invalid: more effects cannot substitute for fewer
# UsePure(Transactional)         # ERROR: ()<transacts>:int </: ():int
```

A `<computes>` function can be passed where `<transacts>` is expected
because fewer effects means the function is more constrained.

When you assign different functions conditionally, Verse finds the
least upper bound (join) of their types:

<!--versetest
base := class:
    Value:int

derived := class(base):
    Extra:string
-->	
<!-- 66 -->
```verse
# Assume the following:
# base := class{Value:int}
# derived := class(base){Extra:string}

F1():base = base{Value:=1}
F2():derived = derived{Value:=2, Extra:="test"}

# Join: ()->base (common supertype)
G := if(true?) {F1} else {F2}
G().Value  # Can access base members
```


### Using `type{}`

The `type{_(...):...}` syntax declares function types with full
detail. This is the mechanism for creating function type signatures
that include parameter types, return types, and effects. Underscore
`_` is a placeholder for the function name, emphasizing that it
describes a signature, not a specific function:

<!--versetest-->
<!-- 72 -->
```verse
# Function type variable
var Handler:?type{_(:string, :int)<decides>:void} = false

# Nested function matching the signature
MakeHandler(Name:string, Count:int)<decides>:void =
    Print("{Name}: {Count}")
    Count > 0  # Decides effect

set Handler = option{MakeHandler}

# Function accepting function parameter
Process(F:type{_(:int):int}, Value:int):int =
    F(Value)

# Nested function to pass
Double(X:int):int = X * 2
Process(Double, 5)  # Returns 10
```

The `type{}` construct *exclusively declares function type signatures*. It cannot be used for general type expressions or to extract types from values:

<!--verse
m:= module:
-->
<!-- 73 -->
```verse
ValidType1 := type{_():int}
ValidType2 := type{_(:string, :int):float}
ValidType3 := type{_()<transacts><decides>:void}
```

Within `type{}`, function declarations must have return types but
*cannot have bodies*.

Function types work as field types in classes:

<!--versetest

calculator := class:
    Operation:type{_(:int,:int):int}

-->
<!-- 74 -->
```verse
# Assume:
# calculator := class:
#    Operation:type{_(:int,:int):int}

Add(X:int, Y:int):int = X + Y
Multiply(X:int, Y:int):int = X * Y

# Create instances with different operations
Adder := calculator{Operation := Add}
Multiplier := calculator{Operation := Multiply}

Adder.Operation(5, 3)      # Returns 8
Multiplier.Operation(5, 3) # Returns 15
```

Function types can be used for local variables, enabling conditional
function selection:

<!--versetest-->
<!-- 75 -->
```verse
ProcessA():int = 10
ProcessB():int = 20

SelectFunction(UseA:logic):int =
    # Choose function based on condition
    Fn:type{_():int} =
        if (UseA?):
            ProcessA
        else:
            ProcessB
    Fn()

SelectFunction(true)   # Returns 10
SelectFunction(false)  # Returns 20
```

Combine `type{}` with `?` to create optional function types:

<!--versetest-->
<!-- 76 -->
```verse
DefaultHandler()<computes>:int = -1
CustomHandler()<computes>:int = 42

Process(Handler:?type{_()<computes>:int})<computes><decides>:int =
    # Use handler if provided, otherwise use default
    Handler?() or DefaultHandler()

Process[false]                   # Returns -1 (no handler)
Process[option{CustomHandler}]   # Returns 42 (custom handler)
```

Create arrays of functions sharing the same signature:

<!--versetest-->
<!-- 77 -->
```verse
GetZero():int = 0
GetOne():int = 1
GetTwo():int = 2

SumFunctions(Functions:[]type{_():int}):int =
    var Result:int = 0
    for (Fn : Functions):
        set Result += Fn()
    Result

SumFunctions(array{GetZero, GetOne, GetTwo})  # Returns 3
```

### Examples

**Map-Filter-Reduce**:

<!--versetest-->
<!-- 78 -->
```verse
# Generic map
Map(Items:[]t, F(:t)<transacts>:u where t:type, u:type)<transacts>:[]u =
    for (Item:Items):
        F(Item)

# Generic filter
Filter(Items:[]t, Pred(:t)<computes><decides>:void where t:type)<computes>:[]t =
    for (Item:Items, Pred[Item]):
        Item

# Generic fold/reduce
Fold(Items:[]t, Initial:u, F(:u, :t)<transacts>:u where t:type, u:type)<transacts>:u =
    var Acc:u = Initial
    for (Item:Items):
        set Acc = F(Acc, Item)
    Acc

# Usage with nested functions
Numbers := array{1, 2, 3, 4, 5}

# Define nested functions for operations
Square(X:int)<computes>:int = X * X
IsEven(X:int)<computes><decides>:void = X = 0 or Mod[X,2] = 0
AddTo(Acc:int, X:int)<computes>:int = Acc + X

Squared := Map(Numbers, Square)
Evens := Filter(Numbers, IsEven)
Sum := Fold(Numbers, 0, AddTo)
```

**Function composition**:

<!--versetest-->
<!-- 79 -->
```verse
Compose(F(:b):c, G(:a):b where a:type, b:type, c:type):type{_(:a):c} =
    # Return a nested function that composes F and G
    Composed(X:a):c = F(G(X))
    Composed

Add1(X:int):int = X + 1
Double(X:int):int = X * 2

# Compose: first doubles, then adds 1
DoubleThenIncrement := Compose(Add1, Double)
DoubleThenIncrement(5)  # Returns 11 (5*2 + 1)
```

**Partial application**:

<!--versetest-->
<!-- 80 -->
```verse
Partial(F(:a, :b):c, X:a where a:type, b:type, c:type):type{_(:b):c} =
    # Return a nested function with X captured
    PartialFunc(Y:b):c = F(X, Y)
    PartialFunc

Add(X:int, Y:int):int = X + Y
Add5 := Partial(Add, 5)
Add5(3)  # Returns 8
```

## Nested Functions

!!! warning "Unreleased Feature"
    Nested functions have not yet been released. This section documents planned functionality that is not currently available.

Nested functions (also called local functions) are functions defined
inside other functions. They provide encapsulation, enable closures
over local variables, and help organize complex logic within a
function's scope. Nested functions have names, can be recursive, and
are the primary way to create function values and closures in Verse.

A nested function is declared just like a top-level function, but
inside another function's body:

<!--versetest-->
<!-- 81 -->
```verse
Outer(X:int):int =
    # Nested function definition
    Inner(Y:int):int = Y * 2

    # Call nested function
    Inner(X)

Outer(5)  # Returns 10
```

Nested functions are only visible within their enclosing function's
scope. They cannot be accessed from outside.

Nested functions capture (close over) variables from any enclosing
scope, creating powerful closures:

<!--versetest-->
<!-- 82 -->
```verse
MakeGreeter(Name:string):type{_():string} =
    # Greeting captures Name from outer scope
    Greeting():string = "Hello, {Name}!"

    # Return the nested function
    Greeting

SayHello := MakeGreeter("Alice")
SayHello()  # Returns "Hello, Alice!"

SayHi := MakeGreeter("Bob")
SayHi()  # Returns "Hello, Bob!"
```

Each call to `MakeGreeter` creates a new closure with its own captured
`Name` value.

Nested functions support overloading by parameter types:

<!--versetest-->
<!-- 83 -->
```verse
Process(X:int):string =
    # Overloaded nested functions
    Format(Value:int):string = "int: {Value}"
    Format(Value:float):string = "float: {Value}"

    # Calls appropriate overload
    IntResult := Format(42)       # Calls int version
    FloatResult := Format(3.14)   # Calls float version

    "{IntResult}, {FloatResult}"

Process(1)  # Returns "Int: 42, Float: 3.14"
```

Overload resolution works the same as for top-level functions.

### Closures with State

Nested functions can capture `var` variables and mutate them, creating stateful closures:

<!--versetest-->
<!-- 84 -->
```verse
MakeCounter(Initial:int):tuple(type{_():int}, type{_():void}) =
    var Count:int = Initial

    # Getter captures Count
    GetCount():int = Count

    # Incrementer mutates captured Count
    Increment():void = set Count = Count + 1

    (GetCount, Increment)

Counter := MakeCounter(0)
GetValue := Counter(0)
IncrementValue := Counter(1)

GetValue()        # Returns 0
IncrementValue()  # Increments count
GetValue()        # Returns 1
IncrementValue()  # Increments count
GetValue()        # Returns 2
```

This pattern creates a closure that maintains private mutable state.

### Restrictions

Nested functions have several important restrictions that distinguish
them from top-level functions:

- Nested functions **cannot** have access specifiers like `<public>`,
  `<internal>`, or `<private>`:
- Nested functions are always private to their enclosing function.
- You cannot define classes inside functions (nested or otherwise):

<!--NoCompile-->
<!-- 86 -->
```verse
# ERROR: Cannot define classes in local scope
F():void =
    my_class := class {}  # ERROR

# Correct: Define classes at module level
my_class := class {}

F():void =
    Instance := my_class{}  # OK - can use class
```

- Nested functions cannot reference variables or other nested
  functions defined later in the same scope (this also means mutually
  recursive nested functions are not allowed):

<!--NoCompile-->
<!-- 87 -->
```verse
# ERROR 3506: G used before defined
F():void =
    X := G()     # ERROR: G not yet defined
    G():int = 42

# Correct: Define before use
F():void =
    G():int = 42
    X := G()     # OK: G is defined
```

- The `(super:)` syntax for calling parent class methods **cannot** be used in nested functions:

<!--NoCompile-->
<!-- 88 -->
```verse
# ERROR 3612: super not allowed in nested function
base_class := class:
    F(X:int):int = X

derived_class := class(base_class):
    F<override>(X:int):int =
        G():int =
            (super:)F(X)  # ERROR: super not allowed here
        G()

# Correct: Use super directly in the overriding method
derived_class := class(base_class):
    F<override>(X:int):int =
        BaseResult := (super:)F(X)  # OK
        G():int = BaseResult * 2
        G()
```

## Parametric Functions

Parametric functions (also called generic functions) allow you to
write code that works with multiple types while maintaining complete
type safety. Rather than writing separate functions for each type, you
define a single function with type parameters that adapt to whatever
types you use them with.

A parametric function declares type parameters using a `where` clause
that specifies constraints on those types:

<!--versetest-->
<!-- 89 -->
```verse
# Simple identity function - works with any type
Identity(X:t where t:type):t = X
# Usage - type parameter inferred automatically
Identity(42)        # t inferred as int, returns 42
Identity("hello")   # t inferred as string, returns "hello"
```

The `where t:type` clause declares `t` as a type parameter with the constraint `type`, meaning it can be any Verse type. The function signature `(X:t):t` means "takes a value of type `t` and returns a value of that same type `t`."

<!--NoCompile-->
<!-- 90 -->
```verse
FunctionName(Parameters where TypeParameter:Constraint, ...):ReturnType = Body
```

- *Type parameters* appear in the `where` clause
- *Constraints* specify requirements (e.g., `type`, `subtype(comparable)`)
- *Multiple type parameters* are comma-separated in the `where` clause

Verse automatically infers type parameters from the arguments you
pass, eliminating the need for explicit type annotations in most
cases:

<!--versetest-->
<!-- 91 -->
```verse
# Function with two type par qameters
Pair(X:t, Y:u where t:type, u:type):tuple(t, u) = (X, Y)

# All type parameters inferred
Pair(1, "one")        # t = int, u = string, returns (1, "one")
Pair(true, 3.14)      # t = logic, u = float, returns (true, 3.14)
```

Inference with collections:

<!--versetest-->
<!-- 92 -->
```verse
# Generic first element function
First(Items:[]t where t:type)<decides>:t = Items[0]

Numbers := array{1, 2, 3}
Result :int= First[Numbers]  # t inferred as int from []int
```

When you pass multiple values to a parametric function expecting a single type parameter, Verse can infer either a tuple or an array:

<!--versetest-->
<!-- 93 -->
```verse
# Returns the argument unchanged
Identity(X:t where t:type):t = X

# Passing multiple values creates a tuple
Result1:tuple(int, int) = Identity(1, 2)  # t = tuple(int, int)

# Can also be treated as an array
Result2:[]int = Identity(1, 2)  # t = []int via conversion
```

### Type Constraints

Type constraints restrict which types can be used with type parameters, enabling operations that require specific capabilities.

The most permissive constraint accepts any type:

<!-- 94 -->
```verse
# Works with absolutely any type
Store(Value:t where t:type):t = Value
```

Restricts to types that are subtypes of a specified type:

<!-- 95 -->
```verse
vehicle := class:
    Speed:float = 0.0

car := class(vehicle):
    NumDoors:int = 4

# Only accepts vehicle or its subtypes
ProcessVehicle(V:t where t:subtype(vehicle)):t =
    # Can access Speed because we know V is a vehicle
    Print("Speed: {V.Speed}")
    V
```
<!-- -->

<!--versetest
vehicle := class:
    Speed:float = 0.0

car := class(vehicle):
    NumDoors:int = 4

ProcessVehicle(V:t where t:subtype(vehicle)):t =
    # Can access Speed because we know V is a vehicle
    Print("Speed: {V.Speed}")
    V
-->
<!-- 200 -->
```verse
# Valid calls
ProcessVehicle(vehicle{})      # t = vehicle
ProcessVehicle(car{})          # t = car (subtype of vehicle)
```

The function returns type `t`, not the base type. This preserves the specific type:

<!--verse
vehicle := class:
    Speed:float = 0.0

car := class(vehicle):
    NumDoors:int = 4

# Only accepts vehicle or its subtypes
ProcessVehicle(V:t where t:subtype(vehicle))<transacts>:t =
    # Can access Speed because we know V is a vehicle
    Print("Speed: {V.Speed}")
    V

M()<transacts>:void={
-->
<!-- 96 -->
```verse
MyCar := car{NumDoors:=4, Speed:=60.0}
Result:car= ProcessVehicle(MyCar)  # Result has type car, not vehicle
Result.NumDoors                  # Can access car-specific fields
```
<!-- } -->

The `subtype(comparable)` constraint enables equality comparisons:

<!-- 97 -->
```verse
# Can use = and <> operators on t
FindInArray(Items:[]t, Target:t where t:subtype(comparable))<decides>:[]int =
    for (Index -> Item : Items, Item = Target):
        Index
```

Type parameters can reference each other in constraints:

<!-- 98 -->
```verse
# u must be a subtype of t
Convert(Base:t, Derived:u where t:type, u:subtype(t)):t = Base
# This ensures type safety across related types
```

### Member Access

When using subtype constraints, you can access members that exist on the base type:

<!-- 99 -->
```verse
entity := class:
    Name:string = "Entity"
    Health:int = 100

player := class(entity):
    Score:int = 0

```
<!-- -->

<!--versetest
entity := class:
    Name:string = "Entity"
    Health:int = 100

player := class(entity):
    Score:int = 0
-->
<!-- 299 -->
```verse
# Can access entity members through type parameter
GetInfo(E:t where t:subtype(entity)):tuple(t, string, int) =
    (E, E.Name, E.Health)            # Can access Name and Health

P := player{Name := "Alice", Health := 100, Score := 1500}
Info := GetInfo(P)                   # Returns (player instance, "Alice", 100)
                                     # Info(0) has type player, not entity 
```

Method calls work too:

<!-- 100 -->
```verse
entity := class:
    GetStatus():string = "Active"

# Call methods on parametrically-typed values
CheckStatus(E:t where t:subtype(entity)):string =
    E.GetStatus()  # Method call through type parameter
```

### Polarity and Variance

Type parameters must be used consistently according to variance rules. This ensures type safety when functions are used as values or passed as arguments.

**Covariant positions** (safe for return types):

- Function return types
- Tuple/array element types (as return)
- Map value types (as return)

**Contravariant positions** (safe for parameter types):

- Function parameter types
- Map key types

**The polarity check:** Verse validates that type parameters appear
only in positions compatible with their intended use:

<!-- 101 -->
```verse
# Valid: t appears covariantly (return type)
GetValue(X:t where t:type):t = X

# Valid: t appears contravariantly (parameter)
Consume(X:t where t:type):void = {}

# Valid: t appears in both positions (through function parameter and return)
Apply(F:type{_(:t):t}, X:t where t:type):t = F(X)
```

**Invariant types cause errors:**

<!--NoCompile-->
<!-- 102 -->
```verse
# ERROR 3502: Cannot return type that's invariant in t
# c(t:type) := class{var X:t}  # Mutable field makes c invariant in t
# MakeContainer(X:t where t:type):c(t) = c(t){X := X}
```

The error occurs because `c(t)` contains a mutable field of type `t`,
making it invariant - neither covariant nor contravariant. Returning
such a type from a parametric function is unsafe.

**Map polarity:** Maps are contravariant in keys and covariant in values:

<!-- 103 -->
```verse
# Valid: contravariant key, covariant value
ProcessMap(M:[t]u where t:subtype(comparable), u:type):[t]u = M
```

## Overloading

Function overloading allows you to define multiple functions with the
same name but different parameter types. The compiler selects the
correct version based on the types of the arguments provided at the
call site.

Define multiple functions with the same name but different parameter types:

<!--versetest-->
<!-- 104 -->
```verse
# Overload by parameter type
Process(Value:int):string = "Integer: {Value}"
Process(Value:float):string = "Float: {Value}"
Process(Value:string):string = "String: {Value}"

# Calls select the appropriate overload
Process(42)        # Returns "Integer: 42"
Process(3.14)      # Returns "Float: 3.14"
Process("hello")   # Returns "String: hello"
```

The compiler determines which overload to call based on the argument
types. Each overload must have a distinct parameter type signature.

### Capture

You cannot take a reference to an overloaded function name:

<!--NoCompile-->
<!-- 105 -->
```verse
# ERROR 3502: Cannot capture overloaded function
f(x:int):void = {}
f(x:float):void = {}

# Error: which f?
# g:void = f
```

This restriction exists because the compiler cannot determine which overload you mean without seeing the call site with arguments.

### Effects

You can overload functions with different effects, but only if the
parameter types are also different:

**Valid: Different types, different effects:**

<!--versetest-->
<!-- 106 -->
```verse
Process(x:float):float = x
Process(x:int)<transacts><decides>:int = x = 1

Process(3.0)   # Returns 3.0 (non-failable)
Process[1]     # Returns option{1} (failable)
```

**Invalid: Same types, different effects:**

<!--NoCompile-->
<!-- 107 -->
```verse
# ERROR 3532: Same parameter type
f(x:int):void = {}
f(x:int)<transacts><decides>:void = {}  # ERROR
```

Effects alone don't create distinctness - you need different parameter types.

### Overloads in Subclasses

Subclasses can add new overloads to methods:

<!--verse-->
<!-- 108 -->
```verse
C0 := class:
    f(X:int):int = X

C1 := class(C0):
    # Add new overload for float
    f(X:float):float = X
```
<!-- -->

<!--versetest
C0 := class:
    f(X:int):int = X

C1 := class(C0):
    # Add new overload for float
    f(X:float):float = X
-->
<!-- 208 -->
```verse
C0{}.f(5)     # OK - int overload
C1{}.f(5)     # OK - inherited int overload
C1{}.f(5.0)   # OK - new float overload
```

**Important:** When a subclass defines a method that shares a name
with a parent method, it must either:

1. Provide a **distinct parameter type** (different from all parent overloads)
2. **Override exactly one** parent overload using `<override>`

<!--NoCompile-->
<!-- 109 -->
```verse
C := class{}
D := class(C){}

# Parent class with overloads
E := class:
    f(c:C):C = c
    f(e:E):E = e

# Valid: Overrides one parent overload
F := class(E):
    f<override>(c:C):D = D{}

# ERROR 3532: D is subtype of C, overlaps but doesn't override
# G := class(E):
#     f(d:D):D = d  # ERROR - ambiguous with f(c:C)
```

### Interfaces with Overloaded Methods

Interfaces can declare overloaded methods:

<!-- 110 -->
```verse
formatter := interface:
    Format(X:int):string = "{X}"
    Format(X:float):string = "{X}"

entity := class(formatter):
    Format<override>(X:int):string = "Entity-{X}"
    Format<override>(X:float):string = "Entity-{X}"
```

### Restrictions

**Cannot use `var` with overloaded functions:**

Function-valued variables cannot be overloaded:

<!--NoCompile-->
<!-- 111 -->
```verse
# ERROR 3502: Cannot have var overloaded functions
# var f():void = {}
# var f(x:int):void = {}

# ERROR: Cannot mix var and regular
# var f():void = {}
# f(x:int):void = {}
```

**Cannot overload functions with non-functions:**

A name cannot be both a function and a non-function value:

<!--NoCompile-->
<!-- 112 -->
```verse
# ERROR 3532: Cannot overload with variable
# f:int = 0
# f():void = {}
```

**Cannot overload classes:**

Class names cannot be overloaded:

<!--NoCompile-->
<!-- 113 -->
```verse
# ERROR 3588, 3532: Cannot overload class name
# C := class{}
# C(x:int):C = C{}
```

**Bottom type cannot resolve overloads:**

The bottom type (from `return` without a value) cannot be used for overload resolution:

<!--NoCompile-->
<!-- 114 -->
```verse
# ERROR 3518: Cannot determine which overload
F(X:int):int = X
F(X:float):float = X

# G():void =
#     F(@ignore_unreachable return)  # ERROR - which F?
#     0
```

### Overloading with `<suspends>`

You can mix suspending and non-suspending overloads if the parameter
types differ:

<!--versetest-->
<!-- 115 -->
```verse
f(x:int)<suspends>:void =
    Sleep(1.0)

f(x:float):void =
    Print("Non-suspending")

# Call non-suspending directly
f(1.0)

# Call suspending with spawn
spawn{f(1)}
```

**Cannot call suspending overload without spawn:**

<!--NoCompile-->
<!-- 116 -->
```verse
# ERROR 3512: suspends version needs spawn context
f(x:int):void = {}
f(x:float)<suspends>:void = {}

# g():void = f(1.0)  # ERROR - float version is suspends
```

**Cannot spawn non-suspending overload:**

<!--NoCompile-->
<!-- 117 -->
```verse
# ERROR 3538: Cannot spawn non-suspends function
f(x:int):void = {}
f(x:float)<suspends>:void = {}

# g():void = spawn{f(1)}  # ERROR - int version not suspends
```

### Types 

Every function has a type that captures its parameters, effects, and
return value. The type syntax uses an underscore as a placeholder for
the function name:

<!--versetest-->
<!-- 118 -->
```verse
type{_(:int,:string)<decides>:float}
```

This represents any function that takes an integer and a string, might
fail, and returns a float when successful.

Multiple functions may share a name through overloading, as long as
their signatures do not create ambiguity. The compiler can distinguish
between overloads based on the argument types:

<!--versetest-->
<!-- 119 -->
```verse
Transform(X:int):string = "I:{X}"
Transform(X:float):string = "F:{X}"
Transform(X:string):string = "S:{X}"

Result1 := Transform(42)        # Calls int version
Result2 := Transform(3.14)      # Calls float version
Result3 := Transform("Hello")   # Calls string version
```

However, overloading has strict limitations based on **type
distinctness**. Two types are considered "distinct" for overload
purposes only if there is no possible value that could match both
types. This restriction prevents ambiguity and ensures that function
calls can always be resolved unambiguously at compile time.

Verse uses precise rules to determine whether two parameter types are
distinct enough to allow overloading. Understanding these rules is
critical for designing clear APIs.

The following type pairs are **not distinct** and cannot be used to
overload functions:

**1. Optional and Logic.** `?t` and `logic` are not distinct because
`logic` is equivalent to `?void`:

<!--NoCompile-->
<!-- 120 -->
```verse
# ERROR: Not distinct
F(:?t):void = {}
F(:logic):void = {}
```

**2. Arrays and Maps.**  Arrays `[]t` and maps `[k]t` are not distinct:

<!--NoCompile-->
<!-- 121 -->
```verse
# ERROR: Not distinct
F(:[]int):void = {}
F(:[string]int):void = {}
```

**3. Functions and Maps.** Function types and maps are not distinct:

<!--NoCompile-->
<!-- 122 -->
```verse
# ERROR: Not distinct
F(:[strings]int):void = {}
F(G(:string)<transacts><decides>:int):void = {}
```

**4. Functions and Arrays.** Function types and arrays are not
distinct because an overloaded function could match both:

<!--NoCompile-->
<!-- 123 -->
```verse
# ERROR: Not distinct
F(:[]range):void = {}
F(G(:string)<transacts><decides>:int):void = {} 
```

**5. Interfaces and Classes.** An interface and any class are never
distinct, even if the class doesn't implement the interface, because a
subtype of the class might:

<!--NoCompile-->
<!-- 124 -->
```verse
i := interface{}
t := class{}

# ERROR: Not distinct (subtype of t might implement i)
f(:i):void = {}
f(:t):void = {}
```

**6. Functions with Different Effects.** Functions are not distinct
based on effects alone. Changing or removing effects doesn't create a
distinct overload:

<!--NoCompile-->
<!-- 126 -->
```verse
a := class{}
b := class{}

# ERROR: Not distinct
F(G(:a)<transacts><decides>:b):void = {}
F(G(:a):b):void = {}
```

**7. Functions with Different Signatures.** Functions with different
parameter or return types are not distinct because of function
overloading:

<!--NoCompile-->
<!-- 127 -->
```verse
# ERROR: Not distinct
F(G(:b):b):void = {}
F(G(:a):b):void = {} 
```

**8. void as Top Type.** `void` is treated as equivalent to the top
type (accepts `any`), so it's not distinct from any other type:

<!--NoCompile-->
<!-- 128 -->
```verse
# ERROR: Not distinct
F(:int):void = {}
F(:void):void = {}
```

**9. Subtype Relationships.** Classes with subtype relationships are
not distinct:

<!--NoCompile-->
<!-- 129 -->
```verse
a := class{}
b := class(a){}

# ERROR: Not distinct
F(:a):void = {}
F(:b):void = {}
```

**10. Tuple Distinctness Rules.**  Tuples have complex distinctness rules:

**Empty tuples and arrays are not distinct:**

<!--NoCompile-->
<!-- 130 -->
```verse
a := class{}

# ERROR: Not distinct
F(:tuple(), :a):void = {}
F(:[]a, :a):void = {} 
```

**Tuples and arrays are distinct only if tuple element types are
completely distinct:**

<!--NoCompile-->
<!-- 131 -->
```verse
a := class{}
b := class(a){}

# ERROR: Not distinct (b is subtype of a)
F(:tuple(a, b), :a):void = {}
F(:[]a, :a):void = {}  
```

**Tuples and maps with `int` key are not distinct:**

<!--NoCompile-->
<!-- 132 -->
```verse
a := class{}

# ERROR: Not distinct
F(:tuple(a), :a):void = {}
F(:[int]a, :a):void = {} 
```

**Tuples and maps with non-`int` key ARE distinct:**

<!-- 133 -->
```verse
a := class{}

# Valid: Distinct types
F(:tuple(a), :a):void = {}
F(:[logic]a, :a):void = {}  # OK
```

**Singleton tuples and optional for `int` are not distinct:**

<!--NoCompile-->
<!-- 134 -->
```verse
a := class{}

# ERROR: Not distinct
F(:tuple(int), :a):void = {}
F(:?int, :a):void = {} 
```

**Singleton tuples and optional for non-`int` ARE distinct:**

<!-- 135 -->
```verse
a := class{}

# Valid: Distinct types
F(:tuple(a), :a):void = {}
F(:?a, :a):void = {}  # OK
```

## Publishing Functions

Publishing a function is a promise of backwards compatibility between
the function and its clients. Consider this function:

<!-- 139 -->
```verse
F1<public>(X:int):int = X + 1
```

The type annotation (`X:int):int`) tells us that this function promises that
given any integer it will always return an integer. That contract cannot be
broken in future versions of the code. Because it has the default effect, which
includes the `<reads>` effect, the implementation could change in the future,
perhaps to perform additional operations or optimizations, as long as it
maintains its signature.

Functions that do not have the `<reads>` effect are less flexible. Consider
this function:

<!-- 140 -->
```verse
F2<public>(X:int)<computes>:int = X + 1
```

Because it has the `<computes>` effect specifier, it does not have the
`<reads>` effect. Without the `<reads>` effect, this function promises to
always return the same result for some given parameters. Changing it to return,
for example, `X + 2` would break that promise, and so must be rejected by the
compiler as backward incompatible.

Functions such as `F1` and `F2` are sometimes called *opaque* as the return
type abstracts the function's body. Future version of Verse will support
*transparent* functions:

<!--NoCompile-->
<!-- 141 -->
```verse
F2<public>(X:int) := X + 1
```

A transparent function does not declare its return type, instead the
function's type is inferred from its body. This implies a very
different promise: a forever guarantee that the function's body will
remain exactly the same throughout the lifetime of the module code.
