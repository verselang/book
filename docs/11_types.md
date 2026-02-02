# Types

Every value has a type, and understanding the type system is
fundamental to mastering any language. Types aren't merely labels -
they form a rich hierarchy that governs how values flow through your
program, what operations are permitted, and how the compiler reasons
about your code. The type system combines static verification with
practical flexibility, catching errors at compile time while still
allowing sophisticated patterns of code reuse and abstraction.

At the top of this hierarchy sits `any`, the universal supertype from
which all other types descend. At the bottom lies `false`, the empty
type that contains no values at all (the uninhabited type). Between
these extremes exists a carefully designed lattice of types, each with
its own capabilities and constraints.

## Understanding Subtyping

Subtyping is the foundation of the type hierarchy. When we say that
type A is a subtype of type B, we mean that every value of type A can
be used wherever a value of type B is expected. This relationship
creates a natural ordering among types, from the most specific to the
most general.

Consider the relationship between `rational` and `int`. Every
integer is a rational number, but not every rational is an integer.
Therefore, `int` is a subtype of `ratioanl`. This means you can
pass an `int` to any function expecting a `rational`, but not vice versa:

<!--versetest
GetInt(X:int):void = Print("Integer: {X}")
GetRat(X:rational):void = Print("Rational: {X}")
MyRat:rational = 1/3
MyInt:int = -10
assert: 
    GetRat(MyInt)  # OK -- int is a subtype of rational

#GetInt(MyRat)  # Compile error -  rational is not a subtype of int
<# 
-->
<!-- 01 -->
```verse
GetInt(X:int):void = Print("Integer: {X}")
GetRat(X:rational):void = Print("Rational: {X}")

MyRat:rational = 1/3
MyInt:int = -10

GetRat(MyInt)  # OK -- int is a subtype of rational
GetInt(MyRat)  # Compile error -  rational is not a subtype of int
```
<!-- #> -->

The subtyping relationship extends to composite types in sophisticated
ways. Arrays and tuples follow covariant subtyping rules for their
elements. This means that `[]int` is a subtype of `[]rational`.
Similarly, `tuple(int, int)` is a subtype of `tuple(rational,
rational)`. This covariance allows collections of more specific types
to be used where collections of more general types are expected.

Maps exhibit more complex subtyping behavior. A map type `[K1]V1` is a
subtype of `[K2]V2` when `K2` is a subtype of `K1` (contravariant in
keys) and `V1` is a subtype of `V2` (covariant in values). The
contravariance in keys might seem counterintuitive at first, but it
ensures type safety: if you can look up values using a more general
key type, you must be able to handle more specific key types as well.

Classes and interfaces introduce nominal subtyping through
inheritance. When a class inherits from another class or implements an
interface, it explicitly declares a subtyping relationship:

<!-- 02 -->
```verse
vehicle := class:
    Speed:float = 0.0

car := class(vehicle):  # car is a subtype of vehicle
    NumDoors:int = 4

sports_car := class(car):  # sports_car is a subtype of car (and vehicle)
    Turbo:logic = true
```

This inheritance hierarchy means that a `sports_car` can be used
anywhere a `car` or `vehicle` is expected, but not the reverse. The
subtype inherits all fields and methods from its supertypes while
potentially adding new ones or overriding existing ones.

## Numeric and String Conversions

All type conversions must be explicit, a design choice that eliminates
entire categories of bugs while making the programmer's intent
clear. Converting between numeric types illustrates this principle
clearly. To convert an integer to a float, you multiply by 1.0:

<!--versetest-->
<!-- 03 -->
```verse
MyI:int   = 42
MyF:float = MyI * 1.0  # Explicit conversion to float
```

The reverse conversion, from float to integer, requires choosing a
rounding strategy:

<!--versetest-->
<!-- 04 -->
```verse
MyF:float = 3.7
Opt1:int = Floor[MyF]  # Results in 3
Opt2:int = Ceil[MyF]   # Results in 4
Opt3:int = Round[MyF]  # Results in 4 (rounds to nearest)
```

These conversion functions are failable - they have the `<decides>`
effect and will fail if passed non-finite values like `NaN` or
`Inf`. The explicit failure forces you to handle edge cases:

<!-- 05 -->
```verse
SafeConvert(Value:float):int =
    if:
       Value <> NaN
       Value <> Inf
       Result:= Floor[Value]
    then:
       Result
    else:
       0  # Assuming that this is safe value
```

String conversions follow similar principles. The `ToString()`
function converts various types to their string representations, while
string interpolation provides a convenient syntax for embedding values
in strings:

<!--versetest-->
<!-- 06 -->
```verse
Score:int  = 1500
Msg:string = "Your score: {Score}"  # Implicit ToString() call
```

## Type `any`

<!-- TODO add a link to the builtin types -->

Type `any` is at the top of the type hierarchy it is the universal
supertype that can hold a value of any type. Every type in Verse is a
subtype of `any`, making it the most permissive type.  It serves as an
escape hatch when you genuinely need to work with values of unknown or
varying types.

Once a value is typed as `any`, you've effectively told the compiler
"I don't know what this is," and the compiler responds by preventing
most operations. This is by design—without knowing the actual type,
the compiler cannot verify that operations are safe.

You can explicitly coerce any value to `any` using function call
syntax, `any(42)`. 

Verse automatically coerces values to `any` when their types would
otherwise be incompatible. Understanding these rules help when working
with heterogeneous data.

Mixed-type arrays and maps automatically become `any`:

<!--versetest-->
<!-- 09 -->
```verse
MixedArray :[]any= array{42, "hello", true, 3.14}
MixedMap :[int]any= map{0=>"zero", 1=>1, 2=>2.0}
ConfigMap:[string]any = map{"count"=>42,"name"=>"Player"}
```

Conditional expressions with disjoint branch types produce `any`:

<!--versetest-->
<!-- 11 -->
```verse
# If branches return different types
GetValue(UseString:logic):any =
    if (UseString?):
        "text result"
    else:
        42
```

Logical OR with disjoint types coerces to `any`:

<!-- 12 -->
```verse
# Returns either int or string
OneOf(Flag:logic, I:int, S:string):any =
    (if (Flag?) then {option{I}} else {1=2}) or S
```

The `any` type has restrictions that reflect its role as a generic
container:

- You cannot use equality operators with `any`
- Because `any` is not comparable, it cannot be used as a map key type
- Because `any` is not castable, it is a sticky type.

## Class and Interface Casting

Verse provides two distinct casting mechanisms for classes and
interfaces: fallible casts for runtime type checking, and infallible
casts for compile-time verified conversions. Understanding when and
how to use each is essential for working with inheritance hierarchies
and polymorphic code.

Fallible casts use square bracket syntax `TargetType[value]` to
perform runtime type checks. These casts return an optional value
(`?TargetType`), succeeding only if the value is actually of the
target type or a subtype:

<!-- 17 -->
```verse
# Define a class hierarchy
component := class<castable>:
    Name:string = "Component"

physics_component := class<castable>(component):
    Velocity:float = 0.0

render_component := class<castable>(component):
    Material:string = "default"

# Runtime type checking with fallible casts
ProcessComponent(Comp:component):void =
    if (PhysicsComp := physics_component[Comp]):
        # Successfully cast - PhysicsComp is physics_component
        Print("Physics velocity: {PhysicsComp.Velocity}")
    else if (RenderComp := render_component[Comp]):
        # Different type - RenderComp is render_component
        Print("Render material: {RenderComp.Material}")
    else:
        # Neither type matched
        Print("Unknown component type")
```

The cast expression evaluates to `false` if the runtime type doesn't
match, allowing you to use it directly in conditionals. The optional
binding pattern `(Variable := Expression)` both performs the cast and
binds the result to a variable when successful.

For classes marked `<unique>`, fallible casts preserve identity—a
successful cast returns the same instance, not a copy:

<!--versetest
entity := class<unique><castable>:
    ID:int
player := class<unique>(entity):
    Name:string
assert:
	P := player{ID := 1, Name := "Alice"}
	if (E := entity[P]):
		E = P  # True - same instance
<#
-->
<!-- 18 -->
```verse
entity := class<unique><castable>:
    ID:int

player := class<unique>(entity):
    Name:string

# Create an instance
P := player{ID := 1, Name := "Alice"}

# Cast to base type
if (E := entity[P]):
    E = P  # True - same instance
```
<!-- #> -->

