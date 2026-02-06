# Modules

Modules and paths are fundamental concepts for code organization,
namespace management, and the ability to share and reuse code across
projects. Think of modules as containers that group related
functionality together, similar to packages in other programming
languages, but with stronger guarantees about versioning and
compatibility.

In the context of game development, modules allow you to separate
different aspects of your game logic into manageable, reusable
pieces. For example, you might have one module for player inventory
management, another for combat mechanics, and yet another for UI
interactions. Each module encapsulates its own functionality while
exposing only the necessary interfaces to other parts of your code.

The module system is designed to support the vision of a persistent,
shared Metaverse where code can be published once and used by anyone,
anywhere, with confidence that it will continue to work even as the
original author updates and improves it. This is achieved through
strict backward compatibility rules and a global namespace system that
ensures every piece of published code has a unique, permanent address.

Each module is intrinsically linked to the file system structure of
your project. When you create a folder in your Verse project, that
folder automatically becomes a module. The module's name is simply the
folder's name, making the relationship between your file organization
and your code organization completely transparent.

All `.verse` files within the same folder are considered part of that
module and share the same namespace. This means that if you have three
files - `player.verse`, `inventory.verse`, and `equipment.verse` - all
in a folder called `player_systems`, they all contribute to the
`player_systems` module and can reference each other's definitions
without any import statements. This automatic grouping makes it easy
to split large modules across multiple files for better organization
while maintaining the logical unity of the module.

## Paths

Paths are the addressing system that makes Verse's vision of a shared,
persistent Metaverse possible. Just as every website on the internet
has a unique URL, every module has a unique path that identifies it
globally. This path system is more than just a naming convention -
it's a fundamental part of how Verse manages code distribution,
versioning, and dependencies.

Paths borrow conceptually from web domains with adaptations for the
needs of a programming language. A path starts with a forward slash
`/` and typically includes a domain-like identifier followed by one or
more path segments. This creates a hierarchical namespace that is both
human-readable and globally unique.

The format `/domain/path/to/module` serves several important purposes:

- **Persistent and unique identification**: Once a module is published
  at a particular path, that path belongs to it forever. No other
  module can ever claim the same path, ensuring that dependencies
  always resolve to the correct code.

- **Ownership and authority**: The domain portion of the path (like
  `Fortnite.com` or `Verse.org`) indicates who owns and maintains the
  module. This helps developers understand the source and
  trustworthiness of the code they're using.

- **Discoverability**: Because paths follow a predictable pattern,
  developers can often guess or easily find the modules they
  need. Documentation and tooling can also leverage this structure to
  provide better discovery experiences.

- **Hierarchical organization**: The path structure naturally supports
  organizing related modules together. For example, all UI-related
  modules might live under `/YourGame.com/UI/`, making them easy to
  find and understand as a group.

Epic Games provides several standard modules that are commonly used:

- `/Verse.org/Verse` - Core language features and standard library functions
- `/Verse.org/Random` - Random number generation utilities
- `/Verse.org/Simulation` - Simulation and timing utilities
- `/Fortnite.com/Devices` - Integration with Fortnite Creative devices
- `/UnrealEngine.com/Temporary/Diagnostics` - Debugging and diagnostic tools
- `/UnrealEngine.com/Temporary/SpatialMath` - 3D math and spatial operations

The use of "Temporary" in some paths indicates that these modules are
provisional and may be reorganized in future versions of Verse. This
naming convention helps set expectations about the stability of the
API.

When you create your own modules, they can exist at various levels of
the path hierarchy:

- `/YourGame/` - Top-level module for your game
- `/YourGame/Player/` - Player-related functionality
- `/YourGame/Player/Inventory/` - Specific inventory management
- `/pizlonator@fn.com/NightDeath/` - Personal or experimental modules

The ability to include email-like identifiers (such as
`pizlonator@fn.com`) allows individual developers to claim their own
namespace without needing to own a domain. This democratizes the
module system while still maintaining uniqueness guarantees.

## Creating Modules

A module can contain:

- Constants and variables
- Functions
- Classes, interfaces, and structs
- Enums
- Other module definitions
- Type definitions

When you create a subfolder in a Verse project, a module is
automatically created for that folder. The file structure directly
maps to the module hierarchy.

You can create modules within a `.verse` file using the following syntax:

<!-- 01 -->
```verse
# Colon syntax
module1 := module:
    # Module contents here
    MyConstant<public>:int = 42

    MyClass<public> := class:
        Value:int = 0

# Bracket syntax (also supported)
module2 := module
{
    # Module contents here
    AnotherConstant<public>:string = "Hello"
}
```

