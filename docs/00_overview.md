# The Verse Programming Language

## Overview

Verse is a multi-paradigm programming language developed by Epic Games for creating gameplay in Unreal Editor for Fortnite and building experiences in the metaverse. Drawing from functional, logic, and imperative traditions, Verse represents a departure from traditional programming languages, designed not just for today's needs but with a vision spanning decades or even centuries into the future.

Verse is built on three fundamental principles:

- **It's Just Code**:
Complex concepts that might require special syntax or constructs in other languages are expressed as regular Verse code. There's no magic—everything is built from the same primitive constructs, creating a uniform and predictable programming model.

- **Just One Language**:
The same language constructs work at both compile-time and run-time. There is no preprocessor. What you write is what executes, whether during compilation or at runtime.

- **Metaverse First**:
Verse is designed for a future where code runs in a single global simulation—the metaverse. This influences every aspect of the language, from its strong compatibility guarantees to its effect system that tracks side effects and ensures safe concurrent execution.

Verse aims to be:

- **Simple enough** for first-time programmers to learn, with consistent rules and minimal special cases.

- **Powerful enough** for complex game logic and distributed systems, with advanced features that scale to large codebases.

- **Safe enough** for untrusted code to run in a shared environment, with strong sandboxing and effect tracking.

- **Fast enough** for real-time games and simulations, with an implementation that can optimize pure computations aggressively.

- **Stable enough** to last for decades, with strong backward compatibility guarantees and careful evolution.

**Why Verse?**

Traditional programming languages carry decades of historical baggage and design compromises. Verse starts fresh, learning from the past but not  bound by it. It's designed for a future where:

- Code lives forever in a persistent metaverse
- Millions of developers contribute to a shared codebase
- Programs must be safe, concurrent, and composable by default
- Backward compatibility is not optional but essential
- The boundary between compile-time and runtime is fluid

Ready to dive in? Start with [Built-in Types](02_primitives.md) to understand Verse's fundamental data types, or jump to [Expressions](01_expressions.md) to see how everything in Verse computes values.

For experienced programmers coming from other languages, the [Failure System](08_failure.md) and [Effects](13_effects.md) sections highlight some of Verse's distinctive features.

## Key Features

**Everything is an Expression**

In Verse, there are no statements—everything is an expression that produces a value. This creates a highly composable system where any piece of code can be used anywhere a value is expected.

<!--versetest
Condition()<computes><decides> :void= {}
Array :[]int= array{1}
-->
<!-- 01 -->
```verse
# Even control flow produces values
Result := if (Condition[]) then "yes" else "no"

# Loops are expressions
Multiply := for (X : Array) { X * 42 }
```

**Failure as Control Flow**

Instead of boolean conditions and exceptions, Verse uses failure as a primary control flow mechanism. Expressions can succeed (producing a value) or fail (producing no value), enabling natural control flow patterns:

<!--versetest
ValidateInput(x:string)<computes><decides>:void= {}
ProcessData(x:string)<computes>:void= {}
myclass := class{
Data:string="hi"
M()<decides>:void=
    ValidateInput[Data] # Square brackets indicate that this function may fail
    ProcessData(Data)   # Data is only processed if valid, parentheses mean must succeed
}
<#
-->
<!-- 02 -->
```verse
ValidateInput[Data] # Square brackets indicate that this function may fail
ProcessData(Data)   # Data is only processed if valid, parentheses mean must succeed
```
<!-- #> -->

See [Failure](08_failure.md) for complete details on failable expressions and failure contexts, and [Control Flow](07_control.md) for if expressions.

**Strong Static Typing with Inference**

Verse features a powerful type system that catches errors at compile time while minimizing the need for type annotations through inference. See [Types](11_types.md) for complete details on the type system and subtyping.

<!--versetest-->
<!-- 03 -->
```verse
X := 42                    # Type inferred 
Name := "Verse"            # Type inferred
```

**Effect Tracking**

Functions declare their side effects through specifiers like `<computes>`, `<reads>`, `<writes>`, `<transacts>`, `<decides>`, and `<suspends>`. These effect specifiers make it immediately clear what a function can do beyond computing its return value:

<!--versetest
x := class:
    GetCurrentValue()<reads>:int=1
    var Score:int=0
    PureCompute()<computes>:int = 2 + 2            # No side effects
    ReadState()<reads>:int = GetCurrentValue()     # Can read mutable state
    UpdateGame()<transacts>:void = set Score += 10 # Can read, write, allocate