Fallible casts work **only with class and interface types**. You
cannot dynamically cast from or to primitive types, structs, arrays,
or other value types:

<!--NoCompile-->
<!-- 19 -->
```verse
component := class<castable>{}

# Error: cannot cast from primitives
Comp := component[42]          # int to class - not allowed
Comp := component[3.14]        # float to class - not allowed
Comp := component["text"]      # string to class - not allowed
Comp := component[array{1,2}]  # array to class - not allowed

# Error: cannot cast to non-class types
Value := int[component{}]      # class to int - not allowed
Value := logic[component{}]    # class to logic - not allowed
Value := (?int)[component{}]   # class to option - not allowed
```

The restriction exists because fallible casts rely on runtime type
information that only classes and interfaces maintain. Value types
like integers and structs don't have runtime type tags.

*Infallible* casts use parenthesis syntax `TargetType(value)` for
conversions that the compiler can verify will always succeed. These
casts require the source type to be a compile-time subtype of the
target type:

<!--versetest
component := class<castable>:
    Name:string = "Component"

physics_component := class<castable>(component):
    Velocity:float = 0.0
-->
<!-- 20 -->
```verse
# Upcasting: always safe, always succeeds
Base:component = physics_component{Velocity := 10.0}
BaseAgain:component = component(Base)
```

Any type can be infallibly cast to `void`, which discards the value:

<!--versetest
component:=class{}
-->
<!-- 21 -->
```verse
void(42)           # Discard an integer
void("result")     # Discard a string
void(component{})  # Discard an object
```

This implictly happens when you call a function for its side effects
and want to ignore its return value.

### Dynamic Type-Based Casting

Types in Verse are first-class values, which means you can store types
in variables and use them dynamically for casting. This enables
powerful patterns for runtime polymorphism:

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}

ComponentType:castable_subtype(component) = physics_component

# Cast using the stored type
TestComponent(Comp:component, ExpectedType:castable_subtype(component)):logic =
    if (Specific := ExpectedType[Comp]):
        true  # Component matches expected type
    else:
        false

assert:
   P := physics_component{}
   TestComponent(P, physics_component)  # true
   TestComponent(P, render_component)   # false
<#
-->
<!-- 22 -->
```verse
# Type hierarchy
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}

# Store types as values
ComponentType:castable_subtype(component) = physics_component

# Cast using the stored type
Test(Comp:component, ExpectedType:castable_subtype(component)):logic =
    if (Specific := ExpectedType[Comp]):
        true  # Component matches expected type
    else:
        false

# Use with different types
P := physics_component{}
Test(P, physics_component)  # true
not Test(P, render_component)   # false
```
<!-- #> -->

This pattern is particularly powerful when the type to check isn't
known until runtime:

<!--versetest
entity:=class{}
component := class<castable>:
    Owner:entity
physics_component := class<castable>(component){}
render_component := class<castable>(component){}
Components:[]component=array{}
ProcessSpecific(:component)<computes>:void={}
LoadedConfig:string=""
-->
<!-- 23 -->
```verse
# Select type based on configuration
GetComponentType(Config:string):castable_subtype(component) =
    if (Config = "physics"):
        physics_component
    else if (Config = "render"):
        render_component
    else:
        component

# Use the dynamically selected type
RequiredType := GetComponentType(LoadedConfig)
for (Comp : Components):
    if (Specific := RequiredType[Comp]):
        # Process components of the required type
        ProcessSpecific(Specific)
```

This bridges compile-time type safety with runtime flexibility,
allowing type decisions to be made based on program state while
maintaining type correctness.

## Where Clauses

Where clauses are the mechanism for constraining type parameters in
generic code. They appear after type parameters and specify
requirements that types must satisfy to be valid arguments. This
creates a powerful system for writing generic code that is both
flexible and type-safe.

<!-- 24 -->
```verse
# Simple subtype constraint
Process(Value:t where t:subtype(comparable)):void =
    if (Value = Value):  # We know it supports equality
        Print("Value equals itself")
```

Using the same type in multiple constraints is not yet supported, when
implemented, it will allow to write code such as:

<!--NoCompile-->
<!-- 25 -->
```verse
# Multiple constraints on the same type
F(In:t where t:subtype(comparable), t:subtype(printable)):t = # Not supported
    Print("Processing: {In}")
    In
```

Where clauses become more powerful when working with multiple type parameters:

<!-- 26 -->
```verse
# Independent constraints on different parameters
Combine(A:t1, B:t2 where t1:type, t2:type):tuple(t1, t2) =
    (A, B)

# Related constraints
Convert(From:t1, Converter:type{_(:t1):t2} where t1:type, t2:type):t2 =
    Converter(From)
```

Where clauses can express sophisticated relationships between types:

<!--versetest
Contains(Arr:[]t, Item:t where t:type)<decides><computes>:logic = false
-->
<!-- 27 -->
```verse
# Constraint that ensures compatible types for an operation
Merge(Container1:[]t, Container2:[]t where t:subtype(comparable)):[]t =
    var Result:[]t = Container1
    for (Element : Container2, not Contains[Result, Element]):
        set Result += array{Element}
    Result

# Function type constraints
ApplyTwice(F:type{_(:t):t}, Value:t where t:type):t =
    F(F(Value))
```

Where clauses enable sophisticated generic programming patterns:

<!-- 28 -->
```verse
MapFunction(F:type{_(:a):b}, Container:[]a where a:type, b:type):[]b =
    for (Element : Container):
        F(Element)
```

## Refinement Types

While `where` clauses constrain type parameters in generic code,
**refinement types** use `where` to constrain the *values* a type can
hold. This creates subtypes that only accept values satisfying
specific conditions, enabling domain-specific constraints enforced by
the type system.

A refinement type defines a constrained subtype using value predicates:

<!--versetest
percent := type{_X:float where 0.0 <= _X, _X <= 1.0} 
-->
<!-- 29 -->
```verse
# Percentages: floats between 0.0 and 1.0
# percent := type{_X:float where 0.0 <= _X, _X <= 1.0}

# Valid assignments
Opacity:percent = 0.5
Alpha:percent = 1.0

# Invalid: out of range (runtime check fails)
# BadPercent:percent = 1.5  # Fails at assignment
```

**Syntax structure:**

<!--NoCompile-->
<!-- 30 -->
```verse
TypeName := type{_Variable:BaseType where Constraint1, Constraint2, ...}
```

- `_Variable` is a placeholder for the value being constrained
- `BaseType` is `int` or `float`
- Constraints are comparison expressions using `<=`, `<`, `>=`, or `>`

Integer refinements restrict int values to specific ranges:

<!--versetest
age := type{_X:int where 0 <= _X, _X <= 120}
ValidAge:age = 25
positive_int := type{_X:int where _X > 0}
Count:positive_int = 42
small_int := type{_X:int where _X < 100}
<#
-->
<!-- 31 -->
```verse
# Age between 0 and 120
age := type{_X:int where 0 <= _X, _X <= 120}

ValidAge:age = 25
# InvalidAge:age = 150  # Fails constraint

# Positive integers
positive_int := type{_X:int where _X > 0}

Count:positive_int = 42
# Zero:positive_int = 0  # Fails: not positive

# Range with single bound
small_int := type{_X:int where _X < 100}
```
<!-- #> -->

Float refinements handle continuous ranges with IEEE 754 semantics:

<!--versetest
normalized := type{_X:float where 0.0 <= _X, _X <= 1.0}
positive := type{_X:float where _X > 0.0}
celsius := type{_X:float where _X >= -273.15}
<#
-->
<!-- 32 -->
```verse
# Unit interval [0.0, 1.0]
normalized := type{_X:float where 0.0 <= _X, _X <= 1.0}

# Positive floats
positive := type{_X:float where _X > 0.0}

# Temperature in Celsius above absolute zero
celsius := type{_X:float where _X >= -273.15}
```
<!-- #> -->

Finite Floats (Excluding Infinity):

<!--versetest
finite := type{_X:float where -Inf < _X, _X < Inf}
assert:
	MaxFinite:finite = 1.7976931348623157e+308
	MinFinite:finite = -1.7976931348623157e+308
<#
-->
<!-- 33 -->
```verse
# Finite values only (no ±Inf)
finite := type{_X:float where -Inf < _X, _X < Inf}

# Maximum and minimum finite IEEE 754 doubles
MaxFinite:finite = 1.7976931348623157e+308
MinFinite:finite = -1.7976931348623157e+308

# Invalid: infinities excluded
# Infinite:finite = Inf  # Fails constraint
```
<!-- #> -->

