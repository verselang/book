# Persistable Types

Persistable types allow you to store data that persists beyond the
current game session. This is essential for saving player progress,
preferences, and other game state that should be maintained across
multiple play sessions.

Persistable data is stored using module-scoped `weak_map(player, t)`
variables, where `t` is any persistable type. When a player joins a
game, their previously saved data is automatically loaded into all
module-scoped variables of type `weak_map(player, t)`.

<!--NoCompile-->
<!-- 01 -->
```verse
using { /Fortnite.com/Devices }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /Verse.org/Simulation }

# Global persistable variable storing player data
MySavedPlayerData : weak_map(player, int) = map{}

# Initialize data for a player if not already present
InitializePlayerData(Player : player) : void =
    if (not MySavedPlayerData[Player]):
        if (set MySavedPlayerData[Player] = 0) {}
```

## Built-in Persistable Types

The following primitive types are persistable by default:

- Numeric Types:

   - **`logic`** - Boolean values (true/false)
   - **`int`** - Integer values (currently 64-bit signed)
   - **`float`** - Floating-point numbers

- Character Types:

   - **`string`** - Text values
   - **`char`** - Single UTF-8 character
   - **`char32`** - Single UTF-32 character

- Container Types:

   - **`array`** - Persistable if element type is persistable
   - **`map`** - Persistable if both key and value types are persistable
   - **`option`** - Persistable if the wrapped type is persistable
   - **`tuple`** - Persistable if all element types are persistable

## Custom Persistable Types

You can create custom persistable types using the `<persistable>`
specifier with classes, structs, and enums.

Classes must meet specific requirements to be persistable:

<!--verse
player_class := enum<persistable>{
    Villager
}
-->
<!-- 02 -->
```verse
player_profile_data := class<final><persistable>:
    Version:int = 1
    Class:player_class = player_class.Villager
    XP:int = 0
    Rank:int = 0
    CompletedQuestCount:int = 0
```

Requirements for persistable classes:

- Must have the `<persistable>` specifier
- Must be `<final>` (no subclasses allowed)
- Cannot be `<unique>` 
- Cannot have a superclass (including interfaces) 
- Cannot be parametric (generic) 
- Can only contain persistable field types 
- Cannot have variable members (`var` fields) 
- Field initializers must be effect-free (cannot use `<transacts>`, `<decides>`, etc.) 

Structs are ideal for simple data structures that won't change after
publication:

<!-- 03 -->
```verse
coordinates := struct<persistable>:
    X:float = 0.0
    Y:float = 0.0
```

Requirements for persistable structs:

- Must have the `<persistable>` specifier
- Cannot be parametric (generic) 
- Can only contain persistable field types (see Prohibited Field Types below) 
- Field initializers must be effect-free (cannot use `<transacts>`, `<decides>`, etc.)
- Cannot be modified after island publication

Enums represent a fixed set of named values:

<!-- 04 -->
```verse
day := enum<persistable>:
    Monday
    Tuesday
    Wednesday
    Thursday
    Friday
    Saturday
    Sunday
```

Important notes:

- `<closed>` persistable enums cannot be changed to open after publication
- Only `<open>` persistable enums can have new values added after publication

## Prohibited Field Types

Persistable types have strict restrictions on what field types they
can contain. The following types **cannot** be used as fields in
persistable classes or structs:

- Abstract and Dynamic Types:

   - **`any`** - Cannot be persisted (too dynamic)
   - **`comparable`** - Abstract interface type
   - **`type`** - Type values cannot be persisted

- Non-Serializable Types:

   - **`rational`** - Exact rational numbers (not persistable)
   - **Function types** (e.g., `int -> int`) - Functions cannot be serialized
   - **`weak_map`** - Weak references are not persistable
   - **Interface types** - Abstract interfaces cannot be persisted

- Non-Persistable User Types

   - **Non-persistable enums** - Enums without `<persistable>` specifier cannot be used
   - **Non-persistable classes** - Classes without `<persistable>` specifier cannot be used
   - **Non-persistable structs** - Structs without `<persistable>` specifier cannot be used


## Example

Initializing Player Data:

<!--versetest
player := class<unique><persistent><module_scoped_var_weak_map_key>{}
player_stats := struct<persistable>:
    Level:int = 1
    Experience:int = 0
    GamesPlayed:int = 0

var PlayerData : weak_map(player, player_stats) = map{}