<#
-->
<!-- 04 -->
```verse
PureCompute()<computes>:int = 2 + 2            # No side effects
ReadState()<reads>:int = GetCurrentValue()     # Can read mutable state
UpdateGame()<transacts>:void = set Score += 10 # Can read, write, allocate
```
<!-- #> -->

See [Effects](13_effects.md) for complete details on the effect system.

**Built-in Concurrency**

Concurrency is a first-class feature with structured concurrency primitives that make concurrent programming safe and predictable.

<!--versetest
TaskA()<suspends>:void={}
TaskB()<suspends>:void={}
TaskC():void={}
FastPath()<suspends>:void={}
SlowButReliablePath()<suspends>:void={}
M()<suspends>:void=
    # Run tasks concurrently and wait for all
    sync:
        TaskA()
        TaskB()
        TaskC()

    # Race tasks and take first result
    race:
        FastPath()
        SlowButReliablePath()
<#
-->
<!-- 05 -->
```verse
# Run tasks concurrently and wait for all
sync:
    TaskA()
    TaskB()
    TaskC()

# Race tasks and take first result
race:
    FastPath()
    SlowButReliablePath()
```
<!-- #> -->

**Speculative Execution**

Verse can speculatively execute code and roll back changes if the execution fails, enabling powerful patterns for validation and error handling.

<!--versetest
TryComplexOperation()<computes><decides>:void={}
-->
<!-- 06 -->
```verse
if (TryComplexOperation[]):
    # Changes performed by TryComplexOperation[] are committed
else:
    # Changes are rolled back automatically
```

**Reactive Programming with Live Variables**

Verse provides first-class support for reactive programming through live variables that automatically recompute when their dependencies change, decreasing the need for manual event handling.

<!--versetest
Log(:string)<transacts>:void={}
M()<transacts>:void =
    var MaxHealth:int = 100
    var Damage:int = 0
    var live Health:int = MaxHealth - Damage

    # Health automatically updates when dependencies change
    set Damage = 20      # Health becomes 80
    set MaxHealth = 150  # Health becomes 130

    # Reactive constructs for event handling
    when(Health < 25):
        Log("Low health warning!")
<#
-->
<!-- 07 -->
```verse
var MaxHealth:int = 100
var Damage:int = 0
var live Health:int = MaxHealth - Damage

# Health automatically updates when dependencies change
set Damage = 20      # Health becomes 80
set MaxHealth = 150  # Health becomes 130

# Reactive constructs for event handling
when(Health < 25):
    Log("Low health warning!")
```
<!-- #> -->

Welcome to Verse—a language built not just for today's games, but for tomorrow's metaverse.

## An Example

Let's explore the language with an example that demonstrates its key features. We'll build an inventory management system for a game, showing how Verse's constructs come together to create robust, maintainable code.