### IEEE 754 Edge Cases

**Negative Zero:**

IEEE 754 distinguishes between `+0.0` and `-0.0`. Refinement types
respect this:

<!--versetest
negative := type{_X:float where _X < 0.0}

assert: 
   negative[-1.0]          # Valid
   negative[-0.5]          # Valid
<#
-->
<!-- 34 -->
```verse
# Negative values (excludes both zeros)
negative := type{_X:float where _X < 0.0}

negative[-1.0]          # Valid
negative[-0.5]          # Valid
negative[0.0 / -1.0]    # Fails: produces -0.0, not truly negative
```
<!-- #> -->

The expression `0.0 / -1.0` produces `-0.0`, which is **not** less
than `0.0` in IEEE 754 semantics, so it fails the constraint.

**Positive vs Zero:**

<!--versetest
positive := type{_X:float where _X > -0.0}

assert:
   positive[1.0]   # Valid
   positive[0.1]   # Valid
<#
-->
<!-- 35 -->
```verse
# Positive (excludes zero)
positive := type{_X:float where _X > -0.0}

positive[1.0]   # Valid
positive[0.1]   # Valid
positive[0.0]   # Fails: zero not considered positive
```
<!-- #> -->

**Floating-Point Precision:**

Constraints respect exact IEEE 754 representations:

<!--versetest
small_float := type{_X:float where _X < 0.1}
assert:
    Tiny:small_float = 0.09999999999999999167332731531132594682276248931884765625
<#
-->
<!-- 36 -->
```verse
# Values strictly less than 0.1
small_float := type{_X:float where _X < 0.1}

# Valid: largest float before 0.1
Tiny:small_float = 0.09999999999999999167332731531132594682276248931884765625

# Invalid: 0.1's actual representation is slightly above 0.1
# NotSmall:small_float = 0.1000000000000000055511151231257827021181583404541015625
```
<!-- #> -->

The decimal `0.1` cannot be represented exactly in binary
floating-point, so the actual stored value is slightly above the
mathematical 0.1.

### Constraint Expression Restrictions

Refinement type constraints have strict limitations on what
expressions are allowed:

**Only Literal Values:** Constraints must use literal numbers, not
variables or expressions:

<!--NoCompile-->
<!-- 37 -->
```verse
# Valid: literal float
bounded := type{_X:float where _X < 100.0}

# Invalid: cannot use variables
Limit:float = 100.0
bad_type := type{_X:float where _X < Limit}  # ERROR 

# Invalid: cannot use function calls
GetMax():float = 100.0
bad_type := type{_X:float where _X < GetMax()}  # ERROR

# Invalid: cannot use qualified names
config := module{Max:float = 100.0}
bad_type := type{_X:float where _X < (config:)Max}  # ERROR
```

This ensures constraints are statically known at compile time.

**Float Literals Required for Float Types:** When constraining floats,
bounds must be float literals (with decimal point):

<!--versetest
good_float := type{_X:float where _X <= 142.0}

assert:
     1
<#
-->
<!-- 38 -->
```verse
# Invalid: integer literal in float constraint
# bad_float := type{_X:float where _X <= 142}  # ERROR 3502

# Valid: float literal
good_float := type{_X:float where _X <= 142.0}
```
<!-- #> -->

**NaN Not Allowed:** Not a Number cannot appear in
constraints:

<!--versetest-->
<!-- 39 -->
```verse
# Invalid: NaN in constraint
# nan_type := type{_X:float where _X <= NaN}      # ERROR 3502
# nan_type := type{_X:float where NaN <= _X}      # ERROR 3502
# nan_type := type{_X:float where 0.0/0.0 <= _X}  # ERROR 3502
```

Since `NaN` comparisons are always false, such constraints would be meaningless.

**Allowed Literal Forms:**

- Float literals: `1.0`, `3.14`, `-2.5`, `1.7976931348623157e+308`
- Integer literals: `0`, `42`, `-100` (for int refinements)
- Special float values: `Inf`, `-Inf`

### Fallible Casts

Refinement types are checked at assignment and through fallible casts:

<!--versetest-->
<!--versetest
percent := type{_X:float where 0.0 <= _X, _X <= 1.0}
GetInputFromUser<public>()<computes>:float = 50.0
ProcessPercent<public>(P:percent):void = {}
ShowError<public>(Msg:string):void = {}
assert:
   Valid:percent = 0.5  # OK
   UserInput:float = GetInputFromUser()
   if (Value := percent[UserInput]):
       ProcessPercent(Value)
   else:
       ShowError()
<#
-->
<!-- 40 -->
```verse
percent := type{_X:float where 0.0 <= _X, _X <= 1.0}

# Direct assignment (compile-time known)
Valid:percent = 0.5  # OK

# Runtime check with fallible cast
UserInput:float = GetInputFromUser()
if (Value := percent[UserInput]):
    # UserInput was in [0.0, 1.0]
    ProcessPercent(Value)
else:
    # Out of range
    ShowError()
```
<!-- #> -->

The cast `percent[UserInput]` returns `?percent`—succeeding if the
value satisfies the constraint, failing otherwise.

### Examples

Refinement types work as parameter and return types:

<!--versetest
finite := type{_X:float where -Inf < _X, _X < Inf}
Half(X:finite):float = X / 2.0
assert:
   Half(100.0)  # Returns 50.0
   Half(1.0)    # Returns 0.5
<#
-->
<!-- 41 -->
```verse
finite := type{_X:float where -Inf < _X, _X < Inf}

# Parameter with constraint
Half(X:finite):float = X / 2.0

Half(100.0)  # Returns 50.0
Half(1.0)    # Returns 0.5

# Cannot pass infinity
# Half(Inf)  # ERROR 3509: Inf not in finite
```
<!-- #> -->

**Coercion and Negation:**

<!--versetest
percent := type{_X:float where 0.0 <= _X, _X <= 1.0}
negative_percent := type{_X:float where _X <= 0.0, _X >= -1.0}

assert:
   MakePercent():percent = 0.5
   NegValue:negative_percent = -MakePercent()  # -0.5 valid
   NegValue2:negative_percent = ---0.7  # Triple negation = -0.7
<#
-->
<!-- 42 -->
```verse
percent := type{_X:float where 0.0 <= _X, _X <= 1.0}
negative_percent := type{_X:float where _X <= 0.0, _X >= -1.0}

MakePercent():percent = 0.5

# Negation preserves constraint compatibility
NegValue:negative_percent = -MakePercent()  # -0.5 valid

# Multiple negations
NegValue2:negative_percent = ---0.7  # Triple negation = -0.7
```
<!-- #> -->

### Overloading Restrictions

Overlapping refinement types cannot be used for function
overloading—they're ambiguous:

<!-- 43 -->
```verse
percent := type{_X:float where 0.0 <= _X, _X <= 1.0}
not_infinity := type{_X:float where Inf > _X}

# ERROR 3532: Cannot distinguish - percent ⊂ not_infinity
# F(X:percent):float = 0.0
# F(X:not_infinity):float = X

# Calling F(0.5) would be ambiguous - which overload?
```

However, **disjoint** refinement types can overload:

<!--versetest-->
<!--versetest
positive := type{_X:float where _X > 0.0}
negative := type{_X:float where _X < 0.0}
F(X:positive):float = X
F(X:negative):float = X + 1.0
assert:
   F(1.0)=1.0   # Returns 1.0 (positive overload)
   F(-1.0)=0.0  # Returns 0.0 (negative overload)
<#
-->
<!-- 44 -->
```verse
positive := type{_X:float where _X > 0.0}
negative := type{_X:float where _X < 0.0}

# Valid: ranges don't overlap (zero excluded from both)
F(X:positive):float = X
F(X:negative):float = X + 1.0

F(1.0)   # Returns 1.0 (positive overload)
F(-1.0)  # Returns 0.0 (negative overload)
# F(0.0)  # Would fail - neither overload matches
```
<!-- #> -->

## Comparable and Equality

The `comparable` type represents a special subset of types that
support equality comparison. Not all types can be compared for
equality - this is a deliberate design choice that prevents
meaningless comparisons and ensures that equality has well-defined
semantics.

