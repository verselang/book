# Mutability

Immutability is the default in Verse. When you create a value, it stays that value forever — unchanging, predictable, and safe to share. This foundational principle makes programs easier to reason about, eliminates entire categories of bugs, and enables powerful optimizations. But games are dynamic worlds where state constantly evolves: health decreases, scores increase, inventories change. Verse embraces both paradigms, providing immutability by default while offering controlled, explicit mutation when you need it.

The distinction between immutable and mutable data in Verse goes deeper than just whether values can change. It fundamentally affects how data flows through your program, how values are shared between functions, and how the compiler reasons about your code. Understanding this distinction is crucial for writing efficient, correct Verse programs.

## The Pure Foundation

In Verse's pure fragment, computation happens without side effects. Values are created but never modified. Functions transform inputs into outputs without changing anything along the way. This isn't a limitation — it's a powerful foundation that makes code predictable and composable.

<!--versetest
point := struct{X:float, Y:float}
Distance(P1:point, P2:point)<reads>:float =
    DX := P2.X - P1.X
    DY := P2.Y - P1.Y
    Sqrt(DX * DX + DY * DY)

assert:
    Origin := point{X:=0.0, Y:=0.0}
    UnitX := point{X := 1.0, Y:=0.0}
    UnitY := point{X:=0.0, Y := 1.0}
<#
-->
<!-- 01 -->
```verse
# Immutable values and structures
point := struct<computes>:
    X:float = 0.0
    Y:float = 0.0

Origin := point{}
UnitX := point{X := 1.0}
UnitY := point{Y := 1.0}

# These values are eternal - Origin will always be (0, 0)
Distance(P1:point, P2:point)<reads>:float =
    DX := P2.X - P1.X
    DY := P2.Y - P1.Y
    Sqrt(DX * DX + DY * DY)
```
<!-- #> -->

In this pure world, equality means structural equality — two values are equal if they have the same shape and content. For primitive types and structs, this happens automatically. For classes, which have identity beyond their content, equality requires more careful consideration.

<!--versetest-->
<!-- 02 -->
```verse
# Recursive data structures using classes
linked_list := class:
    Value:int = 0
    Next:?linked_list = false

    # Custom equality check for structural comparison
    Equals(Other:linked_list)<computes><decides>:void =
        Self.Value = Other.Value
        # Both have no next, or both have next and those are equal
        if (Self.Next?):
            Tmp := Self.Next?
            OtherNext := Other.Next?
            Tmp.Equals[OtherNext]
        else:
            not Other.Next?

List1 := linked_list{Value := 1, Next := option{linked_list{Value := 2}}}
List2 := linked_list{Value := 1, Next := option{linked_list{Value := 2}}}

List1.Equals[List2] # This succeeds
```

Pure computation forms the backbone of functional programming in Verse. It's predictable, testable, and parallelizable. When a function is marked `<computes>`, you know it will always produce the same output for the same input, with no hidden dependencies or surprising behaviors.

## Introducing Mutation

Mutation enters through two keywords: `var` and `set`. The `var` annotation declares that a variable can be reassigned. The `set` keyword performs that reassignment. Together, they provide controlled mutation with clear visibility.

<!--versetest-->
<!-- 03 -->
```verse
Score:int = 100   # Immutable variable - cannot be reassigned
                  # Mutable variable - can be reassigned 
var Health:float = 100.0       # type annotation is required
set Health = 75.0              # Allowed
```

Every use of `var` and `set` has implications for effects. Reading from a `var` variable requires the `<reads>` effect. Using `set` requires both `<reads>` and `<writes>` effects. This isn't bureaucracy — it's transparency. The effects make mutation visible in function signatures, so callers know when functions might observe or modify state.

### Requirements for var Declarations

Mutable variable declarations have strict requirements that prevent common errors:

**Must provide explicit type:**

<!--versetest-->
<!-- 04 -->
```verse
# Valid - explicit type
var X:int = 0

# Invalid - cannot use := syntax with var
# var X := 0  # Error
```

The type inference syntax `:=` cannot be used with `var`. You must explicitly declare the type.

