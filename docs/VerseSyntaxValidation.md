Use this to test and validate syntax highlighting

#### Basics
<!--NoCompile-->
<!-- 01 -->
```verse
<# Class #>
Component := class<final_super>(component) {
    @editable Text:string = "Hello";

    OnBeginSimulation<override>():void = {
        Print("{Self.Text}Verse");
    };
};

<# Enum #>
EAnchor := enum {
    Top,
    Right,
    Bottom,
    Left
};

<# Block #>
block {
    Print("{Self.Text}Verse");
};

block { Print("{Self.Text}Verse"); };

<# Comments #>
Damage := 100 * 1.5  # Apply critical hit multiplier
Result := BaseValue <# original amount #> * Multiplier <# scaling factor #> + Bonus
Text := "abc<#comment#>def"     # Comments in strings are allowed
<# Temporarily disabled for testing
   OriginalFunction()  <# This had a bug #>
   NewFunction()       # Testing this approach
#>
<#>
    This entire block is a comment because it's indented.
    It provides a clean way to write longer documentation
    without cluttering each line with comment markers.

DoSomething()  # Not part of the comment.
```

## Real life examples
<!--NoCompile-->
<!-- 02 -->
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
game_item := class<final><persistable>:
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
            _ => false  # Fails if the item is legenday or unexpected
    
    # Computed property using closed-world function
    GetEffectiveValue()<transacts><decides> :int=
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
    FilterItems(Predicate:type{_(:game_item)<decides>:void} ) :[]game_item =
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

<!--NoCompile-->
<!-- 03 -->
```verse
WaypointComponent<public> := class<final_super><abstract>(component) {
    @editable Index:int = 0;

    EditorOnlySessionEnvironmentAllowList:[]session_environment = array{};

    MeshComponent<protected>:castable_subtype((/Verse.org:)SceneGraph.mesh_component) = (/Verse.org:)SceneGraph.mesh_component;

    GetBounds<public>():vector3;

    OnBeginSimulation<override>():void = {
        Self.Entity.GetComponent[Self.MeshComponent] or Err("Invalid SceneGraph.mesh_component");
    };
};
```

### Inline Text Example
The example begins with Verse's rich type system. Types flow naturally through the code; many type annotations are omitted as they can be infered. When we do specify types, like `Items:[]game_item`, they document intent rather than just satisfy the compiler. The `item_rarity` enum provides type-safe constants without the boilerplate of traditional enumerations. The `item_stats` struct marked as `<persistable>` can be saved and loaded from persistent storage, essential for game saves. The `game_item` class uses `<unique>` to ensure reference equality semantics.

