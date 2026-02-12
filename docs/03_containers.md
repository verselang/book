# Container Types

Container types in Verse manage collections and structured data. Optionals represent values that may or may not be present. Tuples group multiple values of different types into ordered sequences. Arrays hold zero or more values with efficient indexed access. Maps associate keys with values for fast lookups. Weak maps extend regular maps with weak reference semantics for persistent storage.

Let's explore each container type in detail, starting with optionals that elegantly handle the presence or absence of values.

## Optionals

An optional is an immutable container that either holds a value of type `t` or nothing at all. The type is written `?t`. Optionals are useful whenever a value may or may not be present, such as when looking up a key in a map or calling a function that can fail. By making this possibility explicit in the type, Verse allows programmers to handle "no result" situations directly and consistently, instead of relying on ad hoc error codes or special values.

You can create a non-empty optional with `option{...}`, which wraps a value into an optional. For example:

<!--versetest-->
<!-- 01 -->
```verse
A:?int = option{42}    # an optional containing the integer 42
```

If you want to represent "no value," you use the special constant `false`. This is how Verse spells the empty optional:

<!--versetest-->
<!-- 02 -->
```verse
var B:?int = false     # this optional has no element
B = false              # still empty
```

To extract the element of an optional, you write `?` after the optional expression. This produces a `<decides>` expression that succeeds if the optional has an element and fails otherwise. For example:

<!--versetest
A:?int = option{42}
-->
<!-- 03 -->
```verse
S := A? + 2            # succeeds with 44 because A contains 42
```

If `A` had been `false`, then the attempt to use `A?` would fail and so would the whole computation. A failing case makes this clearer:

<!--versetest
B:?int = false
-->
<!-- 04 -->
```verse
X := B? + 1            # Fails because B is false and has no element
```

This shows how Verse integrates optionals tightly with the effect system: the presence or absence of a value can cause an entire computation to succeed or fail.

The `option{...}` form also works in the opposite direction. When you have a computation with the `<decides>` effect, wrapping it in `option{...}` converts it to an optional. On success you get a non-empty optional; on failure you get `false`:

<!--versetest
GetAFloatOrFail()<transacts><decides>:float = 3.14
-->
<!-- 05 -->
```verse
MaybeAFloat := option{GetAFloatOrFail[]}
```

This symmetry is important. The `?` operator unwraps an optional into a `<decides>` expression, while `option{...}` wraps a `<decides>` expression into an optional. Together they provide a smooth bridge between computations that may fail and values that may be absent.

Although an optional value itself is immutable, you can keep one in a variable and change which optional the variable points to. The keyword `set` is used for this:

<!--versetest-->
<!-- 06 -->
```verse
var C:?int = false
set C = option{2}      # C now refers to an optional containing 2
C? = 2                 # succeeds, since C is not empty
```

This ability is useful whenever you want to track success or failure over time, such as gradually computing a result and updating the variable only when you succeed.

A common use case is searching for something that may or may not be there. Imagine a function `Find` that looks through an array of integers and returns the index of the element you want. If the element exists, the function returns `option{index}`; if not, it returns `false`. The caller can then safely decide what to do:

<!--versetest
NumberArray:[]int = array{10, 20, 30}
-->
<!-- 07 -->
```verse
Find(N:[]int, X:int):?int =
    for (I := 0..N.Length-1):
        if (N[I] = X) then return option{I}
    return false
    
Idx:?int = Find(NumberArray, 20)    # returns option{1}
Y := Idx?                           # unwraps the optional
Y = 1
```

Here the optional signals the possibility of failure directly in the type. The `?` operator makes it easy to use the result in an expression, while `option{...}` allows you to turn conditional computations back into optionals. The effect is that the idea of "maybe a value, maybe not" becomes a first-class part of the language, rather than an afterthought, and programmers are encouraged to handle the absence of values in a disciplined way.

## Tuple

A tuple is a container that groups two or more values. Unlike arrays, Tuples allow you to combine values of mixed types and treat them as a unit. The elements of a tuple appear in the order in which you list them, and you access them by their position, called the index. Because the number of elements is always known at compile time, a tuple is both simple to create and safe to use.

The term *tuple* is a back formation from *quadruple*, *quintuple*, *sextuple*, and so on. Conceptually, a tuple is like an unnamed data structure with ordered fields, or like a fixed-size array where each element may have a different type.

A tuple literal is written by enclosing a comma-separated list of expressions in parentheses. For example:

<!--versetest-->
<!-- 08 -->
```verse
Tuple1 := (1, 2, 3)
```

The order of elements matters, so `(3, 2, 1)` is a completely different value. Since tuples allow mixed types, you might write:

<!--versetest-->
<!-- 09 -->
```verse
Tuple2 := (1, 2.0, "three")
```

Tuples can also nest inside each other:

<!--versetest-->
<!-- 10 -->
```verse
X:tuple(int,tuple(int,float,string),string) = (1, (10, 20.0, "thirty"), "three")
```

Tuples are useful when you want to return multiple values from a function or when you want a lightweight grouping of values without the overhead of defining a struct or class. The type of a tuple is written with the `tuple` keyword followed by the types of the elements, but in most cases it can be inferred. For instance, you can write `MyTuple : tuple(int, float, string) = (1, 2.0, "three")`, or simply `MyTuple := (1, 2.0, "three")` and let the compiler deduce the type.

The elements of a tuple are accessed using a zero-based index operator written with parentheses. If `MyTuple := (1, 2.0, "three")`, then `MyTuple(0)` is the integer `1`, `MyTuple(1)` is the float `2.0`, and `MyTuple(2)` is the string `"three"`. Because the compiler knows the number of elements in every tuple, tuple indexing cannot fail: any attempt to use an out-of-bounds index results in a compile-time error.

Another feature of tuples is *expansion*. When a tuple is passed to a function as a single argument, its elements are automatically expanded as if the function had been called with each element separately. For example:

<!--versetest-->
<!-- 11 -->
```verse
F(Arg1:int, Arg2:string):void =
    Print("{Arg1}, {Arg2}")

G():void =
    MyTuple := (1, "two")
    F(MyTuple)   # expands to F(1, "two")
```

Tuples also play a role in structured concurrency. The `sync` expression produces a tuple of results, allowing several computations that unfold over time to be evaluated simultaneously. In this way, tuples provide not only a convenient grouping mechanism but also a foundation for composing concurrent computations.

## Arrays