Modules can contain other modules, creating a hierarchy:

<!-- 02 -->
```verse
base_module<public> := module:
    submodule<public> := module:
        submodule_class<public> := class:
            Value:int = 100

    module_class<public> := class:
        Name:string = ""
```

The file structure `module_folder/base_module` is equivalent to:

<!-- 03 -->
```verse
module_folder := module:
    base_module := module:
        submodule := module:
            submodule_class := class:
                # Class definition
```

### Restrictions

Module bodies have strict requirements about what they can
contain. Understanding these restrictions helps avoid common errors
when defining modules.

**Modules Can Only Contain Definitions:**

A module body can only contain definition statements—declarations that
bind names to values. You cannot include arbitrary expressions or
executable statements:

<!--NoCompile-->
<!-- 04 -->
```verse
# Valid: All definitions
config := module:
    MaxValue:int = 100
    DefaultName:string = "Player"

    CalculateScore(Base:int):int = Base * 10

    player_class := class:
        Name:string

# Invalid: Contains non-definition expressions
bad_module := module:
    MaxValue:int = 100
    1 + 2  # ERROR 3560: Not a definition

# Invalid: Contains function call
bad_module2 := module:
    InitFunction():void = {}
    InitFunction()  # ERROR 3585: Cannot call function in module body
```

The restriction ensures that module initialization is deterministic and doesn't execute arbitrary code when the module is loaded.

**Type Annotations Required:**

All data definitions at module scope must explicitly specify their type. Type inference with `:=` alone is not allowed:

<!--NoCompile-->
<!-- 05 -->
```verse
# Invalid: Missing type annotation
bad_module := module:
    Value := 42  # ERROR 3547: Must specify type domain

# Valid: Explicit type annotation
good_module := module:
    Value:int = 42  # OK: Type explicitly specified
```

This requirement makes module interfaces explicit and helps with separate compilation and module evolution.

**Valid Module Contents:**

Modules can contain these categories of definitions:

<!-- 06 -->
```verse
utilities := module:
    # Constants with explicit types
    Version:int = 1
    AppName:string = "MyApp"

    # Functions
    Calculate(X:int):int = X * 2

    # Classes, interfaces, structs
    data_class := class:
        Value:int

    data_interface := interface:
        GetValue():int

    data_struct := struct:
        X:float
        Y:float

    # Enums
    status := enum:
        Active
        Inactive

    # Nested modules
    nested := module:
        NestedFunction():void = {}

    # Type aliases
    coordinate := tuple(float, float)

    # Refinement types
    positive_int := type{X:int where X > 0}
```

Unlike functions, classes, or data values, modules are not first-class
citizens in Verse. You cannot treat modules as values that can be
stored, passed, or manipulated at runtime.

**Cannot Assign Modules to Variables:**

<!--NoCompile-->
<!-- 07 -->
```verse
my_module := module:
    Value<public>:int = 42

# Invalid: Cannot treat module as value
M:my_module = my_module  # ERROR 
```

Modules exist purely as namespaces and organizational constructs at
compile time. The module identifier `my_module` can only be used in
specific contexts.

**Cannot Pass Modules as Arguments:**

<!--NoCompile-->
<!-- 08 -->
```verse
my_module := module:
    X<public>:int = 1

# Invalid: Cannot pass module as parameter
ProcessModule(M:module):void = {}  # ERROR
ProcessModule(my_module)  # ERROR
```

There is no `module` type that can be used in function signatures.

**Cannot Create Collections of Modules:**

<!--NoCompile-->
<!-- 09 -->
```verse
module_a := module:
    Value:int = 1

module_b := module:
    Value:int = 2

# Invalid: Cannot create tuple or array of modules
Modules := (module_a, module_b)  # ERROR
```

## Importing Modules

The import system is designed to be explicit and predictable. Unlike
some languages that automatically import commonly used modules or
search multiple locations for dependencies, Verse requires you to
explicitly declare every external module you want to use. This
explicitness helps prevent naming conflicts and makes dependencies
clear.

The `using` statement is the primary mechanism for importing modules
into your Verse code. It usually is placed at the top of your file, before
any other code definitions, and makes the contents of the specified module
available in your current scope.

The basic syntax is straightforward - the keyword `using` followed by
the module path in curly braces:

<!--NoCompile-->
```verse
using { /Verse.org/Random }
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
```

When you import a module, all its public members become available in
your code. However, you still need to qualify them with the module
name unless the names are unambiguous. This qualification requirement
helps maintain code clarity and prevents accidental use of the wrong
definition when multiple modules define similar names.