A type is comparable if its values can be meaningfully tested for
equality. The basic scalar types are all comparable: `int`, `float`,
`rational`, `logic`, `char`, and `char32`. Compound types are
comparable if all their components are comparable. This means arrays
of integers are comparable, tuples of floats and strings are
comparable, and maps with comparable keys and values are comparable.

The equality operators `=` and `<>` are defined in terms of the
comparable type:

<!--NoCompile-->
<!-- 45 -->
```verse
operator'='(X:t, Y:t where t:subtype(comparable))<decides>:t
operator'<>'(X:t, Y:t where t:subtype(comparable))<decides>:t
```

The signatures requires that both operands be subtypes of comparable
and the return type is the least upper bound of their types.

<!--NoCompile-->
<!-- 46 -->
```verse
0 = 0        # Succeeds - both are int
0.0 = 0.0    # Succeeds - both are float
0 = 0.0      # Fails - there is no implicit conversion from int to float
```

Here is an example that highlights how the return type of `=` is computed:

<!--46b -->
```verse
I:int=1
R:rational=1/3
X:rational= (I=R)  # Compiles and fails at runtime

I:int=1
S:string="hi"
Y:comparable= (I=S)  # Compiles and fails at runtime
```

In the case of variable `X`, its type can be either `rational` or
`comparable`. For variable `Y`, the only common type between `int` and
`string` is `comparable`.


Classes require special handling for comparability. By default, class
instances are not comparable because there's no universal way to
define equality for user-defined types. However, you can make a class
comparable using the `unique` specifier:

<!--verse
entity := class<unique>:
    ID:int
    Name:string

F()<decides>:void={
Player1 := entity{ID := 1, Name := "Alice"}
Player2 := entity{ID := 1, Name := "Alice"}
Player3 := Player1

Player1 = Player2  # Fails - different instances
Player1 = Player3  # Succeeds - same instance
}<#
-->
<!-- 47 -->
```verse
entity := class<unique>:
    ID:int
    Name:string

Player1 := entity{ID := 1, Name := "Alice"}
Player2 := entity{ID := 1, Name := "Alice"}
Player3 := Player1

Player1 = Player2  # Fails - different instances
Player1 = Player3  # Succeeds - same instance
```
<!--verse
#>
-->

With the `unique` specifier, instances are only equal to themselves
(identity equality), not to other instances with the same field values
(structural equality). This provides a clear, predictable semantics
for class equality.

### Comparable as a Generic Constraint

The `comparable` type is commonly used as a constraint in generic
functions to ensure operations like equality testing are available:

<!--versetest-->
<!-- 48 -->
```verse
Find(Items:[]t, Target:t where t:subtype(comparable))<decides>:int =
    for (Index->Item:Items):
        if (Item = Target):
            return Index
    -1  # Not found

# Works with any comparable type
Position := Find[array{"apple", "banana", "cherry"}, "banana"]  # Returns 1
```

### Array-Tuple Comparison

A notable feature of Verse's equality system is that arrays and tuples
of comparable elements can be compared with each other:

<!--versetest-->
<!-- 49 -->
```verse
# Arrays can equal tuples
array{1, 2, 3} = (1, 2, 3)       # Succeeds
(4, 5, 6) = array{4, 5, 6}       # Succeeds - bidirectional

# Inequality also works
array{1, 2, 3} <> (1, 2, 4)      # Succeeds - different values
```

This comparison works structurally - the sequences must have the same
length and corresponding elements must be equal. This feature allows
functions expecting arrays to accept tuples, increasing flexibility.

### Overload Distinctness with Comparable

You cannot create overloads where one parameter is a specific comparable type and another is the general `comparable` type, as this creates ambiguity:

<!--NoCompile-->
<!-- 50 -->
```verse
# Not allowed - ambiguous overloads
F(X:int):void = {}
F(X:comparable):void = {}  # ERROR: int is already comparable

# Not allowed with unique classes either
unique_class := class<unique>{}
G(X:unique_class):void = {}
G(X:comparable):void = {}  # ERROR: unique_class is comparable
```

However, you can overload with non-comparable types:

<!-- 51 -->
```verse
# This is allowed
regular_class := class{}  # Not comparable
H(X:regular_class):void = {}
H(X:comparable):void = {}  # OK: no ambiguity
```

### Dynamic Comparable Values

When working with heterogeneous collections, you may need to box
comparable values into the `comparable` type explicitly. These boxed
values maintain their equality semantics:

<!--versetest-->
<!-- 52 -->
```verse
AsComparable(X:comparable):comparable = X

# Boxed values compare correctly with both boxed and unboxed
array{AsComparable(1)} = array{1}              # Succeeds
array{AsComparable(1)} = array{AsComparable(1)} # Succeeds
array{AsComparable(1)} <> array{2}             # Succeeds
```

This allows you to create collections that mix different comparable
types by boxing them all to `comparable`.

### Map Keys and Comparable

Map keys must be comparable types. Most comparable types can be used
as map keys, including:

- All numeric types: `int`, `float`, `rational`
- Character types: `char`, `char32`
- Text: `string`
- Enumerations
- `<unique>` classes
- Optionals of comparable types: `?t` where `t` is comparable
- Arrays of comparable types: `[]t` where `t` is comparable
- Tuples of comparable types
- Maps with comparable keys and values: `[k]v`
- Structs with comparable fields