An array is an immutable container that holds zero or more values of the same type `t`. The elements of an array are ordered, and each can be accessed by a zero-based index. Arrays are written with square brackets in their type, for example `[]int` or `[]float`, and are created with the `array{...}` literal form. For instance, `A : []int = array{}` creates an empty array, while `B : []int = array{1, 2, 3}` creates an array of three integers. Accessing elements by index is a failable operation: `B[0]` succeeds with the value `1`, while `B[10]` fails because the index is out of bounds.

Arrays can be concatenated with the `+` operator, and when declared as `var` they can be extended with the shorthand operator `+=`. For example, `var C:[]int= B + array{4}` gives `C` the value `array{1,2,3,4}`, and `set C += array{5}` updates it to `array{1,2,3,4,5}`. The length of an array is available through the `.Length` member, so `C.Length` here would be `5`. Elements are always stored in the order they are inserted, and indexing starts at `0`. Thus `array{10,20,30}[0]` is `10`, and the last valid index of any array is always one less than its length.

Although arrays themselves are immutable, variables declared with `var` can be reassigned to new arrays, or can appear to have their elements changed. For example, `var D:[]int = array{1,2,3}` allows the update `set D[0] = 3`, after which `D` will hold `array{3,2,3}`. What actually happens is that a brand new array is created under the hood, with the specified element updated. In effect, `set D[0] = 3` is compiled into `set D = array{3,D[1],D[2]}`. The old array continues to exist if another variable was referencing it, which means that if `A` and `B` both start as `array{1}` and we update `A[0]`, then `A` and `B` will diverge: `A[0]` is now `2` while `B[0]` is still `1`.

Arrays are useful whenever you want to store multiple values of the same type, such as a list of players in a game: `Players:[]player = array{Player1,Player2}`. Access is by index, for example `Players[0]` is the first player. Since indexing is failable, it is often combined with `if` expressions or iteration. For instance, the following code safely prints out every element of an array:

<!--versetest-->
<!-- 12 -->
```verse
ExampleArray : []int = array{10, 20, 30}
for (Index := 0..ExampleArray.Length - 1):
    if (Element := ExampleArray[Index]):
        Print("{Element} in ExampleArray at index {Index}")
```

produces

```
10 in ExampleArray at index 0
20 in ExampleArray at index 1
30 in ExampleArray at index 2
```

Because arrays are values, "changing" them always means replacing the old array with a new one. With `var` this feels natural, since variables can be reassigned. For example, you can concatenate arrays and then update an element:

<!--versetest-->
<!-- 13 -->
```verse
Array1 : []int = array{10, 11, 12}
var Array2 : []int = array{20, 21, 22}
set Array2 = Array1 + Array2 + array{30, 31}
if (set Array2[1] = 77) {}
```

After this code runs, iterating through `Array2` prints `10, 77, 12, 20, 21, 22, 30, 31`.

Arrays can also be nested to form multi-dimensional structures, similar to rows and columns of a table. For example, the following creates a two-dimensional 4×3 array of integers:

<!--versetest-->
<!-- 14 -->
```verse
var Counter : int = 0
Example : [][]int =
    for (Row := 0..3):
        for (Column := 0..2):
            set Counter += 1
```

This array can be visualized as

```
Row 0:  1  2  3
Row 1:  4  5  6
Row 2:  7  8  9
Row 3: 10 11 12
```

and is accessed with two indices: `Example[0][0]` is `1`, `Example[0][1]` is `2`, and `Example[1][0]` is `4`. You can loop through all rows and columns with nested iteration. Arrays in Verse are not restricted to rectangular shapes: each row can have a different length, producing a jagged structure. For example,

<!--versetest-->
<!-- 15 -->
```verse
Example : [][]int =
    for (Row := 0..3):
        for (Column := 0..Row):
            Row * Column
```

produces a triangular array with rows of increasing length: row 0 has none, row 1 has a single `0`, row 2 has `0, 2, 4`, and row 3 has `0, 3, 6, 9`.

Nested arrays with complex initialization work naturally as class field defaults:

<!--versetest
tile_class := class:
    Position:tuple(int, int)
    var IsOccupied:logic = false

game_board := class:
    Tiles:[][]tile_class =
        for (Y := 0..9):
            for (X := 0..9):
                tile_class{Position := (X, Y)}

    GetTile(X:int, Y:int)<computes><decides>:tile_class =
        Row := Tiles[Y]
        Row[X]
assert:
<# 
-->
<!-- 16 -->
```verse
# Game board with tile grid
tile_class := class:
    Position:tuple(int, int)
    var IsOccupied:logic = false

game_board := class:
    # Initialize 10×10 grid of tiles
    Tiles:[][]tile_class =
        for (Y := 0..9):
            for (X := 0..9):
                tile_class{Position := (X, Y)}

    # Get tile at specific position
    GetTile(X:int, Y:int)<computes><decides>:tile_class =
        Row := Tiles[Y]
        Row[X]

# Create board instance
Board := game_board{}

# Access specific tile
if (CenterTile := Board.GetTile[5, 5]):
    set CenterTile.IsOccupied = true
```
<!--
#>
   Board := game_board{}
   if (CenterTile := Board.GetTile[5, 5]):
       set CenterTile.IsOccupied = true
-->

When you create an empty array with `array{}`, Verse infers the element type from the variable's type annotation:

<!--versetest-->
<!-- 17 -->
```verse
IntArray : []int = array{}       # Empty array of integers
FloatArray : []float = array{}   # Empty array of floats
```

Without a type annotation, the compiler cannot determine what type of array you want, so you must either provide the type explicitly or include at least one element that establishes the type.

Arrays determine their element type from the common supertype of all elements. When you create an array with values of different but related types, Verse finds the most specific type that encompasses all elements:

<!--versetest
class1 := class {}
class2 := class(class1) {}
class3 := class(class1) {}
-->
<!-- 18 -->
```verse
# Array element type is class1 (common supertype)
MixedArray : []class1 = array{class2{}, class3{}}
```

This applies to any type hierarchy, including interfaces. If you mix completely unrelated types, the element type becomes `any`:

<!--versetest-->
<!-- 19 -->
```verse
# Array of comparable - different types sharing comparable in common
DisjointArray : []comparable = array{42, 13.37, true}

# Array of any - different types with no common supertype
AnyArray : []any = array{15.61, "Message", void}
```

### From Tuples to Arrays

