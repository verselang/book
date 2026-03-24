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
   - **`int`** - Integer values (must fit in 64-bit signed range for persistence)
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

<!--versetest-->
<!-- 02 -->
```verse
player_class := enum<persistable>:
    Villager

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

<!--versetest-->
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

<!--versetest-->
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
            player_stats{}
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
player := class<unique>{}
player_data := class<final><persistable>:
    Level:int = 1
    Score:int = 100
PersistenceModule := module{
    ToJson<public>(Data:player_data)<decides>:string = ""
}
-->
<!-- 08 -->
```verse
# Serialize persistable data to JSON
Data := player_data{Level := 5, Score := 250}
JsonString := PersistenceModule.ToJson[Data]
# Produces: {"$package_name":"/...", "$class_name":"player_data", "x_Level":5, "x_Score":250}
```

Deserializes JSON string to typed value:

<!--versetest
player := class<unique>{}
player_data := class<final><persistable>:
    Level:int = 1
    Score:int = 100
PersistenceModule := module{
    FromJson<public>(JsonStr:string, T:type)<transacts><decides>:player_data =
        false?
        player_data{Level := 1, Score := 100}
}
-->
<!-- 09 -->
```verse
# Deserialize JSON to typed value
JsonString := ""
if (Restored := PersistenceModule.FromJson[JsonString, player_data]):
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
player := class<unique>{}
int_ref := class<final><persistable>:
    Value:int
PersistenceModule := module{
    ToJson<public>(Data:int_ref)<decides>:string = ""
}
-->
<!-- 11 -->
```verse
# Serialized as JSON number
JsonString := PersistenceModule.ToJson[int_ref{Value := 42}]
# {"$package_name":"...", "$class_name":"int_ref", "x_Value":42}
```

**Optional types:**

<!--versetest
player := class<unique>{}
optional_ref := class<final><persistable>:
    Value:?int
PersistenceModule := module{
    ToJson<public>(Data:optional_ref)<decides>:string = ""
}
-->
<!-- 12 -->
```verse
# None serialized as false
PersistenceModule.ToJson[optional_ref{Value := false}]
# {..., "x_Value":false}

# Some serialized as object with empty key
PersistenceModule.ToJson[optional_ref{Value := option{42}}]
# {..., "x_Value":{"":42}}
```

**Tuples:**

<!--versetest
player := class<unique>{}
tuple_ref := class<final><persistable>:
    Pair:tuple(int, int)
empty_tuple_ref := class<final><persistable>:
    Empty:tuple()
PersistenceModule := module{
    ToJson<public>(Data:tuple_ref):string = ""
    ToJson<public>(Data:empty_tuple_ref):string = ""
}
-->
<!-- 13 -->
```verse
# Serialized as JSON array
PersistenceModule.ToJson(tuple_ref{Pair := (4, 5)})
# {..., "x_Pair":[4,5]}

# Empty tuple
PersistenceModule.ToJson(empty_tuple_ref{Empty := ()})
# {..., "x_Empty":[]}
```

**Arrays:**
<!--versetest
player := class<unique>{}
array_ref := class<final><persistable>:
    Values:[]int
PersistenceModule := module{
    ToJson<public>(Data:array_ref)<decides>:string = ""
}
-->
<!-- 14 -->
```verse
PersistenceModule.ToJson[array_ref{Values := array{1, 2, 3}}]
# {..., "x_Values":[1,2,3]}
```

**Maps:**

<!--versetest
player := class<unique>{}
map_ref := class<final><persistable>:
    Lookup:[string]int
PersistenceModule := module{
    ToJson<public>(Data:map_ref)<decides>:string = ""
}
-->
<!-- 15 -->
```verse
PersistenceModule.ToJson[map_ref{Lookup := map{"a" => 1, "b" => 2}}]
# {..., "x_Lookup":[{"k":{"":"a"},"v":{"":1}}, {"k":{"":"b"},"v":{"":2}}]}
```

**Enums:**

<!--versetest
player := class<unique>{}
day := enum<persistable>:
    Monday
    Tuesday
enum_ref := class<final><persistable>:
    Day:day
PersistenceModule := module{
    ToJson<public>(Data:enum_ref)<decides>:string = ""
}
-->
<!-- 16 -->
```verse
PersistenceModule.ToJson[enum_ref{Day := day.Monday}]
# {..., "x_Day":"day::Monday"}
```

### Default Value Handling

When deserializing, missing fields are automatically filled with their default values:

<!--versetest
player := class<unique>{}
versioned_data := class<final><persistable>:
    Version:int = 1
    NewField:int = 0
PersistenceModule := module{
    FromJson<public>(JsonStr:string, T:type)<transacts><decides>:versioned_data =
        false?
        versioned_data{Version := 1, NewField := 0}
}
-->
<!-- 17 -->
```verse
# Old JSON without NewField
OldJson := ""

# Deserializes successfully with default for NewField
if (Data := PersistenceModule.FromJson[OldJson, versioned_data]):
    Data.Version = 1
    Data.NewField = 0  # Uses default value
```

This enables forward-compatible schema evolution - new fields with
defaults can be added without breaking old saved data.

### Block Clauses During Deserialization

Block clauses do not execute when deserializing from JSON:

<!--versetest
player := class<unique>{}
logged_class := class<final><persistable>:
    Value:int
PersistenceModule := module{
    ToJson<public>(Data:logged_class):string = ""
    FromJson<public>(JsonStr:string, T:type)<transacts>:logged_class = logged_class{Value := 1}
}
-->
<!-- 18 -->
```verse
# Normal construction triggers block
Instance1 := logged_class{Value := 1}

# Deserialization does NOT trigger block
Json := PersistenceModule.ToJson(Instance1)
Instance2 := PersistenceModule.FromJson(Json, logged_class)  # No print
```

Block clauses are only executed during normal construction, not during
deserialization. This means initialization logic in blocks won't run
for loaded data.

### Integer Range Limitations

Verse protects against integer overflow during serialization. Integers
that exceed the safe serialization range cause runtime errors:

<!--versetest
player := class<unique>{}
int_ref := class<final><persistable>:
    Value:int
PersistenceModule := module{
    ToJson<public>(Data:int_ref)<decides>:string = ""
}
-->
<!-- 19 -->
```verse
# Safe range integers work fine
SafeData := int_ref{Value := 1000000000000000000}
PersistenceModule.ToJson[SafeData]  # OK

# Very large integers may cause runtime errors during serialization
# to prevent silent precision loss
```

This prevents silent precision loss that could occur with
floating-point representation of large integers.


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