<!--NoCompile-->
<!-- 08 -->
```verse
# Module declaration - start by importing utility functions
using { /Verse.org/VerseCLR }

# Define item rarity as an enumeration - showing Verse's type system
item_rarity := enum<persistable>:
    common
    uncommon
    rare
    epic
    legendary

# Struct for immutable item data - functional programming style
item_stats := struct<persistable>:
    Damage:float = 0.0
    Defense:float = 0.0
    Weight:float = 1.0
    Value:int = 0

# Class for game items - object-oriented features with functional constraints
game_item := class<final><unique><persistable>:
    Name:string
    Rarity:item_rarity = item_rarity.common
    Stats:item_stats = item_stats{}
    StackSize:int = 1
    
    # Method with decides effect - can fail
    GetRarityMultiplier()<decides>:float =
        case(Rarity):
            item_rarity.common => 1.0
            item_rarity.uncommon => 1.5
            item_rarity.rare => 2.0
            item_rarity.epic => 3.0
            _ => {false?; 0.0}  # Fails if the item is legenday or unexpected
    
    # Computed property using closed-world function
    GetEffectiveValue()<transacts><decides>:int=
        Floor[Stats.Value * GetRarityMultiplier[]]

# Inventory system with state management and effects
inventory_system := class:
    var Items:[]game_item = array{}
    var MaxWeight:float = 100.0
    var Gold:int = 1000

    # Method demonstrating failure handling and transactional semantics
    AddItem(NewItem:game_item)<transacts><decides>:void =
        # Calculate new weight - speculative execution
        CurrentWeight := GetTotalWeight()
        NewWeight := CurrentWeight + NewItem.Stats.Weight

        # This check might fail, rolling back any changes
        NewWeight <= MaxWeight
        
        # Only executes if weight check passes
        set Items += array{NewItem}
        Print("Added {NewItem.Name} to inventory")

    # Method with query operator and failure propagation
    RemoveItem(ItemName:string)<transacts><decides>:game_item =
        var RemovedItem:?game_item = false
        var NewItems:[]game_item = array{}
        
        for (Item : Items):
            if (Item.Name = ItemName, not RemovedItem?):
                set RemovedItem = option{Item}
            else:
                set NewItems += array{Item}
        set Items = NewItems
        RemovedItem?  # Fails if item not found

    # Purchase with complex failure logic and rollback
    PurchaseItem(ShopItem:game_item)<transacts><decides>:void =
        # Multiple failure points - any failure rolls back all changes
        Price := ShopItem.GetEffectiveValue[]
        Price <= Gold  # Fails if not enough gold
        
        # Tentatively deduct gold
        set Gold = Gold - Price
        
        # Try to add item - might fail due to weight
        AddItem[ShopItem]
        
        # All succeeded - changes are committed
        Print("Purchased {ShopItem.Name} for {Price} gold")

    # Higher-order function with type parameters and where clauses
    FilterItems(Predicate:type{_(:game_item)<decides>:void}):[]game_item =
        for (Item : Items, Predicate[Item]):
            Item

    GetTotalWeight()<transacts>:float =
        var Total:float = 0.0
        for (Item : Items):
            set Total += Item.Stats.Weight
        Total

# Player class using composition
player_character<public> := class:
    Name<public>:string
    var Level:int = 1
    var Experience:int = 0
    var Inventory:inventory_system = inventory_system{}
    
    LevelUpThreshold := 100

    GainExperience(Amount:int)<transacts>:void =
        set Experience += Amount
        
        # Automatic level up check with failure handling
        loop:
            RequiredXP := LevelUpThreshold * Level
            if (Experience >= RequiredXP):
                set Experience -= RequiredXP
                set Level += 1
                Print("{Name} leveled up to {Level}!")
            else:
                break
    
    # Method showing qualified access
    EquipStarterGear()<transacts><decides>:void =
        StarterSword := game_item{
            Name := "Rusty Sword"
            Rarity := item_rarity.common
            Stats := item_stats{Damage := 10.0, Weight := 5.0, Value := 50}
        }
        # These might fail if inventory is full
        Inventory.AddItem[StarterSword]

# Example usage demonstrating control flow and failure handling
RunExample<public>()<suspends>:void =
    # Create a player (can't fail)
    Hero := player_character{Name := "Verse Hero"}
    
    # Try to equip starter gear (might fail)
    if (Hero.EquipStarterGear[]):
        Print("Hero equipped with starter gear")
    
    # Demonstrate transactional behavior
    ExpensiveItem := game_item{
        Name := "Golden Crown"
        Rarity := item_rarity.epic
        Stats := item_stats{Value := 2000, Weight := 90.0}  # Very heavy!
    }
    
    # This might fail due to weight or insufficient gold
    if (Hero.Inventory.PurchaseItem[ExpensiveItem]):
        Print("Purchase successful!")
    else:
        Print("Purchase failed - gold remains at {Hero.Inventory.Gold}")

    # Use higher-order functions with nested function predicate
    IsRareOrLegendary(I:game_item)<decides>:void =
        I.Rarity = item_rarity.rare or I.Rarity = item_rarity.legendary

    RareItems := Hero.Inventory.FilterItems(IsRareOrLegendary)

    Print("Found {RareItems.Length} rare items")
```

<!--

The above has some superfluous <transacts> due to <no_rollback>, in some cases they could be just <computes>.  Apparently an Old VM pathology

Also methods that have an empty return type have weird behavior in some cases. Easily fixed by typing them.
-->

This example showcases Verse in a practical context. Let's explore what makes this code uniquely Verse:

**Type System and Data Modeling**

The example begins with Verse's rich type system. Types flow naturally through the code; many type annotations are omitted as they can be infered. When we do specify types, like `Items:[]game_item`, they document intent rather than just satisfy the compiler. The `item_rarity` enum provides type-safe constants without the boilerplate of traditional enumerations. The `item_stats` struct marked as `<persistable>` can be saved and loaded from persistent storage, essential for game saves. The `game_item` class uses `<unique>` to ensure reference equality semantics.  

