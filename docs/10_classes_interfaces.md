# Classes and Interfaces

Classes and interfaces are Verse's object-oriented building blocks
that enable rich type hierarchies with inheritance, polymorphism, and
interface-based contracts. Classes provide object-oriented programming
with fields, methods, and single inheritance, enabling you to model
complex hierarchies of game entities with shared behavior and
specialized implementations. Interfaces define contracts that classes
must fulfill, promoting loose coupling and enabling multiple
inheritance of behavior specifications.

Together, classes and interfaces form a powerful system for modeling
game entities, components, and systems with both is-a relationships
(through class inheritance) and can-do contracts (through interface
implementation).

Let's explore classes first, then delve into interfaces and how they
complement each other.

## Classes

Classes form the backbone of object-oriented programming in Verse. A
class serves as a blueprint for creating objects that share common
properties and behaviors. When you define a class, you're creating a
new type that bundles data (fields) with operations on that data
(methods), encapsulating related functionality into a cohesive unit.

Class definitions occur at module scope. You cannot define a class
inside another class, struct, interface, or function. Classes are
top-level type definitions that establish the type system's structure:

<!-- 01 -->
```verse
# Valid: class at module scope
my_module := module:
    entity := class:
        ID:int

# Invalid: class inside another class
# outer := class:
#     inner := class:  # ERROR: classes must be at module scope
#         Value:int
```

The simplest form of a class groups related data together. Consider
modeling a character in your game:

<!-- 02 -->
```verse
character := class:
    Name : string
    var Health : int = 100
    var Level : int = 1
    MaxHealth : int = 100
```

This class definition establishes several important concepts. Fields
without the `var` modifier are immutable after construction—once you
create a character with a specific name, that name cannot
change. Fields marked with `var` are mutable and can be modified after
the object is created (see [Mutability](05_mutability.md) for details
on `var` and `set`). Default values provide sensible starting points,
making object construction more convenient while ensuring objects
start in valid states.

### Object Construction

Creating instances of a class involves specifying values for its
fields through an archetype expression:

<!--versetest
character := class:
    Name : string
    var Health : int = 100
    var Level : int = 1
    MaxHealth : int = 100
	
Ignore:int=1
-->
<!-- 03 -->
```verse
Hero := character{Name := "Aldric", Health := 100, Level := 5}
Villager := character{Name := "Martha"}  # default values for unspecified fields
```

The archetype syntax uses named parameters, making the construction
explicit and self-documenting. Any field with a default value can be
omitted from the archetype, and the default will be used. Fields
without defaults must be specified, ensuring objects are always fully
initialized. Fields can be passed to an archetype in any order.

### Methods

Classes become truly powerful when you add methods that operate on the
class's data:

<!-- 04 -->
```verse
character := class:
    Name : string
    var Health : int = 100
    var Level : int = 1
    var MaxHealth : int = 100

    TakeDamage(Amount : int) : void =
        set Health = Max(0, Health - Amount)

    Heal(Amount : int) : void =
        set Health = Min(MaxHealth, Health + Amount)

    IsAlive()<decides>:void= Health > 0

    LevelUp() : void =
        set Level += 1
        set MaxHealth = 100 + (Level * 10)
        set Health = MaxHealth  # Full heal on level up
```

Methods have access to all fields of the class and can modify mutable
fields. They encapsulate the logic for how objects of the class should
behave, ensuring that state changes happen in controlled, predictable
ways.

All methods in non-abstract classes must have implementations. Unlike
interfaces (which can declare abstract methods), a concrete class
method declaration without an implementation is an error:

<!-- 05 -->
```verse
# Valid: method with implementation
valid_class := class:
    Compute():int = 42

# Invalid: method without implementation in concrete class
# invalid_class := class:
#     Compute():int  # ERROR: needs implementation
```

### Blocks for Initialization

Classes can include `block` clauses in their body, which execute when
an instance is created. These blocks run initialization code that goes
beyond simple field assignment, allowing you to perform setup logic,
validation, or side effects during construction:

<!--versetest
GetCurrentTime()<computes>:float=0.0

logged_entity := class:
    ID:int
    var CreationTime:float = 0.0

    block:
        # This executes when an instance is created
        Print("Creating entity with ID: {ID}")
        set CreationTime = GetCurrentTime()

M()<transacts>:void =
    Entity := logged_entity{ID := 42}
    # Prints: "Creating entity with ID: 42"
<#
-->
<!-- 06 -->
```verse
logged_entity := class:
    ID:int
    var CreationTime:float = 0.0

    block:
        # This executes when an instance is created
        Print("Creating entity with ID: {ID}")
        set CreationTime = GetCurrentTime()

# Entity := logged_entity{ID := 42}
# Prints: "Creating entity with ID: 42"
```
<!-- #> -->
```

Block clauses have access to all fields of the class, including
`Self`, and can modify mutable fields. They execute in the order they
appear in the class definition:

<!-- 07 -->
```verse
multi_step_init := class:
    var Step1:int = 0
    var Step2:int = 0

    block:
        set Step1 = 10

    var Step3:int = 0

    block:
        set Step2 = Step1 + 5  # Can access earlier fields
        set Step3 = Step2 * 2

# Instance := multi_step_init{}
# Instance.Step1 = 10, Step2 = 15, Step3 = 30
```

**Execution order with inheritance:** When a class inherits from
another class, the Verse VM executes blocks in
subclass-before-superclass order, while the BP VM uses
superclass-before-subclass order. For portable code, avoid depending
on the execution order of blocks across inheritance hierarchies.

**Constraints on block clauses:**

- Blocks cannot contain failure (`<decides>`) operations
- Blocks cannot call suspending (`<suspends>`) functions
- Blocks can use `defer` statements, which execute when the block exits
- Block clauses are only allowed in classes, not in interfaces,
  structs, or modules

Block clauses are particularly useful for:

- Logging object creation
- Computing derived values during initialization
- Registering objects with global systems
- Performing validation that goes beyond simple field checks

### Self

Within class methods, `Self` is a special keyword that refers to the
current instance of the class. Each method invocation has its own
`Self` that refers to the specific object the method was called on.

You can use `Self` in multiple ways within method bodies:

- access fields of the instance
- calling methods of the instance
- pass the instance to other functions
- return the instance

<!--NoCompile-->
<!-- 08 -->
```verse
character := class:
    var Name : string
    var Config:[string]string = map{}
	
    Announce() : void =
        # Using Self to pass the whole object
        LogCharacterAction(Self, "announced")


    SetOption(Key:string, Value:string):builder =
        set Config[Key] = Value
        Self  # Return this instance for method chaining


    SetName(NewName:stirng):void =
       set Self.Name = NewName	  # Set the name of this instance
	   Self.Announce()            # Call a method of this instance
```

You can capture `Self` when creating nested objects:

<!-- 12 -->
```verse
container := class:
    ID:int

    CreateChild():child_with_parent =
        child_with_parent{Parent := Self}  # Capture this instance

child_with_parent := class:
    Parent:container

# C := container{ID := 42}
# Child := C.CreateChild()
# Child.Parent.ID = 42  # Child stores reference to C
```

### Inheritance

Classes support single inheritance, allowing you to create specialized
versions of existing classes. This creates an "is-a" relationship
where the subclass is a more specific type of the superclass:

<!--versetest
vector3:=struct{}

entity := class:
    var Position : vector3 = vector3{}
    var IsActive : logic = true

    Activate() : void = set IsActive = true
    Deactivate() : void = set IsActive = false

character := class(entity):  # character inherits from entity
    Name : string
    var Health : int = 100

    TakeDamage(Amount : int) : void =
        set Health = Max(0, Health - Amount)
        if (Health = 0):
            Deactivate()  # Can call inherited methods

player := class(character):  # player inherits from character
    var Score : int = 0
    var Lives : int = 3

    AddScore(Points : int) : void =
        set Score += Points
<#
-->
<!-- 13 -->
```verse
entity := class:
    var Position : vector3 = vector3{}
    var IsActive : logic = true

    Activate() : void = set IsActive = true
    Deactivate() : void = set IsActive = false

character := class(entity):  # character inherits from entity
    Name : string
    var Health : int = 100

    TakeDamage(Amount : int) : void =
        set Health = Max(0, Health - Amount)
        if (Health = 0):
            Deactivate()  # Can call inherited methods

player := class(character):  # player inherits from character
    var Score : int = 0
    var Lives : int = 3

    AddScore(Points : int) : void =
        set Score += Points
```
<!-- #> -->
```

Inheritance creates a type hierarchy where a `player` is also a
`character`, and a `character` is also an `entity`. This means you can
use a `player` object anywhere a `character` or `entity` is expected,
enabling polymorphic behavior.

**Important constraints on inheritance:**

1. **Single class inheritance only:** A class can inherit from at most
   one other class, though it can implement multiple
   interfaces. Multiple class inheritance is not supported:

<!-- 14 -->
```verse
base1 := class:
    Value1:int

base2 := class:
    Value2:int

# Valid: inherit from one class and multiple interfaces
interface1 := interface:
    Method1():void

interface2 := interface:
    Method2():void

derived := class<abstract>(base1, interface1, interface2):
    # Valid: one class, multiple interfaces
    Method1<override>():void = {}
    Method2<override>():void = {}

# Invalid: cannot inherit from multiple classes
# invalid := class(base1, base2):  # ERROR
```

2. **No shadowing of data members:** Subclasses cannot declare fields
   with the same name as fields in their superclass. This prevents
   ambiguity and ensures clear data ownership:

<!-- 15 -->
```verse
base := class:
    Value:int

# Invalid: cannot shadow parent's field
# derived := class(base):
#     Value:int  # ERROR: shadowing base.Value
```

3. **No method signature changes:** When overriding a method, you must
   use the exact same signature. Changing parameter types or return
   types creates a shadowing error:

<!-- 16 -->
```verse
base := class:
    Compute():int = 42

# Invalid: different return type
# derived := class(base):
#     Compute():float = 3.14  # ERROR: signature doesn't match
```

To override a method, use the `<override>` specifier with the matching signature.

### Super

Within a subclass, you can use the `super` keyword to refer to the
superclass type. This is primarily used to access the superclass's
implementation or to construct a superclass instance:

<!-- 17 -->
```verse
entity := class:
    ID:int
    Name:string

    Display():void =
        Print("Entity {ID}: {Name}")

character := class(entity):
    Health:int

    Display<override>():void =
        # Create a superclass instance to call its method
        super{ID := ID, Name := Name}.Display()
        Print("Health: {Health}")
```

The `super` keyword represents the superclass type itself. When you
write `super{...}`, you're creating an instance of the superclass with
the specified field values. This allows you to delegate to superclass
behavior while adding subclass-specific functionality.

Within an overriding method, you can call the parent class's
implementation using the `(super:)` syntax. This is the primary way to
invoke parent method implementations while adding or modifying
behavior:

<!-- 18 -->
```verse
base := class:
    Method():void =
        Print("Base implementation")

derived := class(base):
    Method<override>():void =
        # Call parent implementation first
        (super:)Method()
        Print("Derived implementation")

# Creates instance and calls Method()
# derived{}.Method()
# Output:
# Base implementation
# Derived implementation

```

The `(super:)` syntax explicitly calls the parent class's version of
the current method. This is cleaner and more efficient than
constructing a parent instance with `super{...}` when you only need to
call parent methods.

**Basic Usage:**

<!--versetest
ToString(:vector3)<computes>:string=""
vector3:=class<final>{ X:float=0.0; Y:float=0.0; Z:float=0.0 }

entity := class:
    Position:vector3

    Move(Delta:vector3):void =
        Print("Entity moving by {Delta}")
        # Update position logic here

character := class(entity):
    var Stamina:float = 100.0

    Move<override>(Delta:vector3):void =
        # Call parent movement logic
        (super:)Move(Delta)
        # Add character-specific behavior
        set Stamina -= 1.0
