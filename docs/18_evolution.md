# Verse Code Evolution and Compatibility

Verse takes a unique approach to code evolution, designed with the ambitious goal of creating software that could remain functional and valuable for decades or even centuries. This vision stems from Verse's role as the programming language for a persistent, global metaverse where code must coexist, evolve, and maintain compatibility across vast timescales.

At its core, Verse embraces three fundamental principles that shape how code evolves: future-proof design that avoids being rooted in past artifacts of other languages, a metaverse-first approach where code persistence and compatibility are critical, and strong static verification that catches runtime problems at compile time. These principles create a foundation for a language that can grow and adapt while maintaining the stability required for a global, persistent codebase.

## The Nature of Code Publication

When developers publish code to the Verse metaverse, they enter into a social contract with all future users of that code. This contract is more than just a convention—it's enforced by the language itself. Consider what happens when you publish a simple value:

<!-- 01 -->
```verse
Thing<public>:int = 666
```

This seemingly straightforward declaration carries profound implications. By marking `Thing` as public, you're making a commitment that extends indefinitely into the future. Users can depend on `Thing` always existing and always being an integer. While you retain the freedom to change its actual value, the existence and type of `Thing` become permanent fixtures in the metaverse's landscape.

This permanence extends beyond simple values to encompass the entire structure of published code. Persistable structs, once published to an island, become immutable schemas that cannot be altered. Closed enums remain closed forever, unable to accept new values after publication. When a class or interface is marked with the `<castable>` attribute, that decision becomes irreversible, as changing it could introduce unsafe casting behaviors that break existing code.

The publication model distinguishes between two contexts: the live metaverse and islands. In the envisioned live metaverse, publishing an update that attempts to change an immutable variable's value has no effect—the variable already exists with its original value. However, in the current island-based implementation, new instances of an island will adopt the updated value, providing a practical migration path while maintaining conceptual consistency.

## The Architecture of Backward Compatibility

Backward compatibility in Verse goes beyond simple syntactic preservation—it encompasses semantic guarantees about how code behaves. The language enforces these guarantees through multiple mechanisms that work together to create a robust compatibility framework.

Function effects exemplify this approach. When a function is published with specific effects like `<reads>`, indicating it may read mutable heap data, this becomes part of its contract. Future versions of the function can have fewer effects—evolving from `<reads>` to `<computes>`—but never more. This restriction ensures that code depending on the function's effect profile continues to work correctly, as the function only becomes more pure, never less.

Type evolution follows similar principles. Types can become more specific over time, such as changing from `rational` to `int`, as this represents a refinement rather than a fundamental change. Structures must maintain all existing fields, though new fields can be added. Classes marked with `<final_super>` commit to their inheritance hierarchy permanently, ensuring that code relying on specific inheritance relationships remains valid.

The enforcement of these rules happens at publication time, not just at compile time. Verse actively prevents developers from publishing updates that would violate compatibility guarantees, turning what might be runtime failures in other systems into publication-time errors that must be resolved before code can be deployed.

## Managing Breaking Changes

Despite the strong emphasis on compatibility, Verse recognizes that some breaking changes are occasionally necessary. The language provides two mechanisms for managing such changes: a deprecation system for gradual migration and special privileges for essential breaking changes.

The deprecation system operates as a multi-phase process that gives developers ample time to adapt. When code patterns become deprecated, they first generate warnings rather than errors. These warnings appear when saving code, alerting developers to practices that won't be supported in future versions. The code continues to compile and run, allowing projects to function while migration plans are developed. Only when developers explicitly upgrade to a new language version do deprecations become errors, and even then, the option to remain on older versions provides an escape hatch.

Version 1 introduced several significant deprecations that illustrate this process. The prohibition of failure in set expressions, which previously allowed with warnings, now requires explicit handling of failable expressions. Mixed separator syntax, which created implicit blocks and confusing scoping rules, must now use consistent separation. The introduction of local qualifiers provides a new tool for disambiguating identifiers while deprecating the use of 'local' as a regular identifier name.