Verse provides automatic conversion between tuples and arrays in specific contexts, enabling flexible function calls while maintaining type safety. This conversion is *one-way*: tuples can become arrays, but arrays cannot become tuples.

Tuples can be directly assigned to array variables when all tuple elements are compatible with the array's element type:

<!--versetest-->
<!-- 20 -->
```verse
# Homogeneous tuple to array
X:tuple(int, int) = (1, 2)
Y:[]int = X            # Valid - both elements are int
Y[1] = 2               # Can use as normal array

# Longer tuples work too
NumTuple:tuple(int, int, int, int) = (1, 2, 3, 4)
NumberArray:[]int = NumTuple
NumberArray.Length = 4
```

This conversion creates an array containing all the tuple's elements in order.

When a function has a single array parameter, you can call it with multiple arguments, which automatically form an array:

<!--versetest-->
<!-- 21 -->
```verse
ProcessNumbers(Numbers:[]int):int = Numbers.Length

# All these are equivalent:
ProcessNumbers(1, 2, 3)           # Multiple args → array
ProcessNumbers((1, 2, 3))         # Tuple literal → array
Values := (1, 2, 3)
ProcessNumbers(Values)             # Tuple variable → array
```

This "variadic-like" syntax provides convenience while keeping the function signature simple:

<!--versetest-->
<!-- 22 -->
```verse
Sum(Nums:[]int):int =
    var Total:int = 0
    for (N : Nums):
        set Total += N
    Total

Sum(1, 2, 3, 4)                   # Returns 10
Sum((5, 6))                       # Returns 11
Values := (10, 20, 30)
Sum(Values)                       # Returns 60
```

Array conversion only succeeds when **all tuple elements are compatible** with the array's element type:

<!--versetest
F(X:[]int):int = X.Length
entity := class:
    ID:int

player := class(entity):
    Name:string

ProcessEntities(E:[]entity):int = E.Length
GetP()<transacts>:player = player{ID := 1, Name := "Alice"}
GetE()<transacts>:entity = entity{ID := 2}
<#
-->
<!-- 23 -->
```verse
# Homogeneous tuple - all int
F(X:[]int):int = X.Length
F(1, 2, 3)                        # Valid

# Subtype compatibility
entity := class:
    ID:int

player := class(entity):
    Name:string

ProcessEntities(E:[]entity):int = E.Length

P := player{ID := 1, Name := "Alice"}
E := entity{ID := 2}
ProcessEntities(P, E)             # Valid - player is subtype of entity
```
<!-- #> -->

Functions taking `[]any` accept **any tuple**, regardless of element types:

<!--versetest-->
<!-- 24 -->
```verse
GetLength(Items:[]any):int = Items.Length

# All valid - any tuple works
GetLength(1, 2.0)                 # Mixed types OK
GetLength("a", 42, true)          # Different types OK
GetLength((1, 2.0, "hello"))      # Explicit tuple OK
```

This enables generic functions that work with heterogeneous data.

When tuple elements share a common supertype (via inheritance or interface), they convert to an array of that supertype:

<!--versetest
interface1 := interface:
    GetID():int

class1 := class(interface1):
    GetID<override>():int = 1

class2 := class(interface1):
    GetID<override>():int = 2

ProcessInterfaces(Items:[]interface1):int = Items.Length

assert:
    X:class1 = class1{}
    Y:class2 = class2{}
    ProcessInterfaces(X, Y) = 2
<#
-->
<!-- 25 -->
```verse
interface1 := interface:
    GetID():int

class1 := class(interface1):
    GetID<override>():int = 1

class2 := class(interface1):
    GetID<override>():int = 2

ProcessInterfaces(Items:[]interface1):int = Items.Length

X:class1 = class1{}
Y:class2 = class2{}

# Valid - both classes implement interface1
ProcessInterfaces(X, Y)           # Returns 2
```
<!-- #> -->

The compiler finds the most specific common supertype and uses it for the array element type.

Tuple-to-array conversion works with nested structures:

**Nested arrays:**

<!--versetest
ProcessMatrix(Matrix:[][]int):int = Matrix.Length
-->
<!-- 26 -->
```verse
# Nested tuples → nested arrays
MatrixData := ((1, 2), (3, 4))
ProcessMatrix(MatrixData)             # Valid

# Or with explicit nesting
ProcessMatrix((1, 2), (3, 4))   # Valid
```

**Optional arrays:**

<!--versetest-->
<!-- 27 -->
```verse
ProcessOptional(Items:?[]int)<decides>:int = Items?[0]

# Optional tuple → optional array
Values := option{(1, 2)}
ProcessOptional[Values]           # Valid
```

**Tuples containing arrays:**

<!--versetest-->
<!-- 28 -->
```verse
ProcessComplex(Data:tuple([]int, int)):int = Data(0).Length

# First element of tuple becomes array
ProcessComplex(((1, 2), 3))       # Valid - (1,2) becomes []int
```

### Array Slicing

Arrays support slicing operations through the `.Slice` method, which extracts a contiguous portion of an array. Slicing is a failable operation—it succeeds only when the indices are valid.

The two-parameter form `Array.Slice[Start, End]` returns elements from index `Start` up to but not including index `End`:

<!--versetest-->
<!-- 29 -->
```verse
Numbers : []int = array{10, 20, 30, 40, 50}
if (Slice := Numbers.Slice[1, 4]):
    Slice = array{20, 30, 40}
```

The one-parameter form `Array.Slice[Start]` returns all elements from `Start` to the end:

<!--versetest
Numbers : []int = array{10, 20, 30, 40, 50}
-->
<!-- 30 -->
```verse
if (Slice := Numbers.Slice[2]):
    Slice = array{30, 40, 50}
```

Slicing fails if indices are negative, out of bounds, or if `Start` is greater than `End`. Creating an empty slice is valid when `Start` equals `End`:

<!--versetest
NumArray:[]int = array{10, 20, 30, 40, 50}
-->
<!-- 31 -->
```verse
NumArray.Slice[2, 2]  # Succeeds with array{}
# NumArray.Slice[2, 1]  # Would fail - Start > End
# NumArray.Slice[-1, 2] # Would fail - negative index
# NumArray.Slice[0, 10] # Would fail - End beyond array length
```

Slicing also works on strings and character tuples, returning a string:

<!--versetest-->
<!-- 32 -->
```verse
"hello".Slice[1, 4] = "ell"
```

### Array Methods