**Failure as Control Flow**

Throughout the code, failure drives control flow rather than exceptions or error codes. The `<decides>` effect marks functions that can fail, and failure propagates naturally through expressions. When `GetRarityMultiplier()` encounters an unknown rarity, it doesn't throw an exception or return a sentinel value - it simply fails, and the calling code handles this gracefully.
The `AddItem` method demonstrates how failure creates elegant validation. The expression `NewWeight <= MaxWeight` either succeeds (allowing execution to continue) or fails (preventing the item from being added). There's no explicit control flow - just a declarative assertion of what must be true.

**Transactional Semantics and Speculative Execution**

Methods marked with `<transacts>` provide automatic rollback on failure. In `PurchaseItem`, we deduct gold from the player, then try to add the item. If adding fails (perhaps due to weight limits), the gold deduction is automatically rolled back. This eliminates entire categories of bugs related to partial state updates.
This transactional behavior extends to complex operations. When multiple changes need to succeed or fail together, Verse ensures consistency without need for manual clean up.

**Functions as First-Class Values**

The `FilterItems` method accepts a predicate function, demonstrating higher-order programming. The nested function `IsRareOrLegendary` in `RunExample` shows how functions can be defined locally and passed around like any other value. This functional programming style combines naturally with the imperative and object-oriented features.

**Optional Types and Query Operators**

The inventory removal logic uses optional types (`?game_item`) to represent values that might not exist. The query operator `?` extracts values from options, failing if the option is empty. This eliminates null pointer exceptions while providing convenient syntax for handling absent values.

**Pattern Matching and Control Flow**

The `case` expression in `GetRarityMultiplier` demonstrates pattern matching. Unlike a switch statement, `case` is an expression that produces a value. The underscore `_` provides a catch-all pattern, though in this example it leads to failure.
The `if` expression similarly produces values and can bind variables in its condition. The compound conditions show how multiple operations can be chained with automatic failure propagation.

**Module System and Access Control**

The code begins with `using` statements that import functionality from other modules. The path-based module system ensures that dependencies are unambiguous and permanently addressable. Access specifiers like `<public>` control visibility at a fine-grained level.

**Immutable by Default**

Data structures are immutable unless explicitly marked with `var`. This eliminates large classes of bugs and makes concurrent programming safer. When we do need mutation, it's explicit and tracked by the effect system. See [Mutability](05_mutability.md) for complete details on `var` and `set`.

## Naming Conventions

Verse has a set of naming conventions that make code readable and predictable. While the language doesn't enforce these conventions, following them ensures your code integrates well with the broader Verse ecosystem and is immediately familiar to other Verse developers.

Identifiers should be in PascalCase (CamelCase starting with uppercase):

<!--versetest
player_character := class:
    Name:string
    Level:int
inventory_item := struct:
    ItemId:int
    Quantity:int
game_state := enum:
    main_menu
    in_game
    paused
    game_over
PlayerDatabase(id:int)<decides>:player_character=player_character{Name:="", Level:=1}
# Variables and constants use PascalCase
PlayerHealth:int = 100
MaxInventorySize:int = 50
IsGameActive:logic = true

# Functions use PascalCase
CalculateDamage(Base:float, Multiplier:float):float =
    Base * Multiplier

GetPlayerName(Id:int)<decides>:string =
    PlayerDatabase[Id].Name
<#
-->
<!-- 09 -->
```verse
# Variables and constants use PascalCase
PlayerHealth:int = 100
MaxInventorySize:int = 50
IsGameActive:logic = true

# Functions use PascalCase
CalculateDamage(Base:float, Multiplier:float):float =
    Base * Multiplier

GetPlayerName(Id:int)<decides>:string =
    PlayerDatabase[Id].Name

# Classes and structs use snake_case
player_character := class:
    Name:string
    Level:int

inventory_item := struct:
    ItemId:int
    Quantity:int

# Enums and their values use snake_case
game_state := enum:
    main_menu
    in_game
    paused
    game_over
```
<!-- #> -->

Generic type parameters use single lowercase letters or short descriptive names:

<!--versetest-->
<!-- 10 -->
```verse
# Single letter for simple generics
Find(Array:[]t, Target:t where t:type):?int = false

# Descriptive names for complex relationships
Transform(Input:in_t, Processor:type{_(:in_t):out_t} where in_t:type, out_t:type):?out_t = false
```