For truly exceptional circumstances, Epic Games and potentially other future authorities retain "superpowers" to make breaking changes outside the normal compatibility framework. These powers include the ability to delete published entities, change types in non-backward-compatible ways, and rewrite modules for legal or safety reasons. These capabilities acknowledge that being good stewards of the metaverse namespace sometimes requires violating the usual compatibility rules, though such actions should remain rare and justified by compelling reasons.

## Catalog of Compatibility Rules

When you publish code in Verse, many aspects of your definitions become permanent commitments. Understanding exactly what can and cannot change is essential for designing APIs that can evolve gracefully. This catalog documents both the changes that Verse prohibits and the changes it allows to ensure backward compatibility.

The rules follow a general principle: changes that make types more specific (narrowing), add new capabilities, or relax restrictions are often allowed, while changes that make types more general (widening), remove capabilities, or impose new restrictions are typically forbidden. However, the rules vary significantly between final/non-instance members and non-final instance members, with the latter having much stricter requirements.

### Definitions

**Cannot remove public definitions.** Once a public variable, function, class, or other definition is published, it must remain available. Removing it would break any code that depends on it.

**Cannot change the kind of a definition.** A class cannot become a struct, interface, enum, or function. A function cannot become a class or type alias. These fundamental changes alter how code interacts with your definitions.

**Cannot rename definitions.** Renaming is equivalent to deletion plus addition, which breaks existing references.

### Enums

**Cannot add or remove enumerators from closed enums.** Closed enums (the default) commit to a fixed set of values forever. Code can exhaustively match all cases without a wildcard, so adding cases would break such matches.

**Cannot change between open and closed.** An enum published as closed cannot become open, and vice versa. This affects whether exhaustive matching is possible.

**Cannot reorder enumerators.** The order of enum values is part of the public contract.

**Cannot rename enumerators.** Each enumerator name is a permanent identifier.

**Open enums can add new enumerators.** This is the sole evolution path for enums—open enums trade the guarantee of exhaustive matching for the ability to grow.

### Classes and Inheritance

**Class Finality:**

- **Can make non-final class final.** Adding the `<final>` specifier prevents future inheritance, which is a safe addition that strengthens guarantees.
- **Cannot make final class non-final.** Once a class is marked `<final>`, removing this restriction would allow unexpected subclasses that could break assumptions in existing code.

**Class Uniqueness:**

- **Can make non-unique class unique.** Adding the `<unique>` specifier enables identity-based equality, which doesn't break existing code.
- **Cannot make unique class non-unique.** Removing `<unique>` would change the equality semantics from identity to undefined, breaking code that relies on identity comparison.

**Class Abstractness:**

- **Can make abstract class non-abstract.** Allowing instantiation of a previously abstract class is a safe expansion of capabilities.
- **Cannot make non-abstract class abstract.** Preventing instantiation of a previously concrete class breaks code that creates instances.

**Class Concreteness:**

- **Can make non-concrete final class concrete.** Allowing default instantiation of a final class is safe since no subclasses exist to be affected.
- **Cannot change concreteness in other cases.** Making concrete classes non-concrete or changing concreteness of non-final classes could break instantiation code or subclass behavior.

**Inheritance Changes:**

- **Can add inheritance to non-abstract classes.** Adding a parent class or interface extends capabilities without breaking existing functionality.
- **Cannot remove or change inheritance from non-abstract classes.** Removing a parent breaks code that depends on the inheritance relationship.
- **Cannot add, remove, or change inheritance on abstract classes.** Abstract class hierarchies must remain fixed to prevent conflicts and maintain subtype relationships.
- **Cannot add, remove, or change inheritance on interfaces.** Interface hierarchies must remain stable for the same reasons.

**Special Attributes:**

- **Cannot add or remove the `<castable>` attribute.** Runtime type checks depend on this property. Adding it after publication would enable casts that weren't previously safe, while removing it would break existing casts.
- **Cannot remove `<final_super>` once added.** Derived types marked with `<final_super>` must continue inheriting from the same parent to maintain the type hierarchy that `GetCastableFinalSuperClass` depends on.
- **Derived types with `<final_super>` must remain derived from the same parent.** Changing the parent type would break runtime type queries.