Arrays provide intrinsic methods for searching, removing, and replacing elements. These operations create new arrays rather than modifying existing ones, maintaining Verse's immutability guarantees.

The `Find()` method searches for the first occurrence of an element and returns its index, or fails if not found:

<!--versetest
M():void =
    SomeArray:[]int = array{1, 2, 3}
    if (Example := SomeArray.Find[2]) {}
<#
-->
<!-- 33 -->
```verse
Array.Find(Element:t)<decides>:int
```
<!-- #> -->

<!--versetest-->
<!-- 34 -->
```verse
NumArray := array{1, 2, 3, 1, 2, 3}

if (Index := NumArray.Find[2]):
    # Index is 1 (first occurrence)
    Print("Found at index {Index}")

if (not NumArray.Find[0]):
    # Element not in array
    Print("Not found")

# With strings
Strings := array{"Apple", "Orange", "Strawberry"}

if (Index := Strings.Find["Strawberry"]):
    Print("Found at {Index}") # Prints "Found at 2"
```

`Find()` returns the first found index on success (`int`), or fails if the element was not found, enabling safe handling of missing elements without exceptions or special sentinel values.

`RemoveFirstElement()` removes the first occurrence:

<!--versetest
M():void =
    SomeArray:[]int = array{1, 2, 3}
    if (Updated := SomeArray.RemoveFirstElement[2]) {}
<#
-->
<!-- 35 -->
```verse
Array.RemoveFirstElement(Element:t)<decides>:[]t
```
<!-- #> -->

<!--versetest-->
<!-- 36 -->
```verse
NumArray := array{1, 2, 3, 1, 2, 3}

if (Updated := NumArray.RemoveFirstElement[2]):
    # Updated is array{1, 3, 1, 2, 3}
    Print("Removed first 2")

if (not NumArray.RemoveFirstElement[0]):
    # Element not found
    Print("Element not in array")
```

`RemoveAllElements()` removes all occurrences:

<!--versetest-->
<!-- 37 -->
```verse
NumArray := array{1, 2, 3, 1, 2, 3}
Updated := NumArray.RemoveAllElements(2)
Updated = array{1, 3, 1, 3}

# Returns unchanged array if element not found
Same := NumArray.RemoveAllElements(0)
Same = array{1, 2, 3, 1, 2, 3}
```

`Remove()` removes element at specific position:

<!--NoCompile-->
<!--00-->
```verse
Array.Remove(From:int, To:int)<decides>:[]t
```

<!--versetest-->
<!-- 38 -->
```verse
NumArray := array{10, 20, 30, 40}

if (Updated := NumArray.Remove[1,1]):
    # Updated is array{10, 30, 40}

# Negative index would fail
# if (not NumArray.Remove[-1,0]):

# Out of bounds would fail
# if (not NumArray.Remove[6,10]):
```

`ReplaceFirstElement()` replace first occurrence:

<!--NoCompile-->
<!-- 00 -->
```verse
Array.ReplaceFirstElement(OldValue:t, NewValue:t)<decides>:[]t
```

<!--versetest-->
<!-- 39 -->
```verse
NumArray := array{1, 2, 3, 1, 2, 3}

if (Updated := NumArray.ReplaceFirstElement[2, 99]):
    # Updated is array{1, 99, 3, 1, 2, 3}

if (not NumArray.ReplaceFirstElement[0, 99]):
    # Element not found - fail
```

`ReplaceAllElements()` replace all occurrences:

<!--NoCompile-->
<!-- 00 -->
```verse
Array.ReplaceAllElements(OldValue:t, NewValue:t):[]t
```

<!--versetest-->
<!-- 40 -->
```verse
NumArray := array{1, 2, 3, 1, 2, 3}
Updated := NumArray.ReplaceAllElements(2, 99)
# Updated is array{1, 99, 3, 1, 99, 3}

# Returns unchanged array if element not found
Same := NumArray.ReplaceAllElements(0, 99)
# Same is array{1, 2, 3, 1, 2, 3}
```

`ReplaceElement()` replaces at specific index:

<!--NoCompile-->
<!-- 00 -->
```verse
Array.ReplaceElement(Index:int, NewValue:t)<decides>:[]t
```

<!--versetest-->
<!-- 41 -->
```verse
NumArray := array{10, 20, 30, 40}

if (Updated := NumArray.ReplaceElement[1, 99]):
    # Updated is array{10, 99, 30, 40}

if (not NumArray.ReplaceElement[-1, 99]):
    # Negative index fails

if (not NumArray.ReplaceElement[10, 99]):
    # Out of bounds fails
```

`ReplaceAll()` is a pattern-based replacement:

<!--versetest-->
<!-- 42 -->
```verse
NumArray := array{1, 2, 3, 4, 2, 3, 5}
Pattern := array{2, 3}
Replacement := array{99}
Updated := NumArray.ReplaceAll(Pattern, Replacement)
Updated = array{1, 99, 4, 99, 5}

# Works with different length patterns
NumArray2 := array{1, 2, 2, 1, 2, 2, 1}
Updated2 := NumArray2.ReplaceAll(array{2, 2}, array{9, 9, 9})
Updated2 = array{1, 9, 9, 9, 1, 9, 9, 9, 1}

# Strings are []char
SomeMessage := "Hey, this is a string, Hello!"
NewMessage := SomeMessage.ReplaceAll("He", "Apples") # Note: Case sensitive!
NewMessage = "Applesy, this is a string, Applesllo!"
```

`ReplaceAll()` finds contiguous subsequences matching `Pattern` and replaces each with `Replacement`. The replacement can be any length, including empty.

`Insert()` inserts an element at a specific position:

<!--NoCompile-->
<!-- 00 -->
```verse
Array.Insert(Index:int, Element:[]t)<decides>:[]t
```

<!--versetest-->
<!-- 43 -->
```verse
NumArray := array{10, 20, 40}

if (Updated := NumArray.Insert[2, array{30}]):
    # Updated is array{10, 20, 30, 40}
    # Inserted at index 2, existing elements shift right

# Can insert at start
if (Updated2 := NumArray.Insert[0, array{5}]):
    # Updated2 is array{5, 10, 20, 40}

# Can insert at end (index = Length is valid)
if (Updated3 := NumArray.Insert[NumArray.Length, array{50}]):
    # Updated3 is array{10, 20, 40, 50}

# Out of bounds fails
if (not NumArray.Insert[-1, array{5}]):
    # Negative index fails

if (not NumArray.Insert[NumArray.Length + 1, array{5}]):
    # Beyond Length fails
```