GetOrCreatePlayerStats(Player : player) : player_stats =
    if (ExistingStats := PlayerData[Player]):
        ExistingStats
    else:
        NewStats := player_stats{}
        if (set PlayerData[Player] = NewStats):
            NewStats
        else:
            player_stats{}  # Fallback
<#
-->
<!-- 06 -->
```verse
# Define a persistable player stats structure
player_stats := struct<persistable>:
    Level:int = 1
    Experience:int = 0
    GamesPlayed:int = 0

# Global persistent storage
PlayerData : weak_map(player, player_stats) = map{}

# Initialize or retrieve player data
GetOrCreatePlayerStats(Player : player) : player_stats =
    if (ExistingStats := PlayerData[Player]):
        ExistingStats
    else:
        NewStats := player_stats{}
        if (set PlayerData[Player] = NewStats):
            NewStats
        else:
            player_stats{}  # Fallback
```
<!-- #> -->


## JSON Serialization

!!! note "Unreleased Feature"
    JSON Serialization have not yet been released and is not publicly available.

Verse provides JSON serialization functions for persistable types,
enabling manual serialization and deserialization of data. While the
primary persistence mechanism uses `weak_map(player, t)` for automatic
player data, JSON serialization can be useful for debugging, data
migration, or integration with external systems.

Converts a persistable value to JSON string:

<!--versetest
Persistence := module{
    GetPersistentData<public>(P:player):?any = false
}
player := class<unique>{}
-->
<!-- 08 FAILURE
  Line 7: Verse compiler error V3547: Expected a type, got archetype constructor instead.
  Line 8: Verse compiler error V3506: Unknown identifier `Persistence`.
  Line 7: Verse compiler error V3512: This archetype instantiation constructs a class that has the 'transacts' effect, which is not allowed by its context.
-->
```verse
player_data := class<final><persistable>:
    Level:int = 1
    Score:int = 100

Data := player_data{Level := 5, Score := 250}
JsonString := Persistence.ToJson[Data]
# Produces: {"$package_name":"/...", "$class_name":"player_data", "x_Level":5, "x_Score":250}
```

Deserializes JSON string to typed value:

<!-- 09 FAILURE
  Line 3: Verse compiler error V3100: vErr:S86: Expected expression or "}", got "\" in string interpolation
-->
```verse
JsonString := "{\"$package_name\":\"/.../\", \"$class_name\":\"player_data\", \"x_Level\":10, \"x_Score\":500}"
if (Restored := Persistence.FromJson[JsonString, player_data]):
    # Restored.Level = 10
    # Restored.Score = 500
```

All serialized persistable objects include metadata fields:

```json
{
  "$package_name": "/SolIdeDataSources/_Verse",
  "$class_name": "player_data",
  "x_Level": 5,
  "x_Score": 250
}
```

**Metadata fields:**

- `$package_name` - Package path of the type
- `$class_name` - Qualified class/struct name

**Field names:**

- Prefixed with `x_` in current format
- Old format used mangled names like `i___verse_0x123_FieldName`

### Type-Specific Serialization

**Primitives:**

<!--versetest
Persistence := module{
    GetPersistentData<public>(P:player):?any = false
}
player := class<unique>{}
#>
-->
<!-- 11 FAILURE
  Line 7: Verse compiler error V3506: Unknown identifier `Persistence`.
-->
```verse
int_ref := class<final><persistable>:
    Value:int

# Serialized as JSON number
JsonString := Persistence.ToJson[int_ref{Value := 42}]
# {"$package_name":"...", "$class_name":"int_ref", "x_Value":42}
```

**Optional types:**

<!-- 12 FAILURE
  Line 7: Verse compiler error V3585: Function declaration must declare return type or body.
  Line 11: Verse compiler error V3585: Function declaration must declare return type or body.
-->
```verse
optional_ref := class<final><persistable>:
    Value:?int

# None serialized as false
Persistence.ToJson[optional_ref{Value := false}]
# {..., "x_Value":false}

# Some serialized as object with empty key
Persistence.ToJson[optional_ref{Value := option{42}}]
# {..., "x_Value":{"":42}}
```

**Tuples:**

<!-- 13 FAILURE
  Line 7: Verse compiler error V3585: Function declaration must declare return type or body.
  Line 14: Verse compiler error V3585: Function declaration must declare return type or body.