**Must provide initial value (in local scope):**

<!--versetest-->
<!-- 05 -->
```verse
# Valid - initialized
var Health:float = 100.0

# Invalid - no initial value in local scope
# var Score:int  # Error
```

In local scopes (functions, control flow blocks), every `var` declaration requires an initial value. However, when declaring mutable fields in classes or interfaces, the initial value can be omitted and provided during instantiation (see the Classes and Interfaces chapter for details).

**Cannot be completely untyped:**

<!--versetest
assert_semantic_error(3502):
    F():void=
        var X
<#
-->
<!-- 06 -->
```verse
# Invalid - neither type nor value
# var X  
```
<!-- #> -->

### var Declarations as Expressions

Variable declarations with `var` can be used as expressions, evaluating to their initial value:

<!--versetest-->
<!-- 07 -->
```verse
X := (var Y:int = 42)  # X = 42, Y declared and mutable
X = 42
```

However, `var` declarations **cannot be the target of `set`**:

<!--versetest
assert_semantic_error(3509):
    F():void=
        set (var Z:int = 0) = 1
<#
-->
<!-- 08 -->
```verse
# Invalid - var declarations evaluate to values, not variables
# set (var Z:int = 0) = 1  # Error: cannot use set on a value
```
<!-- #> -->

Since `var` declarations return their initial value as an expression result, you cannot use `set` on them - `set` requires a mutable variable, not a value.

### set with Block Expressions

The `set` statement can use block expressions, which allows complex computations and side effects:

<!--versetest-->
<!-- 09 -->
```verse
var X:int = 0
var Y:int = 1

set X = block:
    set Y = X      # Side effect: Y becomes 0
    2              # Block result: X becomes 2

X = 2 and Y = 0
```

This pattern is useful when the new value requires intermediate computations or when you need multiple side effects during assignment.

**Important:** The left-hand side of `set` is evaluated before the block executes, and the block's return value is what gets assigned. This can lead to confusing behavior in certain cases:

<!--versetest-->
<!-- 10 -->
```verse
# Confusing: Setting the same variable inside the block
var X:int = 0
set X = block:
    set X = 5  # X temporarily becomes 5
    2          # But X will be set to 2 (the block result)
X = 2          # The inner set was overwritten!

# Confusing: Modifying index variables used in array access
var Xs:[]int = array{10, 20, 30}
var Index:int = 1
set Xs[Index] = block:
    set Index = 2  # Index changes, but doesn't affect which element is set
    99
Xs[1] = 99         # Element at original Index (1) was modified, not Xs[2]
Index = 2          # Index is now 2, but too late to affect the assignment
```

To avoid confusion, it's best to avoid modifying the target variable or any variables used in the target expression inside the block.

### Scope and Redeclaration Restrictions

**No Variable Shadowing:**

Verse does not allow variable shadowing. Once an identifier is declared, you cannot redeclare it with `:=` anywhere in the same scope or any nested scope. This is more restrictive than many languages that allow inner scopes to shadow outer scope variables.

<!--versetest-->
<!-- 11 -->
```verse
var X:int = 0

# Invalid - X already exists in current scope
# X := 1  # Error
```

Unlike many languages, you cannot shadow variables even in nested blocks:

<!--versetest
SomeCondition:logic=false
-->
<!-- 12 -->
```verse
var A:int = 1

if (SomeCondition?):
    # Invalid - A already declared in outer scope
    # A := 2  # Error: cannot shadow A

block:
    # Also invalid - cannot shadow here either
    # var A:int = 2  # Error: ambiguous identifier
```

If you need multiple identifiers with similar purposes, use descriptive names (e.g., `InitialHealth`, `CurrentHealth`) or use qualified names to create separate scopes (see the [Modules and Paths](16_modules.md) chapter for details on qualified names and disambiguation).

**Cannot redeclare with assignment syntax:**

<!--versetest-->
<!-- 13 -->
```verse
var A:int = 1
var B:int = 2

# Invalid - looks like assignment but A already exists
# A := B  # ERROR
```

