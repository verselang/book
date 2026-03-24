# Verse Language Documentation

!!! warning
    This is an early draft of the Book of Verse. Suggestions
    for improvements are welcome. Frequent updates are to be expected.

This documentation provides an in-depth look at the Verse programming
language, its philosophy, and core concepts.

Verse is a multi-paradigm programming language developed by Epic
Games, drawing from functional, logic, and imperative traditions to
create a coherent system for building metaverse experiences.


Verse has three core principles:

- **It's just code** - Complex concepts are expressed as primitive Verse constructs
- **Just one language** - Same constructs for compile-time and run-time
- **Metaverse first** - Designed for a global simulation environment

!!! note
      The documentation pertains to the head of the main
      development branch of Verse, some features may be discussed
      before they are officially released and are thus subject to
      change. Some Epic internal features may also be discussed.


## Documentation Sections

- [Overview](00_overview.md) - Introduction to Verse philosophy and features
- [Expressions](01_expressions.md) - Everything is an expression paradigm
- [Primitives](02_primitives.md) - Integers, floats, rationals, logic, strings, and special types
- [Containers](03_containers.md) - Optionals, tuples, arrays, maps, and weak maps
- [Operators](04_operators.md) - Arithmetic, comparison, logical, and assignment operators with precedence
- [Mutability](05_mutability.md) - Mutable variables, references, and state management
- [Functions](06_functions.md) - Open-world vs closed-world functions, parameters, and return values
- [Control Flow](07_control.md) - If/else, loops, code blocks, and comments
- [Failure System](08_failure.md) - First-class failure, failable expressions, and speculative execution
- [Structs & Enums](09_structs_enums.md) - Value types and fixed sets of named values
- [Classes & Interfaces](10_classes_interfaces.md) - Object-oriented programming with inheritance and contracts
- [Type System](11_types.md) - Types as functions and type checking
- [Access Specifiers](12_access.md) - Public, private, and protected visibility
- [Effects](13_effects.md) - Effect families, specifiers, and capability declarations
- [Concurrency](14_concurrency.md) - Structured concurrency with sync, race, rush, branch, and spawn
- [Live Variables](15_live_variables.md) - Reactive values that automatically update
- [Modules & Paths](16_modules.md) - Code organization and the global namespace
- [Persistable Types](17_persistable.md) - Types that can be saved and loaded
- [Code Evolution](18_evolution.md) - Versioning and backward compatibility