The `Concatenate()` function is a variadic intrinsic that combines any number of arrays into one:

<!--versetest
M():void =
    Result := Concatenate(array{1}, array{2, 3})
<#
-->
<!-- 44 -->
```verse
Concatenate(Arrays:[]t...):[]t
```
<!-- #> -->

Unlike the `+` operator which joins two arrays, `Concatenate()` accepts zero or more arrays:

<!--versetest-->
<!-- 45 -->
```verse
# Empty call returns empty array
Empty := Concatenate()
Empty = array{}

# Single array returns that array
# Single := Concatenate(array{1, 2, 3})
# Single = array{1, 2, 3}

# Two arrays
TwoArrays := Concatenate(array{1, 2}, array{3, 4})
TwoArrays = array{1, 2, 3, 4}

# Multiple arrays
Many := Concatenate(array{1}, array{2, 3}, array{4}, array{5, 6})
Many = array{1, 2, 3, 4, 5, 6}
```

Empty arrays are handled seamlessly:

<!--versetest-->
<!-- 46 -->
```verse
# Empty arrays contribute nothing
Result1 := Concatenate(array{1, 2}, array{}, array{3})
Result1 = array{1, 2, 3}
Result2 := Concatenate(array{}, array{}, array{})
Result2 = array{}

# Can concatenate many empty arrays
# EmptyResult := Concatenate(for (I := 0..100): array{})
# EmptyResult = array{}
```

**Comparison with `+` operator:**

<!--versetest-->
<!-- 48 -->
```verse
# Using + operator (binary)
A1 := array{1, 2}
A2 := array{3, 4}
A3 := array{5, 6}
Result1 := A1 + A2 + A3  # Works but requires multiple operations

# Using Concatenate (variadic)
Result2 := Concatenate(A1, A2, A3)  # Single operation

Result1 = Result2
```

Arrays in Verse are thus immutable values with predictable behavior, but through `var` they offer the convenience of mutable variables. They can be concatenated, iterated, sliced, searched, and manipulated, making them one of the most flexible and fundamental data structures in the language.

## Maps

Maps are one of the core container types, alongside arrays and optionals. If arrays are ordered sequences indexed by integers, and optionals are the smallest container of all, holding either zero or one value, then Maps generalize both ideas: like arrays, they provide efficient lookup, but instead of being limited to integer indices, they allow any *comparable* type as a key. You can think of a map as an array indexed by arbitrary keys, or as a larger optional that can hold many key–value associations at once.

A map is an immutable associative container that stores zero or more key–value pairs of type `[k]v`, written as `(Key:k, Value:v)`. Maps are the standard way to associate values with other values: you supply a key, and the map returns the value associated with it.

Maps are useful whenever you want to store data that is naturally indexed by something other than an integer position. For example, you might want to store the weights of different objects keyed by their names:

<!--versetest-->
<!-- 50 -->
```verse
Empty := map{}

var Weights:[string]float = map{
    "ant" => 0.0001,
    "elephant" => 500.0,
    "galaxy" => 500000000000.0
}
```

Looking up a value in a map uses square brackets. The expression succeeds if the key is present and fails if it is not. Lookups are designed to be fast, with amortized *O(1)* time complexity:

<!--versetest
Weights:[string]float = map{"ant" => 0.0001}
-->
<!-- 51 -->
```verse
Weights["ant"]  # succeeds, since "ant" key exists in map
# Weights["car"] would fail
```

If you want to update a map stored in a variable, you use `set`. This works both for adding a new key–value pair and for changing the value of an existing key. If you try to modify a key that is not present, the operation fails:

<!--versetest-->
<!-- 52 -->
```verse
var Friendliness:[string]int = map{"peach" => 1000}

set Friendliness["pelican"] = 17     # succeed: add a new value with the given key
set Friendliness["peach"] += 2000    # succeed: update an existing value with the given key
# set Friendliness["tomato"] += 1000   # would fail: can't update a value which key does not exist
```

Every map also carries its size, accessible as the `Length` field:

<!--versetest
Friendliness:[string]int = map{"peach" => 1000, "pelican" => 17}
-->
<!-- 53 -->
```verse
Friendliness.Length = 2         # succeed: the map has 2 entries
```

When constructing a map with duplicate keys, only the last value is kept. This is because a map enforces uniqueness of keys, so earlier entries are silently overwritten:

<!--versetest-->
<!-- 54 -->
```verse
WordCount:[string]int = map{
    "apple" => 0,
    "apple" => 1,
    "apple" => 2
}
# WordCount contains only {"apple" => 2}
```

Maps can also be iterated over, letting you traverse all key–value pairs exactly in the order they were inserted:

<!--versetest-->
<!-- 55 -->
```verse
ExampleMap:[string]string = map{
    "a" => "apple",
    "b" => "bear",
    "c" => "candy"
}

for (Key -> Value : ExampleMap):
    Print("{Value} in ExampleMap at key {Key}")
```

This produces:

- "apple in ExampleMap at key a"
- "bear in ExampleMap at key b"
- "candy in ExampleMap at key c"

Sometimes you want to remove an entry from a map. Since maps are immutable, "removing" means creating a new map that excludes the given key. For example, here is a function that removes an element from a `[string]int` map:

<!--versetest-->
<!-- 56 -->
```verse
RemoveKeyFromMap(TheMap:[string]int, ToRemove:string):[string]int =
    var NewMap:[string]int = map{}
    for (Key -> Value : TheMap, Key <> ToRemove):
        set NewMap = ConcatenateMaps(NewMap, map{Key => Value})
    return NewMap
```

The key type of a map must belong to the class `comparable`, which guarantees that two keys can be checked for equality. All basic scalar types such as `int`, `float`, `rational`, `logic`, `char`, and `char32` are comparable, and so are compound types like arrays, maps, tuples, and `struct`s whose components are comparable. Classes and interfaces cannot be used as keys, since their instances do not provide a built-in notion of equality.

Not all types can be used as map keys. A type must be comparable—meaning values of that type can be checked for equality. Here's a comprehensive guide to what can and cannot be used as map keys:

**Types that can be used as map keys:**