Module names follow the snake_case pattern, while paths use a hierarchical structure with forward slashes and PascalCase for path segments:

<!--NoCompile-->
<!-- 11 -->
```verse
# Module definition
inventory_system := module:
    # Module contents

# Path structure uses PascalCase for segments
using { /Fortnite.com/Characters/PlayerController }
using { /MyGame.com/Systems/CombatSystem }
using { /Verse.org/Random }
```

Class and struct fields use PascalCase, and methods follow the same PascalCase convention as functions:

<!--versetest
player := class:
    Name:string          # PascalCase for fields
    var Health:float= 0.0

    # Methods use PascalCase like functions
    TakeDamage(Amount:float):void =
        set Health = Max(0.0, Health - Amount)

    IsAlive():logic =
        logic{Health > 0.0}
<#
-->
<!-- 12 -->
```verse
player := class:
    Name:string          # PascalCase for fields
    var Health:float= 0.0

    # Methods use PascalCase like functions
    TakeDamage(Amount:float):void =
        set Health = Max(0.0, Health - Amount)

    IsAlive():logic =
        logic{Health > 0.0}
```
<!-- #> -->

## Code Formatting

Verse code follows consistent formatting patterns to emphasize readability.

Use four spaces to indent code blocks. The colon introduces a block, with subsequent lines indented:

<!--versetest
Condition()<decides><transacts>:void = {}
DoSomething()<transacts>:void = {}
DoSomethingElse()<transacts>:void = {}
Inventory:[]int = array{1, 2, 3}
ProcessItem(Item:int)<transacts>:void = {}
UpdateDisplay()<transacts>:void = {}
ImplementationHere()<transacts>:void = {}

M()<transacts>:void =
    if (Condition[]):
        DoSomething()
        DoSomethingElse()

    for (Item : Inventory):
        ProcessItem(Item)
        UpdateDisplay()

class_definition := class:
    Field1:int
    Field2:string

    Method():void =
        ImplementationHere()
<#
-->
<!-- 13 -->
```verse
if (Condition[]):
    DoSomething()
    DoSomethingElse()

for (Item : Inventory):
    ProcessItem(Item)
    UpdateDisplay()

class_definition := class:
    Field1:int
    Field2:string

    Method():void =
        ImplementationHere()
```
<!-- #> -->

Complex expressions benefit from clear formatting that shows structure:

<!--versetest
player_type := struct{Health:int}
Player:player_type = player_type{Health := 75}
BaseDamage:float = 100.0
LevelMultiplier:float = 1.5
BonusPercentage:float = 10.0
rarity_type := enum{common; uncommon; rare; epic; legendary}
Rarity:rarity_type = rarity_type.rare
-->
<!-- 14 -->
```verse
# Multi-line conditionals
Result := if (Player.Health > 50):
    "healthy"
else if (Player.Health > 20):
    "injured"
else:
    "critical"

# Chained operations with clear precedence
FinalDamage :=
    BaseDamage *
    LevelMultiplier *
    (1.0 + BonusPercentage / 100.0)

# Pattern matching with aligned cases
DamageMultiplier := case(Rarity):
    rarity_type.common => 1.0
    rarity_type.uncommon => 1.5
    rarity_type.rare => 2.0
    rarity_type.epic => 3.0
    rarity_type.legendary => 5.0
```

Functions follow a consistent pattern with effects and return types clearly specified:

<!--versetest
difficulty_level := enum{easy; medium; hard}
ValidateAmount(Amount:int)<transacts><decides>:void = {}
DeductBalance(Amount:int)<transacts>:void = {}
RecordTransaction()<transacts>:void = {}
GetBaseReward(Difficulty:difficulty_level)<decides>:?int = option{100}
CalculateTimeBonus(CompletionTime:float):int = 50
-->
<!-- 15 -->
```verse
# Simple pure function
Add(X:int, Y:int)<computes>:int = X + Y

# Function with effects
ProcessTransaction(Amount:int)<transacts><decides>:void =
    ValidateAmount[Amount]
    DeductBalance(Amount)
    RecordTransaction()

# Multi-line function with clear structure
CalculateReward(
    PlayerLevel:int,
    Difficulty:difficulty_level,
    CompletionTime:float
)<decides>:int =
    BaseReward := GetBaseReward[Difficulty]?
    LevelBonus := PlayerLevel * 10
    TimeBonus := CalculateTimeBonus(CompletionTime)
    BaseReward + LevelBonus + TimeBonus
```