Note that while `float` can be used as a map key, floating-point
special values have specific equality semantics (see [Map
documentation](02_primitives.md#floating-point-keys) for details on
`NaN` and zero handling).

There is currently no way to make a regular class comparable by
writing a custom comparison method. Only the `<unique>` specifier
enables class comparability through identity equality.

<!--TODO the above is right, right? It seems like a major
limitation. People will invent their own solutions. -->

## Generators

Generators represent lazy sequences that produce values on demand
rather than storing all elements in memory. Unlike arrays which
materialize all elements upfront, generators compute each value only
when requested during iteration. This makes them memory-efficient for
large or infinite sequences, and essential for scenarios where you're
processing streaming data or expensive computations.

Generators use the parametric type `generator(t)` where `t` is the
element type:

<!--versetest
MakeIntegerSequence():[]int = array{1, 2, 3}
GetAllEntities():[]entity = array{}
entity := class{}

assert:
   IntSequence:generator(int) = MakeIntegerSequence()
   EntityStream:generator(entity) = GetAllEntities()
<#
-->
<!-- 53 -->
```verse
# Generator of integers
IntSequence:generator(int) = MakeIntegerSequence()
EntityStream:generator(entity) = GetAllEntities()
```
<!-- #> -->

Syntax restrictions:

<!--versetest
GetSequence()<computes>:[]int = array{1, 2, 3}
-->
<!-- 54 -->
```verse
# Correct: Use parentheses
ValidGenerator:generator(int) = GetSequence()

# Wrong: Square brackets are invalid
# BadGenerator:generator[int] = GetSequence()  # ERROR 

# Wrong: Curly braces are invalid
# BadGenerator:generator{int} = GetSequence()  # ERROR 
```

Element types must be valid Verse types, not literals or expressions:

<!--NoCompile-->
<!-- 55 -->
```verse
# Valid
generator(int)
generator(string)
generator(my_class)

# Invalid: Cannot use literals
# generator(1)        # ERROR 3547
# generator("text")   # ERROR 3547
```

Constrained types work as element types:

<!--versetest
GetConstrainedSequence()<allocates>:[]int = array{1, 2, 3}
-->
<!-- 56 -->
```verse
# Valid: Constrained element type
PositiveInts:generator(type{X:int where X > 0, X < 10}) = GetConstrainedSequence()
```

### For Loops

The primary way to consume generators is through `for` expressions:

<!--versetest
GetIntegerSequence()<allocates>:[]int = array{1, 2, 3}
-->
<!-- 57 -->
```verse
# Direct iteration
ProcessStream()<transacts>:void =
    for (Item : GetIntegerSequence()):
        Print("{Item}")

# Store in variable first
ProcessWithVariable()<transacts>:void =
    Sequence := GetIntegerSequence()
    for (Item : Sequence):
        Print("{Item}")
```

Generators work with arrow syntax in loops, showing that domain and range are identical:

<!--versetest
GetFloatSequence<public>():[]float = array{1.0, 2.0, 3.0}
-->
<!-- 58 -->
```verse
DoubleCheck():logic =
    for (Index->Value : GetFloatSequence()):
        # Index and Value are the same
        Index = Value
```

**Multiple generators in one loop:**

<!--versetest
GetFloatSequence()<allocates>:[]float = array{1.0, 2.0, 3.0}
-->
<!-- 59 -->
```verse
ProcessPairs()<transacts>:void =
    var Total:float = 0.0
    for (A : GetFloatSequence(), B : GetFloatSequence()):
        set Total += A + B
```

**Combining generators with conditions:**

<!--versetest
GetFloatSequence<public>():[]float = array{1.0, 2.0, 3.0}
-->
<!-- 60 -->
```verse
FilteredSum()<transacts>:float =
    var Total:float = 0.0
    for (
        A : GetFloatSequence(),
        B : array{1.0, 2.0, 4.0, 8.0},
        A <> 4.0,
        B <> 4.0
    ):
        set Total += A + B
    Total
```

### Restrictions

Generators have strict type conversion rules to maintain safety:

**Cannot convert arrays to generators:**

<!--NoCompile-->
<!-- 61 -->
```verse
Numbers := array{1, 2, 3}
# Seq:generator(int) = Numbers  # ERROR 3509
```

**Cannot convert between incompatible element types:**

<!--NoCompile-->
<!-- 62 -->
```verse
IntSeq := GetIntegerSequence()
# FloatSeq:generator(float) = IntSeq  # ERROR 3509
```

**Cannot index generators like arrays:**

<!--NoCompile-->
<!-- 63 -->
```verse
Seq := GetIntegerSequence()
# Value := Seq[0]  # ERROR 3509
# Generators don't support random access
```

**Converting generators to arrays:**

Use a `for` expression to materialize the sequence:

<!--versetest
GetIntegerSequence<public>():[]int = array{1, 2, 3}
-->
<!-- 64 -->
```verse
GeneratorToArray(Gen:generator(t) where t:type):[]t =
    for (Item : Gen):
        Item

Numbers := GeneratorToArray(GetIntegerSequence())
# Numbers is now array{1, 2, 3, 4}
```

### Covariance

Generators are **covariant** in their element type when the element type has subtyping relationships:

<!--versetest
animal := class{}
dog := class(animal){}
GetDogSequence():[]dog = array{}
GetAnimalSequence():[]animal = array{}
assert:
   DogStream:generator(dog) = GetDogSequence()
   AnimalStream:generator(animal) = DogStream  # OK - covariance
   GeneralStream:generator(animal) = GetAnimalSequence()
<#
-->
<!-- 65 -->
```verse
animal := class:
    Name:string

dog := class(animal):
    Breed:string

# Covariant: generator(dog) is a subtype of generator(animal)
DogStream:generator(dog) = GetDogSequence()
AnimalStream:generator(animal) = DogStream  # OK - covariance

# Cannot upcast: generator(animal) is NOT a subtype of generator(dog)
GeneralStream:generator(animal) = GetAnimalSequence()
# SpecificStream:generator(dog) = GeneralStream  # ERROR
```
<!-- #> -->

This covariance enables flexible APIs:

<!--versetest
animal := class{Name:string=""}
-->
<!-- 66 -->
```verse
# Function accepting generator of base type
ProcessAnimals(Animals:generator(animal)):void =
    for (A : Animals):
        Print(A.Name)

# Can pass generator of derived type
ProcessAnimals(GetDogSequence())  # OK due to covariance
```

### Type Joining

When conditionally selecting between generators, Verse finds the least common supertype:

<!--verse
GetChild1Sequence():[]child1 = array{}
GetChild2Sequence():[]child2 = array{}
-->
<!-- 67 -->
```verse
base := class:
    ID:int

child1 := class(base):
    Extra1:string

child2 := class(base):
    Extra2:int

# Conditional selection finds common supertype
GetStream(UseFirst:logic):generator(base) =
    if (UseFirst?):
        GetChild1Sequence()  # Returns generator(child1)
    else:
        GetChild2Sequence()  # Returns generator(child2)
    # Result type: generator(base)
```

Similar to effect joining, the compiler computes the least upper bound
(join) of the generator element types.


### Constraints and Limitations

- **No random access:** Generators don't support indexing or random access operations. They're
strictly sequential.
- **No reusability:** Most generators can only be iterated once. After consuming a
generator, it's exhausted.

## Type Hierarchies

The type system forms a graph rather than a simple tree. This means
types can have multiple supertypes, though multiple inheritance is
currently limited to interfaces. Understanding these relationships
helps you design flexible, reusable code.

At the top of the hierarchy, `any` serves as the universal supertype.
The `void` type is another universal supertype alongside `any`. Every
type is a subtype of `void`, meaning `void` accepts all values. This
is fundamentally different from `false`, the true empty/bottom type.

### Understanding void

Unlike `any`, which erases type information, `void` serves as a
"discard" type indicating that a value's specific type doesn't matter.

Functions with `void` return type can return any value, which is then
discarded by the type system:

<!--versetest
WriteToFile(:string)<transacts>:void = {}
-->
<!-- 77 -->
```verse
LogEvent(Message:string)<transacts>:void =
    WriteToFile(Message)
    42                   # Returns int, but typed as void

F():void = 1             # Valid - returns int, typed as void
F()                      # Result is void
```

Despite being typed as `void`, these functions still produce their
computed values—the values are simply not accessible through the type
system. This ensures side effects and computations occur even when the
return value is discarded:

<!--versetest-->
<!-- 78 -->
```verse
MakePair(X:string, Y:string):void = (X, Y)

# Function computes the pair even though return type is void
MakePair("hello", "world")  # Still creates ("hello", "world")
```

Functions with `void` parameters accept any argument type:

<!--versetest-->
<!-- 79 -->
```verse
Discard(X:void):int = 42

Discard(0)               # int → void 
Discard(1.5)             # float → void 
Discard("test")          # string → void 
```

Class fields can be typed as `void`, accepting any initialization
value:

<!-- 80 -->
```verse
config := class:
    Setting:void = array{1, 2}  # Default with array
```

In function types, `void` participates in variance:

<!--versetest-->
<!-- 81 -->
```verse
IntIdentity(X:int):int = X

# Contravariant return: supertype in return position
F:int->void = IntIdentity  # int->int → int->void ✓
# void is supertype of int, so this works

AcceptVoid(X:void):int = 19

# Contravariant parameter: supertype in parameter position
G:int->int = AcceptVoid    # void->int → int->int ✓
# Can use function accepting void where function accepting int expected
```

However, `void` in parameter position does NOT allow conversion the
other way:

<!--versetest-->
<!-- 82 -->
```verse
IntFunction(X:int):int = X
# F:void->int = IntFunction  # ERROR 3509
# Cannot convert int parameter to void parameter in function type
```

**void vs false**: The `false` type is the empty/bottom type
(uninhabited type) with no values. It's the opposite of `void`:

- **`void`**: Universal supertype - all types are subtypes of void, contains all values
- **`false`**: Bottom type - subtype of all types, contains zero values

Between the universal supertypes (`any`, `void`) and the bottom type
(`false`), types form natural groupings. The numeric types (`int`,
`float`, `rational`) share common arithmetic operations but don't form
a single hierarchy - they're siblings rather than ancestors and
descendants. The container types (arrays, maps, tuples, options) each
have their own subtyping rules based on their element types.

Understanding variance is crucial for working with generic
containers. Arrays and options are covariant in their element type -
if A is a subtype of B, then `[]A` is a subtype of `[]B` and `?A` is a
subtype of `?B`. This allows natural code like (assuming that Verse
had a `nat` type):


TODO change to RATIONAL

<!--NoCompile-->
<!-- 89 -->
```verse
ProcessNumbers(Numbers:[]int):void =
    for (N : Numbers):
        Print("{N}")

NaturalNumbers:[]nat = array{1, 2, 3}
ProcessNumbers(NaturalNumbers)  # Works due to covariance
```

Functions exhibit more complex variance. They're contravariant in
their parameter types and covariant in their return types. A function
type `(T1)->R1` is a subtype of `(T2)->R2` if T2 is a subtype of T1
(contravariance) and R1 is a subtype of R2 (covariance). This ensures
that function subtyping preserves type safety:

<!-- 90 -->
```verse
function_type1 := type{_(:any):int}
function_type2 := type{_(:int):any}

# function_type1 is a subtype of function_type2
# It accepts more general input (any vs int)
# And returns more specific output (int vs any)
```

## Type Aliases

Type aliases allow you to create alternative names for types, making
complex type signatures more readable and maintainable. They're
particularly valuable for function types, parametric types, and
frequently-used type combinations.

A type alias is created using simple assignment syntax at module scope:

<!--verse
entity:=struct{}
-->
<!-- 91 -->
```verse
# Simple type aliases
coordinate := tuple(float, float, float)
entity_map := [string]entity
player_id := int

# Function type aliases
update_handler := type{_(:float):void}
validator := int -> logic
transformer := type{_(:string):int}
```

Type aliases are compile-time only - they create no runtime overhead
and are purely for programmer convenience and code clarity.

**Type aliases are alternative names, not new types.** They don't
create distinct types like `newtype` in some languages. Values of the
alias and the original type are completely interchangeable:

<!--versetest
player_id := int
game_id := int
-->
<!-- 92 -->
```verse
# Assume
# player_id := int
# game_id := int

ProcessPlayer(ID:player_id):void = {}
ProcessGame(ID:game_id):void = {}

PID:player_id = 42
GID:game_id = 42

# These all work - aliases are just names
ProcessPlayer(PID)      # OK
ProcessPlayer(GID)      # OK - game_id is also int
ProcessPlayer(42)       # OK - int literal works too
ProcessGame(PID)        # OK - player_id is also int
```

Type aliases can have access specifiers that control their visibility across modules:

<!--versetest
PublicAlias<public> := int
InternalAlias<internal> := string
<#
-->
<!-- 93 -->
```verse
# Public alias - accessible from other modules
PublicAlias<public> := int

# Internal alias - only accessible within defining module
InternalAlias<internal> := string

# Protected/private also work
ProtectedAlias<protected> := float  # only in classes and interfaces
```
<!-- #> -->

**Type aliases cannot be more public than the types they alias:**

<!-- 94 -->
```verse
PrivateClass := class{}      # No specifier = internal scope

# INVALID: Public alias to internal type (ERROR 3593)
# PublicToPrivate<public> := PrivateClass

# VALID: Same or less visibility
InternalToInternal<internal> := PrivateClass
InternalAlias := PrivateClass  # Defaults to internal
```

This restriction applies to all type constructs:

<!--NoCompile-->
<!-- 95 -->
```verse
PrivateType := class{}

# All INVALID - trying to make internal type public (ERROR 3593)
# Pub1<public> := ?PrivateType           # Optional
# Pub2<public> := []PrivateType          # Array
# Pub3<public> := [int]PrivateType       # Map value
# Pub4<public> := [PrivateType]int       # Map key
# Pub5<public> := tuple(int, PrivateType)  # Tuple
# Pub6<public> := PrivateType -> int     # Function parameter
# Pub7<public> := int -> PrivateType     # Function return
# Pub8<public> := type{_():PrivateType}  # Function type
```

### Requirement

- **Type aliases can only be defined at module scope.** They cannot be
defined inside classes, functions, or any nested scope.
This restriction ensures type aliases have consistent visibility and
prevents scope-dependent type interpretations.

- Type aliases must be defined **before** they are used. Forward
references are not allowed.

- Type aliases are not first-class values and cannot be used as such.

## Metatypes

Verse provides advanced type constructors that allow you to work with
types as values, enabling powerful patterns for runtime polymorphism
and generic instantiation. These metatypes—`subtype`,
`concrete_subtype`, and `castable_subtype`—bridge the gap between
compile-time type safety and runtime flexibility.

### subtype

The `subtype(T)` type constructor represents runtime type values that
are subtypes of `T`. Unlike `concrete_subtype` and `castable_subtype`,
which are specialized for classes and interfaces, `subtype(T)` works
with **any type** in Verse, including primitives, enums, collections,
and function types.

<!-- 100 -->
```verse
C0 := class {}
C1 := class(C0) {}

C2 := class:
    var m0:subtype(C0)  # Can hold C0, C1, or any subtype of C0
    var m1:subtype(C2)  # Can hold C2 or any subtype of C2

    # Assign class types
    f0():void = set m0 = C0
    f1():void = set m0 = C1  # C1 is subtype of C0

    # Accept as parameter
    f3(classArg:subtype(C0)):void = set m0 = classArg
```

The key capability of `subtype(T)` is holding type values at runtime
while maintaining type safety through the subtype relationship.

Unlike the other metatypes, `subtype(T)` accepts any type as its parameter:

<!-- TODO: Andy says that the failures here are bugs. -->

<!--NoCompile-->
<!-- 101 -->
```verse
# Primitives
IntType:subtype(int) = int
LogicType:subtype(logic) = logic
FloatType:subtype(float) = float

# Enums
#my_enum := enum { A, B, C }
EnumType:subtype(my_enum) = my_enum

# Collections
ArrayType:subtype([]int) = []int
OptionType:subtype(?string) = ?string

# Function types
FuncType:subtype(type{_():void}) = type{_():void}

# Classes and interfaces
ClassType:subtype(my_class) = my_class
InterfaceType:subtype(my_interface) = my_interface
```

This universality makes `subtype(T)` the most flexible of the metatypes, suitable for any scenario where you need to store or pass type values.

**Subtyping Relationship:**

The `subtype` constructor preserves the subtyping relationship:
`subtype(T) <: subtype(U)` if and only if `T <: U`. This means you can
assign a more specific subtype to a less specific one:

<!-- 102 -->
```verse
super_class := class{}
sub_class := class(super_class) {}

# Covariance: sub_class <: super_class
SubtypeVar:subtype(sub_class) = sub_class
SupertypeVar:subtype(super_class) = SubtypeVar  # Valid

# Reverse fails - super_class is not <: sub_class
# SubtypeVar2:subtype(sub_class) = super_class  # Error 3509
```

This also applies to interfaces:

<!-- 103 -->
```verse
super_interface := interface{}
sub_interface := interface(super_interface) {}

class_impl := class(sub_interface) {}

# Covariance through interface hierarchy
SpecificType:subtype(sub_interface) = class_impl
GeneralType:subtype(super_interface) = SpecificType  # Valid
```

**Using with Interfaces:**

When working with interfaces, `subtype(T)` can hold any class that implements the interface:

<!-- 104 -->
```verse
printable := interface:
    PrintIt():void

document := class(printable):
    PrintIt<override>():void = {}

# Can hold any type implementing printable
DocumentType:subtype(printable) = document
```

**Relationship to `type`:**

Both `subtype(T)` and `castable_subtype(T)` are subtypes of `type`, meaning they can be used where `type` is expected:

<!-- 105 -->
```verse
C := class:
    f(c:subtype(C)):type = return(c)  # Valid: subtype(C) <: type

T := interface {}
g(x:subtype(T)):type = x  # Valid: subtype(T) <: type
```

**Restrictions:**

While `subtype(T)` is flexible, it has important restrictions:

1. **Cannot use as value:** `subtype(T)` is a type constructor, not a
   value. You cannot use `subtype(T)` itself as a value.
2. **Exactly one argument:** `subtype` requires exactly one type argument.
3. **Cannot use with attributes:** `subtype` cannot be used with
   classes that inherit from `attribute`.

### concrete_subtype

The `concrete_subtype(t)` type constructor creates a type that
represents concrete (instantiable) subclasses of `t`. A concrete class
is one that can be instantiated directly—it has the `<concrete>`
specifier and provides default values for all fields:

<!-- 110 -->
```verse
# Abstract base class
entity := class<abstract>:
    Name:string
    GetDescription():string

# Concrete implementations
player := class<concrete>(entity):
    Name<override>:string = "Player"
    GetDescription<override>():string = "A player character"

enemy := class<concrete>(entity):
    Name<override>:string = "Enemy"
    GetDescription<override>():string = "An enemy creature"

# Class that stores a type and can instantiate it
spawner := class:
    EntityType:concrete_subtype(entity)

    Spawn():entity =
        # Instantiate using the stored type
        EntityType{}

# Use it
# NewEntity := spawner{EntityType := player}.Spawn()
```

The key feature of `concrete_subtype` is that it ensures the stored type can be instantiated. Without this constraint, you couldn't safely call `EntityType{}` because abstract classes cannot be instantiated.

#### Requirements

A type can be used with `concrete_subtype` only if it's a class or
interface type. Additionally, the actual type value assigned must be a
concrete class—one marked with `<concrete>` and having all fields with
defaults:

<!-- 111 -->
```verse
# Valid: concrete class with all defaults
config := class<concrete>:
    MaxPlayers:int = 8
    TimeLimit:float = 300.0

ConfigType:concrete_subtype(config) = config  # Valid

# Invalid: abstract class cannot be concrete_subtype
abstract_base := class<abstract>:
    Value:int

# This would be an error:
# BaseType:concrete_subtype(abstract_base) = abstract_base
```

When you have a `concrete_subtype`, you can instantiate it with the
empty archetype `{}`, but you cannot provide field initializers—the
concrete class must provide all necessary defaults:

<!-- 112 -->
```verse
entity_base := class<abstract>:
    Health:int

warrior := class<concrete>(entity_base):
    Health<override>:int = 100

EntityType:concrete_subtype(entity_base) = warrior

# Valid: empty archetype uses defaults
# Instance := EntityType{}

# Invalid: cannot initialize fields through metatype
# Instance := EntityType{Health := 150}
```

### castable_subtype

The `castable_subtype(t)` type constructor represents types that are
subtypes of `t` and marked with the `<castable>` specifier. This
enables runtime type queries and dynamic casting, which is essential
for component systems and polymorphic hierarchies:

<!--verse
entity:=class{}
vector3:=class{}
-->
<!-- 113 -->
```verse
# Castable base class
component := class<abstract><castable>:
    Owner:entity

# Castable subtypes
physics_component := class<castable>(component):
    Velocity:vector3

render_component := class<castable>(component):
    Material:string

# Function accepting castable subtype
ProcessComponent(CompType:castable_subtype(component), Comp:component):void =
    # Can use CompType to perform type-safe casts
    if (Specific := CompType[Comp]):
        # Comp is now known to be of type CompType
```

### final_super and Type Queries

The `castable_subtype` works with the `<final_super>` specifier and
`GetCastableFinalSuperClass` function to enable sophisticated runtime
type queries. This combination provides a powerful mechanism for
component systems and polymorphic architectures.

The `<final_super>` specifier marks classes as stable anchor points in
inheritance hierarchies. These "final super classes" act as canonical
representatives for families of related types:

<!--verse
entity:=class{}
vector3:=class{}
-->
<!-- 114 -->
```verse
component := class<castable>:
    Owner:entity

# Stable anchor for the physics component family
physics_component := class<final_super>(component):
    Velocity:vector3

# Specific implementations inherit from the anchor
rigid_body := class(physics_component):
    Mass:float

soft_body := class(physics_component):
    SpringConstant:float
```

By marking `physics_component` as `<final_super>`, you declare it as the canonical representative for all physics-related components. Even though `rigid_body` and `soft_body` are distinct types, they both belong to the "physics_component family" anchored at `physics_component`.

#### GetCastableFinalSuperClass

The `GetCastableFinalSuperClass` function queries the type hierarchy to find the `<final_super>` class between a base type and a derived type. Two variants exist:

<!--NoCompile-->
<!-- 115 -->
```verse
# Takes an instance
GetCastableFinalSuperClass[BaseType, instance]:<decides>castable_subtype(BaseType)

# Takes a type
GetCastableFinalSuperClassFromType[BaseType, Type]:<decides>castable_subtype(BaseType)
```

Both return a `castable_subtype` representing the most specific `<final_super>` class that:

1. Directly inherits from the specified base type
2. Is in the inheritance chain of the instance/type

The function fails if no appropriate `<final_super>` class exists.

Consider this hierarchy:


<!--verse
vector3:=class{}
-->
<!-- 116 -->
```verse
component := class<castable>:
    ID:int

# Direct final_super subclass of component
physics_component := class<final_super>(component):
    Velocity:vector3

# Descendants of physics_component
rigid_body := class(physics_component):
    Mass:float

character_body := class(rigid_body):
    Health:int
```

Query results:


<!--versetest
entity:=class{}
vector3:=class{}
component:=class{}
character_body:=class(component){ID :int, Velocity :vector3, Mass :float, Health :int}
-->
<!-- 117 -->
```verse
# All instances in the physics_component family return physics_component
Body := character_body{ID:=1, Velocity:=vector3{}, Mass:=10.0, Health:=100}

if (Family := GetCastableFinalSuperClass[component, Body]):
    # Family = physics_component (the final_super anchor)
    # Even though Body is character_body, the family anchor is physics_component
```

The function "walks up" the inheritance chain from `character_body` → `rigid_body` → `physics_component` and stops at `physics_component` because:

1. It has `<final_super>`
2. It directly inherits from the queried base (`component`)

**When Queries Succeed and Fail?**

**Succeeds when:**

- A `<final_super>` class directly inherits from the base type
- The instance/type inherits from that `<final_super>` class

<!--versetest
base := class<castable>:
    Value:int=1
anchor := class<final_super>(base):
    Extra:string=""
derived := class(anchor){ More:string="" }
<#
-->
<!-- 118 -->
```verse
base := class<castable>:
    Value:int

anchor := class<final_super>(base):
    Extra:string

derived := class(anchor):
    More:string

# Valid: anchor is final_super of base, derived inherits from anchor
GetCastableFinalSuperClass[base, derived{}]  # Returns anchor
GetCastableFinalSuperClass[base, anchor{}]   # Returns anchor
```
<!--
#>
assert:
   GetCastableFinalSuperClass[base, derived{}]  # Returns anchor
   GetCastableFinalSuperClass[base, anchor{}]   # Returns anchor
-->

**Fails when:**

- No `<final_super>` class exists between base and instance
- The queried type itself is the instance type (cannot query from same level)
- Instance is not a subtype of the base


#### Multiple Final Supers

You can have multiple `<final_super>` classes at different levels. The
function returns the one directly inheriting from the queried base:

<!--versetest
base := class<castable>:
    ID:int=1
first_anchor := class<final_super>(base):
    Category:string=""
second_anchor := class<final_super>(first_anchor):
    Subcategory:string=""
leaf := class(second_anchor){ Specific:string="" }
<#
-->
<!-- 120 -->
```verse
base := class<castable>:
    ID:int

first_anchor := class<final_super>(base):
    Category:string

second_anchor := class<final_super>(first_anchor):
    Subcategory:string

leaf := class(second_anchor):
    Specific:string

# Query from base returns first_anchor
GetCastableFinalSuperClass[base, leaf{}]  # Returns first_anchor

# Query from first_anchor returns second_anchor
GetCastableFinalSuperClass[first_anchor, leaf{}]  # Returns second_anchor
```
<!-- 
#>
assert:
    GetCastableFinalSuperClass[base, leaf{}]  # Returns first_anchor
    GetCastableFinalSuperClass[first_anchor, leaf{}]  # Returns second_anchor
-->


This layered approach allows hierarchical categorization where
different levels represent different granularities of type families.

#### GetCastableFinalSuperClassFromType

The type-based variant works identically but takes a type instead of instance:

<!--versetest
component:=class<castable>{}
physics_component := class<final_super>(component){}
rigid_body := class(physics_component){}
-->
<!-- 123 -->
```verse
# Same behavior, different syntax
TypeFamily := GetCastableFinalSuperClassFromType[component, rigid_body]
InstanceFamily := GetCastableFinalSuperClass[component, rigid_body{}]

# Both return the same castable_subtype
```

This is useful when working with type values directly rather than instances.

### classifiable_subset

Building on the concept of runtime type queries introduced by
`castable_subtype`, Verse provides `classifiable_subset`—a
sophisticated mechanism for maintaining sets of runtime types. Where
`castable_subtype` represents a single type value,
`classifiable_subset` represents a collection of types, tracking which
classes are present in a system and supporting queries based on type
hierarchies.

This feature is particularly valuable for component-based
architectures, where you need to track which component types an entity
possesses, query for specific capabilities, or filter operations based
on type compatibility. Rather than maintaining separate boolean flags
or type tags, `classifiable_subset` provides a type-safe,
hierarchy-aware registry of runtime types.

Three related types work together to provide both immutable and
mutable type sets:

**`classifiable_subset(t)`** represents an immutable set of runtime
types, where `t` must be a `<castable>` base type. Once created, the
set cannot be modified, making it suitable for configuration,
capability descriptions, or any scenario where the type set should
remain stable.

**`classifiable_subset_var(t)`** provides a mutable variant with
`Read()` and `Write()` operations, enabling dynamic type sets that
change during program execution. This is essential for runtime systems
where component types are added or removed as entities evolve.

**`classifiable_subset_key(t)`** represents keys used to identify
specific instances when adding them to a mutable set. These keys
enable removal of specific instances later, supporting lifecycle
management of registered types.

Unlike ordinary classes, `classifiable_subset` types cannot be
directly instantiated. You must use the constructor functions
`MakeClassifiableSubset()` and `MakeClassifiableSubsetVar()`:

<!--versetest
component:=class<castable>{}
physics_component := class<final_super>(component){}
rigid_body := class(physics_component){}
render_component := class<castable>(component){}
-->
<!-- 124 -->
```verse
# Immutable set, initially empty
EmptySet:classifiable_subset(component) = MakeClassifiableSubset()

# Immutable set with initial instances
InitialSet:classifiable_subset(component) =
    MakeClassifiableSubset(array{physics_component{}, render_component{}})

# Mutable set
var DynamicSet:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
```

The base type `t` must be `<castable>`, ensuring runtime type queries
are possible. This restriction is enforced at compile time:

<!--versetest
component:=class<computes><castable>{}
f()<reads>:void =
    ComponentSet:classifiable_subset(component) = MakeClassifiableSubset()

<#
-->
<!-- 1215 -->
```verse
ComponentSet:classifiable_subset(component) = MakeClassifiableSubset()

# Invalid: non-castable types cannot be used
regular_class := class:
    Value:int

# This would be an error:
# BadSet:classifiable_subset(regular_class) = MakeClassifiableSubset()
```
<!-- #> -->

You cannot subclass these types or create instances through ordinary
construction syntax. This ensures that all sets use the proper
internal representation for efficient type queries.

#### Type Hierarchy Semantics

The crucial insight of `classifiable_subset` is that it tracks runtime
types, not individual instances. When you add an instance to the set,
the system records that instance's actual runtime type. More
importantly, type queries respect the inheritance hierarchy:


<!--versetest
entity:=class{}
vector3:=class{}
component := class<castable>{}
physics_component := class<castable>(component):
    Velocity:vector3=vector3{}

rigid_body_component := class<castable>(physics_component):
    Mass:float=0.0
-->
<!-- 126 -->
```verse
# Add a rigid body instance
Set:classifiable_subset(component) =
    MakeClassifiableSubset(array{rigid_body_component{}})

# Query results respect hierarchy
Set.Contains[component]             # true - rigid_body is a component
Set.Contains[physics_component]     # true - rigid_body is a physics_component
Set.Contains[rigid_body_component]  # true - directly present
```

This hierarchy awareness makes `classifiable_subset` fundamentally
different from a simple set of type tags. The `Contains` operation
asks "does this set contain any type that is-a T?" rather than "does
this set contain exactly T?".

When you add instances of different types, each distinct runtime type
is tracked separately:

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
rigid_body_component := class<castable>(physics_component){ }
render_component := class<castable>(component){}
audio_component := class<castable>(component){}
-->
<!-- 127 -->
```verse
# Add multiple different types
var Set:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
Key1 := Set.Add(physics_component{})
Key2 := Set.Add(render_component{})
Key3 := Set.Add(audio_component{})

Set.Contains[component]          # true - all three are components
Set.Contains[physics_component]  # true - physics_component present
Set.Contains[render_component]   # true - render_component present
```

The set remembers each distinct type that was added. When you remove an instance by its key, that specific type is removed only if it was the last instance of that type:

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
rigid_body_component := class<castable>(physics_component){ }
-->
<!-- 128 -->
```verse
# Add multiple instances of same type
var Set:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
Key1 := Set.Add(physics_component{})
Key2 := Set.Add(physics_component{})

Set.Contains[physics_component]  # true

Set.Remove[Key1]
Set.Contains[physics_component]  # still true - Key2 remains

Set.Remove[Key2]
# Set.Contains[physics_component]  # false - last instance removed
```

#### Core Operations

The `classifiable_subset` types provide several operations for
querying and manipulating type sets:

**Contains** checks whether any type in the set matches or is a
subtype of the queried type:

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}
-->
<!-- 129 -->
```verse
TheSet:classifiable_subset(component) =
    MakeClassifiableSubset(array{physics_component{}})

if (TheSet.Contains[component]):
    # Physics component is present (and is a component)

if (TheSet.Contains[render_component]):
    # No render component present
```