<#
-->
<!-- 19 -->
```verse
entity := class:
    Position:vector3

    Move(Delta:vector3):void =
        Print("Entity moving by {Delta}")
        # Update position logic here

character := class(entity):
    var Stamina:float = 100.0

    Move<override>(Delta:vector3):void =
        # Call parent movement logic
        (super:)Move(Delta)
        # Add character-specific behavior
        set Stamina -= 1.0
```
<!-- #> -->
```

**With Effect Specifiers:**

The `(super:)` syntax works seamlessly with all effect specifiers:

<!--versetest
async_base := class:
    Process()<suspends>:void =
        Sleep(1.0)
        Print("Base processing")

async_derived := class(async_base):
    Process<override>()<suspends>:void =
        # Parent method suspends, so this suspends too
        (super:)Process()
        Print("Derived processing")

transactional_base := class:
    var Value:int = 0

    Update()<transacts>:void =
        set Value += 1

transactional_derived := class(transactional_base):
    var Counter:int = 0

    Update<override>()<transacts>:void =
        (super:)Update()
        set Counter += 1
<#
-->
<!-- 20 -->
```verse
async_base := class:
    Process()<suspends>:void =
        Sleep(1.0)
        Print("Base processing")

async_derived := class(async_base):
    Process<override>()<suspends>:void =
        # Parent method suspends, so this suspends too
        (super:)Process()
        Print("Derived processing")

transactional_base := class:
    var Value:int = 0

    Update()<transacts>:void =
        set Value += 1

transactional_derived := class(transactional_base):
    var Counter:int = 0

    Update<override>()<transacts>:void =
        (super:)Update()
        set Counter += 1
```
<!-- #> -->
```

**Virtual Dispatch Through Parent Methods:**

When parent methods call other methods, virtual dispatch still applies
based on the actual object type. This means `Self` binds to the
derived instance even when calling through `(super:)`:

<!-- 21 -->
```verse
base := class:
    # Virtual method that can be overridden
    GetValue()<computes>:int = 10

    # Parent method that uses GetValue
    ComputeDouble()<computes>:int =
        2 * GetValue()  # Calls derived GetValue if overridden

derived := class(base):
    # Override GetValue to return different value
    GetValue<override>()<computes>:int = 20

    # Override ComputeDouble to call parent, but GetValue dispatch is virtual
    ComputeDouble<override>()<computes>:int =
        # Calls base.ComputeDouble, which calls derived.GetValue!
        (super:)ComputeDouble()

# derived{}.ComputeDouble()  # Returns 40, not 20
```

In this example, even though `ComputeDouble` calls the parent
implementation, the `GetValue()` call inside the parent uses virtual
dispatch and calls the derived version.

**With Overloaded Methods:**

The `(super:)` syntax works with overloaded methods, calling the
parent's version of the same overload:

<!-- 22 -->
```verse
base := class:
    Process(X:int):void =
        Print("Base int: {X}")

    Process(S:string):void =
        Print("Base string: {S}")

derived := class(base):
    Process<override>(X:int):void =
        (super:)Process(X)  # Calls parent's int overload
        Print("Derived int: {X}")

    Process<override>(S:string):void =
        (super:)Process(S)  # Calls parent's string overload
        Print("Derived string: {S}")
```

**Return Type Covariance:**

When overriding methods with `(super:)`, the return type can be a subtype of the parent's return type (covariant return types):

<!-- 23 -->
```verse
base_type := class:
    Name:string

derived_type := class(base_type):
    Value:int

base := class:
    Create():base_type =
        base_type{Name := "base"}

derived := class(base):
    # Override with more specific return type
    Create<override>():derived_type =
        # Can still call parent even with different return type
        Parent := (super:)Create()
        derived_type{Name := Parent.Name, Value := 42}
```

### Method Overriding

Subclasses can override methods defined in their superclasses to provide specialized behavior:

<!--verse
character:=class:
    IsAlive()<decides><transacts>:void={}
MoveToward(:?character)<transacts>:void={}
Patrol()<transacts>:void={}
ScanForTargets()<transacts>:void={}
-->
<!-- 24 -->
```verse
entity := class:
    OnUpdate<public>() : void = {}  # Default no-op implementation

enemy := class(entity):
    var Target : ?character = false

    OnUpdate<override>()<transacts> : void =
        if (Target?.IsAlive[]):
            MoveToward(Target)
        else:
            Patrol()

turret := class(entity):
    var Rotation:int= 0

    OnUpdate<override>()<transacts>: void =
        if (V:= Mod[Rotation, 360]):
            set Rotation = V
        ScanForTargets()
```

The override mechanism ensures that the correct method implementation
is called based on the actual type of the object, not the type of the
variable holding it. This is the foundation of polymorphic behavior in
object-oriented programming.

### Constructor Functions

Classes don't have traditional constructor methods like you might find
in other object-oriented languages. Instead, Verse provides two
approaches to object construction: direct field initialization through
archetype expressions, and constructor functions for complex
initialization scenarios.

For simple cases where you just need to set field values, use
archetype expressions directly:

<!-- 25 -->
```verse
player := class:
    Name:string
    var Health:int = 100
    Level:int = 1

# Direct construction with archetype
# Hero := player{Name := "Aldric", Health := 150, Level := 5}
```

When you need validation, computation, or complex initialization
logic, use constructor functions annotated with `<constructor>`:

<!--verse
player := class:
    Name:string
    var Health:int = 100
    Level:int = 1

MaxLevel:int = 99
-->
<!-- 26 -->
```verse
MakePlayer<constructor>(InName:string, InLevel:int)<transacts> := player:
    Name := InName
    Level := InLevel
    Health := InLevel * 100
```

Here's an example of calling this constructor:

<!--versetest
player := class:
    Name:string
    var Health:int = 100
    Level:int = 1
MaxLevel:int = 99
MakePlayer<constructor>(InName:string, InLevel:int)<transacts> := player:
    Name := InName
    Level := InLevel
    Health := InLevel * 100
-->
<!-- 261 -->
```verse
Hero := MakePlayer("Aldric", 5) # Call constructor function 
```

Constructor functions are regular functions that return class
instances, but the `<constructor>` annotation enables special
capabilities like delegating to other constructors. When calling a
constructor function from normal code, use just the function name—the
`<constructor>` annotation only appears in the definition.

Constructor functions can have effects that control their
behavior. Common effects include `<computes>`, `<allocates>`, and
`<transacts>`. A particularly useful effect is `<decides>`, which
allows constructors to fail if preconditions aren't met:

<!--verse
player := class:
    Name:string
    var Health:int = 100
    Level:int = 1

MaxLevel:int = 99
-->
<!-- 27 -->
```verse
MakeValidPlayer<constructor>(InName:string, InLevel:int)<transacts><decides> := 
    player:
         Name := InName
         Level := block:
                 InLevel > 0
                 InLevel <= MaxLevel
                 InLevel
         Health := InLevel * 100
```

Here's an example using the validated constructor with failure handling:

<!--versetest
player := class:
    Name:string
    var Health:int = 100
    Level:int = 1
MaxLevel:int = 99
MakeValidPlayer<constructor>(InName:string, InLevel:int)<transacts><decides> := 
    player:
         Name := InName
         Level := block:
                 InLevel > 0
                 InLevel <= MaxLevel
                 InLevel
         Health := InLevel * 100
AddPlayer(:player):void={}
-->
<!-- 271 -->
```verse
# Constructor can fail - use with failure syntax
if (Player := MakeValidPlayer["Hero", 5]):
    # Construction succeeded
    AddPlayer(Player)
else:
    # Construction failed - level out of range
```

Constructor functions cannot use the `<suspends>` effect. Construction
must complete synchronously to maintain object consistency.

### Overloading Constructors

You can provide multiple constructor functions with different
parameter signatures, allowing flexible object creation:

<!--verse
vector3:=class<final>{ X:float=0.0; Y:float=0.0; Z:float=0.0 }
-->
<!-- 28 -->
```verse
entity := class:
    Name:string
    var Health:int = 100
    Position:vector3

# Constructor with all parameters
MakeEntity<constructor>(Name:string, Health:int, Position:vector3) := entity:
    Name := Name
    Health := Health
    Position := Position

# Constructor with defaults
MakeEntity<constructor>(Name:string, Position:vector3) := entity:
    Name := Name
    Health := 100
    Position := Position

# Constructor for origin placement
MakeEntity<constructor>(Name:string) := entity:
    Name := Name
    Health := 100
    Position := vector3{X := 0.0, Y := 0.0, Z := 0.0}

# Each overload can be called based on arguments
# Enemy1 := MakeEntity("Goblin", 50, SpawnPoint)
# Enemy2 := MakeEntity("Guard", PatrolPoint)
# NPC := MakeEntity("Shopkeeper")
```

### Delegating Constructors

Constructor functions can delegate to other constructors, enabling
code reuse and constructor chaining. This is particularly important
for inheritance hierarchies where subclass constructors need to
initialize superclass fields.

When delegating to a parent class constructor from a subclass, you
must initialize the subclass fields first, then call the parent
constructor using the qualified `<constructor>` syntax within the
archetype:

<!-- 29 -->
```verse
entity := class:
    Name:string
    var Health:int

MakeEntity<constructor>(Name:string, Health:int) := entity:
    Name := Name
    Health := Health

character := class(entity):
    Class:string
    Level:int

# Subclass constructor delegates to parent constructor
MakeCharacter<constructor>(Name:string, Class:string, Level:int) := character:
    # Initialize subclass fields first
    Class := Class
    Level := Level
    # Then delegate to parent constructor
    MakeEntity<constructor>(Name, Level * 100)

# Hero := MakeCharacter("Aldric", "Warrior", 5)
```

Constructor functions can also forward to other constructors of the same class:

<!-- 30 -->
```verse
player := class:
    Name:string
    var Score:int

# Primary constructor
MakePlayer<constructor>(Name:string, Score:int) := player:
    Name := Name
    Score := Score

# Convenience constructor forwards to primary
MakeNewPlayer<constructor>(Name:string) := player:
    # Delegate to another constructor of the same class
    MakePlayer<constructor>(Name, 0)
```

Here's an example of calling the constructor:

<!--versetest
player := class:
    Name:string
    var Score:int

# Primary constructor
MakePlayer<constructor>(Name:string, Score:int) := player:
    Name := Name
    Score := Score

# Convenience constructor forwards to primary
MakeNewPlayer<constructor>(Name:string) := player:
    # Delegate to another constructor of the same class
    MakePlayer<constructor>(Name, 0)
-->
<!-- 301 -->
```verse
NewPlayer := MakeNewPlayer("Alice")
```

When delegating to a constructor of the same class, the delegation
replaces all field initialization—any fields you initialize before the
delegation are ignored. When delegating to a parent class constructor,
your subclass field initializations are preserved, and the parent
constructor initializes the parent fields.

### Order of Execution

Understanding execution order is crucial for correct initialization:

1. **Archetype expression:** Field initializers execute in the order
   they're written in the archetype
2. **Delegating constructor:** Subclass fields are initialized first,
   then the parent constructor runs
3. **Class body blocks:** When using direct archetype construction,
   blocks in the class definition execute before field initialization

For delegating constructors to parent classes:

<!-- 31 -->
```verse
base := class:
    BaseValue:int

MakeBase<constructor>(Value:int) := base:
    block:
        Print("Base constructor")
    BaseValue := Value

derived := class(base):
    DerivedValue:int

MakeDerived<constructor>(Base:int, Derived:int) := derived:
    # This executes first
    DerivedValue := Derived
    # Then parent constructor executes
    MakeBase<constructor>(Base)
```

Here's an example showing execution order:

<!--versetest
base := class:
    BaseValue:int

MakeBase<constructor>(Value:int) := base:
    block:
        Print("Base constructor")
    BaseValue := Value

derived := class(base):
    DerivedValue:int

MakeDerived<constructor>(Base:int, Derived:int) := derived:
    # This executes first
    DerivedValue := Derived
    # Then parent constructor executes
    MakeBase<constructor>(Base)
-->
<!-- 311 -->
```verse
# Prints: "Base constructor"
# Results in: derived{BaseValue := 10, DerivedValue := 20}
Instance := MakeDerived(10, 20)
```

For classes with mutable fields, initialization sets starting values
that can change during the object's lifetime. Immutable fields must be
initialized during construction and cannot be modified afterward. This
distinction makes the construction phase critical for establishing
invariants that will hold throughout the object's existence.

## Shadowing and Qualification