Use `set A = B` instead to assign to existing mutable variables.

**Cannot nest var declarations:**

<!--versetest
assert_semantic_error(3549):
    var (var X):int = 0
<#
-->
<!-- 14 -->
```verse
# Invalid
# var (var X):int = 0  # ERROR 3549
```
<!-- #> -->

The `var` keyword cannot be nested within itself.

## Deep vs Shallow Mutability

Verse's approach to mutability differs significantly between structs and classes, reflecting their different roles in the language.

### Struct Mutability: Deep and Structural

When you declare a struct variable with `var`, you're declaring the entire structure as mutable — the variable itself and all its nested fields, recursively. This deep mutability means you can modify any part of the structure tree.

<!--versetest
point:=struct<computes>{X:float, Y:float}
player_stats := struct<computes>:
    Level:int = 1
    Position:point = point{X:=0.0, Y:=0.0}
    Inventory:[]string = array{}

assert:
    Stats1:player_stats = player_stats{}
    var Stats2:player_stats = player_stats{}
    set Stats2.Level = 2
    Stats2.Level = 2
    set Stats2.Position.X = 100.0
    Stats2.Position.X = 100.0
    set Stats2.Inventory = Stats2.Inventory + array{"Sword"}
    Stats2.Inventory = array{"Sword"}
<#
-->
<!-- 15 -->
```verse
player_stats := struct<computes>:
    Level:int = 1
    Position:point = point{}
    Inventory:[]string = array{}

# Immutable struct variable - nothing can change
Stats1:player_stats = player_stats{}
# set Stats1.Level = 2  # ERROR: Cannot modify immutable struct

# Mutable struct variable - everything can change
var Stats2:player_stats = player_stats{}
set Stats2.Level = 2  # OK
set Stats2.Position.X = 100.0  # OK - nested fields are mutable
set Stats2.Inventory = Stats2.Inventory + array{"Sword"}  # OK
```
<!-- #> -->

When you assign one struct variable to another, Verse performs a deep copy. The two variables become independent, each with their own copy of the data. Changes to one don't affect the other.

<!--versetest
point:=struct<computes>{}
player_stats := struct<computes>:
    Level:int = 1
    Position:point = point{}
    Inventory:[]string = array{}

-->
<!-- 16 -->
```verse
var Original:player_stats = player_stats{Level := 5}
var Copy:player_stats = Original

set Copy.Level = 10
Original.Level = 5   # unchanged, they're independent copies
```

This deep-copy semantics extends to all value types: structs, arrays, maps, and tuples. When you pass a struct to a function, the function receives its own copy. When you store a struct in a container, the container holds a copy. This prevents aliasing and makes reasoning about struct mutations local and predictable.

### Class Mutability: Reference Semantics

Classes behave differently. They have reference semantics — when you assign a class instance, you're sharing a reference to the same object, not creating a copy. The `var` annotation on a class variable only affects whether that variable can be reassigned to reference a different object. It doesn't affect the mutability of the object's fields.

<!--versetest
game_character := class:
    Name:string = "Hero"
    var Health:float = 100.0
    MaxHealth:float = 100.0

assert:
    Player1:game_character = game_character{}
    set Player1.Health = 50.0
    Player1.Health = 50.0
    var Player2:game_character = Player1
    set Player2 = game_character{Name := "Villain"}
    Player2.Name = "Villain"
    set Player2.Health = 75.0
    Player2.Health = 75.0
<#
-->
<!-- 17 -->
```verse
game_character := class:
    Name:string = "Hero"
    var Health:float = 100.0  # This field is always mutable
    MaxHealth:float = 100.0   # This field is always immutable

# Immutable variable, but mutable fields can still change
Player1:game_character = game_character{}
# set Player1 = game_character{}  # ERROR: Cannot reassign non-var variable
set Player1.Health = 50.0  # OK: Health field is mutable

# Mutable variable allows reassignment
var Player2:game_character = Player1  # Same object
set Player2 = game_character{Name := "Villain"}  # OK: Can reassign
set Player2.Health = 75.0  # OK: Modifies the new object

# Player1 and the original Player2 reference were the same object
# After reassignment, Player2 references a different object
```
<!-- #> -->