**ContainsAll** verifies that all types in an array are present in the set:

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}
-->
<!-- 130 -->
```verse
TheSet:classifiable_subset(component) =
    MakeClassifiableSubset(array{physics_component{}})

if (TheSet.ContainsAll[array{physics_component, render_component}]):
    # Both physics and render components are present
```

**ContainsAny** checks whether at least one type from an array is present:

<!--NoCompile-->
<!-- 131 -->
```verse
if (TheSet.ContainsAny[array{physics_component, audio_component}]):
    # Either physics or audio component (or both) is present
```

**Add** (mutable sets only) adds an instance and returns a key for later removal:


<!--versetest
component := class<castable>{ Name:string = "Component"}
physics_component := class<castable>(component){}
-->
<!-- 132 -->
```verse
var TheSet:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
Key := TheSet.Add(physics_component{})
# Can later remove using Key
```

**Remove** (mutable sets only) removes a previously added instance by its key:

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
Key:classifiable_subset(component)=component{}
-->
<!-- 133 -->
```verse
TheSet:classifiable_subset(component) =
    MakeClassifiableSubset(array{physics_component{}})

if (TheSet.Remove[Key]):
    # Successfully removed
else:
    # Key was not present (already removed or never added)
```

**FilterByType** creates a new set containing only types that are compatible (assignable to or from) the specified type:


<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}
audio_component := class<castable>(component){}
-->
<!-- 134 -->
```verse
TheSet:classifiable_subset(component) = MakeClassifiableSubset(array{
    physics_component{}, render_component{}, audio_component{}})

# Filter to physics-related types
PhysicsSet := TheSet.FilterByType(physics_component)
PhysicsSet.Contains[physics_component]  # true
PhysicsSet.Contains[render_component]   # false - unrelated sibling
PhysicsSet.Contains[component]          # true - base type compatible
```

The filtering respects both upward and downward compatibility in the
type hierarchy, keeping types that could be assigned to or from the
filter type.

**Union** combines two sets using the `+` operator:

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}
audio_component := class<castable>(component){}
entity := class{}
-->
<!-- 135 -->
```verse
Set1:classifiable_subset(component) =
    MakeClassifiableSubset(array{physics_component{}})
Set2:classifiable_subset(component) =
    MakeClassifiableSubset(array{render_component{}})

Combined := Set1 + Set2
Combined.Contains[physics_component]  # true
Combined.Contains[render_component]   # true
```

For mutable sets, the Read/Write operations enable copying and updating:

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}
audio_component := class<castable>(component){}
-->
<!-- 136 -->
```verse
var Set1:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
Set1.Add(physics_component{})

var Set2:classifiable_subset_var(component) = MakeClassifiableSubsetVar()
Set2.Write(Set1.Read())  # Copy Set1's contents to Set2
```

