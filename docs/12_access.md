# Access Specifiers

Access specifiers control visibility and accessibility of code
elements. They provide a nuanced spectrum of access levels that
reflect the complex reality of modern software development,
particularly in the context of a persistent, global metaverse where
code from many authors must coexist safely.

Five primary visibility levels are defined that form a carefully
designed hierarchy, each serving specific architectural
needs. Understanding when and why to use each level is crucial for
creating well-structured, maintainable code.

| Specifier | Visibility | Usage |
|-----------|------------|-------|
| `<public>` | Universally accessible | Members intended for external use |
| `<internal>` | Only within the module (default) | Module-private implementation |
| `<private>` | Only in immediate enclosing scope | Local to class/struct |
| `<protected>` | Current class and subtypes | Inheritance hierarchies |
| `<scoped>` | Current scope and enclosing scopes | Special use cases |
| `<epic_internal>` | Scopes with the /Verse.org, /UnrealEngine.com, and /Fortnite.com domains | `<epic_internal>` is only usable by Epic-authored code |

## Public

The `<public>` specifier represents the broadest level of access,
making an identifier universally accessible from any code that can
reference the containing module or type. When you mark something as
public, you're making a strong commitment about its availability and
stability:

<!-- 01 -->
```verse
player_manager<public> := module:
    MaxPlayers<public>:int = 100
   
    player<public> := class:
        Name<public>:string
        Level<public>:int = 1
```

Public members form the contract between your code and the outside
world. In the metaverse context, public declarations are particularly
significant because they represent guarantees that extend potentially
forever—once published, removing or incompatibly changing a public
member breaks the promise you've made to other developers who depend
on your code.

The public specifier can be applied to modules, classes, interfaces,
structs, enums, methods, and data members. When applied to a type
definition itself, it makes the type available for use outside its
defining module. When applied to members within a type, it makes those
members accessible to any code that has access to an instance of that
type.

## Protected

The `<protected>` specifier creates a middle ground between public and
private, allowing access within the defining class and any classes
that inherit from it. This level exists specifically to support
inheritance hierarchies while maintaining encapsulation:

<!--verse
vector3:=class{}
MaxHealth:int=1
-->
```verse
game_entity := class:
    var Position<protected>:vector3 = vector3{x:=0.0, y:=0.0, z:=0.0}
    var Health<protected>:int = 100

    UpdatePosition<protected>(NewPos:vector3):void =
        set Position = NewPos
        OnPositionChanged()

    OnPositionChanged<protected>():void = {}  # Overridable by subclasses

player := class(game_entity):
    MoveToSpawn():void =
        UpdatePosition(GetSpawnLocation())  # Can access protected member
        set Health = MaxHealth              # Can modify protected variable
```

Protected access enables the template method pattern and other
inheritance-based designs while preventing external code from
accessing implementation details that should remain within the class
hierarchy. This is particularly valuable for game entities and other
hierarchical structures where parent classes need to share behavior
with children without exposing that behavior to the world.

## Private

The `<private>` specifier provides the strictest access control,
limiting visibility to the immediately enclosing scope. Private
members are truly internal implementation details that can be changed
freely without affecting any external code:

<!--verse
item:=struct{Weight:float=0.0}
-->
<!-- 03 -->
```verse
inventory := class:
    var Items<private>:[]item = array{}
    var Capacity<private>:int = 20
    var CurrentWeight<private>:float = 0.0
    MaxWeight:float=20.0

    AddItem<public>(NewItem:item, At:int)<transacts><decides>:void =
        ValidateCapacity[NewItem]
        set Items[At] = NewItem
        set CurrentWeight = CurrentWeight + NewItem.Weight

    ValidateCapacity<private>(NewItem:item)<reads><decides>:void =
        Items.Length < Capacity
        CurrentWeight + NewItem.Weight <= MaxWeight
```

Private members are the building blocks of encapsulation. They allow
you to maintain invariants, hide complexity, and create clean
abstractions. Changes to private members never break external code,
giving you the freedom to refactor and optimize implementation details
as needed.

## Internal

The `<internal>` specifier, which is the default access level when no
specifier is provided, makes members accessible within the defining
module but not outside it. This creates a natural boundary for
collaborative code that needs to share implementation details without
exposing them publicly:

<!--verse
game_entity:=class{}
collision_info:=class{}
ApplyGravity(:game_entity,:float):void={}
CheckCollisions(:game_entity):void={}