- `logic` - boolean values
- `int`, `float`, `rational` - numeric types
- `char`, `char32` - character types
- `string` - text
- Enumerations - custom enum types
- Classes and Interfaces marked with `<unique>`
- `?t` where `t` is comparable - optionals of comparable types
- `[]t` where `t` is comparable - arrays of comparable elements
- `tuple(t0, t1, ...)` where all elements are comparable - tuples of comparable types
- `struct` types where all fields are comparable

**Types that cannot be used as map keys:**

- `false` - the empty type
- `type` - type values themselves
- Function types like `t -> u`
- `subtype(t)` - subtype expressions
- Regular classes (without `<unique>`)
- Interfaces (without `<unique>`)

Attempting to use a non-comparable type as a key results in a compile-time error.

Like arrays, maps infer their key and value types from the common supertype of all keys and values. When you create a map with mixed but related types, Verse finds the most specific types that encompass all keys and all values:

<!--versetest
class1 := class<unique> {}
class2 := class<unique>(class1) {}
class3 := class<unique>(class1) {}
-->
<!-- 57 -->
```verse
Instance2 := class2{}
Instance3 := class3{}

# Key type is class1 (common supertype of class2 and class3)
# Value type remains int
MixedKeyMap : [class1]int = map{Instance2 => 1, Instance3 => 2}
```

### Ordering and Equality

Maps preserve insertion order, which is significant for both iteration and equality checks. When you insert entries into a map, they maintain the order of insertion. Two maps are equal only if they contain the same key–value pairs **in the same order**:

<!--versetest-->
<!-- 58 -->
```verse
var Scores:[string]int = map{}
set Scores["Alice"] = 100
set Scores["Bob"] = 90
set Scores["Carol"] = 95

# This map equals Scores
Map1 := map{"Alice" => 100, "Bob" => 90, "Carol" => 95}
Scores = Map1

# This map does NOT equal Scores - different order
Map2 := map{"Bob" => 90, "Alice" => 100, "Carol" => 95}
not Scores = Map2
```

When a map literal contains duplicate keys, the last value overwrites earlier values, but the key's position remains from its **first** occurrence:

<!--versetest
-->
<!-- 59 -->
```verse
Map := map{0 => "zero", 1 => "one", 0 => "ZERO", 2 => "two"}
# Equivalent to map{0 => "ZERO", 1 => "one", 2 => "two"}
# The key 0 stays in its original position
```

Iteration over the map will visit entries in their preserved insertion order.

### Empty Map Types

Empty maps can infer their key and value types from context, similar to arrays:

<!--versetest
-->
<!-- 60 -->
```verse
StringToInt : [string]int = map{}  # Empty map with inferred types

var Scores : [string]int = map{}
set Scores = ConcatenateMaps(Scores, map{"Alice" => 100})
```

Without type context, you may need to provide explicit type annotations.

### Variance

Maps exhibit different variance behavior for keys and values. A map type `[K1]V1` is a subtype of `[K2]V2` when:

- **Keys are contravariant**: `K2` is a subtype of `K1` (more general keys → more specific keys)
- **Values are covariant**: `V1` is a subtype of `V2` (more specific values → more general values)

You can create maps with class hierarchy types as keys and values:

<!--versetest
class1 := class<unique> {}
class2 := class<unique>(class1) {}
-->
<!-- 61 -->
```verse
# Map with general keys, specific values: [class1]class2
GeneralKeyMap : [class1]class2 = map{class1{} => class2{}}
```

When modifying a mutable map through `set`, you can only insert keys and values that match the map's declared types:

<!--versetest
class1 := class<unique> {}
class2 := class<unique>(class1) {}
-->
<!-- 62 -->
```verse
var Map : [class2]int = map{}
Key2 : class2 = class2{}
Key1 : class1 = Key2

set Map[Key2] = 1      # Succeeds - exact type match
# set Map[Key1] = 2    # ERROR - cannot use supertype as key
```

### Nested Maps

Maps can contain other maps as values, enabling multi-level associations:

<!--versetest
-->
<!-- 63 -->
```verse
# Map from strings to maps of ints to strings
NestedMap : [string][int]string = map{
    "numbers" => map{1 => "one", 2 => "two"},
    "letters" => map{0 => "a", 1 => "b"}
}

if (InnerMap := NestedMap["numbers"]):
    if (Value := InnerMap[1]):
        Value = "one"
```

Maps can be used as keys of other maps if all values and keys from it are comparable.

### Concatenating Maps

The `ConcatenateMaps()` function merges multiple maps into a single map, similar to how `Concatenate()` combines arrays:

<!--versetest
M():void =
    Map1 := map{1 => "one"}
    Map2 := map{2 => "two"}
    Result := ConcatenateMaps(Map1, Map2)
<#
-->
<!-- 64 -->
```verse
ConcatenateMaps(Maps:[]map(k,v)...):map(k,v)
```
<!-- #> -->

`ConcatenateMaps()` is variadic—it accepts any number of maps and combines them into one. When maps contain duplicate keys, values from **later** maps override values from earlier ones:

<!--versetest-->
<!-- 65 -->
```verse
<#
Map1 := map{1 => "one", 2 => "two"}
Map2 := map{3 => "three", 4 => "four"}
Map3 := map{5 => "five"}

Combined := ConcatenateMaps(Map1, Map2, Map3)
# Combined is map{1 => "one", 2 => "two", 3 => "three", 4 => "four", 5 => "five"}
#>
# Test with two maps since three causes type inference issues
Map1 := map{1 => "one", 2 => "two"}
Map2 := map{3 => "three", 4 => "four"}

Combined := ConcatenateMaps(Map1, Map2)
Combined = map{1 => "one", 2 => "two", 3 => "three", 4 => "four"}
```

**Handling duplicate keys:**

<!--versetest-->
<!-- 66 -->
```verse
Base := map{1 => "original", 2 => "base"}
Override := map{2 => "updated", 3 => "new"}

Result := ConcatenateMaps(Base, Override)
Result = map{1 => "original", 2 => "updated", 3 => "new"}
# Key 2 was overridden by the later map
```

The right-to-left precedence ensures that later maps take priority, enabling a natural override pattern.

**Empty maps:**

<!--versetest-->
<!-- 67 -->
```verse
<#
# Empty maps contribute nothing
M1 := map{1 => "a"}
M2 := map{}
M3 := map{2 => "b"}

Result := ConcatenateMaps(M1, M2, M3)  # map{1 => "a", 2 => "b"}

# Concatenating only empty maps produces an empty map
Empty := ConcatenateMaps(map{}, map{}, map{})  # map{}

# Single map returns that map
Single := ConcatenateMaps(map{1 => "one"})  # map{1 => "one"}
#>
# Test with two maps (three causes type inference issues)
M1 := map{1 => "a"}
M2 : [int]string = map{}

Result := ConcatenateMaps(M1, M2)
Result = map{1 => "a"}
```