The key insight: for classes, field mutability is determined at class definition time, not at variable declaration time. A `var` field is always mutable, regardless of how you access it. A non-`var` field is always immutable, even if accessed through a `var` variable.

<!--versetest
point:=struct<computes>{X:float}
container := class:
    ImmutableData:point= point{X:=1.0}
    var MutableData:int = 0
assert:
    Box:container = container{}
    set Box.MutableData = 42
    Box.MutableData = 42
<#
-->
<!-- 18 -->
```verse
container := class:
    ImmutableData:point= point{}  # Always immutable
    var MutableData:int = 0       # Always mutable

# Even through an immutable variable, mutable fields can change
Box:container = container{}
set Box.MutableData = 42         # Allowed
# set Box.ImmutableData = Point{X := 1.0}  # ERROR: Field is immutable
```
<!-- #> -->

### Collection Mutability: Arrays and Maps

Arrays and maps follow struct semantics—they are values, not references. When you copy a collection, you get an independent copy. Mutations to one copy don't affect the other.

#### Basic Array Mutation

Mutable arrays allow element replacement:

<!--versetest-->
<!-- 19 -->
```verse
var Nums:[]int = array{0, 1}
Nums[0] = 0
Nums[1] = 1

set Nums[0] = 42
Nums[0] = 42
Nums[1] = 1  # Unchanged

set Nums[1] = 666
Nums[0] = 42
Nums[1] = 666
```

You cannot add elements beyond the array's current length:

<!--versetest-->
<!-- 20 -->
```verse
var A:[]int = array{0}
not (set A[1] = 1)  # Fails - index out of bounds
# Must use concatenation: set A = A + array{1}
```

#### Basic Map Mutation

Mutable maps allow both updating existing keys and adding new keys:

<!--versetest-->
<!-- 21 -->
```verse
var Scores:[int]int = map{0 => 1, 1 => 2}
set Scores[1] = 42
Scores[1] = 42

# Adding new keys
set Scores[2] = 100
Scores[2] = 100

# Map with string keys
var Config:[string]int = map{"volume" => 50}
set Config["brightness"] = 75
```

Looking up a non-existent key doesn't add it:

<!--versetest-->
<!-- 22 -->
```verse
M:[int]int := map{}
not (M[0] = 0)  # Key doesn't exist, comparison fails
# M is still empty - lookup didn't add the key
```

**Deleting keys from maps:**

Verse does not have a direct "delete" or "remove" operation for maps. To remove keys, create a new map that excludes the unwanted keys by iterating over the original map:

<!--versetest-->
<!-- 23 -->
```verse
var Scores:[string]int = map{"Alice" => 100, "Bob" => 85, "Charlie" => 92}

# Remove "Bob" by creating a new map without that key
var NewScores:[string]int = map{}
for (Name->Score:Scores):
    if (Name <> "Bob"):
        set NewScores[Name] = Score

set Scores = NewScores

# Scores now only contains Alice and Charlie
Scores["Alice"] = 100
Scores["Charlie"] = 92
```

This pattern can be wrapped in a helper function for reusability. See the [Control Flow](07_control.md) chapter for more details on `for` loops.

#### Nested Collection Mutation

Collections can be nested, and `set` works through multiple levels:

**Map of arrays:**

<!--versetest-->
<!-- 24 -->
```verse
var Data:[int][]int = map{}
set Data[666] = array{42}
Data[666] = array{42}

# Mutate nested array element
set Data[666][0] = 1234
Data = map{666 => array{1234}}
Data[666] = array{1234}
```

**Array of maps:**

<!--versetest-->
<!-- 25 -->
```verse
var Grid:[][int]int = array{map{}}

# Replace entire map at index
set Grid[0] = map{42 => 666}
Grid[0] = map{42 => 666}
Grid[0][42] = 666

# Add new key to nested map
set Grid[0][1234] = 4321
Grid[0] = map{42 => 666, 1234 => 4321}
Grid[0][42] = 666
Grid[0][1234] = 4321

# Update existing key in nested map
set Grid[0][42] = 1122
Grid[0][42] = 1122
```