-->
<!-- 04 -->
```verse
physics := module:
    # Internal types and constants
    gravity_constant:float = 9.81

    collision_detector := class<abstract>:
        DetectCollision<internal>(A:game_entity, B:game_entity):?collision_info 

    physics_world := class:
        var Entities<internal>:[]game_entity = array{}

        SimulateStep<internal>(DeltaTime:float):void =
            for (Entity : Entities):
                ApplyGravity(Entity, DeltaTime)
                CheckCollisions(Entity)
```

Internal access is ideal for module-wide utilities, shared
implementation details, and helper functions that multiple classes
within a module need but shouldn't be exposed to external code. It
provides a clean separation between the module's public interface and
its implementation machinery.

## Scoped

The `<scoped>` specifier creates custom access boundaries between
modules or code locations. Unlike the fixed visibility levels of
`public`, `internal`, and `private`, `scoped` access allows you to
explicitly grant access to particular modules while excluding all
others—creating a kind of "friend" relationship between program
entities.

### Scoped Definitions

A scoped access level is created using the `scoped{...}` expression,
which takes one or more module references:

<!-- NoCompile -->
```verse
collaboration := module:
    # Create a scope that includes both ModuleA and ModuleB
    Shared<public> := scoped{ModuleA, ModuleB}

    # This class is only accessible within ModuleA and ModuleB
    SharedResource<Shared> := class:
        Data<public>:int = 42
```

The scoped definition creates an access level that can then be used as
a specifier on classes, functions, variables, and other
definitions. Code within any of the listed entities can access the
scoped member, while code outside those modules cannot—even if it can
see the containing scope.

### Cross-Module Collaboration

The most powerful use of scoped access is enabling controlled
collaboration between modules. A definition can be created in one
module but scoped to another, making it accessible where it's needed
while keeping it hidden elsewhere:

<!--verse
bounding_box:=class{}
-->
<!-- 06 -->
```verse
graphics := module:
    # Define an interface scoped to the physics module
    CollidableShape<scoped{physics}> := interface:
        GetBounds():bounding_box

physics := module:
    using{graphics}

    # Physics can implement the interface even though it's defined in graphics
    sphere_collider := class<abstract>(CollidableShape):
        GetBounds<override>():bounding_box
```

This pattern allows graphics to define contracts that physics
implements without exposing those implementation details publicly. The
interface exists at the boundary between the two modules but isn't
part of either module's public API.

You can scope a definition to multiple modules, creating a shared
private space for collaboration:

<!-- 07 -->
```verse
gameplay := module:
    # This scope includes both the inventory and crafting modules
    SharedGameplayScope := scoped{inventory, crafting}

    # Items can be accessed by both inventory and crafting
    Item<SharedGameplayScope> := class:
        ID<public>:int
        Properties<public>:[string]string

    # Factory function available to both systems
    CreateItem<SharedGameplayScope>(TheID:int):Item = Item{ID:=TheID, Properties:=map{}}

inventory := module:
    using{gameplay}

    AddToInventory(ItemID:int):void =
        NewItem := CreateItem(ItemID)  # Can access scoped function
        # Implementation...

crafting := module:
    using{gameplay}

    CraftItem(Recipe:[]int)<decides>:Item =
        # Can create items and access their properties
        CreateItem(Recipe[0])
```

### Scoped Read or Write Access

Like other access specifiers, scoped can be applied separately to read
and write operations on variables:

<!--  BUG?  Or at least unhelpful error message

a:=class<computes>{}
F()<computes>:a= a{}
b := class{ G:a = F() }

Gives:
  Line 8: Verse compiler error V3582: Divergent calls (calls that might not complete) cannot be used to define data-members.
-->


<!--verse
ModuleA:=module{}
ModuleB:=module{}
game_state:=class{}

-->
<!-- 08 -->
```verse
SharedScope := scoped{ModuleA, ModuleB}

state_manager := class:
    # Public read access, but only ModuleA and ModuleB can write
    var<SharedScope> GameState<public>:game_state = game_state{}

    # Only ModuleA and ModuleB can read or write this internal state
    var<SharedScope> SyncCounter<SharedScope>:int = 0
```

This pattern is particularly useful for shared state that multiple
modules need to coordinate on without exposing write access publicly.

### Visibility and Access Paths

An important subtlety of scoped access is that it grants access to a
specific member, but doesn't make intermediate types or modules
visible. To access a scoped member, you must be able to see the entire
path to it:

<!-- NoCompile -->
```verse
outer := module:
    # Internal to outer
    inner := module:
        # Scoped to target_module
        SharedClass<scoped{target_module}> := class:
            Value:int = 42

target_module := module:
    using{outer}

    # ERROR: Can't see outer.inner because inner is internal to outer
    # even though SharedClass is scoped to us
    UseShared():void = outer.inner.SharedClass{}
```

For scoped access to work, either the containing scope must be
accessible (public or also scoped appropriately), or the scoped member
must be accessed through a public interface that exposes it.

A definition can only have one scoped access level—you cannot apply
multiple scoped specifiers:

<!-- NoCompile-->
```verse
# ERROR: Cannot have multiple access level specifiers
InvalidScope<scoped{ModuleA}><scoped{ModuleB}> := class{}
```

### Scoped Access and Inheritance

When a class member has scoped access, overriding members in
subclasses can maintain or narrow that access, following normal
inheritance rules:

<!--verse
ModuleA:=module{}
ModuleB:=module{}
-->
<!-- 11 -->
```verse
SharedScope := scoped{ModuleA, ModuleB}

base := class:
    # Accessible only in ModuleA and ModuleB
    ComputeValue<SharedScope>():int = 42

derived := class(base):
    # Can override with same or more restrictive access
    ComputeValue<override>():int = 100  # Now internal to this module
```

### Using Scoped for API Boundaries

Scoped access excels at creating controlled API boundaries where
certain functionality should be shared between specific modules but
not exposed as part of the public interface:

<!-- NoCompile -->
```verse
networking := module:
    # Public scope for modules that need network access
    NetworkScope<public> := scoped{player_system, matchmaking, telemetry}

    # Core networking available to specific systems
    SendPacket<NetworkScope>(Data:[]uint8):void =
        # Implementation...

    # Internal statistics
    var<NetworkScope> BytesSent<NetworkScope>:int = 0
```

This creates an explicit architectural boundary—only the modules
listed in the scope can access the networking primitives, while other
code must use higher-level public APIs.

### Design Considerations

Scoped access represents an architectural commitment between
modules. When using it effectively:

- Use scoped for legitimate cross-module collaboration that doesn't
  belong in the public API
- Keep scope definitions at the module level where they can be documented and maintained
- Prefer scoping to explicit modules rather than deeply nested scopes
- Consider whether protected or internal access might be simpler for your use case
- Document why particular modules are included in a scope

The scoped specifier fills a unique niche between internal and public
access, enabling sophisticated module architectures where multiple
components need to collaborate intimately without exposing those
implementation details to the wider codebase.

## Separating Read and Write Access

An innovative feature is the ability to apply different access
specifiers to reading and writing operations on the same
variable. This fine-grained control allows you to create variables
that are widely readable but narrowly writable, implementing common
patterns like read-only properties elegantly:

<!-- 13 -->
```verse
game_state := class:
    # Public read, protected write
    var<protected> Score<public>:int = 0

    # Public read, private write
    var<private> PlayerCount<public>:int = 0

    # Internal read, private write
    var<private> SessionID<internal>:string
```

This dual-specifier system solves a common problem in object-oriented
programming where you want to expose state for reading without
allowing external modification. Rather than requiring getter methods
or property syntax, Verse makes this pattern a first-class language
feature.

The syntax places the write-access specifier on the `var` keyword and
the read-access specifier on the identifier itself. This visual
separation makes the access levels immediately clear when reading
code. The write specifier must be at least as restrictive as the read
specifier — you cannot write to a variable that's privately readable
but publicly writable, as this would violate basic encapsulation
principles.

## Best Practices

Understanding when to use each access level requires thinking about
your code's architecture and evolution. The principle of least
privilege suggests starting with the most restrictive access that
works and only broadening it when necessary.

For public  APIs, every public  member is a commitment.  Before making
something public, consider  whether it truly needs to be  part of your
module's contract or if it's  an implementation detail that happens to
be  needed elsewhere  temporarily.  Public members  should be  stable,
well-documented, and designed for longevity.

Protected access should be used thoughtfully in inheritance
hierarchies. Not everything in a base class needs to be protected—only
those members that form the inheritance contract between parent and
child classes. Overuse of protected access can create tight coupling
between classes in a hierarchy.