**Type constraints:**

The resulting map type will coerce to the most specific shared type from the input maps:

<!--versetest-->
<!-- 68 -->
```verse
<#
# All maps have same types
M1 := map{1 => "a"}
M2 := map{2 => "b"}
Combined := ConcatenateMaps(M1, M2)  # [int]string

# Maps with different types
M3 := map{1 => "a"}
M4 := map{"string" => "b"}
Combined2 := ConcatenateMaps(M3, M4)  # [comparable]string

# Mismatched key and value types
M5 := map{1 => "a"}        # [int]string
M6 := map{5 / 3 => "b"} # [rational]string
Combined3 := ConcatenateMaps(M5, M6) # [rational]string
#>
# Test that maps with same types can be concatenated
M1 := map{1 => "a"}
M2 := map{2 => "b"}
Combined := ConcatenateMaps(M1, M2)
Combined = map{1 => "a", 2 => "b"}
```

## Weak Maps

The `weak_map` type is a specialized supertype of `map` designed for persistent data storage with weak key references. It behaves similarly to ordinary maps for individual entry access, but deliberately restricts bulk operations. You cannot ask for its length, you cannot iterate over its entries, and you cannot use `ConcatenateMaps`. These restrictions enable efficient weak reference semantics and integration with Verse's persistence system.

A `weak_map` is declared with `weak_map(k,v)` and can be initialized from an ordinary `map{}`. Updating and accessing individual entries works the same way as regular maps:

<!--versetest
-->
<!-- 69 -->
```verse
var MyWeakMap:weak_map(int,int) = map{}

set MyWeakMap[0] = 1
Value := MyWeakMap[0]         # succeeds with 1

set MyWeakMap = map{0 => 2}   # reassignment still works (for local variables)
```

Because `weak_map` is a supertype of `map`, you can assign regular maps to weak_map variables when needed, but you lose the ability to count or iterate once you are working with a weak map.

### Restrictions

**No Length Property:**

<!--versetest
M():void =
    var MyWeakMap:weak_map(int,int) = map{1 => 2}
<#
-->
<!-- 70 -->
```verse
var MyWeakMap:weak_map(int,int) = map{1 => 2}
# ERROR: weak_map has no Length property
# Size := MyWeakMap.Length
```
<!-- #> -->

**No Iteration:**

<!--versetest
M():void =
    var MyWeakMap:weak_map(int,int) = map{1 => 2, 3 => 4}
<#
-->
<!-- 71 -->
```verse
var MyWeakMap:weak_map(int,int) = map{1 => 2, 3 => 4}
# ERROR: Cannot iterate over weak_map
# for (Entry : MyWeakMap) {}
```
<!-- #> -->

**Cannot Coerce to Comparable:**

<!--versetest
M():void =
    var MyWeakMap:weak_map(int,int) = map{}
<#
-->
<!-- 72 -->
```verse
var MyWeakMap:weak_map(int,int) = map{}
# ERROR: weak_map cannot be converted to comparable
# C:comparable = MyWeakMap
```
<!-- #> -->

**Cannot Join with Regular Maps:**

<!--versetest
M():void =
    var MyWeakMap:weak_map(int,int) = map{1 => 2}
<#
-->
<!-- 73 -->
```verse
var MyWeakMap:weak_map(int,int) = map{1 => 2}

# ERROR: Cannot join weak_map with regular map to produce regular map
# Result:[int]int = if (true?) then MyWeakMap else map{3 => 4}
```
<!-- #> -->

### Module-Scoped weak_map Variables

When using `weak_map` as a module-scoped variable (for persistent data), there are additional restrictions:

**Cannot Read Complete Map:**

<!--versetest
M():void =
    var LocalData:weak_map(int, int) = map{}
    if (set LocalData[1] = 100) {}
<#
-->
<!-- 74 -->
```verse
# Module-scoped persistent weak_map
var PlayerData:weak_map(player, int) = map{}

GetAllData():weak_map(player, int) =
    # ERROR: Cannot read complete module-scoped weak_map
    # PlayerData
    map{}  # Must construct new map instead
```
<!-- #> -->

**Cannot Write Complete Map:**

<!--versetest
M():void =
    var LocalData:weak_map(int, int) = map{}
    set LocalData = map{}
<#
-->
<!-- 75 -->
```verse
var PlayerData:weak_map(player, int) = map{}

ResetAllData():void =
    # ERROR: Cannot replace module-scoped weak_map
    # set PlayerData = map{}
    {}
```
<!-- #> -->

**Individual Entry Access Works:**

<!--versetest
M()<transacts>:void =
    var LocalData:weak_map(int, int) = map{}

    GetScore(Key:int):int =
        if (Score := LocalData[Key]):
            Score
        else:
            0

    SetScore(Key:int, Score:int)<transacts>:void =
        if (set LocalData[Key] = Score) {}
<#
-->
<!-- 76 -->
```verse
var PlayerData:weak_map(player, int) = map{}

# OK: Can read individual entries
GetPlayerScore(Player:player):int =
    if (Score := PlayerData[Player]):
        Score
    else:
        0

# OK: Can write individual entries
SetPlayerScore(Player:player, Score:int):void =
    set PlayerData[Player] = Score
```
<!-- #> -->

This restriction exists because module-scoped weak_maps integrate with the persistence system, which only tracks individual entry updates, not complete map replacements.

For module-scoped `var weak_map` variables, both key and value types have strict requirements:

**Key Type Must Have `<module_scoped_var_weak_map_key>` Specifier:**

<!--versetest
regular_class := class<unique> {}

M():void =
    var LocalData:weak_map(regular_class, int) = map{}
<#
-->
<!-- 77 -->
```verse
# Valid key type
persistent_class := class<unique><allocates><computes><persistent><module_scoped_var_weak_map_key> {}

var ValidData:weak_map(persistent_class, int) = map{}

# Invalid key type - missing specifier
regular_class := class<unique><allocates><computes> {}

# ERROR: Key type lacks <module_scoped_var_weak_map_key>
# var InvalidData:weak_map(regular_class, int) = map{}
```
<!-- #> -->

**Value Type Must Be Persistable:**