**Array of arrays:**

<!--versetest-->
<!-- 26 -->
```verse
var Matrix:[][]int = array{array{1234}}
set Matrix[0][0] = 42
Matrix = array{array{42}}
Matrix[0] = array{42}
Matrix[0][0] = 42

# Replace inner array
set Matrix[0] = array{666}
Matrix[0] = array{666}
Matrix[0][0] = 666
```

All nested levels should exist to use `set`, if any of the higher levels don't exist, the entire set will fail.

<!--versetest-->
<!-- 27 -->
```verse
var Grid:[string][]int = map{"apples"=>array{1,2,3,4}}

set Grid["bananas"] = array{}  # OK - no nesting, just adds new key
set Grid["apples"][2] = 7      # OK - changes nested array element "3" to "7"

# This would fail: set Grid["oranges"][0] = 10
# Error: "oranges" key doesn't exist, so Grid["oranges"] fails
```

#### Value Semantics for Collections

Extracting a value from a mutable collection creates an independent copy:

<!--versetest-->
<!-- 28 -->
```verse
var X:[][int]int = array{map{42 => 1122, 1234 => 4321}}

# Y gets a copy of the map, not a reference
Y := X[0]
Y = map{42 => 1122, 1234 => 4321}

# Mutating X doesn't affect Y
set X[0][0] = 111
X[0] = map{42 => 1122, 1234 => 4321, 0 => 111}
Y = map{42 => 1122, 1234 => 4321}  # Unchanged

# Replacing entire element doesn't affect Y
set X[0] = map{42 => 4242}
X[0] = map{42 => 4242}
Y = map{42 => 1122, 1234 => 4321}  # Still unchanged
```

This is different from class reference semantics—collections copy, classes share.

#### Collections with Mutable Values

When collections contain classes or structs with mutable fields, you can mutate through the collection:

<!--versetest
the_class := class:
    var X:[]int = array{0}
-->
<!-- 29 -->
```verse
C := the_class{}
set C.X[0] = 4266642
C.X[0] = 4266642
```

**Map values with mutable members:**

<!--versetest
class0 := class:
    var AM:int = 20
-->
<!-- 30 -->
```verse
var M:[int]class0 = map{0 => class0{}}
M[0].AM = 20

# Mutate class field through map
set M[0].AM = 30
M[0].AM = 30
```

The map constructed from a `var` doesn't track changes to the source variable:

<!--versetest-->
<!-- 31 -->
```verse
var I0:int = 42
M:[int]int = map{0 => I0}
M[0] = 42

set I0 = 0
M[0] = 42  # Still 42! Map has a copy of the value
```


### Arrays of Structs: Independent Copies

When you store structs in an array, each element is an independent copy:

<!--versetest
my_struct := struct<computes>:
    I:int = 10
-->
<!-- 32 -->
```verse
S := my_struct{I := 88}
var A : []my_struct = array{S, S}

# All three have the value 88, but are independent
S.I = 88
A[0].I = 88
A[1].I = 88

# Mutating one doesn't affect the others
set A[0].I = 99
S.I = 88     # Unchanged
A[0].I = 99  # Changed
A[1].I = 88  # Unchanged
```

### Arrays of Classes: Shared References

Arrays of classes behave very differently—all references to the same object share mutations:

<!--versetest
my_class := class:
    var I:int = 20
-->
<!-- 33 -->
```verse
C := my_class{}
var A:[]my_class = array{C, C, C}

# All three array elements reference the same object
A[0].I = 20
A[1].I = 20
A[2].I = 20

# Mutating through one affects all references
set A[0].I = 30
A[0].I = 30
A[1].I = 30  # Changed!
A[2].I = 30  # Changed!

set A[1].I = 40
A[0].I = 40  # All three see the change
A[1].I = 40
A[2].I = 40

# Replacing an element breaks the sharing for that element
set A[1] = my_class{}
A[0].I = 40  # Still references original
A[1].I = 20  # New object with default value
A[2].I = 40  # Still references original
```