Private access is your default for implementation details. Most helper
functions, intermediate calculations, and state management should be
private. This gives you maximum flexibility to refactor and optimize
without breaking dependent code.

The dual-specifier pattern for variables is particularly powerful for
maintaining invariants. By making variables publicly readable but
privately or protectively writable, you can expose state for
observation while maintaining complete control over modifications:

<!-- 14 -->
```verse
resource_manager := class:
    var<private> TotalResources<public>:int = 1000
    var<private> AllocatedResources<public>:int = 0
    var<private> AvailableResources<public>:int = 1000

    AllocateResources<public>(Amount:int)<decides><transacts>:void =
        Amount <= AvailableResources
        set AllocatedResources = AllocatedResources + Amount
        set AvailableResources = AvailableResources - Amount
```

## Annotations and Metadata

Verse provides an annotation system for attaching metadata to
definitions using the `@` prefix syntax. Annotations provide compiler
directives and metadata that affect how code is treated during
compilation and evolution.

### Built-in Annotations

#### @deprecated

!!! warning "Internal Feature"
    @deprecated attribute is currently an internal feature and cannot be used by end-users.

The `@deprecated` annotation marks definitions that should no longer
be used. When code references a deprecated definition, the compiler
produces a warning, alerting developers to update their code:

<!--versetest
@deprecated
OldFunction():void =
    Print("This function is deprecated")

@deprecated
legacy_player := class:
    Name:string

UseDeprecated():void =
    OldFunction()  # Warning: OldFunction is deprecated
<#
-->
<!-- 15 -->
```verse
# Mark a definition as deprecated
@deprecated
OldFunction():void =
    Print("This function is deprecated")

# Mark a class as deprecated
@deprecated
legacy_player := class:
    Name:string

# Attempting to use deprecated code produces a warning
UseDeprecated():void =
    OldFunction()  # Warning: OldFunction is deprecated
```
<!-- #> -->

Deprecated definitions can use other deprecated definitions without
warnings, but non-deprecated code cannot use deprecated definitions
without triggering warnings. This allows gradual migration of
deprecated APIs:

<!--versetest
@deprecated
OldAPI():int = 42
@deprecated
MigrateOldAPI():int = OldAPI()

# Warning: non-deprecated calling deprecated
# NewCode():int = OldAPI()

<#
-->
<!-- 16 -->
```verse
@deprecated
OldAPI():int = 42

# Valid: deprecated can call deprecated
@deprecated
MigrateOldAPI():int = OldAPI()

# Warning: non-deprecated calling deprecated
# NewCode():int = OldAPI()
```
<!-- #> -->

The `@deprecated` annotation can be applied to:
- Functions and methods
- Classes, interfaces, structs, and enums
- Individual enum values
- Data members
- Modules

#### @experimental

!!! warning "Internal Feature"
    @deprecated attribute is currently an internal feature and cannot be used by end-users.

The `@experimental` annotation marks features that are not yet stable
and may change or be removed in future versions. Experimental features
can only be used when the `AllowExperimental` package flag is enabled:

<!-- NoCompile -->
```verse
# Mark a feature as experimental
@experimental
experimental_class := class:
    NewFeature:int

# Using experimental features requires AllowExperimental flag
# Without flag: error
# With AllowExperimental:=true: allowed
UseExperimental(Obj:experimental_class):void =
    Print("Using experimental feature")
```

Experimental definitions behave similarly to deprecated
ones—experimental definitions can freely use other experimental
definitions, but stable code cannot use experimental definitions
unless the `AllowExperimental` flag is set.