#### Design Considerations

Several important constraints govern `classifiable_subset` usage:

The base type must be `<castable>` to enable runtime type
queries. This requirement ensures that type checks can be performed
efficiently.

You cannot subclass `classifiable_subset` types or create instances
except through the designated constructor functions. This restriction
maintains internal invariants required for correct type tracking.

Keys from one set cannot be used with a different set—they're bound to
the specific set instance where the element was added.

The type parameter must be consistent across operations. You cannot
add a `physics_component` to a `classifiable_subset(render_component)`
even if both inherit from `component`:

<!--versetest
component := class<castable>{}
physics_component := class<castable>(component){}
render_component := class<castable>(component){}
audio_component := class<castable>(component){}
-->
<!-- 137 -->
```verse
render_set:classifiable_subset(render_component) = MakeClassifiableSubset()
physics_comp:physics_component = physics_component{}

# This would be a type error - physics_component is not a render_component
# render_set.Add(physics_comp)
```

Mutable sets require careful lifetime management. Keys become invalid
when their corresponding instances are removed, and attempting to
remove an already-removed key returns false.

Performance characteristics matter for large type sets. While
`Contains` queries are efficient due to the internal representation,
operations like `FilterByType` may need to examine each type in the
set.

When designing systems with `classifiable_subset`, consider whether
immutable or mutable sets better fit your needs. Immutable sets
provide stronger guarantees and work well for configuration, while
mutable sets support dynamic systems where component types change
frequently.

The hierarchy-aware semantics mean that adding a derived type makes
queries for base types succeed. This is usually desirable but requires
awareness—if you only want exact type matches, `classifiable_subset`
may not be the right tool.