This is a critical distinction: **structs in collections are copies, classes in collections are shared references**.

### Compound Assignment Operators

Verse supports compound assignment operators that combine arithmetic with mutation:

<!--versetest
struct0 := struct<computes>:
    A:int = 10
-->
<!-- 34 -->
```verse
var S0:struct0 = struct0{}

set S0.A += 10
S0.A = 20

set S0.A -= 3
S0.A = 17

set S0.A *= 4
S0.A = 68
```

Available compound operators:

- `set += ` - Addition assignment (int, float, string, array)
- `set -= ` - Subtraction assignment (int, float)
- `set *= ` - Multiplication assignment (int, float)
- `set /= ` - Division assignment (float only)

**Important**: `set /=` doesn't work with integers because integer division is failable.

Compound assignments work anywhere regular assignment does:

<!--versetest-->
<!-- 35 -->
```verse
var Score:int = 100
set Score += 50
set Score *= 2

var Data:[]int = array{1, 2, 3}
set Data += array{4, 5}  # Array concatenation
Data = array{1, 2, 3, 4, 5}

var Nums:[][]int = array{array{1}}
set Nums[0][0] *= 42
Nums[0][0] = 42
```

### Tuple Mutability: Replacement Only

Tuples can be replaced entirely but individual elements cannot be mutated:

<!--versetest-->
<!-- 36 -->
```verse
var T0:tuple(int, int) = (10, 20)
T0(0) = 10
T0(1) = 20

# Can replace entire tuple
set T0 = (30, 40)
T0(0) = 30
T0(1) = 40
```

**Cannot mutate elements:**

<!--versetest
assert_semantic_error(3509):
    TestTupleMutation()<transacts>:void =
        var T0:tuple(int, int) = (50, 60)
        set T0(0) = 70
<#
-->
<!-- 37 -->
```verse
var T0:tuple(int, int) = (50, 60)
set T0(0) = 70  # ERROR: Cannot mutate tuple elements
```
<!-- #> -->

This restriction applies even when the tuple is mutable. You must replace the entire tuple to change its contents.

### Map Ordering and Mutation

Maps preserve **insertion order**, and this order is maintained through mutations:

#### New Keys Append to End

<!--versetest-->
<!-- 38 -->
```verse
var M:[int]int = map{2 => 2}

set M[1] = 1  # Appends to end
set M[0] = 0  # Appends to end

# Iteration order is insertion order: 2, 1, 0
Keys := array{2, 1, 0}
var Index:int = 0
for (Key->Value : M):
    Keys[Index] = Key
    set Index += 1

M = map{2 => 2, 1 => 1, 0 => 0}
```

#### Updating Existing Keys Preserves Position

<!--versetest-->
<!-- 39 -->
```verse
var M:[string]int = map{"a" => 3, "b" => 1, "c" => 2}

# Mutating value keeps key position
set M["a"] = 0
M = map{"a" => 0, "b" => 1, "c" => 2}  # Same order

# Another update
set M["c"] = 0
set M["a"] = 2
M = map{"a" => 2, "b" => 1, "c" => 0}  # Still same order
```

#### Order Matters for Equality

Map equality considers both keys/values **and order**:

<!--versetest-->
<!-- 40 -->
```verse
var M:[string]int = map{"a" => 3, "b" => 1, "c" => 2}
set M["a"] = 0

# Same keys and values, same order = equal
M = map{"a" => 0, "b" => 1, "c" => 2}

# Same keys and values, different order = not equal
M <> map{"b" => 1, "c" => 2, "a" => 0}
```

## Critical Mutability Restrictions

Verse imposes several important restrictions on where and how mutation can occur. These aren't arbitrary—they prevent unsound behaviors and maintain type safety.

### Cannot Mutate Immutable Class Fields

Classes might contain unique pointers or other resources that cannot be safely cloned. Therefore, you cannot mutate immutable fields of a class instance:

<!--versetest
assert_semantic_error(3509):
    classX := class:
        AI:int = 20

    F()<transacts>:void=
        CX:classX = classX{}
        set CX.AI = 30
<#
-->
<!-- 41 -->
```verse
classX := class:
    AI:int = 20  # Immutable field

CX:classX = classX{}
CX.AI = 20
set CX.AI = 30  # Error: Cannot mutate immutable class field
```
<!-- #> -->

This restriction applies even when the class instance itself is mutable. Only `var` fields of classes can be mutated.

### Only <computes> Structs Allow Field Mutation

Only structs marked `<computes>` (pure structs) allow field mutation through a variable:

<!--versetest-->
<!-- 42 -->
```verse
# OK: <computes> struct allows field mutation
my_mutable_struct := struct<computes>{M:int = 0, J:float = 3.0}

var S:my_mutable_struct = my_mutable_struct{}

Old := S # makes a copy of the struct

set S.M = 1 # makes a copy of the struct, but updates `M` in the process

S.M = 1 # Succeeds
not (Old = S) # Structs do not pass as references
```

When a new struct is constructed, it is assigned the updated value and copied other fields.
If there is other places referencing the old struct, they will not have the updated values (unlike classes)

This restriction ensures that only predictable, effect-free structs can be mutated.

### Cannot Mutate Through Immutable Class Fields

When mutating nested structures, you cannot mutate through an immutable field of a class (a field not declared with `var`):

<!--versetest
assert_semantic_error(3509):
    inner_struct := struct<computes>{Value:int = 0}
    immutable_class := class:
        Field:inner_struct = inner_struct{}
    outer_struct := struct<computes>:
        C:immutable_class

    F()<transacts>:void=
        var S:outer_struct = outer_struct{C := immutable_class{}}
        set S.C.Field.Value = 10
<#
-->
<!-- 43 -->
```verse
struct0 := struct<computes>{A:int = 10}
struct1 := struct<computes>{S0:struct0 = struct0{}}
class0 := class{CI:struct1 = struct1{}}  # Class with immutable field CI
struct2 := struct<computes>{C0:class0 = class0{}}
struct3 := struct<computes>{S2:struct2 = struct2{}}

var S3:[]struct3 = array{struct3{}, struct3{}}
set S3[1].S2.C0.CI.S0.A = 7  # ERROR: Cannot mutate through immutable field CI
```
<!-- #> -->

The error occurs because `CI` is an immutable field (not declared with `var`). **However**, you CAN mutate through `var` fields of a class in the mutation path.

Even with a mutable index, you cannot mutate an immutable array:

<!--NoCompile-->
<!-- 44 -->
```verse
var I:int = 2  # Mutable index
A:[]int = array{5, 6, 7}  # Immutable array
set A[I] = 2  # ERROR: A is not var - mutability of I doesn't matter
```

The array itself must be declared `var` to allow element mutation:

<!--versetest-->
<!-- 45 -->
```verse
I:int = 2
var A:[]int = array{5, 6, 7}
set A[I] = 2  # OK: A is var
```

## Identity and Uniqueness

The `<unique>` specifier gives classes identity-based equality. Without it, classes can't be compared for equality at all (you'd need to write custom comparison methods). With it, equality means identity — two references are equal only if they refer to the exact same object.

<!--versetest
unique_item := class<unique>:
    var Count:int = 0
assert:
    Item1:unique_item = unique_item{}
    Item2:unique_item = Item1
    Item3:unique_item = unique_item{}
    Item1 = Item2
    not (Item1 = Item3)
<#
-->
<!-- 46 -->
```verse
unique_item := class<unique>:
    var Count:int = 0

Item1:unique_item = unique_item{}
Item2:unique_item = Item1  # Same object
Item3:unique_item = unique_item{}  # Different object

if (Item1 = Item2):
    Print("Same object")  # This prints

if (Item1 = Item3):
    Print("Same object")  # This doesn't print - different objects
```
<!-- #> -->

This identity-based equality is crucial for game objects that need distinct identities even when their data is identical. Two monsters might have the same stats, but they're still different monsters.