The `@experimental` annotation cannot be applied to:
- Local variables
- Override methods (base method's experimental status is inherited)

#### @available

The `@available` annotation controls when a definition becomes
available based on version numbers. This enables gradual API rollout
and version-specific functionality:

<!--versetest
using { /Verse.org/Native }  # Required for @available
@available{MinUploadedAtFNVersion := 3000}
NewFeature():void =
    Print("New feature")
@available{MinUploadedAtFNVersion := 2900}
OldImplementation():int = 42

@available{MinUploadedAtFNVersion := 3000}
NewImplementation():int = 100

<#
-->
<!-- 18 -->
```verse
using { /Verse.org/Native }  # Required for @available

# Available only in version 3000 and later
@available{MinUploadedAtFNVersion := 3000}
NewFeature():void =
    Print("New feature")

# Multiple definitions can coexist for different versions
@available{MinUploadedAtFNVersion := 2900}
OldImplementation():int = 42

@available{MinUploadedAtFNVersion := 3000}
NewImplementation():int = 100
```
<!-- #> -->

The `@available` annotation can be applied to the same kinds of
definitions as `@deprecated`.

### Custom Attributes

!!! warning "Internal Feature"
    Custom attributes are currently an internal feature and cannot be created by end-users.

You can create custom attributes by inheriting from the special
`attribute` class. Custom attributes allow you to attach
domain-specific metadata to your code:

<!--versetest
@attribscope_class
gameplay_element := class<computes>(attribute):
    Category:string
    Priority:int
@gameplay_element{Category := "Combat", Priority := 1}
weapon_system := class:
    Damage:int
<#
-->
<!-- 19 -->
```verse
# Define a custom attribute
@attribscope_class
gameplay_element := class<computes>(attribute):
    Category:string
    Priority:int

# Use the custom attribute
@gameplay_element{Category := "Combat", Priority := 1}
weapon_system := class:
    Damage:int
```
<!-- #> -->

#### Attribute Scopes

When defining custom attributes, you must specify where they can be
applied using scope annotations:

- **@attribscope_class** - Can be applied to regular classes
- **@attribscope_attribclass** - Can be applied to attribute classes (classes that inherit from `attribute`)
- **@attribscope_enum** - Can be applied to enums
- **@attribscope_interface** - Can be applied to interfaces
- **@attribscope_function** - Can be applied to functions and methods
- **@attribscope_data** - Can be applied to data members

Example of scoped custom attributes:

<!--versetest
# Attribute that can only be applied to functions
@attribscope_function
performance_critical := class<computes>(attribute):
    MaxExecutionTimeMs:int

# Attribute that can only be applied to data members
@attribscope_data
serializable_field := class<computes>(attribute):
    SerializationKey:string

# Use them appropriately
entity := class<abstract>:
    @serializable_field{SerializationKey := "entity_id"}
    ID:int

    @performance_critical{MaxExecutionTimeMs := 16}
    Update():void

<#
-->
<!-- 20 -->
```verse
# Attribute that can only be applied to functions
@attribscope_function
performance_critical := class(attribute):
    MaxExecutionTimeMs:int

# Attribute that can only be applied to data members
@attribscope_data
serializable_field := class(attribute):
    SerializationKey:string

# Use them appropriately
entity := class<abstract>:
    @serializable_field{SerializationKey := "entity_id"}
    ID:int

    @performance_critical{MaxExecutionTimeMs := 16}
    Update():void
```
<!-- #> -->

Attempting to use an attribute in the wrong location produces a
compiler error. For example, a function-scoped attribute cannot be
applied to a class.

### Getter and Setter Accessors

!!! warning "Internal Feature"
    Getter and setter accessors are currently an internal feature and cannot be used by end-users.

While not strictly annotations, the `<getter(...)>` and
`<setter(...)>` specifiers provide a related form of metadata for
controlling field access. These can be applied to both class and
interface fields to define custom access logic:

<!--versetest
entity := class:
    # External field with custom accessors
    var Health<getter(GetHealth)><setter(SetHealth)>:int = external{}

    var InternalHealth:int = 100

    GetHealth(:accessor):int = InternalHealth

    SetHealth(:accessor, NewValue:int):void =
        if (NewValue >= 0, NewValue <= 100):
            set InternalHealth = NewValue

<#
-->
<!-- 21 -->
```verse
entity := class:
    # External field with custom accessors
    var Health<getter(GetHealth)><setter(SetHealth)>:int = external{}

    var InternalHealth:int = 100

    GetHealth(:accessor):int = InternalHealth

    SetHealth(:accessor, NewValue:int):void =
        if (NewValue >= 0, NewValue <= 100):
            set InternalHealth = NewValue
```
<!-- #> -->

Constraints on accessors:

- Must include both `<getter(...)>` and `<setter(...)>` - cannot have only one
- The field must have `= external{}` or no default value (with archetype initialization required)
- Fields with accessors cannot be overridden in subclasses
- The field must be mutable (marked with `var`)
- Not all types are supported for accessor fields
- Accessor fields are currently only allowed in epic_internal scopes

For more details on accessor patterns, see [Fields with Accessors](10_classes_interfaces.md).

### Localization

The `<localizes>` specifier marks definitions as localizable messages
for internationalization. Localized messages use the `message` type
and can be extracted for translation into different languages:

<!-- 22 -->
```verse
# Simple localized message
WelcomeMessage<localizes> : message = "Welcome to the game!"

# Call Localize to get the string
ShowWelcome():void =
    Print(Localize(WelcomeMessage))
```

#### Message Parameters

Localized messages can accept parameters for dynamic content interpolation:

<!-- 23 -->
```verse
# Message with parameter interpolation
GreetPlayer<localizes>(PlayerName:string) : message = "Hello, {PlayerName}!"

# Use with arguments
ShowGreeting(Name:string):void =
    Print(Localize(GreetPlayer(Name)))
    # Outputs: "Hello, Aldric!" (if Name = "Aldric")
```

**Supported parameter types:**
- `string` - Text values
- `int` - Integer values (formatted with comma separators)
- `float` - Floating-point values

**Parameter interpolation syntax:**
- Use `{ParameterName}` to insert parameter values
- Parameters can be used multiple times or not at all
- Only parameter names and Unicode code points allowed in braces

<!-- 24 -->
```verse
# Multiple parameters, some repeated
ScoreMessage<localizes>(Player:string, Score:int) : message =
    "Congratulations {Player}! Your score is {Score}. Great job, {Player}!"

# Outputs: "Congratulations Alice! Your score is 1,500. Great job, Alice!"

# Not all parameters required in message text
OptionalParam<localizes>(Name:string, Score:int) : message =
    "Thanks for playing!"  # Score parameter ignored
```

#### Integer Formatting

Integer parameters are automatically formatted with comma separators for readability:

<!-- 25 -->
```verse
HighScore<localizes>(Points:int) : message = "New record: {Points} points!"

# Localize(HighScore(190091)) produces: "New record: 190,091 points!"
```

#### Named and Default Parameters

Localized messages support named parameters and default values:

<!--versetest
ConfigMessage<localizes>(?MaxPlayers:int = 8, ?TimeLimit:int = 300):message =
    "Game settings: {MaxPlayers} players, {TimeLimit} seconds"
-->
<!-- 26 -->
```verse
ConfigMessage<localizes>(?MaxPlayers:int = 8, ?TimeLimit:int = 300):message =
    "Game settings: {MaxPlayers} players, {TimeLimit} seconds"

# Can be called with any combination
Localize(ConfigMessage())                           # Uses defaults
Localize(ConfigMessage(?MaxPlayers := 16))          # Override one
Localize(ConfigMessage(?TimeLimit := 600, ?MaxPlayers := 32))  # Override both
```

#### Tuple Parameters

Messages can accept tuple parameters, which are destructured in the parameter list:

<!--versetest
LocationMessage<localizes>(Player:string, (X:int, Y:int)) : message =
    "{Player} is at position ({X}, {Y})"
-->
<!-- 27 -->
```verse
LocationMessage<localizes>(Player:string, (X:int, Y:int)) : message =
    "{Player} is at position ({X}, {Y})"

# Call with tuple
Localize(LocationMessage("Hero", (10, 20)))
# Outputs: "Hero is at position (10, 20)"
```

#### String Escaping and Unicode

**Unicode code points:**

<!-- 28 -->
```verse
UnicodeMessage<localizes> : message = "The letter is {0u004d}"
# Outputs: "The letter is M"
```

**Escaped braces** (to show literal braces):

<!-- 29 -->
```verse
EscapedMessage<localizes>(Name:string) : message =
    "Use \{Name\} to insert {Name}"
# Localize(EscapedMessage("value")) produces: "Use {Name} to insert value"
```

**Special characters:**

<!-- 30 -->
```verse
SpecialChars<localizes> : message =
    "Supports: \\r\\n\\t\\\"\\'\\#\\<\\>\\&\\~"
```

**Whitespace and comments** are allowed in interpolation:

<!-- 31 -->
```verse
SpacedParam<localizes>(Name:string) : message = "Hello { Name }"
CommentedParam<localizes>(Name:string) : message = "Hello {<# comment #>Name}"
```

#### Scope Requirements

Localized messages **must be defined at module or snippet scope**. They cannot be defined inside functions:

<!-- NoCompile -->
```verse
# Valid: module scope
MyModule := module:
    ModuleMessage<localizes> : message = "Valid"

# Valid: snippet scope
TopLevelMessage<localizes> : message = "Valid"

BadFunction():void =
    LocalMessage<localizes> : message = "Invalid"  # ERROR
```

#### Inheritance and Override

Localized messages can be overridden in class hierarchies:

<!-- 33 -->
```verse
base_ui := class:
    Title<localizes>:message = "Base Title"
    Description<localizes>:message = "Base description"

derived_ui := class(base_ui):
    # Override the title message
    Title<localizes><override>:message = "Derived Title"
    # Inherits Description from base
```

Localized messages can also be abstract:

<!-- 34 -->
```verse
quest_base := class<abstract>:
    # Abstract message - must be implemented by subclasses
    TaskDescription<localizes><public> : message
    # Concrete message with default
    CompletionMessage<localizes><protected> : message = "Quest complete!"

fetch_quest := class<final>(quest_base):
    TaskDescription<localizes><override> : message = "Collect 10 items"
```

#### Restrictions and Errors

**Must use explicit type annotation:**

The type annotation `: message` is required. Implicit typing is not supported:

<!-- 35 -->
```verse
# ERROR: Missing type annotation
# BadMessage<localizes> := "Text"  # ERROR 3639

# Valid: Explicit type
GoodMessage<localizes> : message = "Text"
```

**RHS must be string literal:**

<!-- 36 -->
```verse
# ERROR: Expression not allowed
# InvalidMessage<localizes> : message = "A" + "B"  # ERROR 3638

# Valid: Literal only
ValidMessage<localizes> : message = "AB"
```

**Restricted parameter types:**

Not all types are supported as parameters:

<!-- 37 -->
```verse
# ERROR: Optional types not supported
# OptionalMsg<localizes>(Player:?string) : message = "{Player}"  # ERROR 3509

# ERROR: Custom classes not supported
my_class := class{Value:int}
# ClassMsg<localizes>(Obj:my_class) : message = "Object"  # ERROR 3509
```

**Interpolation syntax restrictions:**

Only parameter names and Unicode code points are allowed inside `{}`:

<!-- 38 -->
```verse
# ERROR: Expressions not allowed
# ExprMessage<localizes>(Name:string) : message = "{"Hello"}"  # ERROR 3652

# Valid: Parameter names only
ParamMessage<localizes>(Name:string) : message = "{Name}"
```

**Non-parameter identifiers are escaped:**

If you reference an identifier that isn't a parameter, it gets escaped in the output:

<!-- 39 -->
```verse
GlobalName:string = "World"

RefMessage<localizes>(Greeting:string) : message =
    "{Greeting} to {GlobalName}"

# Localize(RefMessage("Hello")) produces: "Hello to \{GlobalName\}"
# Note: GlobalName is escaped because it's not a parameter
```

#### Access Specifiers

Localized messages support standard access specifiers:

<!-- 40 -->
```verse
my_module := module:
    PublicMessage<localizes><public> : message = "Public message"
    InternalMessage<localizes> : message = "Internal message"

    some_class := class:
        PrivateMessage<localizes><private> : message = "Private message"  # private not allowed in module scopes
```

#### Best Practices

**Keep messages translatable:**
- Use complete sentences, not fragments that might be concatenated
- Avoid gender or number assumptions that don't translate well
- Provide context through parameter names

**Design for different languages:**
- Don't assume word order - let translators rearrange parameter positions
- Allow repeated parameter use for languages that need it
- Keep formatting codes (like comma separators) automated

**Organization:**
- Group related messages in the same module
- Use descriptive names that indicate message purpose
- Consider using abstract base classes for message families

<!-- 41 -->
```verse
# Good: Clear, complete, flexible
PlayerJoined<localizes>(PlayerName:string, TeamName:string) : message =
    "{PlayerName} joined team {TeamName}"

# Avoid: Fragments that might be concatenated
# PlayerPrefix<localizes>(Name:string) : message = "Player {Name}"
# JoinedSuffix<localizes>(Team:string) : message = "joined {Team}"
```

## Evolution

Access specifiers play a crucial role in code evolution. Changing
access levels after publication can break compatibility:

- Narrowing access (public to private) breaks external code that
  depends on the member
- Widening access (private to public) is generally safe but creates
  new commitments
- Changing protected members affects the inheritance contract

The `<castable>` specifier on classes has special compatibility
requirements—once published, it cannot be added or removed, as this
would affect the safety of dynamic casts throughout the codebase.

When designing for long-term evolution, consider using internal access
for members that might eventually become public. This allows you to
test and refine APIs within your module before committing to public
exposure.