## Comments

Comments are ignored during execution but are valuable for understanding and maintaining code. Verse offers several styles of comments to suit different documentation needs. The simplest is the single-line comment, which begins with `#` and continues to the end of the line:

<!--versetest-->
<!-- 16 -->
```verse
CalculateDamage := 100 * 1.5  # Apply critical hit multiplier
```

When you need to document something within a line of code without breaking it up, inline block comments provide the perfect solution. These are enclosed between `<#` and `#>`:

<!--versetest
BaseValue:int = 100
Multiplier:int = 2
Bonus:int = 10
-->
<!-- 17 -->
```verse
Result := BaseValue <# original amount #> * Multiplier <# scaling factor #> + Bonus
```

The same can be used to write multi-line block comments, making them ideal for explaining complex algorithms or providing detailed context:

<!--versetest
<# This function implements the quadratic damage falloff formula
   used throughout the game. The falloff ensures that damage
   decreases smoothly with distance, creating strategic positioning
   choices for players. #>
CalculateFalloffDamage(Distance:float, MaxDamage:float):float =
    MaxDamage  # Implementation here
<#
-->
<!-- 18 -->
```verse
<# This function implements the quadratic damage falloff formula
   used throughout the game. The falloff ensures that damage
   decreases smoothly with distance, creating strategic positioning
   choices for players. #>
CalculateFalloffDamage(Distance:float, MaxDamage:float):float =
    # Implementation here
```
<!-- #> -->

Block comments nest, which allows you to temporarily disable code that already contains comments without having to remove or modify existing documentation:

<!--versetest-->
<!-- 19 -->
```verse
<# Temporarily disabled for testing
   OriginalFunction()  <# This had a bug #>
   NewFunction()       # Testing this approach
#>
```

Indented comments begin with a `<#>` on its own line; everything indented by four spaces on subsequent lines becomes part of the comment:

<!--versetest
DoSomething():void = {}
-->
<!-- 20 -->
```verse
<#>
    This entire block is a comment because it's indented.
    It provides a clean way to write longer documentation
    without cluttering each line with comment markers.

DoSomething()  # Not part of the comment.
```

## Syntactic Styles

Verse offers flexible syntax to accommodate different programming styles. The same logic can be expressed using braces, indentation, or inline forms, allowing you to choose the clearest representation for each context.

The braced style uses curly braces to delimit blocks, familiar from C-family languages:

<!--versetest
Score:int = 85
-->
<!-- 21 -->
```verse
Result := if (Score > 90) {
    "excellent"
} else if (Score > 70) {
    "good"
} else {
    "needs improvement"
}
```

The indented style uses colons and indentation to define structure, similar to Python:

<!--versetest
Score:int = 85
-->
<!-- 22 -->
```verse
Result := if (Score > 90):
    "excellent"
else if (Score > 70):
    "good"
else:
    "needs improvement"
```

For simple expressions, the inline style keeps everything on one line:

<!--versetest
Score:int = 85
-->
<!-- 23 -->
```verse
Result := if (Score > 90) then "excellent" else if (Score > 70) then "good" else "needs improvement"
```

The dotted style uses a period to introduce the expression:

<!--versetest
Score:int = 85
-->
<!-- 24 -->
```verse
Result := if (Score > 90). "excellent" else if (Score > 70). "good" else. "needs improvement"
```

You can even mix styles when it makes sense:

<!--versetest
ComplexCondition()<transacts><decides>:void = {}
AnotherCheck()<transacts><decides>:void = {}
YetAnotherValidation()<transacts><decides>:void = {}
M()<transacts>:void =
    Result := if:
        ComplexCondition[] and
        AnotherCheck[] and
        YetAnotherValidation[]
    then { "condition met" } else { "condition not met" }
<#
-->
<!-- 25 -->
```verse
Result := if:
    ComplexCondition() and
    AnotherCheck() and
    YetAnotherValidation()
then { "condition met" } else { "condition not met" }
```
<!-- #> -->

All these forms produce the same result. The choice between them is about readability and context. Use braces when working with existing brace-heavy code, indentation for cleaner vertical layouts, and inline forms for simple expressions. This flexibility lets you write code that reads naturally.