<!--versetest
regular_struct := struct:
    Value:int

M():void =
    var LocalData:weak_map(int, regular_struct) = map{}
<#
-->
<!-- 78 -->
```verse
persistent_class := class<unique><allocates><computes><persistent><module_scoped_var_weak_map_key> {}

# Valid: persistable value type
persistable_struct := struct<persistable>:
    Value:int

var ValidData:weak_map(persistent_class, persistable_struct) = map{}

# Invalid: non-persistable value type
regular_struct := struct:
    Value:int

# ERROR: Value type must be persistable
# var InvalidData:weak_map(persistent_class, regular_struct) = map{}
```
<!-- #> -->

Common key types that satisfy the requirements:

- **`player`** - The standard key type for player-specific data
- **`persistent_key`** - Custom persistent keys with validity tracking
- **`session_key`** - Transient keys that don't persist across sessions

### Covariance

The `weak_map` type is **covariant** in its key type, meaning you can use a weak_map with a subclass key type where a parent class key type is expected:

<!--versetest
base_class := class<unique> {}
derived_class := class(base_class) {}

value_struct := struct {}

CreateDerivedMap():weak_map(derived_class, value_struct) =
    map{}

F():void=
    BaseMap:weak_map(base_class, value_struct) = CreateDerivedMap()
<#
-->
<!-- 79 -->
```verse
base_class := class<unique> {}
derived_class := class(base_class) {}

value_struct := struct {}

CreateDerivedMap():weak_map(derived_class, value_struct) =
    map{}

# OK: weak_map is covariant in key type
BaseMap:weak_map(base_class, value_struct) = CreateDerivedMap()

# ERROR 3509: Cannot go the other way (contravariance)
# DerivedMap:weak_map(derived_class, value_struct) = BaseMap
```
<!-- #> -->

This covariance also allows regular maps to be assigned to weak_maps with compatible key types:

<!--versetest
base_class := class<unique> {}
derived_class := class(base_class) {}
value_struct := struct {}

F():void=
    DerivedKey := derived_class{}
    RegularMap:[derived_class]value_struct = map{DerivedKey => value_struct{}}

    WeakMap:weak_map(base_class, value_struct) = RegularMap
<#
-->
<!-- 80 -->
```verse
DerivedKey := derived_class{}
RegularMap:[derived_class]value_struct = map{DerivedKey => value_struct{}}

# OK: Regular map converts to weak_map with covariant key
WeakMap:weak_map(base_class, value_struct) = RegularMap
```
<!-- #> -->

### Partial Field Updates

When the value type is a struct or class, you can update individual fields of stored values:

<!--versetest
player_data := class:
    var Level:int = 0
    var Score:int = 0

GetPlayerData()<transacts>:player_data = player_data{}

M()<transacts>:void =
    var LocalData:weak_map(int, player_data) = map{}

    UpdateLevel(Key:int, NewLevel:int)<transacts>:void =
        Data := GetPlayerData()
        set Data.Level = NewLevel
        set Data.Score = 0
        if (set LocalData[Key] = Data) {}

        if (Stored := LocalData[Key]):
            set Stored.Level = NewLevel + 1
<#
-->
<!-- 81 -->
```verse
player_data := struct<persistable>:
    Level:int
    Score:int

var PlayerData:weak_map(player, player_data) = map{}

UpdatePlayerLevel(Player:player, NewLevel:int):void =
    # Set entire struct first
    set PlayerData[Player] = player_data{Level := NewLevel, Score := 0}

    # Then update just one field
    set PlayerData[Player].Level = NewLevel + 1
```
<!-- #> -->

### Transaction and Rollback Semantics

Like all mutable state in Verse, `weak_map` updates participate in transaction semantics. If a `<decides>` expression fails, all changes are rolled back:

<!--versetest
player := class<unique> {}

F():void=
    var GameData:weak_map(player, int) = map{}

    AttemptUpdate():void =
        if:
            set GameData[player{}] = 100
            set GameData[player{}] = 200
            false?


    AttemptUpdate()
<#
-->
<!-- 82 -->
```verse
var GameData:weak_map(int, int) = map{}

AttemptUpdate():void =
    if:
        set GameData[1] = 100
        set GameData[2] = 200
        false?  # Transaction fails

    # Both updates rolled back
    # GameData[1] still does not exist
    # GameData[2] still does not exist
```
<!-- #> -->

This applies to complete map replacements (for local variables), individual entries, and partial field updates.

### Island Limits

!!! warning "Important"
    Current island limits and rules may vary and not match exactly the values shown bellow

There is a **limit on the number of persistent `weak_map` variables** per island. In the standard environment, this limit is 4 persistent weak_maps. Exceeding this limit produces an error:

<!--versetest
key_class := class<unique><allocates><computes><persistent><module_scoped_var_weak_map_key> {}
value_class := class<final><persistable> {}

var Map1:weak_map(key_class, int) = map{}
var Map2:weak_map(key_class, int) = map{}
var Map3:weak_map(key_class, value_class) = map{}
<#
-->
<!-- 83 -->
```verse
key_class := class<unique><allocates><computes><persistent><module_scoped_var_weak_map_key> {}

var Map1:weak_map(key_class, int) = map{}  # OK
var Map2:weak_map(key_class, int) = map{}  # OK
var Map3:weak_map(key_class, int) = map{}  # OK
var Map4:weak_map(key_class, int) = map{}  # OK

# ERROR 3502: Exceeds island limit
# var Map5:weak_map(key_class, int) = map{}
```
<!-- #> -->

**Exception:** If the value type is a class (not a primitive or struct), the weak_map doesn't count toward this limit:

<!--versetest
key_class := class<unique><allocates><computes><persistent><module_scoped_var_weak_map_key> {}
value_class := class<final><persistable> {}

var Map1:weak_map(key_class, int) = map{}
var Map2:weak_map(key_class, int) = map{}
var Map3:weak_map(key_class, int) = map{}
var Map4:weak_map(key_class, value_class) = map{}
<#
-->
<!-- 84 -->
```verse
value_class := class<final><persistable> {}

var Map1:weak_map(key_class, int) = map{}       # Counts (1/4)
var Map2:weak_map(key_class, int) = map{}       # Counts (2/4)
var Map3:weak_map(key_class, int) = map{}       # Counts (3/4)
var Map4:weak_map(key_class, value_class) = map{}  # Doesn't count (class value)
```
<!-- #> -->