-->
```verse
tuple_ref := class<final><persistable>:
    Pair:tuple(int, int)

# Serialized as JSON array
Persistence.ToJson[tuple_ref{Pair := (4, 5)}]
# {..., "x_Pair":[4,5]}

# Empty tuple
empty_tuple_ref := class<final><persistable>:
    Empty:tuple()

Persistence.ToJson[empty_tuple_ref{Empty := ()}]
# {..., "x_Empty":[]}
```

**Arrays:**
<!-- 14 FAILURE
  Line 6: Verse compiler error V3585: Function declaration must declare return type or body.
-->
```verse
array_ref := class<final><persistable>:
    Numbers:[]int

Persistence.ToJson[array_ref{Numbers := array{1, 2, 3}}]
# {..., "x_Numbers":[1,2,3]}
```

**Maps:**

<!-- 15 FAILURE
  Line 6: Verse compiler error V3585: Function declaration must declare return type or body.
-->
```verse
map_ref := class<final><persistable>:
    Lookup:[string]int

Persistence.ToJson[map_ref{Lookup := map{"a" => 1, "b" => 2}}]
# {..., "x_Lookup":[{"k":{"":"a"},"v":{"":1}}, {"k":{"":"b"},"v":{"":2}}]}
```

**Enums:**

<!-- 16 FAILURE
  Line 10: Verse compiler error V3585: Function declaration must declare return type or body.
-->
```verse
day := enum<persistable>:
    Monday
    Tuesday

enum_ref := class<final><persistable>:
    Day:day

Persistence.ToJson[enum_ref{Day := day.Monday}]
# {..., "x_Day":"day::Monday"}
```

### Default Value Handling

When deserializing, missing fields are automatically filled with their default values:

<!-- 17 FAILURE
  Line 8: Verse compiler error V3100: vErr:S86: Expected expression or "}", got "\" in string interpolation
-->
```verse
versioned_data := class<final><persistable>:
    Version:int = 1
    NewField:int = 0  # Added in v2

# Old JSON without NewField
OldJson := "{\"$package_name\":\"...\", \"$class_name\":\"versioned_data\", \"x_Version\":1}"

# Deserializes successfully with default for NewField
if (Data := Persistence.FromJson[OldJson, versioned_data]):
    Data.Version = 1
    Data.NewField = 0  # Uses default value
```

This enables forward-compatible schema evolution - new fields with
defaults can be added without breaking old saved data.

### Block Clauses During Deserialization

Block clauses do not execute when deserializing from JSON:

<!--versetest
Persistence := module{
    GetPersistentData<public>(P:player):?any = false
}
player := class<unique>{}
-->
<!-- 18 FAILURE
  Line 9: Verse compiler error V3547: Expected a type, got archetype constructor instead.
  Line 12: Verse compiler error V3506: Unknown identifier `Persistence`.
  Line 13: Verse compiler error V3506: Unknown identifier `Persistence`.
  Line 9: Verse compiler error V3512: This archetype instantiation constructs a class that has the 'transacts' effect, which is not allowed by its context.
-->
```verse
logged_class := class<final><persistable>:
    Value:int
    block:
        Print("Constructed!")

# Normal construction triggers block
Instance1 := logged_class{Value := 1}  # Prints "Constructed!"

# Deserialization does NOT trigger block
Json := Persistence.ToJson[Instance1]
Instance2 := Persistence.FromJson[Json, logged_class]  # No print
```

Block clauses are only executed during normal construction, not during
deserialization. This means initialization logic in blocks won't run
for loaded data.

### Integer Range Limitations

Verse protects against integer overflow during serialization. Integers
that exceed the safe serialization range cause runtime errors:

<!-- 19 FAILURE
  Line 8: Verse compiler error V3585: Function declaration must declare return type or body.
  Line 12: Verse compiler error V3560: Expected definition but found macro invocation.
  Line 7: Verse compiler error V3547: Expected a type, got archetype constructor instead.
  Line 11: Verse compiler error V3502: Module-scoped `var` must have `weak_map` type.
  Line 7: Verse compiler error V3512: This archetype instantiation constructs a class that has the 'transacts' effect, which is not allowed by its context.
-->
```verse
int_ref := class<final><persistable>:
    Value:int

# Safe range integers work fine
SafeData := int_ref{Value := 1000000000000000000}
Persistence.ToJson[SafeData]  # OK

# Overflow protection - runtime error for very large integers
var BigInt:int = 1
for (I := 1..63):
    set BigInt *= 2

# Runtime error: Integer too large for safe serialization
# Persistence.ToJson[int_ref{Value := BigInt}]
```