Verse has strict rules about name shadowing to prevent ambiguity and
maintain code clarity. Understanding these rules and the qualification
syntax is essential for working with inheritance hierarchies, multiple
interfaces, and nested modules.

In most contexts, you **cannot redefine names** that already exist in
an enclosing scope. This applies to functions, variables, classes,
interfaces, and modules:

<!-- 32 -->
```verse
# ERROR 3532: Function at module level shadows class method
# F(X:int):int = X + 1
# c := class:
#     F(X:int):int = X + 2  # ERROR - shadows outer F
```

This prohibition extends across various contexts:

<!--NoCompile-->
<!-- 33 -->
```verse
# ERROR: Cannot shadow classes
something := class {}

m := module:
    something := class {}  # ERROR

# ERROR: Cannot shadow variables
Value:int = 1

m := module:
     Value:int = 2        # ERROR

# ERROR: Cannot shadow data members
c := class { A:int }

A():void = {}             # ERROR - order doesn't matter

# ERROR: Module and function cannot share name

id():void = {}
id := module {}           # ERROR
```

The shadowing prohibition exists **regardless of definition order** -
it doesn't matter whether the outer name is defined before or after
the inner scope.

To define methods with the same name in different contexts, use
**qualified names** with the syntax `(ClassName:)MethodName`:

<!--versetest
# Class with qualified method of same name
c := class:
    (c:)F(X:int):int = X + 2
-->
<!-- 34 -->
```verse
# Class with qualified method of same name
# c := class:
#    (c:)F(X:int):int = X + 2

# Module-level function
F(X:int):int = X + 1

# Call the module-level function
F(10)  # Returns 11

# Call the class method
c{}.F(10)  # Returns 12

# Explicit qualification (optional here)
c{}.(c:)F(10)  # Returns 12
```

The `(c:)` qualifier indicates this `F` is defined specifically in
the `c` class context, distinguishing it from the module-level
`F`. This allows the same name to coexist without shadowing errors.

### Methods with Same Name

Using qualifiers, you can define *new methods* with the same name as
inherited methods, creating multiple distinct methods in the same
class:

<!-- 35 -->
```verse
c := class<abstract> { F(X:int):int }

d := class(c):
    F<override>(X:int):int = X + 1

e := class(d):
    (e:)F(X:int):int = X + 2 # NEW method with same name, not an override

# e now contains BOTH methods:
#    - (d:)F inherited from d
#    - (e:)F newly defined in e
```

Using the above:

<!--versetest
c := class<abstract> { F(X:int):int }
d := class(c):
    F<override>(X:int):int = X + 1
e := class(d):
    (e:)F(X:int):int = X + 2 # NEW method with same name, not an override
-->
<!-- 351 -->
```verse
E := e{}
E.(c:)F(10)  # Returns 11 (inherited from d's override)
E.(e:)F(10)  # Returns 12 (new method in e)
```

Key distinction:

- `F<override>` without qualifier: Overrides the inherited `F`
- `(e:)F` without `<override>`: Defines a **new** `F` specific to `e`

This allows a class to have multiple methods with the same name,
differentiated by their qualifiers, each serving different purposes in
the class hierarchy.

### `(super:)` Qualified

The `(super:)` qualifier works with qualified method names to call the
parent class's implementation:

<!-- 36 -->
```verse
i := interface { F(X:int):int }

ci := class(i):
    (i:)F<override>(X:int):int = X + 1
    (ci:)F(X:int):int = X + 2

dci := class(ci):
    # Override both inherited methods, calling super implementations
    (i:)F<override>(X:int):int = 100 + (super:)F(X)
    (ci:)F<override>(X:int):int = 200 + (super:)F(X)

```

And a use case:

<!--versetest
i := interface { F(X:int):int }

ci := class(i):
    (i:)F<override>(X:int):int = X + 1
    (ci:)F(X:int):int = X + 2

dci := class(ci):
    # Override both inherited methods, calling super implementations
    (i:)F<override>(X:int):int = 100 + (super:)F(X)
    (ci:)F<override>(X:int):int = 200 + (super:)F(X)
-->
<!-- 361 -->
```verse
DCI := dci{}
DCI.(i:)F(10)  # Returns 111 (100 + ci's 11)
DCI.(ci:)F(10)  # Returns 212 (200 + ci's 12)
```

`(super:)F(X)` within the qualified method calls the parent class's
implementation of that same qualified method. This enables you to
extend behavior for multiple method variants independently.

### Interface Collisions

When implementing multiple interfaces with methods of the same name,
qualifiers disambiguate which interface's method you're implementing:


<!-- 37 -->
```verse
i := interface:
    B(X:int):int

j := interface:
    B(X:int):int

collision := class(i, j):
    # Implement both B methods separately
    (i:)B<override>(X:int):int = 20 + X
    (j:)B<override>(X:int):int = 30 + X
```

And a use case:

<!--versetest
i := interface:
    B(X:int):int
j := interface:
    B(X:int):int
collision := class(i, j):
    (i:)B<override>(X:int):int = 20 + X
    (j:)B<override>(X:int):int = 30 + X
-->
<!-- 371 -->
```verse
Obj := collision{}
Obj.(i:)B(1)  # Returns 21
Obj.(j:)B(1)  # Returns 31
```

Without qualifiers, the compiler cannot determine which interface's
method you're implementing, resulting in an error. The qualification
makes your intent explicit.

**Complex interface hierarchies:**

<!-- 38 -->
```verse
i := interface:
    C(X:int):int

j := interface(i):
    A(X:int):int

k := interface(i):
    B(X:int):int
    (k:)C(X:int):int  # k redefines C

multi := class(j, k):
    A<override>(X:int):int = 10 + X
    B<override>(X:int):int = 20 + X
    # Must implement C from both inheritance paths
    (i:)C<override>(X:int):int = 30 + X
    (k:)C<override>(X:int):int = 40 + X
```

A use case:

<!--versetest
i := interface:
    C(X:int):int

j := interface(i):
    A(X:int):int

k := interface(i):
    B(X:int):int
    (k:)C(X:int):int  # k redefines C

multi := class(j, k):
    A<override>(X:int):int = 10 + X
    B<override>(X:int):int = 20 + X
    # Must implement C from both inheritance paths
    (i:)C<override>(X:int):int = 30 + X
    (k:)C<override>(X:int):int = 40 + X
-->
<!-- 381 -->
```verse
Obj := multi{}
Obj.(i:)C(1)  # Returns 31
Obj.(k:)C(1)  # Returns 41
```

When an interface redefines a method from a parent interface using
qualification `(k:)C`, implementing classes must provide
separate implementations for both variants.

### Nested Module Qualification

Modules can be nested, and deeply qualified names reference members
through the entire hierarchy:

<!-- 39 -->
```verse
top := module:
    (top:)m<public> := module:
        (top.m:)Value<public>:int = 1
        (top.m:)F<public>(X:int):int = X + 10

        (top.m:)m<public> := module:
            (top.m.m:)Value<public>:int = 3
            (top.m.m:)F<public>(X:int):int = X + 100
```

And a use case:

<!--versetest
top := module:
    (top:)m<public> := module:
        (top.m:)Value<public>:int = 1
        (top.m:)F<public>(X:int):int = X + 10

        (top.m:)m<public> := module:
            (top.m.m:)Value<public>:int = 3
            (top.m.m:)F<public>(X:int):int = X + 100

using { top.m }
using { top.m.m }

-->
<!-- 391 -->
```verse
# using { top.m }
# using { top.m.m }

# Access with full qualification
(top.m:)F(0)          # Returns 10
(top.m.m:)F(0)        # Returns 100

# Access via path
top.m.F(1)            # Returns 11
top.m.m.F(1)          # Returns 101
```

Nested modules can have the same simple name (e.g., both `m`)
when qualified with their full path, allowing hierarchical
organization without naming conflicts.

### Restrictions

Qualifiers can only be used in appropriate contexts. You cannot use
class qualifiers for local variables:

<!--NoCompile-->
<!-- 40 -->
```verse
C := class:
    f():void =
        (C:)X:int = 0  # ERROR - wrong context
```

Certain qualifiers are not supported. Function qualifiers for local
variables are not allowed:

<!--NoCompile-->
<!-- 41 -->
```verse
C := class:
    f():void =
        (C.f:)X:int = 0  # ERROR - unsupported pattern
```

Similarly, using module function paths as qualifiers is not supported:

<!--NoCompile-->
<!-- 42 -->
```verse
M := module:
    f():void =
        (M.f:)X:int = 0  # ERROR
```

Local variables cannot shadow class members:

<!--NoCompile-->
<!-- 43 -->
```verse
A := class:
    I:int
    F(X:int):void =
        I:int = 5  # ERROR - shadows member I
```

Currently, there is no `(local:)` qualifier to disambiguate, so this
pattern is not supported. You must use different names for local
variables and members.

## Parametric Classes

Parametric classes, also known as generic classes, allow you to define
classes that work with any type. Rather than writing separate
container classes for integers, strings, players, and every other
type, you write one parametric class that accepts a type parameter.

A parametric class takes one or more type parameters in its definition:

<!-- 46 -->
```verse
# Simple container that holds a single value
container(t:type) := class:
    Value:t
```

Here are examples of instantiating this parametric class with different types:

<!--versetest
# Simple container that holds a single value
container(t:type) := class:
    Value:t

player := class:
    Name:string
    var Health:int = 100
-->
<!-- 461 -->
```verse
# Can be instantiated with any type
IntContainer := container(int){Value := 42}
StringContainer := container(string){Value := "hello"}
PlayerContainer := container(player){Value := player{Name := "Hero", Health := 100}}
```

The syntax `container(t:type)` defines a class that is parameterized by type `t`. Within the class definition, `t` can be used anywhere a concrete type would appear—in field declarations, method signatures, or return types.

**Multiple type parameters:**

Classes can accept multiple type parameters:

<!-- 47 -->
```verse
pair(t:type, u:type) := class:
    First:t
    Second:u
```

Here are examples of using the parametric pair class:

<!--versetest
pair(t:type, u:type) := class:
    First:t
    Second:u
-->
<!-- 471 -->
```verse
# Different types for each parameter
Coordinate := pair(int, int){First := 10, Second := 20}
NamedValue := pair(string, float){First := "score", Second := 99.5}
```

**Type parameters in methods:**

Type parameters are available throughout the class, including in methods:

TODO
<!--NoCompile-->
<!-- 48 -->
```verse
optional_container(t:type) := class:
    var MaybeValue:?t = false

    Set(Value:t):void =
        set MaybeValue = option{Value}

    Get()<decides>:t =
        MaybeValue?

    Clear():void =
        set MaybeValue = false
```

Methods automatically know about the type parameter from the class
definition—you don't redeclare it in method signatures.

### Instantiation and Identity

When you instantiate a parametric class with specific type arguments,
Verse creates a concrete type. Critically, **multiple instantiations
with the same type arguments produce the same type**:

<!-- 49 -->
```verse
container(t:type) := class:
    Value:t

# These are the same type
Type1 := container(int)
Type2 := container(int)
Type3 := container(int)

# All three are equal - they're the same type
```

This type identity is guaranteed across the program:

<!--versetest
container(t:type) := class:
    Value:t
-->
<!-- 50 -->
```verse
# Create instances
C1 := container(int){Value := 1}
C2 := container(int){Value := 2}

# Both have the same type: container(int)
# Type checking treats them identically
```

The instantiation process is **deterministic and memoized**. The first
time you write `container(int)`, Verse generates a concrete
type. Every subsequent use of `container(int)` refers to that same
type, not a new copy.

This matters for:

- **Type compatibility**: Two values of `container(int)` can be used
  interchangeably
- **Memory efficiency**: Not creating duplicate type definitions
- **Semantic correctness**: Same type arguments always mean the same type

While the same type arguments always produce the same type, different
type arguments produce distinct, incompatible types:

<!-- 52 -->
```verse
container(t:type) := class:
    Value:t
```

Here's an example showing that different instantiations create distinct types:

<!--versetest
container(t:type) := class:
    Value:t
-->
<!-- 521 -->
```verse
IntContainer := container(int){Value := 42}
StringContainer := container(string){Value := "text"}

# These are different types and cannot be mixed
# IntContainer = StringContainer  # Type error!
```

