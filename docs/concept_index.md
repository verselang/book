# 📚 Concept Index

This index provides quick access to key concepts, language features, and important terms in the Verse documentation. Each entry links to the specific subsection where the concept is defined or explained in detail.

## Type System

### Primitive Types
- **any** - universal supertype: [Primitives - Any](02_primitives.md#any), [Type System](11_types.md)
- **void** - empty type: [Primitives - Void](02_primitives.md#void), [Type System](11_types.md)
- **logic** - boolean values: [Primitives - Booleans](02_primitives.md#booleans), [Type System](11_types.md)
- **int** - integers: [Overview](00_overview.md), [Primitives - Integers](02_primitives.md#integers), [Type System](11_types.md)
- **float** - floating-point: [Overview](00_overview.md), [Primitives - Floats](02_primitives.md#floats), [Type System](11_types.md)
- **rational** - exact fractions: [Primitives - Rationals](02_primitives.md#rationals), [Operators](04_operators.md), [Type System](11_types.md)
- **char** - UTF-8 character: [Primitives - Characters and Strings](02_primitives.md#characters-and-strings), [Type System](11_types.md)
- **char32** - UTF-32 character: [Primitives - Characters and Strings](02_primitives.md#characters-and-strings), [Type System](11_types.md)
- **string** - text values: [Overview](00_overview.md), [Primitives - Characters and Strings](02_primitives.md#characters-and-strings), [Type System](11_types.md)

### Composite Types
- **array** - ordered collections: [Overview](00_overview.md), [Containers - Arrays](03_containers.md#arrays), [Type System](11_types.md)
- **map** - key-value pairs: [Containers - Maps](03_containers.md#maps), [Type System](11_types.md)
- **tuple** - fixed-size collections: [Containers - Tuple](03_containers.md#tuple), [Expressions](01_expressions.md), [Type System](11_types.md)
- **option** - nullable values: [Overview](00_overview.md), [Containers - Optionals](03_containers.md#optionals), [Type System](11_types.md)
- **class** - reference types: [Overview](00_overview.md), [Classes - Classes](10_classes_interfaces.md#classes), [Type System](11_types.md)
- **struct** - value types: [Structs - Structs](09_structs_enums.md#structs), [Type System](11_types.md)
- **interface** - contracts: [Classes - Interfaces](10_classes_interfaces.md#interfaces), [Type System](11_types.md)
- **enum** - named values: [Overview](00_overview.md), [Enums - Enums](09_structs_enums.md#enums)

### Type Features
- **subtyping** - type relationships: [Type System - Understanding Subtyping](11_types.md#understanding-subtyping)
- **comparable** - equality testing: [Type System](11_types.md)
- **parametric types** - generics: [Classes - Parametric Classes](10_classes_interfaces.md#parametric-classes), [Type System](11_types.md)
- **type{}** - type expressions: [Expressions](01_expressions.md), [Primitives - Type type](02_primitives.md#type-type), [Type System](11_types.md)
- **where clauses** - type constraints: [Overview](00_overview.md), [Functions](06_functions.md), [Classes - Parameter Constraints](10_classes_interfaces.md#parameter-constraints), [Type System](11_types.md)

### Type Variance
- **covariance** - type compatibility: [Classes - Covariant](10_classes_interfaces.md#covariant), [Type System - Covariance](11_types.md#covariance)
- **contravariance** - reverse compatibility: [Type System](11_types.md)
- **invariance** - exact type match: [Type System](11_types.md)
- **bivariance** - both directions: [Type System](11_types.md)

### Type Casting
- **casting** - type conversion: [Type System - Class and Interface Casting](11_types.md#class-and-interface-casting)
- **dynamic casts** - runtime type checking: [Type System - Dynamic Type-Based Casting](11_types.md#dynamic-type-based-casting)
- **fallible casts** - casts that may fail: [Type System - Fallible Casts](11_types.md#fallible-casts)

### Type Predicates and Metatypes
- **subtype** - runtime type values: [Type System - subtype](11_types.md#subtype)
- **concrete_subtype** - instantiable types: [Type System - concrete_subtype](11_types.md#concrete_subtype)
- **castable_subtype** - castable relationship: [Type System - castable_subtype](11_types.md#castable_subtype), [Classes - Using castable_subtype](10_classes_interfaces.md#using-castable_subtype)
- **classifiable_subset** - type set tracking: [Type System - classifiable_subset](11_types.md#classifiable_subset)
- **classifiable_subset_var** - mutable type set: [Type System - classifiable_subset](11_types.md#classifiable_subset)
- **classifiable_subset_key** - type set keys: [Type System - classifiable_subset](11_types.md#classifiable_subset)

### Type Query Functions
- **GetCastableFinalSuperClass** - get cast root from instance: [Type System - GetCastableFinalSuperClass](11_types.md#getcastablefinalsuperclass)
- **GetCastableFinalSuperClassFromType** - get cast root from type: [Type System - GetCastableFinalSuperClassFromType](11_types.md#getcastablefinalsuperclassfromtype)
- **MakeClassifiableSubset** - create immutable type set: [Type System - classifiable_subset](11_types.md#classifiable_subset)
- **MakeClassifiableSubsetVar** - create mutable type set: [Type System - classifiable_subset](11_types.md#classifiable_subset)

## Effects

### Effect Specifiers
- **`<computes>`** - pure computation: [Overview](00_overview.md), [Effects](13_effects.md), [Mutability](05_mutability.md)
- **`<reads>`** - observe state: [Overview](00_overview.md), [Effects](13_effects.md), [Mutability](05_mutability.md)
- **`<writes>`** - modify state: [Effects](13_effects.md), [Mutability](05_mutability.md)
- **`<allocates>`** - create unique values: [Effects](13_effects.md)
- **`<transacts>`** - full heap access: [Overview](00_overview.md), [Classes - Classes](10_classes_interfaces.md#classes), [Effects](13_effects.md)
- **`<decides>`** - can fail: [Overview](00_overview.md), [Functions](06_functions.md), [Failure](08_failure.md), [Effects](13_effects.md)
- **`<suspends>`** - async execution: [Overview](00_overview.md), [Effects](13_effects.md), [Concurrency](14_concurrency.md)
- **`<converges>`** - guaranteed termination: [Effects](13_effects.md)
- **`<diverges>`** - may not terminate: [Effects](13_effects.md)
- **`<predicts>`** - client execution: [Effects](13_effects.md)
- **`<dictates>`** - server-only: [Effects](13_effects.md)

## Control Flow

### Basic Control
- **if/then/else** - conditional execution: [Overview](00_overview.md), [Expressions](01_expressions.md), [Control Flow](07_control.md), [Failure](08_failure.md)
- **case** - pattern matching: [Overview](00_overview.md), [Enums - Using Enums](09_structs_enums.md#using-enums), [Control Flow](07_control.md)
- **for** - iteration: [Overview](00_overview.md), [Control Flow](07_control.md), [Failure](08_failure.md)
- **loop** - infinite loops: [Control Flow](07_control.md), [Failure](08_failure.md), [Concurrency](14_concurrency.md)
- **block** - statement sequences: [Control Flow](07_control.md), [Failure](08_failure.md), [Classes - Blocks for Initialization](10_classes_interfaces.md#blocks-for-initialization), [Concurrency](14_concurrency.md)
- **break** - exit loops: [Control Flow](07_control.md)
- **continue** - skip iteration: [Control Flow](07_control.md)
- **defer** - cleanup code: [Control Flow](07_control.md)
- **return** - exit functions: [Functions](06_functions.md)

### Failure System
- **failure** - control through failure: [Overview](00_overview.md), [Failure](08_failure.md), [Effects](13_effects.md)
- **failable expressions** - can fail: [Containers - Optionals](03_containers.md#optionals), [Functions](06_functions.md), [Failure](08_failure.md)
- **query operator (?)** - test values: [Overview](00_overview.md), [Containers - Optionals](03_containers.md#optionals), [Operators](04_operators.md), [Failure](08_failure.md)
- **speculative execution** - rollback on failure: [Overview](00_overview.md), [Failure](08_failure.md)

## Concurrency

### Structured Concurrency
- **sync** - wait for all: [Overview](00_overview.md), [Concurrency](14_concurrency.md)
- **race** - first to complete: [Overview](00_overview.md), [Concurrency](14_concurrency.md)
- **rush** - first to succeed: [Concurrency](14_concurrency.md)
- **branch** - all that succeed: [Concurrency](14_concurrency.md)

### Unstructured Concurrency
- **spawn** - independent tasks: [Overview](00_overview.md), [Effects](13_effects.md), [Concurrency](14_concurrency.md)
- **task** - concurrent execution: [Concurrency](14_concurrency.md)
- **async expressions** - time-taking operations: [Concurrency](14_concurrency.md)
- **cancellation** - stopping tasks: [Concurrency](14_concurrency.md)

### Timing Functions
- **Sleep()** - pause execution: [Concurrency](14_concurrency.md)
- **Await()** - suspend for task completion: [Concurrency](14_concurrency.md)
- **NextTick()** - defer to next update: [Concurrency](14_concurrency.md)
- **GetSecondsSinceEpoch** - get current time: [Concurrency](14_concurrency.md)

## Live Variables

### Reactive Programming
- **live** - reactive variables: [Live Variables](15_live_variables.md)
- **await** - suspend until condition: [Live Variables - The await Expression](15_live_variables.md#the-await-expression)
- **upon** - one-shot reactive behavior: [Live Variables - The upon Expression](15_live_variables.md#the-upon-expression)
- **when** - continuous reactive behavior: [Live Variables - The when Expression](15_live_variables.md#the-when-expression)
- **batch** - group variable updates: [Live Variables - The batch Expression](15_live_variables.md#the-batch-expression)
- **Old()** - access previous value: [Live Variables - Recursive Targets](15_live_variables.md#recursive-targets)

### Live Variable Features
- **input-output variables** - bidirectional sync: [Live Variables - Input-Output Variables](15_live_variables.md#input-output-variables)
- **live expressions** - dynamic relationships: [Live Variables - Live Expressions](15_live_variables.md#live-expressions)

## Mutability

### Mutation Control
- **var** - mutable variables: [Mutability](05_mutability.md), [Effects](13_effects.md)
- **set** - assignment: [Overview](00_overview.md), [Mutability](05_mutability.md)
- **immutability** - default behavior: [Overview](00_overview.md), [Effects](13_effects.md), [Mutability](05_mutability.md)
- **deep copying** - struct semantics: [Mutability](05_mutability.md), [Structs - Structs](09_structs_enums.md#structs)
- **reference semantics** - class behavior: [Classes - Classes](10_classes_interfaces.md#classes), [Mutability](05_mutability.md)
- **value semantics** - struct behavior: [Structs - Structs](09_structs_enums.md#structs), [Mutability](05_mutability.md)

## Class & Type Specifiers

### Structure Specifiers
- **`<unique>`** - identity equality: [Overview](00_overview.md), [Classes - Unique](10_classes_interfaces.md#unique), [Mutability](05_mutability.md), [Access Specifiers](12_access.md)
- **`<abstract>`** - cannot instantiate: [Classes - Abstract](10_classes_interfaces.md#abstract), [Access Specifiers](12_access.md)
- **`<concrete>`** - can instantiate: [Classes - Concrete](10_classes_interfaces.md#concrete), [Access Specifiers](12_access.md)
- **`<final>`** - cannot inherit: [Classes - Final](10_classes_interfaces.md#final), [Persistable Types](17_persistable.md), [Access Specifiers](12_access.md)
- **`<final_super>`** - terminal inheritance: [Classes - Final](10_classes_interfaces.md#final), [Access Specifiers](12_access.md)
- **`<final_super_base>`** - inheritance root: [Classes - Final](10_classes_interfaces.md#final)
- **`<castable>`** - runtime type checking: [Classes - Castable](10_classes_interfaces.md#castable), [Access Specifiers](12_access.md), [Code Evolution](18_evolution.md)
- **`<persistable>`** - saveable data: [Overview](00_overview.md), [Classes - Persistable](10_classes_interfaces.md#persistable), [Structs - Persistable Structs](09_structs_enums.md#persistable-structs), [Persistable Types](17_persistable.md)
- **`<constructor>`** - factory methods: [Classes - Constructor Functions](10_classes_interfaces.md#constructor-functions)

### Enum Specifiers
- **`<open>`** - extensible enums: [Enums - Open vs Closed Enums](09_structs_enums.md#open-vs-closed-enums), [Access Specifiers](12_access.md), [Code Evolution](18_evolution.md)
- **`<closed>`** - fixed enums: [Enums - Open vs Closed Enums](09_structs_enums.md#open-vs-closed-enums), [Access Specifiers](12_access.md), [Code Evolution](18_evolution.md)

## Access Control

### Visibility Specifiers
- **`<public>`** - universal access: [Overview](00_overview.md), [Classes - Access Specifiers](10_classes_interfaces.md#access-specifiers), [Modules and Paths](16_modules.md), [Access Specifiers](12_access.md)
- **`<private>`** - class/module only: [Classes - Access Specifiers](10_classes_interfaces.md#access-specifiers), [Modules and Paths](16_modules.md), [Access Specifiers](12_access.md)
- **`<protected>`** - subclass access: [Classes - Access Specifiers](10_classes_interfaces.md#access-specifiers), [Modules and Paths](16_modules.md), [Access Specifiers](12_access.md)
- **`<internal>`** - module access: [Modules and Paths](16_modules.md), [Access Specifiers](12_access.md)
- **`<scoped>`** - path-based access: [Access Specifiers](12_access.md)

### Method Specifiers
- **`<override>`** - replace parent method: [Classes - Method Overriding](10_classes_interfaces.md#method-overriding), [Access Specifiers](12_access.md)
- **`<native>`** - implemented in C++: [Access Specifiers](12_access.md)

## Operators

### Arithmetic
- **+, -, \*, /, %** - math operations: [Primitives - Mathematical Functions](02_primitives.md#mathematical-functions), [Operators](04_operators.md)
- **+=, -=, \*=, /=** - compound assignment: [Operators](04_operators.md)

### Comparison
- **<, <=, >, >=** - ordering: [Operators](04_operators.md)
- **=, <>** - equality/inequality: [Operators](04_operators.md), [Type System](11_types.md)

### Logical
- **and** - logical AND: [Operators](04_operators.md), [Failure](08_failure.md)
- **or** - logical OR: [Operators](04_operators.md), [Failure](08_failure.md)
- **not** - logical NOT: [Operators](04_operators.md), [Failure](08_failure.md)

### Access
- **.** - member access: [Operators](04_operators.md), [Expressions](01_expressions.md)
- **[]** - indexing: [Containers - Arrays](03_containers.md#arrays), [Operators](04_operators.md), [Expressions](01_expressions.md)
- **()** - function call: [Operators](04_operators.md), [Expressions](01_expressions.md)
- **{}** - object construction: [Operators](04_operators.md), [Expressions](01_expressions.md)

### Special
- **:=** - initialization: [Operators](04_operators.md), [Expressions](01_expressions.md)
- **..** - range operator: [Operators](04_operators.md), [Expressions](01_expressions.md)
- **?** - query operator: [Overview](00_overview.md), [Containers - Optionals](03_containers.md#optionals), [Operators](04_operators.md), [Failure](08_failure.md)

## Functions

### Function Features
- **parameters** - function inputs: [Functions](06_functions.md)
- **named arguments** - explicit parameter names: [Functions](06_functions.md)
- **return values** - function outputs: [Functions](06_functions.md)
- **function types** - function signatures: [Functions](06_functions.md), [Type System](11_types.md)
- **overloading** - multiple definitions: [Functions](06_functions.md), [Operators](04_operators.md)
- **lambdas** - anonymous functions (not yet supported, use nested functions): [Functions](06_functions.md), [Expressions](01_expressions.md)
- **nested functions** - local function definitions: [Functions](06_functions.md)
- **higher-order functions** - functions as values: [Overview](00_overview.md), [Functions](06_functions.md)

## Modules & Organization

### Module System
- **module** - code organization: [Modules and Paths](16_modules.md)
- **using** - import statements: [Overview](00_overview.md), [Modules and Paths](16_modules.md)
- **module paths** - hierarchical names: [Modules and Paths](16_modules.md)
- **qualified names** - full paths: [Modules and Paths](16_modules.md)
- **qualified access** - explicit paths: [Modules and Paths](16_modules.md)
- **nested modules** - module hierarchy: [Modules and Paths](16_modules.md)

## Persistence

### Save System
- **weak_map(player, t)** - player data: [Containers - Weak Maps](03_containers.md#weak-maps), [Persistable Types](17_persistable.md)
- **weak_map(session, t)** - session data: [Containers - Weak Maps](03_containers.md#weak-maps), [Persistable Types](17_persistable.md)
- **persistable types** - saveable data: [Overview](00_overview.md), [Classes - Persistable](10_classes_interfaces.md#persistable), [Structs - Persistable Structs](09_structs_enums.md#persistable-structs), [Persistable Types](17_persistable.md)
- **module-scoped variables** - persistent storage: [Modules and Paths](16_modules.md), [Persistable Types](17_persistable.md)

## Evolution & Compatibility

### Version Management
- **backward compatibility** - preserving APIs: [Overview](00_overview.md), [Effects](13_effects.md), [Code Evolution](18_evolution.md)
- **versioning** - tracking changes: [Code Evolution](18_evolution.md)
- **deprecation** - phasing out features: [Code Evolution](18_evolution.md)
- **publication** - making code public: [Modules and Paths](16_modules.md), [Access Specifiers](12_access.md), [Code Evolution](18_evolution.md)
- **breaking changes** - incompatible updates: [Code Evolution](18_evolution.md)
- **schema evolution** - data structure changes: [Classes - Classes](10_classes_interfaces.md#classes), [Code Evolution](18_evolution.md)

### Annotations
- **@deprecated** - mark as deprecated: [Code Evolution](18_evolution.md)
- **@experimental** - mark as experimental: [Code Evolution](18_evolution.md)
- **@available** - version availability: [Code Evolution](18_evolution.md)

## Built-in Functions

### Math Functions
- **Abs()** - absolute value: [Primitives - Mathematical Functions](02_primitives.md#mathematical-functions)
- **Floor()** - round down: [Primitives - Mathematical Functions](02_primitives.md#mathematical-functions)
- **Ceil()** - round up: [Primitives - Mathematical Functions](02_primitives.md#mathematical-functions)
- **Round()** - round to nearest: [Primitives - Mathematical Functions](02_primitives.md#mathematical-functions)
- **Sqrt()** - square root: [Primitives - Mathematical Functions](02_primitives.md#mathematical-functions)
- **Min()** - minimum value: [Primitives - Mathematical Functions](02_primitives.md#mathematical-functions)
- **Max()** - maximum value: [Primitives - Mathematical Functions](02_primitives.md#mathematical-functions)

### Utility Functions
- **Print()** - output text: [Overview](00_overview.md), [Effects](13_effects.md)
- **ToString()** - convert to string: [Primitives - ToString()](02_primitives.md#tostring)
- **GetSession()** - current session: [Modules and Paths](16_modules.md)

### Array Methods
- **Find()** - find element index: [Containers - Array Methods](03_containers.md#array-methods)
- **Remove()** - remove by index: [Containers - Array Methods](03_containers.md#array-methods)
- **RemoveFirstElement()** - remove first occurrence: [Containers - Array Methods](03_containers.md#array-methods)
- **RemoveAllElements()** - remove all occurrences: [Containers - Array Methods](03_containers.md#array-methods)
- **ReplaceElement()** - replace by index: [Containers - Array Methods](03_containers.md#array-methods)
- **ReplaceFirstElement()** - replace first occurrence: [Containers - Array Methods](03_containers.md#array-methods)
- **ReplaceAllElements()** - replace all occurrences: [Containers - Array Methods](03_containers.md#array-methods)
- **ReplaceAll()** - pattern-based replacement: [Containers - Array Methods](03_containers.md#array-methods)

## Syntax Elements

### Literals
- **integer literals** - whole number values: [Expressions](01_expressions.md)
- **float literals** - decimal values: [Expressions](01_expressions.md)
- **string literals** - text values: [Expressions](01_expressions.md)
- **character literals** - single characters: [Expressions](01_expressions.md)
- **boolean literals** - true/false: [Expressions](01_expressions.md)

### Special Values
- **false** - failure value, empty optional: [Primitives - Booleans](02_primitives.md#booleans), [Containers - Optionals](03_containers.md#optionals), [Failure](08_failure.md)
- **true** - success value: [Primitives - Booleans](02_primitives.md#booleans)
- **NaN** - not a number: [Primitives - Floats](02_primitives.md#floats)
- **Inf** - infinity: [Primitives - Floats](02_primitives.md#floats)

### Language Constructs
- **comments** - code documentation: [Overview](00_overview.md)
- **identifiers** - names: [Expressions](01_expressions.md)

## Special Concepts

### Language Features
- **archetype expression** - prototype patterns: [Classes - Object Construction](10_classes_interfaces.md#object-construction), [Expressions](01_expressions.md)
- **string interpolation** - embedded expressions: [Primitives - Characters and Strings](02_primitives.md#characters-and-strings)
- **pattern matching** - structural matching: [Overview](00_overview.md), [Enums - Using Enums](09_structs_enums.md#using-enums), [Control Flow](07_control.md)
- **inheritance** - class hierarchy: [Classes - Inheritance](10_classes_interfaces.md#inheritance), [Type System](11_types.md), [Access Specifiers](12_access.md)
- **polymorphism** - multiple forms: [Classes - Method Overriding](10_classes_interfaces.md#method-overriding), [Type System](11_types.md)
- **transactional semantics** - rollback behavior: [Overview](00_overview.md), [Failure](08_failure.md), [Effects](13_effects.md)
- **option{}** constructor: [Overview](00_overview.md), [Containers - Optionals](03_containers.md#optionals)
- **array{}** constructor: [Overview](00_overview.md), [Containers - Arrays](03_containers.md#arrays)
- **map{}** constructor: [Containers - Maps](03_containers.md#maps)

---

*Note: This index covers all major concepts in the Verse documentation. Each entry links directly to the subsection where the concept is defined or explained in detail. Use your browser's search function (Ctrl+F or Cmd+F) to quickly find specific terms.*