**Special Transformations:**

- **Can change final class with no inheritance to struct.** This is a safe transformation since both are value-like and the class cannot have subclasses.
- **Can potentially change abstract class with no class inheritance to interface.** This transformation maintains the same contract but is not yet fully implemented (marked as TODO in tests).

### Structs

**Cannot add any fields to structs.** Structs are immutable value types with a fixed memory layout. Adding fields would change this layout and break binary compatibility.

**Cannot change between class and struct.** These are fundamentally different types with different semantics—classes are references, structs are values.

### Fields and Data Members

**Adding Fields:**

- **Can add fields with default values to classes.** New fields with defaults don't break existing construction code since the defaults are used automatically.
- **Cannot add fields without default values to classes.** Existing code that constructs instances would break since it doesn't provide values for the new fields.
- **Cannot add any fields to structs.** Structs have fixed memory layout and adding fields breaks binary compatibility.

**Removing Fields:**

- **Cannot remove fields from classes or structs.** All published fields must remain available since code may reference them.

**Field Mutability:**

- **Can change final instance field to non-final.** Allowing mutation where it was previously prohibited is a safe expansion of capabilities.
- **Cannot change non-final instance field to final.** Once code depends on being able to mutate a field, making it immutable breaks that code.

**Field Type Changes:**