`container(int)` and `container(string)` are completely different
types, with no subtype relationship. They happen to share the same
structure (both defined from `container`), but that doesn't make them
compatible.

While different instantiations of a parametric class are distinct
types, Verse allows certain instantiations to be used in place of
others based on **variance**. Variance determines when
`parametric_class(subtype)` can be used where
`parametric_class(supertype)` is expected (or vice versa).

The variance of a parametric type depends on how the type parameter is
used within the class definition:

#### Covariant

When a type parameter appears only in **return positions** (method
return types, field types being read), the parametric class is
**covariant** in that parameter (see
[Types](11_types.md#understanding-subtyping) for details on
variance). This means instantiations follow the same subtyping
direction as their type arguments:

<!-- 53 -->
```verse
# Base class hierarchy
entity := class:
    ID:int

player := class(entity):
    Name:string

# Covariant class - type parameter only in return position
producer(t:type) := class:
    Value:t

    Get():t = Value  # Returns t - covariant position

# Can use producer(player) where producer(entity) expected
ProcessProducer(P:producer(entity)):int = P.Get().ID
```

Here's an example demonstrating covariance:

<!--versetest
# Base class hierarchy
entity := class:
    ID:int

player := class(entity):
    Name:string

# Covariant class - type parameter only in return position
producer(t:type) := class:
    Value:t

    Get():t = Value  # Returns t - covariant position

# Can use producer(player) where producer(entity) expected
ProcessProducer(P:producer(entity)):int = P.Get().ID
-->
<!-- 531 -->
```verse
# Covariance allows subtype → supertype
PlayerProducer:producer(player) = producer(player){Value := player{ID := 1, Name := "Alice"}}
EntityProducer:producer(entity) = PlayerProducer  # Valid!

Result := ProcessProducer(PlayerProducer)  # Works!
```

**Why this is safe:** If you expect to get an `entity` from a
producer, receiving a `player` (which is a subtype of `entity`) is
always valid—a `player` has all the properties of an `entity`.

**Direction:** `producer(player)` → `producer(entity)` ✓ (follows
subtype direction)

#### Contravariant

When a type parameter appears only in **parameter positions** (method
parameters being consumed), the parametric class is **contravariant**
in that parameter (see [Types](11_types.md#understanding-subtyping)
for details on variance). This means instantiations follow the
**opposite** subtyping direction:


<!-- 54 -->
```verse
entity := class:
    ID:int

player := class(entity):
    Name:string

# Contravariant class - type parameter only in parameter position
consumer(t:type) := class:
    Process(Item:t):void = {}  # Accepts t - contravariant position
```

And a use case:

<!--versetest
entity := class:
    ID:int
player := class(entity):
    Name:string
consumer(t:type) := class:
    Process(Item:t):void = {}
-->
<!-- 54 -->
```verse
# Contravariance allows supertype → subtype
EntityConsumer:consumer(entity) = consumer(entity){}
PlayerConsumer:consumer(player) = EntityConsumer  # Valid!

# Can use consumer(entity) where consumer(player) expected
ProcessPlayers(C:consumer(player)):void =
    C.Process(player{ID := 1, Name := "Bob"})

ProcessPlayers(EntityConsumer)                    # Works!
```

**Why this is safe:** If you have a function that accepts any
`entity`, it can certainly handle the more specific `player` type. A
`consumer(entity)` can consume anything a `consumer(player)` can
consume, plus more.

**Direction:** `consumer(entity)` → `consumer(player)` ✓ (opposite of
subtype direction)

#### Invariant

When a type parameter appears in **both parameter and return
positions**, the parametric class is **invariant** in that
parameter. No subtyping relationship exists between different
instantiations:

<!-- 55 -->
```verse
entity := class:
    ID:int

player := class(entity):
    Name:string

# Invariant class - type parameter in both positions
transformer(t:type) := class:
    Transform(Input:t):t = Input  # Both parameter and return
```

Here's an example showing that no variance exists between different instantiations:

<!--versetest
entity := class:
    ID:int

player := class(entity):
    Name:string

# Invariant class - type parameter in both positions
transformer(t:type) := class:
    Transform(Input:t):t = Input  # Both parameter and return
-->
<!-- 551 -->
```verse
# No variance - cannot convert in either direction
EntityTransformer:transformer(entity) = transformer(entity){}
PlayerTransformer:transformer(player) = transformer(player){}

# Invalid: Cannot use one where the other is expected
# X:transformer(entity) = PlayerTransformer  # ERROR 3509
# Y:transformer(player) = EntityTransformer  # ERROR 3509
```

**Why this is necessary:** If a `transformer(player)` could be used as
a `transformer(entity)`, you could pass any `entity` to its
`Transform` method, which expects specifically a `player`. This would
be unsafe.

**Direction:** No conversion allowed in either direction

#### Bivariant

When a type parameter is not used in any method signatures (only in
private implementation details or not at all), the parametric class is
**bivariant**. Any instantiation can be converted to any other:

<!-- 56 -->
```verse
entity := class:
    ID:int

player := class(entity):
    Name:string

# Bivariant class - type parameter not used in public interface
container(t:type) := class:
    DoSomething():void = {}  # Doesn't use t at all
```

Here's an example showing that bivariant classes allow conversion in both directions:

<!--versetest
entity := class:
    ID:int

player := class(entity):
    Name:string

# Bivariant class - type parameter not used in public interface
container(t:type) := class:
    DoSomething():void = {}  # Doesn't use t at all
-->
<!-- 561 -->
```verse
# Bivariant allows conversion in both directions
EntityContainer:container(entity) = container(entity){}
PlayerContainer:container(player) = container(player){}

# Both directions work
X:container(entity) = PlayerContainer  # Valid
Y:container(player) = EntityContainer  # Also valid
```

**Why this works:** Since the type parameter doesn't affect the
observable behavior, the instantiations are interchangeable.

#### Common Pitfalls

**Attempting invalid conversions:**

TODO broken...

<!--NoCompile-->
<!-- 57 -->
```verse
# Invariant parameter - neither direction works
refer(t:type) := class:
    var Value:t
    Get():t = Value
    Set(V:t):void = set Value = V

PlayerRef:refer(player) = refer(player){Value := player{ID := 1, Name := "Test"}}

# Invalid: refer is invariant
# EntityRef:refer(entity) = PlayerRef  # ERROR
```

**Confusing variance direction:**

<!--NoCompile-->
<!-- 58 -->
```verse
# Common mistake: thinking contravariance works like covariance
consumer(t:type) := class:
    Accept(Item:t):void = {}

EntityConsumer := consumer(entity){}

# Invalid: Wrong direction for contravariance
# PlayerConsumer:consumer(player) = consumer(entity){}  # ERROR

# Valid: Contravariance goes opposite direction
PlayerConsumer:consumer(player) = EntityConsumer  # Correct!
```

### Parameter Constraints

You can constrain type parameters to require certain properties:

<!--NoCompile-->
<!-- 59 -->
```verse
# Only comparable types allowed
sorted_list(t:type where t:subtype(comparable)) := class:
    var Items:[]t = array{}

    Add(Item:t):void =
        # Can compare because t is comparable
        set Items = InsertSorted(Items, Item)

    Contains(Item:t):logic =
        for (Element : Items):
            if (Element = Item):
                return true
        false

# Valid: int is comparable
IntList := sorted_list(int){}

# Invalid: regular classes aren't comparable by default
# PlayerList := sorted_list(player){}  # Error if player isn't comparable
```

The `where` clause specifies requirements on the type
parameter. Common constraints include:

- `t:subtype(comparable)` - requires equality comparison
- `t:subtype(SomeClass)` - requires inheriting from a specific class
- `t:type` - any type (the default if no constraint specified)

### Restrictions

Parametric classes have certain limitations:

**Cannot be `<castable>`:**

Parametric classes cannot use the `<castable>` specifier because
runtime type checks require knowing the concrete type:

<!--NoCompile-->
<!-- 60 -->
```verse
# Invalid: parametric classes cannot be castable
container(t:type) := class<castable>:  # Error!
    Value:t
```

However, specific instantiations can be used where `<castable>` types
are needed:

<!--NoCompile-->
<!-- 61 -->
```verse
component := class<castable>{}

container(t:type) := class:
    Value:t

# Error not supported
ProcessComponent(Comp:component):void =
    if (Wrapped := container(component)[Comp]):
        # Wrapped is container(component)
```

**Cannot cast between different parametric instantiations:**

Even when instantiations are fixed (non-parametric), you cannot use
cast syntax to convert between different instantiations of the same
parametric class or interface. This restriction is enforced at compile
time:

<!-- 62 -->
```verse
container(t:type) := class:
    Value:t
```

Here's an example showing that you cannot cast between different instantiations:

<!--versetest
container(t:type) := class:
    Value:t
-->
<!-- 621 -->
```verse
X := container(int){Value := 42}

# Invalid: Cannot cast between different instantiations
# if (Y := container(float)[X]):     # ERROR 3502
#     # This will not compile
# if (Z := container([]int)[X]):     # ERROR 3502
#     # This also will not compile
```

Different instantiations like `container(int)` and `container(float)`
are completely distinct types with no subtype relationship, so cast
expressions between them are disallowed. The compiler rejects these
casts even though both are concrete types.

This restriction extends to parametric class hierarchies:

<!-- 63 -->
```verse
base := class:
    Property:int

parametric_child(t:type) := class(base):
    GetProperty():int = Property
```

Here's an example showing that you cannot cast between different instantiations in parametric class hierarchies:

<!--versetest
base := class:
    Property:int

parametric_child(t:type) := class(base):
    GetProperty():int = Property
-->
<!-- 631 -->
```verse
# Cannot cast between different instantiations of parametric_child
Foo:base = parametric_child(float){Property := 42}

# Invalid: Different type parameters prevent casting
# if (FooChild := parametric_child(int)[Foo]):  # ERROR 3502
#     # Cannot cast parametric_child(float) to parametric_child(int)
```

Even though both `parametric_child(int)` and `parametric_child(float)`
inherit from `base`, you cannot cast between them because they are
different instantiations of a parametric type.

**Parametric interfaces also cannot be used in casts:**

Cast expressions involving parametric interfaces with type parameters are disallowed:

<!-- 64 -->
```verse
parametric_interface(t:type) := interface:
    Foo():t

child := class{}

impl := class(child, parametric_interface(float)):
    Foo<override>():float = 42.42
```

Here's an example showing that you cannot cast to parametric interfaces:

<!--versetest
parametric_interface(t:type) := interface:
    Foo():t

child := class{}

impl := class(child, parametric_interface(float)):
    Foo<override>():float = 42.42
-->
<!-- 641 -->
```verse
# Invalid: Cannot cast to parametric interface with type parameter
X:child := impl{}
# if (X_Casted := parametric_interface(float)[X]):  # ERROR 3502
#     # Parametric interface casts not allowed
```

However, specialized (non-parametric) interfaces derived from parametric interfaces can be used in casts:

<!-- 65 -->
```verse
parametric_interface(t:type) := interface:
    Foo():t

# Specialized interface fixes the type parameter
specialized_interface := interface(parametric_interface(float)){}

impl := class(specialized_interface):
    Foo<override>():float = 42.42
```

Here's an example showing that specialized interfaces work with casts:

<!--versetest
parametric_interface(t:type) := interface:
    Foo():t

# Specialized interface fixes the type parameter
specialized_interface := interface(parametric_interface(float)){}

impl := class(specialized_interface):
    Foo<override>():float = 42.42
-->
<!-- 651 -->
```verse
# Valid: specialized_interface is no longer parametric
X := impl{}
if (X_Casted := specialized_interface[X]):
    X_Casted.Foo()  # Works!
```

**Valid casting scenarios:**

While casts between different parametric instantiations fail, the
following patterns work:

1. **Non-parametric class hierarchies** support normal casting:

<!-- 66 -->
```verse
base := class<castable>:
    ID:int

child := class(base):
    Name:string
```

Here's an example of normal class hierarchy casting:

<!--versetest
base := class<castable>:
    ID:int
child := class(base):
    Name:string
-->
<!-- 661 -->
```verse
B:base = child{ID := 1, Name := "Test"}
if (C := child[B]):
    # Valid: Normal class hierarchy cast
    Print(C.Name)
```

2. **Fixed parametric instantiations** where the type parameter is
   locked in the subclass:

<!-- 67 -->
```verse
parametric_base(t:type) := class:
    Property:t

# Child fixes the type parameter to int
int_child := class(parametric_base(int)):
    GetProperty():int = Property
```

Here's an example of casting with fixed parametric instantiation:

<!--versetest
parametric_base(t:type) := class:
    Property:t

# Child fixes the type parameter to int
int_child := class(parametric_base(int)):
    GetProperty():int = Property
-->
<!-- 671 -->
```verse
Foo:parametric_base(int) = int_child{Property := 42}
if (FooChild := int_child[Foo]):
    # Valid: Type parameter is fixed to int in both
    FooChild.Property = 42
```

**Cannot be `<persistable>` directly:**

While you can define parametric classes, making them persistable
requires special consideration for how the type parameter is
serialized. Specific instantiations with persistable types may work
depending on the implementation.

### Recursive Parametric Types

Parametric classes can reference themselves in their field types,
enabling recursive generic data structures like linked lists, trees,
and graphs. However, Verse imposes specific restrictions on how
recursion can occur.

The most common form of recursive parametric type is when a class
references itself with **the same type parameter**:

<!-- 69 -->
```verse
# Linked list node
list_node(t:type) := class:
    Value:t
    Next:?list_node(t)  # Same type parameter 't'

# Helper to create lists
Cons(Head:t, Tail:?list_node(t) where t:type):list_node(t) =
    list_node(t){Value := Head, Next := Tail}

# Sum a linked list
SumList(List:?list_node(int)):int =
    if (Head := List?):
        Head.Value + SumList(Head.Next)
    else:
        0
```

Here's an example of using the linked list:

<!--versetest
# Linked list node
list_node(t:type) := class:
    Value:t
    Next:?list_node(t)  # Same type parameter 't'

# Helper to create lists
Cons(Head:t, Tail:?list_node(t) where t:type):list_node(t) =
    list_node(t){Value := Head, Next := Tail}

# Sum a linked list
SumList(List:?list_node(int)):int =
    if (Head := List?):
        Head.Value + SumList(Head.Next)
    else:
        0
-->
<!-- 691 -->
```verse
# Usage
IntList := list_node(int){
    Value := 1
    Next := option{list_node(int){
        Value := 2
        Next := false
    }}
}
```

Binary trees work similarly:

TODO Broken

<!--NoCompile-->
<!-- 70 -->
```verse
tree_node(t:type) := class:
    Value:t
    var Left:?tree_node(t) = false   # Same parameter
    var Right:?tree_node(t) = false  # Same parameter

# Create a tree
Root := tree_node(int){
    Value := 5
    Left := option{tree_node(int){Value := 3}}
    Right := option{tree_node(int){Value := 7}}
}
```

**Why this works:** Each instantiation creates a complete, consistent
type. `list_node(int)` always contains `int` values and references
other `list_node(int)` nodes. The type system can verify this
recursion is well-formed.

**Disallowed: Direct Type Alias Recursion**

You cannot define a parametric type that directly aliases to a
structural type containing itself:

<!-- 71 -->
```verse
# Invalid: Direct array recursion
# t(u:type) := []t(u)  # ERROR 3502

# Invalid: Direct map recursion
# t(u:type) := [int]t(u)  # ERROR 3502

# Invalid: Direct optional recursion
# t(u:type) := ?t(u)  # ERROR 3502

# Invalid: Direct function recursion
# t(u:type) := u->t(u)  # ERROR 3502
# t(u:type) := t(u)->u  # ERROR 3502
```

These fail because they create infinite type expansion—the compiler
cannot determine the actual structure of the type.

**Valid alternative:** Wrap in a class:

<!-- 72 -->
```verse
# Valid: Indirect recursion through class
nested_list(t:type) := class:
    Items:[]nested_list(t)  # OK - wrapped in class
```

Here's an example of using nested_list:

<!--versetest
# Valid: Indirect recursion through class
nested_list(t:type) := class:
    Items:[]nested_list(t)  # OK - wrapped in class
-->
<!-- 721 -->
```verse
Tree := nested_list(int){
    Items := array{
        nested_list(int){Items := array{}},
        nested_list(int){Items := array{}}
    }
}
```

**Disallowed: Polymorphic Recursion**

Polymorphic recursion occurs when a parametric type references itself
with a **different type argument**:

<!--NoCompile-->
<!-- 73 -->
```verse
# Invalid: Type parameter changes
# my_type(t:type) := class:
#     Next:my_type(?t)  # ERROR 3509 - ?t is different from t

# Invalid: Alternating type parameters
# bi_list(t:type, u:type) := class:
#     Value:t
#     Next:?bi_list(u, t)  # ERROR 3509 - parameters swapped
```

**Why this is disallowed:** Polymorphic recursion makes type inference
undecidable and can create infinitely complex types. When you
instantiate `my_type(int)`, it would need `my_type(?int)`, which needs
`my_type(??int)`, and so on forever.

**Current limitation:** While polymorphic recursion is theoretically
sound in some type systems, Verse currently does not support it to
keep type checking tractable.

**Disallowed: Mutual Recursion**

Mutual recursion between multiple parametric types is not supported:

<!-- 74 -->
```verse
# Invalid: Mutual recursion
# t1(t:type) := class:
#     Next:?t2(t)  # References t2
#
# t2(t:type) := class:
#     Next:?t1(t)  # References t1
#
# # ERROR 3509, 3509
```

**Why this is disallowed:** Similar to polymorphic recursion, mutual
recursion complicates type inference and can create circular
dependencies that are difficult for the compiler to resolve.

**Workaround:** Combine into a single type:

<!-- 75 -->
```verse
# Valid: Single type with multiple cases
node_type := enum:
    TypeA
    TypeB

combined_node(t:type) := class:
    Type:node_type
    Value:t
    Next:?combined_node(t)
```

**Disallowed: Inheritance Recursion**

You cannot inherit from a type variable or create recursive
inheritance through parametric types:

<!-- 76 -->
```verse
# Invalid: Inheriting from parametric self
# t(u:type) := class(t(u)){}  # ERROR 3590

# Invalid: Inheriting from type variable
# inherits_from_variable(t:type) := class(t){}  # ERROR 3590
```

**Why this is disallowed:** Inheritance requires knowing the parent's
structure,but with parametric recursion, this structure would be
self-referential before being defined.


### Parametric Interfaces

While parametric classes get most of the attention, interfaces can
also be parametric, enabling abstract contracts that work with any
type:

<!-- TODO why is this not working?-->

<!-- 80 -->
```verse
# Generic equality interface
equivalence(t:type, u:type) := interface:
    Equal(Left:t, Right:u)<transacts><decides>:t

# Generic collection interface
collection_ifc(t:type) := interface:
    Add(Item:t)<transacts>:void
    Remove(Item:t)<transacts><decides>:void
    Has(Item:t)<reads>:logic
```

Classes implement parametric interfaces by providing concrete types
for the parameters:

<!-- 81 -->
```verse
equivalence(t:type, u:type) := interface:
    Equal(Left:t, Right:u)<transacts><decides>:t

# Implement with specific types
int_equivalence := class(equivalence(int, comparable)):
    Equal<override>(Left:int, Right:comparable)<transacts><decides>:int =
        Left = Right

# Or with type parameters matching the class
comparable_equivalence(t:subtype(comparable)) := class(equivalence(t, comparable)):
    Equal<override>(Left:t, Right:comparable)<transacts><decides>:t =
        Left = Right
```

Here's an example of using the parametric interface:

<!--versetest
equivalence(t:type, u:type) := interface:
    Equal(Left:t, Right:u)<transacts><decides>:t

# Implement with specific types
int_equivalence := class(equivalence(int, comparable)):
    Equal<override>(Left:int, Right:comparable)<transacts><decides>:int =
        Left = Right

# Or with type parameters matching the class
comparable_equivalence(t:subtype(comparable)) := class(equivalence(t, comparable)):
    Equal<override>(Left:t, Right:comparable)<transacts><decides>:t =
        Left = Right
-->
<!-- 811 -->
```verse
# Usage
Eq := comparable_equivalence(int){}
Eq.Equal[5, 5]  # Succeeds
```

Parametric interfaces follow the same variance rules as parametric classes:

<!-- 82 -->
```verse
entity := class:
    ID:int

player := class(entity):
    Name:string

# Covariant interface - returns t
producer_interface(t:type) := interface:
    Produce():t

player_producer := class(producer_interface(player)):
    Produce<override>():player = player{ID := 1, Name := "Test"}
```

Here's an example of covariant subtyping:

<!--versetest
entity := class:
    ID:int

player := class(entity):
    Name:string

# Covariant interface - returns t
producer_interface(t:type) := interface:
    Produce():t

player_producer := class(producer_interface(player)):
    Produce<override>():player = player{ID := 1, Name := "Test"}
-->
<!-- 821 -->
```verse
# Covariant subtyping works
EntityProducer:producer_interface(entity) = player_producer{}
```

You can create specialized (non-parametric) interfaces from parametric ones:

<!-- 83 -->
```verse
generic_handler(t:type) := interface:
    Handle(Item:t):void

# Specialize to a concrete type
int_handler := interface(generic_handler(int)):
    # Inherits Handle(Item:int):void
    # Can add more methods here

int_processor := class(int_handler):
    Handle<override>(Item:int):void =
        Print("Handling: {Item}")
```

Here's an example of using specialized interfaces in casts:

<!--versetest
generic_handler(t:type) := interface:
    Handle(Item:t):void

# Specialize to a concrete type
int_handler := interface(generic_handler(int)):
    # Inherits Handle(Item:int):void
    # Can add more methods here

int_processor := class(int_handler):
    Handle<override>(Item:int):void =
        Print("Handling: {Item}")
-->
<!-- 831 -->
```verse
# Can use in casts now (specialized interfaces are non-parametric)
Base := int_processor{}
if (Handler := int_handler[Base]):
    Handler.Handle(42)
```

#### Multiple Type Parameters

Interfaces can have multiple type parameters with independent variance:

<!-- 84 -->
```verse
converter_interface(input:type, output:type) := interface:
    Convert(In:input):output
    # input is contravariant, output is covariant

entity := class:
    ID:int

player := class(entity):
    Name:string

# Implement with specific types
player_to_entity := class(converter_interface(player, entity)):
    Convert<override>(In:player):entity = entity{ID := In.ID}
```

Is used here:

<!--versetest
converter_interface(input:type, output:type) := interface:
    Convert(In:input):output
    # input is contravariant, output is covariant

entity := class:
    ID:int

player := class(entity):
    Name:string

# Implement with specific types
player_to_entity := class(converter_interface(player, entity)):
    Convert<override>(In:player):entity = entity{ID := In.ID}
<#
-->
<!-- 841 -->
```verse
# Variance allows flexible usage
C:converter_interface(player, entity) = player_to_entity{}
```
<!-- #> -->

### Advanced Parametric Types

#### First-Class Parametrics

Parametric type definitions can be used as first-class values, allowing dynamic type application:

<!--NoCompile
 TODO : Unnecessary restriction to the compiler according to Andy
container(t:type) := class:
    Value:t
TypeConstructor := container
-->
<!-- 85 -->
```verse
# Parametric class
container(t:type) := class:
    Value:t

# Store parametric type as value
TypeConstructor := container
```

And a use case:

<!--NoCompile  TODO : Unnecessary restriction to the compielr according to Andy
container(t:type) := class:
    Value:t
TypeConstructor := container
-->
<!-- 851 -->
```verse
# Apply type argument dynamically
IntContainer := TypeConstructor(int)

# Construct instance
Instance := IntContainer{Value := 42}
Instance.Value = 42  # Success
```

This enables powerful patterns for generic factories and type-driven
programming:

<!--NoCompile
<!-- 86 -->
```verse
# Factory that works with any parametric container
CreateContainer(TypeCtor:type, Value:t where t:type) :type=
    TypeCtor(t){Value := Value}

# Can work with different container types
container1(t:type) := class:
    Value:t

container2(t:type) := class:
    Data:t
```
-->

And a use:

<!--NoCompile
CreateContainer(TypeCtor:type, Value:t where t:type) :=
    TypeCtor(t){Value := Value}

container1(t:type) := class:
    Value:t

container2(t:type) := class:
    Data:t
-->
<!-- 86 -->
```verse
X := CreateContainer(container1, 42)  # container1(int)
Y := CreateContainer(container2, "hello")  # container2(string)
```

#### Effects

Parametric types can have effect specifiers that apply to all instantiations:

<!-- 88 -->
```verse
# Parametric class with effects
async_container(t:type) := class<computes>:
    Property:t

# All instantiations inherit the effect
X:async_container(int) = async_container(int){Property := 1}  # <computes> effect

# Multiple effects
transactional_container(t:type) := class<transacts>:
    Property:t

# Constructor inherits effects
# Y:transactional_container(int) = transactional_container(int){Property := 2}
```

**Allowed effects:**

- `<computes>` - Allows non-terminating computation
- `<transacts>` - Participates in transactions
- `<reads>` - Reads mutable state
- `<writes>` - Writes mutable state
- `<allocates>` - Allocates resources

**Not allowed:**

- `<decides>` - Can fail
- `<suspends>` - Can suspend execution
- `<converges>` - Would conflict with parametric instantiation 

**Effect propagation:**

<!-- 89 -->
```verse
# Effect on parametric type propagates to constructor
my_type(t:type) := class<computes>:
    Property:t

# This requires <computes> in the context
CreateInstance()<computes>:my_type(int) =
    my_type(int){Property := 1}
```

The effect becomes part of the type's contract—all code constructing or working with instances must account for these effects.

#### Aliases

You can create type aliases that simplify complex parametric type expressions:

<!-- 92 -->
```verse
# Alias for map type
string_map(t:type) := [string]t

# Use the alias
PlayerScores:string_map(int) = map{
    "Alice" => 100,
    "Bob" => 95
}

# Alias for optional array
optional_array(t:type) := []?t

# Simplifies type signatures
FilterValid(Items:optional_array(int)):[]int =
    for (Item : Items; Value := Item?):
        Value
```

**Composing parametric aliases:**

<!-- 93 -->
```verse
# Nested parametric aliases
map_alias(k:type where k:subtype(comparable), v:type) := [k]v   # k must be comparable (int, string, etc.)
array_alias(t:type) := []t

# Compose them
nested(t:type) := array_alias(map_alias(string, t))

# Usage: []([string]t)
Data:nested(int) = array{
    map{"a" => 1, "b" => 2},
    map{"c" => 3}
}
```

**Structural type aliases:**

<!-- 94 -->
```verse
# Function type aliases
transformer(input:type, output:type) := input -> output
predicate(t:type) := t -> logic

# Tuple type aliases
pair(t:type, u:type) := tuple(t, u)
triple(t:type) := tuple(t, t, t)

# Use in signatures
ApplyTransform(T:transformer(int, string), Value:int):string =
    T(Value)

CheckCondition(P:predicate(int), Value:int):logic =
    P(Value)
```

Type aliases improve readability and maintainability for complex generic types.

#### Advanced Type Constraints

Beyond basic `subtype` constraints, parametric types support specialized constraints:

**Subtype constraints:**

<!--versetest
entity:=class{ID:int=0}
player:=class(entity){}

# Constrain to subtype of a class
bounded_container(t:subtype(entity)) := class:
    Value:t

    GetID():int = Value.ID  # Can access entity members

# Valid: player is subtype of entity
# PlayerContainer := bounded_container(player){}

# Invalid: int is not subtype of entity
# IntContainer := bounded_container(int){}  # Type error

<#
-->
<!-- 95 -->
```verse
# Constrain to subtype of a class
bounded_container(t:subtype(entity)) := class:
    Value:t

    GetID():int = Value.ID  # Can access entity members

# Valid: player is subtype of entity
# PlayerContainer := bounded_container(player){}

# Invalid: int is not subtype of entity
# IntContainer := bounded_container(int){}  # Type error
```
<!-- #> -->

**Castable subtype constraints:**

<!--versetest
component:=class<castable>{}
ProcessTyped(:component)<computes>:void={}

# Requires castable subtype
dynamic_handler(t:castable_subtype(component)) := class:
    Handle(Item:component):void =
        if (Typed := t[Item]):
            # Typed has the specific subtype
            ProcessTyped(Typed)

<#
-->
<!-- 96 -->
```verse
# Requires castable subtype
dynamic_handler(t:castable_subtype(component)) := class:
    Handle(Item:component):void =
        if (Typed := t[Item]):
            # Typed has the specific subtype
            ProcessTyped(Typed)
```
<!-- #> -->

**Multiple constraints:**

TODO BROKEN

<!--NoCompile-->
<!-- 97 -->
```verse
# Combine multiple requirements
sorted_unique(t:type where t:subtype(comparable)) := class<unique>:
    var Items:[]t = array{}

    Add(Item:t):void =
        # Can use comparison because t:subtype(comparable)
        if (not Contains(Item)):
            set Items = Sort(Items + array{Item})

    Contains(Item:t):logic =
        for (Element : Items):
            if (Element = Item):
                return true
        false
```

**Constraint propagation:**

<!-- 98 -->
```verse
# Constraints propagate through function calls
wrapper(t:subtype(comparable)) := class:
    Data:t

Process(W:wrapper(t) where t:subtype(comparable))<computes><decides>:void =
    # Compiler knows t is comparable here
    W.Data = W.Data
```

When defining parametric functions that work with parametric types,
the constraints must be compatible:

<!-- 99 -->
```verse
base_class := class:
    ID:int

constrained(t:subtype(base_class)) := class:
    Data:t

# Valid: Constraint matches
UseConstrained(C:constrained(t) where t:subtype(base_class)):int =
    C.Data.ID

# Invalid: Missing or incompatible constraint
# UseConstrained(C:constrained(t) where t:type):int =  # ERROR 3509
#     C.Data.ID
```

### Access Specifiers

Classes support fine-grained control over member visibility through
access specifiers:

<!-- 100 -->
```verse
game_state := class:
    Score<public> : int = 0                    # Anyone can read
    var Lives<private> : int = 3               # Only this class can access
    var Shield<protected> : float = 100.0      # This class and subclasses
    DebugInfo<internal> : string = ""          # Same module only

    # Public method - anyone can call
    GetLives<public>() : int = Lives

    # Protected method - subclasses can override
    OnLifeLost<protected>() : void = {}

    # Private helper - only this class
    ValidateState<private>() : void = {}
```

Access specifiers apply to both fields and methods, controlling who
can read fields and call methods. The default visibility is
`internal`, restricting access to the same module. This encapsulation
is crucial for maintaining class invariants and hiding implementation
details.

### Concrete

The `<concrete>` specifier enforces that all fields have default
values, allowing construction with an empty archetype:

<!--NoCompile-->
<!-- 101 -->
```verse
config := class<concrete>:
    MaxPlayers : int = 8
    TimeLimit : float = 300.0
    FriendlyFire : logic = false

# Can construct with empty archetype
DefaultConfig := config{}
```

This is particularly useful for configuration classes where reasonable
defaults exist for all values.

A concrete class `C` can be constructed by writing `C{}`, that is to say with the empty archetype.

A concrete class may have non-concrete subclasses.

### Unique

The `<unique>` specifier creates classes and interfaces with reference
semantics where each instance has a distinct identity. When a class or
interface is marked as `<unique>`, instances become comparable using
the equality operators (= and <>), with equality based on object
identity rather than field values.

Classes marked with `<unique>` compare by identity, not by value:

<!--verse
vector3:=struct{X:float,Y:float,Z:float}
entity := class<unique>:
   Name : string
   Position : vector3
F()<decides>:void={
E1 := entity{Name := "Guard", Position := vector3{X := 0.0, Y := 0.0, Z := 0.0}}
E2 := entity{Name := "Guard", Position := vector3{X := 0.0, Y := 0.0, Z := 0.0}}
E3 := E1

E1 = E2  # Fails - different instances despite identical field values
E1 = E3  # Succeeds - same instance
}
<#
-->
<!-- 102 -->
```verse
entity := class<unique>:
   Name : string
   Position : vector3

E1 := entity{Name := "Guard", Position := vector3{X := 0.0, Y := 0.0, Z := 0.0}}
E2 := entity{Name := "Guard", Position := vector3{X := 0.0, Y := 0.0, Z := 0.0}}
E3 := E1

E1 = E2  # Fails - different instances despite identical field values
E1 = E3  # Succeeds - same instance
```
<!-- #> -->

Without `<unique>`, class instances cannot be compared for equality at
all—the language prevents meaningless comparisons. With `<unique>`,
you gain the ability to use instances as map keys, store them in sets,
and perform identity checks, essential for tracking specific objects
throughout their lifetime.

#### Interfaces

Interfaces can also be marked with `<unique>`, which makes all
instances of classes implementing that interface comparable by
identity:

<!-- 103 -->
```verse
component := interface<unique>:
    Update():void
    Render():void

physics_component := class(component):
    Update<override>():void = {}
    Render<override>():void = {}
```

And a use case:

<!--versetest
component := interface<unique>:
    Update():void
    Render():void

physics_component := class(component):
    Update<override>():void = {}
    Render<override>():void = {}
-->
<!-- 1031 -->
```verse
# Instances are comparable because component is unique
P1 := physics_component{}
P2 := physics_component{}

P1 <> P2  # true - different instances
P1 = P1   # true - same instance
```

The `<unique>` property propagates through interface inheritance. If a
parent interface is marked `<unique>`, all child interfaces and
classes implementing those interfaces automatically become comparable:

<!-- 104 -->
```verse
base_component := interface<unique>:
    Update():void

# Child interface inherits <unique> from parent
advanced_component := interface(base_component):
    AdvancedUpdate():void

# Classes implementing any interface in the hierarchy become comparable
player_component := class(advanced_component):
    Update<override>():void = {}
    AdvancedUpdate<override>():void = {}
```

And a use case:

<!--versetest
base_component := interface<unique>:
    Update():void

# Child interface inherits <unique> from parent
advanced_component := interface(base_component):
    AdvancedUpdate():void

# Classes implementing any interface in the hierarchy become comparable
player_component := class(advanced_component):
    Update<override>():void = {}
    AdvancedUpdate<override>():void = {}
-->
<!-- 104 -->
```verse
C1 := player_component{}
C2 := player_component{}
C1 <> C2  # true - comparable due to base_component being unique
```

When a class implements multiple interfaces, comparability is
determined by whether ANY of the inherited interfaces is `<unique>`:

<!-- 105 -->
```verse
updateable := interface:  # Not unique
    Update():void

renderable := interface<unique>:  # Unique
    Render():void

game_object := class(updateable, renderable):
    Update<override>():void = {}
    Render<override>():void = {}
```

And a use case:

<!--versetest
updateable := interface:  # Not unique
    Update():void

renderable := interface<unique>:  # Unique
    Render():void

game_object := class(updateable, renderable):
    Update<override>():void = {}
    Render<override>():void = {}
-->
<!-- 105 -->
```verse
# game_object is comparable because renderable is unique
G1 := game_object{}
G2 := game_object{}
G1 <> G2  # true - comparable due to renderable interface
```

Even if most interfaces are non-unique, a single `<unique>` interface
in the hierarchy makes the entire class comparable.

#### Unique in Default Values

When a `<unique>` class appears in a field's default value, each
containing object receives its own distinct instance. This guarantee
applies even when the unique class is nested within complex parametric
types:

<!-- 106 -->
```verse
token := class<unique>:
    ID:int = 0

container := class:
    MyToken:token = token{}
```

And a use case:

<!--versetest
token := class<unique>:
    ID:int = 0

container := class:
    MyToken:token = token{}
-->
<!-- 106 -->
```verse
C1 := container{}
C2 := container{}
C1.MyToken <> C2.MyToken  # true - each container has its own unique token
```

This behavior extends to `<unique>` instances within arrays,
optionals, tuples, and maps:

<!-- 107 -->
```verse
item := class<unique>{}

# Each class instantiation creates fresh unique instances in default values
with_array := class:
    Items:[]item = array{item{}}

with_optional := class:
    MaybeItem:?item = option{item{}}

with_map := class:
    ItemMap:[int]item = map{0 => item{}}
```

And a use case:

<!--versetest
item := class<unique>{}

# Each class instantiation creates fresh unique instances in default values
with_array := class:
    Items:[]item = array{item{}}

with_optional := class:
    MaybeItem:?item = option{item{}}

with_map := class:
    ItemMap:[int]item = map{0 => item{}}
-->
<!-- 107 -->
```verse
A := with_array{}
B := with_array{}
A.Items[0] <> B.Items[0]  # true - different unique instances

C := with_optional{}
D := with_optional{}
if (ItemC := C.MaybeItem?, ItemD := D.MaybeItem?):
    ItemC <> ItemD  # true - different unique instances
```

The same principle applies when parametric classes contain unique
instances in their fields:


<!-- 108 -->
```verse
entity := class<unique>{}

registry(t:type) := class:
    DefaultEntity:entity = entity{}
    Data:t
```

And a use case:

<!--versetest
entity := class<unique>{}

registry(t:type) := class:
    DefaultEntity:entity = entity{}
    Data:t
-->
<!-- 1081 -->
```verse
R1 := registry(int){Data:=1}
R2 := registry(int){Data:=2}
R1.DefaultEntity <> R2.DefaultEntity  # true

R3 := registry(string){Data:="hi"}
R3.DefaultEntity <> R1.DefaultEntity  # true - even across different type parameters
```

This guarantee ensures that identity-based operations remain
reliable. If you store objects in maps keyed by unique instances, or
maintain sets of unique objects, each container genuinely owns
distinct instances rather than sharing references. The language
prevents subtle bugs where multiple objects might unexpectedly share
the same identity.

#### Overload Resolution

Types marked with `<unique>` are subtypes of the built-in `comparable`
type. This can create overload ambiguity:

<!-- 109 -->
```verse
# Valid: non-unique interface doesn't conflict with comparable
regular_interface := interface:
    Method():void

Process(A:comparable, B:comparable):void = {}
Process(A:regular_interface, B:regular_interface):void = {}  # OK - no conflict

# Invalid: unique interface conflicts with comparable
unique_interface := interface<unique>:
    Method():void

Handle(A:comparable, B:comparable):void = {}
# Handle(A:unique_interface, B:unique_interface):void = {}  # ERROR - ambiguous!
```

Since `unique_interface` is a subtype of `comparable`, both overloads
could match when called with `unique_interface` arguments, causing a
compilation error. When designing overloaded functions, be aware that
`<unique>` types participate in the `comparable` type hierarchy.

#### Use Cases

The `<unique>` specifier is ideal for:

**Game Entities:** Where each entity in the world must be
distinguishable regardless of current state

<!--versetest
vector3:=class<final>{ X:float=0.0; Y:float=0.0; Z:float=0.0 }
entity := class<unique>:
    var Health:int = 100
    var Position:vector3
-->
<!-- 110 -->
```verse
#entity := class<unique>:
#    var Health:int = 100
#    var Position:vector3

# Can track specific entities in collections
var ActiveEntities:[entity]logic = map{}
```

**Component Interfaces:** Where you need identity-based equality for
interface types

<!--versetest
entity:=class:

component := interface<unique>:
    Owner:entity
    Update():void
-->
<!-- 111 -->
```verse
#component := interface<unique>:
#    Owner:entity

# Can use interface references as map keys
var ComponentRegistry:[component]string = map{}
```

**Session Objects:** Where identity matters more than current property values

<!--versetest
connection_info := class:

player_session := class<unique>:
    PlayerID:string
    var ConnectionTime:float
-->
<!-- 112 -->
```verse
#player_session := class<unique>:
#    PlayerID:string
#    var ConnectionTime:float

# Track specific sessions
var ActiveSessions:[player_session]connection_info = map{}
```

**Resource Handles:** Where you need to track specific instances
rather than equivalent values

<!--versetest
gpu_resource:=class:

texture_handle := class<unique>:
    ResourceID:int
    FilePath:string
-->
<!-- 113 -->
```verse
#texture_handle := class<unique>:
#    ResourceID:int
#    FilePath:string

# Manage resource lifecycle
var LoadedTextures:[texture_handle]gpu_resource = map{}
```

The `<unique>` specifier enables these patterns by providing
identity-based equality semantics, making it possible to use instances
as map keys, maintain sets of unique objects, and distinguish between
different instances even when their data is identical.

### Abstract

The `<abstract>` specifier marks classes that cannot be instantiated
directly — they exist solely as base classes for inheritance. When you
declare a class with `<abstract>`, you're creating a template that
defines structure and behavior for subclasses to inherit and
implement.

Abstract classes serve as architectural foundations in a type
hierarchy. They define contracts through abstract methods that
subclasses must implement, while potentially providing concrete
methods and fields that subclasses inherit. This creates a powerful
pattern for code reuse and polymorphic behavior.

<!-- 114 -->
```verse
  vehicle := class<abstract>:
      Speed():float             # Abstract method
      MaxPassengers:int = 1

      # Concrete method all vehicles share
      CanTransport(Count:int)<decides>:void =
          Count <= MaxPassengers

  car := class(vehicle):
      Speed<override>():float = 60.0
      MaxPassengers<override>:int = 4

  bicycle := class(vehicle):
      Speed<override>():float = 15.0
```

Abstract methods within abstract classes have no implementation —
they're pure declarations that establish what subclasses must
provide. An abstract method creates a contract: any non-abstract
subclass must override all abstract methods or the code won't compile.

### Castable

The `<castable>` specifier enables runtime type checking and safe
downcasting for classes. When a class is marked with `<castable>`, you
can use dynamic type tests and casts to determine if an object is an
instance of that class or its subclasses at runtime.

Without `<castable>`, Verse's type system operates purely at compile
time. The `<castable>` specifier adds runtime type information,
allowing code to inspect and react to actual object types during
execution. This bridges the gap between static type safety and dynamic
polymorphism.

Verse provides two forms of type casting: **fallible casts** (which
can fail at runtime) and **infallible casts** (which are verified at
compile time).

**Fallible casts** use bracket syntax `Type[Value]` and return an
optional result. These are runtime checks that succeed only if the
value is actually an instance of the target type:

<!--verse
vector3:=class<final>{ X:float=0.0; Y:float=0.0; Z:float=0.0 }
ToString(:vector3):string=""
-->
<!-- 115 -->
```verse
component := class<abstract><castable><allocates>:
    Name:string

physics_component := class<allocates>(component):
    Name<override>:string = "Physics"
    Velocity:vector3

render_component := class<allocates>(component):
    Name<override>:string = "Render"
    Material:string

ProcessComponent(Comp:component):void =
    # Attempt to cast to physics_component
    if (PhysicsComp := physics_component[Comp]):
        # Cast succeeded - PhysicsComp has type physics_component
        Print("Physics component with velocity: {PhysicsComp.Velocity}")
    else if (RenderComp := render_component[Comp]):
        # Cast succeeded - RenderComp has type render_component
        Print("Render component with material: {RenderComp.Material}")
    else:
        # Neither cast succeeded
        Print("Unknown component type")
```

The cast expression has the `<decides>` effect—it fails if the object
is not an instance of the target type. This integrates naturally with
Verse's failure handling:

<!--versetest
vector3:=class<final><allocates>{ X:float=0.0; Y:float=0.0; Z:float=0.0 }
component := class<abstract><castable><allocates>:
    Name:string

physics_component := class<allocates>(component):
    Name<override>:string = "Physics"
    Velocity:vector3=vector3{}

SomeComponent:component=physics_component{}
UpdatePhysics(:physics_component)<computes>:void={}
-->
<!-- 116 -->
```verse
GetPhysicsComponent(Comp:component)<computes><decides>:physics_component =
    # Returns physics_component or fails
    physics_component[Comp]

# Use with failure handling
if (Physics := GetPhysicsComponent[SomeComponent]):
    UpdatePhysics(Physics)
```

**Infallible casts** use parenthesis syntax `Type(Value)` and only
work when the compiler can verify the cast is safe—that is, when the
value type is a subtype of the target type:


<!-- 117 -->
```verse
base := class:
    ID:int

derived := class(base):
    Name:string

GetDerived():derived = derived{ID := 1, Name := "Test"}
```

Use case:

<!--versetest
base := class:
    ID:int

derived := class(base):
    Name:string

GetDerived():derived = derived{ID := 1, Name := "Test"}
-->
<!-- 1171 -->
```verse
# Infallible upcast - derived is a subtype of base
BaseRef:base = base(GetDerived())  # Always safe
```

Attempting an infallible downcast (from supertype to subtype) is a
compile error, as the compiler cannot guarantee safety:

<!--NoCompile-->
<!-- 118 -->
```verse
DerivedRef := derived(BaseRef)  # ERROR: not a subtype relationship
```

#### Castable and Inheritance

The `<castable>` property is inherited by all subclasses. When you
mark a class as `<castable>`, every class that inherits from it
automatically becomes castable as well:

<!-- 119 -->
```verse
base := class<castable>:
    Value:int

child := class(base):
    # Automatically castable - inherits from castable base
    Name:string

grandchild := class(child):
    # Also automatically castable
    Extra:string

# Can cast through the hierarchy
ProcessBase(Instance:base):void =
    if (AsChild := child[Instance]):
        Print("It's a child: {AsChild.Name}")
    if (AsGrandchild := grandchild[Instance]):
        Print("It's a grandchild: {AsGrandchild.Extra}")
```

**Important constraint:** Parametric types cannot be
`<castable>`. This prevents type erasure issues at runtime:

<!-- 120 -->
```verse
# Valid: non-parametric castable class
valid_castable := class<castable>:
    Data:int

# Invalid: parametric classes cannot be castable
# invalid_castable(t:type) := class<castable>:  # ERROR
#     Data:t
```

However, a non-parametric class can be `<castable>` even if it
inherits from or contains parametric types:

<!-- 121 -->
```verse
container(t:type) := class:
    Value:t

# Valid: concrete instantiation of parametric type
int_container := class<castable>(container(int)):
    Extra:string
```

#### Using castable_subtype

The `castable_subtype` type constructor works with `<castable>`
classes to enable type-safe filtered queries and dynamic type
dispatch:

<!--NoCompile-->
<!-- 122 -->
```verse
  component<public> := class<abstract><unique><castable>:
      Parent<public>:entity

  entity<public> := class<concrete><unique><transacts><castable>:
      FindDescendantEntities(entity_type:castable_subtype(entity)):generator(entity_type)
```

When you call `FindDescendantEntities(player)`, the function returns
only entities that are actually player instances or subclasses
thereof, verified at runtime through the castable mechanism. The type
parameter ensures type safety—the returned values have the specific
subtype you requested.

#### Permanence of Castable

Once a class is published with `<castable>`, this decision becomes
permanent. You cannot add or remove the `<castable>` specifier after
publication because doing so would break existing code that relies on
runtime type checking. Code that performs casts would suddenly fail or
behave incorrectly if the castable property changed.

This permanence is enforced through the versioning system—attempting
to change the `<castable>` status of a published class will result in
a compatibility error.

### Final

The `<final>` specifier prevents inheritance, creating a terminal
point in a class hierarchy. When you mark a class with `<final>`, no
other class can inherit from it. For methods, `<final>` prevents
overriding in subclasses, locking the implementation at that level of
the hierarchy.

Classes marked with `<final>` serve as concrete implementations that
cannot be extended. This is particularly important for persistable
classes, which require `<final>` to ensure their structure remains
stable for serialization:

<!--verse
player_stats:=struct<persistable>{}
-->
<!-- 123 -->
```verse
  player_profile := class<final><persistable>:
      Username:string = "Player"
      Level:int = 1
      Gold:int = 0

  player_data := class<final><persistable>:
      Version:int = 1
      LastLogin:string = ""
      Statistics:player_stats = player_stats{}
```

The `<final>` requirement for persistable classes prevents schema
evolution problems. If subclasses could extend persistable classes,
the serialization system would face ambiguity about which fields to
persist and how to handle polymorphic deserialization.

For methods, `<final>` locks behavior at a specific point in the
inheritance chain:

<!-- 124 -->
```verse
  base_entity := class:
      GetName():string = "Entity"

  game_object := class(base_entity):
      GetName<override><final>():string = "GameObject"
      # Any subclass of game_object cannot override GetName
```

The related `<final_super>` specifier marks classes as terminal base
classes — they can be inherited from but their subclasses cannot be
further extended.  `<final_super_base>` marks a class as the ultimate
root of a restricted inheritance tree. Classes with this specifier can
be inherited from, but their subclasses automatically become final —
they cannot be further extended. This creates a two-level inheritance
limit starting from the base:

<!-- TODO  DOES NOT WORK -->

<!--versetest
entity:=class{}
component := class<abstract><unique><castable><final_super_base>:
      Parent: entity
	  
physics_component := class<final_super>(component): 
      Mass:float = 1.0
<# 
-->
<!-- 125 -->
```verse
component := class<abstract><unique><castable><final_super_base>:
      Parent:entity

  # Can inherit from component (first level)

physics_component := class<final_super>(component):
      Mass:float = 1.0

 # Cannot inherit from physics_component - it's implicitly final

 gravity_component := class(physics_component): # COMPILE ERROR
```
<!-- #> -->

So, `<final_super>` marks a class that inherits from a
`<final_super_base>` class, explicitly declaring it as the final
inheritance point. While classes inheriting from `<final_super_base>`
are implicitly final, using `<final_super>` makes this finality
explicit and self-documenting.

<!--versetest
copter_camera_component_director_version := class{}
component:=class<final_super_base>{}
# Explicitly marking as final_super (though implicitly final anyway)
name_component := class<final_super>(component):
      Name:string = ""

copter_camera_component := class<final_super>(copter_camera_component_director_version):
      # Terminal implementation
<#
-->
<!-- 126 -->
```verse
# Explicitly marking as final_super (though implicitly final anyway)
name_component := class<final_super>(component):
      Name:string = ""

copter_camera_component := class<final_super>(copter_camera_component_director_version):
      # Terminal implementation
```
<!-- #> -->

This pattern is particularly valuable in component architectures where
you want a base component interface that various concrete components
implement, but don't want those implementations to spawn their own
inheritance subtrees. The base class defines the contract, immediate
subclasses provide implementations, and inheritance stops there —
clean, controlled, and predictable.

This design enforces architectural discipline, preventing the
"inheritance explosion" that can occur when every class becomes a
potential base for further specialization. By limiting inheritance
depth, these specifiers promote composition over deep inheritance,
leading to more maintainable and understandable code structures.

### Persistable

The `<persistable>` specifier marks types that can be saved and
restored across game sessions, enabling permanent storage of player
progress, achievements, and game state. This specifier transforms
ephemeral gameplay into lasting progression, creating the foundation
for meaningful player investment.

Persistence works through module-scoped `weak_map(player, t)`
variables, where `t` is any persistable type.  These special maps
automatically synchronize with backend storage — when players join,
their data loads; when they leave or data changes, it saves. The
system handles all serialization, network transfer, and storage
management transparently.

<!--verse
player:=string
-->
<!-- 127 -->
```verse
  player_inventory := class<final><persistable>:
      Gold:int = 0
      Items:[]string = array{}
      UnlockedAreas:[]string = array{}

  # This variable automatically persists across sessions

  SavedInventories : weak_map(player, player_inventory) = map{}
```

The `<persistable>` specifier enforces strict structural requirements
to guarantee data integrity across versions. Classes must be `<final>`
because inheritance would complicate serialization schemas. They
cannot contain `var` fields, preserving immutability guarantees even
in persistent storage. They cannot be `<unique>` since identity-based
equality doesn't survive serialization. These constraints ensure that
what you save today can be reliably loaded tomorrow, next month, or
next year.

## Interfaces

Interfaces define contracts that classes can implement, specifying
both the data and behavior that implementing classes must
provide. Unlike many traditional languages where interfaces only
declare method signatures, Verse interfaces are rich contracts that
can include fields, default method implementations, and even custom
accessor logic.

An interface can declare method signatures, provide default
implementations, and define data members:

<!-- 128 -->
```verse
damageable := interface:
    # Abstract method - implementing classes must provide
    TakeDamage(Amount:int)<transacts>:void

    # Method with default implementation
    GetHealth()<computes>:int = 100

    # Data member - implementing classes inherit or must provide
    MaxHealth:int = 100

    IsAlive()<computes>:logic = logic{GetHealth() > 0}

healable := interface:
    Heal(Amount:int):void
    GetMaxHealth():int
```

Interfaces establish contracts that can be purely abstract (method
signatures only), partially concrete (some default implementations),
or fully implemented (complete behavior that classes inherit). Any
class implementing an interface must provide implementations for
abstract methods, but inherits concrete implementations and default
field values.

### Implementing Interfaces

Classes implement interfaces by inheriting from them and providing
concrete implementations where required:

<!--versetest
healable:=interface:
    TakeDamage(Amount:int)<transacts>:void ={}
    GetHealth():int = 0
    Heal(Amount:int)<transacts>:void ={}

damageable:=interface{}

character := class(damageable, healable):
    var Health : int = 100
    MaxHealth : int = 100

    TakeDamage<override>(Amount:int)<transacts>:void =
        set Health = Max(0, Health - Amount)

    GetHealth<override>():int = Health

    Heal<override>(Amount:int)<transacts>:void =
        set Health = Min(MaxHealth, Health + Amount)

<#
-->
<!-- 129 -->
```verse
character := class(damageable, healable):
    var Health : int = 100
    MaxHealth : int = 100

    TakeDamage<override>(Amount:int)<transacts>:void =
        set Health = Max(0, Health - Amount)

    GetHealth<override>()<reads>:int = Health

    Heal<override>(Amount:int)<transacts>:void =
        set Health = Min(MaxHealth, Health + Amount)
```
<!-- #> -->

A class can implement multiple interfaces, effectively achieving
multiple inheritance of both behavior contracts and data
specifications. This provides more flexibility than single class
inheritance while maintaining type safety.

### Interface Fields

Interfaces can declare data members that implementing classes must
provide or inherit. These fields can be either immutable or mutable,
and may include default values:

<!-- 130 -->
```verse
# Interface with various field types
entity_properties := interface:
    # Immutable field with default - classes inherit this value
    EntityID:int = 0

    # Mutable field with default
    var Health:float = 100.0

    # Field without default - classes must provide a value
    Name:string

    # Field that can be overridden
    MaxHealth:float = 100.0

player_entity := class(entity_properties):
    # Must provide Name (no default in interface)
    Name<override>:string = "Player"

    # Can override to change default
    MaxHealth<override>:float = 150.0

    # Inherits EntityID and Health with their defaults
```

When an interface field has a default value, implementing classes
automatically inherit that default unless they override it. Fields
without defaults must be provided either by the implementing class or
through construction parameters.

### Default Implementations

Interfaces can provide complete method implementations that
implementing classes inherit automatically:

<!-- 131 -->
```verse
animated := interface:
    var CurrentFrame:int = 0
    TotalFrames:int = 10

    # Concrete implementation provided by interface
    NextFrame()<transacts><decides>:void =
        set CurrentFrame = Mod[(CurrentFrame + 1),TotalFrames] or 0

    # Can access interface fields
    ProgressPercent()<reads><decides>:rational =
        CurrentFrame / TotalFrames

sprite := class(animated):
    TotalFrames<override>:int = 20
    # Automatically inherits NextFrame and ProgressPercent implementations
```

Classes inherit these implementations without modification, allowing
interfaces to provide reusable behavior. Implementing classes can
override these methods if they need specialized behavior, but the
interface provides a working default.

### Overriding Members

Classes can override both fields and methods from interfaces to
provide specialized implementations:

<!-- 132 -->
```verse
base_stats := interface:
    BaseHealth:int = 100

    CalculateFinalHealth():int = BaseHealth

warrior := class(base_stats):
    # Override field with different default
    BaseHealth<override>:int = 150

    # Override method for specialized calculation
    CalculateFinalHealth<override>():int =
        BaseHealth * 2  # Warriors get double health

mage := class(base_stats):
    BaseHealth<override>:int = 75

    CalculateFinalHealth<override>():int =
        BaseHealth + MagicBonus

    MagicBonus:int = 25
```

Field overrides can provide different default values or specialize to
subtypes. Method overrides replace the interface's implementation
entirely. All overrides must maintain type compatibility—fields can
only be overridden with subtypes, and method signatures must match
exactly.

### Multiple Interfaces with Sharing

When a class implements multiple interfaces that declare fields or
methods with the same name, you must use qualified names to
disambiguate:

<!-- 133 -->
```verse
magical := interface:
    Power:int = 50
    GetPowerLevel()<computes>:int = Power

physical := interface:
    Power:int = 75
    GetPowerLevel()<computes>:int = Power * 2

hybrid := class(magical, physical):
    UseHybridPowers():void =
       MagicPower := (magical:)Power         # Access magical's Power
       PhysicalPower := (physical:)Power     # Access physical's Power
       MagicLevel := (magical:)GetPowerLevel()
       PhysicalLevel := (physical:)GetPowerLevel()
```

The qualified name syntax `(InterfaceName:)MemberName` specifies which
interface's member you're accessing. Each interface maintains its own
instance of the field, allowing the class to support both contracts
simultaneously without conflict.

### Interface Hierarchies

Interfaces can extend other interfaces, creating hierarchies of
contracts that combine data and behavior requirements:

<!--NoCompile-->
<!-- 134 -->
```verse
combatant := interface(damageable, healable):
    var AttackPower:int = 10

    Attack(Target:damageable):void =
        Target.TakeDamage(AttackPower)

    GetAttackPower():int = AttackPower

boss := interface(combatant):
    Phase:int = 1

    UseSpecialAbility():void
    GetPhase():int = Phase
```

A class implementing `boss` inherits all fields and methods from the
entire hierarchy—`boss`, `combatant`, `damageable`, and
`healable`. Diamond inheritance (where an interface is inherited
through multiple paths) is fully supported, with fields properly
merged so each field exists only once in the implementing class.

**Important:** A class cannot directly inherit the same interface
multiple times (e.g., `class(interface1, interface1)` is an error),
but can inherit it indirectly through diamond inheritance. This means
`class(interface2, interface3)` is valid even if both `interface2` and
`interface3` inherit from the same base interface.

### Fields with Accessors

Interfaces can define fields with custom getter and setter logic,
encapsulating complex behavior behind simple field access syntax:

<!--versetest
subscribable_property := interface:
    # External field with accessor methods
    var Value<getter(GetValue)><setter(SetValue)>:int = external{}

    # Internal storage
    var Storage:int = 100

    # Getter adds computation
    GetValue(:accessor):int = Storage + 10

    # Setter adds validation
    SetValue(:accessor, NewValue:int):void =
        if (NewValue >= 0):
            set Storage = NewValue

tracked_value := class(subscribable_property):

UseTrackedValue():void =
    Object := tracked_value{}

    # Uses getter - returns 110 (Storage + 10)
    Current := Object.Value

    # Uses setter - validates and updates Storage
    set Object.Value = 150
<#
-->
<!-- 135 -->
```verse
subscribable_property := interface:
    # External field with accessor methods
    var Value<getter(GetValue)><setter(SetValue)>:int = external{}

    # Internal storage
    var Storage:int = 100

    # Getter adds computation
    GetValue(:accessor):int = Storage + 10

    # Setter adds validation
    SetValue(:accessor, NewValue:int):void =
        if (NewValue >= 0):
            set Storage = NewValue

tracked_value := class(subscribable_property):

UseTrackedValue():void =
    Object := tracked_value{}

    # Uses getter - returns 110 (Storage + 10)
    Current := Object.Value

    # Uses setter - validates and updates Storage
    set Object.Value = 150
```
<!-- #> -->

The `external{}` keyword indicates the field has no direct storage—all
access goes through the accessor methods. This pattern is powerful for
implementing property change notifications, validation, computed
properties, and other scenarios requiring logic around field access.

**Important:** Fields with accessors defined in interfaces cannot be
overridden in implementing classes. The accessor implementation is
fixed by the interface.