This prevents silent precision loss that could occur with
floating-point representation of large integers.

### Backward Compatibility

The serialization system maintains backward compatibility with older JSON formats:

**Field name migration:**
<!-- 20 FAILURE
  Line 4: Verse compiler error V3100: vErr:S86: Expected expression or "}", got "\" in string interpolation
-->
```verse
# Old format (V1) with mangled names
OldJson := "{\"$package_name\":\"...\", \"i___verse_0x123_Value\":42}"

# Deserializes correctly
Data := Persistence.FromJsonV1[OldJson, int_ref]

# Re-serializes with new format
NewJson := Persistence.ToJson[Data]
# {"$package_name":"...", "x_Value":42}
```

## Best Practices

- **Schema Stability:** Design your persistable types carefully, as
they cannot be easily changed after publication. Consider versioning
strategies for future updates.

- **Use Structs for Simple Data:** For data that won't need
inheritance or complex behavior, prefer persistable structs over
classes.

- **Handle Missing Data:** Always check if data exists for a player
before accessing it, and provide appropriate defaults.

- **Atomic Updates:** When updating persistent data, create new
instances rather than trying to modify existing ones (Verse uses
immutable data structures).

- **Consider Memory Usage:** Persistent data is loaded for all players
when they join, so be mindful of the amount of data stored per player.


## Example: Player Profile System

<!-- 25 FAILURE
  Line 3: Verse compiler error V3587: The identifier 'Fortnite.com' in  does not refer to a logical scope. Possible segments are Verse.org, localhost
  Line 4: Verse compiler error V3587: The identifier 'Simulation' in /Verse.org does not refer to a logical scope. Possible segments are Verse, Native, Concurrency, Predicts, Random, VerseCLR, Persona
  Line 29: Verse compiler error V3506: Unknown identifier `player`.
  Line 40: Verse compiler error V3506: Unknown identifier `player`.
  Line 32: Verse compiler error V3506: Unknown identifier `creative_device`.
  Line 34: Verse compiler error V3523: Function (/localhost/EmptyProject/profile_manager:)OnBegin has an <override> attribute, but could not find a parent function to override (perhaps the parent function's access specifiers are too restrictive?).
  Line 36: Verse compiler error V3506: Unknown identifier `GetPlayspace`.
  Line 37: Verse compiler error V3524: Must be an array, map, or generator after ':' inside `for`
  Line 41: Verse compiler warning V2017: This container lookup is unlikely to succeed. (Did you mean to use a different key?)
  Line 43: Verse compiler error V3512: This invocation calls a function that has the 'decides' effect, which is not allowed by its context. The 'decides' effect indicates that the invocation calls a function that might fail, and so must occur in a failure context that will handle the failure. Some examples of failure contexts are the condition clause of an 'if', the left operand of 'or', or the clause of the 'logic' macro.
  Line 43: Verse compiler warning V2017: This container lookup is unlikely to succeed. (Did you mean to use a different key?)
  Line 43: Verse compiler error V3509: The assignment's left hand expression type `player_profile` cannot be assigned to
-->
```verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }

# Player class enum
player_class := enum<persistable>:
    Warrior
    Mage
    Archer
    Rogue

# Achievement data
achievement := struct<persistable>:
    Name:string = ""
    Completed:logic = false
    CompletedDate:int = 0  # Timestamp

# Complete player profile
player_profile := class<final><persistable>:
    Username:string = "Player"
    Level:int = 1
    Experience:int = 0
    SelectedClass:player_class = player_class.Warrior
    TotalPlayTime:float = 0.0
    Achievements:[]achievement = array{}

# Global player profiles
PlayerProfiles : weak_map(player, player_profile) = map{}

# Profile management device
profile_manager := class(creative_device):

    OnBegin<override>()<suspends>:void =
        # Initialize all players
        AllPlayers := GetPlayspace().GetPlayers()
        for (Player : AllPlayers):
            InitializeProfile(Player)

    InitializeProfile(Player : player) : void =
        if (not PlayerProfiles[Player]):
            DefaultProfile := player_profile{}
            set PlayerProfiles[Player] = DefaultProfile
```

This demonstrates how to create and manage persistable player data,
ensuring that player progress and achievements are maintained across
game sessions.