**Using is a Statement, Not an Expression:**

The `using` directive is a statement-level declaration that must
appear at the top level of your code. You cannot use it as an
expression or embed it in other expressions:

<!--NoCompile-->
<!-- 11 -->
```verse
# Invalid: using in expression context
# f():void = using{MyModule}  # ERROR 3669

# Invalid: using in conditional
# if (using{MyModule}, Condition?):
#     DoSomething()  # ERROR 3669

# Invalid: using in class/struct/interface body
# my_class := class:
#     using{MyModule}  # ERROR 3537
#     Field:int

# Invalid: using module path in function body
# ProcessData():void =
#     using{/MyProject/UtilityModule}  # ERROR 3669
#     Calculate()
```

Module `using` statements must appear at the file or module level, not
nested within other constructs. This ensures that imports are visible
and consistent throughout the scope where they're declared.

While module imports with paths are not allowed in function bodies,
Verse does support **local scope `using`** with local variables and
parameters. See [Local Scope Using](#local-scope-using) below for
details.

**Valid using placement:**

<!--NoCompile-->
<!-- 12 -->
```verse
# At file level (most common)
using { /Verse.org/Random }
using { /Verse.org/Simulation }

ProcessData():void =
    # Use imported functions
    Value := GetRandomFloat(0.0, 1.0)

# Within module definition
utilities := module:
    using { /Verse.org/Random }

    GenerateId<public>():int =
        GetRandomInt(1, 1000000)
```

### Import Resolution

When Verse encounters a `using` statement, it follows a specific resolution process:

1. **Absolute paths** (starting with `/`) are resolved from the global module registry
2. **Relative paths** (without leading `/`) are resolved relative to the current module's location
3. **Nested modules** can be accessed through their parent modules

This resolution process happens at compile time, meaning that all
imports must be resolvable when your code is compiled. There's no
runtime module loading or dynamic imports in Verse.

### Local and Relative Imports

For modules within your own project, you have flexibility in how you reference them:

<!--NoCompile-->
<!-- 13 -->
```verse
# Absolute import from your project root
using { /MyGameProject/Systems/Combat }

# Import from a sibling folder
using { ../UI/MainMenu }

# Import from the same directory
using { player_controller }

# Import from a subdirectory
using { Subsystems/WeaponSystem }
```

The choice between absolute and relative imports often depends on your
project structure and whether you plan to reorganize your
modules. Absolute imports are more stable when refactoring, while
relative imports can make module groups more portable.

### Nested Imports

Nested modules present special considerations for importing. The order
in which you import modules matters, and there are multiple valid
approaches:

<!--versetest
game_systems := module:
    inventory<public> := module{}
m:=module{
# Method 1: Import parent first, then child
using { game_systems }
using { inventory }  # Assumes inventory is nested in game_systems

# Method 2: Direct path to nested module
using { game_systems.inventory }

# Method 3: Import parent and access child through qualification
using { game_systems }
}
<#
-->
<!-- 14 -->
```verse
# Method 1: Import parent first, then child
using { game_systems }
using { inventory }  # Assumes inventory is nested in game_systems

# Method 2: Direct path to nested module
using { game_systems.inventory }

# Method 3: Import parent and access child through qualification
using { game_systems }
# Later in code: game_systems.inventory.Item

# IMPORTANT: This order causes an error
# using { inventory }      # Error: inventory not found
# using { game_systems }   # Too late, inventory import already failed
```
<!-- #> -->

The restriction on import order exists because Verse resolves imports
sequentially. When you import a nested module directly, Verse needs to
know about its parent module first. This is why importing the parent
before the child always works, while the reverse order fails.

### Scope and Visibility

Imports have file scope - they only affect the file in which they
appear. If you have multiple `.verse` files in the same module, each
file needs its own import statements for external modules. However,
files within the same module can see each other's definitions without
imports:

<!-- 15 -->
```verse
# File: player_module/health.verse
health_component := class:
    CurrentHealth:float = 100.0

# File: player_module/armor.verse
# No import needed for health_component since it's in the same module
armor_component := class:
    HealthComp:health_component = health_component{}
```

### Import Conflicts

When two imported modules define members with the same name, you need to disambiguate:

<!--NoCompile-->
<!-- 16 -->
```verse
using { /GameA/Combat }
using { /GameB/Combat }

# Both modules might define CalculateDamage
# You must use qualified names:
DamageA := Combat.CalculateDamage(10.0)  # Error: ambiguous
DamageA := (/GameA/Combat:)CalculateDamage(10.0)  # OK: fully qualified
DamageB := (/GameB/Combat:)CalculateDamage(10.0)  # OK: fully qualified
```

### Qualified Names

After importing, you can refer to module contents using qualified
names. Verse provides two forms of qualification: standard dot
notation for most cases, and special qualified access syntax for
disambiguation.

When you need to disambiguate between identifiers with the same name
from different modules, or when you want to explicitly specify the
scope of an identifier, use a qualified access expression using
parentheses and a colon:


<!-- BUG? Or bad error message?

m := module{ item<public> := class{} }

x := module{
item := class{}
F():void =
    A := (local:)item{} 
    B := (m:)item{}
}


LogVerseBuild: Error: C:/VerseBook/Book/verse/16_modules/17.versetest(8,10, 8,22): Script Error 3506: Unknown identifier `item`. Did you mean any of:
inventory_module.item
item
LogVerseBuild: Error: C:/VerseBook/Book/verse/16_modules/17.versetest(9,10, 9,33): Script Error 3506: Unknown identifier `item`. Did you mean any of:
inventory_module.item

-->

<!--NoCompile-->
<!-- 17 -->
```verse
# Qualified access syntax: (qualifier:)identifier

using { combat_module }
using { magic_module }

ProcessDamage():void =
    # Both modules define CalculateDamage
    PhysicalDamage := (combat_module:)CalculateDamage(100.0)
    MagicalDamage := (magic_module:)CalculateDamage(100.0)

    # Explicitly qualify local vs module identifiers
    LocalItem := item{Name := "Sword"}  # Local definition
    ModuleItem := (inventory_module:)item{Name := "Shield"}  # From module
```

The qualified access expression `(module:)identifier` is particularly useful in several scenarios:

1. **Resolving naming conflicts**: When multiple imported modules export the same identifier
2. **Explicit scoping**: When you want to make it clear which module an identifier comes from for readability
3. **Accessing shadowed names**: When a local definition shadows a module member
4. **Generic programming**: When working with parametric types where the qualifier might be computed

## Module-Scoped Variables

Variables defined at module scope are global to any game instance where the variable is in scope.

Use `weak_map(session, t)` for variables that persist for the duration of a game session:

<!--versetest
session := class<unique>{}
GetSession()<transacts>:session = session{}
-->
<!-- 20 -->
```verse
var GlobalCounter:weak_map(session, int) = map{}

IncrementCounter()<transacts>:void =
    CurrentValue := if (Value := GlobalCounter[GetSession()]) then Value + 1 else 0
    if (set GlobalCounter[GetSession()] = CurrentValue) {}
```

Use `weak_map(player, t)` for data that persists across game sessions:

<!--versetest
player := class<unique><persistent><module_scoped_var_weak_map_key>{}
var PlayerSaveData:weak_map(player, player_data) = map{}

player_data := class<final><persistable>:
    Level:int = 1
    Experience:int = 0
    UnlockedItems:[]string = array{}

SavePlayerProgress(Player:player, NewData:player_data)<decides>:void =
    set PlayerSaveData[Player] = NewData
<#
-->
<!-- 21 -->
```verse
var PlayerSaveData:weak_map(player, player_data) = map{}

player_data := class<final><persistable>:
    Level:int = 1
    Experience:int = 0
    UnlockedItems:[]string = array{}

SavePlayerProgress(Player:player, NewData:player_data)<decides>:void =
    set PlayerSaveData[Player] = NewData
```
<!-- #> -->

## Metaverse and Publishing

When you publish a module to the Metaverse, the module path becomes
globally accessible, its public members become part of the module's
API, and from that point the module must maintain backward
compatibility.

The following example of shows how evolution works:

<!--NoCompile-->
<!-- 22 -->
```verse
# Initial publication
Thing<public>:rational = 1/3

# Valid updates:
# - Change the value (not the type)
Thing<public>:rational = 10/3

# - Make the type more specific (subtype)
Thing<public>:int = 20  # nat is a subtype of int

# Invalid updates (would be rejected):
# - Remove the member
# - Change to incompatible type
# Thing<public>:string = "hello"  # Would fail
```

## Local Qualifiers

The `(local:)` qualifier can disambiguate identifiers within
functions. This is critical for evolution compatibility—when external
modules add new public definitions after your code is published,
`(local:)` ensures your local definitions take precedence.

<!-- 23 -->
```verse
# External module adds ShadowX after your code published
ExternalModule<public> := module:
    ShadowX<public>:int = 10  # Added later!

MyModule := module:
    using{ExternalModule}

    # Without (local:) - error 3588/3532: shadowing conflict
    # Foo():float =
    #     ShadowX:float = 0.0  # Error: conflicts with ExternalModule.ShadowX
    #     ShadowX

    # With (local:) - clear disambiguation
    Foo():float =
        (local:)ShadowX:float = 0.0  # Local variable
        (local:)ShadowX              # Returns 0.0, not 10
```

The `(local:)` qualifier can be used in these contexts:

**Function parameters:**

<!-- 24 -->
```verse
ProcessValue((local:)Value:int):int =
    (local:)Value + 1
```

**Function body data definitions:**

<!-- 25 -->
```verse
Compute():int =
    (local:)Result:int = 42
    (local:)Result
```

**For loop variables:**

<!-- 26 -->
```verse
SumValues():int =
    var Total:int = 0
    for ((local:)I := 0..10):
        set Total += (local:)I
    Total
```

**If conditions:**

<!--versetest
GetValue<public>()<computes><decides>:float = 10.0
-->
<!-- 27 -->
```verse
CheckValue():float =
    if (X := GetValue[], (local:)X > 5.0):
        (local:)X
    else:
        0.0
```

**Block scopes:**

<!-- 28 -->
```verse
ComputeInBlock():int =
    block:
        (local:)Temp:int = 10
        (local:)Temp * 2
```

**Class blocks:**

<!--NoCompile-->
<!-- 29 -->
```verse
my_class := class:
    var Value<public>:int = 0
    block:
        (local:)Value:int = 42
        set (my_class:)Value = (local:)Value
```

The `(local:)` qualifier **cannot** be used in these contexts (all produce error 3612):


**Nested Scope Limitation:**

Currently, you **cannot** redefine a `(local:)` qualified identifier in nested blocks (error 3532):

<!--NoCompile-->
```verse
# Error: cannot redefine local identifier
F((local:)X:int):int =
    block:
        (local:)X:float = 5.5  # Error: X already defined in function
    (local:)X
```

This limitation may be lifted in future versions to support more complex scoping patterns.

## Automatic Qualification

When you write Verse code, you use simple, unqualified identifiers for
clarity and readability. However, the Verse compiler internally
transforms all identifiers into fully-qualified forms that explicitly
specify their scope and origin. This process, called **automatic
qualification**, ensures that every identifier is unambiguous and can
be resolved to exactly one definition.

Understanding automatic qualification helps you understand how Verse
resolves names, why certain errors occur, and how the module system
maintains correctness even in complex codebases with many modules and
overlapping names.

The compiler qualifies several categories of identifiers:

1. **Top-level definitions** - Functions, variables, classes, modules at package scope
2. **Type references** - All types, including built-in types like `int` and `string`
3. **Function parameters** - Local parameters get the `(local:)` qualifier
4. **Class and interface members** - Methods, fields, nested within composite types
5. **Module members** - Public and internal definitions within modules
6. **Nested scopes** - References within nested modules, classes, and functions

Verse uses several patterns to qualify identifiers based on their scope:

**Package-level qualification**: Definitions at the root of a package
are qualified with the package path:

<!--NoCompile-->
```verse
# What you write:
Function(X:int):int = X

# How the compiler sees it:
(/YourPackage:)Function((local:)X:(/Verse.org/Verse:)int):(/Verse.org/Verse:)int = (local:)X
```

The package path `/YourPackage` becomes the qualifier for `Function`,
while the parameter `X` gets the special `(local:)` qualifier, and the
built-in type `int` is qualified with its standard library path
`/Verse.org/Verse`.

**Local scope qualification**: Function parameters and local variables are marked with `(local:)`:

<!--NoCompile-->
```verse
# What you write:
ProcessValue(Input:int, Multiplier:int):int =
    Input * Multiplier

# How the compiler sees it:
(/YourPackage:)ProcessValue((local:)Input:(/Verse.org/Verse:)int, (local:)Multiplier:(/Verse.org/Verse:)int):(/Verse.org/Verse:)int =
    (local:)Input * (local:)Multiplier
```

**Nested scope qualification**: Members within classes, interfaces, or modules get qualified with their container's path:

<!--NoCompile-->
```verse
# What you write:
player_class := class:
    Health:float = 100.0

    TakeDamage(Amount:float):void =
        set Health = Health - Amount

# How the compiler sees it:
(/YourPackage:)player_class := class:
    (/YourPackage/player_class:)Health:(/Verse.org/Verse:)float = 100.0

    (/YourPackage/player_class:)TakeDamage((local:)Amount:(/Verse.org/Verse:)float):(/Verse.org/Verse:)void =
        set (/YourPackage/player_class:)Health = (/YourPackage/player_class:)Health - (local:)Amount
```

Notice how `Health` and `TakeDamage` are qualified with `/YourPackage/player_class` to indicate they're members of the class.

**Module member qualification**: Definitions within modules are qualified with the module path:

<!--MoCompile-->
```verse
# What you write:
config := module:
    MaxPlayers<public>:int = 100

    GetPlayerLimit<public>():int = MaxPlayers

# How the compiler sees it:
(/YourPackage:)config := module:
    (/YourPackage/config:)MaxPlayers<public>:(/Verse.org/Verse:)int = 100

    (/YourPackage/config:)GetPlayerLimit<public>():(/Verse.org/Verse:)int =
        (/YourPackage/config:)MaxPlayers
```

All built-in types are qualified with their standard library
paths. This makes it explicit where these types come from and
maintains consistency with user-defined types:

<!--NoCompile-->
```verse
# Common built-in types and their full qualifications:
int       → (/Verse.org/Verse:)int
float     → (/Verse.org/Verse:)float
string    → (/Verse.org/Verse:)string
logic     → (/Verse.org/Verse:)logic
message   → (/Verse.org/Verse:)message
```

When you write `X:int`, the compiler expands it to `X:(/Verse.org/Verse:)int`, making the type's origin explicit.

### Example

Here's a more realistic example showing how qualification works across multiple scopes:

<!--NoCompile-->
```verse
# What you write:
game_system := module:
    BaseValue:int = 42

    calculator := module:
        Multiplier:int = 2

        Calculate(Input:int):int =
            Input * Multiplier + BaseValue

# How the compiler sees it:
(/YourGame:)game_system := module:
    (/YourGame/game_system:)BaseValue:(/Verse.org/Verse:)int = 42

    (/YourGame/game_system:)calculator := module:
        (/YourGame/game_system/calculator:)Multiplier:(/Verse.org/Verse:)int = 2

        (/YourGame/game_system/calculator:)Calculate((local:)Input:(/Verse.org/Verse:)int):(/Verse.org/Verse:)int =
            (local:)Input * (/YourGame/game_system/calculator:)Multiplier + (/YourGame/game_system:)BaseValue
```

Notice how:

- The parameter `Input` is `(local:)`
- `Multiplier` is qualified with its containing module path
- `BaseValue` is qualified with the outer module path
- All type references are qualified with the Verse standard library path

### Qualification with Using

When you import modules with `using`, the compiler still qualifies all identifiers, but it can resolve unqualified names to the imported modules:

<!-- NoCompile-->
```verse
# What you write:
using { /Verse.org/Random }

GenerateRandomValue():float =
    GetRandomFloat(0.0, 1.0)

# How the compiler sees it:
using { /Verse.org/Random }

(/YourGame:)GenerateRandomValue():(/Verse.org/Verse:)float =
    (/Verse.org/Random:)GetRandomFloat(0.0, 1.0)
```

The compiler resolves `GetRandomFloat` to `(/Verse.org/Random:)GetRandomFloat` based on the `using` statement.

### When It Matters

You rarely need to think about automatic or manual qualification during normal
development, as the compiler handles it transparently. However,
understanding it helps in several situations:

**Debugging name resolution errors**: When the compiler reports
ambiguous or unresolved identifiers, understanding qualification helps
you see why:

<!--NoCompile-->
```verse
using { /ModuleA }
using { /ModuleB }

# Both modules define Calculate
Result := Calculate(10)  # ERROR: Ambiguous - could be either module
```

The error occurs because the compiler cannot automatically qualify `Calculate` - it could be either `(/ModuleA:)Calculate` or `(/ModuleB:)Calculate`.

**Shadowing conflicts**: When a local variable has the same name as a module member:

<!--NoCompile-->
```verse
MyModule := module:
    Value:int = 100

    Process(Value:int):int =
        # Without explicit qualification, this is ambiguous
        Value + Value  # Which Value? Module or parameter?
```

The compiler needs qualification to distinguish `(/MyModule:)Value` from `(local:)Value`.

**Understanding error messages**: Compiler error messages sometimes
show qualified names to precisely identify which definition is
involved:

```
Error: Cannot assign (/Verse.org/Verse:)string to (/Verse.org/Verse:)int at line 42
```

This makes it clear that the error involves the built-in `string` and
`int` types, not user-defined types with the same names.

**Working with generated or reflected code**: Tools that generate
Verse code or analyze code structure work with the qualified form, so
understanding it helps when working with such tools.

### Explicit Qualification

While the compiler automatically qualifies identifiers, you can also
explicitly qualify them using the qualified access syntax
`(qualifier:)identifier`. This is useful when you want to override
automatic resolution or make your intent explicit:

<!-- 45 FAILURE
  Line 11: Verse compiler error V3509: The assignment's left hand expression type `int` cannot be assigned to
-->
```verse
game_system := module:
    Value:int = 100

    # Explicitly qualify to avoid any ambiguity
    GetValue():int = (game_system:)Value

    # Use local qualifier for parameters
    SetValue((local:)Value:int):void =
        set (game_system:)Value = (local:)Value
```

Explicit qualification is particularly valuable when:

- Resolving naming conflicts between imported modules
- Making code more self-documenting
- Overriding shadowing behavior
- Working with dynamic or computed qualifiers

## Local Scope Using

While module-level `using` imports modules by their paths, Verse also
supports **local scope `using`** within function bodies to enable
member access inference from local variables and parameters. This
feature makes code cleaner when working with objects that have many
member accesses.

Local scope `using` takes a local variable or parameter identifier
(not a module path) and makes its members accessible without explicit
qualification:

<!-- 46 -->
```verse
entity := class:
    Name:string = "Entity"
    var Health:int = 100

    UpdateHealth(Amount:int):void =
        set Health = Health + Amount

ProcessEntity(E:entity):void =
    # Explicit member access
    Print(E.Name)
    E.UpdateHealth(-10)
    Print("{E.Health}")

    # With local using - inferred member access
    using{E}
    Print(Name)         # Inferred as: E.Name
    UpdateHealth(-10)   # Inferred as: E.UpdateHealth(-10)
    Print("{Health}")       # Inferred as: E.Health
```

The `using{E}` expression makes all members of `E` accessible without the `E.` prefix within the current scope.

### With Local Variables

Local `using` works with variables defined in the same function:

<!--versetest
player := class:
    var Name:string = ""
    var Score:int = 0
-->
<!-- 47 -->
```verse
CreateAndProcess():void =
    Player := player{Name := "Alice", Score := 100}

    # Without using
    Print(Player.Name)
    set Player.Score = Player.Score + 50

    # With using
    using{Player}
    Print(Name)         # Inferred as: Player.Name
    set Score = Score + 50  # Inferred as: Player.Score
```

### Block Scoping

The `using` scope is limited to the block where it appears and any nested blocks:

**Using in same block:**

<!--versetest
data_record := class:
    Value:int = 0
    UpdateField<public>(V:int):void = {}
-->
<!-- 48 -->
```verse
ProcessData():void =
    block:
        Data := data_record{}
        using{Data}
        UpdateField(Value)  # Inferred as: Data.UpdateField(Data.Value)
    # Data members no longer accessible here
```

**Using from outer block:**

<!--versetest
data_record := class:
    Value:int = 0
    UpdateField<public>(V:int):void = {}
-->
<!-- 49 -->
```verse
ProcessData():void =
    Data := data_record{}
    block:
        using{Data}  # Can use variable from outer scope
        UpdateField(Value)  # Works - Data in scope
```

**Nested block inheritance:**

<!--versetest
data_record := class:
    Value:int = 0
    UpdateField<public>(V:int):void = {}
-->
<!-- 50 -->
```verse
ProcessData():void =
    Data := data_record{}
    using{Data}  # Applies to this block and nested blocks

    block:
        # Inner block inherits outer using
        UpdateField(Value)  # Still infers Data.UpdateField(Data.Value)
```

### Order

Member inference only works **after** the `using` expression is encountered:

<!--NoCompile-->
```verse
# ERROR: Cannot infer before using
ProcessData(Data:data_record):void =
    UpdateField()  # ERROR - before using
    using{Data}
    UpdateField()  # OK - after using

# ERROR: Using scope doesn't extend backward
ProcessData(Data:data_record):void =
    block:
        using{Data}
        UpdateField()  # OK - within using scope
    UpdateField()  # ERROR - after using scope ended
```

The `using` statement acts as a declaration point - inference is not retroactive.

### Conflict Resolution

You can have multiple `using` expressions in the same scope, but conflicting member names must be explicitly qualified:

<!-- 52 -->
```verse
player_stats := class:
    Health:int = 100
    Mana:int = 50
    GetInfo():string = "Player"

enemy_stats := class:
    Health:int = 80
    Armor:int = 20
    GetInfo():string = "Enemy"

ProcessCombat(Player:player_stats, Enemy:enemy_stats):void =
    using{Player}
    Print(GetInfo())  # Player.GetInfo()
    Print("{Mana}")       # Player.Mana (no conflict)

    using{Enemy}
    # Now both are in scope
    Print("{Armor}")      # Enemy.Armor (no conflict with Player)

    # ERROR: Conflicts must be qualified
    # Print(Health)   # Ambiguous - both have Health
    # Print(GetInfo())  # Ambiguous - both have GetInfo

    # Must qualify conflicting members
    Print("{Player.Health}")
    Print("{Enemy.Health}")
    Print(Player.GetInfo())
    Print(Enemy.GetInfo())
```

When members exist in multiple `using` contexts, you must explicitly qualify to disambiguate.

### Mutable Member

Local `using` works with mutable fields through the `set` keyword:

<!-- 53 -->
```verse
config := class:
    var Volume:float = 1.0
    var Quality:int = 2

UpdateSettings(Settings:config):void =
    using{Settings}

    # Mutable field access
    set Volume = 0.8     # Inferred as: set Settings.Volume = 0.8
    set Quality = 3      # Inferred as: set Settings.Quality = 3
```

## Troubleshooting

When working with modules, you may encounter various issues. Understanding these common problems and their solutions will help you debug module-related errors more efficiently.

### Module Not Found Errors

**Problem**: The compiler reports that a module cannot be found when you try to import it.

**Common Causes and Solutions**:

1. **Incorrect path**: Double-check the module path in your `using` statement. Remember that paths are case-sensitive.

<!--NoCompile-->
<!-- 54 -->
```verse
# Wrong: different case
using { /verse.org/random }  # Error: module not found

# Correct: proper case
using { /Verse.org/Random }  # Works
```

2. **Missing parent module import**: When importing nested modules, ensure the parent is imported first.

<!--NoCompile-->
<!-- 55 -->
```verse
# Wrong: child before parent
using { inventory }  # Error if inventory is nested

# Correct: parent first
using { game_systems }
using { inventory }
```

3. **File location mismatch**: Ensure your file structure matches your module structure. If you have a folder named `player_systems`, all files in that folder are part of the `player_systems` module.

### Access Denied Errors

**Problem**: You can't access a member of an imported module.

**Common Causes and Solutions**:

1. **Missing access specifier**: Members without the `<public>` specifier are internal by default.

<!--NoCompile-->
<!-- 56 -->
```verse
# In module_a
SecretValue:int = 42  # Internal by default
PublicValue<public>:int = 100  # Explicitly public

# In another module
using { module_a }
X := module_a.SecretValue  # Error: not accessible
Y := module_a.PublicValue  # Works
```

2. **Protected or private members**: These are not accessible outside their defining scope.

<!--NoCompile-->
<!-- 57 -->
```verse
# In a class
class_a := class:
    PrivateField<private>:int = 10
    ProtectedField<protected>:int = 20
    PublicField<public>:int = 30

# Outside the class
Obj := class_a{}
X := Obj.PrivateField  # Error: private
Y := Obj.PublicField   # Works
```

### Circular Dependency Errors

**Problem**: Two modules try to import each other, creating a circular dependency.

**Solution**: Restructure your code to avoid circular dependencies:

1. **Extract common code**: Move shared definitions to a third module that both can import.
2. **Use interfaces**: Define interfaces in a separate module to break the dependency cycle.
3. **Reconsider architecture**: Circular dependencies often indicate a design issue that needs rethinking.

### Name Collision Errors

**Problem**: Two imported modules define members with the same name.

**Solution**: Use fully qualified names to disambiguate:

<!--NoCompile-->
```verse
using { /GameA/Combat }
using { /GameB/Combat }

# Ambiguous
Damage := CalculateDamage(10.0)  # Error: which CalculateDamage?

# Explicit
DamageA := /GameA/Combat.CalculateDamage(10.0)  # Clear
DamageB := /GameB/Combat.CalculateDamage(10.0)  # Clear
```

### Persistence Issues

**Problem**: Module-scoped variables aren't persisting as expected.

**Common Causes and Solutions**:

1. **Wrong type used**: Ensure you're using `weak_map(player, t)` for player persistence.
2. **Type not persistable**: Check that your custom types have the `<persistable>` specifier.
3. **Initialization timing**: Make sure you're initializing persistent data at the right time in the game lifecycle.

### Local Qualifier Conflicts

**Problem**: Shadowing errors when local identifiers conflict with module members.

**Solution**: Use the `(local:)` qualifier to disambiguate:

<!-- 59 -->
```verse
module_x := module:
    Value:int = 10

    ProcessValue((local:)Value:int):int =
        (module_x:)Value + (local:)Value  # Clear distinction
```