### UnrealEngine.digest.verse (Simplified)
<!--NoCompile-->
<!-- 04 -->
```verse
# Copyright Epic Games, Inc. All Rights Reserved.
#################################################
# Generated Digest of Verse API
# DO NOT modify this manually!
# Generated from build: ++Fortnite+Release-39.30-CL-50141518
#################################################

Itemization<public> := module:
    using {/Verse.org/Assets}
    using {/Verse.org/Presentation}
    using {/Verse.org/Simulation}
    using {/Verse.org/Native}
    using {/Verse.org/SceneGraph}
    @experimental
    add_item_result<native><public> := class<epic_internal>:
        # Items that were newly added to this inventory as a result of the transaction.
        AddedItems<native><public>:[]entity

        # Items whose stack size changed as a result of the transaction, and the previous stack size value.
        ModifiedItems<native><public>:[]tuple(entity, int)

    @experimental
    equip_item_result<native><public> := class<epic_internal>:
        Item<native><public>:entity

    @experimental
    # When adding an item, 'find_inventory_event' is used as a first pass to find the best inventory for an item. It is sent downwards.
    # 'add_item_query_event' can be used to veto inventory choices. It is sent upwards.
    find_inventory_event<native><public> := class<epic_internal>(scene_event):
        ItemComponent<native><public>:item_component

        var ChosenInventory<native><public>:?inventory_component = external {}

        var ChosenInventoryPriority<native><public>:float = external {}

    @available {MinUploadedAtFNVersion := 3800}
    @experimental
    (Item:item_component).CanEquip<native><public>()<transacts>:result(false, []equip_item_error)

WebAPI<public> := module:
    # Usage:
    #     Licensed users create a derived version of `client_id` in their module.
    #     The Verse class path for your derived `client_id` is then used as the 
    #     configuration key in your backend service to map to your endpoint.
    # 
    #     WARNING: do not make your derived `client_id` class public. This object
    #     type is your private key to your backend.
    # 
    # Example:
    #     my_client_id<internal> := class<final><computes>(client_id)
    #     MyClient<internal> := MakeClient(my_client_id)
    client_id<native><public> := class<abstract><computes>:

    client<native><public> := class<final><computes><internal>:
        Get<native><public>(Path:string)<suspends>:response

    response<native><public> := class<internal>:

    body_response<native><public> := class<internal>(response):
        GetBody<native><public>()<computes>:string

    MakeClient<native><public>(ClientId:client_id)<converges>:client

# Module import path: /UnrealEngine.com/SceneGraph
(/UnrealEngine.com:)SceneGraph<public> := module:
    using {/Verse.org/Native}
Temporary<public> := module:
    # Module import path: /UnrealEngine.com/Temporary/UI
    UI<public> := module:
        using {/Verse.org/Assets}
        using {/Verse.org/Colors}
        using {/UnrealEngine.com/Temporary/SpatialMath}
        using {/Verse.org/Simulation}
        # Returns the `player_ui` associated with `Player`.
        # Fails if there is no `player_ui` associated with `Player`.
        GetPlayerUI<native><public>(Player:player)<transacts><decides>:player_ui

        # Text justification values:
        #   Left: Justify the text logically to the left based on current culture.
        #   Center: Justify the text in the center.
        #   Right: Justify the text logically to the right based on current culture.
        # The Left and Right value will flip when the local culture is right-to-left.
        text_justification<native><public> := enum:
            Left
            Center
            Right
            InvariantLeft
            InvariantRight

        # Base widget for text widget.
        text_base<native><public> := class<abstract>(widget):
            # Sets the opacity of the displayed text.
            SetTextOpacity<native><public>(InOpacity:type {_X:float where 0.000000 <= _X, _X <= 1.000000}):void

            # Gets the opacity of the displayed text.
            GetTextOpacity<native><public>():type {_X:float where 0.000000 <= _X, _X <= 1.000000}

    # Module import path: /UnrealEngine.com/Temporary/SpatialMath
    (/UnrealEngine.com/Temporary:)SpatialMath<public> := module:
        using {/Verse.org/SpatialMath}
        using {/Verse.org/Native}
        using {/Verse.org/Simulation}
        @editable
        @import_as("/Script/EpicGamesTemporary.FVerseRotation_Deprecated")
        (/UnrealEngine.com/Temporary/SpatialMath:)rotation<native><public> := struct<concrete>:

        @vm_no_effect_token
        # Makes a `rotation` by applying `YawRightDegrees`, `PitchUpDegrees`, and `RollClockwiseDegrees`, in that order:
        #  * first a *yaw* about the Z axis with a positive angle indicating a clockwise rotation when viewed from above,
        #  * then a *pitch* about the new Y axis with a positive angle indicating 'nose up',
        #  * followed by a *roll* about the new X axis axis with a positive angle indicating a clockwise rotation when viewed along +X.
        # Note that these conventions differ from `MakeRotation` but match `ApplyYaw`, `ApplyPitch`, and `ApplyRoll`.
        (/UnrealEngine.com/Temporary/SpatialMath:)MakeRotationFromYawPitchRollDegrees<native><public>(YawRightDegrees:float, PitchUpDegrees:float, RollClockwiseDegrees:float)<reads><converges>:(/UnrealEngine.com/Temporary/SpatialMath:)rotation

JSON<public> := module:
    value<native><public> := class:
        # Retrieve an object value or fail if value is not a json object
        AsObject<native><public>()<transacts><decides>:[string]value

    # Parse a JSON string returning a value with its contents
    Parse<native><public>(JSONString:string)<transacts><decides>:value

# Module import path: /UnrealEngine.com/ControlInput
ControlInput<public> := module:
    using {/Verse.org/Assets}
    using {/Verse.org/Native}
    using {/Verse.org/Simulation}
    @available {MinUploadedAtFNVersion := 3630}
    # Input_events is a container for user input events which can be subscribed to.
    #   * Use the 'GetPlayerInput' and 'GetInputEvents' functions to retrieve an input_events object for a given player.
    #   * Low-level notifications of current user input: DetectionBeginEvent, DetectionOngoingEvent, and DetectionEndEvent.
    #   * High-level notifications of triggered events: ActivationTriggeredEvent and ActivationCanceledEvent.
    # 
    #                         /—----------<-------\ 
    #  DetectionBeginEvent -> DetectionOngoingEvent -> ActivationTriggeredEvent -> DetectionEndEvent 
    #            /\                         /\                                            / 
    #              \---------------------> ActivationCanceledEvent ----------------------/
    input_events<native><public>(t:type) := class<epic_internal>:
        (/UnrealEngine.com/ControlInput/input_events:)ControlInput_input_events_Variance<private>:?type {_():tuple(t)} = external {}

        # This input has met all required conditions and has successfully fired. Most of the time, you should bind to this event.
        #  Tuple payload: 0: the player generating this event
        #                 1: the value generated by the physical input
        ActivationTriggeredEvent<native><public>:listenable(tuple(player, t)) = external {}

    @available {MinUploadedAtFNVersion := 3630}
    # This is the main manager class for input-related settings and functions for a player.
    player_input<native><public> := class:
        GetInputEvents<native><public>(ActionToBind:input_action(t) where t:type):input_events(t)

# Module import path: /UnrealEngine.com/BasicShapes
BasicShapes<public> := module:
    using {/Verse.org/SceneGraph}

    sphere<public> := class<final><public>(mesh_component):

# Module import path: /UnrealEngine.com/Assets
(/UnrealEngine.com:)Assets<public> := module:
    using {/Verse.org/SpatialMath}
    using {/UnrealEngine.com/Temporary/SpatialMath}
    using {/Verse.org/Assets}
    SpawnParticleSystem<native><public>(Asset:particle_system, Position:(/UnrealEngine.com/Temporary/SpatialMath:)vector3, ?Rotation:(/UnrealEngine.com/Temporary/SpatialMath:)rotation = external {}, ?StartDelay:float = external {})<transacts>:cancelable

    SpawnParticleSystem<native><public>(Asset:particle_system, Position:(/Verse.org/SpatialMath:)vector3, ?Rotation:(/Verse.org/SpatialMath:)rotation = external {}, ?StartDelay:float = external {})<transacts>:cancelable
```