For **final or non-instance data** (fields that can't be overridden):
- **Can narrow the type (make more specific).** For example, changing from `any` to `int` strengthens the guarantee about what values the field holds.
- **Cannot widen the type (make more general).** For example, changing from `int` to `any` violates the guarantee that callers could read a specific type.

For **non-final instance data** (fields that can be overridden in subclasses):
- **Cannot narrow or widen the type.** These must maintain their exact type to prevent breaking overrides in subclasses or calling code.

**Default Initializers:**

- **Can add a default initializer to a class field.** This makes construction easier without breaking existing code.
- **Cannot remove a default initializer from a class field.** Removing a default breaks construction code that relied on it.

**Overrides:**

- **Can add an override to a field.** Providing a more specific implementation in a subclass is allowed.
- **Can remove an override if it didn't narrow the type.** If the override maintained the same type, removing it is safe.

### Functions and Methods

Function signature changes follow different rules depending on whether the function is **final/non-instance** (can't be overridden) or a **non-final instance method** (can be overridden). The rules reflect fundamental principles of type safety: functions can become more flexible about what they accept (contravariance) and more specific about what they return (covariance), but only when overriding isn't involved.

**Overload Management:**

- **Cannot remove function overloads.** Each published function signature must remain available since code may call it.
- **Function overloads are matched by signature.** When checking compatibility, functions with the same parameters are compared to ensure compatible types and effects.

**Return Types (Covariance):**

For **final or non-instance functions** (module functions, static methods, final methods):
- **Can narrow the return type (make more specific).** Changing from `any` to `int` means the function now guarantees a more specific return value, which is always safe for callers.
- **Cannot widen the return type (make more general).** Changing from `int` to `any` means the function might return different types, breaking code that expects an integer.

For **non-final instance methods** (overridable methods):
- **Cannot narrow or widen the return type.** These must maintain their exact return type to ensure subclass overrides remain compatible.

**Parameter Types (Contravariance):**

For **final or non-instance functions**:
- **Can widen parameter types (make more general).** Changing from `int` to `any` means the function accepts more inputs, which never breaks existing calls with integers.
- **Cannot narrow parameter types (make more specific).** Changing from `any` to `int` means the function rejects some previously valid arguments.
- **Can relax type parameter constraints.** Changing from `t:subtype(comparable)` to `t:type` allows more type arguments.
- **Cannot strengthen type parameter constraints.** The reverse change restricts valid type arguments.

For **non-final instance methods**:
- **Cannot narrow or widen parameter types.** These must maintain their exact parameter types to ensure subclass overrides and calls remain compatible.

**Optional Parameters:**

- **Can add optional named parameters with defaults.** This doesn't break existing calls since the parameters are optional.
- **Can change default values of optional parameters.** New callers get the new defaults while existing compiled code continues using the values it was compiled with.

**Effects (Covariance):**

For **final or non-instance functions**:
- **Can narrow effects (reduce).** Changing from `<transacts>` to `<reads>` to `<computes>` makes the function more pure, which is always safe since code expecting more effects can handle fewer.
- **Cannot widen effects (increase).** Changing from `<computes>` to `<reads>` violates the contract that the function has limited effects.

For **non-final instance methods**:
- **Cannot narrow or widen effects.** These must maintain their exact effects to ensure overrides work correctly.

**Conversions Between Callable Forms:**

- **Cannot convert between normal functions and constructors.** These are fundamentally different callable entities with different calling conventions.
- **Cannot convert between functions and parametric types.** A function cannot become a type parameter or vice versa.

**Function body:**

- **Cannot change the body of transparent functions.** Verification of callers might depend on the function body of transparent functions, so changes could break callers.
- **Cannot change the body of opaque functions without the `<reads>` effect.** This is to ensure that `NonReadsFunction()=NonReadsFunction()` even when code is evolving.
- **Can change the body of opaque functions that have the `<reads>` effect.** Code evolution can be observed by the `<reads>` effect.

**Understanding Variance:**

The asymmetry in these rules reflects **variance** in type theory:
- **Parameters are contravariant**: Accepting more general types (widening) is safe
- **Returns are covariant**: Returning more specific types (narrowing) is safe
- **Effects are covariant**: Having fewer effects is safe

These rules only apply to final/non-instance functions because overridable methods must maintain exact signatures to preserve the Liskov Substitution Principle—any subclass override must be callable wherever the base method is called.

### Access Specifiers

**Increasing Accessibility (Allowed):**

- **Can increase accessibility of definitions.** Making a private definition public, or protected to public, expands access without breaking existing code.
- **Can make constructors more accessible.** Allowing more code to construct instances is a safe capability expansion.

**Reducing Accessibility (Forbidden):**

- **Cannot reduce accessibility of definitions.** Making a public definition protected, internal, or private breaks all external code using it. Making a protected definition private breaks subclass access.
- **Cannot make constructors less accessible.** A class constructor that was public cannot become private or protected.

### Persistable Types

Persistable types require stricter compatibility rules because they define the format of saved player data that must remain loadable indefinitely. Changes to persistable types risk corrupting or losing saved data.

**Persistable Attribute Changes:**

- **Cannot add the `<persistable>` attribute after publication.** Making a type persistable changes its serialization behavior and imposes new restrictions.
- **Cannot remove the `<persistable>` attribute.** Saved data depends on the persistence format of these types.

**Persistable Class Fields:**

- **Can add fields with default values to persistable classes.** Saved data without the new field will load successfully using the default.
- **Cannot add fields without defaults to persistable classes.** Old saved data wouldn't have values for these fields.
- **Cannot remove any fields from persistable classes.** Saved data may contain these field values and must be able to load them.

**Persistable Struct Fields:**

- **Cannot add any fields to persistable structs.** Structs have fixed layouts and saved data expects the exact structure.
- **Cannot remove any fields from persistable structs.** All fields in saved data must be loadable.

**Persistable Enum Changes:**

For **closed persistable enums**:
- **Cannot add enumerators.** Case statements may exhaustively match all values, and saved data deserialization depends on the fixed set.
- **Cannot remove enumerators.** Saved data may contain removed values, making it unloadable.

For **open persistable enums**:
- **Can add new enumerators.** Open enums are designed to grow, and the persistence system handles unknown values.
- **Cannot remove enumerators.** Saved data may still reference removed values.

**Type Lifecycle:**

- **Can add new persistable types.** Publishing new types for data persistence is always allowed.
- **Cannot remove persistable types once published.** They must remain available to deserialize old saved data.
- **Cannot change the structure of persistable types.** Field types, inheritance relationships, and other structural changes break deserialization.

**Module/Type Aliases:**

- **Can add module or type aliases to persistable types.** This provides additional ways to reference existing types without changing them.
- **Can remove module or type aliases to persistable types.** Removing an alias doesn't affect the underlying type's persistence.
- **Module aliases must reference the same path.** Changing the target breaks all code using the alias.
- **Type aliases must reference the same type.** Changing the aliased type breaks all code using the alias.

**Non-Persistable Changes:**

- **Can freely add or remove non-persistable types.** Types without `<persistable>` don't affect saved data and can be added or removed as needed.

**Persistent Variables:**

Verse supports persistent variables (`var` declarations in module scope) that maintain values across sessions:

- **Can add new persistent variables.** New variables are initialized with their default values.
- **Cannot remove persistent variables.** The metaverse expects these variables to exist persistently.
- **Cannot change persistent variable types.** Saved values must match the expected type.
- **Non-persistent variables can be freely changed.** Local or instance variables don't persist and can be modified.

### Parametric Types

Parametric types (generic types with type parameters) have additional compatibility considerations:

**Type Parameter Constraints:**

- **Can widen type parameter constraints in parametric type domains.** Making constraints more permissive (e.g., from `t:subtype(comparable)` to `t:type`) allows more type arguments.
- **Cannot narrow type parameter constraints.** Restricting valid type arguments breaks existing code using the parametric type.
- **Type parameters are treated as rigid when checking functions inside parametric types.** This ensures type safety within the generic context.

**Parametric vs Non-Parametric:**

- **Cannot convert between parametric and non-parametric forms.** A parametric type cannot lose its type parameters, and a regular type cannot gain them.
- **Cannot convert between functions and parametric types.** These are fundamentally different constructs.

**Variance:**

- **Variance is inferred from usage, not declared.** How type parameters are used (in input positions, output positions, or both) determines their variance.
- **Cannot change inferred variance.** Once a type parameter's usage pattern is published, it establishes a variance contract that must be maintained.

### Summary

This catalog represents the core compatibility guarantees that Verse enforces. While these restrictions may seem extensive, they ensure that published code remains a stable foundation for the metaverse ecosystem.

Key principles to remember:

1. **Additions are usually safe**: New optional fields, new overloads, new enumerators in open enums
2. **Removals are usually forbidden**: Removing public definitions breaks dependent code
3. **Narrowing is often safe**: More specific return types, fewer effects
4. **Widening is selectively safe**: More general parameter types (contravariance)
5. **Final/non-instance members are more flexible**: They can evolve types and effects
6. **Non-final instance members are rigid**: They must maintain exact signatures
7. **Persistable types are strictest**: Saved data imposes permanent constraints

The key to working within these constraints is thoughtful initial design—choosing the right visibility, finality, effects, and type properties from the start. Consider future evolution needs when making these irreversible decisions.

## Design Philosophy for Longevity

Creating code that remains viable across extended timescales requires a different approach to software design. Developers must think beyond immediate functionality to consider how their code will evolve and interact with future systems. This forward-thinking approach influences every aspect of development, from initial design to ongoing maintenance.

Schema planning becomes critical when working with persistable types. Since these cannot be changed after publication, developers must carefully consider not just current requirements but potential future needs. This might mean including optional fields that aren't immediately necessary or choosing open enums over closed ones when future expansion seems likely. The cost of getting these decisions wrong—being locked into inflexible schemas—encourages thorough upfront design.

Effect specification offers an interesting trade-off. While Verse allows and sometimes encourages over-specification of effects, marking a function as having effects it doesn't currently use, this provides flexibility for future implementation changes. A function marked as `<reads>` can later be optimized to `<computes>` without breaking compatibility, but the reverse isn't true. This asymmetry encourages conservative effect declarations that leave room for future modifications.

The choice between open and closed constructs represents another long-term decision. Open enums allow new values to be added after publication, providing extensibility at the cost of preventing exhaustive pattern matching. Closed enums offer the opposite trade-off. Understanding when flexibility or completeness is more valuable requires thinking about how the code will be used not just today, but years into the future.
