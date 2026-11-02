# Verse runtime documentation overrides

Prose written here replaces the `@doc` comment that `bin/verse_api` reads out
of the engine, for the declaration named in the heading above it. Leave a
section's body empty to keep whatever the engine says.

Only `##` headings and the prose under them are read. Everything else,
including HTML comments, is ignored — which is why the engine's current text is
kept beside each heading for reference.

Run `bin/verse_api --stubs` again after the engine changes: it appends
headings for anything new and never touches what is already here.

## Easing.CubicBezier

Builds an easing function from the two interior control points of a cubic
Bézier curve, following the CSS easing specification. The curve always runs
from `(0, 0)` to `(1, 1)`; `(X1, Y1)` and `(X2, Y2)` bend it in between. The
shape is exactly what `cubic-bezier(X1, Y1, X2, Y2)` would give you in CSS, so
the control points published for a CSS easing can be pasted straight in.

`X1` and `X2` must both lie in `[0, 1]`. Outside that the curve would double
back and a single progress value would have several answers. The function does
not fail when they do not: it quietly returns the identity instead, so a
mistyped X coordinate shows up as an animation that no longer eases rather than
as an error.

The Y coordinates carry no such restriction, and taking them outside `[0, 1]`
is how you build a curve that overshoots and settles back.

The eased value is found by Newton-Raphson iteration rather than in closed
form, so it is an approximation — close enough for animation, not for anything
that needs the exact root.

<!-- engine text:
Make a cubic bezier interpolation function.
-->
## Easing.Linear

Returns its argument unchanged: progress maps straight to output, so motion
driven by it moves at a constant speed and starts and stops abruptly. It is
the baseline the other curves are departures from.

<!-- engine text:
Linear interpolation function. `Linear` animations move at a constant speed.
-->
## Easing.Ease

The default easing, equivalent to CSS `ease` and to control points
`(0.25, 0.1)` and `(0.25, 1.0)`. Motion begins slowly, accelerates through the
middle and settles at the end, easing out over a longer stretch than it eases
in. That asymmetry is what makes it read as natural rather than mechanical,
and it is the right first choice when nothing else suggests itself.

<!-- engine text:
Ease interpolation function. `Ease` animations start slowly, speed up, then end slowly. The speed of the animation is slightly slower at the end than the start.
-->
## Easing.EaseIn

Equivalent to CSS `ease-in`, control points `(0.42, 0.0)` and `(1.0, 1.0)`.
Starts from rest and accelerates the whole way, arriving at full speed. Suited
to something leaving the screen or a state the viewer is not meant to dwell
on, since the abrupt stop is hidden by whatever follows.

<!-- engine text:
Ease-in interpolation function. `EaseIn` animations start slow, then speed up towards the end.
-->
## Easing.EaseOut

Equivalent to CSS `ease-out`, control points `(0.0, 0.0)` and `(0.58, 1.0)`.
The mirror of `EaseIn`: full speed immediately, then a decelerating approach
to the end. Good for something arriving, where the eye follows it in and wants
to see it come to rest.

<!-- engine text:
Ease-out interpolation function. `EaseOut` animations start fast, then slow down towards the end.
-->
## Easing.EaseInOut

Equivalent to CSS `ease-in-out`, control points `(0.42, 0.0)` and
`(0.58, 1.0)`. Accelerates away and decelerates in, symmetric about the
midpoint. `Ease` does much the same thing with a bias towards the end; this
one is the even-handed version, and the better choice when a movement should
not favour either end.

<!-- engine text:
Ease-in-out interpolation function. `EaseInOut` animations are similar to `Ease` but the start and end animation speed is symmetric.
-->
## enableable.Enable

Puts the object into its enabled state, so that it takes part in simulation
again. Enabling an object that is already enabled has no effect.

<!-- engine text:
Enable this object.
-->
## enableable.Disable

Puts the object into its disabled state. A disabled object keeps its identity
and its data, but stops taking part in simulation until `Enable` is called
again. Disabling an object that is already disabled has no effect.

<!-- engine text:
Disable this object.
-->
## Err

Stops the program. The message is written to the runtime log as an error and
no further Verse code runs in the surrounding content scope, so this is a way
to abandon an impossible situation rather than to report a recoverable one —
for that, use a `<decides>` function and let the caller handle the failure.

Its declared result is `false`, the type with no values, which is the type
system's way of saying the call never comes back.

<!-- engine text:
Halts the Verse runtime with error `Message`.
-->
## event.Signal

Wakes everything waiting on the event, handing each one `Val`.

Tasks suspended in `Await` are resumed first, in the order they suspended, so
the order the waits appear in your code is the order they come back. Each
resumed task runs until it blocks again before the next one is given a turn,
which makes the sequence deterministic but also means one slow waiter delays
the rest.

A task that calls `Await` while this `Signal` is still running joins the next
round rather than this one. Without that rule a task could wake itself in a
loop and the signal would never finish.

Subscribers, on implementations that have them, are invoked only after every
waiting task has been resumed.

<!-- engine text:
Concurrently resumes the tasks that were suspended by `Await` calls before this call to `Signal`.

Tasks are resumed in the order they were suspended. Each task will perform as much work as it can until it encounters a blocking call, whereupon it will transfer control to the next suspended task.
-->
## GetSecondsSinceEpoch

Unix time: seconds elapsed since 1 January 1970 UTC, ignoring leap seconds.

The clock behind it is sampled once at the start of each frame, not on each
call, so every call made during one frame returns the same reading and the
resolution of the whole thing is a frame. Subtracting two readings taken within
one frame gives zero, which makes this the wrong tool for measuring how long a
piece of code took and the right one for asking what time it is.

The reading is also monotonic. If the machine's clock is moved backwards, it
holds its last value until real time catches up, so a duration computed from
two readings is never negative.

<!-- engine text:
Returns the number of seconds since January 1, 1970 UTC, ignoring leap seconds. I.e, this function implements Unix time. This function always returns the same value within the same transaction.
-->
## Sqrt

Returns the square root of `X`. Unlike `Ceil` or `Floor`, this cannot fail: a
negative argument yields `NaN`, which then flows through the rest of the
calculation rather than stopping it.

Verse considers `-0.0` and `0.0` to be the same value, so `Sqrt` normalises its
argument before computing and answers `0.0` for both. Plain IEEE-754 would hand
back `-0.0` for the negative zero.

<!-- engine text:
Returns the square root of `X` if `X >= 0.0`.
Returns `NaN` if `X < 0.0`.
-->
## Quotient

Integer division, rounded so that `Quotient[X, Y] * Y + Mod[X, Y]` always
reconstructs `X` and `Mod` is never negative. That means rounding down when `Y`
is positive and up when `Y` is negative — Euclidean division, not the
truncate-towards-zero division that C and most of its descendants use. The two
agree whenever both operands are positive and part company as soon as one is
not: `Quotient[-7, 2]` is `-4` here, where a truncating language says `-3`.

Fails when `Y` is zero. One case it cannot express at all: the smallest `int`
divided by `-1` is one past the largest, and that raises an integer-overflow
runtime error which stops execution in the surrounding content scope rather
than failing in the ordinary way you could recover from.

<!-- engine text:
Returns the quotient `X/Y` as defined by Euclidean division, i.e.:
 * `Quotient[X/Y] = Floor[X/Y]` when `Y > 0`
 * `Quotient[X/Y] = Ceil[X/Y]` when `Y < 0`
 * `Quotient[X/Y] * Y + Mod[X,Y] = X`
Fails if `Y = 0`.
-->
## Mod

The remainder that pairs with `Quotient`, and the reason to prefer this
division over C's: the result always lies in `[0, Abs(Y))`, never negative.
`Mod[-7, 2]` is `1`, where C's `%` gives `-1`. Wrapping an index or stepping
round a cycle therefore works without the usual correction for negative
inputs.

Fails when `Y` is zero, and raises an integer-overflow runtime error for the
smallest `int` with `Y = -1`, the one pair whose quotient does not fit.

<!-- engine text:
Returns the remainder of `X/Y` as defined by Euclidean division, i.e.:
 * `Mod[X,Y] = X - Quotient(X/Y)*Y`
 * `0 <= Mod[X,Y] < Abs(Y)`
Fails if `Y=0`.
-->
## Math:Lerp(float,float,float)

Blends between `From` at `Parameter = 0.0` and `To` at `Parameter = 1.0`, and
keeps going outside that range: `2.0` lands as far beyond `To` as `To` is
beyond `From`, and `-1.0` as far before `From`. Nothing clamps the parameter,
so extrapolation is a feature rather than an accident.

It computes `From*(1 - Parameter) + To*Parameter` rather than the cheaper
`From + Parameter*(To - From)`. The two differ only in rounding, but they
differ where it is most visible: this form returns exactly `From` and exactly
`To` at the endpoints, so an animation driven by it starts and finishes on its
keyframes instead of a rounding step away from them.

Expects finite arguments; an infinity or a `NaN` anywhere propagates.

<!-- engine text:
Used to linearly interpolate/extrapolate between `From` (when `Parameter = 0.0`) and `To` (when `Parameter = 1.0`). Expects that all arguments are finite.
Returns `From*(1 - Parameter) + To*Parameter`.
-->
## Join([]string,string)

Concatenates the elements of `Strings` with `Separator` between each adjacent
pair, and none at either end. An empty array gives an empty string and a single
element comes back untouched, so there is no special case to write at the call
site.

Lengths are counted in UTF-8 code units, and the result has an upper bound: if
the pieces together would exceed roughly two billion code units the call raises
a runtime error rather than returning something truncated.

<!-- engine text:
Makes a `string` by concatenating `Separator` between the elements of `Strings`.
-->
## ToString(char)

Wraps a single `char` into a `string` one code unit long.

Because a `char` is one UTF-8 code unit rather than a whole Unicode code point,
that is a complete character only below `0x80`. Hand it a code unit taken from
the middle of a multi-byte character and you get one byte of that sequence,
which means nothing until it is rejoined with its neighbours. Slicing a string
at arbitrary `char` boundaries and converting the pieces back has the same
hazard.

<!-- engine text:
Makes a `string` from `Character`.
-->
## subscribable.Subscribe

Registers `Callback` to run each time the event is signalled, and hands back a
`cancelable` whose `Cancel` unregisters it again. Holding on to that object is
the only way to stop the callback short of the whole scope going away.

Do not let one callback depend on another having already run. Nothing orders
subscribers, and the standard event implementation goes further by shuffling
them before every signal, so an accidental dependency will work in testing and
fail later. Each callback is also run in a transaction of its own: one that
fails rolls back its own work only, and the remaining subscribers still run.

<!-- engine text:
Registers `Callback` to be invoked on matching calls to `signable.Signal`.
Returns an unsubscriber object. Call `cancelable.Cancel` on the unsubscriber to unregister `Callback`.
-->
## operator'/'(int,int)

Dividing one `int` by another gives a `rational`, not an `int`. This is the
detail that catches people arriving from other languages: `7 / 2` is not `3`,
it is the exact value seven halves, carried as a ratio with nothing thrown
away. Verse declines to guess whether you wanted the quotient rounded down,
rounded towards zero, or kept whole.

To land back on an `int`, say which you meant: `Floor[X / Y]`, `Ceil[X / Y]`,
or `Quotient[X, Y]`.

The operation can fail, and does when `Y` is zero — which is why it appears in
square brackets or under an `if` rather than being written bare.

<!-- no documentation in the engine source -->
## GetRandomFloat

A uniformly distributed `float` somewhere in `[Low, High]`, both ends included.
The two bounds may arrive in either order. The draw takes 53 random bits — the
full precision of a `float` — and the result is clamped back into range so that
rounding in the interpolation can never push it a hair outside the interval you
asked for.

Read the note on `GetRandomInt` about transactions and repeatability; it
applies here in full.

<!-- engine text:
Returns a uniformly distributed, cryptographically-secure random `float` between `Low` and `High`, inclusive. (`Low` and `High` can be out of order.)
-->
## GetRandomInt

A uniformly distributed `int` in `[Low, High]`, both ends included, with the
bounds accepted in either order. Candidates outside the range are rejected and
redrawn rather than folded back in, so every value really is equally likely —
no bias towards the low end of the interval.

The numbers are cryptographically sourced: a hardware entropy seed, mixed per
thread and ratcheted forward with SHA-256. There is no seed parameter and no
way to replay a sequence. If you need a repeatable one, you need your own
generator.

The part that will bite you: **the draw is deliberately taken outside the
enclosing transaction**. Rolling back a `<transacts>` block does not roll back
the random state, so re-running rolled-back code produces *different* numbers.
That is a considered choice — with no seed there is no sequence to restore —
but it means a random value must not be something your rollback logic assumes
it can reproduce.

<!-- engine text:
Returns a uniformly distributed, cryptographically-secure random `int` between `Low` and `High`, inclusive. (`Low` and `High` can be out of order.)
-->
## operator'='

Succeeds when the two operands are the same value, and when it succeeds it
produces that value — so a comparison can stand in for the thing compared:
`if (Found := Needle = Haystack[0])` binds `Found` to the matching element.

Equality here is *extensional*: two values are the same when nothing you can
observe tells them apart. That is not IEEE float equality. `NaN = NaN`
succeeds, and `0.0 = -0.0` succeeds, because Verse cannot expose a difference
between those pairs. Rationals compare by value, so `1/1 = 2/2` succeeds too.

The right operand is typed `comparable`, the class of everything that can be
compared at all. Classes and interfaces are outside it unless marked
`<unique>`, since object identity is the only equality they could offer.

<!-- no documentation in the engine source -->
## operator'<>'

The negation of `=`: succeeds when the two operands are *not* the same value,
and yields the left operand when it does. The same extensional notion of
sameness applies, so `NaN <> NaN` fails — the two are indistinguishable, and
so equal, however much IEEE-754 disagrees.

<!-- no documentation in the engine source -->
## operator'+='(ref(int),int)

Adds `Rhs` into the variable on the left and produces the new value. Written
`set X += Y`.

Unlike the plain arithmetic operators this one writes to memory, so it carries
`<transacts>`: inside a transaction that later rolls back, the write is undone
with everything else.

<!-- no documentation in the engine source -->
## Abs(int)

The magnitude of `Val`, discarding its sign.

There is no value this cannot represent: `int` in VerseVM is arbitrary
precision, so unlike a fixed-width integer there is no most-negative value
whose absolute value overflows. On BPVM, where `int` is 64 bits, that edge
does raise a runtime error.

<!-- no documentation in the engine source -->
## BitAnd

Bitwise AND of two integers, treating them as two's-complement bit patterns of
unlimited width. Negative values behave as though sign-extended forever to the
left, so `BitAnd(-1, X)` is `X`.

<!-- no documentation in the engine source -->
## BitOr

Bitwise OR of two integers, treating them as two's-complement bit patterns of
unlimited width.

<!-- no documentation in the engine source -->
## BitXor

Bitwise exclusive-OR of two integers, treating them as two's-complement bit
patterns of unlimited width.

<!-- no documentation in the engine source -->
## BitNot

Inverts every bit of `Val`. On two's-complement numbers that is the same as
`-Val - 1`, so `BitNot(0)` is `-1`. Because `int` has no fixed width there is
no leading-bit cutoff to worry about.

<!-- no documentation in the engine source -->
## BitShiftLeft

Shifts the bits of `Lhs` left by `Rhs` places, filling with zeros. That is the
same as multiplying by 2 to the power `Rhs`, for negative values too, so
`BitShiftLeft[-5, 2]` is `-20`. Because `int` has no fixed width the result
grows rather than wrapping around. Fails if `Rhs` is negative.

<!-- no documentation in the engine source -->
## BitShiftRight

Shifts the bits of `Lhs` right by `Rhs` places, dropping the bits shifted out.
That is the same as dividing by 2 to the power `Rhs` and rounding toward
negative infinity, so `BitShiftRight[-97, 5]` is `-4`, not `-3`. Shifting past
every bit leaves only the sign: `0` or `-1`. Fails if `Rhs` is negative.

<!-- no documentation in the engine source -->
## operator'>'(int,int)

Succeeds when `Lhs` is greater than `Rhs`, and produces `Lhs` when it does.
Comparison is a failable expression rather than something returning `logic`,
which is why it belongs in an `if` or a `for` filter rather than in a variable.

Chaining is separate syntax rather than repeated application. `0 <= I <= Length`
is one expression that checks both `0 <= I` and `I <= Length`; it is not
`(0 <= I) <= Length`, which would compare the returned `0` against `Length` and
never look at `I` again.

<!-- no documentation in the engine source -->
## MakeRationalFromInt

Widens an `int` to a `rational` with a denominator of one. Rationals are exact
ratios, so nothing is lost and nothing is approximated — this is a change of
representation rather than a conversion.

<!-- no documentation in the engine source -->
## Ceil(rational)

Rounds a `rational` up to the nearest `int`. Together with `Floor` this is how
you leave the exact world of rationals for whole numbers, most often right
after an integer division: `Ceil[Total / PerPage]` is the page count.

Applied to something that is already an `int`, it hands it straight back.

<!-- no documentation in the engine source -->
## Floor(rational)

Rounds a `rational` down to the nearest `int` — towards negative infinity, not
towards zero, so `Floor[-7/2]` is `-4` rather than `-3`. This is the rounding
that makes `Floor[X / Y]` agree with `Quotient[X, Y]` for positive divisors.

Applied to something that is already an `int`, it hands it straight back.

<!-- no documentation in the engine source -->
## operator'/'(float,float)

Floating-point division, which — unlike the `int` version — always succeeds.
Dividing by zero gives `+Inf`, `-Inf` or `NaN` rather than failing, following
IEEE-754, and that value then flows onward through the calculation.

If you want a failure instead of an infinity, test the divisor first.

<!-- no documentation in the engine source -->
## Abs(float)

The magnitude of `Val`, discarding its sign. `Abs(-0.0)` is `0.0`, and
`Abs(NaN)` is `NaN` — magnitude says nothing about a value that is not a
number.

<!-- no documentation in the engine source -->
## operator'<'(float,float)

Succeeds when `Lhs` is less than `Rhs`, producing `Lhs`.

This is plain IEEE-754 comparison, so a `NaN` on either side makes it fail:
both `NaN < 1.0` and `1.0 < NaN` fail. `<=` is not the same shape — it is
adjusted so that `NaN <= NaN` succeeds, since Verse requires `NaN` to equal
itself — which means these operators form a partial order, and a failing
`X >= Y` does not let you conclude `X < Y`.

Worth keeping separate from the *total* order Verse uses to sort and hash
floats, where `NaN` ranks above `+Inf` so that floats can serve as map keys.
The comparison operators and that ordering genuinely disagree.

<!-- no documentation in the engine source -->
## operator'?'(logic)

Succeeds when `Value` is `true` and fails when it is `false`. Written
`Value?`.

It turns a `logic` — an ordinary value you can store and pass around — into a
failable expression that `if` and the other failure contexts can use. The
inverse direction is `logic{...}`, which turns a failable expression back into
a `logic`.

<!-- no documentation in the engine source -->
## operator'+'([]t,[]t)

Concatenates two arrays into a new one. Neither input is modified — arrays are
immutable values, so `+` builds a third array rather than extending the first.

<!-- no documentation in the engine source -->
## operator'array.Length'

The number of elements in an array, written `Array.Length`.

For a `string`, which is an array of `char`, that is a count of UTF-8 code
units rather than of characters as a reader would count them: a string holding
one emoji has a `Length` of four.

<!-- no documentation in the engine source -->
## operator'()'([]t,int)

Reads the element of `Array` at `Index`, written `Array[Index]`.

It fails rather than erroring when the index is out of range, which is why
indexing appears inside `if` or with square brackets on the call. There is no
unchecked variant: bounds are part of the type discipline, not a debug feature
you can switch off.

Indices count from zero and run to `Array.Length - 1`.

<!-- no documentation in the engine source -->
## operator'()'(ref([]t,[]u),int)

An array element used as the target of an assignment, written
`set Array[Index] = Value`.

Like reading, it fails when the index is out of range, so the whole assignment
is a failable expression. It carries `<reads>` as well as failing, because the
current array has to be examined before it can be replaced.

<!-- no documentation in the engine source -->
## operator'map.Length'

The number of key-value pairs in a map, written `Map.Length`.

<!-- no documentation in the engine source -->
## ConcatenateMaps

Combines two maps into a new one. Where a key appears in both, the value from
the right-hand map wins — the entries are laid down left first, then right,
and a map keeps only the last value given for a key.

This is the map counterpart of array concatenation, and like it, neither input
is modified.

<!-- no documentation in the engine source -->
## operator'()'(weak_map(t,u),t)

Reads the value stored against `Key`, written `Map[Key]`. Fails when the key
is absent — and in a `weak_map`, a key can become absent on its own once
nothing else holds it alive.

<!-- no documentation in the engine source -->
## weak_map

The type constructor behind `weak_map(key_type, value_type)`. It appears where
a type is expected rather than where a value is, which is why it reads as a
function call but never evaluates one.

A `weak_map` does not keep its keys alive: an entry disappears once nothing
else refers to its key. That is what makes it the right shape for data hung
off objects with their own lifetimes, and the basis for persistent storage.

<!-- no documentation in the engine source -->
## operator'?'(?t)

Unwraps an optional. Succeeds and produces the contained value when there is
one, fails when the optional is `false`. Written as a suffix: `Value?`.

This is the only way into an optional, and the reason optionals are safe: the
type system will not let you reach the value without handling the possibility
that it is absent.

<!-- no documentation in the engine source -->
## FitsInPlayerMap

Succeeds when `Value` is something a player's persistent map is allowed to
hold, and produces the value unchanged when it does.

Persistence imposes limits that ordinary values do not have — on what types
may be stored and how large the data may be — and this is the check that
decides. Use it to find out before writing rather than discovering afterwards
that the data did not survive.

<!-- no documentation in the engine source -->
## operator'char.ToCodeUnit'

The numeric value of a UTF-8 code unit, `0` to `255`, written
`Character.ToCodeUnit()`.

Since a `char` is one code unit and not a whole Unicode code point, this is a
character's code point only for ASCII. Above `0x7F` it is one byte of a
multi-byte sequence.

<!-- no documentation in the engine source -->
## operator'int.ToChar'

Converts a number to a `char`, written `Value.ToChar()`. Fails when the number
is not a valid UTF-8 code unit, which is what stops an arbitrary integer from
being smuggled into a string.

<!-- no documentation in the engine source -->
## value

One node of a parsed JSON document: an object, an array, a number, a string, a
boolean, or null.

JSON is untyped where Verse is typed, so every way out of a `value` is a
question that can fail. `AsObject[]`, `AsArray[]`, `AsInt[]` and the rest each
succeed only if the node really is of that shape, which pushes you to handle
malformed input at the point you read it rather than discovering it later.

<!-- no documentation in the engine source -->
## editable_curve

A curve of `float` values over time, authored in the editor and exposed to
Verse as an `@editable` property.

Use one when a designer should be able to shape how a value changes — a damage
falloff, a difficulty ramp, a camera ease — without that shape being compiled
into the Verse code.

<!-- no documentation in the engine source -->
## modifier.Evaluate

Takes a value and returns the modified one. A modifier never mutates in place:
it is a function from `t` to `t`, which is what allows a stack of them to be
composed and applied in order, each seeing the output of the one before.

<!-- no documentation in the engine source -->
## animation_sequence

A reference to a single animation clip — one recorded motion, as opposed to a
graph or state machine that chooses between motions.

<!-- no documentation in the engine source -->
## material

A reference to a material — the description of how a surface responds to light,
which you assign to a mesh to change how it looks.

Materials are the asset type most often exposed as an `@editable` so that a
designer can restyle something without touching Verse.

<!-- no documentation in the engine source -->
## particle_system

A reference to a particle effect. Like a sound, it is a thing you trigger
rather than a thing you read: the asset describes the effect, and the component
that plays it decides where and when.

<!-- no documentation in the engine source -->
## mesh

A reference to a static mesh: the geometry of a piece of scenery or a prop,
without any animation of its own.

Every type in this module works the same way, and none of them is constructed in
Verse — there would be nothing to construct from. You declare an `@editable`
property of the asset type you want, pick the content in the editor, and Verse
receives a reference to whatever was picked.

<!-- no documentation in the engine source -->
## sound_wave

A reference to an audio clip.

<!-- no documentation in the engine source -->
## texture

A reference to a texture asset.

`Width` and `Height` come with the reference rather than being read from the
loaded image, so they are available without the texture being in memory. The
consequence is that they are fixed when the project is built: replacing the
image behind a reference changes the picture but not the dimensions Verse
reports until the manifest is regenerated.

<!-- no documentation in the engine source -->
## texture.Height

The height of the texture in pixels, recorded when the project's asset manifest
was generated rather than measured at runtime.

<!-- no documentation in the engine source -->
## texture.Width

The width of the texture in pixels, recorded when the project's asset manifest
was generated rather than measured at runtime.

<!-- no documentation in the engine source -->
## input_action

A reference to a single input action, parameterised by the type of value the
action carries: `void` for a button, a scalar for a trigger, a vector for a
stick.

The type parameter is what keeps input honest — an action declared to carry a
direction cannot be read as though it were a button press.

<!-- no documentation in the engine source -->
## input_mapping

A reference to an input mapping asset — the table that connects physical
inputs, across keyboard, mouse, gamepad and touch, to the abstract actions a
game responds to.

Working against actions rather than keys is what lets one piece of Verse serve
every control scheme.

<!-- no documentation in the engine source -->
## collision_channel

The category a volume belongs to for collision purposes.

Channels do not decide anything by themselves. A volume declares which channel
it is on, and a `collision_profile` maps each channel to a
`collision_interaction` — ignore, overlap, or block — which is what determines
how any two volumes actually meet. Splitting it this way means a volume can be
solid to characters, transparent to the camera and invisible to sight tests
without needing three volumes.

<!-- engine text:
Every volume has a collision channel as part of its collision_profile. It is used to determine how two volumes interact. See collision_profile.
-->
## CollisionChannels.stationary

The channel for world geometry that does not move: floors, walls, terrain, the
fixed shape of a level.

<!-- no documentation in the engine source -->
## CollisionChannels.dynamic

The channel for objects that move under the simulation — props, debris,
projectiles, anything whose position is not fixed.

<!-- no documentation in the engine source -->
## CollisionChannels.avatar

The channel for characters: the volumes that represent players and other agents
moving through the world.

<!-- no documentation in the engine source -->
## CollisionChannels.visibility

The channel for line-of-sight tests. Putting something on this channel is what
lets it block or not block sight independently of whether it blocks movement — a
bush that can be walked through but not seen through, or a pane of glass that is
the reverse.

<!-- no documentation in the engine source -->
## CollisionChannels.camera

The channel for camera collision, which decides what the camera is pushed away
from. Keeping it separate from `stationary` is what lets thin decoration be
solid to the player without shoving the camera around.

<!-- no documentation in the engine source -->
## CollisionChannels.physics

The channel for the physics simulation proper, as distinct from the query
channels that only answer questions.

<!-- no documentation in the engine source -->
## contact_point

One point of contact reported by a collision: where the surfaces met, which way
they faced, how hard, and how far they had already overlapped.

A single collision can produce several of these — a box landing flat on the
ground touches at more than one place — so they arrive as a collection rather
than singly.

<!-- no documentation in the engine source -->
## contact_point.ContactPosition

Where the two surfaces met, in world space.

<!-- no documentation in the engine source -->
## contact_point.ContactNormal

The direction the contacted surface faces at that point, as a unit vector.
Reflecting motion off a surface, or deciding whether a landing counts as
standing on something rather than brushing past it, both start here.

<!-- no documentation in the engine source -->
## contact_point.ContactImpulse

How much momentum the contact transferred. This is the number to test against
when a hit should only count if it was hard enough — a threshold on impulse
distinguishes a collision from a scrape.

<!-- no documentation in the engine source -->
## contact_point.ContactDepth

How far the two shapes had already overlapped when the contact was reported.
Discrete simulation lets fast bodies interpenetrate slightly before being pushed
apart, and this is the measure of that.

<!-- no documentation in the engine source -->
## has_collision

Implemented by things that occupy space for the purposes of collision — the
queryable, blockable presence of a mesh part in the world.

The interface delegates to the `mesh_part` behind `Self`, so it is the mesh
parts of an entity, not the entity as a whole, that carry collision.

<!-- no documentation in the engine source -->
## has_dynamics

Implemented by things that take part in the physics simulation: mass, velocity,
and the forces and impulses that change them.

Like `has_collision`, each method delegates to the `mesh_part` behind `Self`. If
there is no such part the call is quietly a no-op, or returns a zero value, so
these are safe to call on something that turns out not to be simulated.

<!-- no documentation in the engine source -->
## has_dynamics.ApplyLinearImpulse

Adds an instantaneous change of momentum, in the direction and magnitude of
`LinearImpulse`. Use this for a kick, a hit, a jump — a one-off event — where
`ApplyForce` is for something sustained.

<!-- no documentation in the engine source -->
## has_dynamics.ApplyAngularImpulse

Adds an instantaneous change of angular momentum, setting the body spinning
about the axis of `AngularImpulse` in proportion to its magnitude.

<!-- no documentation in the engine source -->
## has_dynamics.GetLinearVelocity

The body's current velocity, in world space.

<!-- no documentation in the engine source -->
## has_dynamics.SetLinearVelocity

Replaces the body's velocity outright, rather than nudging it as an impulse
would. Convenient for teleporting motion, but it discards momentum, so a body
moved this way will not conserve energy in a collision the way a body pushed by
an impulse does.

<!-- no documentation in the engine source -->
## has_dynamics.GetAngularVelocity

The body's current rate of rotation.

<!-- no documentation in the engine source -->
## has_dynamics.SetAngularVelocity

Replaces the body's rate of rotation outright.

<!-- no documentation in the engine source -->
## has_dynamics.ApplyForce

Adds a force, which acts over time rather than all at once. Applied once it has
almost no visible effect; applied every tick it produces steady acceleration —
thrust, wind, a tractor beam.

<!-- no documentation in the engine source -->
## has_dynamics.ApplyTorque

Adds a rotational force about the axis of `Torque`, accelerating the body's spin
for as long as it keeps being applied.

<!-- no documentation in the engine source -->
## has_dynamics.GetMass

The body's mass, which is what decides how much a given impulse or force moves
it. Mass comes from the physics setup of the mesh part rather than from Verse.

<!-- no documentation in the engine source -->
## KeyframedMovement.easing_function.Evaluate

Maps a progress value to an eased one. Subclasses supply the curve;
`cubic_bezier_easing_function` is the usual one.

<!-- no documentation in the engine source -->
## mesh_part

One piece of a mesh, addressable on its own.

Collision and physics live here rather than on the entity: a mesh split into
parts can have some parts solid and others not, and forces applied to one part
need not move the others. Being `<unique>` it has identity, so a part can be
used as a map key to hang state off it.

<!-- no documentation in the engine source -->
## particle_system_component.Stop

Stops the effect. Particles already emitted are not removed — the emitter simply
stops producing more, so the effect fades out as they expire rather than
vanishing.

<!-- no documentation in the engine source -->
## rarity.Color

The colour conventionally used to indicate this rarity in the interface.

<!-- no documentation in the engine source -->
## stackable_component.ChangeStackSizeEvent

Signalled after the stack size changes, carrying both the old and the new size.

Because the event reports the change rather than the state, a listener can tell
the difference between a stack growing and a stack shrinking without keeping its
own copy of the previous value.

<!-- no documentation in the engine source -->
## stackable_component.ChangeMaxStackSizeEvent

Signalled after the stack's capacity changes, carrying the old and new maximum.
Both are optional, since a stack may have no maximum at all.

<!-- no documentation in the engine source -->
## change_stack_size_result

The payload of `ChangeStackSizeEvent`: which component changed, and the sizes
either side of the change.

<!-- no documentation in the engine source -->
## change_max_stack_size_result

The payload of `ChangeMaxStackSizeEvent`: which component changed, and the
maximums either side of the change. They are optional because a stack may be
unbounded, before or after.

<!-- no documentation in the engine source -->
## origin.GetTransform

The transform that a `transform_component` should treat as its frame of
reference, instead of its parent's.

<!-- no documentation in the engine source -->
## entity_origin.Entity

The entity whose transform is used as the origin.

<!-- no documentation in the engine source -->
## agent

A participant in the simulation — a human player, a bot, anything the game
treats as an actor with a will of its own. `agent` is the type you accept when
a function should work for any of them, and `player` is the narrower case.

You never construct one. Agents arrive from the simulation: from an event
payload, from the session, from whatever produced the thing you are reacting
to.

Being `<unique>` gives an agent identity-based equality, and that is what makes
`[agent]int` and friends legal — a class can only be a map key if it is
`<unique>`, because identity is the only equality an object can offer. It is
also an `entity`, so it participates in the scene graph and can carry
components.

<!-- no documentation in the engine source -->
## player

An `agent` that is a human participant in the session.

Unlike a bare `agent`, a `player` can key a module-scoped `var weak_map`, which
is how per-player data survives across sessions. That privilege is conditional:
`IsActive` tells you whether this player is currently joined, and using an
inactive player as such a key is a runtime error rather than a failure you can
recover from. Check first.

<!-- no documentation in the engine source -->
## Environment

The `session_environment` this session is running in — which tells you whether
you are on a developer's machine, in a test environment, or live in front of
players.

Behaviour that should differ between a playtest and a shipped experience keys
off this: verbose logging, cheat commands, shortened timers. Reading it costs
nothing, so branch on it directly rather than caching the answer.

<!-- no documentation in the engine source -->
## team

A group of `agent`s the simulation treats as one side.

Like `agent`, a `team` is `<unique>` — identity-based equality — so teams can
be used as map keys and compared for sameness. You obtain teams from the
session rather than constructing them.

<!-- no documentation in the engine source -->
## tag_search_sort_type

How the results of a tag search are ordered.

<!-- no documentation in the engine source -->
## tag_search_criteria.RequiredTags

Tags a candidate must carry to appear in the results at all.

<!-- no documentation in the engine source -->
## tag_search_criteria.PreferredTags

Tags that do not filter but influence ordering: a candidate carrying more of
them sorts ahead of one carrying fewer.

<!-- no documentation in the engine source -->
## tag_search_criteria.ExclusionTags

Tags that disqualify a candidate, applied after `RequiredTags`.

<!-- no documentation in the engine source -->
## tag_search_criteria.SortType

How the surviving candidates are ordered.

<!-- no documentation in the engine source -->
## classifiable_subset.GetDiagnostic

Describes the set for diagnostic output, listing the types it currently holds.
As with every `diagnostic`, the exact wording is not part of the contract and
may change between versions — read it, do not parse it.

<!-- no documentation in the engine source -->
## Easing

Interpolation curves for animation, all of them shaped like the CSS easing
functions: they map progress from `0.0` to `1.0` onto an eased value over the
same range.

`Linear`, `Ease`, `EaseIn`, `EaseOut` and `EaseInOut` are the standard set.
`CubicBezier` builds one from control points when none of those is the shape
you want.

<!-- no documentation in the engine source -->
## diagnostic.GetDiagnostic

Returns the diagnostic itself, since a `diagnostic` is already the form that
diagnostic output wants. Implementing `diagnosable` this way lets a diagnostic
be embedded in another one without special-casing.

<!-- no documentation in the engine source -->
## date_time

A point in time, held as a count of ticks.

Being a `struct` it is a value: comparing two `date_time`s compares the instants
they name, and one can be stored in a map or made persistent like any other
value.

<!-- no documentation in the engine source -->
## date_time.Ticks

The instant as a whole number of ticks, where a tick is 100 nanoseconds.

Working in ticks rather than seconds keeps the type exact — arithmetic on
instants and durations never accumulates the rounding error a `float` count of
seconds would.

<!-- no documentation in the engine source -->
## CreateDateTime

Builds a `date_time` from calendar fields, failing if they do not name a real
instant: month 13, or the 30th of February.

Because it fails rather than clamping, a date arriving from outside the program
is validated by the act of constructing it. `ValidateDateTime` answers the same
question without building anything, for when you want to report the problem
rather than branch on it.

<!-- no documentation in the engine source -->
## ValidateDateTime

Answers whether these calendar fields name a real instant, as a `logic` rather
than as a failure.

`CreateDateTime` performs the same check; use this one when you want to test the
fields without constructing anything — validating a form, say, where the answer
is a message rather than a value.

<!-- no documentation in the engine source -->
## prefix'-'(int)

On VerseVM an `int` has no bounds, so negation is always exact and always
succeeds. On the older BPVM an `int` is a 64-bit two's-complement value, and
that representation holds one more negative number than positive: the most
negative value has no negation. The implementation detects this and raises an
unrecoverable runtime error rather than failing, so no failure context can
catch it.

Since negation carries no `<decides>`, there is nothing you can write to guard
it. If the magnitude comes from untrusted data and BPVM is in play, range-check
the value before negating it.

<!-- no documentation in the engine source -->
## operator'+'(int,int)

VerseVM integers are arbitrary precision. Addition starts in an inline 32-bit
representation, widens to 64 bits, and finally allocates a heap big integer, so
it can never overflow; the only price of very large values is allocation. BPVM
computes in 64 bits with a checked add and raises a runtime error when the
result leaves that range — an error, not a failure, so it cannot be recovered
from. The same source can therefore run cleanly on one VM and abort on the
other.

The instruction behind this declaration is shared with array and string
concatenation and with rational addition; the overload exists to tell the type
checker that two `int`s give an `int`.

<!-- no documentation in the engine source -->
## operator'-'(int,int)

Each arithmetic step is range-checked on its own on BPVM, so an expression
like `A - B + C` can abort on the intermediate result even when the final
mathematical value would have fitted in 64 bits. Rearranging the expression to
keep intermediates small is a real fix, not superstition.

VerseVM has no such limit, but the same rearrangement pays off differently
there: an intermediate that exceeds 64 bits is promoted to a heap-allocated
big integer, and that allocation is the cost you avoid.

<!-- no documentation in the engine source -->
## operator'*'(int,int)

BPVM detects overflow properly rather than approximately — the product's
magnitude is computed in 32-bit halves and the discarded high bits inspected —
but the outcome is still an unrecoverable runtime error. VerseVM instead
promotes to a heap big integer, so a loop that repeatedly multiplies grows the
value without limit and consumes ever more time and memory rather than
wrapping or erroring.

Multiplication is also the only arithmetic operator with mixed `int`/`float`
overloads, so `2 * X` type-checks for a float `X` where `2 + X` does not.

<!-- no documentation in the engine source -->
## operator'-='(ref(int),int)

Not a single atomic step. It lowers to a read through the reference, a freeze
of the value read, the subtraction, and a write back, and it evaluates to the
new value rather than the old one. Being `<transacts>`, the write is undone if
the surrounding transaction fails.

On BPVM the overflow check runs before the store, so when a subtraction
overflows the runtime error is raised and the variable keeps its previous
value.

<!-- no documentation in the engine source -->
## operator'*='(ref(int),int)

The same read-modify-write shape as the other compound assignments: read,
freeze, multiply, store, yielding the new value.

There is deliberately no `/=` for `int`. Dividing two `int`s produces a
`rational`, not an `int`, so there would be nothing of the right type to store
back — the only compound division in the language is the `float` one.

<!-- no documentation in the engine source -->
## operator'>='(int,int)

Like every comparison in Verse this is `<decides>` and evaluates to its left
operand on success, so `X >= Floor` can stand in for `X` inside the branch it
guards.

Integer comparison never coerces to `float`: on VerseVM the implementation
compares inline and heap-allocated integers directly, so ordering stays exact
at any magnitude. There is no mixed `int`/`float` comparison overload at all,
which means comparing an `int` against a `float` requires an explicit
conversion — and it is that conversion, not the comparison, that loses
precision.

<!-- no documentation in the engine source -->
## operator'<'(int,int)

Strict integer ordering, `<decides>`, evaluating to its left operand. When the
comparison appears directly as the condition of a failure context the compiler
emits a dedicated fast-failing instruction that branches straight to the
alternative arm instead of unwinding the failure context, so comparisons in
`if` conditions are cheap.

<!-- no documentation in the engine source -->
## operator'<='(int,int)

A distinct operation rather than something synthesised from `<` and `=`, and
like the others it hands back its left operand.

The same `<=` spelling turns up in the `where` clauses that define constrained
integer types, as in `type{X:int where 0 <= X, X < 256}`, but those are not
calls to this operator. The compiler extracts the bounds at compile time and
the runtime tests membership with a single range check.

<!-- no documentation in the engine source -->
## prefix'-'(float)

A sign-bit flip, so negating zero genuinely produces `-0.0` — a different bit
pattern from `0.0`, yet one that compares equal to it under Verse's
extensional equality. Verse closes the one hole through which the difference
would otherwise leak: division normalises a negative-zero divisor to positive
zero, so dividing by `-0.0` yields `+Inf`, not `-Inf`.

Negating a NaN yields a NaN, which still equals `NaN`.

<!-- no documentation in the engine source -->
## operator'+'(float,float)

Ordinary IEEE-754 double addition, but the implementation is deliberately
quarantined in a module compiled with precise floating-point pragmas and with
fast-math and fused-multiply-add contraction switched off. That is what lets
Verse promise the same answer on every platform: the compiler is not permitted
to reassociate your sums or fold them into an FMA.

Overflow produces `Inf` rather than an error, so float arithmetic — unlike
integer arithmetic on BPVM — never aborts.

<!-- no documentation in the engine source -->
## operator'-'(float,float)

Subject to the same precise-floating-point guarantees as addition. `Inf - Inf`
is indefinite: you get a NaN, and the sign of that NaN is not guaranteed and
may differ between x86-64 and arm64. The difference is unobservable from
Verse, because every NaN compares equal to every other NaN, but it is a good
reason never to reason about float bit patterns.

<!-- no documentation in the engine source -->
## operator'*'(float,float)

Zero times infinity is a NaN, as is any product involving a NaN, so a
multiplication is one of the easy ways to turn a perfectly reasonable
computation into a value that fails every `<` and `>` comparison you
subsequently apply to it.

<!-- no documentation in the engine source -->
## operator'+='(ref(float),float)

Read, freeze, add, store; the expression evaluates to the new value. Float
addition can neither fail nor error, so the only way this does not take effect
is a transaction rollback.

Accumulating in a loop gives you exactly the sequential sum, in order, because
reassociation is disabled for these operations. That is reproducible rather
than accurate — the usual advice about summation error still applies.

<!-- no documentation in the engine source -->
## operator'-='(ref(float),float)

A read, a subtract and a write, not a single update. That matters when the
left-hand side is not a plain local: for a field backed by an accessor the
getter runs first and the setter afterwards, and for a live variable the write
goes through the live-variable path that wakes awaiting tasks. Anything
observing the variable sees two distinct events.

<!-- no documentation in the engine source -->
## operator'*='(ref(float),float)

The same read-modify-write shape. Note that multiplying by `0.0` is not a
reliable way to clear a float variable: if it currently holds a NaN or an
infinity, the result is a NaN.

<!-- no documentation in the engine source -->
## operator'/='

The only compound-assignment division in the language, and it exists only for
`float`, because dividing two `int`s yields a `rational` and there is nothing
of the right type to store back.

Dividing by zero does not fail here. The divisor is first normalised so that
`-0.0` behaves exactly as `0.0`, and the result is then `+Inf`, `-Inf` or
`NaN` by the usual IEEE rules. If you want division that fails on a zero
divisor, that is the integer operator, which is `<decides>`.

<!-- no documentation in the engine source -->
## operator'*'(int,float)

Mixed-mode arithmetic exists for multiplication alone. `+`, `-` and `/`
require both operands to have the same type, so `2 * X` compiles for a float
`X` while `2 + X` does not — an asymmetry that catches people out regularly.

The `int` operand is converted to the nearest `double` first. On VerseVM,
where integers are unbounded, that conversion loses precision above 2^53 and
yields `Inf` for anything beyond the range of a `double`, silently and without
failing.

<!-- no documentation in the engine source -->
## operator'*'(float,int)

The mirror-image declaration. Commutativity is not inferred here: the two
operand orders resolve to two separate overloads, both of which convert the
integer and then multiply, so `2 * X` and `X * 2` do agree.

Because the conversion happens before the multiplication, multiplying by a
very large `int` rounds the integer first rather than computing exactly and
rounding at the end.

<!-- no documentation in the engine source -->
## operator'>'(float,float)

Defined as `<` with the operands swapped, and `<` is plain IEEE less-than: any
comparison involving a NaN is false and therefore fails. This is the one place
where Verse's usual treatment of NaN gives way. Equality is extensional, so
`NaN = NaN` succeeds, and the ranking function that orders float map keys and
hashes places NaN above `Inf` — yet `Inf < NaN` and `NaN > Inf` both fail.

The practical consequence is that `<` and `>` must not be used to sort or
bisect float data that might contain a NaN; the comparison operators and the
sort order genuinely disagree.

<!-- no documentation in the engine source -->
## operator'>='(float,float)

Derived from `<=` with the operands swapped, and `<=` is special-cased so that
a NaN on the left succeeds only when the right operand is also a NaN. Hence
`NaN >= NaN` succeeds while `NaN >= 0.0` and `NaN > NaN` fail.

The trap is that a failing `X >= Y` does not mean `X < Y` succeeds. If either
operand is a NaN, both fail, so the two arms of a float comparison are not a
dichotomy and code that assumes they are will silently take neither path.

<!-- no documentation in the engine source -->
## operator'<='(float,float)

One of the three primitive float relations — `=`, `<` and `<=` — from which
`!=`, `>` and `>=` are derived by negation or by swapping operands. It is not
IEEE `<=`: a NaN left operand succeeds when the right operand is also a NaN,
which keeps `X <= X` true for every float including NaN and so preserves
reflexivity of the ordering.

The price is that `<=` still does not agree with the total order used for
sorting: NaN ranks above `Inf`, but `Inf <= NaN` fails.

<!-- no documentation in the engine source -->
## operator'+='(ref([]t),[]t)

What matters here is cost. The general lowering reads the variable, freezes
the current array into an immutable snapshot, concatenates, and writes the
result back — work proportional to the combined length on every single append.
The compiler can instead emit a guarded in-place append, but only when the
value of the expression is unused and the right-hand side performs no writes;
a runtime guard then rejects arrays that are native-backed or reached through
a domain or accessor and falls back to the copying path. So using the result
of `set X += Y` quietly costs you the fast path.

Being `<transacts>`, appends are journalled and undone when the transaction
fails. On BPVM the `string` specialisation of this operator raises a runtime
error if the combined length would exceed the 2^31-1 byte limit on strings.

<!-- no documentation in the engine source -->
## operator'()'(ref(false,[]u),int)

A reference type in Verse carries two types: one for what may be written
through it and one for what is read back. When the write type is `false` — the
empty type, which has no values at all — nothing can ever be written, so the
reference is read-only. This overload indexes such a reference and produces an
element reference that is read-only in the same way.

It exists only under VerseVM, and it is a fallback: whenever the general
`ref([]t,[]u)` form also applies, the compiler discards this one. Both lower
to exactly the same instruction, a call on the container, so the choice
affects only the type the checker sees. The indexing itself is `<decides>` and
fails for a negative or out-of-range index, and it reads, so it needs an
effect context that permits reads.

<!-- no documentation in the engine source -->
## operator'()'(ref([t]u,[t]v),t)

This is what makes `set M[Key] = Value` work on a map variable: indexing
yields a reference into the map rather than a value. Assigning through that
reference inserts a key that is not yet present. Reading through it does not —
which is exactly why a compound update such as `set M[Key] += 1` fails when
the key is missing, even though the plain assignment beside it would have
created the entry. That asymmetry between `=` and `+=` on maps surprises
nearly everyone once.

The key type is constrained to a subtype of `comparable`, and the value's read
and write types are tracked as separate variables, which is what allows the
result to be usable in both directions.

<!-- no documentation in the engine source -->
## operator'()'(ref(weak_map(t,u),weak_map(t,v)),t)

The weak-map counterpart, and the declaration behind persistent player data:
`set PlayerData[Player] = Stats`. Inserting on write, and failing when a
missing key is read, behave as they do for ordinary maps.

Unlike the read-only variants, this form is implemented on both VMs, and on
BPVM it is mapped onto the very same native helper as the ordinary-map
reference lookup — maps and weak maps share one implementation of element
referencing there.

<!-- no documentation in the engine source -->
## operator'()'(ref(false,weak_map(comparable,v)),comparable)

The read-only weak-map form, and the least preferred of the four reference
lookups: it is discarded whenever either the ordinary-map lookup or the
symmetric weak-map lookup applies, so it only takes over for references that
cannot be written through at all.

Its key parameter is plain `comparable` rather than a type variable, which
spares the checker from solving for a key type. Like the read-only array form
it exists only under VerseVM and compiles to the same call instruction as its
siblings.

<!-- no documentation in the engine source -->
## operator'char32.ToCodePoint'

An extension method taking no arguments, written `C.ToCodePoint()`. It is
total: a `char32` is a Unicode scalar by construction — nothing outside
0 to 0x10FFFF, and nothing in the surrogate range, can be stored in one — so
the code point always exists and the call cannot fail. Its inverse,
`ToChar32`, is fallible precisely because an `int` carries no such guarantee.

Mechanically the receiver arrives as the first parameter and the call's own
empty argument tuple as the second, which is why the intrinsic is a
two-parameter function. That is how extension methods are represented, not
something you write.

<!-- no documentation in the engine source -->
## operator'char.ToAsciiChar32'

Fails for any byte above 127, which looks needlessly strict until you
remember that a `char` in Verse is a single UTF-8 code unit rather than a
character. Bytes 128 to 255 only ever occur as the lead or continuation bytes
of a multi-byte sequence and mean nothing on their own; widening them
individually would silently reinterpret UTF-8 as Latin-1 and produce
mojibake. The operation refuses rather than guess.

When you need non-ASCII text, decode the string as a whole instead of
promoting bytes one at a time.

<!-- no documentation in the engine source -->
## operator'char32.ToAsciiString'

The name undersells it: this encodes any Unicode scalar as UTF-8, emitting
between one and four `char` values, not just ASCII. It cannot fail, because a
`char32` is always a valid scalar and no range check is needed, and it is the
natural counterpart to `ToAsciiChar32`, which handles only the single-byte
case.

Since the result is `[]char` — that is, `string` — one character can lengthen
a string by up to four elements. Any code tracking positions by index is
tracking bytes, not characters.

<!-- no documentation in the engine source -->
## operator'int.ToChar32'

Written `N.ToChar32[]`: it is `<decides>`, so the square brackets are
required. It rejects negatives, anything above 0x10FFFF, and the UTF-16
surrogate range 0xD800 to 0xDFFF, which encodes no scalars of its own and
exists only so that pairs of 16-bit units can address astral characters.

Everything else is accepted, including unassigned code points and the
designated non-characters. This is a scalar-value check, not a check that the
code point means anything in the current version of Unicode.

<!-- no documentation in the engine source -->
## UnsafeCast

Erases all checking, and does so completely. On VerseVM it compiles to a
single register move: the type argument is discarded at compile time and
nothing whatsoever is verified at runtime. On BPVM it copies the
dynamically-typed value through unchanged, likewise ignoring the requested
type. Whatever you claim the value is, the rest of the program believes you,
and being wrong is undefined behaviour rather than a failure you can catch.

The checked alternative is an ordinary type cast inside a failure context,
which actually tests the value and fails when it does not match.

<!-- no documentation in the engine source -->
## PredictsGetDataValue

Looks up a `@predicts` data member on an object by name at runtime and returns
its current value. The name must correspond to a `predicts` var recorded on
the object's class; if it does not, the implementation asserts rather than
failing, so this is not a general reflection facility. Passing something that
is neither an object nor a reference to one, or a null object, raises an
internal runtime error.

The lookup also has a side effect the signature gives no hint of: it marks the
object's field dirty for prediction bookkeeping before the value is read. It
is implemented only for the older VM — the VerseVM code generator has no entry
for it at all.

<!-- no documentation in the engine source -->
## PredictsGetDataRef

The same lookup, yielding a reference to the underlying property instead of a
copy so that the caller can write through it. It shares its implementation
with the value form, including the dirty-marking side effect.

The reference it hands back is a BPVM-style reference rather than the kind
used for array and map element access, which is the stated reason `predicts`
vars of array type are not yet supported: the two reference mechanisms have
not been unified.

<!-- no documentation in the engine source -->
## Inf

A compile-time constant folded straight into the bit pattern
0x7ff0000000000000; there is no runtime lookup or initialisation. Its declared
type is the singleton float range whose lower and upper bounds are both
positive infinity, so it is not merely a `float` that happens to be infinite —
the type admits no other value.

`Inf` is also the only identifier the compiler will accept as a bound in the
`where` clause of a constrained float type, optionally under a unary minus.
Every other bound there must be a literal, and `NaN` is not accepted at all —
even though the unconstrained `float` type is internally the range from `-Inf`
up to `NaN`.

<!-- no documentation in the engine source -->
## NaN

Also folded to a constant, the canonical quiet NaN 0x7ff8000000000000, and
typed as a singleton range whose lower and upper bounds are both NaN. Unlike
IEEE NaN this one is reflexive: `NaN = NaN` succeeds, which is what allows
Verse to promise extensional equality — that two values comparing equal are
genuinely indistinguishable.

The consequences repay a moment's thought. NaN sits at the very top of the
total order used for sorted maps and hashes, above `Inf`, but `<` and `>` are
plain IEEE comparisons and fail on any NaN operand, so the comparison
operators and the sort order disagree. `<=` and `>=` are patched to succeed
when both sides are NaN, so `NaN <= NaN` holds while `NaN < NaN` does not. And
`float` itself is internally the range from `-Inf` to `NaN`, which is why the
upper bound of the unconstrained float type is a NaN rather than an infinity.

VerseVM stores every value NaN-boxed inside the NaN space of a double, so only
certain "pure" NaN payloads are representable. Float arithmetic is guaranteed
to produce those, but a NaN arriving from outside the VM is canonicalised on
the way in.

<!-- no documentation in the engine source -->
## value.AsObject

Returns the members of a JSON object as a map from member name to nested
`value`, and fails for every other JSON kind — array, number, string, `null`
or boolean. Because the members are held in a map rather than a list,
duplicate names in the source text do not survive: the last occurrence wins,
so the map may be smaller than the number of members actually written in the
document.

Nothing is copied on the way out — the nested `value` objects are the same
ones the parse produced, so walking a large document repeatedly is cheap once
`Parse` has run.

<!-- engine text:
Retrieve an object value or fail if value is not a json object
-->
## value.AsArray

Returns the elements in document order, and fails for every other JSON kind.
An empty JSON array succeeds and yields an empty Verse array, so failure
always means "not an array" and never "no elements". Elements are themselves
`value`, which is how you descend a document: alternate `AsArray[]` and
`AsObject[]` to navigate, then finish with one of the scalar accessors.

<!-- engine text:
Retrieve an array value or fail if value is not a json array
-->
## value.AsInt

Succeeds for any JSON *number*, not merely integer-looking ones. A value
written with a fractional part or an exponent was stored as a double and is
truncated towards zero, so `1.9` yields `1` and `-1.9` yields `-1`. Unsigned
literals larger than the greatest signed 64-bit integer saturate at that
maximum rather than failing, and a double outside the 64-bit range is
converted with no range check at all, so treat wildly large numbers as
unreliable.

It fails for strings, booleans, `null`, objects and arrays — including
strings that happen to contain nothing but digits, which is the usual
stumbling block when reading APIs that quote their identifiers. If a field
may legitimately be fractional, read it with `AsFloat` and round it yourself
so that the rounding is visible in your code.

<!-- engine text:
Retrieve an integer value or fail if value is not a json number
-->
## value.AsFloat

Succeeds for any JSON number, widening integer values to `float`. That
widening is lossy above 2^53, so a 64-bit identifier read through `AsFloat`
can come back with its low bits altered; use `AsInt` for anything you intend
to compare for equality. Fails for every non-number kind, `null` included.

<!-- engine text:
Retrieve a float value or fail if value is not a json number
-->
## value.AsString

Succeeds only for JSON strings. Nothing is coerced: a number, boolean or
`null` will not be rendered as text for you. Escape sequences — including
`\uXXXX` — are decoded during the parse, so what you receive holds real
characters rather than backslashes. (The engine's own doc text says "object
value" here; that is a copy-and-paste slip.)

<!-- engine text:
Retrieve an object value or fail if value is not a string
-->
## value.AsNull

Succeeds only for a JSON `null` and carries no payload, so it is purely a
predicate: use it to distinguish an explicitly null field from a missing one,
which `AsObject` reports by failing the map lookup instead.

Worth knowing about the shape of this API as a whole: the corresponding
`AsBool` accessor is commented out of the declaration, so JSON `true` and
`false` are currently unreachable from Verse. All six accessors simply fail
on a boolean, which makes a boolean field indistinguishable from a malformed
one.

<!-- engine text:
Retrieve an object value or fail if value is not null
-->
## Parse

Parses in strict mode: no comments, no trailing commas, no `NaN` or
`Infinity` literals, and no trailing content after the top-level value. Any
violation is a recoverable failure rather than an error, so `Parse[Text]`
belongs in a query and you get no diagnostic explaining what went wrong.

The whole document is materialised eagerly into a tree of `value` objects —
one object per scalar, member and element — so cost and allocation are
proportional to the input, and there is no streaming or lazy variant. The
input is read as a NUL-terminated buffer, so an embedded NUL character would
end the document early rather than being rejected.

<!-- engine text:
Parse a JSON string returning a value with its contents
-->
## party_member_info

An empty class today. It exists so that the generic party group can be typed
as `agent_group_interface(party_member_info)`, giving Epic somewhere to hang
per-member fields later without changing the signature of `GetLocalParty`.
The interface it satisfies, `member_info_interface`, is likewise empty, so at
present the type carries nothing but its identity.

It is `epic_internal`, so creator code can neither construct nor subclass it;
instances only ever arrive from the member map of the group returned by
`GetLocalParty`.

<!-- engine text:
Per-member info for party members. Can be extended with additional fields in future versions.
-->
## GetLocalParty

Party groups are keyed by the pair (owning `simulation_entity`, party
leader's network id). That means two players who really are in the same
platform party share a group only if they are also in the same simulation
entity — the filtering the doc text mentions is a hard partition, not a
courtesy. Within a key the instance is canonical, which is what makes
`A.GetLocalParty() = B.GetLocalParty()` a genuine same-party test and lets a
subscription taken through one member observe every member's joins and
leaves.

The party composition is not something the server knows on its own: a
component on the player controller reports it from the client, and until that
report arrives the player is treated as their own leader. That is the
mechanism behind "a party of at least 1" — you always get a valid group, but
early in a player's lifetime it may be a group of one that later merges.

The implementation is server-only. Called from client code it cannot find the
subsystem, trips an engine assertion and hands back a freshly made empty
group, so treat this as a server-side query.

<!-- engine text:
Returns the party context for `InPlayer`.
Filters by the simulation_entity owning this player.
A player is always in a party of at least 1 (themselves).
-->
## SortBy

A stable merge sort over a copy of the input, so the original array is
untouched, equal elements keep their relative order, and you pay for a
temporary buffer the size of the array on top of the result. Comparison count
is the usual O(n log n), but each comparison is a Verse call, which makes the
callback the dominant cost — for large arrays prefer a `Less` that compares a
single precomputed field.

`Less` must behave as a strict weak ordering, and in particular must *fail*
for elements that are equivalent. A comparison that succeeds in both
directions does not corrupt memory or hang, but the resulting permutation is
arbitrary. Each comparison runs inside its own transaction; should one raise
a runtime error, the remaining comparisons short-circuit and the content
scope halts, so the returned array is never observed in that case.

<!-- engine text:
Stably sort `Array` using `Less` where `Less` succeeding indicates `Left` should precede `Right`
-->
## editable_curve.Evaluate

Delegates to Unreal's `UCurveFloat`, which is single precision throughout:
`Time` is narrowed to a 32-bit float on the way in and the result widened
back on the way out. That matters if you feed it accumulated game time, where
the double you hold may carry more resolution than the curve can distinguish.

Outside the keyed range the answer is decided by the curve's own pre- and
post-infinity extrapolation settings, authored alongside the keys: constant
by default, holding the first or last key's value, with linear, cycle and
oscillate as alternatives. A curve with no keys evaluates to `0.0` at every
time and one with a single key returns that key's value everywhere, so an
unauthored curve fails silently rather than loudly.

<!-- engine text:
Evaluates this float curve at the specified time and returns the result as a float
-->
## debug_draw_duration_policy

Chooses how long a shape lingers, and — less obviously — which of two
rendering paths it takes. Only `FiniteDuration` actually reads the `?Duration`
argument that every drawing method offers; `SingleFrame` and `Persistent`
ignore it. `FiniteDuration` is also the value behind
`DefaultDebugDrawDurationPolicy`, so a bare `DrawSphere(Pos)` leaves a sphere
standing for five seconds.

<!-- engine text:
Enumerated presets for policies describing a desired draw duration.
-->
## debug_draw_duration_policy.SingleFrame

Forces the shape's lifetime to zero, which sends it to the world's transient
line batcher instead of the channel's own one. Three consequences follow: the
`?Duration` you pass is discarded, the shape lives for about one server tick
(the engine substitutes `1/NetServerMaxTickRate` for a zero lifetime), and
neither `Clear` nor `ClearChannel` can retract it, because it is gone before
you could ask. It is also the one policy whose draws are suppressed outright
while the channel is hidden.

This is the policy for per-tick visualisation — a shape re-issued from a loop
every frame, where redrawing is the whole idea.

<!-- no documentation in the engine source -->
## debug_draw_duration_policy.FiniteDuration

The default policy: the shape is queued in the channel's own persistent line
batcher with a lifetime of `?Duration` seconds (`DefaultDebugDrawDuration` is
`5.0`), and expires on its own. Because it lives in the channel's batcher it
can be hidden with `HideChannel` and removed early with `Clear` or
`ClearChannel`.

Watch the boundary: a `?Duration` of zero or less falls back to the transient
world batcher, so `FiniteDuration` with `?Duration := 0.0` behaves exactly
like `SingleFrame`.

<!-- no documentation in the engine source -->
## debug_draw_duration_policy.Persistent

Gives the shape a lifetime of `-1`, meaning it never expires. The only ways it
leaves the screen are `Clear`, `ClearChannel`, or teardown of the Verse content
scope that drew it. `?Duration` is ignored. Useful for marking up static
geometry once at startup rather than re-drawing it every tick, but easy to
leak: nothing will ever tidy these up for you.

<!-- no documentation in the engine source -->
## debug_draw_channel

An empty abstract class whose only job is to be a name. You subclass it with an
empty body — `my_channel := class(debug_draw_channel){}` — and pass the
subclass itself, not an instance, as `debug_draw.Channel`; because it is used
as a class value rather than constructed, `<abstract>` never gets in the way.

Identity is per class, so any number of `debug_draw` instances naming the same
channel are shown, hidden and cleared together, and each channel gets its own
line batcher component on each client.

<!-- engine text:
debug_draw_channel is the base class used to define debug draw channels.
-->
## debug_draw

Built as an archetype — `MyDraw := debug_draw{Channel := my_channel}` — and
then used for as many draws as you like. Every method is `<transacts>` and
defers its real work to transaction commit, so a shape requested inside a
transaction that rolls back is never drawn at all. Drawing is broadcast: each
shape becomes a reliable client RPC to every player controller in the world, so
server-side Verse code draws on everybody's screen.

The `<internal>` constants behind the parameter defaults are yellow
(`NamedColors.Yellow`) for colour, `FiniteDuration` and `5.0` seconds for
duration, `10.0` for `DefaultDebugDrawSize`, `0.0` for thickness and `1.0` for
text font scale. Distances are Unreal centimetres throughout, as the source's
own examples make clear: `?Radius := 200.0` is a two-metre sphere and
`?Thickness := 1.0` is a one-centimetre-thick line.

Two gates are worth knowing about. Debug drawing is active only in editor
builds unless the host game explicitly turns it on, so in a cooked build every
one of these calls early-outs. And there is a global budget of 100 draw calls
per frame shared by all `debug_draw` instances (the console variable
`VerseDebugDraw.DrawLimitPerFrame`); once you exceed it the rest of the frame's
shapes are silently dropped and an on-screen notice appears. `DrawText` is
exempt from that budget.

<!-- engine text:
debug draw class to draw debug shapes on screen.
-->
## debug_draw.Channel

Holds a class, not an instance, and defaults to `debug_draw_channel` itself —
so every `debug_draw` that does not name a channel ends up sharing one. The
channel's unique class ID is what `ShowChannel`, `HideChannel` and
`ClearChannel` key on, and what selects the line batcher your timed and
persistent shapes are stored in. Give each subsystem its own channel and you
can toggle its visualisation independently of the others.

<!-- engine text:
Channel will be used to clear specific debug draw.
-->
## debug_draw.ShowChannel

Enables the channel on every connected player, unhiding the line batcher that
holds its timed and persistent shapes.

In practice this is not optional. Channels start out disabled, and a channel's
line batcher is created hidden when the channel is not yet enabled, so a
freshly written debug-draw pass usually shows nothing at all until
`ShowChannel` has been called once. Reach for it before concluding your
coordinates are wrong.

<!-- engine text:
Show Debug Draw for the channel for all users.
-->
## debug_draw.HideChannel

Disables the channel for every player. Existing geometry is not discarded, just
hidden, and their lifetimes keep counting down while out of sight, so a later
`ShowChannel` reveals whatever has not yet expired. `SingleFrame` draws issued
while the channel is hidden are dropped rather than merely hidden, since they
never reach the channel's batcher.

<!-- engine text:
Hide Debug Draw for the channel for all users.
-->
## debug_draw.ClearChannel

Flushes the channel's line batcher and discards its debug text on every client,
irrespective of which `debug_draw` instance produced them. Like the draw calls
it is deferred to transaction commit. It cannot remove `SingleFrame` shapes,
which live in the shared world batcher and have already expired.

<!-- engine text:
Clears all debug draw for the channel.
-->
## debug_draw.Clear

The narrower sibling of `ClearChannel`: it removes only the shapes and text
drawn by this particular `debug_draw` object, using the object's own identity as
a batch tag, and leaves anything drawn by other instances on the same channel
alone. Prefer it whenever several `debug_draw` values share a channel — which
they do by default, since `Channel` defaults to the same base class for
everyone.

<!-- engine text:
Clears all debug draw from this debug_draw instance.
-->
## debug_draw.DrawSphere((/Verse.org/SpatialMath:)vector3,float=DefaultDebugDrawSize,color=DefaultDebugDrawColor,int=12,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

A wireframe sphere of latitude and longitude rings. `?NumSegments` — default
`12`, clamped up to a minimum of 4 — controls both directions at once, so the
line count is roughly `2 × NumSegments²`: the default already costs 288 lines,
and 32 segments costs over two thousand. Given the 100-draws-per-frame budget
applies to whole shapes rather than lines, it is the renderer rather than the
budget that will complain.

`?Radius` defaults to `DefaultDebugDrawSize`, `10.0` centimetres, which is
small enough to be easy to miss; `?Thickness` of `0.0` gives hairline lines.

<!-- engine text:
Draws a sphere at the named location, and using the provided draw parameters.
-->
## debug_draw.DrawSphere((/UnrealEngine.com/Temporary/SpatialMath:)vector3,float=DefaultDebugDrawSize,color=DefaultDebugDrawColor,int=12,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

An overload for the deprecated `/UnrealEngine.com/Temporary/SpatialMath`
`vector3`. It is a plain Verse-level wrapper that converts the centre with
`FromVector3` and calls the `/Verse.org/SpatialMath` version, so behaviour is
identical. Prefer the other overload in new code; this one exists only so that
older callers keep compiling.

<!-- engine text:
Draws a sphere at the named location, and using the provided draw parameters.
-->
## debug_draw.DrawBox((/Verse.org/SpatialMath:)vector3,(/Verse.org/SpatialMath:)rotation,(/Verse.org/SpatialMath:)vector3=(/Verse.org/SpatialMath:)vector3{Forward:=DefaultDebugDrawSize,Left:=DefaultDebugDrawSize,Up:=DefaultDebugDrawSize},color=DefaultDebugDrawColor,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

A twelve-line box wireframe. The important detail is that `?Extent` is a
half-extent measured outward from `Center` along each axis, so the default of
`10.0` per axis draws a 20-centimetre cube, and passing an extent straight from
a bounding-box size will give you a box twice as large as you expected.
`Rotation` is applied about the centre.

The extent's components are named `Forward`, `Left` and `Up` here, matching
`/Verse.org/SpatialMath`.

<!-- engine text:
Draws a box at the named location, and using the provided draw parameters
-->
## debug_draw.DrawBox((/UnrealEngine.com/Temporary/SpatialMath:)vector3,(/UnrealEngine.com/Temporary/SpatialMath:)rotation,(/UnrealEngine.com/Temporary/SpatialMath:)vector3=(/UnrealEngine.com/Temporary/SpatialMath:)vector3{X:=DefaultDebugDrawSize,Y:=DefaultDebugDrawSize,Z:=DefaultDebugDrawSize},color=DefaultDebugDrawColor,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

The deprecated-`vector3` overload, converting centre, rotation and extent and
forwarding to the `/Verse.org/SpatialMath` version. Note that here the extent's
components are `X`, `Y` and `Z` rather than `Forward`, `Left` and `Up` — the
same numbers in the same order, but a different vocabulary. Prefer the other
overload.

<!-- engine text:
Draws a box at the named location, and using the provided draw parameters
-->
## debug_draw.DrawCapsule((/Verse.org/SpatialMath:)vector3,(/Verse.org/SpatialMath:)rotation,float=DefaultDebugDrawSize,float=25.0,color=DefaultDebugDrawColor,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

Draws a capsule around `Center`, its axis along the rotated up direction, with
a fixed sixteen sides — there is no segment count to tune. `?Height` is the
full height and is halved internally into a half-height that includes the
hemispherical caps, so the cylindrical section is `Height/2 - Radius` long
either side of the centre.

That interacts badly with the defaults: `?Height` defaults to
`DefaultDebugDrawSize` (`10.0`) while `?Radius` defaults to `25.0`, so a
defaulted capsule has no cylindrical section at all and renders as a
sphere-like blob. Pass a `?Height` comfortably greater than twice `?Radius` if
you want something recognisably capsule-shaped.

<!-- engine text:
Draws a capsule at the named location, and using the provided draw parameters.
-->
## debug_draw.DrawCapsule((/UnrealEngine.com/Temporary/SpatialMath:)vector3,(/UnrealEngine.com/Temporary/SpatialMath:)rotation,float=DefaultDebugDrawSize,float=25.0,color=DefaultDebugDrawColor,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

The deprecated-`vector3` overload: it converts `Center` and `Rotation` and
forwards to the `/Verse.org/SpatialMath` version, defaults and quirks included.
Prefer the other overload.

<!-- engine text:
Draws a capsule at the named location, and using the provided draw parameters.
-->
## debug_draw.DrawCone((/Verse.org/SpatialMath:)vector3,(/Verse.org/SpatialMath:)vector3,float=DefaultDebugDrawSize,int=12,float=PiFloat/4.0,float=PiFloat/4.0,color=DefaultDebugDrawColor,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

`Origin` is the apex and `Direction` the axis the cone opens along; `?Height`
is its length along that axis. The two angles are full apex angles in radians,
not half-angles, and are independent, so the cross-section is an ellipse unless
you keep them equal — which makes this a natural fit for drawing view cones and
perception frusta. Both default to `PiFloat / 4.0`, that is 45 degrees, and are
clamped internally into the open interval between 0 and π.

`?NumSides` (default `12`, clamped up to at least 4) is the number of rays
around the rim.

<!-- engine text:
Draws a cone at the named location, and using the provided draw parameters.
-->
## debug_draw.DrawCone((/UnrealEngine.com/Temporary/SpatialMath:)vector3,(/UnrealEngine.com/Temporary/SpatialMath:)vector3,float=DefaultDebugDrawSize,int=12,float=PiFloat/4.0,float=PiFloat/4.0,color=DefaultDebugDrawColor,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

The deprecated-`vector3` overload, converting both vectors and forwarding to
the `/Verse.org/SpatialMath` version. Prefer the other overload.

<!-- engine text:
Draws a cone at the named location, and using the provided draw parameters.
-->
## debug_draw.DrawCylinder((/Verse.org/SpatialMath:)vector3,(/Verse.org/SpatialMath:)vector3,int=12,float=DefaultDebugDrawSize,color=DefaultDebugDrawColor,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

Unusually for this family, the cylinder is specified by its two end centres
rather than a centre and a rotation, which makes it convenient for visualising
a swept path or a spring between two points. `?Radius` defaults to
`DefaultDebugDrawSize` (`10.0`) and `?NumSegments` to `12`, clamped up to at
least 4; each segment costs three lines. If `Start` and `End` coincide the axis
falls back to world up rather than failing.

<!-- engine text:
Draws a cylinder at the named location, and using the provided draw parameters.
-->
## debug_draw.DrawCylinder((/UnrealEngine.com/Temporary/SpatialMath:)vector3,(/UnrealEngine.com/Temporary/SpatialMath:)vector3,int=12,float=DefaultDebugDrawSize,color=DefaultDebugDrawColor,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

The deprecated-`vector3` overload, converting both endpoints and forwarding to
the `/Verse.org/SpatialMath` version. Prefer the other overload.

<!-- engine text:
Draws a cylinder at the named location, and using the provided draw parameters.
-->
## debug_draw.DrawLine((/Verse.org/SpatialMath:)vector3,(/Verse.org/SpatialMath:)vector3,color=DefaultDebugDrawColor,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

The cheapest primitive here — one line, and the unit every other shape is built
out of. `?Thickness` is in centimetres and defaults to `0.0`, which draws a
hairline of constant screen width; give it a positive value when a line needs
to read at distance. Remember that the per-frame draw budget counts calls, so a
polyline stitched together from `DrawLine` calls consumes it one segment at a
time.

<!-- engine text:
Draws a line from Start to End locations, and using the provided draw parameters.
-->
## debug_draw.DrawLine((/UnrealEngine.com/Temporary/SpatialMath:)vector3,(/UnrealEngine.com/Temporary/SpatialMath:)vector3,color=DefaultDebugDrawColor,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

The deprecated-`vector3` overload, converting both endpoints and forwarding to
the `/Verse.org/SpatialMath` version. Prefer the other overload.

<!-- engine text:
Draws a line from Start to End locations, and using the provided draw parameters.
-->
## debug_draw.DrawPoint((/Verse.org/SpatialMath:)vector3,color=DefaultDebugDrawColor,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

A single screen-facing dot. The parameter to watch is `?Thickness`, which is not
a line width here — it is passed straight through as the point's size — and it
defaults to `DefaultDebugDrawThickness`, which is `0.0`. Always pass an
explicit `?Thickness` (a value of ten or twenty reads well) or you will be
hunting for something with no size.

One further oddity: unlike the line-based shapes, a point's colour is
reinterpreted rather than converted from sRGB, so the same `color` renders
noticeably brighter as a point than as a line.

<!-- engine text:
Draws a point at the named location, and using the provided draw parameters.
-->
## debug_draw.DrawPoint((/UnrealEngine.com/Temporary/SpatialMath:)vector3,color=DefaultDebugDrawColor,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

The deprecated-`vector3` overload, converting the position and forwarding to the
`/Verse.org/SpatialMath` version — including the zero default size. Prefer the
other overload.

<!-- engine text:
Draws a point at the named location, and using the provided draw parameters.
-->
## debug_draw.DrawArrow((/Verse.org/SpatialMath:)vector3,(/Verse.org/SpatialMath:)vector3,float=25.0,color=DefaultDebugDrawColor,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

A `DrawLine` from `Start` to `End` plus a two-line arrowhead at the `End`,
which makes it the natural choice for velocities, normals and aim directions —
three lines rather than the line's one.

`?ArrowSize` behaves surprisingly: it is square-rooted before use, so the
head's barbs are `sqrt(ArrowSize)` centimetres long — about five centimetres at
the default of `25.0`. The head therefore grows very slowly, and you need
`?ArrowSize := 400.0` for a twenty-centimetre head.

<!-- engine text:
Draws an arrow pointing from Start to End locations, and using the provided draw parameters.
-->
## debug_draw.DrawArrow((/UnrealEngine.com/Temporary/SpatialMath:)vector3,(/UnrealEngine.com/Temporary/SpatialMath:)vector3,float=25.0,color=DefaultDebugDrawColor,float=DefaultDebugDrawThickness,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration)

The deprecated-`vector3` overload, converting both endpoints and forwarding to
the `/Verse.org/SpatialMath` version. Prefer the other overload.

<!-- engine text:
Draws an arrow pointing from Start to End locations, and using the provided draw parameters.
-->
## debug_draw.DrawText(string,(/Verse.org/SpatialMath:)vector3,color=DefaultDebugDrawColor,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration,float=DefaultDebugTextFontScale,logic=false)

The odd one out: text is not a line-batcher primitive but an entry in the
player's HUD debug-text list, re-submitted every tick and drawn as flat screen
text at the projected world position. It consequently needs the player to have
a HUD, has no thickness, and is the one drawing call exempt from the
hundred-draws-per-frame budget.

`?FontScale` defaults to `1.0` and `?DrawDropShadow` to `false`; a shadow is
worth turning on for text over bright geometry. Under `SingleFrame` each new
piece of text supersedes the single-frame text submitted on earlier frames, so
a label re-drawn every tick updates in place rather than accumulating.

<!-- engine text:
Draws a 3D text using the provided draw parameters.
-->
## debug_draw.DrawText(string,(/UnrealEngine.com/Temporary/SpatialMath:)vector3,color=DefaultDebugDrawColor,debug_draw_duration_policy=DefaultDebugDrawDurationPolicy,float=DefaultDebugDrawDuration,float=DefaultDebugTextFontScale,logic=false)

The deprecated-`vector3` overload, converting the position and forwarding to the
`/Verse.org/SpatialMath` version. Prefer the other overload.

<!-- engine text:
Draws a 3D text using the provided draw parameters.
-->
## log_level

Selects the Unreal log verbosity the message is emitted at on the `LogVerse`
category: `Debug` becomes `VeryVerbose`, `Verbose` becomes `Verbose`, `Normal`
becomes `Log`, and `Warning` and `Error` map to their namesakes. The level is
also carried along when the message is forwarded to a connected editor, where it
drives how the entry is categorised.

Nothing here changes control flow — an `Error` is a log line, not a failure.
The practical distinction is which levels survive default verbosity filtering:
`Normal` and above do, `Verbose` and `Debug` do not.

<!-- engine text:
log levels available for various log commands
-->
## log_level.Debug

The quietest level, emitted as Unreal's `VeryVerbose`. Filtered out under the
default `LogVerse` verbosity, so these lines cost you nothing in a normal
session and appear only once you raise verbosity for the category. Good for the
chatty per-tick tracing you want to leave in the code.

<!-- no documentation in the engine source -->
## log_level.Verbose

Emitted as Unreal's `Verbose`, one step louder than `Debug` and still filtered
out by default. The natural home for diagnostics you want on demand while
investigating a subsystem, without recompiling.

<!-- no documentation in the engine source -->
## log_level.Normal

Emitted as Unreal's `Log`, and the level you get when you say nothing:
`log.DefaultLevel` initialises to `log_level.Normal`. Visible under default
verbosity, which is exactly why it should not be used inside per-frame loops.

<!-- no documentation in the engine source -->
## log_level.Warning

Emitted as Unreal's `Warning`. Visible by default and singled out by log
tooling, so reserve it for conditions a reader should act on rather than for
ordinary progress reporting.

<!-- no documentation in the engine source -->
## log_level.Error

Emitted as Unreal's `Error` and the loudest level available. It is still only a
log line: it does not fail, abort a transaction, or halt execution. If you want
the program to stop, you need a failable expression or a runtime error, not
this.

<!-- no documentation in the engine source -->
## log_channel

An empty abstract class that exists purely to give log output a name. Subclass
it with an empty body and pass the subclass itself — not an instance — as
`log.Channel`; the class's name is then prefixed verbatim to every message the
logger prints, producing lines such as `LogVerse: log_foo: Hello world!`. If
the channel is somehow unset the prefix becomes `None`.

Because the channel is identified by class rather than by instance, several
`log` values can share one channel while differing in their default level, and
the channel name is what editor-side tooling groups messages by.

<!-- engine text:
log_channel is the base class used to define log channels. When printing a message to a log, the log channel class name will be prefixed to the output message.
-->
## log

An archetype-instantiated logger: `LogFoo := log{Channel := log_foo}`, with an
optional `DefaultLevel`. Output goes to Unreal's `LogVerse` category, formatted
as the channel name, a colon and the message, and truncated at 2048 characters
per line.

The interesting part is how it cooperates with transactions. Print calls do not
emit immediately; they are queued and flushed when the enclosing transaction
completes. If the transaction rolls back the lines are still printed, each
prefixed with `(Rolling Back) `, so you can see what a failed branch was doing;
under AutoRTFM the logs of a retried transaction are suppressed entirely so
retries stay invisible. Messages produced inside a client `predicts` context
gain a `<predicts> ` prefix, which makes prediction bugs much easier to read.

One last kindness: because printing is slow enough that a tight logging loop
could trip the engine's hang detector before Verse's own execution-time limit,
each print polls the execution budget and raises a Verse runtime error first.

<!-- engine text:
log class to send messages to the default log
-->
## log.Channel

Has no default, so it must be supplied when you instantiate the logger. It
holds a `log_channel` subclass rather than an instance, and its class name
becomes the prefix on every line this logger emits. Two loggers may name the
same channel — the engine's own example pairs a default-level `log` and a
warning-level `log` on one channel — which keeps related output grouped while
letting call sites stay terse.

<!-- engine text:
Channel class name will be added as a prefix used when printing the message e.g. '[log_channel]: #Message
-->
## log.DefaultLevel

Supplies the `?Level` that `Print` and `PrintCallStack` use when none is given,
and initialises to `log_level.Normal`. Since it is an ordinary field you fix it
at instantiation to make a purpose-built logger — a warning logger, say — and
then call `Print` with no level at all, overriding per call only where it
matters. Being `<predicts>`, it can also be read from predicting code, which is
what lets the string overload of `Print` be `<predicts>` too.

<!-- engine text:
Sets the default log level of the displayed message. See log_level enum for more info on log levels. Defaults to log_level.Normal.
-->
## log.Print(string,log_level=DefaultLevel)

The workhorse. Note that it is not itself native: it is a thin Verse wrapper
around a private, final native implementation, and is declared in the
extension-method form `(log:)Print`, which makes it non-virtual. That is
deliberate — the same native implementation serves the `diagnostic` overload,
and a user-written subclass of `log` must not be able to intercept the call and
read a diagnostic's contents as text.

Being `<computes><predicts>` it is usable from predicting code, unlike the
`diagnostic` overload. The message is prefixed with the channel name and the
whole line truncated at 2048 characters, so very long dumps will be cut short.

<!-- engine text:
Print `Message` using the given log level.
-->
## log.Print(diagnostic,log_level=DefaultLevel)

Prints a `diagnostic` — the opaque message type produced by failure diagnostics
and `GetDiagnostic`, whose text Verse code is deliberately unable to read. This
overload works because the conversion to a string happens inside the engine, in
a final private implementation that a subclass cannot override; the format is
explicitly not stable and should not be parsed.

It is `<computes>` only, without the `<predicts>` the string overload carries,
so it cannot be called from predicting code.

<!-- engine text:
Print `Message` diagnostic using the given log level.
-->
## log.PrintCallStack

Prints the current Verse script call stack: the channel name, a
`Script Stack (N frames):` header, then one function name per line. The stack is
truncated by the engine rather than unbounded, and the whole entry is subject to
the same 2048-character cap as any other log line, so deep stacks will lose
their tail. If no frames are available nothing is printed at all.

Two caveats. Source locations are gathered but not yet displayed — the engine
carries a `TODO` about passing them to the editor for file links — and the
channel name currently appears twice in the output, once from the header and
once from the standard channel prefix, which the engine also flags as a known
wart.

<!-- engine text:
Prints the current script call stack using the given log level.
-->
## Rotation_Deprecated:rotation

An opaque wrapper around Unreal's `FQuat` — four doubles, none of them
exposed to Verse. Because the struct declares no members you cannot build
one field-by-field; you must go through `MakeRotation`,
`MakeRotationFromYawPitchRollDegrees` or `IdentityRotation`. The one
exception is worth knowing: the native quaternion is initialised to
`FQuat::Identity`, so the empty archetype `rotation{}` is the identity
rotation rather than an uninitialised value.

This is the older of Verse's two rotation types. It lives alongside the
`X`/`Y`/`Z` flavour of `vector3` and inherits Unreal's left-handed axis
convention, which is why `MakeRotation`, `GetAxis` and `GetAngle` here
disagree in sign with their counterparts in `/Verse.org/SpatialMath`.
`FromRotation` converts between the two, and it simply copies the
quaternion across — the stored value means exactly the same orientation in
both modules, so only the accessors' sign conventions change. Note that
`rotation` is not `<persistable>`: to save an orientation you must store
its yaw/pitch/roll or axis and angle yourself.

<!-- engine text:
An abstract representation of an orientation change in 3d-space.
-->
## MakeRotation

The axis need not be unit length; it is normalised internally. If
normalisation fails you get the identity rotation instead of a rotation
full of `NaN`s, which is a real safety net, but the test is not quite the
one the engine text implies: the native code rejects the axis when its
squared length falls below `1.0e-8`, i.e. when its length is below roughly
`1.0e-4`, rather than testing each component with `IsAlmostZero[]`.

`AngleRadians` is in radians and is unbounded — values beyond `2 * PiFloat`
simply wrap, and values beyond `PiFloat` produce a quaternion with a
negative real part, which is what makes `GetAngle` report the long way
round. The sign convention is left-handed and matches `ApplyYaw` and the
`ApplyWorldRotation*` family, but not `ApplyPitch` or `ApplyRoll`. The
successor, `MakeRotationRadians` in `/Verse.org/SpatialMath`, negates the
angle to become right-handed and drops the zero-axis guard, so it is not a
drop-in replacement.

<!-- engine text:
Makes a `rotation` from `Axis` and `AngleRadians` using a left-handed sign convention (e.g. a positive rotation around +Z takes +X to +Y). If `Axis.IsAlmostZero[]`, make the identity rotation.
-->
## Rotation_Deprecated:MakeRotationFromYawPitchRollDegrees(float,float,float)

Angles are in degrees, unlike almost everything else in this module.
Internally this builds an Unreal `FRotator(Pitch, Yaw, Roll)` and converts
it to a quaternion, so you get Unreal's intrinsic convention exactly: each
successive rotation is taken about the axes produced by the previous one,
which is why the engine text talks about "the new Y axis" and "the new X
axis". Inputs outside ±180 degrees are accepted, but a round trip through
`GetYawPitchRollDegrees` will fold them back into the canonical ranges.

The clash with `MakeRotation` is narrower than the engine comment suggests
and worth pinning down. Yaw agrees: a positive `YawRightDegrees` is the
same left-handed sense as `MakeRotation` about `+Z`. Pitch and roll are the
odd ones out — they are right-handed, and the native code implements them
by negating the angle before building the quaternion. So a positive pitch
turns the nose up, which is the opposite sense to what `MakeRotation` would
give you about `+Y`.

<!-- engine text:
Makes a `rotation` by applying `YawRightDegrees`, `PitchUpDegrees`, and `RollClockwiseDegrees`, in that order:
 * first a *yaw* about the Z axis with a positive angle indicating a clockwise rotation when viewed from above,
 * then a *pitch* about the new Y axis with a positive angle indicating 'nose up',
 * followed by a *roll* about the new X axis axis with a positive angle indicating a clockwise rotation when viewed along +X.
Note that these conventions differ from `MakeRotation` but match `ApplyYaw`, `ApplyPitch`, and `ApplyRoll`.
-->
## Rotation_Deprecated:IdentityRotation()

Returns `FQuat::Identity`. Since it takes no arguments and is `<converges>`
it is effectively a constant, and it is the default value of
`transform.Rotation`. The archetype `rotation{}` gives the same value, so
this function is mostly about readability at call sites.

The identity is the one rotation whose axis is genuinely undefined, and the
accessors here cope by convention rather than by failing: `GetAngle`
returns `0.0` and `GetAxis` returns the `+X` axis.

<!-- engine text:
Makes the identity `rotation`.
-->
## Rotation_Deprecated:Distance(rotation,rotation)

Computed as `1.0 - Abs(DotProduct(Q1, Q2))` on the underlying unit
quaternions, which works out to `1 - Abs(Cos(Angle/2))`. That makes it
cheap — no inverse trigonometry at all — but it is emphatically not linear
in the angle. Half way up the range is not 90 degrees apart but 120: a
result of `0.5` means `Cos(Angle/2) = 0.5`, so `Angle = 120` degrees. Treat
the value as a monotonic dissimilarity score, ideal for thresholds and for
sorting candidates, not as an angle in disguise.

Taking the absolute value of the dot product is what handles the
quaternion double cover, so a rotation and its negation — the same
orientation — correctly score `0.0`. If you want radians, use
`AngularDistance`.

<!-- engine text:
Returns the 'distance' between `Rotation1` and `Rotation2`. The result will be between:
 * `0.0`, representing equivalent rotations and
 * `1.0` representing rotations which are 180 degrees apart (i.e., the shortest rotation between them is 180 degrees around some axis).
-->
## AngularDistance

Implemented by building the shortest rotation between the two arguments and
asking for its angle, so the result is genuinely the smallest angle in
radians and always lies in `[0.0, PiFloat]` regardless of how the two
rotations were constructed. That involves an `Acos`, so it is a good deal
more expensive than `Distance`; prefer `Distance` when you only need to
compare or threshold.

In `/Verse.org/SpatialMath` this function was renamed
`AngularDistanceRadians`, with a `AngularDistanceDegrees` wrapper beside
it — the rename is the module's general habit of putting the unit in the
name.

<!-- engine text:
Returns the 'smallest angular distance' between `Rotation1` and `Rotation2` in radians.
-->
## ApplyPitch

Post-multiplies the delta onto `InitialRotation`, which is what makes it a
local-frame operation: the pitch is taken about the body's own `+Y` axis
after `InitialRotation` has been applied, not about the world `+Y`. The
result is renormalised, so chaining these in a loop will not drift.

The angle is in radians here, even though the matching constructor
`MakeRotationFromYawPitchRollDegrees` takes degrees. The sign is
right-handed — the native code negates `PitchUpRadians` before building the
quaternion — so positive means nose up. This is the trap the module's own
comment flags: pitch and roll are right-handed while `ApplyYaw` is
left-handed, so a positive pitch and a positive yaw turn in opposite senses
about their respective axes.

<!-- engine text:
Makes a `rotation` by applying `PitchUpRadians` of right-handed rotation around the local +Y axis to `InitialRotation`.
-->
## ApplyRoll

Post-multiplies a roll about the body's own `+X` axis, so it is applied
after `InitialRotation` in the local frame, and the result is renormalised.
Radians, and right-handed by way of an internal sign flip, giving a
positive angle the clockwise sense you would see looking along `+X`.

Together with `ApplyPitch` and `ApplyYaw` this reproduces the composition
that `MakeRotationFromYawPitchRollDegrees` performs, which is why those
four share a sign convention that `MakeRotation` does not.

<!-- engine text:
Makes a `rotation` by applying `RollClockwiseRadians` of right-handed rotation around the local +X axis to `InitialRotation`.
-->
## ApplyYaw

Post-multiplies a yaw about the body's own `+Z` axis onto
`InitialRotation`, in radians, renormalising the result. Unlike
`ApplyPitch` and `ApplyRoll` the angle is passed through unchanged, so this
one is left-handed and agrees with `MakeRotation` and the
`ApplyWorldRotation*` family: positive yaw is clockwise seen from above.

For an upright object whose `Up` has not been tilted, local yaw and world Z
rotation coincide; the moment there is any pitch or roll in
`InitialRotation` they diverge, and `ApplyWorldRotationZ` is the one that
keeps turning about the world vertical.

<!-- engine text:
Makes a `rotation` by applying `YawRightRadians` of left-handed rotation around the local +Z axis to `InitialRotation`.
-->
## ApplyWorldRotationX

Pre-multiplies the delta, so unlike `ApplyPitch`, `ApplyRoll` and
`ApplyYaw` the axis is the fixed world `+X` and not a body axis:
`InitialRotation` happens first, then this rotation is applied on top of it
in world space. The result is renormalised. Radians, and left-handed with
no internal sign flip, matching `MakeRotation`.

There is also a Verse-level `ApplyLocalRotationX` in this module for the
body-axis equivalent; it is written as `RotateBy(MakeRotation(...))` over
`GetLocalForward()`, which is a useful illustration of how the two families
differ.

<!-- engine text:
Makes a `rotation` by applying `AngleRadians` of left-handed rotation around the world +X axis to `InitialRotation`.
-->
## ApplyWorldRotationY

The world-space sibling of `ApplyPitch`: the delta is pre-multiplied about
the fixed world `+Y` axis, so the result is `InitialRotation` followed by
this rotation, and the quaternion is renormalised afterwards. Radians.

Note the sign difference from `ApplyPitch`. This function is left-handed —
the angle reaches the quaternion untouched — whereas `ApplyPitch` negates
it. Swapping one for the other therefore reverses the direction of turn as
well as changing the frame.

<!-- engine text:
Makes a `rotation` by applying `AngleRadians` of left-handed rotation around the world +Y axis to `InitialRotation`.
-->
## ApplyWorldRotationZ

Pre-multiplies a rotation about the fixed world `+Z` axis, so
`InitialRotation` is applied first and this turn is stacked on top of it in
world space; the result is renormalised. Radians, left-handed, agreeing in
sign with both `ApplyYaw` and `MakeRotation`.

This is the one you want for turning a character or camera about the world
vertical, because it is unaffected by any pitch or roll already present in
`InitialRotation`.

<!-- engine text:
Makes a `rotation` by applying `AngleRadians` of left-handed rotation around the world +Z axis to `InitialRotation`.
-->
## RotateBy

Composition, ordered so that `InitialRotation` is applied first and
`AdditionalRotation` second — the native code reverses the quaternion
product to achieve exactly that, since Unreal's `FQuat` multiplication
composes in the opposite order. `AdditionalRotation`'s axis is therefore
interpreted in the frame `InitialRotation` is expressed in, i.e. world
space, which is why `ApplyLocalRotationX` has to build its delta from
`GetLocalForward()` before handing it here.

The result is renormalised on every call, so accumulating thousands of
small rotations will not slowly inflate the quaternion. The successor is
`operator'*'` on two `rotation`s, which keeps the same left-to-right
application order.

<!-- engine text:
Makes a `rotation` by composing `AdditionalRotation` to `InitialRotation`.
-->
## UnrotateBy

Pre-multiplies the inverse of `RotationToRemove`, which cancels a rotation
that was applied after `InitialRotation` — the exact undo of
`RotateBy`. The result is renormalised.

Two footnotes on the engine text. The function it names, `InvertRotation`,
does not exist; the equivalent spelling is
`InitialRotation.RotateBy(RotationToRemove.Invert())`. And the inversion
itself is implemented as the quaternion conjugate, which is only the true
inverse for unit quaternions — safe here, because every `rotation` you can
construct in this module is normalised.

<!-- engine text:
Makes a `rotation` by composing the inverse of `RotationToRemove` from `InitialRotation`. such that InitialRotation = RotateBy(UnrotateBy(InitialRotation, RotationToRemove), RotationToRemove). This is equivalent to RotateBy(InitialRotation, InvertRotation(RotationToRemove))
-->
## Rotation_Deprecated:GetYawPitchRollDegrees()

Returns a three-element `[]float`, so every read is a failable array index
and you need a failure context to get at the numbers. The module's own
source carries a TODO to change this to `tuple(float, float, float)`, which
is what `/Verse.org/SpatialMath` did; prefer that module if the ergonomics
matter to you.

The values come from Unreal's quaternion-to-`FRotator` conversion, so they
are canonicalised: pitch is derived from an arcsine and lands in
`[-90.0, 90.0]`, while yaw and roll come from `Atan2` and land in
`(-180.0, 180.0]`. At the gimbal-lock poles — pitch within a whisker of
±90 — the conversion gives up on separating the two remaining angles,
forcing roll to `0.0` and folding the whole turn into yaw. Round-tripping
through `MakeRotationFromYawPitchRollDegrees` therefore preserves the
orientation but not necessarily your original triple of numbers.

<!-- engine text:
Makes an `[]float` with three elements:
 * *yaw* degrees of `rotation`
 * *pitch* degrees of `rotation`
 * *roll* degrees of `rotation`
using the conventions of `MakeRotationFromYawPitchRollDegrees`.
-->
## Rotation_Deprecated:GetAxis()

Always returns a unit vector. When the quaternion's vector part has a
squared length below `1.0e-8` — a rotation of essentially nothing — there
is no meaningful axis, and Unreal's fallback of `+X` is returned, as the
engine text says.

No sign flip is applied, so the axis pairs with `GetAngle`'s left-handed
angle and a `MakeRotation` round trip returns the axis you supplied. Be
aware that the pair is not reduced to the shortest arc: `GetAngle` can
exceed `PiFloat`, in which case you are looking at the long way round about
this axis rather than the equivalent short rotation about its opposite.

<!-- engine text:
Makes a `vector3` from the axis of `rotation`.
If `rotation` is nearly identity, this will return the +X axis. See also `GetAngle`.
-->
## GetAngle

Computed as `2 * Acos(W)` on the underlying quaternion, so the result is in
radians and never negative, but it ranges over `[0.0, 2*PiFloat]` rather
than `[0.0, PiFloat]`. Build a rotation with an angle of, say, `4.0`
radians and that is what you get back — the function reports the rotation
as authored, not the shortest equivalent.

If you want the shortest angle, `AngularDistance` against
`IdentityRotation()` gives it to you, since that function enforces the
shortest arc first. Use `GetAxis` for the matching axis.

<!-- engine text:
Returns the radians of `rotation` around the axis of `rotation`. See also `GetAxis`.
-->
## MakeShortestRotationBetween(rotation,rotation)

Negates `FinalRotation`'s quaternion when its dot product with
`InitialRotation` is negative — the standard shortest-arc fix for the
quaternion double cover — and then composes the inverse of
`InitialRotation` with the result, renormalising. The consequence is the
guarantee you want: the returned rotation's `GetAngle()` never exceeds
`PiFloat`.

This overload exists only in this deprecated module.
`/Verse.org/SpatialMath` keeps only the `vector3` form, so there you build
the delta yourself by composing with `Invert()`.

<!-- engine text:
Makes the smallest angular `rotation` from `InitialRotation` to `FinalRotation` such that:
`InitialRotation.RotateBy(MakeShortestRotationBetween(InitialRotation, FinalRotation)) = FinalRotation` and
`MakeShortestRotationBetween(InitialRotation, FinalRotation)?.GetAngle()` is as small as possible.
-->
## Rotation_Deprecated:MakeShortestRotationBetween(vector3,vector3)

Neither vector needs to be unit length; the implementation scales by
`Sqrt(LengthSquared(A) * LengthSquared(B))`, so magnitudes cancel out. Only
the directions matter, and the roll about the resulting axis is the minimum
possible — there is no unique answer otherwise.

Two degenerate cases are handled silently rather than by failing. If the
vectors point in opposite directions there is no preferred axis, so the
implementation picks an arbitrary perpendicular and gives you a 180-degree
turn about it; do not rely on which perpendicular. If either vector is zero
the intermediate quaternion collapses to all zeroes and renormalisation
snaps it to the identity, so you get `IdentityRotation()` and no `NaN`.

<!-- engine text:
Makes the smallest angular `rotation` from `InitialVector` to `FinalVector` such that:
`InitialVector.RotateBy(MakeShortestRotationBetween(InitialVector, Vector)) = FinalVector` and
`MakeShortestRotationBetween(InitialVector, FinalVector)?.GetAngle()` is as small as possible.
-->
## MakeComponentWiseDeltaRotation

This is not a geometric difference between two rotations, and it is worth
being blunt about that. Both arguments are converted to Unreal `FRotator`s,
their yaw, pitch and roll are subtracted independently, each result is
wrapped into `(-180.0, 180.0]`, and a quaternion is rebuilt from the
triple. The rotation you get back does not generally take `RotationB` to
`RotationA`; for that, use `MakeShortestRotationBetween`.

What it is good for is per-channel work — feeding three independent
springs, dampers or comparisons for yaw, pitch and roll. Because it routes
through `FRotator` it also inherits that type's gimbal-lock behaviour, so
near ±90 degrees of pitch the yaw and roll channels are not meaningfully
separable. There is no equivalent in `/Verse.org/SpatialMath`.

<!-- engine text:
Makes a new `rotation` from the component wise subtraction of the Euler angle components in `RotationA` by 
the Euler angle components in `RotationB` and ensures the returned value is normalized.
-->
## Rotation_Deprecated:Slerp(rotation,rotation,float)

The `<decides>` effect is doing real work here: the native code checks
`0.0 <= Parameter <= 1.0` up front and simply produces nothing if the
parameter is out of range, so out-of-range values fail rather than
extrapolate. Its successor in `/Verse.org/SpatialMath` dropped the check
and will happily extrapolate past either end, so porting code across
changes the failure behaviour.

Interpolation takes the shorter of the two arcs, chosen by flipping the
sign of the second quaternion when the dot product is negative. When the
two rotations are already nearly aligned — cosine above `0.9999` — the
implementation falls back to a component-wise lerp followed by
normalisation, which avoids dividing by a vanishing sine and is
indistinguishable from a true slerp at that separation.

<!-- engine text:
Used to perform spherical linear interpolation between `From` (when `Parameter = 0.0`) and `To` (when `Parameter = 1.0`). Expects that `0.0 <= Parameter <= 1.0`.
-->
## RotateVector

A quaternion-vector rotation, so it preserves length up to floating-point
error and is equally suitable for directions and for positions about the
origin. It does not normalise `Vector` first, and it does not apply any
scale or translation — for that, `TransformVector` on a `transform`.

The successor spelling in `/Verse.org/SpatialMath` is
`operator'*'(vector3, rotation)`, written `Vector * Rotation`, which reads
in the same left-to-right application order as chained rotations.

<!-- engine text:
Makes a `vector3` by applying `Rotation` to `Vector`.
-->
## UnrotateVector

Applies the inverse rotation, which in practice is the world-to-local
direction: given a `vector3` in world space and the object's `rotation`,
this hands you the vector in the object's own axes. It calls Unreal's
`UnrotateVector` directly, so it is a touch cheaper than building
`Rotation.Invert()` and rotating by that, though the results agree.

`/Verse.org/SpatialMath` has no named equivalent; there you write
`Vector * Rotation.Invert()`.

<!-- engine text:
Makes a `vector3` by applying the inverse of `Rotation` to `Vector`.
-->
## Rotation_Deprecated:Invert()

Implemented as the quaternion conjugate — three sign flips and nothing
else — which is exact and cheap, and is the true inverse because every
`rotation` this module can produce is unit length. No normalisation is
performed.

The engine text's `ApplyRotation` is stale; no such function exists. The
identity it is reaching for is
`Rotation.RotateBy(Rotation.Invert()) = IdentityRotation()`, and
`UnrotateBy` is the shorthand for composing with an inverse in one step.

<!-- engine text:
Makes a `rotation` by inverting `Rotation` such that `ApplyRotation(Rotation, Rotation.Invert())) = IdentityRotation`.
-->
## Rotation_Deprecated:IsFinite()

Tests the four components of the underlying quaternion, not any derived
axis or Euler angles, and returns the rotation itself on success so you can
use it inline in a chain. It says nothing about whether the quaternion is
unit length, so it will not catch a denormalised rotation.

In this module non-finite rotations are hard to come by, because
`MakeRotation` guards against a zero axis and the yaw/pitch/roll
constructor goes through `FRotator`. The check earns its keep for values
arriving from native code or from deserialised data — and in
`/Verse.org/SpatialMath`, where `MakeRotationRadians` has no zero-axis
guard at all.

<!-- engine text:
Returns `Rotation` if it does not contain `NaN`, `Inf` or `-Inf`.
-->
## Transform_Deprecated:transform

Scale, then rotation, then translation, applied in that order — the same
decomposition as Unreal's `FTransform`, which is what it converts to
natively. Every field has a default (unit scale, identity rotation, zero
translation), so `transform{}` is the identity transform and you can supply
only the fields you care about.

It is `<computes>`, so it is pure and usable in constant contexts, but it
is not `<persistable>`: only the `vector3` parts of it could be saved
directly. Apply it with `TransformVector`, or with `TransformVectorNoScale`
when you want orientation and position but not scale. There is no operator
for composing two `transform`s and no inverse; the successor in
`/Verse.org/SpatialMath` replaces `TransformVector` with
`operator'*'(vector3, transform)` and drops the no-scale variant.

<!-- engine text:
A combination of scale, rotation, and translation, applied in that order.
-->
## Transform_Deprecated:transform.Scale

A component-wise multiplier applied to a vector in the transform's own
axes, before the rotation. Defaults to `vector3{X:=1.0, Y:=1.0, Z:=1.0}`.
Nothing validates it, so zero and negative components are accepted — a
negative component mirrors, and a zero one flattens.

Because this module's axes are Unreal's own, the native conversion sends
`Scale` through the same `FVector` path as `Translation`. Its successor
cannot do that: in `/Verse.org/SpatialMath` the `Left` axis is negated
relative to Unreal's `Y`, so `Scale` there has to be treated as a triple of
scalars rather than a direction. That is exactly why
`FromScalarVector3` exists alongside `FromVector3` for converting between
the two modules — use the scalar form for scales.

<!-- engine text:
The scale of this `transform`.
-->
## Transform_Deprecated:transform.Rotation

Defaults to `IdentityRotation()`. Applied after `Scale` and before
`Translation`, so a non-uniform scale is stretched along the transform's
own axes and then the whole thing is turned.

Because it is the deprecated `rotation`, its axis and angle accessors
follow this module's left-handed convention. `FromTransform` converts a
whole `transform` to the `/Verse.org/SpatialMath` type in one step and
copies the quaternion verbatim, so the orientation survives the move
unchanged.

<!-- engine text:
The rotation of this `transform`.
-->
## Transform_Deprecated:transform.Translation

Applied last, after scale and rotation, in the coordinates of whatever
space the transform is expressed in. Defaults to the origin.

Both `TransformVector` and `TransformVectorNoScale` add it, so it is the
one part of a `transform` you cannot opt out of when transforming a point.
If you want to transform a direction rather than a position, subtract the
translation yourself or rotate with `RotateVector` instead.

<!-- engine text:
The location of this `transform`.
-->
## vector2

A pair of doubles named `X` and `Y`, both defaulting to `0.0`, backed
natively by Unreal's `FVector2D` conventions. It is `<computes>` and
`<persistable>`, so it is both usable in constant contexts and safe to
store in a `weak_map` for persistence — which is more than can be said for
`rotation` or `transform`.

There is no two-dimensional vector in `/Verse.org/SpatialMath`, so this
remains the only option even in new code, and it keeps the old `X`/`Y`
naming rather than adopting `Forward`/`Left`. Its `MakeUnitVector` is
failable and rejects both non-finite vectors and vectors whose every
component is within `1.0e-8` of zero, which is the sensible behaviour that
the `/Verse.org/SpatialMath` `vector3` gave up. Equality compares both
components exactly, bit pattern for bit pattern, so vectors that merely
agree to within rounding are not equal — use `IsAlmostEqual` with a
tolerance you choose.

<!-- engine text:
2-dimensional vector with `float` components.
-->
## vector2.X

The first component, conventionally the horizontal one.

<!-- no documentation in the engine source -->
## vector2.Y

The second component, conventionally the vertical one.

<!-- no documentation in the engine source -->
## vector2i

A pair of integers, `X` and `Y`, stored natively as `int64` and defaulting
to `0`. `<computes>` and `<persistable>`, and the natural type for grid
coordinates, tile indices and pixel positions where floating-point drift
would be a nuisance.

The arithmetic on offer is deliberately thin: negation, component-wise
addition and subtraction, multiplication by an `int` on either side, and
`DotProduct`. There is no division, no component-wise product and no
length — the source has an outstanding TODO for the missing operators.
`Equals` is a failable comparison that returns the vector on success, and
`ToVector2i` truncates a `vector2` component-wise and fails if either
component cannot be converted.

<!-- engine text:
2-dimensional vector with `int` components.
-->
## vector2i.X

The first component, conventionally the horizontal one. Being an `int`, a
`vector2i` names a cell rather than a position — a pixel, a tile, a grid
coordinate — where `vector2` names a point that can lie between them.

<!-- no documentation in the engine source -->
## vector2i.Y

The second component, conventionally the vertical one.

<!-- no documentation in the engine source -->
## Vector3_Deprecated:vector3

Three doubles named `X`, `Y` and `Z` that map straight onto Unreal's
`FVector` with no transformation whatsoever: `X` forward, `Y` right, `Z`
up, and hence Unreal's left-handed basis. All three default to `0.0`, so
`vector3{}` is the origin, and the struct is `<computes>` and
`<persistable>`.

The replacement in `/Verse.org/SpatialMath` is not a rename. It calls the
axes `Forward`, `Left` and `Up`, and `Left` is the negation of this type's
`Y`, which turns the basis right-handed and flips the sign convention of
every rotation function in the module. Convert with `FromVector3` for
positions and directions, and with `FromScalarVector3` for magnitude-only
triples such as a scale, since the latter deliberately does not flip the
sign.

One behavioural difference worth carrying across: this module's
`MakeUnitVector` is `<decides>` and fails on a non-finite or almost-zero
vector, whereas the newer one divides unconditionally and will hand you
`NaN` components for a zero-length input.

<!-- engine text:
3-dimensional vector with `float` components.
-->
## vector3.X

Unreal's `X` axis, forward, passed through natively with no sign change.
Defaults to `0.0` and is `@editable`, so it appears in the editor's details
panel. Stored as a `double`, and compared for equality exactly rather than
with a tolerance — reach for `IsAlmostEqual` if that is not what you want.
The corresponding axis in `/Verse.org/SpatialMath` is `Forward`, with the
same sign.

<!-- no documentation in the engine source -->
## vector3.Y

Unreal's `Y` axis, which points to the right in Unreal's left-handed basis.
Defaults to `0.0` and is `@editable`. This is the component that changes
sign in `/Verse.org/SpatialMath`, where the axis is called `Left` and holds
the negation of this value; if you copy a `Y` into a `Left` by hand rather
than using `FromVector3`, you will mirror the vector.

<!-- no documentation in the engine source -->
## vector3.Z

Unreal's `Z` axis, up. Defaults to `0.0` and is `@editable`. It survives
the move to `/Verse.org/SpatialMath` unchanged as `Up`, sign and all. This
is the component that `LengthXY`, `LengthSquaredXY`, `DistanceXY` and
`DistanceSquaredXY` deliberately ignore, which is how you get planar
distances between two points at different heights.

<!-- no documentation in the engine source -->
## modifier

A single-method interface: given a `t`, return a possibly modified `t`.
`Evaluate` is `<reads>`, so a modifier may consult game state but may not
mutate it — a deliberate restriction, because `modifier_stack` re-runs the
entire chain on every evaluation and caches nothing, so a modifier with side
effects would fire an unpredictable number of times.

Note that `modifier_stack` itself implements `modifier(t)`. Stacks therefore
compose: a whole stack can be inserted into another stack as a single entry,
which is the intended way to build grouped or layered modification.

<!-- engine text:
Implemented by classes to provide a method for modification evaluation.
-->
## modifier_stack

Entries are held in an array kept sorted by position, and that array is
`@replicated`, so a stack is a networked, server-authoritative structure
whose composition propagates to clients rather than a local convenience.

Positions are `rational` rather than `int` precisely so that you can always
insert between two existing entries without renumbering anything — there is
always another rational between any two. They are stored exactly as supplied,
deliberately not reduced, so that a position read back matches what was
passed in; comparison reduces and sign-normalises first and then cross
multiplies, so ordering is exact rather than floating point.

Because the class implements `modifier(t)`, a stack is also a modifier, and
nesting stacks is how you express priority bands.

<!-- engine text:
Modifier stacks provide an ordered application of modifiers.
-->
## modifier_stack.Evaluate

Threads `InValue` through every entry in ascending position order, each
modifier seeing the previous one's output; an empty stack returns `InValue`
unchanged. Nothing is memoised — every call re-runs the whole chain, which is
exactly why `modifier.Evaluate` is confined to `<reads>`.

The traversal is written as recursion rather than iteration, one Verse frame
per entry, terminating when the index runs past the end of the array. Deep
stacks therefore cost proportional call depth as well as time, which is worth
remembering if a stack is driven from a per-frame update.

<!-- engine text:
Returns a t which is the input evaluated against each modifier in the stack, executed in position order.
-->
## modifier_stack.AddModifier

Inserts into sorted position, placing a new entry *after* any already sitting
at the same position — so among equal positions insertion order is evaluation
order, and the most recently added modifier has the last word. Prepending and
appending are recognised by comparing against the cached first and last
positions and cost nothing to locate; an insertion strictly inside the
occupied range is a linear scan plus an array shift.

The returned `cancelable` is the only handle for removal, so keep it if the
modifier is not meant to live for ever. `Cancel` unlinks that one entry and
recomputes the cached bounds; calling it a second time is harmless, because
it simply finds no matching entry.

<!-- engine text:
Insert a Modifier at Position in the stack.
If multiple modifiers are added at the same position, they are applied such that the most recently added is the last evaluated.
Returns a cancelable which can be used to remove Modifier from the stack.
-->
## modifier_stack.FirstPosition

A cached copy of the position of the entry at index zero, maintained as
modifiers are added and removed, rather than a value computed on demand.

The wrinkle is the empty case: when the last entry leaves, this resets to the
default `rational` value of zero, which is indistinguishable from a stack
that genuinely holds a modifier at position zero. If the difference matters,
test emptiness separately. The value returned is the exact rational passed to
`AddModifier`, not a reduced form of it.

<!-- engine text:
Returns the current first position in the stack. If the stack is empty, this is the default position (0).
-->
## modifier_stack.LastPosition

The mirror of `FirstPosition`: the position of the final entry, cached and
maintained in step with insertions and removals, and reset to zero when the
stack empties. Together the two bound the occupied range, which is what makes
"apply this after everything currently registered" expressible — pass any
position greater than `LastPosition`. As with `FirstPosition`, zero means
either "empty" or "one modifier at zero".

<!-- engine text:
Returns the current last position in the stack. If the stack is empty, this is the default position (0).
-->
## StickyEvent:sticky_event(type)

A latch rather than a doorbell. Signal it once and it stays signalled: the
payload is stored, and every subsequent `Await` returns that same stored
value immediately instead of suspending. It derives from `event` and reuses
its resume machinery, so ordering and subscription behaviour are inherited.

That difference decides which one to reach for. `event` only reaches tasks
already waiting, so a task that starts a moment too late misses the
notification entirely; `sticky_event` is the right answer for one-shot facts
like "has initialisation finished?", where the answer must survive being
asked late. Call `ClearSignal` to rearm.

Note the parameterless alias is `sticky_event(void)`, not
`sticky_event(tuple())` as with `event()`.

<!-- engine text:
---------------------------------------------------------------------------------------- A *persistent* event state allowing a simple mechanism to coordinate between concurrent tasks: - several tasks wait on the event - another task sets the event signal state and resumes any waiting tasks See `event` for a version of an event that is designed to be successively signaled and stateless.
-->
## sticky_event.IsSignaled

A plain read of the latch bit. Because a signalled event never leaves an
`Await` call suspended, this succeeding also tells you that no awaiters are
pending — the two facts are equivalent, not merely correlated.

The state can change under you in one specific situation: while `Signal` is
resuming the queued tasks, any one of them may call `ClearSignal`, so a task
resumed early can see the event signalled where a task resumed later sees it
clear. Do not treat the answer as stable across a suspension point.

<!-- engine text:
Returns true if the event is in a signaled state. [There will also be no `Await()` calls pending since they are only suspended when not in a signaled state.] Call `Signal()` to set the signaled state and `ClearSignal()` to clear it. Note: The signal state may be cleared while in the middle of a call to `Signal()` as `Await()` tasks are being resumed.
-->
## sticky_event.ClearSignal

Rearms the latch so that subsequent `Await` calls suspend again, and does
nothing if the event was already clear. It leaves the stored payload in
place, which is harmless: a cleared event never hands the payload out.

The implementation asserts that it is running inside a transaction, because
the write must be able to roll back with the surrounding transaction — hence
the `<writes>` effect rather than something weaker. It is the intended way to
turn a one-shot latch into a reusable gate, and calling it from one of the
tasks that `Signal` is resuming is explicitly supported: awaiters resumed
after that point will find the event clear.

<!-- engine text:
Clears the signaled state if it is set. Once the signaled state is clear any new calls to `Await()` will suspend/block until the event is signaled again. If the event is already not in a signaled state then do nothing. Note: This can be called while in the middle of a call to `Signal()` in a resuming `Await()` task so that new calls to `Await()` will suspend.
-->
## sticky_event.Await

If the latch is already set this returns the payload recorded by the original
`Signal` without ever suspending, so every late awaiter observes the *same*
value rather than a fresh one. Otherwise it falls through to `event`'s
implementation, joining the FIFO queue of suspended tasks.

Because it may complete synchronously, do not rely on it yielding: a loop of
`Await` calls on a signalled sticky event never gives up control and will
spin. That is the price of the guarantee that a notification cannot be
missed.

<!-- engine text:
Suspends/blocks the current task until this event is signaled by having another task call `Signal()`. If this event is already in a signaled state then this coroutine completes immediately.
-->
## sticky_event.Signal

Sets the latch, records the payload, and then resumes the queued awaiters in
the order they suspended, each running until it blocks before the next is
resumed. Awaiters that appear during this drain — including ones created by
the tasks being resumed — return immediately, since the latch is now set.

Signalling an already-signalled event is treated as a programming error and
guarded by an engine assertion rather than a Verse runtime error. In a build
with checks enabled it halts; in a build with checks compiled out the second
signal is silently ignored and the stored payload keeps its original value,
which is a quiet way to lose data. Guard with `IsSignaled[]`, or call
`ClearSignal()` first if a repeat signal is legitimate.

<!-- engine text:
The Await() calls' tasks are resumed in the order that they were made and each task will do as much atomic work as it can until it encounters a block/yield in the form of a call to a coroutine/async call whereupon it will cooperatively transfer control to the next Await() task until all the tasks are resumed. If this is called while the signaled state is already set or while in the middle of of a `Signal()` call resuming suspended Await() tasks, it asserts. Call `ClearSignal()` to clear the signaled state and allow calls to `Await()` suspend until signaled again rather than return immediately. The resumed Await() tasks can have more calls to `Await()` in the middle of this call to `Signal()` before they yield. Any such new Await() calls will return immediately() if this event is still in a signaled state. If it is desired to have new Await() calls to suspend until the next signal then a call to `ClearSignal()` must be made in one or more resumed tasks before any new calls to Await() are made (or use the `event` instead).
-->
## member_info_interface

An empty marker interface: it declares no members at all, and implementing it
does nothing except make your class acceptable as the `member_info` argument
of `agent_group` and `agent_group_interface`. Whatever per-member state a
group needs to carry is declared on your implementing class, not here.

Because a group stores its members as `[agent]member_info`, one instance is
associated with each member, and the map is Verse-owned storage, so the
instance stays alive for as long as the membership does. The engine's own
example is `party_member_info` in `/Verse.org/SocialSynergy`, which is the
`member_info` type of the group returned by `player.GetLocalParty()`.

<!-- engine text:
Interface that defines a class as being usable as member info in an agent group
-->
## agent_group_interface

The read-only face of an agent group, parameterised by the `member_info` type
its members carry. It offers a membership map and three events, and no way to
add or remove anyone — that lives on the concrete `agent_group`. This split is
deliberate: `player.GetLocalParty()` hands back an
`agent_group_interface(party_member_info)` precisely so that Verse code can
observe party membership without being able to change it.

The interface is `<unique>`, so each implementing instance has its own
identity and can be compared and used as a map key. Note that the parameter
is a type, not a value: `agent_group_interface(a)` and
`agent_group_interface(b)` are unrelated types, so a function that accepts
groups generally has to be parametric over `member_info` itself.

<!-- engine text:
Interface that defines a class as providing an agent group.
-->
## agent_group_interface.GetMemberMap

Returns the whole membership as an ordinary Verse `map`, which is a value
rather than a view: the result is a snapshot that is safe to hold, iterate and
pass around, and it will not change when the group's membership later does.
Look an individual member up with `Map[Agent]`, which fails when that agent is
not a member — that failure is the intended way to ask "is this agent in the
group?".

The call only `<reads>`, so it is cheap to call again rather than caching, and
re-calling is the only way to see changes. If you need to react to changes
instead of polling, subscribe to the three events.

<!-- engine text:
Get the members of this agent group with their member info
-->
## agent_group_interface.AddMemberEvent

Payload is the agent that joined together with the `member_info` it joined
with, so a subscriber needs no follow-up lookup. Being a `listenable`, it
offers `Subscribe`, which returns a `cancelable` you should keep if the
subscription is not meant to outlive its owner, and `Await`, which suspends
until the next join. There is no `Signal` on `listenable` — signalling belongs
to a separate interface that this one does not extend — so consumers can only
observe.

This fires for genuine joins only. Re-supplying `member_info` for an agent who
is already a member signals `MemberInfoChangeEvent` instead, so a subscriber
that only listens here will see each agent at most once per membership.

<!-- engine text:
Signalled whenever an agent successfully joins this agent group.Passes in the agent that joined along with their member_info.
-->
## agent_group_interface.RemoveMemberEvent

The payload carries the `member_info` that was in force at the moment of
removal, which matters because by the time the callback runs the agent is
already gone from `GetMemberMap` — this event is your last opportunity to see
the departing member's state. Save what you need from it rather than trying to
look the agent up again.

It is an event about group membership, not about the game: nothing here is
triggered by a player disconnecting. It fires only when someone calls
`RemoveMember`, and only when there was in fact a member to remove.

<!-- engine text:
Signalled whenever an agent successfully leaves this agent group.Passes in the agent that left along with their member_info.
-->
## agent_group_interface.MemberInfoChangeEvent

Fires when an agent who is already a member is given a fresh `member_info`
object. Since that happens through the same `AddMember` call used for joining,
this event is what distinguishes "the same member, new state" from "a new
member" — treat the two events as a pair and expect exactly one of them per
successful add.

Only the new `member_info` is passed. If you care about the previous value,
read it out of `GetMemberMap` before the change, or keep it from the
`AddMemberEvent` or earlier `MemberInfoChangeEvent` that delivered it.

<!-- engine text:
Signalled whenever the MemberInfo class is re-instantiated for a given agent.Passes in the agent that was updated along with their new member_info.
-->
## agent_group

A concrete group: a `[agent]member_info` map plus the three events, with
`AddMember` and `RemoveMember` to mutate it. `agent` is `<unique>`, which is
what makes it a legal map key, and membership is therefore by object identity;
the group holds each `member_info` alive for as long as that agent's
membership lasts.

The class knows nothing about the game around it. Membership changes only when
something calls `AddMember` or `RemoveMember`, so an agent whose player has
left the session remains a member until someone removes it. The one group type
shipped in the engine is the party group in `/Verse.org/SocialSynergy`, whose
membership is driven from native code; its public API is exposed as
`agent_group_interface` rather than as the class, which is the pattern to copy
if you build your own group and do not want callers mutating it.

<!-- engine text:
An agent group is defined as a set of agents that share a common ownership.This class stores agents and specific information about each member via the member_info type provided.
-->
## agent_group.GetMemberMap

Hands back the group's backing map directly. Because Verse maps are values,
that is still a snapshot: iterating it or holding on to it is safe, and it
will not reflect subsequent joins and departures.

Indexing it is the cheapest membership test, and it fails rather than
returning an optional, so it composes into a guard: `if (Info :=
Group.GetMemberMap()[Agent])` both proves membership and gives you the
member's state in one step.

<!-- engine text:
Get the members of this agent group with their member info
-->
## agent_group.AddMember

Does double duty. If the agent is not yet a member it joins, and
`AddMemberEvent` is signalled; if it already is, the `member_info` is
replaced and `MemberInfoChangeEvent` is signalled instead. Either way the map
is updated before the event fires, so a subscriber sees a consistent group.

The `result` is consumed through `GetSuccess[]` and `GetError[]`, both of
which are failable, so branch on them rather than expecting a value. In
practice the error branch is reached only if the underlying map assignment
itself fails, and the value returned is a bare `add_member_error` carrying no
detail — so treat a failure as "the add did not happen" and nothing more.

Event delivery is not part of the transaction. The signalling is done in
native code specifically to escape the rollback discipline that a
`<transacts>` function is held to, so subscribers run immediately and are not
un-run if the surrounding transaction later rolls back.

<!-- engine text:
Attempt to add the given agent to this agent group.This function returns a result that will either succeed or return an error.
-->
## agent_group.RemoveMember

Idempotent by design: removing an agent who is not a member is not an error,
it simply reports success, because the end state is the one you asked for. So
this is safe to call speculatively, and it cannot be used to discover whether
an agent was a member — check `GetMemberMap` first if you need to know.

`RemoveMemberEvent` is signalled only when there really was a member, and it
carries the `member_info` that was removed. As implemented, no code path here
ever produces a `remove_member_error`, so the error half of the `result` is
always empty; writing the branch anyway costs little and guards against that
changing.

<!-- engine text:
Attempt to remove the given agent from this agent group.This function returns a result that will either succeed or return an error.
-->
## agent_group.AddMemberEvent

One event object per group instance, so subscriptions are scoped to the group
you subscribe on. It is exposed through `listenable`, which grants `Subscribe`
and `Await` but deliberately not `Signal` — only the group itself, from
native, can raise it.

Signalling is best effort. The native helper that raises the event drops the
signal if the event object is not in a signalable state, and reports nothing
back, which is why `AddMember` returns success regardless of whether
subscribers were reached. Do not treat a successful `AddMember` as proof that
your callback ran.

<!-- engine text:
Signalled whenever an agent successfully joins this agent group.Passes in the agent that joined along with their member_info.
-->
## agent_group.RemoveMemberEvent

Raised from `RemoveMember`, and only when an agent was actually removed, with
the `member_info` that was in effect at that moment. Nothing else in the class
raises it; in particular it is not a hook for players leaving the game.

`Subscribe` returns a `cancelable`, and since the event lives on the group,
a subscription outlives the individual memberships it reports on. Cancel it
when the observer goes away rather than relying on the group being collected.

<!-- engine text:
Signalled whenever an agent successfully leaves this agent group.Passes in the agent that left along with their member_info.
-->
## agent_group.MemberInfoChangeEvent

Raised when `AddMember` is called for an agent that is already a member, i.e.
when the member's `member_info` object is replaced. Subscribing to this as
well as `AddMemberEvent` is the only way to see every state a member has had;
subscribing to just one leaves a gap.

Like the other two, it is signalled from native code outside the transaction
that caused it, so callbacks are not rolled back with the caller, and a
failure to deliver is silently swallowed rather than reported through the
`result` of `AddMember`.

<!-- engine text:
Signalled whenever the MemberInfo class is re-instantiated for a given agent.Passes in the agent that was updated along with their new member_info.
-->
## add_member_error

The declared error type of `agent_group.AddMember`, and nothing more: it is
`<computes>`, has no members, is not subclassed anywhere in the engine, and
the only value ever produced is a bare instance. There is consequently no
information to extract from one — reaching the error branch tells you the add
did not take effect, not why.

That still leaves it worth handling. `GetError[]` is failable, so a caller
that ignores the `result` silently ignores a failed add; writing the branch
also means you will not have to revisit the call site if richer error
subclasses appear later.

<!-- engine text:
Base class for all errors returned from agent_group.AddMember.
-->
## remove_member_error

The declared error type of `agent_group.RemoveMember`. Unlike its counterpart
it is not produced at all by the current implementation: removing a non-member
is treated as success, and no other path fails, so the error half of that
`result` is always empty. It has no members and no subclasses.

Its presence in the signature is what allows the operation to start reporting
failures without breaking callers, so it is reasonable to write the `GetError[]`
branch even though today it can never be taken.

<!-- engine text:
Base class for all errors returned from agent_group.RemoveMember.
-->
## material.OnPropertyChangedFromVerse

<!-- no documentation in the engine source -->
## has_icon

An interface whose entire content is a single mutable property, which makes it
a small but unusual thing in Verse: implementers must supply storage for a
`var` declared on an interface, not merely a method body. Because that property
is `@editable`, a class implementing this gains an icon slot that a creator
fills in from the editor's details panel rather than from code.

Alongside the property the interface declares private `<native_callable>`
accessors, which is how native code reads and writes the icon on any
implementer without knowing the concrete class. The engine's own implementer is
`icon_component`, which routes the property through those accessors to a
private replicated field.

<!-- engine text:
Interface that provides an icon.
-->
## has_icon.Icon

Readable and assignable through the interface, so given any `has_icon` you can
both display its current icon and swap it. `texture` is a reference to an
asset in the project, not image data: you cannot construct one in Verse, so
whatever you assign must have come from an `@editable` property, from a
constant declared elsewhere, or from another object's `Icon`. Assignment
rebinds the reference and copies nothing.

The `@editable` annotation is on the interface declaration, which means every
implementer inherits the editor-exposed slot. An implementing class that wants
the property backed by something other than a plain field — replication, a
change notification — overrides it with getter and setter accessors, as
`icon_component` does.

<!-- engine text:
A texture used as the 2D visual representation of this entity (e.g. an icon or portrait).
-->
## task

Declared `<abstract><final>`, an unusual pair that between them mean creator
code can neither instantiate a `task` nor derive from one: the only way to
obtain a task is from a `spawn` expression.

Of its members only `Await` is public. The phase predicates (`Active[]`,
`Completed[]`, `Canceling[]`, `Canceled[]` and their groupings) and `Cancel()`
are all `epic_internal`, so from creator code a task is effectively a
write-once future you can wait on and nothing more — you cannot ask whether
it finished without waiting for it.

Awaiting is not owning. The awaited task is not registered as a subtask of
the awaiting one, so cancelling the awaiter leaves the task running; this is
the deliberate difference between `spawn` plus `Await` and a structured
concurrency block, where cancelling the parent cancels the child.

<!-- engine text:
---------------------------------------------------------------------------------------- A stateful, asynchronous future used to represent the invoked context for an async expression (such as an invoked coroutine) executing concurrently in a cooperatively multitasked environment over time - having a lifespan of one or more updates / ticks / frames of the Verse runtime system before it completes. A task is usually obtained from the result of a unstructured concurrency `spawn` expression.
-->
## task.Await

Returns immediately only when the task has already reached the "completed"
phase. Every other phase suspends, and that includes both directions of the
obvious hazard: a *cancelled* task never resumes its awaiters, so the call
does not fail, does not error, and simply stays suspended for ever. There is
no way through `Await` alone to distinguish "still working" from "cancelled
and will never answer", which is why awaiting a task you did not spawn
usually wants a `race` against a timeout.

Multiple awaiters are allowed and are resumed in the order they registered.
If the awaiting task is itself cancelled it deregisters automatically, so the
completed task will not try to resume a dead caller.

<!-- engine text:
Wait until the current task has completed - this essentially anchors this task and adds a caller for it to return to at this call point. Notes: - Multiple `Await()` calls can be made on this one same task - essentially giving it multiple callers to return to. - The order that `Await()` calls are accumulated is important - they are woken in first in first out (FIFO) order. - If this task has already completed, then this coroutine completes immediately. - If this task is canceled, this `Await()` coroutine will not be notified and will appear to take forever. - If this `Await()` task is canceled then it will automatically unregister itself to be woken up from this task. - This task is not registered as a subtask to the `Await()` task so if the `Await()` task or any of its calling tasks are canceled, this task will *not* also be canceled as with a standard subtask of a caller.
-->
## capsule_light_component

A capsule light is a point light with a stretched source: internally it drives
a `UPointLightComponent` whose source radius and length describe a capsule
aligned with the entity's local Z axis. With both `SourceRadius` and
`SourceLength` at zero the source degenerates to a mathematical point, which
is how you get a classic point light out of this component; the defaults are
10 cm and 50 cm, a short tube.

It is the one shaped light that does not implement `bounded`, so unlike
`sphere_light_component`, `rect_light_component` and `spot_light_component` it
contributes nothing to its entity's extent no matter how large its attenuation
radius. Everything else — enabling, shadow casting, colour filtering —
comes from `light_component`.

<!-- engine text:
A `capsule_light_component` emits light in all directions into the scene from a capsule shaped source with a specified radius and length. A radius and length of 0 makes it a point light. You can use these
to simulate any kind of light sources that emit in all directions and need an elongated source shape, such as a long light bulb.
-->
## capsule_light_component.OnAddedToSceneInternal

<!-- engine text:
component interface
-->
## capsule_light_component.Intensity

Candelas (lumens per steradian), defaulting to `8.0`. The value is handed
straight to the renderer as soon as you assign it, and the proxy light is
configured with candela units explicitly, so the number means the same thing
regardless of how large you make the capsule's source shape.

`ColorFilter` is applied afterwards as a per-channel multiplier, so the
light's effective output is `Intensity` times the filter; a mid-grey filter
halves a 100 cd light rather than merely tinting it.

<!-- engine text:
Set the visible light intensity emitted in SI unit Candela.
Specified before ColorFilter (which multiplies each color component after the intensity calculation and can change the effective intensity of the light).
-->
## capsule_light_component.AttenuationRadius

Centimetres, defaulting to `option{1000.0}` — a 10 m sphere of influence.
Within that sphere the falloff is inverse-square, with an extra smoothing term
near the tail so the contribution reaches zero rather than being cut off
abruptly. The radius is a performance dial as much as a look dial: the
renderer must consider every surface inside it.

Setting it to `false` does not give you an unbounded light. The renderer has
no representation for "no limit" yet, so an unset radius is passed down to it
as 10 000 cm, or 100 m.

<!-- engine text:
The bounds of the light's visible influence. This clamping of the light's influence is not physically correct but very important for performance,
larger lights cost more. The light falloff is based on Inverse Square law. Towards the tail end of the AttenuationRadius,
there is an additional smoothing factor to fade out the light contribution to 0 to avoid a hard cutoff.
-->
## capsule_light_component.SourceRadius

The capsule's radius in centimetres, measured around the local Z axis; the
default is 10 cm. Growing it softens shadow penumbrae and broadens specular
highlights, because the renderer treats the light as an area rather than a
point. A radius of zero, together with a zero `SourceLength`, reduces the
light to a point source.

Keep the capsule clear of shadow-casting geometry: a source shape that
intersects a wall or floor produces shadowing artefacts, since part of the
emitter is then inside the occluder.

<!-- engine text:
Radius of the source capsule shape in centimeters around the local Z axis. Note that light shapes which intersect shadow casting geometry can cause shadowing artifacts.
-->
## capsule_light_component.SourceLength

The capsule's length in centimetres along the local Z axis, default 50 cm. It
extends the emitter into a tube of total length `SourceLength` capped by
hemispheres of `SourceRadius`, so the entity's orientation matters: rotate the
entity and the highlight streak rotates with it. This is what makes the
capsule light the right choice for strip lights and fluorescent tubes, where a
sphere light would give a point-like highlight.

Zero length collapses the capsule to a sphere of `SourceRadius`, making the
component behave exactly like `sphere_light_component`.

<!-- engine text:
Length of the source capsule shape in centimeters along the local Z axis. Note that light shapes which intersect shadow casting geometry can cause shadowing artifacts.
-->
## collision_interaction

The three cases are ordered from most permissive to most restrictive, and that
order is load-bearing: when the engine resolves a pair it asks each side how it
treats the other's channel and takes the *minimum* of the two answers. One side
saying `Ignore` is therefore a veto, and `Block` only happens when both sides
independently agree to block.

On the C++ side this enum is a straight reinterpretation of UE's
`ECollisionResponse`, so `Ignore`, `Overlap` and `Block` are exactly
`ECR_Ignore`, `ECR_Overlap` and `ECR_Block`. A Verse `collision_profile` and a
hand-authored UE collision response table describe the same thing.

<!-- engine text:
Specifies how a collision volume pair should interact. See collision_profile.
-->
## collision_interaction.Ignore

The pair is invisible to each other in every sense: no overlap or sweep result,
no contact in the solver. Because the pair verdict is the minimum of the two
sides' answers, a single `Ignore` decides the pair on its own — a volume that
ignores the `camera` channel cannot be blocked *by* the camera even if the
camera's own profile blocks everything.

<!-- engine text:
The pair will not be detected by Overlap and Sweep queries. The pair will not collide in the physics simulation.
-->
## collision_interaction.Overlap

Detection without resistance: the pair shows up in overlap and sweep results
and in begin/end overlap events, but the solver never pushes the two apart.
This is the setting for trigger volumes and for visibility or line-of-sight
probes, and it is what `FindSweepHits` reports for everything it passes through
before the first blocking hit.

<!-- engine text:
The pair will be detected by Overlap and Sweep queries. The pair will not collide in the physics simulation.
-->
## collision_interaction.Block

Detection *and* resistance. Sweeps stop at the first blocking hit — that hit is
reported last, since results are sorted by distance — and the physics solver
generates contacts, which is what drives `has_collision`'s begin/end collision
events and their contact points. `Block` requires agreement from both profiles,
so it is the setting you lose most easily by changing only one side.

<!-- engine text:
The pair will be detected by Overlap and Sweep queries. The pair will collide in the physics simulation.
-->
## collision_profile

The profile is the pair of "what am I" (`Channel`) and "how do I treat others"
(`GetChannelInteraction`), and the `Min` of the two directional answers is what
makes the scheme workable: you never have to enumerate object pairs, only
channels, and every relationship is symmetric by construction even though both
halves are authored independently. This is the indirection that lets one wall be
solid to characters and transparent to the camera.

In practice you rarely build one. The factory that turns a channel class plus a
mapping function into a profile is module-`internal`, so from outside
`/Verse.org/SceneGraph` your profiles are the ready-made constants in the
`CollisionProfiles` module — `StationaryBlockAll`, `DynamicOverlapAll`,
`StationaryBlockVisible` (the invisible-wall/glass case) and friends.

Be aware that the current C++ treats a profile largely as data. The response
table it can bake from a profile has no consumer in the engine yet, real
collision filtering comes from the underlying UE body setup, and the queries
that take a bare volume ignore its profile entirely. Treat a profile as a
declaration of intent that the runtime is still catching up with.

<!-- engine text:
A collision profile determines how a volume interacts with other volumes for Overlap queries, Sweep queries, and physics simulation. When two volumes are being tested to see how they interact, the algorithm looks like this:
   GetInteraction(A:collision_profile, B:collision_profile):collision_interaction = 
       InteractionA = B.GetChannelInteraction(A.Channel) 
       InteractionB = A.GetChannelInteraction(B.Channel) 
       return Min(InteractionA, InteractionB) 

-->
## collision_profile.Channel

The channel is an identity, not a behaviour: it is the key that *other* profiles
look up when deciding how to treat this volume. Channels are objects rather than
enum cases, and each built-in channel class wraps one UE `ECollisionChannel`, so
a Verse channel and a UE trace channel are the same thing under the hood.

The default value is a bare `collision_channel`, which the native constructor
initialises to `ECC_MAX` — the sentinel the engine reads as "unset", meaning
"all channels" when it is used to seed a default interaction. A real profile
should always name one of the `CollisionChannels` classes instead.

<!-- engine text:
The collision channel for the owning object.
-->
## collision_profile.GetChannelInteraction

Rather than a table, the response side of a profile is a function value, so it
must be `<computes>` — pure, no reads of mutable state. You discriminate the
channel by class-casting it, as in `if (CollisionChannels.camera[Channel])`,
which reads like a small chain of `if`s and is exactly how the shipped profiles
in `CollisionProfiles` are written; `BlockVisibleInteraction` there is the
canonical two-line example.

Because it is a function rather than data, the native side is set up to call it
once per UE channel and flatten the answers into a response container — so keep
it cheap, and expect it to be asked about channels you did not think about. If
the call cannot be completed the engine substitutes `Block`, which is also the
default mapping a profile starts with, so a profile you forget to configure is
solid to everything rather than invisible.

<!-- engine text:
How the owning object should interact with other objects.GetChannelInteraction is a function which maps a collision_channel to a collision_interaction. It can be implemented as an simple sequence of if statements. For example, to block all channels except camera:
    BlockAllIgnoreCamera(Channel:collision_channel)<computes>:collision_interaction =
        if (CollisionChannels.camera[Channel]):
            return collision_interaction.Ignore
        return collision_interaction.Block
    MyProfile<public>:collision_profile = MakeCollisionProfile(CollisionChannels.dynamic, BlockAllIgnoreCamera)
-->
## CollisionChannels

Six channels, and the set is closed because each one is pinned to a UE trace
channel: `stationary` is `ECC_WorldStatic`, `dynamic` is `ECC_WorldDynamic`,
`avatar` is `ECC_Pawn`, `visibility` is `ECC_Visibility`, `camera` is
`ECC_Camera` and `physics` is `ECC_PhysicsBody`. That mapping is the reason
SceneGraph collision interoperates with content and traces authored the classic
UE way, and the reason you cannot add a channel from Verse.

Two are worth calling out for query work. `visibility` is the channel the
engine itself traces on for bare-volume overlap and sweep queries, so a volume
that ignores `visibility` is effectively unqueryable by that route; and putting
a mesh on `camera`-ignoring profiles is the standard trick for geometry the
camera should pass through.

<!-- engine text:
The set of built-in collision_channels. This is a closed set for now.
-->
## overlap_hit

One hit per intersecting pair, delivered as a `generator`, so the natural use is
`for (Hit := Entity.FindOverlapHits())`. Nothing about the query fails: if the
entity has no physics scene, or nothing intersects, you simply get a generator
that yields nothing.

The count can exceed the number of physical intersections. The converter emits
one hit per *target* `mesh_part` it can resolve for a result, and a single
part-less hit when it can resolve none, so two hits may differ only in their
`TargetMeshHit`. Results whose component belongs to no entity — plain UE actors
with no SceneGraph presence — are dropped before you see them.

Read a hit through `SourceMeshHit` and `TargetMeshHit`. The component and volume
fields are the original, pre-`mesh_hit` shape of this struct, and the volumes in
particular have never carried real data.

<!-- engine text:
The results of an overlap query. See entity.FindOverlapHits(). We will get one overlap_hit for each intersection of any volume in SourceVolumes with any other volume.
-->
## overlap_hit.SourceComponent

Set for a query that started from something in the scene, and `false` for a
query built from a bare shape — `FindOverlapHits(GlobalTransform, Volume)` —
for the honest reason that such a query has no source object at all. Native code
produces this field and `SourceMeshHit` together so the two can never disagree
about who asked.

For the bare-shape case the source `mesh_hit` still has to name an entity, so it
substitutes the target's simulation entity; that is the one place where reading
the source end of a hit tells you about the scene rather than about the query.

<!-- engine text:
The source component and volume (query input). For compound inputs (like an entity hierarchy) this will be a component/volume in that hierarchy. The SourceTransform is the transform of SourceVolume used for the overlap test. For single volume inputs like a sphere, the Source volume and transform are just the inputs to the overlap test, and the component is false.
-->
## overlap_hit.SourceVolume

A placeholder. Every overlap hit points this at a pooled instance of an internal
volume class: the physics scene hands out one dummy per shape index purely so
that hits hash and compare distinctly, and the `has_collision` overlap path uses
a single shared object. There is no shape, radius or profile to read, and no
public type to downcast to.

The information you actually want — which mesh, which part — now travels in
`SourceMeshHit`.

<!-- engine text:
The source volume (query input)
-->
## overlap_hit.SourceGlobalTransform

The world transform at which the source shape was tested, which for an
entity-based query is simply the transform you passed to `FindOverlapHits` (or
the entity's current global transform, for the no-argument form). It is echoed
back so that code handling a batch of hits from a speculative "what would
overlap me *here*" query does not have to carry the query pose alongside.

<!-- engine text:
The source volume transform
-->
## overlap_hit.TargetComponent

The SceneGraph `component` that was intersected — non-optional, because a hit
with no resolvable target component is discarded rather than reported. Note that
it need not be a `mesh_component`: components that own physics directly are
reported as whatever they are, which is why the mesh-specific detail lives in
`TargetMeshHit` and is allowed to be absent there.

<!-- engine text:
The component that was hit by SourceVolume
-->
## overlap_hit.TargetVolume

Like `SourceVolume`, a pooled placeholder rather than the geometry you hit. Even
when it is populated with a per-shape-index dummy it is an internal class, so it
downcasts to none of `collision_sphere`, `collision_box` and friends, and its
`CollisionProfile` is default-constructed rather than the profile of the thing
that was hit. Use `TargetMeshHit` to identify the target.

<!-- engine text:
The volume that was hit by SourceVolume
-->
## overlap_hit.SourceMeshHit

The querying end of the intersection, as an entity plus, where applicable, a
`mesh_component` and `mesh_part`. Its accessors are `<decides>` deliberately:
resolution is deferred to the moment you ask, so `GetHitEntity[]` and
`GetMeshComponent[]` can fail for a hit whose object is gone or which never had
one — a bare-shape query, or an end that owns physics without being a mesh.

For overlaps raised through `has_collision.GetBeginOverlapEvent` this identifies
the `mesh_part` whose event you subscribed to. One caveat on cost-tuned builds:
with `SceneGraph.GenerateMeshHits` set to false, every hit shares a single empty
`mesh_hit`, and all three accessors fail.

<!-- engine text:
Hit data for the source mesh
-->
## overlap_hit.TargetMeshHit

The other end, and the field that explains the hit count. Native code resolves
which `mesh_part`s of the target body a result belongs to and emits one hit for
each; when it can resolve none you get a single hit whose `GetMeshPart[]` fails.

Today that is the *normal* case for overlaps: the underlying `FOverlapResult`
carries no shape index, so only parts that claim a whole body can be named.
Sweeps do better, resolving the part from the hit element index. If you need
part-accurate overlap information, a sweep with a small displacement resolves
targets more precisely than an overlap does.

<!-- engine text:
Hit data for the target mesh
-->
## sweep_hit

The result of tracing a shape or an entity along a displacement vector. Hits
arrive sorted by distance, and the run stops at the first blocking hit — so a
sweep yields every `Overlap` interaction encountered along the way, with the
blocking hit last if there is one. As with overlaps, an entity outside a physics
scene yields an empty generator rather than a failure.

Beyond the contact geometry, the field you will reach for most is
`SourceHitTranslation` (or `SourceHitDistance`): those are what let you place the
swept object *at* the point of contact, which is the whole reason to sweep
instead of overlap.

Sweeps also resolve target `mesh_part`s properly, from the hit element index, so
you may get several hits for one geometric contact — one per part — differing
only in `TargetMeshHit`.

<!-- engine text:
The results of a sweep query. See entity.FindSweepHits(). We will get one sweep_hit for each intersection of any volume in SourceVolumes with any other volume.
-->
## sweep_hit.SourceComponent

Set when the sweep began from something in the scene, `false` when it began from
a bare volume or a line trace, which have no source object. Produced in lockstep
with `SourceMeshHit`, so the two always name the same source, and for the
objectless case the source `mesh_hit` falls back to the target's simulation
entity.

<!-- engine text:
The source component and volume (query input). For compound inputs (like an entity hierarchy) this will be a component/volume in that hierarchy. The SourceGlobalTransform is the transform of SourceVolume at the start of the sweep. For single volume inputs like a sphere, the volume and transform are just the inputs to the sweep, and the component is false.
-->
## sweep_hit.SourceVolume

Placeholder data, as on `overlap_hit`: the physics scene assigns a pooled
internal volume per shape index so that hits stay distinguishable, and there is
no real shape, extent or profile behind it. Identify the swept object through
`SourceMeshHit` instead.

<!-- engine text:
The source volume (query input).
-->
## sweep_hit.SourceStartGlobalTransform

The pose the sweep started from, in world space — the transform you passed in,
not the transform at the moment of contact. It is the anchor for
`SourceHitTranslation`: add that vector to this transform's translation and you
have where the swept shape came to rest.

<!-- engine text:
The source volume transform at the start of the sweep.
-->
## sweep_hit.SourceHitTranslation

A world-space *delta*, not a position: it is the swept shape's location at the
touch point minus the start location. Add it to
`SourceStartGlobalTransform.Translation` to get the resting pose, or compare its
length against your displacement to see how far along the sweep you got.

Because it is derived from the same data as `SourceHitDistance`, the two agree;
the vector form is more convenient when the displacement was not axis-aligned.
A hit that was already penetrating at the start of the sweep reports a zero
translation and a zero distance, so guard against that case if you are using the
value to nudge an object forwards.

<!-- engine text:
The world-space translation (relative to SourceStartGlobalTransform) of SourceVolume when it touches TargetVolume.
-->
## sweep_hit.TargetComponent

The component that was swept into. Non-optional — hits with no resolvable
SceneGraph target are discarded before they reach Verse — and not necessarily a
`mesh_component`, since components that own physics directly participate in
sweeps too.

<!-- engine text:
The component that was hit by SourceVolume.
-->
## sweep_hit.TargetVolume

Another pooled placeholder of an internal element type. Even for shapes that
*do* have a public Verse class this is not that class, and for shapes that do not
(triangle mesh, heightfield, convex hull) there would be nothing to downcast to
anyway. `TargetMeshHit` is the field with real information.

<!-- engine text:
The volume that was hit by SourceVolume.
-->
## sweep_hit.SourceMeshHit

Identifies the swept end: entity, and mesh component and part when there are
any. `mesh_part` is null for whole-entity sweeps, since the query geometry there
is a whole mesh component rather than one of its parts, so expect
`GetMeshPart[]` to fail on this end unless the sweep came from a part-level
system.

The accessors are `<decides>` because access is evaluated lazily, at the point
of use, and they all fail for the shared empty `mesh_hit` handed out when
`SceneGraph.GenerateMeshHits` is disabled.

<!-- engine text:
Hit data for the source mesh
-->
## sweep_hit.TargetMeshHit

The end that was hit, resolved down to the `mesh_part` when the engine can
name one: sweeps carry a hit element index, which is enough to map the contact
onto specific parts of the target body. Where several parts match, you receive
one hit per part with everything else identical; where none match, a single hit
whose `GetMeshPart[]` fails but whose entity and component still resolve.

A target that is not a mesh at all still reports its entity here, with the mesh
fields unset — so prefer `GetHitEntity[]` when all you want is "who did I hit".

<!-- engine text:
Hit data for the target mesh
-->
## sweep_hit.SourceHitDistance

Distance travelled along the sweep before contact, in world units, taken
straight from the underlying trace. It is also the sort key for the generator, so
the first hit you iterate is the nearest and a blocking hit is the last.

Zero has a specific meaning: the pair was already intersecting when the sweep
began. Those initial overlaps are included in the results, and a stable sort
keeps them in shape order at the front of the list rather than in an arbitrary
one.

<!-- engine text:
The Distance along the sweep at which SourceVolume touches TargetVolume.
-->
## sweep_hit.ContactPosition

The world-space impact point on the target surface — not the centre of the swept
shape at the touch pose, which is what `SourceStartGlobalTransform` plus
`SourceHitTranslation` gives you. This is the point to spawn a decal, an impact
effect or a sound at.

<!-- engine text:
The point of contact between SourceVolume and TargetVolume.
-->
## sweep_hit.ContactNormal

The normal as seen by the *swept* shape, which for spheres and capsules is
computed from the shape's centre through the contact point. This makes it the
right normal for reflecting a velocity or resolving penetration, since it points
along the direction the swept object must move to separate. For boxes and for
line traces it coincides with `ContactFaceNormal`.

<!-- engine text:
The normal on TargetVolume at the HitPosition.
-->
## sweep_hit.ContactFaceNormal

The surface normal of the geometry that was hit, which is what you want for
questions about the world rather than about the swept object — is this floor
walkable, which way does this wall face. On an edge or vertex of a polygonal
target, where the true normal is ambiguous, the engine picks the face normal
most opposed to the sweep direction, so a shape sliding into a corner gets a
usable answer rather than an averaged one.

For a sphere or capsule sweep this and `ContactNormal` genuinely differ; for a
box or a line trace they are the same vector.

<!-- engine text:
If TargetVolume is a polygonal object (mesh, convex hull, etc.) and the contact point is on an edge or vertex, this is the most-opposing face normal of the faces that share that edge or vertex. Otherwise it is the same as HitNormal.
-->
## collision_hit

Contacts from the physics solver, as opposed to the query results in
`overlap_hit` and `sweep_hit`. They arrive through `has_collision`'s begin and
end collision events, which fire only for pairs whose profiles resolve to
`Block` — an `Overlap` pair produces overlap events and no contacts.

The struct is deliberately thin: two `mesh_hit`s and the contact points. There
are no volumes and no transforms, because the identity of each end now travels
in the `mesh_hit` pair. As with the query results, one hit is emitted per
resolved target `mesh_part`, and collisions with bodies that have no SceneGraph
component are skipped entirely.

Also worth knowing: the type has no equality operator, so you cannot use a
`collision_hit` as a key to correlate a begin with its matching end. Match on the
target identity you read out of `TargetMeshHit` instead.

<!-- engine text:
The result of a collision in the physics engine. See has_collision::GetCollisionEvent()
-->
## collision_hit.SourceMeshHit

The end that owns the event — the `mesh_part` whose `has_collision` listenable
you subscribed to, together with its component and entity. It is filled from the
subscribing part rather than from the solver's ordering, which matters because
the solver may report the pair in either order; native code swaps the ends (and
negates the contact normals and impulses) so that "source" always means you.

<!-- engine text:
Hit data for the source mesh
-->
## collision_hit.TargetMeshHit

The thing you collided with, resolved to a `mesh_part` where the shape index
identifies one. Either end of a solver contact may be a non-mesh component, in
which case the entity resolves and the mesh fields do not.

This is the field to key on for tracking: the engine itself diffs contacts
frame to frame by target part, and rebuilds end-collision events from nothing but
the recorded target identity.

<!-- engine text:
Hit data for the target mesh
-->
## collision_hit.ContactPoints

Position, normal, impulse and penetration depth per contact, oriented so that
the normal and impulse are expressed from the source side. In current builds a
solver contact yields a single entry rather than a full manifold, so treat the
array as "at least one" rather than "the complete contact set".

The important asymmetry: end-collision events carry an *empty* array. Exits are
reconstructed from the remembered target identity after the contact has already
gone, so there is no contact data left to report — read impulses and depths on
the begin event, and cache anything you need for the end.

<!-- engine text:
Array of physical contact points between the two meshes/mesh_parts.
-->
## collision_volume

The abstract root of the collision shape hierarchy. In practice its concrete
subclasses serve one clearly-working purpose today: as *query* shapes, handed to
the volume-taking overloads of `FindOverlapHits` and `FindSweepHits`. The
supported query shapes are sphere, capsule, box and convex hull; anything else
makes the query fail. Volumes also appear as `SourceVolume`/`TargetVolume` on
hits, where they are pooled placeholders with no real content.

Note the shape's own `GetLocalTransform` is composed with the transform you pass
to the query, so a volume can carry a fixed offset from the pose you supply.
The class is `<predicts>`, so a volume can be built and swept in predicted
client code.

<!-- engine text:
Collision Volumes represent the collision shapes of meshes. They can be detected by Overlap and Sweep queries and generate collisions in the physics simulation.
-->
## collision_volume.Collidable

A replicated flag — `RepNotify`, default `true` — that reads as "this shape
takes part in the physics simulation". Be aware that the native hook the setter
calls to push the change onto the owning body is still a stub, so setting it on
a volume changes the value and replicates it but does not currently reconfigure
anything in the solver.

To actually enable or disable physical collision at runtime, go through
`has_collision.SetCollidable` on the `mesh_part`, which writes the per-shape
collision flags on every associated body.

<!-- engine text:
Enable/disable collision on this volume.
-->
## collision_volume.Queryable

The query-side counterpart of `Collidable`, replicated the same way and
defaulting to `true`. The same caveat applies, and more sharply: the code path
that turns a volume into a query shape never consults this flag, so clearing it
on a volume you pass to `FindOverlapHits` will not stop the query from using it.
It is best read as authored intent rather than a runtime switch.

<!-- engine text:
Enable/disable spatial queries against this volume.
-->
## collision_volume.GetLocalTransform

Returns the volume's transform in its owner's space — the replicated value, not
a world transform, so it is stable regardless of where the owner has moved to.
For a volume being used as a query shape this is the offset that is pre-composed
with the query transform, which is often the easiest way to explain a result
that appears displaced from where you thought you were testing.

<!-- engine text:
Get the transform of this volume in the space of its owner (usually a component on an entity)
-->
## collision_volume.SetLocalTransform

Writes the replicated local transform and notifies the volume that it changed.
Two things follow: the value is authoritative-then-replicated rather than local,
and the notification hook that would tell the owning body about the move is
still unimplemented, so moving a volume that is attached to something does not
yet move its physics representation.

Where it does take effect immediately is on a query volume, because the query
reads the local transform each time it runs. Setting a local offset here is the
supported way to sweep a shape that sits ahead of, or above, the transform you
pass in.

<!-- engine text:
Set the transform of this volume in the space of its owner (usually a component on an entity)
-->
## collision_element

The leaf-shaped half of the hierarchy: one shape, one profile, one material.
The distinction from `collision_volume` matters when you read query results —
a query always reports an element, so a hit against a triangle mesh names the
individual triangle rather than the mesh, and you never have to reason about
which of a compound volume's materials applied.

The catch is that not every shape the physics engine can hit has a public Verse
element class yet. Hits against triangle meshes, heightfields and convex hulls
come back as an internal element type that downcasts to nothing public — and in
current builds the volume fields on hits are placeholders in any case.

<!-- engine text:
Base class for collision_volumes that consist of a single volume with a single collision_profile and collision_material for the whole volume. This covers most volume types used in queries and physics, except compound types like a mesh. A query will always return an element rather than a general volume. For example when colliding with a mesh, the element will be a collision_triangle, which is a collision_element and has a single material, rather than a collision_triangle_mesh, which is not an element and has a material palette.
-->
## collision_element.CollisionProfile

Replicated, `RepNotify`, and defaulting to `CollisionProfiles.StationaryBlockAll`
— a volume you do not configure sits on the static-world channel and blocks
everything.

Two facts about its reach are worth knowing before you rely on it. The native
hook that would push a profile change onto the owning body's shapes is still a
TODO, so setting it stores and replicates a value rather than reconfiguring the
solver; and the bare-volume query paths trace on the `visibility` channel with
an `Overlap` response to every channel, ignoring the profile of the volume you
passed. Filtering that genuinely takes effect today comes from the UE body setup
behind the mesh.

<!-- engine text:
The collision_profile for this volume.
-->
## collision_capsule

Always aligned along its local Z axis; to lie a capsule down, rotate it via
`SetLocalTransform` rather than looking for an axis field. It is one of the four
shapes supported for overlap and sweep queries, which makes it the usual choice
for character-shaped tests.

Defaults are a radius of 50 and a length of 100. Note how the native conversion
builds the query shape: it passes half of `Length` as UE's capsule half-height,
which UE measures including the end caps. The shape a query actually uses is
therefore `Length` tall overall, not `Length + 2 * Radius`.

<!-- engine text:
A collision capsule aligned along the Z axis.
-->
## collision_capsule.Radius

The radius of both hemispherical caps and of the cylindrical section, replicated
with `RepNotify` and defaulting to 50. As with the other shape parameters, the
setter updates the replicated value and calls a modification hook that does not
yet propagate to an owning physics body — but query shapes read the value
afresh on every query, so changing the radius of a volume you sweep takes effect
immediately.

<!-- engine text:
The radius of the capsule
-->
## collision_capsule.Length

The distance between the two cap centres — the cylindrical section only, so the
capsule's full authored height is `Length + 2 * Radius`. Default 100.

Sanity-check this against what the engine does with it: the value is halved and
handed to UE as a capsule half-height, a quantity UE measures cap-to-cap. If you
are matching a capsule to a mesh by eye, verify with a sweep rather than trusting
the arithmetic.

<!-- engine text:
The length of the capsule's cylindrical section (distance between the two end cap centers)
-->
## collision_sphere

The cheapest and best-supported query shape, and the one the engine falls back
to internally when a volume type has no real conversion. It is `<predicts>`, so
client-predicted code can construct one and sweep with it — which, combined with
`FindSweepHits`, is the standard way to do a thick line trace in SceneGraph.

<!-- engine text:
A collision sphere.
-->
## collision_sphere.Radius

Radius in world units, replicated with `RepNotify`, defaulting to 50. Queries
read it at query time, so it is safe to build one sphere and resize it between
sweeps rather than allocating a fresh volume each frame.

<!-- engine text:
The radius of the sphere
-->
## collision_point

A degenerate element with no parameters at all: the native conversion turns it
into a sphere of radius zero. Swept, it behaves like a line trace along the
displacement vector; used for an overlap, it asks "is this exact point inside
anything".

It is `<concrete>`, so unlike most of the hierarchy you can write
`collision_point{}` with no arguments — position and orientation come entirely
from its local transform composed with the query transform.

<!-- engine text:
A collision point.
-->
## collision_box

Axis-aligned in its *own* space, not in world space: the local transform and the
query transform both apply, so a rotated box is perfectly possible — the
constraint is only that the box has no independent orientation of its own.

Its extents are half-sizes, matching UE's convention, and the default is
`{100, 100, 100}` — a 200-unit cube, not a 100-unit one. Getting this wrong by a
factor of two is the most common mistake with box queries; the per-component
accessors that take a member name (`"Forward"`, `"Left"`, `"Up"`) return zero for
any other string rather than failing, so a typo shows up as a flat box.

<!-- engine text:
An axis-aligned collision box.
-->
## collision_box.Extents

The half-dimensions of the box, measured from its centre outwards along each
axis. A box with extents of `(50, 50, 50)` is 100 units on a side.

Half-extents rather than full ones because collision maths works from the centre:
every test becomes a comparison against a distance from the middle.

<!-- no documentation in the engine source -->
## directional_light_component

The light has no position, only a direction: it is read from the entity's
`transform_component` rotation, and the translation is irrelevant to the
lighting result. Because every ray is parallel, there is no attenuation radius
and no source shape to place — which is also why the component does not
implement `bounded`.

The distinction from the other lights shows up in the units. Where the local
lights are specified in candelas, a directional light is specified in lux via
`Illuminance`, because what you are describing is the light arriving at a
surface rather than the output of an emitter.

<!-- engine text:
A `directional_light_component` simulates light that is being emitted from a source that is infinitely far away. This means that all shadows cast by this light will be parallel, making this the ideal choice for simulating sunlight.
-->
## directional_light_component.OnAddedToSceneInternal

<!-- engine text:
component interface
-->
## directional_light_component.Illuminance

Lux, that is lumens per square metre arriving at a surface facing the light.
The default is a very dim `10.0`; for reference, full daylight is on the order
of 100 000 lux, so expect to raise this by orders of magnitude for a sun.
Assigning it pushes the value to the renderer immediately.

As with the other lights, `ColorFilter` multiplies the result per channel
afterwards, so a tinted sun is also a dimmer sun.

<!-- engine text:
Intensity of the light hitting the surface. In Lux (Lumen per square meter).
-->
## directional_light_component.SourceAngleDegrees

The angular diameter of the source as seen from the scene, in degrees. The
default of `0.5357` is the real angular diameter of the Sun, and the editor
offers a 0 to 5 degree slider. The value does not change brightness; it
changes softness, because a wider disc means shadow penumbrae widen with
distance from the occluder and specular highlights spread out.

Set it to zero for a mathematically perfect point at infinity: shadows become
uniformly hard and highlights collapse to pinpricks, which reads as artificial
but is useful for stylised looks.

<!-- engine text:
Angle subtended by light source in degrees (also known as angular diameter). Defaults to 0.5357 which is the angle for our sun.
-->
## has_collision.GetCollidable

True when *any* shape of any physics body associated with this `mesh_part` has
physical collision enabled. That "any" matters for parts backed by several
shapes: a true result does not mean the whole part is solid. The value is read
live from the body instances' per-shape collision-enabled flags, not from a
cached Verse field.

Because the interface's implementation is written as a cast of `Self` to
`mesh_part`, calling it on something that is not a mesh part returns `false`
rather than failing — an easy source of quietly wrong answers if you have
implemented the interface yourself.

<!-- engine text:
True if any associated physics objects are physically collidable
-->
## has_collision.SetCollidable

The call that actually changes physical collision at runtime, unlike the flag of
the same name on `collision_volume`. It writes a replicated value and then, on
both server and client, walks every associated body and rewrites the
collision-enabled setting of each of its shapes — preserving the query and probe
bits, so a shape stays queryable while becoming non-solid.

There is a second, less obvious effect: this also gates the per-frame overlap
search that feeds the begin/end overlap events. Disabling collision unregisters
that update and drops the tracked contact set, and re-enabling starts from empty
by design — a listener then sees begin-overlap events for whatever it is already
touching, rather than a burst of stale end events.

Ordering caution: overlap and collision listeners are signalled inline, so
calling this from inside such a listener re-enters the machinery that is
mid-iteration. The engine defers the reset for exactly that reason, but it means
the effect of your call lands after the current batch has finished being
delivered.

<!-- engine text:
Set the physics collidability for all associated physics objects
-->
## has_collision.GetBeginCollisionEvent

Fires when the solver reports a new contact between one of this part's shapes and
another SceneGraph component's, carrying `collision_hit`s with populated
`ContactPoints` — impulse and penetration depth included. It is the only place
to read that data, so cache what you need for later.

The event payload is a `generator`, and events are signalled per target
`mesh_part`, so a single frame can raise the event several times and each
raising can yield several hits. Contacts with bodies that have no SceneGraph
component, and contacts on shapes belonging to a different part of the same
body, are filtered out before you see them.

Cost is listener-gated: when nothing is subscribed, the per-frame rebuild is
skipped entirely and the tracked contact state is dropped, so a subscriber that
attaches later begins from a clean slate rather than receiving history.

<!-- engine text:
Temp workaround: Once <native> can be written in interfaces, use the listenable that lives on the interfaces directly.
-->
## has_collision.GetEndCollisionEvent

The mirror of the begin event, raised when a tracked contact is absent from the
solver's report for a frame. Getting this to fire at all requires the engine to
ask to be re-dispatched on frames where nothing touches you, which it does while
anything remains tracked — so ends are reliable, with one exception.

Two limitations shape how you use it. The hits carry an *empty* `ContactPoints`
array, because the exit is reconstructed from the remembered target identity
after the contact is gone. And an exit is dropped rather than reported if either
end has been destroyed by the time it would be raised — often the very reason
the contact ended. In out-of-order teardown you can therefore see a begin with
no matching end; if that would leak state, key your bookkeeping on something
whose destruction you can observe independently.

<!-- engine text:
Temp workaround: Once <native> can be written in interfaces, use the listenable that lives on the interfaces directly.
-->
## has_collision.GetBeginOverlapEvent

Overlaps are not solver events but a spatial query the engine runs for you once
per frame over this part's own shapes, using the body's channel and response
table. The set of results is diffed against last frame's, and this event
delivers what is newly present. Initial overlaps are included, and the part's
own actors are excluded, so you will not hear about yourself.

Two practical consequences of it being a query. Non-convex shapes are skipped:
this per-part overlap pass only tests convex geometry, so a part whose collision
is a triangle mesh raises nothing. And it costs real query time every frame the
event has listeners — with none subscribed the whole pass is skipped and the
tracked set cleared, which is why a late subscriber sees begins for everything it
is already inside.

The payload is a `generator`, so each signal delivers a batch of `overlap_hit`s
rather than one. Bear in mind the target-`mesh_part` resolution caveat on
`overlap_hit.TargetMeshHit`: for overlaps specifically, the target part usually
cannot be named.

<!-- engine text:
Temp workaround: Once <native> can be written in interfaces, use the listenable that lives on the interfaces directly.
-->
## has_collision.GetEndOverlapEvent

Delivers the overlaps present last frame and absent this frame, computed by the
same per-frame diff. Because it comes from a query rather than from destruction
notifications, it fires promptly and symmetrically with the begin event — but
only while the pass is running, which means only while collision is enabled and
something is listening.

Note that the exited hits are the *previous frame's* hit values replayed, so the
transforms and identities they carry describe the state when the overlap was
last seen, not the current state. Disabling collision, or removing the part,
clears the tracked set without raising ends for what was touching.

<!-- engine text:
Temp workaround: Once <native> can be written in interfaces, use the listenable that lives on the interfaces directly.
-->
## has_dynamics.GetDynamic

True if any physics body associated with this `mesh_part` is currently
simulating. It is read from the bodies themselves, so it reflects reality rather
than intent — with one useful exception: before the part is wired to an owner,
it falls back to the last replicated value, which is what makes the answer
sensible on a client that has received the state but not yet finished
initialising.

Like the rest of these interface methods it is implemented as a cast of `Self`
to `mesh_part` and returns `false` when that cast fails, so it never fails
outright.

<!-- engine text:
By default, true if any associated physics objects are physically simulated
-->
## has_dynamics.SetDynamic

Does considerably more than flip a flag. It sets a replicated value whose
notification writes the dynamic state onto every associated body; then it tells
the owning `mesh_component` that its dynamism changed, which is what starts or
stops the ticking that pushes simulated transforms into the scene; then it
flushes the mesh transform immediately rather than at the end of the frame; and
finally it asks the entity's physics replication component to gather a first
frame of movement, so the first replicated update is not a frame late.

That bundle is the reason to prefer this over trying to assemble the same effect
from lower-level calls. It is also why toggling dynamism every frame is a bad
idea: each call forces a transform flush and a replication gather.

<!-- engine text:
By default, set the dynamic state for all associated physics objects
-->
## KeyframedMovement

A self-contained module for moving an entity along a canned path: the
`keyframed_movement_component` that does the moving, the
`keyframed_movement_delta` that describes one leg of the journey, the three
playback modes, and the easing curves that shape each leg. Everything is
declared inside the module rather than at scene-graph scope, so you either
qualify names (`KeyframedMovement.linear_easing_function{}`) or pull the
module in with a `using`.

The design is deliberately relative: keyframes are deltas from the previous
keyframe, and `SetKeyframes` rebases the whole path onto wherever the entity
happens to be at the time. That makes a path authored once reusable from any
starting transform.

<!-- engine text:
Animate Scene Graph entities with keyframes.
-->
## KeyframedMovement.easing_function

The abstract base for the curve that reshapes a keyframe's progress. Its one
member, `Evaluate(Input:float):float`, maps normalised time within the
keyframe to normalised progress along it. Because the class is
`<epic_internal>` you cannot write your own easing; in practice every usable
curve is one of the `cubic_bezier_easing_function` subclasses.

Being `<computes>`, constructing an easing has no side effects, which is why
`keyframed_movement_delta.Easing` can default to `linear_easing_function{}` in
a field initialiser.

<!-- engine text:
Base class for an animation easing function.
-->
## KeyframedMovement.cubic_bezier_easing_function

Four floats — `X0`, `Y0`, `X1`, `Y1` — give the two interior control
points of a cubic Bézier running from (0,0) to (1,1), with X as elapsed time
and Y as progress. This is exactly the convention of the CSS `cubic-bezier()`
timing function, and the five named subclasses below carry precisely the CSS
values, so intuitions carried over from web animation transfer directly.

The defaults, (0,0) and (1,1), collapse the curve onto the diagonal and so
describe constant speed. This class is the concrete one, so you can also
construct it directly with your own control points instead of picking a named
preset.

<!-- engine text:
Cubic bezier easing function. See CubicBezierEasingFunctions for some basic easing values.
-->
## KeyframedMovement.cubic_bezier_easing_function.X0

The X coordinate of the first control point. As with CSS easing, the curve runs
from `(0, 0)` to `(1, 1)` and the two control points bend it in between; the X
coordinates must lie in `[0, 1]` so that each progress value has one answer.

<!-- no documentation in the engine source -->
## KeyframedMovement.cubic_bezier_easing_function.Y0

The Y coordinate of the first control point. Y is unconstrained, and taking it
outside `[0, 1]` is how a curve overshoots and settles back.

<!-- no documentation in the engine source -->
## KeyframedMovement.cubic_bezier_easing_function.X1

The X coordinate of the second control point, again restricted to `[0, 1]`.

<!-- no documentation in the engine source -->
## KeyframedMovement.cubic_bezier_easing_function.Y1

The Y coordinate of the second control point.

<!-- no documentation in the engine source -->
## KeyframedMovement.cubic_bezier_easing_function.Evaluate

Maps progress to its eased value by following the curve the four control points
describe.

<!-- no documentation in the engine source -->
## KeyframedMovement.linear_easing_function

Constant speed: the control points sit at (0,0) and (1,1), leaving the curve
on the diagonal. This is the default `Easing` for a
`keyframed_movement_delta`, so a path built without specifying easing moves
uniformly and changes velocity abruptly at each keyframe.

<!-- engine text:
`Linear` animations move at a constant speed.
-->
## KeyframedMovement.linear_easing_function.X0

Fixed at the value that puts the control point on the diagonal, which is what
makes the curve a straight line: progress maps to itself and motion runs at a
constant speed.

<!-- no documentation in the engine source -->
## KeyframedMovement.linear_easing_function.Y0

Fixed at `0.0`. Together with `X0`, also `0.0`, this pins the first control
point to the curve's start, contributing nothing to the shape.

<!-- no documentation in the engine source -->
## KeyframedMovement.linear_easing_function.X1

Fixed at `1.0`, pinning the second control point to the curve's end.

<!-- no documentation in the engine source -->
## KeyframedMovement.linear_easing_function.Y1

Fixed at `1.0`. With `X1` also `1.0` the second control point coincides with
the end point, which is what flattens the Bézier into the straight diagonal.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_cubic_bezier_easing_function

Control points (0.25, 0.1) and (0.25, 1.0) — the CSS `ease` curve. The
asymmetry is intentional: the run-up is short and the settle is long, so the
motion decelerates for most of the keyframe. Use it as the general-purpose
"looks natural" choice; reach for `ease_in_out_cubic_bezier_easing_function`
when you want the acceleration and deceleration to match.

<!-- engine text:
`Ease` animations start slowly, speed up, then end slowly. The speed of the animation is slightly slower at the end than the start.
-->
## KeyframedMovement.ease_cubic_bezier_easing_function.X0

Fixed to the control points of CSS `ease`: slow to start, quick through the
middle, settling over a longer stretch than it took to get going. The asymmetry
is what makes it read as natural.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_cubic_bezier_easing_function.Y0

`0.1`. A small non-zero starting slope, which is what stops `ease` from
feeling completely stationary at the beginning.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_cubic_bezier_easing_function.X1

`0.25`. Placing the second control point this early in time is what stretches
the deceleration across the back three-quarters of the keyframe.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_cubic_bezier_easing_function.Y1

`1.0`, so the second control point sits at full progress and the curve arrives
flat — no motion at the very end of the keyframe.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_in_cubic_bezier_easing_function

Control points (0.42, 0.0) and (1.0, 1.0) — the CSS `ease-in` curve.
Progress starts flat and the entity is still accelerating when the keyframe
ends, so a one-shot animation using this alone stops at full speed. Pair it
with an `ease_out` keyframe at the end of the path if you want a clean
arrival.

<!-- engine text:
`EaseIn` animations start slow, then speed up towards the end.
-->
## KeyframedMovement.ease_in_cubic_bezier_easing_function.X0

Fixed to the control points of CSS `ease-in`: starts from rest and accelerates
the whole way, arriving at speed.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_in_cubic_bezier_easing_function.Y0

`0.0`. Zero starting slope is the whole point of an ease-in: no progress is
made in the first instant.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_in_cubic_bezier_easing_function.X1

`1.0`, pinning the second control point to the end so nothing tempers the
motion on the way out.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_in_cubic_bezier_easing_function.Y1

`1.0`. With `X1` also at `1.0`, the curve reaches its end point at maximum
slope, which is why an ease-in finishes abruptly.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_out_cubic_bezier_easing_function

Control points (0.0, 0.0) and (0.58, 1.0) — the CSS `ease-out` curve, the
mirror image of `ease_in`. Motion begins at full speed and glides to a halt,
so this is what you want on the final keyframe of a path, or for anything that
should feel like it is coming to rest.

<!-- engine text:
`EaseOut` animations start fast, then slow down towards the end.
-->
## KeyframedMovement.ease_out_cubic_bezier_easing_function.X0

Fixed to the control points of CSS `ease-out`: leaves at speed and decelerates
into its destination.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_out_cubic_bezier_easing_function.Y0

`0.0`, and since `X0` is also `0.0` the first control point sits on the start
point, leaving the initial slope steep.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_out_cubic_bezier_easing_function.X1

`0.58`. Pulling the second control point back from the end in time is what
produces the long deceleration.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_out_cubic_bezier_easing_function.Y1

`1.0`, so the curve flattens as it reaches full progress and the entity
settles rather than stopping dead.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_in_out_cubic_bezier_easing_function

Control points (0.42, 0.0) and (0.58, 1.0) — the CSS `ease-in-out` curve.
Unlike `ease`, the two control points are placed symmetrically about the
midpoint, so the ramp up and the ramp down take the same time. This is usually
the better choice for a keyframe that both starts and ends at rest.

<!-- engine text:
`EaseInOut` animations are similar to `Ease` but the start and end animation speed is symmetric.
-->
## KeyframedMovement.ease_in_out_cubic_bezier_easing_function.X0

Fixed to the control points of CSS `ease-in-out`: accelerates away and
decelerates in, symmetric about the midpoint.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_in_out_cubic_bezier_easing_function.Y0

`0.0`: flat at the start, so the entity eases away from rest.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_in_out_cubic_bezier_easing_function.X1

`0.58`, the mirror of `X0`'s `0.42`. That symmetry is what distinguishes this
curve from `ease_cubic_bezier_easing_function`.

<!-- no documentation in the engine source -->
## KeyframedMovement.ease_in_out_cubic_bezier_easing_function.Y1

`1.0`: flat at the end, so the entity eases back to rest.

<!-- no documentation in the engine source -->
## KeyframedMovement.keyframed_movement_playback_mode

Abstract base for how a keyframe path is traversed once `Play` is called. It
is a class hierarchy rather than an enum so a mode can carry parameters in
future; today all three concrete modes are empty and `<computes>`, so you pass
one as a value — `SetKeyframes(Path,
loop_keyframed_movement_playback_mode{})`.

Choice of mode has an observable consequence beyond looping: only one-shot
playback can ever reach the end, so `FinishedEvent` never fires for the other
two, and `Duration` reports the endless case rather than a finite number.

<!-- engine text:
Controls how the animation plays back.
-->
## KeyframedMovement.oneshot_keyframed_movement_playback_mode

Runs the keyframes once and stops at the final one. This is the only mode that
terminates on its own, so it is the only mode for which `FinishedEvent` fires
and the only one that yields a finite `Duration`. Note that stopping this way
leaves the entity at the end of the path; call `Stop` if you want it returned
to where it started.

<!-- engine text:
Play once and stop.
-->
## KeyframedMovement.loop_keyframed_movement_playback_mode

Replays the keyframes from the beginning, indefinitely. Because each keyframe
is a delta, the loop only returns to its starting point if the deltas sum to
nothing — otherwise the entity drifts a full path-length every cycle, which
is a handy way to build a conveyor or a patrolling platform.

<!-- engine text:
Play once and repeat indefinitely.
-->
## KeyframedMovement.pingpong_keyframed_movement_playback_mode

Runs to the end, then back to the start, forever. `KeyframeReachedEvent`
carries an `IsReversed` flag precisely for this mode, so a listener can tell
an outward pass from a return pass over the same keyframe index.

<!-- engine text:
Play continuously reversing direction at each end.
-->
## KeyframedMovement.keyframed_movement_delta

One leg of a path: a change in transform plus the time to take over it and the
curve to take it on. Deltas are chained, each one relative to the pose left by
its predecessor, which is what lets `SetKeyframes` rebase an entire path onto
the entity's current transform.

The class is `<final><concrete>` and its fields are plain data, so a path is
just an ordinary array literal of archetypes.

<!-- engine text:
Represents a change in pose and scale over a duration.
-->
## KeyframedMovement.keyframed_movement_delta.Transform

A delta, not a pose. Translation and scale are added to the previous
keyframe's values rather than replacing them, which is why the field's default
overrides `transform`'s usual scale of (1,1,1) with (0,0,0): zero means "no
scale change".

That default is a trap worth knowing about. Writing `Transform :=
transform{Translation := V}` discards the override and reinstates the (1,1,1)
scale, so every keyframe would add one to the entity's scale. If you set
`Transform` yourself, set `Scale` to the zero vector explicitly unless you
actually want a scale change.

<!-- engine text:
Represents a change in the transform relative to the previous keyframe or initial animation position. Translation and Scale are interpreted additively.
-->
## KeyframedMovement.keyframed_movement_delta.Duration

How long this leg takes, in seconds; the editor clamps it to zero or above. A
duration of zero makes the delta an instantaneous jump, which is how the
component's "teleportation" behaviour is expressed — a single zero-duration
keyframe.

<!-- engine text:
Duration of this keyframe in seconds.
-->
## KeyframedMovement.keyframed_movement_delta.Easing

The curve applied to this leg's progress, defaulting to
`linear_easing_function{}`. Easing is per keyframe, not per path, so you can
ease out of the first leg, run the middle legs linearly, and ease into the
last.

The field is declared with an explicit class qualifier, so in an archetype you
may need to write `(keyframed_movement_delta:)Easing := ...` if a plain
`Easing` would be ambiguous with the `/Verse.org/Verse/Easing` module.

<!-- engine text:
Easing function to use for playback.
-->
## KeyframedMovement.keyframed_movement_component

Drives the entity's transform along a keyframe path, updating in the
pre-physics phase so that physics and anything reading transforms later in the
frame see the new pose. Add it, call `SetKeyframes` to install a path, then
`Play`; the component does not start on its own.

Playback is server-authoritative and replicated as a command rather than as a
stream of transforms — the server publishes the keyframes, the playback mode
and a start time, and each client reconstructs the motion locally. That keeps
bandwidth flat regardless of path length, but it also means the animation is
reproduced from the shared description rather than followed frame by frame.

Because the movement is applied to the entity's own transform, it composes
with the transform hierarchy in the usual way: children follow, and if the
entity's frame of reference is a parent or an `origin`, the animation plays
out relative to that.

<!-- engine text:
Provides teleportation and simple keyframe-based animation for an entity. Animations play back in the Pre-Physics tick phase. When animating an entity with a parent_constraint, animation will be relative to the parent entity.
-->
## KeyframedMovement.keyframed_movement_component.Pause

Freezes playback where it is, leaving the entity at its current interpolated
pose and remembering the position in the path. A later `Play` resumes from
that point rather than restarting. Fires `PausedEvent`. Use this rather than
`Stop` whenever you intend to continue, since `Stop` throws away the progress
and returns the entity to where the path began.

<!-- engine text:
Pause movement. Subsequently calling Play() will resume from the point in the animation when it was paused.
-->
## KeyframedMovement.keyframed_movement_component.Play

Starts the path from the beginning, or resumes it if it was paused, and fires
`PlayedEvent`. It is the only way playback begins — neither adding the
component nor calling `SetKeyframes` starts it. With nothing installed there
is nothing to play, so guard with `HasValidAnimation[]` if the keyframes come
from elsewhere.

<!-- engine text:
Begin or resume playback.
-->
## KeyframedMovement.keyframed_movement_component.Stop()

Halts playback and snaps the entity back to the transform the path was based
on, discarding progress; the next `Play` starts over. This overload is written
in Verse and simply forwards to `Stop(0.0)`, so the return is instantaneous
— reach for the `float` overload when a visible snap would be jarring.

<!-- engine text:
Stop and reset transform to the initial state. Subsequently calling Play() will begin the animation anew.
-->
## KeyframedMovement.keyframed_movement_component.Stop(float)

Halts playback and returns the entity to the transform the path was based on,
blending over `BlendOutTime` seconds instead of snapping. Progress through the
path is still discarded, so the next `Play` begins from the first keyframe.
Passing `0.0` is exactly what the no-argument `Stop` does.

<!-- engine text:
Stop and reset transform to the initial state. Subsequently calling Play() will begin the animation anew.
-->
## KeyframedMovement.keyframed_movement_component.StoppedEvent

Signalled by either `Stop` overload. It fires when the stop is requested, so
with a non-zero blend-out time the entity is still moving when your handler
runs; if you need to act once the entity has actually come to rest, wait out
the blend yourself.

<!-- engine text:
Get the event that fires when the animation is Stopped.
-->
## KeyframedMovement.keyframed_movement_component.PlayedEvent

Signalled by `Play`, for both a fresh start and a resume after `Pause`. It
carries no payload, so if the distinction matters, check `IsPaused[]` before
calling `Play` rather than trying to infer it from the event.

<!-- engine text:
Get the event that fires when the animation begins or resumes Playing.
-->
## KeyframedMovement.keyframed_movement_component.PausedEvent

Signalled by `Pause`. Together with `PlayedEvent` and `StoppedEvent` it lets
other components mirror playback state — driving a sound or a particle
effect for the duration of the movement, say — without polling `IsPlaying[]`
every frame.

<!-- engine text:
Get the event that fires when the animation is Paused.
-->
## KeyframedMovement.keyframed_movement_component.IsPlaying

Succeeds while the path is being traversed. This is a `<decides><reads>`
query, so it belongs in a failure context: `if (Component.IsPlaying[])`. It is
false both before the first `Play` and while paused, so it is not the negation
of `IsPaused[]`.

<!-- engine text:
Is the animation currently playing?
-->
## KeyframedMovement.keyframed_movement_component.IsPaused

Succeeds only in the specific state left behind by `Pause` — stopped
mid-path with progress retained. A component that has never played, or that
has been stopped, satisfies neither this nor `IsPlaying[]`.

<!-- engine text:
Is the animation paused?
-->
## KeyframedMovement.keyframed_movement_component.Duration

The total time the installed path takes, as an optional read; the setter is
private, so this is derived state rather than something you configure. The
option is unset when the duration is not known — including when it cannot be
determined on the server — and holds `Inf` for a path known to run forever.

That last case is the one to watch: a successful `Duration?` is not
necessarily a finite number, so check for `Inf` before using the value in
arithmetic. In practice only one-shot playback yields a usable figure.

<!-- engine text:
Gets the duration in seconds this keyframed movement will take. Fails if a fixed duration is not known (ex: looping animations).
-->
## KeyframedMovement.keyframed_movement_component.FinishedEvent

Signalled when the path has been traversed in full. Only one-shot playback
ever reaches that point, so this event never fires under looping or ping-pong
playback — await it only when you know the mode terminates, or you will wait
forever. It is distinct from `StoppedEvent`, which reflects an explicit
`Stop`.

<!-- engine text:
Get the event that fires when the animations ends, failing if the animation is of infinite duration
-->
## KeyframedMovement.keyframed_movement_component.SetKeyframes

Installs a path and a playback mode. Any animation in progress is stopped
first, and the new keyframes are rebased onto the entity's current transform
— so the same array of deltas describes a different route through the world
depending on where the entity is when you call this.

Playback does not begin here; call `Play` afterwards. Calling `SetKeyframes`
again is the way to swap paths at runtime, and it is safe mid-playback
precisely because it stops and rebases.

<!-- engine text:
Stop any ongoing animation, sets the animation path and rebases it relative to the actor's current transform. Does not start playing until you call Play().
-->
## KeyframedMovement.keyframed_movement_component.HasValidAnimation

Succeeds when a playable set of keyframes is installed. Worth checking before
`Play` when the path was authored in the editor or arrived over the wire
rather than being set by the code that plays it, since `Play` on an empty
component simply does nothing observable.

<!-- engine text:
Is there a valid set of playable keyframes?
-->
## KeyframedMovement.keyframed_movement_component.KeyframeReachedEvent

Fires as each keyframe is reached, with the keyframe's index and whether the
path is currently being traversed backwards. The reversed flag exists for
ping-pong playback, where every index is visited twice per cycle and the two
visits usually mean different things — arriving at a platform versus leaving
it.

Under looping playback the event fires afresh on every cycle, which makes it
the natural hook for effects that should repeat at fixed points along a path.

<!-- engine text:
Signaled when any keyframe is reached. (Keyframe:int, IsReversed:logic).
-->
## KeyframedMovement.keyframed_movement_component.OnInitializedInternal

<!-- engine text:
component interface
-->
## KeyframedMovement.keyframed_movement_component.OnEndSimulationInternal

<!-- no documentation in the engine source -->
## light_component

Every light here is a thin, `<final_super>` façade over Unreal's own light
components. When the entity enters the scene the component spawns a hidden
proxy actor carrying the appropriate `ULightComponent` subclass, pushes the
current property values onto it, and registers an update that copies the
entity's finalised global transform into the proxy in the pre-physics window
whenever the transform changes. Removing the entity from the scene destroys
the proxy.

The `transform_component` dependency is satisfied for you — it is fetched or
created during initialisation — so adding a light to a bare entity works.
Because the properties are replicated, a change made on the server reaches
clients, which reapply it to their own proxy when the value arrives.

Configure rather than subclass: the class is `<abstract>` and its subclasses
are `<final>`, so you use `capsule_light_component`, `sphere_light_component`,
`rect_light_component`, `spot_light_component` or
`directional_light_component` and set their properties.

<!-- engine text:
Base class for light components in the SceneGraph.

Dependencies:
  * `transform_component` on the entity positions the light.

Examples of components implementing `light_component`:
  * `directional_light_component`
  * `capsule_light_component`
  * `sphere_light_component`
  * `rect_light_component`
  * `spot_light_component`
-->
## light_component.OnInitializedInternal

<!-- engine text:
component interface
-->
## light_component.OnUninitializingInternal

<!-- no documentation in the engine source -->
## light_component.OnAddedToSceneInternal

<!-- no documentation in the engine source -->
## light_component.OnRemovingFromSceneInternal

<!-- no documentation in the engine source -->
## light_component.CastShadows

Defaults to `true`, and takes effect the moment you assign it. Turning it off
does not dim the light at all — surfaces still receive its full contribution
— it only stops the light from generating shadow maps, which is usually the
single largest cost a dynamic light carries. A common pattern is a bright hero
light with shadows and several cheap fill lights without.

<!-- engine text:
Whether the light should cast any shadows.
-->
## light_component.ColorFilter

A tint applied in front of the emitter, with each channel in the normalised 0
to 1 range and white by default. Because it multiplies the intensity per
channel it can only ever remove light: there is no way to use it to make a
light brighter.

Note what happens on the way to the renderer. Although `color` holds linear
doubles, the filter is converted to sRGB and quantised to eight bits per
channel, and values outside 0 to 1 are clamped. So the filter gives you 256
steps per channel, and animating it smoothly at the very bottom of the range
will step visibly.

<!-- engine text:
Set the filter color of the light. This acts as a colored filter in front of the light source. Note that this can change the light's effective intensity. In normalized range 0-1.
-->
## light_component.SpecularScale

A non-physical multiplier on this light's specular response, `1.0` by default
and exposed in the editor as a 0 to 1 slider. At `0.0` the light still lights
surfaces diffusely but produces no highlight at all, which is the standard
trick for fill lights that should not betray themselves as a second glint in a
character's eyes.

It pairs with `DiffuseScale`: setting both to zero leaves a light that is
present in the scene, and still costs shadow work if `CastShadows` is on,
while contributing nothing visible.

<!-- engine text:
Multiplier on specular highlights. Can be used to artistically remove highlights mimicking polarizing filters or photo touch up. Any value besides 1.0 is not physical. 0.0 means no specular contribution from this light.
-->
## light_component.DiffuseScale

A non-physical multiplier on this light's diffuse contribution, `1.0` by
default and offered as a 0 to 1 slider in the editor. Zero suppresses diffuse
lighting entirely, leaving only the specular response — the inverse of the
`SpecularScale` trick, and the way to build a light whose only job is to put a
highlight on a surface.

<!-- engine text:
Multiplier on diffuse lighting. Any value besides 1.0 is not physical. 0.0 means no diffuse contribution from this light.
-->
## light_component.Enable

Restores the light by making its proxy light component visible again. The
proxy actor and every property on it survive a `Disable`, so this is a cheap
toggle rather than a rebuild — nothing is respawned and no settings are
lost.

<!-- engine text:
Enables rendering of this light.
-->
## light_component.Disable

Hides the proxy light component, so the light stops contributing to the scene
and stops costing shadow and lighting work. The proxy itself is kept alive
with all of its configuration intact, which is what makes `Enable` and
`Disable` a suitable pair for flickering or for lights that are switched on by
gameplay.

<!-- engine text:
Disables rendering of this light.
-->
## light_component.IsEnabled

Succeeds only when the component has not been disabled *and* the component is
currently in the scene. That second condition is specific to lights: unlike
`mesh_component`, `particle_system_component` and `sound_component`, whose
`IsEnabled` reports the flag alone, a light on an entity that has not yet been
added to the scene reports itself as disabled even though `Enable` was called
on it.

<!-- engine text:
Succeeds if the component is enabled, fails if it's disabled.
-->
## mesh_component

Gives an entity a visible shape: attach one and the entity is drawn using the
mesh it refers to.

It is `<final_super>`, so it cannot be subclassed — configure it rather than
extend it. Being `bounded` it contributes to the entity's extent, and being
`enableable` it can be switched off to hide the entity without removing the
component or losing its settings.

<!-- no documentation in the engine source -->
## mesh_component.OnInitializedInternal

<!-- engine text:
component interface
-->
## mesh_component.OnUninitializingInternal

<!-- no documentation in the engine source -->
## mesh_component.OnAddedToSceneInternal

<!-- no documentation in the engine source -->
## mesh_component.OnRemovingFromSceneInternal

<!-- no documentation in the engine source -->
## mesh_component.OnBeginSimulationInternal

<!-- no documentation in the engine source -->
## mesh_component.OnEndSimulationInternal

<!-- no documentation in the engine source -->
## mesh_component.Enable

Adds the mesh back to the world — both the render representation and the
rigid body, which is returned to the physics scene at the entity's current
transform. It is guarded, so calling it on an already-enabled mesh does
nothing, and it only takes effect if the component is in the scene; enabling a
mesh on a detached entity records the flag and defers the work until the
entity is added.

<!-- engine text:
Enables rendering of this mesh.
-->
## mesh_component.Disable

Removes the mesh from the world entirely: the render representation is taken
out of the scene and the rigid body is removed from the physics scene. That
makes `Disable` considerably more than a visibility switch — a disabled mesh
cannot be collided with, hit by a query, or reported by the overlap events,
and its `GetBoundedGlobalBox` falls back to cached bounds.

Reach for `Visible` instead when you want the geometry to vanish while its
collision keeps working, which is the usual requirement for invisible triggers
and blockers.

<!-- engine text:
Disables rendering of this mesh.
-->
## mesh_component.IsEnabled

Reports the enabled flag alone, without regard to whether the component is in
the scene. So it can succeed for a mesh that is not currently rendered or
simulated, because the entity has not been added to the scene yet — the flag
records intent, and `Enable` reapplies it when the entity arrives. Contrast
`light_component.IsEnabled`, which folds the in-scene check into its result.

<!-- engine text:
Succeeds if the component is enabled, fails if it's disabled.
-->
## mesh_component.Collidable

Defaults to `true`, and writes through to the underlying rigid body as soon as
the value changes; assigning the same value again is skipped, so it is safe to
set from a per-frame update. It governs physical contact only — a mesh with
`Collidable` off is still found by spatial queries and still reports overlaps
unless you also clear `Queryable`.

Being replicated, the setting travels to clients, which reapply it to their
own copy of the body.

<!-- engine text:
Enable/disable collision on this mesh. If enabled, meshes may collide in the physics simulation.
-->
## mesh_component.Queryable

Defaults to `true` and controls two things at once: whether the body answers
spatial queries at all, and whether the per-frame overlap search is running.
Clearing it disconnects that search, which is why `EntityEnteredEvent` and
`EntityExitedEvent` go silent — a useful optimisation for meshes that only
need to block, since the overlap query is real per-frame work.

Setting it back to `true` reconnects the search and seeds the body's overlap
cache first, so entities that were already overlapping are treated as known
rather than firing a burst of spurious entered events.

<!-- engine text:
Enable/disable spatial queries against this mesh. Disabling this field will also disable EntityEnteredEvent/EntityExitedEvent.
-->
## mesh_component.Visible

Defaults to `true` and affects rendering only. Clearing it marks the render
state dirty rather than removing the mesh from the world, so collision,
spatial queries, overlap events and the reported bounds all carry on
unchanged; the change is applied when the render state is next refreshed
rather than inside your assignment.

This is the property for invisible collision volumes and for hiding geometry
briefly. Use `Disable` when you want the mesh to stop existing for physics
too.

<!-- engine text:
Enable/disable visibility of this mesh.
-->
## mesh_component.CanAffectNavigation

Defaults to `true` and, uniquely among these flags, is authoritative on the
server and never replicated — the setter's body is compiled out of
client-only builds, since navigation data is generated server-side. Assigning
it pushes the value onto the rigid body and re-evaluates the body's navigation
relevance, so the navmesh is updated at runtime rather than only at load.

It is a veto, not a grant: the mesh must also have collision that blocks pawns
before it can appear in the navmesh at all. Clearing it on something solid is
the dangerous direction, because NPCs will happily path straight through a
wall that does not affect navigation.

<!-- engine text:
When enabled, this mesh's collision can contribute to AI navigation. Still requires collision that blocks pawns. Use with care: NPCs will not route around meshes that do not affect navigation. Server-authoritative: this value is not replicated.
-->
## mesh_component.EntityEnteredEvent

Signalled once per frame from the mesh's overlap search, for each entity that
was not overlapping last frame and is now. The search only runs while
`Queryable` is set, and it is skipped altogether when nobody is listening, so
subscribing is what turns the cost on. When the search is (re)connected the
currently overlapping set is captured as a baseline, so you are told about
changes from the moment you start listening rather than receiving a backlog.

Because the event is `<predicts>`, handlers can run on a predicting client as
well as on the server.

<!-- engine text:
Triggered at the beginning of each tick when another entity first overlaps this entity.
-->
## mesh_component.EntityExitedEvent

The counterpart to `EntityEnteredEvent`, signalled from the same per-frame
overlap pass for each entity that has stopped overlapping. It shares the same
preconditions: `Queryable` must be set, and the query is skipped when neither
event has listeners — so if you care only about exits you must still leave
`Queryable` on, and you will still pay for the search.

Note that the events describe pairs of overlapping shapes, so an entity is
reported as exited when the geometry separates, not when the entity is
destroyed.

<!-- engine text:
Triggered at the beginning of each tick when another entity is no longer overlapping this entity
-->
## mesh_component.GetMeshParts

Returns the `mesh_part` fields declared on this component's Verse class,
gathered by reflecting over the class chain: fields of the most derived class
first, in declaration order, then each superclass in turn. There is no
underlying cache — every call walks the chain and allocates a fresh array
— so hoist the result out of loops rather than calling it per hit.

Mesh parts also change how the component is set up: a `mesh_component` that
declares any of them is not treated as strictly static, because its parts can
be addressed and altered individually at runtime.

<!-- engine text:
Get mesh_part's on this mesh_component.
-->
## mesh_component.OnPropertyChangedFromVerse

<!-- no documentation in the engine source -->
## mesh_component.GetBoundedGlobalBox

While the mesh is actually in the world this is the live render bounds, which
reflect the real geometry of the mesh asset under the entity's current
transform. Once the mesh is not in the world — because it was disabled, or
the entity has not been added to the scene — it falls back to a local box
cached when the mesh was last added, transformed by the entity's global
transform. The box is therefore always usable but is an approximation for
meshes that are not currently rendered.

`Visible` has no bearing on the result; only `Enable` and `Disable` do.

<!-- engine text:
Returns the bounded box of this component, in world space.
-->
## mesh_component.GetBoundedLocalBox

The same two sources as `GetBoundedGlobalBox`, minus the transform: the impl's
local bounds when the mesh is in the world, otherwise the cached local box.
Since the entity's transform is not applied, scaling the entity does not
change this box — which makes it the right one to use when you want to
reason about the asset itself, and the wrong one for anything involving world
placement.

<!-- engine text:
Returns the bounded box of this component, in local space.
-->
## mesh_part.GetDiagnostic

A debug string, not structured data. The text is the part's full object path,
followed by a count of the physics bodies and shapes it is associated with, and
then a list of which of the capability interfaces its class implements —
`has_collision`, `has_dynamics`, `has_ue_physics_properties`, `has_origin`.

Those two facts are exactly what you want when collision is not behaving: a
part reporting zero bodies and zero shapes has nothing for the solver or the
overlap pass to act on, which explains the silent `false` from `GetCollidable`
and the absence of any collision or overlap events, and the interface list tells
you whether the capability you are calling is even implemented on this part.

<!-- no documentation in the engine source -->
## particle_system_component

Adding this component to a scene spawns a hidden Niagara proxy actor whose
transform is driven from the entity's finalised global transform each time it
changes, and destroys the proxy on removal. Notably, the proxy is never
created on a dedicated server, so the simulation genuinely only exists where
there is something to render; `Play` and `Stop` still replicate, and each
client runs its own copy of the effect.

The system does not auto-activate on its own — the component drives it. That
means playback is entirely a matter of `Enabled`, `AutoPlay` and `Play`, and
those decisions are replicated through a start counter so that a client
joining late, or an entity becoming relevant again, ends up in the same state
as the server.

Subclassing it is how you drive a system's parameters: replicated fields on
the Verse subclass are matched to Niagara user parameters by name and pushed
when the proxy is created and again whenever the field changes.

<!-- engine text:
Used to spawn a `particle_system` at the location of this entity. The `particle_system` will simulate while the `particle_system_component` is in the scene.

Dependencies:
  * `transform_component` on the entity positions the `particle_system`.
-->
## particle_system_component.OnInitializedInternal

<!-- engine text:
component interface
-->
## particle_system_component.OnUninitializingInternal

<!-- no documentation in the engine source -->
## particle_system_component.OnAddedToSceneInternal

<!-- no documentation in the engine source -->
## particle_system_component.OnRemovingFromSceneInternal

<!-- no documentation in the engine source -->
## particle_system_component.OnBeginSimulationInternal

<!-- no documentation in the engine source -->
## particle_system_component.Enable

Returns immediately if the component is already enabled. Otherwise it records
the new state, starts playing if `AutoPlay` is set, and activates the Niagara
system with a reset — so re-enabling an effect restarts it from its first
frame rather than resuming where `Disable` interrupted it.

With `AutoPlay` cleared, `Enable` leaves the effect enabled but idle, waiting
for an explicit `Play`.

<!-- engine text:
Enables the simulation and rendering of this `particle_system`.
-->
## particle_system_component.Disable

Returns immediately if already disabled. Otherwise it stops playback and then
deactivates the Niagara system immediately, which is a harder cut than `Stop`
alone: `Stop` lets already-spawned particles live out their lifetimes, whereas
`Disable` makes them disappear in the same frame. If you want an effect to
trail off, stop it and disable it later.

Being disabled is also a gate on `Play`, which does nothing at all while the
component is disabled.

<!-- engine text:
Disables the simulation and rendering of this `particle_system`.
-->
## particle_system_component.IsEnabled

Reports the `Enabled` flag and nothing else. In particular it says nothing
about whether the system is currently playing — an enabled component that
has been stopped, or that has never been played because `AutoPlay` was off,
still succeeds here. It also does not consider whether the component is in the
scene, unlike `light_component.IsEnabled`.

<!-- engine text:
Succeeds if the component is enabled, fails if it’s disabled.
-->
## particle_system_component.Enabled

The authored starting state, `true` by default, and the flag that `Enable` and
`Disable` maintain thereafter. It is readable from anywhere but writable only
inside the class, so this is the field you inspect and the methods are how you
change it — assigning it directly is not available to you, which keeps the
Niagara activation state and the flag from drifting apart.

It is replicated with change notification, so a client that receives a new
value activates or deactivates its own copy of the system to match.

<!-- engine text:
Controls if the `particle_system_component` should start enabled.
-->
## particle_system_component.Play

Starts the simulation, activating the Niagara system with a reset so the
effect runs from its first frame. It is silently ignored while the component
is disabled, which is worth remembering when a call appears to do nothing:
check `IsEnabled` before blaming the asset.

Playback state is replicated as a monotonically increasing start counter
rather than as a boolean, which is what allows repeated plays to be
distinguished from one another over the network. The method is `<predicts>`,
so a client may call it optimistically and the result is reconciled against
the server's counter when it arrives.

<!-- engine text:
Begin Playable implementation
-->
## particle_system_component.AutoPlay

Whether the effect starts by itself, `true` by default. It is consulted in two
places: when simulation begins, but only if no play state has yet arrived from
the server, so authored auto-play never overrides a replicated decision; and
inside `Enable`, so a component switched back on resumes playing
automatically.

Clearing it gives you an effect that is present, enabled and parameterised but
inert until you call `Play` — the right setup for one-shot impacts and for
effects triggered by gameplay.

<!-- engine text:
Controls if the `particle_system_component` should play the simulation automatically when added to the scene, or when enabled from a disabled state.
-->
## particle_system_component.OnPropertyChangedFromVerse

<!-- engine text:
-TODO: property_changed_interface will be removed
-->
## possessable_component

Marks an entity as something an agent can take control of, and records who
currently has it. It is `<epic_internal>`, so you cannot add it yourself; you
encounter it on entities the engine has already made possessable, and read
`Agent` to find out who is driving.

Possession is torn down for you: when the component's simulation ends —
because the entity was removed from the scene, or the experience reset — it
tells the possessing agent's possessor to release it, so an unpossess is never
missed merely because the possessed entity went away.

<!-- engine text:
Marks an entity that can be possessed by an agent.
-->
## possessable_component.Agent

Who currently possesses the entity, or `false` if nobody does. The variable is
publicly readable but privately settable, so you observe possession here and
change it through the possession machinery rather than by assignment.

<!-- engine text:
Which agent is this entity currently possessed by.
-->
## possessable_component.OnEndSimulation

<!-- no documentation in the engine source -->
## SetPresentableToPlayers

Restricts which players see this entity. The optional is the interesting part:
`false` means presentable to everyone, while `option{array{}}` — a set value
holding an empty array — means presentable to nobody. Those two are easy to
confuse and mean opposite things.

Visibility is recorded on an internal presentation component and replicated,
so this is a server-side call whose effect the clients discover; it is not a
local hide.

<!-- engine text:
Assign the players that this entity will be presented to. False = presentable to everyone, array = presentable to no one.
-->
## GetPresentableToPlayers

Reads back the audience set by `SetPresentableToPlayers`, with the same
convention: `false` for "everyone", a set-but-empty array for "nobody", and a
populated array for a specific audience. It never fails — an entity that has
never had its audience restricted simply reports `false` — so use the
optional's shape, not success, to tell the cases apart.

<!-- engine text:
Get the players that this entity is currently be presented to. False = presentable to everyone, array = presentable to no one.
-->
## rect_light_component

A rectangular emitter of `SourceWidth` by `SourceHeight` centimetres, lying in
the plane perpendicular to the entity's forward axis and driving Unreal's
`URectLightComponent`. Unlike the sphere and capsule lights it is inherently
one-sided and shaped, which is what makes it the natural fit for screens,
softboxes and lit panels.

It implements `bounded`, but its bounds are computed purely from
`AttenuationRadius` — the source rectangle and the barn doors do not enter
into it, so a wide, shallow panel still reports a spherical extent.

<!-- engine text:
A `rect_light_component` emits light into the scene from a rectangular plane with a specified width and height. You can use these
to simulate any kind of light sources that have rectangular areas, such as televisions or monitor screens, overhead lighting
fixtures, or wall sconces.
-->
## rect_light_component.OnAddedToSceneInternal

<!-- engine text:
component interface
-->
## rect_light_component.Intensity

Candelas, `8.0` by default, pushed to the renderer as soon as you assign it;
the proxy light is configured for candela units explicitly. The number
describes the emitter's luminous intensity and is independent of `SourceWidth`
and `SourceHeight`, so enlarging the panel spreads the same intensity over a
larger area rather than scaling the total output.

`ColorFilter` multiplies each channel after this value, so a tinted rect light
is also a dimmer one.

<!-- engine text:
Set the visible light intensity emitted in SI unit Candela.
Specified before ColorFilter (which multiplies each color component after the intensity calculation and can change the effective intensity of the light).
-->
## rect_light_component.AttenuationRadius

Centimetres, `option{1000.0}` by default, bounding where the light is
considered at all; falloff inside it is inverse-square with a smoothing term
at the tail so the contribution fades to zero instead of clipping. This is the
component's main performance control, and it is also the only input to
`GetBoundedGlobalBox` and `GetBoundedLocalBox`.

`false` means no authored bound, not an infinite one: the renderer, which
cannot yet express an unlimited radius, is given 10 000 cm instead, and the
bounded box collapses to a default `bounded_box`.

<!-- engine text:
The bounds of the light's visible influence, in centimeters. This clamping of the light's influence is not physically correct but very important for performance,
larger lights cost more. The light falloff is based on Inverse Square law. Towards the tail end of the AttenuationRadius,
there is an additional smoothing factor to fade out the light contribution to 0 to avoid a hard cutoff.
-->
## rect_light_component.SourceWidth

The emitting rectangle's width in centimetres, 64 cm by default. Together with
`SourceHeight` it determines how soft the light is: a large panel gives broad,
gentle shadow penumbrae and a wide specular smear, a narrow one behaves closer
to a line light. A source shape that intersects shadow-casting geometry will
produce artefacts, so keep the rectangle clear of the surface it is mounted
on.

<!-- engine text:
The width of the light source rect, in centimeters. Note that light source shapes which intersect shadow casting geometry can cause shadowing artifacts.
-->
## rect_light_component.SourceHeight

The emitting rectangle's height in centimetres, also 64 cm by default, giving
a square emitter unless you change one of the two. Setting a very small height
against a large `SourceWidth` produces a strip-like source, which is a cheaper
way to get an elongated highlight than a capsule light if the emitter only
needs to face one way.

<!-- engine text:
The height of the light source rect, in centimeters. Note that light source's shapes which intersect shadow casting geometry can cause shadowing artifacts.
-->
## rect_light_component.BarnDoorAngleDegrees

The angle of the flaps around the rectangle, clamped to 0 to 90 degrees and
defaulting to `88.0` — almost fully open, which is why a fresh rect light
looks unrestricted. Lower values swing the flaps inwards and narrow the
light's spread, in the manner of the barn doors on a real studio fixture; at
`0.0` the flaps are flat against the emitter's axis and the beam is at its
most constrained.

The effect only exists in combination with `BarnDoorLength`: flaps of zero
length occlude nothing whatever the angle.

<!-- engine text:
The angle of the barn door in degrees attached to the light source rect. Clamped between 0.0 and 90.0 degrees.
-->
## rect_light_component.BarnDoorLength

How far the flaps extend from the rectangle, in centimetres, 20 cm by default.
Length and angle work together — the length sets how much occluder there is,
the angle sets where it points — so a long flap at a shallow angle gives a
tightly controlled beam with a soft edge, and a zero length disables barn-door
shaping altogether regardless of `BarnDoorAngleDegrees`.

<!-- engine text:
The length of the barn door attached to the light source rect, in centimeters.
-->
## rect_light_component.GetBoundedGlobalBox

The axis-aligned box enclosing a sphere of `AttenuationRadius` centred on the
entity's global position. The source rectangle, its orientation and the barn
doors are all ignored, so the reported extent is conservative — a thin panel
claims as much space as a sphere light with the same radius.

If `AttenuationRadius` is unset the result is a default `bounded_box` rather
than a box of the 10 000 cm fallback the renderer uses, so an unbounded rect
light appears to have no extent at all.

<!-- engine text:
Returns the bounded box of this component, in world space.
-->
## rect_light_component.GetBoundedLocalBox

The same sphere-derived box as the global variant, but built around the
entity's *local* translation — its position relative to its parent, not the
origin. So the box is generally offset rather than centred, and it does not
shrink or grow with the entity's own scale. As with the global box, an unset
`AttenuationRadius` yields a default `bounded_box`.

<!-- engine text:
Returns the bounded box of this component, in local space.
-->
## sound_component

The base for components that play audio from an entity's position, so that what
the listener hears follows the entity as it moves.

Abstract: attach one of its concrete subclasses rather than this.

<!-- no documentation in the engine source -->
## sound_component.OnInitializedInternal

<!-- engine text:
component interface
-->
## sound_component.OnUninitializingInternal

<!-- no documentation in the engine source -->
## sound_component.OnAddedToSceneInternal

<!-- no documentation in the engine source -->
## sound_component.OnRemovingFromSceneInternal

<!-- no documentation in the engine source -->
## sound_component.OnBeginSimulationInternal

<!-- no documentation in the engine source -->
## sound_component.AutoPlay

Whether the sound starts by itself, `true` by default. Despite the engine's
comment this is a plain configuration flag, and it is read in exactly two
situations: when simulation begins, but only if no playback state has yet
arrived from the server, so an authored value never overrides a replicated
one; and inside `Enable`, so a component switched back on starts playing
again.

Clear it for sounds fired by gameplay — impacts, notifications, one-shots
— and leave it set for ambiences that should simply be running.

<!-- engine text:
Begin Playable implementation
-->
## sound_component.Play

Starts the sound if the component is enabled, and does nothing at all if it is
not. Before playback begins the proxy actor is snapped to the entity's current
global transform; from then on it follows the entity, but only while the sound
is actually playing, so the position of a silent sound component is not
tracked and is resolved afresh at the next `Play`.

Playback is replicated as an increasing start counter rather than a boolean,
so successive plays are distinguishable over the network, and the method is
`<predicts>` so a client may start the sound optimistically and be reconciled
against the server. There is no audio proxy on a dedicated server: the server
tracks and replicates the decision, clients make the noise.

<!-- engine text:
Play the sound asset
-->
## sound_component.Stop

Stops playback and broadcasts the corresponding notification. It returns
immediately if the sound is not currently playing, so it is safe to call
speculatively. Like `Play` it moves the replicated start counter, so clients
stop in step with the server, and it can be predicted on a client.

Stopping does not disable the component: `Play` will start it again, and
`AutoPlay` still applies the next time the component is enabled.

<!-- engine text:
Stop the sound asset
-->
## sound_component.Enable

Returns immediately if the component is already enabled. Otherwise it records
the new state, activates the underlying audio component, and starts playing if
`AutoPlay` is set — so re-enabling an ambience restarts it, while a one-shot
with `AutoPlay` cleared stays quiet until you call `Play`.

<!-- engine text:
Enable the sound component.
-->
## sound_component.Disable

Returns immediately if already disabled. Otherwise it stops any playback in
progress and deactivates the audio component, so the sound ceases at once
rather than fading. Every parameter you have set on the component survives,
and being disabled is a gate on `Play`, which is silently ignored until the
component is enabled again.

<!-- engine text:
Disable the sound component.
-->
## sound_component.IsEnabled

Succeeds when the component's enabled flag is set, regardless of whether a
sound is actually playing or whether the component is in the scene. A stopped
but enabled sound therefore succeeds here — use it to check whether `Play`
will be honoured at all, not to ask whether anything is currently audible.

<!-- engine text:
Succeeds if the sound component is enabled, fails if it is disabled.
-->
## sound_component.Enabled

Whether the component is active. Its setter is `<private>`, so this is read
freely but changed only through the component's own interface rather than
assigned to directly.

<!-- no documentation in the engine source -->
## sound_component.OnPropertyChangedFromVerse

<!-- no documentation in the engine source -->
## sphere_light_component

The plainest of the local lights: a `UPointLightComponent` whose emitter is a
sphere of `SourceRadius`, radiating equally in all directions. A radius of
zero makes it a true point light, and it is the component to reach for when
you want a bulb, a torch flame or a glowing object.

It implements `bounded`, with an extent derived entirely from
`AttenuationRadius`. It also differs from `capsule_light_component` only in
lacking a source length, so the two are interchangeable in practice — pick
the capsule when the emitter needs to be elongated, the sphere otherwise.

<!-- engine text:
A `sphere_light_component` emits light in all directions into the scene from a spherical source shape with a specified radius. A radius of 0 makes it a point light. You can use these
to simulate any kind of light sources that emit in all directions, such as a light bulb.
-->
## sphere_light_component.OnAddedToSceneInternal

<!-- engine text:
component interface
-->
## sphere_light_component.Intensity

Candelas, `8.0` by default; the proxy light's intensity units are set
explicitly so the figure is unambiguous, and assigning the property pushes it
to the renderer straight away. Because the intensity describes the emitter and
not its surface, growing `SourceRadius` softens the light without changing how
bright it reads.

`ColorFilter`, applied afterwards, multiplies each channel and so alters the
effective intensity as well as the hue.

<!-- engine text:
Set the visible light intensity emitted in SI unit Candela.
Specified before ColorFilter (which multiplies each color component after the intensity calculation and can change the effective intensity of the light).
-->
## sphere_light_component.AttenuationRadius

Centimetres, `option{1000.0}` by default: the sphere within which the light is
evaluated at all. Inside it, falloff is inverse-square with an added smoothing
term near the boundary so that the contribution reaches zero rather than being
truncated. Larger radii cost more, since more of the scene has to be lit.

An unset radius does not mean unlimited. The renderer has no encoding for that
yet, so it receives 10 000 cm, while `GetBoundedGlobalBox` and
`GetBoundedLocalBox` degenerate to a default `bounded_box`.

<!-- engine text:
The bounds of the light's visible influence, in centimeters. This clamping of the light's influence is not physically correct but very important for performance,
larger lights cost more. The light falloff is based on Inverse Square law. Towards the tail end of the AttenuationRadius,
there is an additional smoothing factor to fade out the light contribution to 0 to avoid a hard cutoff.
-->
## sphere_light_component.SourceRadius

The emitting sphere's radius in centimetres, 10 cm by default. It is a
softness control rather than a brightness one: a larger sphere widens shadow
penumbrae and broadens specular highlights, while zero gives a hard point
source with pinpoint highlights. Note that it plays no part in the component's
reported bounds, which depend only on `AttenuationRadius`.

Watch out for source spheres that intersect shadow-casting geometry — a bulb
sunk into a ceiling will produce shadowing artefacts.

<!-- engine text:
Radius of the source shape, in centimeters. Note that light shapes which intersect shadow casting geometry can cause shadowing artifacts.
-->
## sphere_light_component.GetBoundedGlobalBox

The axis-aligned box around a sphere of `AttenuationRadius` centred on the
entity's global position — so the entity's rotation and scale are
irrelevant, as they should be for an omnidirectional light. `SourceRadius` is
not included, which is harmless in practice since the source is always well
inside the attenuation sphere.

With `AttenuationRadius` unset the result is a default `bounded_box`, not a
box of the renderer's 10 000 cm fallback.

<!-- engine text:
Returns the bounded box of this component, in world space.
-->
## sphere_light_component.GetBoundedLocalBox

The same construction as the global box but centred on the entity's *local*
translation, that is its offset from its parent rather than the origin. A
light positioned away from its parent therefore reports an off-centre local
box. An unset `AttenuationRadius` again yields a default `bounded_box`.

<!-- engine text:
Returns the bounded box of this component, in local space.
-->
## spot_light_component

A cone of light along the entity's forward axis, driving Unreal's
`USpotLightComponent`. Full brightness fills the inner cone and falls off from
there to the outer cone, giving the soft edge to the disc of illumination; the
cone's length is set by `AttenuationRadius`, not by a separate parameter, so
the attenuation radius doubles as the beam's reach.

The two cone angles are actively kept consistent: whenever either is applied,
the inner is pulled down or the outer pushed up so that the inner can never
exceed the outer. It implements `bounded`, and it is the one light whose
bounds account for its shape — the box is derived from a bounding sphere of
the outer cone rather than of the whole attenuation sphere.

<!-- engine text:
A `spot_light_component` emits light from a single point in a cone shape. The shape of the light is defined by two cones: the `InnerConeAngleDegrees`
and `OuterConeAngleDegrees`. Within the `InnerConeAngleDegrees` the light achieves full brightness. As you go from the extent of the inner radius to the
extents of the `OuterConeAngleDegrees` a falloff takes place, creating a penumbra, or softening around the `spot_light_component`'s disc of
illumination. The Radius of the light defines the length of the cones. More simply, this will work like a flash light or stage can light.
-->
## spot_light_component.OnAddedToSceneInternal

<!-- engine text:
component interface
-->
## spot_light_component.Intensity

Candelas, `8.0` by default, applied to the renderer immediately on assignment
with the proxy's units set explicitly to candelas. It is independent of the
cone angles, so narrowing the beam concentrates the same intensity into a
smaller solid angle rather than dimming it — a tight spot and a wide flood
at the same intensity do not look equally bright on the surfaces they hit.

`ColorFilter` multiplies each channel afterwards and so changes the effective
brightness too.

<!-- engine text:
Set the visible light intensity emitted in SI unit Candela.
Specified before ColorFilter (which multiplies each color component after the intensity calculation and can change the effective intensity of the light).
-->
## spot_light_component.AttenuationRadius

Centimetres, `option{1000.0}` by default. For a spot light this is both the
performance bound and the visible length of the beam: the cone simply ends
there, with inverse-square falloff along its length and a smoothing term at
the tail so the end fades out rather than being cut.

Leaving it unset does not produce an infinitely long beam. The renderer
receives 10 000 cm in place of the missing value, and the component's bounded
box collapses to a default `bounded_box` — so an unset radius quietly
removes the light from its entity's extent.

<!-- engine text:
The bounds of the light's visible influence, in centimeters. This clamping of the light's influence is not physically correct but very important for performance,
larger lights cost more. The light falloff is based on Inverse Square law. Towards the tail end of the AttenuationRadius,
there is an additional smoothing factor to fade out the light contribution to 0 to avoid a hard cutoff.
-->
## spot_light_component.SourceRadius

The radius of the emitter at the cone's apex, in centimetres, 10 cm by
default. It softens the light — wider penumbrae, broader highlights —
without widening the beam, which is what the cone angles are for. Zero gives a
hard point source.

A source sphere that intersects shadow-casting geometry causes shadowing
artefacts, which is easy to hit with a spot light mounted flush against a wall
or inside a housing.

<!-- engine text:
Radius of the source shape, in centimeters. Note that light shapes which intersect shadow casting geometry can cause shadowing artifacts.
-->
## spot_light_component.InnerConeAngleDegrees

The half-angle, in degrees, of the fully-lit core of the beam, clamped to 0 to
80 and `0.0` by default — so out of the box the whole beam is penumbra and
the spot has the softest possible edge. Raising it towards
`OuterConeAngleDegrees` widens the region at full brightness and
correspondingly sharpens the falloff.

The pair cannot cross. When the value is applied, an inner angle greater than
the outer causes the outer to be raised to match, so you never end up with an
inverted cone; if you are widening both, set the outer first to avoid dragging
it along.

<!-- engine text:
The light's inner cone shaped angle in degrees. Clamped between 0.0 and 80.0.
-->
## spot_light_component.OuterConeAngleDegrees

The half-angle, in degrees, at which the light has fallen to nothing, clamped
to 1 to 80 and `44.0` by default — an 88 degree beam. This is the angle that
defines how wide the spot is, and the only cone angle that affects the
component's reported bounds.

As with the inner angle the two are kept ordered: applying an outer angle
smaller than the inner pulls the inner down to match. Narrowing a beam by
reducing the outer angle alone will therefore also reduce the inner angle, and
the fully-lit core is not restored when you widen the outer angle again.

<!-- engine text:
The light's outer cone shaped angle in degrees. Clamped between 1.0 and 80.0.
-->
## spot_light_component.GetBoundedGlobalBox

The axis-aligned box around a bounding sphere of the beam's cone, computed
from `AttenuationRadius`, `OuterConeAngleDegrees` and the entity's global
position and forward direction. This makes it the tightest of the light
bounds: rotating the entity changes the box, and a narrow beam reports a much
smaller extent than an equivalently long sphere light would.

If `AttenuationRadius` is unset the result is a default `bounded_box`, so an
unbounded spot contributes nothing to its entity's extent.

<!-- engine text:
Returns the bounded box of this component, in world space.
-->
## spot_light_component.GetBoundedLocalBox

The same cone-bounding construction, but built at the origin along the local
forward axis — the entity's own local translation and rotation are not
applied, unlike the sphere and rect lights, whose local boxes are offset by
their local position. The result therefore describes the beam's shape in its
own frame: useful for reasoning about the cone itself, but not a placement in
the parent's space. An unset `AttenuationRadius` yields a default
`bounded_box`.

<!-- engine text:
Returns the bounded box of this component, in local space.
-->
## float_range

A closed interval of `float`, used where a component wants to describe a band
of values rather than a single one. Both bounds default to `0.0`, and the
contract is one-directional: a value is inside the range only when `Minimum`
is less than or equal to `Maximum`, so an inverted range contains nothing
rather than being silently normalised.

It is a plain `struct<concrete>` with no operations of its own — comparison
against the bounds is left to whoever consumes it. Despite living in the
text-display header, it carries nothing specific to text.

<!-- engine text:
A range with a minimum and maximum value. For a value to fall inside of this range, the min value must be less than or equal to the max value.
-->
## float_range.Minimum

The lower bound, defaulting to `0.0`. It is not clamped against `Maximum` on
assignment, so nothing stops you creating an inverted range; that range will
simply never contain anything.

<!-- engine text:
The minimum value of the range. Must be less than or equal to Max for values to fall inside the range.
-->
## float_range.Maximum

The upper bound, defaulting to `0.0`, so a default-constructed `float_range`
admits only the single value zero. As with `Minimum`, the ordering constraint
is a contract rather than something the struct enforces.

<!-- engine text:
The maximum value of the range. Must be greater than or equal to Min for values to fall inside the range.
-->
## easing_window

Pairs an easing curve with when to apply it. `Duration` is the length of the
blend in seconds (default `0.3`), and `Easing` is an ordinary function value
of type `type{_(:float)<reads>:float}` — not a class — defaulting to
`EaseInOut` from `/Verse.org/Verse/Easing`, so you can pass any of that
module's curves or your own function.

`Offset` slides the window along the easing modifier's internal timeline: a
positive offset delays the blend, a negative one brings it forward. Offsetting
an ease-in earlier and an ease-out later leaves a gap in which the target is
held, which is how you observe a "frozen" pose of a target that is itself
changing over time.

<!-- engine text:
An easing function combined with a relative time window
-->
## FindDescendantEntities

Walks the subtree rooted at `InEntity` and yields every entity that casts to
`entity_type`, including `InEntity` itself — a point worth remembering when
you call it from a component and expect only children. Since `entity_type` is
a `castable_subtype`, passing a prefab class is the idiomatic way to find "all
the doors below here".

The result is materialised before you see the first element, so adding or
removing entities while iterating cannot disturb the walk. Order is
deliberately unspecified: parts of the subtree are answered from an entity
registry index rather than by traversal, so do not rely on the sequence you
observe today. A query rooted at an entity that has already been destroyed
yields nothing rather than erroring.

<!-- engine text:
Finds all descendant entities including `InEntity` of type `entity_type`.
The order of the returned entities is unspecified and subject to change.
-->
## FindDescendantEntitiesWithComponent

Like `FindDescendantEntities`, but selects on capability instead of class: it
yields each entity in the subtree, `InEntity` included, that carries a
component of `component_type`. This is usually what you want, since
scene-graph advice is to put behaviour in components rather than in `entity`
subclasses.

It returns the entities, not the components — reach for
`FindDescendantComponents` if the component is what you are after and you
would only have to look it up again.

<!-- engine text:
Finds all descendant entities including `InEntity` containing a component of type `component_type`.
The order of the returned entities is unspecified and subject to change.
-->
## FindDescendantComponents

Yields the components themselves rather than their owners, for every entity in
the subtree including `InEntity`. At most one component per entity is
returned, which costs nothing given that an entity may hold only one component
from each subclass group; the exception is passing `component` itself, which
is special-cased to return every component on every entity in the subtree.

The typed result means no cast at the call site, which is why this carries
`<predicts>` and is the natural choice for gathering, say, every light below a
room entity.

<!-- engine text:
Finds all components attached to descendant entities to and including `InEntity` of type `component_type`.
The order of the returned components is unspecified and subject to change.
-->
## FindAncestorEntities

Walks upwards from `InEntity` to the root, yielding ancestors that cast to
`entity_type`. Unlike the descendant queries, `InEntity` itself is excluded
— the walk starts at its parent — so a component asking for its own prefab
type finds the enclosing one, not itself.

The traversal stops when it runs out of parents, so an entity not currently in
the scene yields little or nothing. As with all these queries, order is
unspecified and the result is a snapshot.

<!-- engine text:
Finds all ancestor entities to `InEntity` of type `entity_type`.
The order of the returned entities is unspecified and subject to change.
-->
## FindAncestorEntitiesWithComponent

Yields ancestors of `InEntity`, excluding `InEntity`, that carry a component
of `component_type`. The typical use is finding the context an entity sits in
— the vehicle above a seat, the room above a prop — without hard-coding
how many levels up it lives.

If you need the nearest such ancestor rather than all of them, remember the
order is unspecified: walk `GetParent[]` yourself instead of taking the first
element.

<!-- engine text:
Finds all ancestor entities to `InEntity` containing a component of type `component_type`.
The order of the returned entities is unspecified and subject to change.
-->
## FindAncestorComponents

The component-returning form of `FindAncestorEntitiesWithComponent`, again
skipping `InEntity` and returning at most one component per ancestor (unless
you pass `component` itself, which returns all of them). Results come back
already typed as `component_type`, so no cast is needed.

<!-- engine text:
Finds all components attached to ancestor entities to `InEntity` of type `component_type`.
The order of the returned components is unspecified and subject to change.
-->
## skeletal_animation

A `modifier(skeleton)`: rather than owning a pose, it takes an incoming
skeleton and returns a modified one, which is what allows animations to be
stacked and blended by composing modifiers. It is `<epic_internal>` and
`<experimental>`, so in practice you meet instances generated from animation
assets rather than constructing them.

<!-- engine text:
A modifier of skeletons, used to animate meshes using skeletal animation
-->
## skeletal_animation.Evaluate

Takes a skeleton pose and returns the posed skeleton, which is what lets
animations be stacked: each one receives the result of the previous, so a
walk cycle, a lean and a recoil compose into a single pose.

<!-- no documentation in the engine source -->
## skeleton

An opaque handle to a collection of bones and the sets or chains defined over
them. It carries no public members: its purpose is to be the value that
`modifier(skeleton)` implementations such as `skeletal_animation` transform.

<!-- engine text:
Skeletons are collections of bones & sets/chains
-->
## entity_streaming_policy

Chooses how an entity is loaded on clients, independently of its parent. The
policy is held as an optional on the internal streaming component, so leaving
it unset means "inherit the surrounding behaviour" rather than picking a
default.

<!-- engine text:
Entity client streaming modes
-->
## entity_streaming_policy.Spatial

The entity streams in and out with distance from the viewer, using the
streaming distance configured alongside it. This is the right choice for
ordinary world content, and the one that lets a large scene stay affordable.

<!-- engine text:
Entity will be spatially loaded.
-->
## entity_streaming_policy.NonSpatial

The entity is loaded without reference to where the viewer is. Use this for
content that must exist regardless of proximity but still participates in
loading — logic and coordination entities rather than visible geometry.

<!-- engine text:
Entity will be non-spatially loaded.
-->
## entity_streaming_policy.Persistent

The entity is always loaded and never streams out. The strongest guarantee and
the most expensive, so it suits singletons such as game-mode or scoring
entities.

<!-- engine text:
Entity will be always loaded.
-->
## children_streaming_policy

Decides whether an entity's children share its streaming fate or manage their
own. Like `entity_streaming_policy` it is stored as an optional, so leaving it
unset does not pin the behaviour.

<!-- engine text:
Child entities client streaming modes
-->
## children_streaming_policy.Atomic

Children load and unload together with their parent, as one unit. Choose this
when a group only makes sense whole — a vehicle and its wheels, a machine
and its moving parts — so that no client ever sees half of it.

<!-- engine text:
Child entities are loaded atomically with their parent.
-->
## children_streaming_policy.Discrete

Children stream independently of the parent, so a distant child can be absent
while its parent is loaded. This is what you want for a container entity
holding scattered content, where loading everything because one piece is near
would defeat the purpose.

<!-- engine text:
Child entities are loaded independently from their parent.
-->
## component

The unit of behaviour in the scene graph. An entity is a node in a hierarchy;
what it actually does comes from the components attached to it. Components are
deliberately unopinionated — one may wrap an engine concept such as a mesh,
another may hold an inventory, another may be a whole game mode — and
whether you write one large component or many small ones is a design choice,
not a rule.

Two structural rules matter. First, a class that is to be attached to an
entity must derive from `component` directly and say `<final_super>`; further
subclassing of that class is then free. Second, an entity may hold only one
component from each such subclass group — one `light_component`, whichever
concrete light it happens to be — so multiple lights means multiple
entities, not multiple components.

The lifecycle is where most component code lives. `OnAddedToScene` runs when
the component reaches the scene and is the point after which scene queries are
valid; `OnBeginSimulation` follows and is the place for setup that must
complete immediately, such as subscribing to `TickEvents`; `OnSimulate` then
runs concurrently and is where `<suspends>` logic belongs. Shutdown mirrors
this: `OnSimulate` is cancelled, then `OnEndSimulation`, then
`OnRemovingFromScene`. Every shutdown hook is only called if its opening
counterpart ran, so cleanup code can assume its setup happened.

<!-- engine text:
Base class for authoring logic and data in the SceneGraph. Using components you
can author re-usable building blocks of logic and data which can then be added to
entities in the scene.

Components are a very low level building block which can be used in many ways.
For example:
  * Exposing engine level concepts like mesh or sound
  * Adding gameplay capabilities like damage or interaction
  * Storing an inventory for a character in the game

As components are generic there is no specific way that they must be used.
It is up to the needs of your experience if you use one big game component
or if you break up logic into many small components.

Classes deriving from component must also specify `<final_super>` to be added
to entities. This ensures the class will always derive directly from `component`.
Further subclassing of the initial derived component is allowed and does not require
specifying `<final_super>` on the derived classes.

Only one instance of a component from each subclass group can be added to an entity
at a time. For example, given this group of components, only one light_component can
exist on a single entity. To create multiple lights you should use multiple entities.

  light_component             := class<final_super>(component)
  capsule_light_component     := class<final>(light_component)
  directional_light_component := class<final>(light_component)
  spot_light_component        := class<final>(light_component)
  sphere_light_component      := class<final>(light_component)
  rect_light_component        := class<final>(light_component)

==============================================================================
Component Lifetime

  Components move through a series of lifetime functions as they are added
  to entities, added to the scene, and begin running in the simulation. Components
  should override these methods to perform setup and run their simulation.

  As a component shuts down it will then move through shutdown version of these
  functions, giving users the opportunity to clean up any retained state on the
  component before it is disposed
.
  Lifetime Methods:
     OnAddedToScene
       OnBeginSimulation -> OnSimulate<suspends>
       OnEndSimulation
     OnRemovingFromScene
==============================================================================
-->
## component.Entity

The entity this component belongs to. It is supplied at construction and can
never change: components are not moved between entities, and a component
removed from an entity can only be added back to that same one. That
immutability is why `Entity` is safe to read at any point in the lifecycle,
including before the component has reached the scene.

It is the usual starting point for reaching everything else — sibling
components via `Entity.GetComponent[...]`, position via
`Entity.GetGlobalTransform()`, neighbours via the `Find*` queries.

<!-- engine text:
The parent entity of this component.
  * Components must have a parent entity pointer provided when being constructed.
  * Components cannot be moved between parents.
-->
## component.RemoveFromEntity

Detaches the component, running it through `OnEndSimulation` and then
`OnRemovingFromScene` on the way out, so your cleanup hooks fire exactly as
they would if the entity itself were removed. It is `<final>`, so no subclass
can intercept the call.

The detached component is not destroyed and may be added back — but only to
the same entity, since `Entity` is fixed for life. If you want the behaviour
somewhere else, construct a new component there.

<!-- engine text:
Removes the component from the entity.
  * Removed components are removed from the scene and can only be added back to the same entity.
  * Flows through `OnEndSimulation`-> `OnRemovingFromScene`.
-->
## component.IsInScene

Succeeds between `OnAddedToScene` and `OnRemovingFromScene`. This is the guard
for anything that touches the wider scene: outside that window the component
exists and knows its entity, but querying for other components is not
meaningful.

Being a `<decides><reads>` query it is used in a failure context, and it is
implied by `IsSimulating[]` — a simulating component is necessarily in the
scene, so testing both is redundant.

<!-- engine text:
Succeeds if the component is currently in the scene.
  * After `OnAddedToScene` is called this call succeeds.
  * After `OnRemovingFromScene` is called this call fails.
-->
## component.IsSimulating

Succeeds between `OnBeginSimulation` and `OnEndSimulation`, the narrower of
the two lifecycle windows. This is the check to make before doing anything
that assumes the component is live: signalling events, driving movement, or
acting on a callback that may have outlived the component's simulation.

It is especially worth guarding inside `OnSimulate` after a suspension point,
since a task can resume into a component whose simulation has since ended.

<!-- engine text:
Succeeds if the component is currently simulating.
  * After `OnBeginSimulation` is called this call succeeds.
  * After `OnEndSimulation` is called this call fails.
-->
## component.SendDown

Delivers a scene event to this component alone, invoking its `OnReceive`, and
reports whether it was consumed. Despite the name it does not walk the
hierarchy — the propagation is in `entity.SendDown`, which calls this on
each of the entity's components before descending.

Use it to hand an event to a specific component you already hold, and use the
entity-level `SendUp` or `SendDown` when you want the event to travel.

<!-- engine text:
Send a scene event to this component, invoking OnReceive.  Returns true if any participant consumed the event.
-->
## component.GetDiagnostic

Satisfies the `diagnosable` interface, producing the value used to identify
this component when it appears in engine diagnostics. It is `<reads>` and you
would rarely call it yourself; its presence is what makes a component nameable
in an error message. `entity` overrides the same member for the same reason.

<!-- no documentation in the engine source -->
## scene_event

An empty marker interface for messages that travel through the scene graph.
You define your own event by writing a class that implements it and carries
whatever payload you need, then send it with `entity.SendUp` or
`entity.SendDown`.

Delivery reaches components through `OnReceive`, whose `logic` return decides
whether the event is consumed: returning true halts propagation there, so the
same mechanism serves both broadcast notification and first-responder-wins
dispatch. Several engine components use it internally — the stackable, icon
and rarity components each announce their state down the tree this way.

<!-- engine text:
An event which can be sent through the scene graph.
-->
## entity

A node in the scene hierarchy. Everything in an experience is built from
entities: they nest, they can be reparented at runtime, and their behaviour
comes entirely from the `component`s attached to them. Query upwards with
`GetParent[]`, downwards with `GetEntities()`, and further afield with the
`Find*` extension methods.

Lifetime follows the hierarchy. A parent owns its children and their
components, so removing an entity from the scene takes its whole subtree with
it, running every affected component through `OnEndSimulation` and
`OnRemovingFromScene`. Adding an entity to a new parent moves it through its
lifecycle hooks until it matches the parent's state, which is how an entity
constructed in code comes alive the moment it is parented under something
already in the scene.

A class deriving from `entity` is a prefab — a reusable bundle of entities
and components, normally authored in the editor and surfaced to Verse through
the generated `Assets.digest.verse`. Epic's own guidance is not to put logic
in the `entity` subclass: keep it in components so you can restructure prefabs
later without refactoring a class hierarchy.

<!-- engine text:
Entities are the base object in the SceneGraph.
  * Objects in experiences are constructed of one or more entities.
  * Entities are hierarchical. You can query your parent using `GetParent` and add child entities using `AddEntities`.
  * Behavior is added to entities through `component`s. You can add new components using `AddComponents`.
  * The structure and content of entities is dynamic and be changed at any time through your experience
.
==============================================================================
Deriving from entity

  In the SceneGraph system a class that derives from `entity` is also known as a prefab. Prefabs are useful when you
  want to spawn/re-use a collection of entities and components many times within your game. Primarily prefabs are
  authored through the editor, with their Verse classes generated as part of the build into the projects
  Assets.digest.verse file.

  While you can create base prefabs for common game object types like a vehicle or character, we highly recommended
  that you do not add code directly to the entity class, and instead keep logic in components. Keeping logic and data in
  components allows you to restructure your prefabs throughout production of your experience, without needing to massively
  refactor your class structure.
-->
## entity.GetParent

Returns the entity one level up, failing if there is none. Failure means the
entity is either the root of the experience or currently unparented — a
perfectly ordinary state for an entity you have just constructed, or one you
have removed from the scene intending to re-add.

The parent relationship is also the ownership relationship: it decides
lifetime, and by default it decides the frame of reference for the transform
hierarchy too, unless a `transform_component` overrides that with an `origin`.

<!-- engine text:
Returns the parent entity of this entity.
  * The parent entity controls the lifetime of its child entities and components. When an entity
    is removed from the scene, all its child entities and components will be removed as well.
  * Method fails if there is currently no parent entity.
-->
## entity.RemoveFromParent

Takes the entity, and with it everything below, out of the scene. Components
on the entity and all its descendants run `OnEndSimulation` and then
`OnRemovingFromScene`, so this is a graceful teardown rather than a deletion.

The entity survives the call and can be brought back with
`NewParent.AddEntities(array{Entity})`, at which point its components run
through their startup hooks again. Note that a Verse reference to a removed
entity remains valid, so a `Find*` query rooted at one simply yields nothing
rather than failing.

<!-- engine text:
Removes this entity from its parent. This is used to remove entities from the scene.
  * Components on this entity and its children will run through `OnEndSimulation` -> `OnRemovingFromScene`.
  * Entity can be added back later by using `NewParent.AddEntities`.
-->
## entity.AddEntities

Parents the given entities under this one. An entity that already has a parent
is removed from it first, so this doubles as reparenting — there is no
separate detach step. The added children then run through their lifecycle
hooks until they reach the same state as the new parent: nothing happens if
this entity is not in the scene, `OnAddedToScene` if it is, and
`OnBeginSimulation` too if it is simulating.

Reparenting has a transform consequence worth knowing: on the server the child
keeps its world transform across the move, its local transform being
recomputed against the new parent, so an entity does not jump when it changes
hands.

<!-- engine text:
Adds the provided entities as children of this entity.
  * If child entity already has a parent, removes the entity from its current parent and adds it to the new one.
  * Added child entities will move through their lifetime methods until they match the state of the new parent.
-->
## entity.GetEntities

Returns the direct children visible from the calling context — one level
only. For anything deeper use `FindDescendantEntities` and friends, which walk
the whole subtree and can filter by type, component or tag in one call.

The array is a snapshot, so reparenting during iteration will not disturb it.
Because visibility depends on the caller's context, this is not necessarily
every child that exists.

<!-- engine text:
Returns the child entities belonging to this entity which are accessible from the calling context.
  * This method only gets the direct entity children. To query multiple levels down the entity structure use
    the Find* query methods instead.
-->
## entity.GetComponent

The workhorse lookup: succeeds with the entity's component of the given type,
or fails if there is none — or if it is not visible from the calling
context. Since an entity may hold only one component per subclass group,
asking for a base type such as `light_component` reliably returns whichever
concrete light is there.

Its most useful property is phase-awareness. Called during `OnAddedToScene` or
`OnBeginSimulation`, it guarantees the component it hands back has itself
reached that phase, so a component may look up a sibling it depends on without
worrying about the order in which the two were initialised.

Being `<decides>`, use it in a failure context: `if (Light :=
Entity.GetComponent[light_component])`.

<!-- engine text:
Succeeds and returns the child component of type `component_type` if it exists and is accessible from the calling context.
  Note: When called during the AddedToScene or BeginSimulation phase, it will make sure the returned component has achieved the corresponding phase.
  Fails if no component of `component_type` exists or can be accessed.
-->
## entity.GetComponents

Returns all of the entity's components that are visible from the calling
context, as an array of `component` — so you will be casting or matching
interfaces on the way out. This is the right call when you want to ask every
component something rather than find one specific type; the stackable
component uses exactly this pattern to poll its siblings for merge vetoes.

For a specific type prefer `GetComponent[...]`, which is both typed and
phase-aware.

<!-- engine text:
Returns the child components belonging to this entity which are accessible from the calling context.
-->
## entity.AddComponents

Attaches components, in a deliberate three-pass order: all of them join the
entity's child list first, then all of them receive `OnAddedToScene` if the
entity is in the scene, then all of them receive `OnBeginSimulation` if it is
simulating. That batching is what lets a set of mutually dependent components
be added together — each can already see the others by the time its hooks
run.

A component that is not permitted on this entity — typically because its
subclass group is already occupied — is skipped silently rather than
reported, so do not assume every component you passed was accepted. As with
`GetComponent`, calling this during a lifecycle phase brings the new
components up to that same phase before returning.

<!-- engine text:
Adds the provided components to the entity.
  * If a component is not allowed to be added to this entity it is skipped.
  Note: When called during the AddedToScene or BeginSimulation phase, it will make sure the added component has achieved the corresponding phase.
  * Components are added following these rules:
      1. All components are added to the entity child list.
      2. All components have `OnAddedToScene` called (if this entity is in the scene).
      3. All components have `OnBeginSimulation` called (if this entity is simulating).
-->
## entity.GetDiagnostic

Satisfies `diagnosable` for entities, yielding the value the engine uses to
name this entity in diagnostics. `component` overrides the same member;
between them they are why scene-graph error messages can point at a specific
node rather than at a type.

<!-- no documentation in the engine source -->
## entity.SendUp

Sends a scene event towards the root. The entity's own components are offered
the event first, each through `OnReceive`, and then the event moves to the
parent, repeating until it is consumed or runs out of ancestors. The return
value reports whether anyone consumed it.

This is the direction for reporting: a component that knows something happened
locally announces it upwards and lets whichever ancestor cares handle it,
without either end knowing how far apart they are in the hierarchy.

<!-- engine text:
Send a scene event to this entity and then up the hierarchy. First, SendDown/OnReceive will be invoked on each component on this entity. Next, SendUp will be invoked on this entity's parent. Consuming the event at any point will halt propagation. Returns true if any participant consumed the event.
-->
## entity.SendDown

Sends a scene event into the subtree. This entity's components see it first,
then each child entity is sent the same event recursively. Any `OnReceive`
returning true consumes the event and stops propagation from that point, and
the call reports whether that happened anywhere.

This is the direction for broadcast, and it is what the engine's own
components use to publish state changes — `icon_component`,
`rarity_component` and `stackable_component` all announce themselves down the
tree when they begin simulating and again when they end.

<!-- engine text:
Send a scene event to this entity and then down the hierarchy. First, SendDown/OnReceive will be invoked on each component on this entity. Next, SendDown will be invoked on each child entity.  Consuming the event at any point will halt propagation. Returns true if any participant consumed the event.
-->
## entity.AddTag

Attaches a tag instance and hands back a `tag_key` identifying that particular
instance. The key matters because tags are instances, not flags: the same tag
type can be added more than once, and `RemoveTag` needs the key to know which
one you mean.

Hold on to the key if the tag is temporary. If you only ever want the tag
present or absent, the coarser `RemoveAllTags[...]` will do instead.

<!-- engine text:
Adds a `tag` instance to this entity. Returns a `tag_key` that is uniquely associated with the added instance.
-->
## entity.RemoveTag

Removes the one tag instance identified by the key, succeeding only if an
instance was actually removed — so a second removal with the same key fails
rather than passing silently. Keys come from `AddTag`; if you did not keep
one, `RemoveAllTags[...]` is the alternative.

<!-- engine text:
Removes the tag instance associated with the `tag_key`, succeeds if an instance was removed, fails otherwise.
-->
## entity.RemoveAllTags

Removes every tag instance of the given type, and succeeds only if at least
one was removed. That makes it usable both as the removal and as the test: a
failing call tells you the entity had no such tag, so there is no need to
check `ContainsTag[...]` first.

<!-- engine text:
Removes all tag instances of type `tag_type`, succeeds if at least one instance was removed, fails otherwise.
-->
## entity.RemoveAllTagsExcept(castable_subtype(tag))

Keeps tags of the given type and removes all the others, succeeding only if
something was actually removed. Useful for resetting an entity to a single
classification in one step rather than enumerating everything you want gone.

<!-- engine text:
Removes all tag instances that are not of type `tag_type`, succeeds if at least one instance was removed, fails otherwise.
-->
## entity.RemoveAllTagsExcept([]castable_subtype(tag))

The multi-type form: everything not of one of the listed types is removed, and
the call succeeds only if at least one instance went. Note the degenerate case
— an empty array excepts nothing, so this strips every tag and then succeeds
or fails according to whether the entity had any.

<!-- engine text:
Removes all tag instances that are not of any of the types in `tag_types`, succeeds if at least one instance was removed, fails otherwise.
-->
## entity.ContainsTag

Succeeds if the entity carries at least one tag of the given type. Because the
check is by type and `tag_type` is a `castable_subtype`, a tag subclass
answers for its base, which lets you group related tags under a common parent
and test for the whole family at once.

<!-- engine text:
Succeeds if at least one tag of type `tag_type` is found in this container, fails otherwise.
-->
## entity.ContainsAllTags

Succeeds only when every type in the array is present. The edge case is worth
committing to memory: an empty array succeeds, since there is nothing missing.
That is the mathematically consistent answer and the opposite of what
`ContainsAnyTag` does with the same input.

<!-- engine text:
Fails if at least one type in `tag_types` cannot be found in this container, succeeds otherwise. Note that this means that if `tag_types` is empty this call succeeds.
-->
## entity.ContainsAnyTag

Succeeds when at least one of the listed types is present, and — the mirror
of `ContainsAllTags` — fails on an empty array, since none of no types can
be found. If your list of types is computed, be deliberate about which of the
two you call, because they diverge exactly where the input is empty.

<!-- engine text:
Succeeds if at least of the types in `tag_types` is found in this container, fails otherwise. Note that this means that if `tag_types` is empty this call fails.
-->
## entity_prefab

An asset reference to a prefab authored in the editor. It is `<epic_internal>`
and exists to be mentioned by generated digest code; your own Verse refers to
a prefab through the `entity` subclass that the build generates for it, which
is what you construct and pass to `AddEntities`.

<!-- engine text:
Reference type to editor defined prefab. Only generated digest code should reference this type.
-->
## FindDescendantEntitiesWithTag

Yields entities in the subtree, `InEntity` included, that carry any tag of the
given type — tags being the loosest way to mark up a scene, requiring
neither a shared class nor a shared component.

There is one asymmetry to note: when the query is rooted at the simulation
entity, the simulation entity itself is left out of the results even though
the other descendant queries include their root. As always the order is
unspecified.

<!-- engine text:
Finds all descendant entities including `InEntity` that has any tags of type `tag_type`.
When querying from the simulation entity, the simulation entity itself is not included in the results.
The order of the returned entities is unspecified and subject to change.
-->
## FindAncestorEntitiesWithTag

Walks from `InEntity`'s parent to the root, yielding ancestors that carry any
tag of the given type. `InEntity` is not included, matching the other ancestor
queries and differing from the descendant ones. Handy for asking "which region
am I in?" when regions are marked by a tag rather than by a class.

<!-- engine text:
Finds all ancestor entities to `InEntity` that has any tags of type `tag_type`.
The order of the returned entities is unspecified and subject to change.
-->
## icon_component

Holds a single `texture` to represent the entity in the interface,
implementing the `has_icon` interface so that UI code can ask for an icon
without knowing what kind of entity it has.

Setting the icon is not a private matter: the component announces itself down
the entity's subtree with a scene event, and does so again when simulation
begins — and, with the icon cleared, when simulation ends. Anything below
that displays the icon therefore learns about changes without polling, and
learns about disappearance too.

<!-- engine text:
Component that holds an icon for an entity.
-->
## icon_component.Icon

The texture shown as this entity's icon.

Declared with a getter and setter rather than as plain data, so assigning to it
runs the component's own code — the displayed icon updates rather than the field
quietly changing underneath it.

<!-- no documentation in the engine source -->
## icon_component.OnBeginSimulation

<!-- no documentation in the engine source -->
## icon_component.OnEndSimulation

<!-- no documentation in the engine source -->
## rarity

A classification handle that gameplay and presentation systems use to rank
things, carrying a `Color` that defaults to grey. Being `<castable>` and
`<unique>`, a rarity is compared by identity and tested with a cast rather
than by an enum value.

The ranking is expressed as a subclass chain: `uncommon_rarity` derives from
`common_rarity`, `rare_rarity` from `uncommon_rarity`, and so on up through
epic and legendary, each overriding `Color`. That has a pleasing consequence
— a cast to `common_rarity` succeeds for anything of common rarity or
better, so "at least this rare" is a cast rather than a comparison.

<!-- engine text:
Rarity may be used by gameplay and presentation systems to classify and rank things.
-->
## rarity_component

Gives an entity a rarity, and only one: as with any component, a single
instance per subclass group means an entity cannot be two rarities at once.
The value is replicated, so clients see the same classification the server
assigned.

Like the icon component, it publishes changes as a scene event sent down the
subtree, both on change and at the boundaries of simulation, so presentation
components beneath the entity can recolour themselves without asking.

<!-- engine text:
Component that denotes the rarity of an entity.
-->
## rarity_component.Rarity

The entity's rarity, exposed through a getter and setter pair rather than as a
bare field, which is how assignment can also notify the subtree. Reading gives
you a `rarity` instance whose `Color` you can use directly for presentation,
and whose class you can cast against to test the rank.

<!-- engine text:
The rarity of this entity. An entity can have only one rarity.
-->
## rarity_component.OnBeginSimulation

<!-- no documentation in the engine source -->
## rarity_component.OnEndSimulation

<!-- no documentation in the engine source -->
## GetSimulationEntity

Returns the root-most entity of the experience, failing if this entity is not
currently in the scene — which makes it a serviceable "am I live?" check as
well as a lookup. An entity you have constructed but not yet parented, or one
you have removed, will fail here.

It is most useful as the root for a broad query: `FindDescendantEntities` from
the simulation entity searches the whole experience. Bear in mind that the
tag-based descendant query deliberately excludes the simulation entity itself
from its results.

<!-- engine text:
Returns the simulation entity parent for this entity.
  * The simulation entity is the rootmost entity in an experience.
  * Fails if this entity is not currently in the scene.
-->
## stackable_component

Lets an entity stand for a quantity rather than a single thing, and merge with
compatible entities instead of accumulating clutter in the scene. The class is
`<abstract>`, so you use a subclass — `basic_stackable_component` is the
supplied one — and you get the counting, splitting and merging protocol for
free.

Mergeability is collaborative. Beyond the component's own rules, every
component on the entity that implements `has_merge_rules` is consulted and may
veto a merge through `AllowMergeInto`, and is told about a completed one
through `OnMergeInto`. That is how unrelated state — durability,
enchantments, whatever your game tracks — can block a merge that would
otherwise silently lose it.

The component also announces itself down the entity's subtree when simulation
begins and ends, so inventory or presentation logic below it can track the
stack's existence without polling.

<!-- engine text:
A component that when attached to an entity allows for it to merge or 'stack' with other entities with compatible components.
-->
## stackable_component.StackSize

How many of the thing this entity currently represents, starting at one. The
variable is publicly readable but privately settable, so all changes go
through `SetStackSize`, `Split` or `MergeInto` — and therefore through the
validation and the change event those provide.

Pair it with `ChangeStackSizeEvent` rather than polling if you are mirroring
the count in a UI.

<!-- engine text:
The current amount of this entity held in the stack.
-->
## stackable_component.MaxStackSize

The ceiling on `StackSize`, or `false` for no ceiling at all. The default is
`option{1}` — a maximum of one — so a freshly authored stackable does not
actually stack until you raise or clear the limit.

Like `StackSize` it is read-only from outside; change it through
`SetMaxStackSize`, which can also clamp the current size down to the new
maximum.

<!-- engine text:
The maximum amount this component can hold. If unset, it holds an unlimited amount.
-->
## stackable_component.SetStackSize

Sets the count, ignoring the request outright if the value is invalid —
negative, or above `MaxStackSize`. It neither fails nor clamps, so a call that
quietly does nothing is indistinguishable from one that had no work to do
unless you read `StackSize` back afterwards.

If you are moving quantity between entities, prefer `Split` and `MergeInto`,
which keep the totals consistent on both sides.

<!-- engine text:
Sets the stack size of this component. If the provided stack size is invalid, e.g. negative or exceeding MaxStackSize, stack size will not change.
-->
## stackable_component.SetMaxStackSize

Sets the ceiling, where a `false` argument means unlimited. The
`?ClampStackSize` named argument, false by default, decides what happens when
the new maximum is below the current `StackSize`: pass true to have the count
clamped down, or leave it and the existing overflow persists.

<!-- engine text:
Sets the maximum stack size for this component. If NewMaxStackSize is false, stack size is unlimited. If ClampStackSize is true, StackSize will be clamped to NewMaxStackSize.
-->
## stackable_component.Split

Takes `Amount` out of the stack and returns it as an entity, reducing this
stack correspondingly. Asking for the entire stack is special-cased: rather
than create a new entity and empty this one, the call returns this very
entity, so always use the returned reference rather than assuming a new one
appeared.

The call fails if the amount cannot be taken. It is `<native_callable>` and
overridden by `basic_stackable_component`, which is where the new entity's
prefab type comes from.

<!-- engine text:
Splits the specified amount out of this component’s stack, reducing this component’s stack size in the process. Returns an instance of split_prefab_type with a stack size equal to the amount it was able to take from this entity. If taking the exact (full) amount, the entity itself will be returned instead.
-->
## stackable_component.CanMergeInto

Tests whether this entity could merge into the target: they must be different
entities, the target must have a `stackable_component`, native code gets a
chance to override the answer, and then every `has_merge_rules` component on
this entity may veto.

The important caveat is in the engine's own note — the relation is not
symmetric, so a true answer here does not imply the reverse. If either
direction would do, check both.

<!-- engine text:
Succeeds if this entity can be merged into the target entity. Merging an entity with itself will always fail. Note that merging should be checked in both directions!
-->
## stackable_component.MergeInto

Moves quantity from this entity into the target, all of it by default or just
`TargetAmount` if you name one, failing if the amount is not positive, exceeds
the current stack, or the merge is refused. On success every `has_merge_rules`
component on this entity is told how much actually moved, which may be less
than requested if the target's own ceiling intervened.

Because the amount merged is reported rather than assumed, the pattern for a
partial merge is to act on that figure rather than on the amount you asked
for.

<!-- engine text:
Attempts to merge this entity into the specified entity. Fails if entities cannot be merged.
 If TargetAmount is specified, only that amount will try to be merged into this entity. By default, the entire stack will try to merge.
 If the specified amount is invalid, the merge will fail.
-->
## stackable_component.OnBeginSimulation

<!-- no documentation in the engine source -->
## stackable_component.OnEndSimulation

<!-- no documentation in the engine source -->
## change_stack_size_result.StackableComponent

The component whose stack changed, so that one listener can serve several stacks
and still tell which one signalled.

<!-- no documentation in the engine source -->
## change_stack_size_result.PreviousStackSize

The stack size before the change.

<!-- no documentation in the engine source -->
## change_stack_size_result.CurrentStackSize

The stack size after the change. Comparing it with `PreviousStackSize` is how a
listener tells growth from shrinkage without keeping its own record.

<!-- no documentation in the engine source -->
## change_max_stack_size_result.StackableComponent

The component whose capacity changed.

<!-- no documentation in the engine source -->
## change_max_stack_size_result.PreviousMaxStackSize

The capacity before the change, or `false` if the stack had no maximum.

<!-- no documentation in the engine source -->
## change_max_stack_size_result.CurrentMaxStackSize

The capacity after the change, or `false` if the stack now has no maximum.

<!-- no documentation in the engine source -->
## basic_stackable_component

The ready-made stackable: it adds a prefab field and implements `Split` and
`CanMergeInto` in terms of it, so two entities stack when they agree on the
same prefab type. Unless you need bespoke merge rules, this is the one to
attach.

<!-- engine text:
Stackable component which both merges and splits based on a prefab field.
-->
## basic_stackable_component.split_prefab_type

The entity class instantiated when this stack is split, and the identity used
to decide what may merge with what. It defaults to `entity` itself, which is
permissive enough to be almost certainly wrong for real content — set it to
the prefab the stack represents.

<!-- engine text:
The prefab used when this entity merges with another or when it is split into a new instance.
-->
## basic_stackable_component.Split

Implements the split in Verse: it fails if the stack holds less than `Amount`,
returns this entity unchanged when you ask for the whole stack, and otherwise
reduces this stack, constructs a `split_prefab_type{}` and sets the new
entity's stack size to `Amount`.

Note that the new entity is created but not parented; it is up to the caller
to place it in the scene with `AddEntities`, which is also when its components
begin their lifecycle.

<!-- engine text:
Splits the specified amount out of this component’s stack, reducing this components’s stack size in the process. Returns an instance of split_prefab_type with a stack size equal to the amount it was able to take from this entity. If taking the exact (full) amount, the entity itself will be returned instead.
-->
## basic_stackable_component.CanMergeInto

Adds the prefab check on top of the base rules, and does so in both
directions: the target must cast to this component's `split_prefab_type`, and
this entity must cast to the target's. Two stacks therefore merge only when
each recognises the other as its own kind, which stops a stack of a base
prefab absorbing a specialised variant.

<!-- engine text:
Succeeds if this entity can be merged into the target entity. Merging an entity with itself will always fail.
-->
## tick_events

The per-frame hooks a component can attach to, exposed as an object of
`execution_listenable` phases rather than a single tick function. Subscribing
to a phase, rather than overriding a method, means a component can listen to
more than one point in the frame, and can stop listening by cancelling.

The intended shape is to subscribe in `OnBeginSimulation`, keep the returned
`cancelable`, and cancel it in `OnEndSimulation` — the component
documentation calls this out explicitly, and forgetting the second half is the
classic scene-graph leak.

<!-- engine text:
Describes discrete phases of a frame update. Subscribe to members of the tick_events object to run code before or after the physics system has updated your object, allowing you to affect or react to these updates.
-->
## tick_events.PrePhysics

Runs before physics has updated the object this frame, which makes it the
place to affect the simulation: apply forces, set a target transform, drive
movement. The keyframed movement component animates in exactly this phase.

<!-- engine text:
Listen `PrePhysics` to run your code before the physics system has updated your object this frame.
-->
## tick_events.PostPhysics

Runs after physics has updated the object, so it is the place to react rather
than act: read the resulting transform, respond to a collision outcome, follow
something that physics just moved. Work done here will not be seen by this
frame's physics step.

<!-- engine text:
Listen `PostPhysics` to run your code after the physics system has updated your object this frame.
-->
## transform_component

Holds an entity's position, and by extension its place in the transform
hierarchy. It keeps both a local and a global transform and maintains the
relationship between them: set one and the other is recomputed. Local is
relative to the entity's frame of reference — its parent by default, or
whatever its `Origin` names — and global is absolute.

Propagation is a dependency graph rather than a walk. Each component registers
itself as depending on the transform it is relative to, so changing a parent's
transform signals its dependents; the recomputation is gathered into a
dedicated graph that runs at defined points in the frame. The getters also
heal lazily, so reading a transform after moving an ancestor always gives an
up-to-date answer even if the graph has not run yet.

Two behaviours are worth internalising. When the frame of reference merely
changes value — the parent moved — the local transform is preserved and
the global one recomputed, so children follow their parent. When the frame of
reference itself changes — a reparent, or a new `Origin` — the global
transform is preserved on the server and the local one recomputed instead, so
an entity does not jump when it changes hands. Only one `transform_component`
may exist per entity; the class is `<final>`, so there is no subclassing it.

<!-- engine text:
Stores the transforms for an entity, which are used to position the entity.
-->
## transform_component.OnInitializedInternal

<!-- engine text:
component interface
-->
## transform_component.OnUninitializingInternal

<!-- no documentation in the engine source -->
## transform_component.GlobalTransform

The entity's absolute transform. It is a getter/setter pair rather than a
plain field, which is what allows a write to update `LocalTransform` to match
and signal every dependent transform, and a read to bring a stale value up to
date first.

Setting a value at construction is pointless — the note in the engine source
is blunt about it — because the component recomputes the global transform
from the local one and its frame of reference as soon as it is initialised.
Set `LocalTransform` at construction and `GlobalTransform` at runtime.

Individual fields can be assigned through the accessor — `set
Component.GlobalTransform.Translation = V` — and each such write goes
through the same recompute-and-notify path as a whole-transform assignment.

<!-- engine text:
Current transform of the entity, globally referenced. Any value set at construction will be overrridden with the calculation from the Local Transform
-->
## transform_component.LocalTransform

The transform relative to the entity's frame of reference: its parent, or its
`Origin` if one is set. This is the authored value — it is the property the
editor exposes and the one that is replicated — so it is what you set to
place an entity within its prefab.

Writing it recomputes `GlobalTransform` by composing with the frame of
reference, and signals the dependent chain so children move too. Reading it
first heals any pending update, so you never observe a local transform that is
inconsistent with the global one.

<!-- engine text:
LocalTransform to its parent/origin
-->
## transform_component.Origin

An optional replacement for the entity's frame of reference. Unset — the
default — means the local transform is relative to the parent entity. Set,
it means the local transform is relative to whatever the `origin` reports,
which lets an entity be positioned against something that is not its parent
without disturbing ownership or lifetime.

Assigning through the setter re-evaluates the dependency: the component
unsubscribes from its old reference transform, subscribes to the new one, and
preserves its world position by recomputing the local transform. Assigning
`false` is equivalent to `ResetOrigin`, returning the entity to its parent.

Circular arrangements are no longer rejected at the point of assignment; the
component detects re-entrant evaluation and declines to recurse, and the
execution manager reports the cycle. Do not rely on a bad assignment failing.

<!-- engine text:
alternate origin than the default parent entity
-->
## GetGlobalTransform

The convenient way to ask where an entity is, without first finding its
`transform_component`. If the entity has no transform of its own the call
walks up to the nearest ancestor that does and returns that ancestor's global
transform, which is usually the sensible answer — an entity with no
transform sits wherever its parent sits. With nothing found anywhere up the
chain the result is the identity transform.

It never fails, so a returned identity may mean "at the origin" or "nothing in
this branch has a transform". Reading through this path also heals any pending
transform updates, so the value reflects moves made earlier in the frame.

<!-- engine text:
Returns the global transform of this entity, in the case the entity does not have a transform_component it will return the transform of the first parent that has a transform
-->
## GetLocalTransform

Returns the entity's transform relative to its parent or `origin`. Unlike
`GetGlobalTransform` this does not walk up the hierarchy: an entity with no
`transform_component` of its own reports the identity transform rather than
borrowing its parent's local transform, which would be meaningless.

Since the call cannot fail, use `GetOrigin[...]` or a direct
`GetComponent[transform_component]` when you need to distinguish "at its
parent's position" from "has no transform at all".

<!-- engine text:
Returns the local transform of this entity, in the case the entity does not have a transform_component it will return identity
-->
## GetOrigin

Returns the entity's alternative frame of reference, failing if there is none
— and also failing if the entity has no `transform_component` at all, since
there is then nowhere for an origin to live. The two failures are not
distinguished, so this is not a way to test for the component's presence.

Success means the entity's local transform is measured against something other
than its parent, which is worth knowing before you interpret a local transform
or reparent the entity.

<!-- engine text:
Returns the origin of the entity in any, in the case the entity does not have a transform_component the method will fail
-->
## SetGlobalTransform

Places an entity at an absolute transform. If it already has a
`transform_component` this sets the global transform and back-computes the
local one. If it does not, one is created for it — with the local transform
worked out relative to the parent's global transform, so the entity really
does land where you asked.

That silent component creation makes this convenient but not free: it changes
the entity's structure. If you are positioning an entity you will move often,
fetch the `transform_component` once and use it directly.

<!-- engine text:
Sets the global transform of this entity, in the case the entity does not have a transform_component it will create one and set its global transform
-->
## SetLocalTransform

Places an entity relative to its parent or `origin`, creating a
`transform_component` with that local transform if the entity has none.
Because the local transform is the replicated, editor-authored value, this is
the call that matches how content is built, and the one to prefer when an
entity's position is meaningful only in the context of its prefab.

Writing the local transform propagates to descendants, whose own local
transforms are preserved as they follow.

<!-- engine text:
Sets the local transform of this entity, in the case the entity does not have a transform_component it will create one and set its local transform
-->
## SetOrigin

Redirects the entity's frame of reference away from its parent, creating a
`transform_component` if there is not one already. The entity keeps its world
position across the change — the local transform is recomputed against the
new reference — so this is a way to change what an entity follows without
moving it.

Despite the wording in the engine's documentation, the function returns `void`
and has no `<decides>`, so it cannot report a cyclic arrangement to you.
Cycles are no longer rejected on assignment: re-entrant evaluation is detected
and skipped, and the execution manager logs the problem. Check the
relationship yourself before wiring one entity's origin to another's.

<!-- engine text:
Sets the origin of this entity, in the case the entity does not have a transform_component it will create one and set its origin. This method fails if it recognized dependency recursion.
-->
## ResetOrigin

Returns the entity to using its parent as its frame of reference. The local
transform is recomputed so the entity stays where it is in the world, and the
dependency on the old origin is dropped.

Note the asymmetry with `SetOrigin`: this call does not create a
`transform_component`. On an entity without one there is nothing to reset, and
the call simply does nothing.

<!-- engine text:
Resets the origin of this entity, which will now default to its parent
-->
## origin

The interface behind an entity's alternative frame of reference. Its single
member, `GetTransform()`, supplies the transform that a `transform_component`
composes its local transform with — the role a parent entity plays by
default.

The interface is `<epic_internal>`, so the implementations are the engine's:
`entity_origin` for following another entity, plus internal variants for
following an actor or a socket on one. What matters for user code is that a
transform hierarchy need not match the ownership hierarchy, and `origin` is
where the two part company.

<!-- engine text:
Interface to provide alternative origin to an entity which is defaulted to its parent. See `transform_component`
-->
## entity_origin

Makes one entity the frame of reference for another. Its `GetTransform`
override simply returns `Entity.GetGlobalTransform()`, so the follower's local
transform is measured against the target's world transform — the same
arithmetic as parenting, but with no effect on ownership or lifetime.

It is more than a stored pointer. The `transform_component` registers a
dependency on the target's transform, so the follower is updated when the
target moves, exactly as a child would be. The target's transform is also
replicated on the origin itself, which covers the case where the target entity
is not replicated to a given client and so cannot be consulted there.

<!-- engine text:
class to provide alternative origin to the 'transform_component' as an entity
-->
## entity_origin.GetTransform

The transform of the entity being used as the origin.

<!-- no documentation in the engine source -->
## execution_listenable

The `listenable(float)` handed out by each phase of a component's
`tick_events`, where the payload is the delta time since the previous update.
You can either `Subscribe` a callback or `Await` it in a suspending task,
which is what makes both the callback and the per-frame-loop styles of
component available from the same object.

<!-- engine text:
Users to subscribe to, or await on, a DeltaTime based callback from one of the phases in a component's `TickEvents` object.
-->
## execution_listenable.Await

Suspends until the phase next runs, returning that frame's delta time.
Awaiting in a loop inside `OnSimulate` gives you a per-frame update without
any subscription to keep or cancel: when `OnSimulate` is cancelled at the end
of simulation, the loop goes with it.

<!-- engine text:
Suspends the current task until resumed by a matching call to `signalable.Signal`. Returns the event `payload`.
-->
## execution_listenable.Subscribe

Registers a callback that receives the frame's delta time, and returns a
`cancelable`. Subscribing suits a component that reacts rather than loops, and
that wants to start and stop ticking independently of its `OnSimulate` task.

The returned `cancelable` is not optional bookkeeping. The component
documentation is explicit: keep it, and cancel it in `OnEndSimulation`, or the
callback outlives the simulation it belongs to.

<!-- engine text:
Subscribe a callback function to this TickEvent phase. The input parameter to your function (DeltaTime) is the time that has passed between the last update and the current update.
-->
## player.IsActive

The guard you must write before using a `player` as a key in a module-scoped
`var weak_map`. It is `<decides>`, so the idiom is `if (Player.IsActive[])`,
and the reason it exists is that the map access itself is not failable: using
an inactive `player` as a key raises a runtime error, which unwinds rather
than giving you a branch to handle. There is no recoverable form of that
mistake, so this check is the whole of your protection.

It succeeds for exactly the interval between the player joining the game and
leaving it, and it is a plain flag read — `<reads>` only, no allocation, no
world queries — so there is no cost to checking it at every use site. Note
that the runtime keeps the same `player` object for a returning player rather
than minting a fresh one, so a check that fails now may succeed again later:
an inactive `player` is dormant, not permanently dead, and code that caches
"this player is gone" can be wrong.

Because `player` is also `<persistent>`, a module-scoped `var weak_map` keyed
on it must have a `persistable` value type, and its contents survive the
session. That is the storage this check is protecting; a lookup in an ordinary
local `map` keyed by `player` needs no such guard.

<!-- engine text:
Succeeds when this `player` may be used as a module-scoped `var` `weak_map` key. This coincides with the corresponding player having joined the game and not yet left. Using a `player` as a module-scope `var` `weak_map` key when this method fails results in a runtime error.
-->
## session

A key type, essentially. There is one instance, reachable through
`GetSession`, and it is `<unique>` and `<module_scoped_var_weak_map_key>`,
which together make it the stand-in for a global variable: Verse will not let
you declare a module-scoped `var` of an arbitrary type, but it will let you
declare a `weak_map` whose key type carries that specifier, and a
session-keyed map with a single entry is a global in all but name.

Unlike `player` it is not `<persistent>`, so values stored against it need not
be `persistable` and are not saved anywhere — this is shared mutable state for
the running experience, not storage. Take the note about rounds seriously in
both directions: do not build on session-keyed state being wiped between
rounds, and do not build on it being carried across them either.

<!-- engine text:
Type for which there is a single instance per round.  Use `GetSession` to get the current round's `session` instance. May be used with `weak_map` to implement global variables.
Note: may be changed in a future release to a single instance per game. Round-local behavior should not be relied upon.
-->
## GetSession

Non-failable and `<reads>`, and it returns the same instance every time, so
there is nothing to cache and no benefit in threading a `session` value
through your code — call it at the point of use. It is the only way to obtain
a `session`; the class has no accessible constructor.

Its purpose is almost always to be the key in a `weak_map(session, ...)`
declared as a module-scoped `var`. Since the map has exactly one live key,
the usual restrictions on module-scoped weak maps (no length, no iteration, no
wholesale replacement) cost you nothing: you only ever read and write the one
entry.

<!-- engine text:
Returns the `session` corresponding to the current round.  The result can be used with `weak_map` to implement global variables.
Note: may be changed in a future release to return a single instance per game. Round-local behavior should not be relied upon.
-->
## session_environment

Distinguishes editing, playtesting and shipping, and is obtained from the
`Environment` accessor on `session` rather than being inferable from anything
else in the language. Enum values are `<computes>` and comparable, so the
normal shape is a `case` over the three alternatives.

This is the hook for behaviour that should not reach players: verbose logging,
cheat commands, shortened timers. Query it once and store the answer in your
own flag if you like, since it does not change under a running session.

<!-- engine text:
Specifies what type of environment the current session is in.
-->
## session_environment.Edit

The session was started from inside UEFN. Code guarded on this case will never
run for a player, which makes it the right place for authoring aids and for
work-arounds that only matter when the level is being edited.

<!-- engine text:
The current session is in an Edit environment for an experience, such as a session started within UEFN.
-->
## session_environment.Private

A private session such as a playtest: a real game running with real players,
but not a published one. Keep this distinct from `Edit` in your reasoning —
anything that assumes single-player or editor-only conditions is wrong here.

<!-- engine text:
The current session is in a Private environment for an experience, such as a playtest.
-->
## session_environment.Live

A published experience. It is also the fallback the runtime reports when the
environment has not been established, and the accessor does not fail in that
situation, so `Live` means "live, or not yet known". Treat it as the default
and put your restrictions on the other two cases rather than relying on `Live`
as proof of production.

<!-- engine text:
The current session is in a Live environment for an experience.
-->
## Sleep

Three of the argument's ranges are special cases rather than degrees of the
same thing. `0.0` resumes on the next update and, crucially, does yield, which
is what makes it the correct body of a per-frame coroutine loop. `Inf`
suspends with no timer at all, so the coroutine can only ever be resumed by
cancellation — that is the idiom for a `race` branch that must never win.
Negative values do not merely sleep briefly, they complete in place without
yielding, so a loop whose only suspension point is `Sleep(-1.0)` starves
everything else; the value is in being able to make yielding conditional on
data.

For positive finite waits, resumption is driven by the world's timer manager,
so this measures game time and not wall-clock time, and it is quantised to
ticks: a sleep resumes on the first update at or after its deadline and never
sooner than the next one. Short sleeps therefore round up, and a chain of them
accumulates error — do not build a clock out of `Sleep`, read
`GetSimulationElapsedTime` instead.

Cancellation is clean: the pending timer is cleared when the sleep is
cancelled, so a `race` that abandons a sleeping branch leaves nothing behind.

<!-- engine text:
Waits specified number of seconds and then resumes. If `Seconds` = 0.0 then it waits until next tick/frame/update. If `Seconds` = Inf then it waits forever and only calls back if canceled - such as via `race`. If `Seconds` < 0.0 then it completes immediately and does not yield to other aysnc expressions.
Waiting until the next update (0.0) is especially useful in a loop of a coroutine that needs to do some work every update and this yields to other coroutines so that it doesn't hog a processor's resources.
Waiting forever (Inf) will have any expression that follows never be evaluated. Occasionally it is desireable to have a task never complete such as the last expression in a `race` subtask where the task must never win the race though it still may be canceled earlier.
Immediately completing (less than 0) is useful when you want programmatic control over whether an expression yields or not.

-->
## GetSimulationElapsedTime

Seconds of simulated time since the level began playing. It is game time, not
real time — it shares its clock with `Sleep`, which is why the two agree with
each other, and it means the value stops advancing while the game is paused
and is scaled by time dilation. Use it for differences between two readings
rather than treating the absolute number as meaningful.

The value a client sees is the server's, reconstructed from a replicated
correction, so it can step slightly rather than advancing perfectly smoothly
there; on the server it is plain world time. Very early in a session, before
there is any game state to read, the call yields `0.0`, so a subtraction
against a timestamp captured at startup can legitimately come out as zero.

<!-- engine text:
Get the seconds that have elapsed since the world began simulating
-->
## has_tags

A mutable multiset of tag instances, not a set of tag types — which is the
single most important thing to know about it. Each `AddTag` stores a fresh
entry under a newly minted `tag_key`, so the same tag can be present many
times over, whereas every query and every bulk removal is expressed in terms
of a tag type and matches subclasses as well. Adding is by instance,
asking is by type.

The interface name is visible but only engine types may implement it. The one
that matters is `entity`, which forwards all eight methods to a tag component
created on demand, so tags on an entity are reached straight through the
entity. There is also an experimental standalone `tag_set` for tag collections
that are not attached to anything.

<!-- engine text:
An interface representing a mutable collection of tags.
-->
## has_tags.AddTag

Never fails and never deduplicates. It does not look to see whether an
equivalent tag is already present, so calling it twice with the same tag
leaves two entries behind and returns two different keys, and a subsequent
`ContainsTag` cannot tell you which situation you are in. If "at most one" is
part of your model, enforce it yourself with `ContainsTag` first.

The returned `tag_key` is the only handle to that particular entry, so keep it
if you will ever want to withdraw exactly this tag and leave others of the
same type alone; otherwise discard it and remove by type later. On an `entity`,
the first `AddTag` is what brings the underlying tag storage into existence —
before that, the query and removal calls simply find nothing.

<!-- engine text:
Adds a `tag` instance to this container. Returns a `tag_key` that is uniquely associated with the added instance.
-->
## has_tags.RemoveTag

Removes precisely the one entry the key names, leaving every other entry and
every other key untouched — keys are independent handles, not indices, so
nothing shifts underneath them. It fails when the key names nothing, which
includes calling it a second time with a key you have already used.

A key is only meaningful to the container it came from: passing a key obtained
from one container to another will not match, and fails. Being `<transacts>`
and `<decides>`, the call needs a failure context, and the natural reading of
that failure is "this tag was already gone".

<!-- engine text:
Removes the tag instance associated with the `tag_key`, succeeds if an instance was removed, fails otherwise.
-->
## has_tags.RemoveAllTags

Type-directed bulk removal, and inclusive of subclasses: passing an interior
tag type removes every instance of it and of every type derived from it, and
passing `tag` itself empties the container. This is where a hierarchy of tag
classes earns its keep — one call clears a whole category.

It fails when nothing matched, which makes it tempting to use as an existence
test. Prefer `ContainsTag` for that, since this call has already destroyed the
evidence by the time it tells you. Any `tag_key` referring to a removed
instance stops matching from here on.

<!-- engine text:
Removes all tag instances of type `tag_type`, succeeds if at least one instance was removed, fails otherwise.
-->
## has_tags.RemoveAllTagsExcept(castable_subtype(tag))

The complement of `RemoveAllTags`: instances of the given type and its
subtypes are kept and everything else is dropped, in a single pass. Useful for
resetting an object to one classification without having to know what else has
accumulated on it.

Failure means nothing was dropped — the container already held only matching
tags, or held nothing at all — so a failure here is a statement about what was
not removed, the opposite polarity from most of the other calls in this
interface. As with the other bulk removals, keys naming dropped instances go
dead.

<!-- engine text:
Removes all tag instances that are not of type `tag_type`, succeeds if at least one instance was removed, fails otherwise.
-->
## has_tags.RemoveAllTagsExcept([]castable_subtype(tag))

Same operation as the single-type overload, generalised: an instance survives
if it matches any one of the listed types, subclasses included, and is dropped
otherwise. Overload resolution is on the argument type alone, so passing an
array of one is equivalent to passing that type directly.

The array form is a single pass over the container, which is not just faster
than a sequence of single-type calls but semantically different: applying the
single-type version twice would leave nothing, because the second call would
drop what the first one spared.

<!-- engine text:
Removes all tag instances that are not of any of the types in `tag_types`, succeeds if at least one instance was removed, fails otherwise.
-->
## has_tags.ContainsTag

The right way to ask a yes/no question about a tag type, and subclass
inclusive: a query for a parent type succeeds when the container holds any
instance of a derived type. It is `<reads>` and `<decides>`, so it drops
straight into an `if` guard and costs nothing beyond the scan.

It answers "at least one", not "how many". Since `AddTag` allows duplicates,
a container may hold several instances matching the query and this call cannot
distinguish that from one — if the count matters, you need to track it
yourself.

<!-- engine text:
Succeeds if at least one tag of type `tag_type` is found in this container, fails otherwise.
-->
## has_tags.ContainsAllTags

Conjunction over a list of tag types, each matched subclass-inclusively, and
it gives up on the first one it cannot find. The empty-array case succeeds,
which is the mathematically correct answer and also a genuine trap: if the
list is data-driven and a configuration mistake leaves it empty, every object
passes the check.

Pair the reading of this with `ContainsAnyTag`, which fails on an empty list.
The two disagree there on purpose — each returns the identity of its own
operation — so when the list may be empty, decide explicitly which of the two
answers you want rather than letting the choice of call decide for you.

<!-- engine text:
Fails if at least one type in `tag_types` cannot be found in this container, succeeds otherwise. Note that this means that if `tag_types` is empty this call succeeds.
-->
## has_tags.ContainsAnyTag

Disjunction over a list of tag types, subclass-inclusive, succeeding as soon
as one is found. An empty list fails, since there is nothing that could
succeed.

That makes it the safer of the two list queries for data-driven input: an
empty requirement list rejects rather than admits. When you want the other
polarity — an empty list meaning "no constraints" — `ContainsAllTags` is the
call, but say so deliberately in a comment, because the asymmetry between the
two is easy to misread later.

<!-- engine text:
Succeeds if at least of the types in `tag_types` is found in this container, fails otherwise. Note that this means that if `tag_types` is empty this call fails.
-->
## tag

The root of the user-defined tag hierarchy, and the hierarchy really is class
inheritance: you declare tags by subclassing, and a subclass is a more
specific tag, so a query for the parent type matches instances of any child.
That is what "hierarchically evaluate a classification" amounts to — there is
no separate string-based tag namespace to learn, only Verse classes.

The class is `<abstract>`, so `tag` itself is never instantiated, and the same
trick works one level down: making interior nodes of your hierarchy abstract
and only the leaves concrete gives you categories that can be queried but not
attached. Only concrete tag classes can actually be added to a container.

`<castable>` is what makes the rest of the API possible. It is the specifier
that permits `castable_subtype(tag)`, which is how every query and bulk
removal names a tag — they take a type and test stored instances against it at
runtime, rather than comparing instances for equality.

<!-- engine text:
A base type used for tagging objects in order to hierarchically evaluate an objects classification.
-->
## tag_key

An opaque handle, minted afresh by every `AddTag` call. Two adds of the same
tag — even the very same instance — produce two different keys, because the
key identifies the entry rather than the tag; there is nothing in it derived
from the tag's type, and no accessible fields, so its only use is to be handed
back to `RemoveTag`.

Keys are unique across containers rather than being positions within one, so
they cannot be confused between containers, but equally a key from one
container will simply fail to match in another. The struct is `<internal>`
with no public constructor, so you cannot fabricate or default-construct one:
if you did not keep the value `AddTag` returned, removal by type is your only
route.

<!-- engine text:
A `tag_key` is the return value from adding a `tag` to a container implementing the `has_tags` interface, and is used to selectively remove such an instance from the same container.
-->
## tag_search_sort_type.Unsorted

One of the two values of the `SortType` field on `tag_search_criteria`,
selecting results in whatever order the search produced them. It belongs
entirely to the deprecated tag-search API; new code should use the
`FindCreativeObjectsWithTag` family, which has no sort flag.

<!-- no documentation in the engine source -->
## tag_search_sort_type.Sorted

Requests that search results be sorted by tag, and is the default value of
`tag_search_criteria.SortType`, so the old search API sorts unless you
explicitly ask it not to. Like its counterpart it exists only for that
deprecated class.

<!-- no documentation in the engine source -->
## tag_search_criteria

The query object of the superseded tag search, holding three tag lists and a
sort flag. The semantics of the lists are not symmetric: `RequiredTags` must
all be present, `ExclusionTags` disqualify a match outright, and
`PreferredTags` are consulted only when `RequiredTags` is empty, where they
act as an any-of. So supplying both required and preferred tags silently
ignores the preferred ones.

The lists hold `tag` instances rather than tag types, which is exactly what
the replacement API changed: `FindCreativeObjectsWithTag` takes a tag type and
matches subclasses, giving you the hierarchy for free instead of requiring an
instance per tag you want to mention. Prefer it; this class is deprecated and
the compiler will say so.

<!-- engine text:
Advanced tag search criteria
-->
## tag_view

The read-only query interface of the previous tag API, superseded by
`has_tags`. The difference is not only that this one cannot mutate: its
queries are phrased in terms of tag instances rather than types, and its
backing container stores a plain list of tag types with no per-entry handles,
so there is nothing corresponding to `tag_key` and no way to speak about one
occurrence rather than another.

Within the engine the only implementer is the equally deprecated
`tag_container`. If you are holding a `tag_view`, the three methods below are
all you can do with it; if you are choosing an API, go to `has_tags` through
`entity`.

<!-- engine text:
A queryable collection of tags.
-->
## tag_view.Has

Hierarchical containment in one direction only, and it is worth being precise
about which. A container holding the child tag answers yes when asked about
the parent, because holding a refinement implies holding the classification; a
container holding only the parent answers no when asked about the child,
because the classification does not imply any particular refinement. The
question this call really asks is "do I have this classification, or something
more specific than it?".

An invalid tag always fails rather than raising anything, so a query built
from unset data quietly reports absence.

<!-- engine text:
Determine if TagToCheck is present in this container, also checking against parent tags {"A.1"}.Has("A") will return True, {"A"}.Has("A.1") will return False If TagToCheck is not Valid it will always return False.
-->
## tag_view.HasAny

Disjunction: succeeds if any tag in the argument is present, with the same
parent-matching direction as `Has` — a container holding `A.1` matches a query
containing `A`, but a container holding `A` does not match a query for `A.1`.
An empty or invalid argument always fails, there being nothing that could
match.

<!-- engine text:
Checks if this container contains ANY of the tags in the specified container, also checks against parent tags {"A.1"}.HasAny({"A","B"}) will return True, {"A"}.HasAny({"A.1","B"}) will return False If InTags is empty/invalid it will always return False.
-->
## tag_view.HasAll

Conjunction, with the same one-directional parent matching. An empty argument
succeeds, on the grounds that no check failed — the same asymmetry with
`HasAny` that the newer `ContainsAllTags` and `ContainsAnyTag` inherited, and
the same hazard when the tag list comes from configuration rather than from
source. Check for emptiness yourself if "no tags listed" ought to mean
something other than "everything matches".

<!-- engine text:
Checks if this container contains ALL of the tags in the specified container, also checks against parent tags {"A.1","B.1"}.HasAll({"A","B"}) will return True, {"A","B"}.HasAll({"A.1","B.1"}) will return False If InTags is empty/invalid it will always return True, because there were no failed checks.
-->
## Rotation:rotation

An opaque `FQuat` with no Verse-visible members, so it can only be built by
the module's constructor functions — or as the empty archetype
`rotation{}`, which is the identity, since the native quaternion defaults
to `FQuat::Identity`.

Being `<uht_comparable>`, this version supports `=` and `<>`, but the
comparison is a bitwise-exact test of all four quaternion components. Two
rotations that describe the same orientation will compare unequal if they
differ in the last bits, and — because a unit quaternion and its negation
denote the same orientation — even mathematically identical orientations
can compare unequal. Use `Distance` or `AngularDistanceRadians` with a
tolerance instead. It is also `<predicts>` and replicatable, so it can
cross the network and take part in client-side prediction; it is not
`<persistable>`.

Old saved data containing the deprecated `rotation` upgrades into this type
automatically, copying the quaternion straight across. The orientation is
therefore unchanged by the migration — what changes is that this module's
axis and angle accessors use a right-handed convention where the older
module used a left-handed one.

<!-- engine text:
An abstract representation of an orientation change in 3d-space.
-->
## MakeRotationRadians

Right-handed, in contrast to the deprecated `MakeRotation`: the native code
negates the angle when building the quaternion, so a positive rotation
about `Up` takes `Forward` towards `Left`. The axis is normalised for you
and need not be unit length.

The important difference from `MakeRotation` is what happens to a
degenerate axis. There is no zero-length check here — the implementation
takes an unguarded inverse square root — so a zero or vanishingly small
axis yields a non-finite rotation rather than the identity. Guard the input
with `IsAlmostZero[]`, or check the result with `IsFinite[]`, if the axis is
computed rather than a literal. Use `MakeRotationDegrees` if your angle is
in degrees; it is a thin wrapper over this function. Both carry an
`@available` guard requiring an upload version of at least 3600, added so
the new names cannot collide with functions of the same name in
already-published projects.

<!-- engine text:
Makes a `rotation` from `Axis` and `Angle` in radians using a right-handed sign convention (e.g. a positive rotation around Up takes Forward to Left).
-->
## Rotation:MakeRotationFromYawPitchRollDegrees(float,float,float)

Despite the module's switch to right-handed axes, this constructor is
byte-for-byte the same native code as the deprecated module's version: an
Unreal `FRotator(Pitch, Yaw, Roll)` converted to a quaternion. Its
conventions therefore did not change, which makes it the odd one out here —
a positive yaw is still clockwise seen from above, a positive pitch is
still nose up, and a positive roll is still clockwise looking along
`Forward`. The module documents that as right-handed rotation about `Down`,
`Right` and `Forward`, which is the same thing said in the new axis names.

The rotations are intrinsic: yaw first, then pitch about the already-yawed
axis, then roll about the axis both have moved. That makes it distinct from
`MakeRotationFromEulerRadians`, which composes about fixed axes in a
different order — the two are not interchangeable even after matching
signs. `MakeRotationFromYawPitchRollRadians` is a Verse-level wrapper that
converts to degrees and calls this, so radians users pay a conversion but
get identical behaviour.

<!-- engine text:
Degrees version of `MakeRotationFromYawPitchRollRadians`
-->
## MakeRotationFromEulerRadians

Builds three quaternions about the fixed `Left`, `Up` and `Forward` axes,
each with the angle negated to give right-handed sense, and composes them
so that a vector is turned about `Left` first, then `Up`, then `Forward`.
Crucially the axes do not travel with the object: these are fixed-axis
rotations, unlike the intrinsic yaw-pitch-roll of
`MakeRotationFromYawPitchRollDegrees`. Different axis order and different
kind of composition, so do not expect the two to agree.

Angles are in radians; `MakeRotationFromEulerDegrees` converts and
delegates. `GetEulerRadians` is the matching decomposition, with the
caveats about range noted there. Like most of the renamed entry points in
this module it is gated behind an `@available` upload-version guard.

<!-- engine text:
Makes a `rotation` by applying a post-rotation of `LeftAxisAngle` followed by `UpAxisAngle` and then `ForwardAxisAngle `in that order. Right-handed convention (e.g. a positive rotation around Up takes +Forward to Left).
-->
## Rotation:IdentityRotation()

Returns `FQuat::Identity`, is `<converges>`, and is the default value of
`transform.Rotation`. The archetype `rotation{}` produces the same value,
so this is a matter of expressing intent at the call site.

The degenerate accessor behaviour is worth remembering: `GetAngleRadians`
on the identity is `0.0`, but `GetAxis` has no meaningful answer and falls
back to a fixed axis — see `GetAxis` for what actually comes out, which is
not what the engine comment claims.

<!-- engine text:
Makes the identity `rotation`.
-->
## Rotation:Distance(rotation,rotation)

The same `1.0 - Abs(DotProduct(Q1, Q2))` as in the deprecated module, which
is `1 - Abs(Cos(Angle/2))`. No trigonometry is involved beyond the dot
product, and it is `<converges>`, so it is the cheapest way to ask "are
these two rotations close?".

The scale is not linear in the angle, which trips people up: a value of
`0.5` corresponds to 120 degrees of separation, not 90. Use it for
thresholds and ordering, and switch to `AngularDistanceRadians` or
`AngularDistanceDegrees` when you need an actual angle.

<!-- engine text:
Returns the distance between `Rotation1` and `Rotation2`. The result will be between:
 * `0.0`, representing equivalent rotations and
 * `1.0` representing rotations which are 180 degrees apart (i.e., the shortest rotation between them is 180 degrees around some axis).
-->
## AngularDistanceRadians

Builds the shortest rotation between the two arguments — flipping the sign
of one quaternion when needed to take the short arc — and returns its
angle, so the result is always in `[0.0, PiFloat]` radians. That is a
genuine angle, unlike `Distance`, at the cost of an `Acos`.

`AngularDistanceDegrees` wraps it for degrees. Both carry the `@available`
upload-version guard that protects already-published projects from name
collisions, so very old projects see only the older module's
`AngularDistance`.

<!-- engine text:
Returns the smallest angular distance between `Rotation1` and `Rotation2` in radians.
-->
## operator'*'(rotation,rotation)

Composition that reads in application order, left to right: `PreRotation`
is applied first and `PostRotation` second, so `V * A * B` and `V * (A * B)`
agree. The native implementation reverses the quaternion product to make
that true, because Unreal's `FQuat` multiplication composes in the opposite
direction — a nicety that spares you the usual quaternion order confusion.

The result is renormalised on every call, so long chains of small rotations
will not accumulate scale error. This replaces the deprecated `RotateBy`,
with the same operand order. There is no `UnrotateBy` and no division
operator here: compose with `Invert()` to remove a rotation, as
`R * R.Invert()` is the identity.

<!-- engine text:
Apply a `PreRotation` to `PostRotation` as `v * PreRotation * PostRotation`.
-->
## Rotation:GetYawPitchRollDegrees()

Returns a `tuple(float, float, float)` of yaw, pitch and roll, so the
components are extracted with plain indexing and no failure context — the
fix for the deprecated module's `[]float`. Degrees, matching
`MakeRotationFromYawPitchRollDegrees`, and `GetYawPitchRollRadians` is a
wrapper that converts each element of this result.

The values come from Unreal's quaternion-to-`FRotator` conversion and are
canonicalised: pitch comes from an arcsine and lies in `[-90.0, 90.0]`,
while yaw and roll come from `Atan2` and lie in `(-180.0, 180.0]`. Within a
whisker of ±90 degrees of pitch the decomposition hits gimbal lock, sets
roll to `0.0` and folds the remainder into yaw, so a round trip preserves
the orientation but not necessarily the triple you started from.

<!-- engine text:
Degrees version of `GetYawPitchRollRadians`.
-->
## GetEulerRadians

The inverse of `MakeRotationFromEulerRadians`, returning the three
fixed-axis angles in radians in `Left`, `Up`, `Forward` order.
`GetEulerDegrees` converts the result.

The middle element is the one to watch. It is recovered with an arcsine, so
it is confined to `[-PiFloat/2, PiFloat/2]`, while the other two come from
`Atan2` and span the full `(-PiFloat, PiFloat]`. As the `Up` angle
approaches either limit the split between the `Left` and `Forward` angles
becomes ill-conditioned in the familiar gimbal-lock way, so a round trip
through `MakeRotationFromEulerRadians` reproduces the rotation but not
necessarily your numbers. The engine text's `MakeRotationEulerRadians` is a
typo for `MakeRotationFromEulerRadians`.

<!-- engine text:
Makes a `tuple(float, float, float)` with three elements:
 * *left axis* `rotation` in radians
 * *up axis* of `rotation` in radians
 * *forward axis* of `rotation` in radians
using the conventions of `MakeRotationEulerRadians`.
-->
## Rotation:GetAxis()

Returns a unit vector, and applies the module's right-handed flip by
negating Unreal's rotation axis. Because the underlying angle is
`2 * Acos(W)` and therefore never negative, that negation happens on every
call, not only for some rotations.

The near-identity case does not behave as documented. When the quaternion's
vector part is smaller than `1.0e-8` in squared length there is no axis to
report and Unreal falls back to its `+X`; the unconditional negation then
turns that into `vector3{Forward := -1.0, Left := 0.0, Up := 0.0}`. So an
identity rotation yields the backward axis, not the `+Forward` the engine
comment promises. Treat the axis of a near-identity rotation as meaningless
and check `GetAngleRadians` first. Pair this with `GetAngleRadians` for a
full axis-angle decomposition.

<!-- engine text:
Makes a `vector3` from the axis of `rotation` for an right-handed angle.
If `rotation` is nearly identity, this will return the +Forward axis. See also `GetAngleRadians`.
-->
## GetAngleRadians

Computed as the absolute value of `2 * Acos(W)`, in radians. For a
well-formed unit quaternion `Acos` already returns a non-negative value, so
the absolute value is belt-and-braces; what matters is the range, which is
`[0.0, 2*PiFloat]` and not `[0.0, PiFloat]`. A rotation authored as three
radians about an axis reports three radians, not the shortest equivalent
turn the other way.

`GetAngleDegrees` wraps it. If you want the shortest angle, use
`AngularDistanceRadians` against `IdentityRotation()`, which enforces the
short arc. Like the other `*Radians` renames, this one is behind an
`@available` upload-version guard.

<!-- engine text:
Returns the radians of right-handed `rotation` around the axis of `rotation`. See also `GetAxis`.
-->
## Rotation:MakeShortestRotationBetween(vector3,vector3)

Both vectors may be any length — the implementation divides out
`Sqrt(LengthSquared(A) * LengthSquared(B))` — so only their directions
matter, and the roll about the resulting axis is the smallest possible.

Neither degenerate case fails. Antiparallel vectors have no preferred axis,
so an arbitrary perpendicular is chosen and you get a half-turn about it;
which perpendicular is an implementation detail, so do not depend on it. A
zero-length input collapses the intermediate quaternion to all zeroes,
and normalisation snaps that to the identity, so you get
`IdentityRotation()` rather than `NaN`s. Unlike the deprecated module,
there is no `rotation`-to-`rotation` overload here; compose with `Invert()`
instead.

<!-- engine text:
Makes the smallest angular `rotation` from `InitialVector` to `FinalVector` two vectors of arbitrary length such that:
`InitialVector * MakeShortestRotationBetween(InitialVector, FinalVector) = FinalVector` and
`MakeShortestRotationBetween(InitialVector, FinalVector)?.GetAngleRadians()` is as small as possible.
-->
## Rotation:Slerp(rotation,rotation,float)

Note what is missing compared with the deprecated version: this one is not
`<decides>`. The range check has gone, and a `Ratio` outside `[0.0, 1.0]`
now extrapolates along the great arc rather than failing or clamping. If
your ratio comes from a timer or user input, clamp it yourself.

Interpolation takes the shorter arc, achieved by flipping the sign of the
second quaternion when the dot product is negative. When the two rotations
are nearly aligned — cosine above `0.9999` — it falls back to a
component-wise lerp followed by normalisation, avoiding a division by a
vanishing sine; at that separation the two are indistinguishable anyway.

<!-- engine text:
Used to perform spherical linear interpolation between `From` (when `Ratio = 0.0`) and `To` (when `Ratio = 1.0`). Expects `0.0 <= Ratio <= 1.0`.
-->
## operator'*'(vector3,rotation)

The rotation is applied to the vector by quaternion, so length is preserved
up to floating-point error and the function serves equally for directions
and for points about the origin. `Vector` is not normalised first.

Writing it as an operator is what makes rotation chains read in order:
`V * A * B` turns `V` by `A` and then by `B`. The axis-convention flip
between Verse's `Forward`/`Left`/`Up` and Unreal's `X`/`Y`/`Z` is handled
inside the conversion, so no manual sign fiddling is needed. For the
inverse direction — world space to local — use
`Vector * Rotation.Invert()`; there is no `UnrotateVector` in this module.
`transform` has a matching
`operator'*'` that adds scale and translation.

<!-- engine text:
Makes a `vector3` by applying `Rotation` to `Vector`.
-->
## Rotation:Invert()

The quaternion conjugate: three sign flips, no normalisation, no
trigonometry. It is the true inverse because every `rotation` this module
produces is unit length, and it is `<converges>` and exact, so
`Rotation * Rotation.Invert()` normalises to precisely the identity.

The engine text refers to an `ApplyRotation` function that does not exist;
in this module composition is spelled with `*`. Inversion is also how you
express the operations this module dropped — `A * B.Invert()` removes a
rotation `B` that was applied after `A`, and `Vector * Rotation.Invert()`
replaces the deprecated `UnrotateVector`.

<!-- engine text:
Makes a `rotation` by inverting `Rotation` such that `ApplyRotation(Rotation, Rotation.Invert())) = IdentityRotation`.
-->
## Rotation:IsFinite()

Checks the four components of the underlying quaternion and returns the
rotation itself on success, so it composes neatly inside a failure context.
It does not verify that the quaternion is unit length, so a denormalised
rotation will pass.

This matters more here than in the deprecated module, because
`MakeRotationRadians` normalises its axis without a zero-length guard: feed
it a computed direction that happens to collapse to zero and you get a
rotation full of `NaN`s that will silently poison every vector it touches.
Either test the axis with `IsAlmostZero[]` beforehand or check the rotation
with this afterwards.

<!-- engine text:
Returns `Rotation` if it does not contain `NaN`, `Inf` or `-Inf`.
-->
## Transform:transform

Scale, then rotation, then translation, mirroring Unreal's `FTransform`,
which is what it converts to natively. All three fields have defaults —
zero translation, identity rotation, unit scale — so `transform{}` is the
identity and partial archetypes work.

It is `<computes>` and `<predicts>` and `<uht_comparable>`, the last of
which means `=` compares all three parts exactly, component by component,
with the same bitwise strictness as `vector3` and `rotation`. It is
replicatable but not `<persistable>`, so a `transform` cannot be stored
directly in persistent state — save the `vector3`s and rebuild the rotation
from angles instead.

Apply it with `operator'*'(vector3, transform)`, defined in Verse as
`((Scale * V) * Rotation) + Translation`, which makes the order of
operations plain. There is deliberately little else: no composition of two
transforms, no inverse, and no no-scale variant of the sort the deprecated
module offered as `TransformVectorNoScale`.

<!-- engine text:
A combination of scale, rotation, and translation, applied in that order.
-->
## Transform:transform.Translation

The transform's position, applied last, after scale and rotation, and
expressed in whatever space the transform belongs to. Defaults to the
origin, and is the first field declared — the deprecated `transform`
declared the same three fields in the opposite order.

It is a direction-and-position `vector3`, so converting it to Unreal
negates the `Left` component to produce Unreal's `Y`. That distinction is
exactly what separates it from `Scale`, which is converted as a triple of
scalars.

<!-- engine text:
The location of this `transform`.
-->
## Transform:transform.Rotation

Defaults to `IdentityRotation()`, and is applied after `Scale` and before
`Translation` — so a non-uniform scale stretches along the transform's own
axes and the result is then turned.

Because it is the `/Verse.org/SpatialMath` `rotation`, its axis and angle
accessors follow this module's right-handed convention, and it is compared
by exact quaternion components. Note that the rotation is applied to the
already-scaled vector: with a non-uniform `Scale`, changing `Rotation`
changes the direction in which the stretch is oriented, not just the final
heading.

<!-- engine text:
The rotation of this `transform`.
-->
## Transform:transform.Scale

Defaults to `vector3{Forward:=1.0, Left:=1.0, Up:=1.0}` and is applied
component-wise, before the rotation, in the transform's own axes. Nothing
validates it: zero flattens an axis and a negative value mirrors it.

The interesting part is that it is marked with `@units("x")` in the source,
which flags it as a multiplier rather than a direction. Two things follow.
Natively it is converted to Unreal without negating the `Left` component,
unlike `Translation`. And the editor's data upgrade that flipped the sign
of every saved `Left` value when the module moved from right-handed to
left-handed naming deliberately skipped properties marked as multipliers,
so old scale values were left alone. If you are converting a scale from the
deprecated module by hand, use `FromScalarVector3`, not `FromVector3`.

<!-- engine text:
The scale of this `transform`.
-->
## Vector3:vector3

Three doubles named for directions rather than letters: `Forward`, `Left`
and `Up`, all defaulting to `0.0`, so `vector3{}` is the origin. The names
are not merely friendlier — `Left` is the negation of Unreal's `Y`, and
that single sign change turns Unreal's left-handed basis into a
right-handed one, with `CrossProduct(Forward, Left) = Up`. That is why
every rotation function in this module uses a right-handed sign convention
while the deprecated module's uses a left-handed one, and why the module
also exposes a `CrossProductLeftHanded` for the older behaviour.

The struct is `<computes>`, `<persistable>`, `<predicts>`,
`<uht_comparable>` and replicatable, making it the only one of the three
spatial types you can store in persistent state. Equality is exact,
component by component, so use `IsAlmostEqual` with a tolerance for
geometry that has been through arithmetic.

One regression to be aware of when porting: `MakeUnitVector` here is not
failable. It simply divides by the length, so a zero-length vector produces
`NaN` components rather than failing as the deprecated module's version
did. The same is true of `ReflectVector`, which normalises the surface
normal on your behalf without checking it. Test with `IsAlmostZero[]` first.

<!-- engine text:
3-dimensional vector with `float` components.
-->
## vector3.Left

Positive towards the object's left, and the negation of Unreal's `Y`, which
points right. Defaults to `0.0` and is `@editable`. This is the component
that carries the module's whole handedness story: `LeftAxis()` is
`vector3{Left := 1.0, ...}` while `RightAxis()` is `Left := -1.0`, and the
native conversions negate it going in either direction.

Data saved before the axis was renamed from `Right` to `Left` is repaired
on load by negating this component — except on properties marked as
multipliers, such as `transform.Scale`, which are magnitudes and must not
be flipped. If you carry a value across from the deprecated `vector3.Y` by
hand rather than through `FromVector3`, remember the sign.

<!-- engine text:
The Left (was -Y) component of this vector.
-->
## vector3.Up

Unreal's `Z` axis, unchanged in name's spirit and in sign, defaulting to
`0.0` and `@editable`. It is the one component that survives conversion
between the two `vector3` types untouched.

This is also the component that `LengthForwardLeft`,
`LengthSquaredForwardLeft`, `DistanceForwardLeft` and
`DistanceSquaredForwardLeft` deliberately ignore — the renamed successors
of the `*XY` functions — which is how you measure ground distance between
two points at different heights.

<!-- engine text:
The Up (was Z) component of this vector.
-->
## vector3.Forward

Unreal's `X` axis, forward, with the same sign, defaulting to `0.0` and
`@editable`. `ForwardAxis()` returns the unit vector along it and
`BackwardAxis()` its negation.

It is also the axis that degenerate rotations fall back on: `GetAxis` on a
near-identity `rotation` returns a vector along `Forward` — with a negative
sign, in practice — because the underlying quaternion has no axis to
report.

<!-- engine text:
The Forward (was X) component of this vector.
-->
## cancelable

The runtime's universal "undo this registration" interface, returned by
`subscribable.Subscribe`, `modifier_stack.AddModifier` and similar
registration calls. It is an ordinary Verse interface, so your own classes
can implement it and hand out cancellation handles in the same idiom.

`Cancel` being `<native_callable>` means native code can drive a Verse
implementation, which is how engine subsystems tear down registrations made
from Verse. Note that `cancelable` says nothing about lifetime: holding a
`cancelable` does not keep the thing it cancels alive.

<!-- engine text:
Implemented by classes that allow users to cancel an operation. For example, calling `subscribable.Subscribe` with a callback returns a `cancelable` object. Calling `Cancel` on the return object unsubscribes the callback.
-->
## cancelable.Cancel

Idempotent by convention throughout the engine — every implementation checks
whether it still holds anything before unlinking, so cancelling twice, or
cancelling after the underlying object has been torn down, does nothing. That
makes it safe to cancel defensively.

Being `<transacts>` has a real consequence: a cancel performed inside a
transaction that later rolls back is undone. Event subscriptions make this
explicit by re-registering the callback on rollback, so a speculative cancel
inside a failed `if` leaves the subscription intact.

<!-- engine text:
Prevents any current or future work from completing.
-->
## classifiable_subset

Despite the name it is a bag, not a set. Elements are stored in a map from a
freshly minted unique key to the element, so nothing is ever deduplicated:
constructing one from `array{X, X}` gives two entries. Those per-element keys
are the whole trick — they allow an element to be removed without any notion
of value equality, which is essential because the element type is not
required to be comparable.

Every operation returns a new subset rather than mutating one; the
`classifiable_subset_var` wrapper exists purely because Verse has no `ref`
keyword yet, and is documented in the source as temporary. The class is
`<final>` and `<computes>`, and implements `diagnosable` by printing its own
full object name followed by each element's diagnostic string.

It is `internal` and experimental, and most of the interesting operations —
`Contains`, `FilterByType` and friends — are extension methods constrained to
`castable_subtype`, so in practice the element type has to be a castable
class even though the class itself does not demand it.

<!-- engine text:
A `classifiable_subset` is a container that holds a set of elements. A classifiable_subset can hold multiple elements of the same type.
-->
## MakeClassifiableSubset

Gives every element of `InElements` its own unique key, which is why
duplicates survive and why the resulting subset always holds exactly
`InElements.Length` entries. The input's order is not retained — a subset has
no order, and iterating one visits elements in map order.

Being `<converges>` it is effect-free and guaranteed to terminate, so it can
be called from the strictest contexts, including where the compiler needs to
prove a loop finishes.

<!-- engine text:
Constructs a `classifiable_subset` containing the `InElements`.
-->
## operator'+'(classifiable_subset(t),classifiable_subset(t))

Union by key rather than by value. The two element maps are appended, and
since keys are unique per element nothing collapses: the result contains
every element of both operands, duplicates included, and its size is the sum
of the two sizes. Neither operand is modified — the result is a brand new
subset.

The one case where an element is dropped is a key present in both operands,
which happens when the two sets both derive from a common ancestor; the
right-hand entry then wins, but it is the same element, so the outcome is
what you would want anyway. Keys survive the operation, so a key obtained
when an element was originally added still identifies that element in the
sum, and in anything derived from it.

<!-- engine text:
Returns a new set that is the union of all elements in `InSetL` set and `InSetR`.
-->
## FilterByType

A runtime type test applied across a whole container: each element's dynamic
type is checked against `element_type` and the matches are kept, subclasses
included. Cost is linear in the number of elements and the input is left
alone.

Two details make it more useful than it first appears, and one less. Keys are
preserved, so a key obtained earlier still refers to the same element in the
filtered result — filtering does not invalidate your removal handles. But the
static type does not narrow: you get back `classifiable_subset(t)`, not
`classifiable_subset(element_type)`, so you still have to cast the individual
elements when you come to use them.

<!-- engine text:
Returns a new set that contains all the elements in `InSet` that are of type `element_type`.
-->
## disposable

The weaker half of a pair: `disposable` asserts that an object has a bounded
lifetime, and `invalidatable` — which extends it — adds the ability to ask
whether that lifetime has ended. Nothing in the runtime calls `Dispose` for
you, and the interface carries no state, so it is a convention made
type-checkable rather than a managed resource system.

<!-- engine text:
Implemented by classes whose instances have limited lifetimes.
-->
## disposable.Dispose

Declared without `<decides>`, so it cannot report failure; implementations
are consequently expected to tolerate being called on an object that has
already been disposed. Nothing in the language enforces that a disposed
object stops working, and there is no "is disposed" query here — a class
whose callers need to check should also implement `invalidatable`.

<!-- engine text:
Cleans up this object.
-->
## enableable

Three members: `Enable()`, `Disable()` and `IsEnabled[]`. The interface fixes
only the shape of the vocabulary, not its meaning: what "disabled" does to an
object — stop ticking, stop responding, become invisible — is entirely up to
the implementing class. It is deliberately separate from `showable`, so a
thing can be enabled but hidden, or visible but inert.

<!-- engine text:
Implemented by classes whose instances can be enabled and disabled.
-->
## enableable.IsEnabled

Reports its answer through failure rather than a `logic` return value, which
is the Verse idiom: it drops straight into an `if` condition, and `not
X.IsEnabled[]` is the test for disabled. There is no third state — an
`enableable` is always one or the other.

It is not `<computes>`, so the answer depends on mutable state and may differ
between two calls. Check it at the point of use rather than caching it across
a suspension point.

<!-- engine text:
Succeeds if the object is enabled, fails if it’s disabled.
-->
## Event:event(type)

A recurring rendezvous with no memory. A `Signal` reaches exactly the tasks
already suspended in `Await` and the callbacks currently subscribed; anyone
who arrives a moment later hears nothing at all. When a notification must not
be missed, use `sticky_event` instead.

The two delivery mechanisms have strikingly different guarantees. Suspended
awaiters resume in the order they suspended, and each runs until it blocks
before the next is resumed; awaits registered *during* a signal are moved
into a separate frame and are deliberately not resumed by that same signal.
Subscribed callbacks, by contrast, are invoked in a randomised order on every
signal, each inside its own transaction, and skipped entirely if the content
scope that registered them has gone away. The shuffle is intentional: it
stops one subscriber from silently coming to depend on running before
another.

Destroying an event does not cancel the tasks awaiting it — they simply never
resume.

<!-- engine text:
A *recurring*, successively signaled parametric `event` with a `payload` allowing a simple mechanism to coordinate between concurrent tasks.
-->
## event.Await

Registers the calling task in the event's FIFO queue and suspends. If the
awaiting task is cancelled it deregisters itself automatically, so an
abandoned awaiter does not keep the event holding a reference to a dead task.

There is no timeout and no failure mode: if the event is never signalled
again the call takes for ever, which is why this is normally combined with
`race` or a task group to bound it. Calling it while a `Signal` is in the
middle of resuming other tasks is safe but lands the new registration in a
fresh frame, so it waits for the *next* signal rather than the one in
progress — the property that makes an `Await`-in-a-loop pattern behave
sanely.

<!-- engine text:
Suspends the current task until another task calls `Signal`.
If called during another invocation of `Signal`, the the task will still suspend and resume during the next call to `Signal`.
-->
## invalidatable

Extends `disposable`, so anything invalidatable is also disposable. The
distinction is who ends the lifetime: `Dispose` is something you call,
whereas invalidity is something that happens to the object — typically
because the entity, actor or subscription it stands for was destroyed
elsewhere. An invalidatable reference is therefore one you must re-check
rather than one you must remember to clean up.

<!-- engine text:
Implemented by classes whose instances can become invalid at runtime.
-->
## invalidatable.IsValid

The idiomatic guard before touching a reference you have been holding across
time. Because it fails rather than returning `logic`, it reads naturally as a
condition and composes with `not`.

It is not `<computes>`: the answer can change between two calls, so check it
at the point of use rather than caching the result across a suspension point
or a frame boundary. The interface carries no notification of invalidation
either — if you need to be told rather than to ask, the API must also offer a
`subscribable`.

<!-- engine text:
Succeeds if this object is still valid.
-->
## Listenable:listenable(type)

Purely a conjunction. It declares no members of its own and simply inherits
`awaitable(payload)` and `subscribable(payload)`, so it exists to let an API
say "you may either wait for this or register a callback on it" in a single
type. A parameterless `listenable()` alias stands for `listenable(tuple())`.

In practice this is the type you see on public event fields — for instance
`agent_group_interface` exposes its membership changes as
`listenable(tuple(agent, member_info))`. Note that `event` itself does *not*
implement `listenable`; the class that does is internal, so the concrete
object behind a `listenable` field is usually hidden from you, and with it
the ability to signal it.

<!-- engine text:
A parametric interface combining `awaitable` and `subscribable`.
-->
## locale

An empty `epic_internal` struct — a placeholder for "which language", with no
fields yet. Nothing in the public localisation path takes one: the native
`Localize(Message:message)` reads the ambient culture from the running
content scope's world context rather than being told.

`locale` only surfaces as an optional `?Where` parameter on the trivial
`Localize` overloads for `string`, `int` and `float`, which ignore it
entirely and simply call `ToString`. Treat it as reserved space rather than a
knob you can turn.

<!-- engine text:
Used for message localization.
-->
## message

The runtime form of a `<localizes>` definition, and the reason localisation
in Verse works at all. It carries three things: a `Key` identifying the entry
in the compiled string tables, the `DefaultText` — the source string, which
doubles as the fallback when no translation exists — and a map of named
`Substitutions` holding the *values* captured at the point of construction.

Because it stores values rather than an already-formatted string, one
`message` can be rendered into any language, with numbers formatted according
to that culture. That is why the localisation-aware APIs take `message`
rather than `string`: converting to `string` throws away the information
needed to translate.

Only the key and default text are harvested for translation, in the editor,
and only when both are non-empty. A message synthesised at runtime therefore
has no table entry of its own — as `Join` demonstrates, its parts are
translated but its own text is not. The class is `epic_internal`, so build
messages with `<localizes>` definitions and interpolation rather than by
hand.

<!-- engine text:
A localizable text message.
-->
## Localize

Renders a `message` into a `string` for the current culture: looks up `Key`,
falls back to `DefaultText` when no translation is found, and substitutes the
captured values with culture-appropriate number formatting.

It is `<reads>` rather than `<computes>` for good reason — the result depends
on ambient state, namely the active culture and, on the Blueprint VM path,
the content scope's world context. Two calls with the same `message` can
therefore disagree, so do not cache the string across a culture change.

The practical advice is to localise as late as possible: pass `message`
values through your code and call `Localize` only at the point where you
genuinely need characters, because a `string` cannot be translated back. The
same-named overloads for `string`, `int` and `float` are conveniences that
just call `ToString` and ignore their optional locale.

<!-- engine text:
Makes a `string` by localizing `Message` based on the current `locale`.
-->
## Join([]message,message)

Builds a new `message` whose default text is a format string of the shape
`{0}{s}{1}{s}…{n}`, with each element bound to a numbered substitution and
the separator bound once under the key `s`. The result therefore stays
localisable: when `Localize` finally runs, every part is translated in its
own right, and the separator is stored only once no matter how long the list.

Two shortcuts are worth knowing. An empty `Messages` yields an empty message,
and a single-element `Messages` returns that very object rather than wrapping
it — so joining a one-element list is free and identity-preserving. The
joined message has no key of its own, so it is never itself looked up in a
string table.

Reach for this instead of `Localize`-then-`Join`-strings whenever the list is
assembled from translatable pieces; joining strings works, but it fixes the
language at the moment of joining.

<!-- engine text:
Makes a `message` by concatenating `Separator` between the elements of `Messages`.
-->
## Math:Clamp(int,int,int)

Returns the median of the three arguments, which is the tidy way of saying
that the order of `A` and `B` does not matter: `Clamp(5, 2, -2)` and
`Clamp(5, -2, 2)` both give `2`. The implementation takes the minimum and
maximum of the bounds before clamping, so there is no inverted-range case for
you to guard against and no assertion to trip.

Being the integer overload it is free of the subtleties of the `float`
version, where `NaN` behaves as though it were greater than `+Inf` and can
therefore be returned as the clamped result. `<computes>` and `<predicts>`,
so it is usable from pure contexts and from client prediction code.

<!-- engine text:
Constrains the value of `Val` between `A` and `B`. Robustly handles different argument orderings.
Returns the median of `Val`, `A`, and `B`.
-->
## Sin

Takes radians. Both infinities return `NaN` rather than failing — there is no
meaningful phase to report — and `NaN` propagates, as the engine's own tests
pin down.

Accuracy degrades with the magnitude of `X` in the way it always does: the
argument reduction is performed on the double you supplied, and by the time
`X` reaches around 1e16 consecutive representable inputs are further apart
than a whole period, so the result is essentially arbitrary. Reduce large
angles yourself before calling.

Note also that `Sin(PiFloat)` is not `0.0` but about 1.2e-16, because
`PiFloat` is only the nearest `float` to π. Compare results with
`IsAlmostZero` rather than `= 0.0`.

<!-- engine text:
Returns the sine of `X`, where `X` is interpreted as a value in radians, if `IsFinite[X]`.
Returns `NaN` if `not IsFinite[X]`.
-->
## Cos

Takes radians; `±Inf` gives `NaN` and `NaN` propagates. The same argument
reduction caveat as `Sin` applies — large magnitudes lose meaning long before
they lose finiteness.

The near-miss to watch for here is `Cos(PiFloat/2.0)`, which is about 6.1e-17
rather than `0.0`, so a quadrant test written as an exact comparison will
fail. If you need both a sine and a cosine of the same angle, note that
calling both costs two independent range reductions; there is no combined
sincos in this module.

<!-- engine text:
Returns the cosine of `X`, where `X` is interpreted as a value in radians, if `IsFinite[X]`.
Returns `NaN` if `not IsFinite[X]`.
-->
## Tan

Takes radians. The poles are not special-cased: `Tan(PiFloat/2.0)` returns a
huge finite value of order 1e16 rather than `Inf`, because the argument is
the nearest double to π/2 rather than π/2 itself — a point the engine's test
suite calls out explicitly. Any code that expects an infinity near a pole
will instead see a large number and keep going.

`±Inf` gives `NaN` and `NaN` propagates. The argument is normalised with
`Value + 0.0` before the call, which folds `-0.0` into `0.0`; that costs
nothing observable under Verse's extensional float equality, but it does keep
the printed result free of a stray minus sign.

<!-- engine text:
Returns the tangent of `X`, where `X` is interpreted as a value in radians, if `IsFinite[X]`.
Returns `NaN` if `not IsFinite[X]`.
-->
## ArcSin

Returns radians in [-π/2, π/2] for arguments in [-1, 1], and is exact at the
three usual points: `-1.0` gives `-π/2`, `0.0` gives `0.0`, `1.0` gives π/2.

Outside that domain the engine deliberately leaves the behaviour
unspecified, and it is worth knowing why. The implementation clamps the
argument into [-1, 1] rather than producing `NaN`, so `ArcSin(2.0)` quietly
returns π/2. Worse, the clamp is written as a pair of `<` tests, both of
which `NaN` fails, so `NaN` clamps to `1.0` and `ArcSin(NaN)` returns π/2 —
`NaN` does not propagate here. The engine's own test file has the
NaN-propagation assertion commented out for exactly this reason. If a bad
input must be visible, range-check it yourself.

<!-- engine text:
Returns the inverse sine (arcsine) of `X` as a value in radians if `-1.0 <= X <= 1.0`.
-->
## ArcCos

Returns radians in [0, π] for arguments in [-1, 1], decreasing rather than
increasing: `-1.0` gives π, `0.0` gives π/2, `1.0` gives `0.0`.

It shares `ArcSin`'s clamping, so the domain is silently enforced instead of
reported: an argument above 1 returns `0.0` and one below -1 returns π. And
because the clamp's comparisons both fail for `NaN`, `ArcCos(NaN)` returns
`0.0` — a perfectly plausible-looking angle produced from a nonsense input.
Validate before calling if that would matter.

<!-- engine text:
Returns the inverse cosine (arccosine) of `X` as a value in radians if `-1.0 <= X <= 1.0`.
-->
## ArcTan(float)

The one inverse trigonometric function here with no domain restriction and no
clamping surprises: every `float` maps into (-π/2, π/2), the infinities map
to exactly `±π/2`, and `NaN` propagates properly.

Because the range spans only half a turn it cannot recover the quadrant of a
direction — `ArcTan(Y/X)` loses the signs of `Y` and `X`, and divides by zero
for a vertical direction into the bargain. Use the two-argument overload for
anything geometric.

<!-- engine text:
Returns the inverse tangent (arctangent) of `X` as a value in radians such that:`-PiFloat/2.0 <= ArcTan(x) <= PiFloat/2.0`.
-->
## ArcTan(float,float)

Note the argument order: `Y` comes first, matching `atan2` rather than
reading order. The result covers the full turn, (-π, π], so this is the form
to use for recovering an angle from a direction.

The origin is special-cased before the library call, so `ArcTan(0.0, 0.0)` is
`0.0` rather than platform-dependent. The test that does this is an equality
against zero, which `-0.0` also satisfies, so `ArcTan(0.0, -0.0)` is `0.0`
where the IEEE rule would give π — worth knowing if you are feeding it the
output of a subtraction.

Infinities are treated as directions rather than errors: the engine's test
suite asserts that for infinite arguments `ArcTan(Y, X)` equals
`ArcTan(Sgn(Y), Sgn(X))`, so `ArcTan(Inf, Inf)` is π/4 and `ArcTan(Inf,
-Inf)` is 3π/4. `NaN` in either argument propagates.

<!-- engine text:
Returns the angle in radians at the origin between a ray pointing to `(X, Y)` and the positive `X` axis such that `-PiFloat < ArcTan(Y, X) <= PiFloat`.
Returns `0.0` if `X=0.0 and Y=0.0`.
-->
## Sinh

Odd and unbounded: `±Inf` maps to `±Inf` and `NaN` propagates, per the
engine's tests. It overflows to `±Inf` for magnitudes beyond roughly 710,
which arrives far sooner than `float`'s exponent range would suggest, because
the result grows as e^X/2.

Near zero `Sinh(X)` is very close to `X`, and unlike a naive
`(Exp(X) - Exp(-X))/2.0` the library implementation does not lose the leading
digits there — prefer this to hand-rolling it.

<!-- engine text:
Returns the hyperbolic sine of `X`.
-->
## Cosh

Even, with a minimum of exactly `1.0` at zero; both infinities give `+Inf`
and `NaN` propagates. It overflows to `+Inf` at around ±710, the same point
as `Sinh`, and there is no argument at which it returns a value below 1, so
`ArCosh(Cosh(X))` is always defined — though it only ever recovers `Abs(X)`.

<!-- engine text:
Returns the hyperbolic cosine of `X`.
-->
## Tanh

A saturating sigmoid: strictly increasing from -1 to 1, with `-Inf` giving
exactly `-1.0`, `Inf` giving exactly `1.0`, and `NaN` propagating. Because
the approach to the asymptotes is exponential it reaches exactly ±1.0 in
double precision at around |X| = 19, long before anything overflows — so
`Tanh` is the safe way to squash an unbounded value into a bounded range,
where `Sinh` and `Cosh` would blow up.

<!-- engine text:
Returns the hyperbolic tangent of `X`.
-->
## ArSinh

The inverse of `Sinh` over the whole real line: no domain restriction, no
failure mode, and no clamping. Infinities map to infinities and `NaN`
propagates — the engine's tests assert `ArSinh(-Inf) = -Inf` and `ArSinh(Inf)
= Inf`, despite a stale source comment claiming otherwise, so the
"if `IsFinite(X)`" hedge in the doc text is more cautious than the
implementation requires.

It grows only logarithmically, which makes it a well-behaved
signed-compression function for values of unknown scale, and unlike a
hand-written `Ln(X + Sqrt(X*X + 1.0))` it stays accurate for large negative
arguments.

<!-- engine text:
Returns the inverse hyperbolic sine of `X` if `IsFinite(X)`.
-->
## ArCosh

The domain is `X >= 1`. Anything below — including `-Inf` — returns `NaN`
rather than failing, and `Inf` returns `Inf`. Since `Cosh` is even this can
only recover the non-negative branch: `ArCosh(Cosh(-2.0))` is `2.0`, not
`-2.0`.

Precision degrades near `X = 1`, where the derivative is infinite, so a value
just above 1 loses significant digits; if your input is naturally expressed
as `1.0 + Small`, that is the case to be careful about.

<!-- engine text:
Returns the inverse hyperbolic cosine of `X` if `1.0 <= X`.
-->
## ArTanh

The domain is the open interval (-1, 1). The endpoints are poles and return
`±Inf`, and any argument with magnitude greater than 1 returns `NaN`. `NaN`
propagates.

The infinities are also mapped to `NaN` today, which is arguably wrong given
that `Tanh(±Inf)` is `±1.0`; the engine's own test file records the question
as unresolved with a TODO, so do not build on the exact behaviour at `±Inf`.
Like `ArCosh`, it loses precision as the argument approaches the pole.

<!-- engine text:
Returns the inverse hyperbolic tangent of `X` if `IsFinite(X)`.
-->
## Pow

Routed straight to the C library's `pow`, and it inherits all of that
function's corner cases — most of which are not what a mathematician would
choose. `Pow(0.0, 0.0)`, `Pow(NaN, 0.0)` and `Pow(1.0, NaN)` all return
`1.0`, so `NaN` does *not* reliably propagate; the engine's tests pin exactly
those three. A negative base with a non-integral exponent gives `NaN`, while
a negative base with an integral exponent works and preserves the sign.

For small integer powers prefer plain multiplication: `A * A` is faster and
exactly the square, where `Pow(A, 2.0)` need not be. For a square root use
`Sqrt`, which is both faster and correctly rounded. Note also that the
argument order here is base then exponent, whereas `Log(B, X)` takes base
then argument — an easy pair to transpose.

<!-- engine text:
Returns `A` to the power of `B`.
-->
## Exp

Raises e to the power of `X`. `Exp(-Inf)` is `0.0`, `Exp(Inf)` is `Inf`, and
`NaN` propagates.

The usable domain is far narrower than `float`'s range: the result overflows
to `+Inf` just above `X = 709.78` and underflows to `0.0` below roughly -745,
so any exponential fed by unbounded gameplay values wants clamping first.

There is no constant for e in this module — a source TODO notes the omission
— so if you need the base itself, `Exp(1.0)` is the idiomatic spelling.

<!-- engine text:
Returns the natural exponent of `X`.
-->
## Ln

The natural logarithm. `Ln(0.0)` is `-Inf`, any negative argument is `NaN`,
`Ln(Inf)` is `Inf`, and `NaN` propagates. The argument is normalised with
`Value + 0.0` first, so `-0.0` and `0.0` both give `-Inf` rather than
diverging — consistent with Verse treating the two as the same value.

The classic trap is precision near 1: `Ln(1.0 + X)` loses significance for
small `X` and there is no `Ln1p` to fall back on, so accumulate in the log
domain if you can.

For other bases use `Log(B, X)`, which is defined as `Ln(X)/Ln(B)` and so
carries a rounding error in the quotient — `Log(2.0, 8.0)` need not be
exactly `3.0`. Round the result if you are using it as an index.

<!-- engine text:
Returns the natural logarithm of `X`.
-->
## result

A tagged union expressed as an interface: two `<decides>` accessors, exactly
one of which succeeds for any given instance. Build values with `MakeSuccess`
and `MakeError`.

The elegant part is the typing. `MakeSuccess` returns `result(success_type,
false)` and `MakeError` returns `result(false, error_type)`, using the
uninhabited type `false` for the side that cannot be present. Subtyping then
carries the knowledge of which case you have to wherever the compiler can see
it, while a function that returns `result(t, e)` erases that knowledge and
forces the caller to test — which is exactly the distinction you want.

It is `<computes>`, so results can be constructed and examined from the
purest contexts, and `internal`, so it appears in signatures such as
`agent_group.AddMember` rather than being something you declare yourself.

<!-- engine text:
Implemented by classes that provide a result for an operation, which can fail or be successful
-->
## result.GetSuccess

Succeeds and yields the payload on a success result, and fails on an error
result — so the natural shape is a query in an `if`, with the error branch
calling `GetError` instead.

Because `MakeError` types the success side as the uninhabited `false`, asking
for the success of something statically known to be an error is usually
caught at compile time: there is no value of the return type to bind. At
runtime the error class's override fails immediately by querying the `false`
literal, so no runtime error is raised and the `Err` call written after it is
unreachable.

<!-- engine text:
Returns the success data of the specified type.
-->
## result.GetError

The mirror image: succeeds only on an error result. Both accessors are
`<computes>`, so the answer is fixed for the lifetime of the value and can be
queried from anywhere, including inside a `<computes>` helper — you can
safely test a result once and pass the extracted payload onward.

The two accessors together are exhaustive but the compiler does not know
that, so a chain of `if` on `GetSuccess[]` and `GetError[]` still needs a
final `else`; there is no `case`-style completeness check for results.

<!-- engine text:
Returns the error data of the specified type.
-->
## showable

A single-member interface whose member is a mutable field rather than a
method. It is intentionally orthogonal to `enableable`: an object may be
enabled but hidden, or shown but inert, and a class can implement either or
both.

<!-- engine text:
Implemented by classes whose instances can change visibility to be shown or hidden.
-->
## showable.Show

A `var` field declared on an interface, so implementing classes must expose
visibility as assignable and callers change it by assignment rather than by
calling `Show()`/`Hide()` methods. Being a field, it is also readable, so the
current state is available without a separate query.

Its type is `logic` rather than `void`, which means `true` shows and `false`
hides — assigning is idempotent, and there is no third "inherit" state.
Nothing in the interface specifies propagation: whether hiding a container
also hides its children is entirely up to the implementation.

<!-- engine text:
Set this value to hide or show the class.
-->
## signalable

The write half of the event triad, with `subscribable` and `awaitable` as the
read halves. Splitting them is what lets an API hand out one direction only:
expose a field typed `listenable(t)` and consumers can wait or subscribe but
cannot signal, while the object that owns the event keeps the `signalable(t)`
view to itself. Reach for this interface when you want to accept "something I
can signal" without committing to `event` as the concrete type.

<!-- engine text:
A parametric interface implemented by events with a `payload` that can be signaled.
Can be used with `awaitable`, `subscribable`, or both (see: `listenable`).
-->
## signalable.Signal

Fans out to both reader mechanisms in a single call, but with strikingly
different ordering guarantees, and the difference matters. Awaiting tasks
resume in the order they suspended, each running until it blocks before the
next is resumed. Subscribed callbacks, in `event`'s implementation, are
invoked in a *randomised* order on every signal, each wrapped in its own
transaction, and skipped entirely if the content scope that registered them
has been torn down — so no subscriber may rely on running before another, or
indeed on running at all.

Note that `Signal` returns before the resumed tasks have finished. They run
only until they block, so control can come back to the signaller with
awaiters still mid-flight, and any state the callbacks touched may be
half-updated from the signaller's point of view.

<!-- engine text:
Concurrently resumes the tasks waiting for this event in `awaitable.Await` and synchronously invokes any callbacks added to this event by `subscribable.Subscribe`.
-->
## Subscribable:subscribable(type)

The callback half of the event triad. `Subscribe` returns a `cancelable`
rather than a handle you look up later, so unsubscribing is a method call on
the returned object and there is no registry to keep in sync.

Two lifetime behaviours make this safer than it looks. Subscriptions are torn
down automatically when the content scope that created them is cleaned up, so
a subscription cannot outlive the code that made it; and a `Subscribe`
performed inside a transaction that later rolls back is undone. You therefore
rarely need to unsubscribe defensively.

Choose subscribing over awaiting when you want to react many times without
tying up a suspended task, and awaiting when the reaction is a step in a
sequential coroutine. `listenable(t)` offers both on one type.

<!-- engine text:
A parametric interface implemented by events with a `payload` that can be subscribed to.
Matched with `signalable.`
-->
## diagnostic

An opaque string wrapper that is deliberately write-only from Verse. The
underlying text field is `epic_internal`, so creator code can build
diagnostics and concatenate them — `+` is overloaded for
`diagnostic`/`diagnostic`, `diagnostic`/`string` and `string`/`diagnostic` —
but cannot read the text back out or compare two of them.

That opacity is the whole design. The format is free to change between
releases, and making it unreadable stops gameplay logic from quietly coming
to depend on it, in the way that code parsing a log message inevitably does.
It implements `diagnosable` trivially by returning itself, so a `diagnostic`
can be passed anywhere a diagnosable value is wanted.

<!-- engine text:
An opaque diagnostic message that only shows up in diagnostic logs. The format of the diagnostic may change at any time without warning and may not be inspected by Verse code.
-->
## ToDiagnostic

Accepts any value at all. For objects whose class implements the internal
`diagnosable` interface it delegates to that class's own `GetDiagnostic` —
which is how containers like `classifiable_subset` come to print their
contents rather than just their address — and everything else goes through
the runtime's generic value printer.

The `<predicts>` effect is the interesting part. Called inside a client
prediction context the function cannot reach server state, so it degrades
rather than failing: numbers, booleans and strings still print, an object
prints its path name, an object the client is not permitted to inspect
becomes `<invalid object>`, an uninitialised value becomes `Uninitialized`,
and anything else becomes `<unavailable on clients>`. A diagnostic that reads
perfectly well on the server can therefore be nearly content-free on a
client, which is worth remembering before relying on one to debug prediction
mismatches.

<!-- engine text:
Converts any Verse value into an opaque diagnostic message.
-->
## Ceil(float)

Rounds towards `+Inf` and then converts to `int`. It fails, recoverably, for
`NaN` and both infinities — but note the second and much less obvious failure
mode: if the rounded value falls outside the 64-bit range the runtime raises
an integer-bounds error that *halts the content scope* rather than failing.
So `Ceil[X]` is not a complete guard against a wild `X`; if the input is
genuinely unbounded, check its magnitude before converting.

Remember that rounding up means towards positive infinity, not away from
zero: `Ceil[-1.5]` is `-1`. That makes `Ceil` agree with `Int` on negative
values and differ from it on positive ones, which is the opposite of `Floor`.

<!-- engine text:
Returns the smallest `int` that is greater than or equal to `Val`.
Fails if `not IsFinite(Val)`.
-->
## Floor(float)

Rounds towards `-Inf`, so `Floor[-1.5]` is `-2`. It fails for `NaN` and the
infinities, and carries the same halting integer-bounds error as `Ceil` when
the result will not fit in 64 bits.

This is the right rounding for anything that has to tile the number line
evenly, because it is the only one of the four whose buckets all have the
same width across zero. It is also the one that matches the module's integer
division: `Quotient` is defined as `Floor[X/Y]` for positive `Y`, so mixing
`Floor` with `Mod` keeps the identity `Quotient*Y + Mod = X` intact where
mixing `Int` with a truncating remainder would not.

<!-- engine text:
Returns the largest `int` that is less than or equal to `Val`.
Fails if `not IsFinite(Val)`.
-->
## Round

Rounds half to even, following IEEE-754's default mode: `0.5` becomes `0`,
`1.5` becomes `2`, `-0.5` becomes `0` and `-1.5` becomes `-2`, all four
pinned by the engine's test suite. This is not the round-half-away-from-zero
that most people expect. It is unbiased over many samples, which is what you
want when accumulating quantities, and mildly astonishing when applied to a
single number a designer is looking at. For half-up behaviour write
`Floor[X + 0.5]`.

The implementation uses `llrint`, which honours the ambient floating-point
rounding mode — nothing in Verse changes that mode, which is where the
"IEEE-754 default" wording in the doc comes from. Fails for `NaN` and the
infinities, and raises the same halting integer-bounds error as `Ceil` for
results outside the 64-bit range.

<!-- engine text:
Returns `Val` rounded to the nearest `int`. When the fractional part of `Val` is `0.5`, rounds to the nearest *even* `int` (per the IEEE-754 default rounding mode).
Fails if `not IsFinite(Val)`.
-->
## Int

Truncates towards zero: `Int[-1.5]` is `-1` and `Int[1.5]` is `1`. It
therefore agrees with `Ceil` on negatives and with `Floor` on positives,
which sounds convenient and is usually a bug.

The asymmetry makes it a poor choice for bucketing signed values, because
both `-0.5` and `0.5` map to `0` and the zero bucket comes out twice as wide
as every other one — reach for `Floor` when the buckets must be uniform.
`Int` is right when you specifically want the integer part with the sign
preserved, as in splitting a value into whole and fractional halves.

Fails for `NaN` and the infinities, with the same halting integer-bounds
error as `Ceil` outside the 64-bit range.

<!-- engine text:
Returns the `int` that equals `Val` without the fractional part.
Fails if `not IsFinite(val)`.
-->
## ToString(float)

Fixed point with exactly six digits after the decimal point, always: never
scientific notation, never fewer digits, never more. Three consequences
follow and all of them bite in practice. It is lossy —
`1.2345678901234567` prints as `1.234568`, and nothing printed this way can
be read back exactly. It can be enormous — `1e100` prints as 101 digits
followed by `.000000`, and the largest finite `float` as 309 digits. And it
collapses everything small — every subnormal prints as `0.000000`.

Special values print as `NaN`, `Inf` and `-Inf`. The sign survives even when
the digits do not, so a tiny negative value prints as `-0.000000`: a value
that compares equal to `0.0` under Verse's extensional float equality yet
prints differently from it.

The runtime does contain a better formatter — shortest round-trippable, with
`.0` appended so that floats stay visually distinct from integers — but this
function is deliberately pinned to the legacy behaviour for compatibility
with published content. If you need a specific number of decimal places or a
round-trippable form, build it yourself.

<!-- engine text:
Makes a `string` representation of `Val`.
-->
## ToString(int)

Plain decimal with a leading `-` for negatives: no thousands separators, no
padding, no explicit `+`, and no format options at all — a source TODO notes
that hexadecimal is still missing. Zero prints as `"0"`.

It is `<computes>`, the only member of the `ToString` family here that is,
which means it can be called from the strictest contexts and is a candidate
for constant folding. The native implementation passes through a 64-bit
integer, so it covers the whole signed 64-bit range; Verse integers are
conceptually unbounded, and the engine's own tests keep the
arbitrary-precision cases commented out precisely because the native
interface assumes 64 bits.

<!-- engine text:
Makes a printable `string` representation of `Val`.
-->
## day_of_week

Seven values in ISO-8601 order, Monday first — not the Sunday-first
convention of C's `tm_wday` or JavaScript's `getDay`. The enum is closed
(there is no `<open>`), so a `case` covering all seven names is exhaustive
and needs no wildcard branch.

The ordering is not arbitrary: the engine's calendar is anchored so that
tick zero of a `date_time` — midnight on 1 January 0001 — is a Monday.
That is why `GetDayOfWeek` needs no calendar lookup at all; it divides the
tick count by the ticks in a day and takes the remainder modulo seven.

<!-- engine text:
Enumerates the days of the week in 7-day calendars.
-->
## day_of_week.Monday

<!-- no documentation in the engine source -->
## day_of_week.Tuesday

<!-- no documentation in the engine source -->
## day_of_week.Wednesday

<!-- no documentation in the engine source -->
## day_of_week.Thursday

<!-- no documentation in the engine source -->
## day_of_week.Friday

<!-- no documentation in the engine source -->
## day_of_week.Saturday

<!-- no documentation in the engine source -->
## day_of_week.Sunday

<!-- no documentation in the engine source -->
## month_of_year

Twelve closed values, so `case` over all of them is exhaustive. This is
the enum counterpart of `GetMonth`, which returns a plain `int` from 1 to
12; prefer `GetMonthOfYear` and this type when you are branching, since
only the enum gets exhaustiveness checking from the compiler.

Month lengths are available separately through `DaysInMonth`, which takes
a year as well because February varies. Nothing here is localised — these
are Gregorian month identities, not display names.

<!-- engine text:
Enumerates the months of the year in 12-month calendars.
-->
## month_of_year.January

<!-- no documentation in the engine source -->
## month_of_year.February

<!-- no documentation in the engine source -->
## month_of_year.March

<!-- no documentation in the engine source -->
## month_of_year.April

<!-- no documentation in the engine source -->
## month_of_year.May

<!-- no documentation in the engine source -->
## month_of_year.June

<!-- no documentation in the engine source -->
## month_of_year.July

<!-- no documentation in the engine source -->
## month_of_year.August

<!-- no documentation in the engine source -->
## month_of_year.September

<!-- no documentation in the engine source -->
## month_of_year.October

<!-- no documentation in the engine source -->
## month_of_year.November

<!-- no documentation in the engine source -->
## month_of_year.December

<!-- no documentation in the engine source -->
## DaysInMonth

Returns 28, 29, 30 or 31, taking the year into account so that February
answers correctly under the proleptic Gregorian leap rule. The year is not
otherwise range-checked: ask about year 0 or year 50000 and you still get
a plausible number, even though no `date_time` could hold such a date.

The month, by contrast, must be 1 to 12. This function neither fails nor
clamps — an out-of-range month is treated as a programming error and trips
an engine assertion in a development build rather than being reported back
to Verse. Validate the month yourself first, or let `ValidateDateTime`
check the whole date at once.

<!-- engine text:
Return the number of days in the specified month of the specified year
-->
## DaysInYear

Returns 366 for a leap year and 365 otherwise, using the proleptic
Gregorian rule: divisible by four, except centuries, except centuries
divisible by 400. Comparing the result with 366 is the module's only leap
year test.

Like `DaysInMonth` it does no range checking and cannot fail, so it will
happily answer for years outside the 1 to 9999 window that `date_time`
itself supports.

<!-- engine text:
Return the number of days in the specified year
-->
## ToString(date_time)

Produces a fixed-width 19-character string such as `2026.09.14-08.30.00`.
The year is zero-padded to four digits, so `DateTimeMin` renders as
`0001.01.01-00.00.00`. Note that the separators are dots throughout, with
a hyphen between the date and the time.

Everything finer than a second is discarded, so this is lossy: a value and
the same value plus 999 milliseconds print identically, and the string
cannot be turned back into the original tick count. Keep the `Ticks` field
if you need round-tripping. No offset or zone designator is emitted and no
conversion is performed — the digits are simply the value's fields, which
by the module's convention are UTC.

<!-- engine text:
Returns a string representation of the datetime in the following format: yyyy.mm.dd-hh.mm.ss. Assumes Datetime is in UTC.
-->
## UtcNow

Always UTC. There is no local-time counterpart in this module and a
`date_time` stores no offset, so any presentation in a player's local time
is on you. The natural companion is subtraction: `UtcNow() - Start` yields
a `time_span`.

Do not read the tick resolution as the clock's resolution. The underlying
platform clock delivers whole milliseconds, so the bottom four digits of
the tick count are normally zero, and on some platforms the value is
estimated from a cached base time advanced by a high-frequency counter and
rebased periodically. Differences below a millisecond are noise, and this
is a wall clock rather than a monotonic one.

<!-- engine text:
Returns the current UTC date_time.
-->
## date_parts

The calendar fields of a `date_time` — year, month and day — pulled apart so
they can be read individually.

<!-- no documentation in the engine source -->
## time_of_day_parts

Bundles the six sub-day components of a `date_time`, and is what
`GetTimeOfDay` fills in. In practice you cannot use it from project code:
although the type name is `<public>`, the struct itself is `<internal>`
and its fields carry no access specifier — which defaults to `internal`
too — so outside the module you can neither construct one nor read a
component out of one. Call `GetHours`, `GetMinutes`, `GetSeconds`,
`GetMilliseconds`, `GetMicroseconds` and `GetNanoseconds` on the
`date_time` directly instead.

Where it is visible, the fields hold `Hours` 0-23, `Minutes` and `Seconds`
0-59, and then three overlapping views of the same fractional second:
`Milliseconds` 0-999, `Microseconds` 0-999999 and `Nanoseconds` up to
999999900. They are alternative resolutions, not successive refinements,
so summing them would triple-count. The engine's own note on this struct
is an open ticket, so treat its shape as provisional.

<!-- engine text:
TODO: Create a time_space struct and related time_span methods - FORT-416561
-->
## GetDate

Splits the calendar part of an instant into year, month and day in one call,
which is cheaper and reads better than three separate accessors when you want
all three.

<!-- no documentation in the engine source -->
## GetTimeOfDay

Splits the time-of-day part of an instant into hours through nanoseconds, for
when you want the clock face rather than the date.

<!-- no documentation in the engine source -->
## GetYear

The year of `Val`.

<!-- no documentation in the engine source -->
## GetMonth

The month of `Val`, `1` for January through `12` for December.

<!-- no documentation in the engine source -->
## GetDay

The day of the month of `Val`, counting from `1`.

<!-- no documentation in the engine source -->
## GetHours(date_time)

The hour of `Val` on a 24-hour clock, `0` through `23`.

<!-- no documentation in the engine source -->
## GetMinutes(date_time)

The minute of `Val`, `0` through `59`.

<!-- no documentation in the engine source -->
## GetSeconds(date_time)

The second of `Val`, `0` through `59`.

<!-- no documentation in the engine source -->
## GetMilliseconds(date_time)

The millisecond within the second of `Val`, `0` through `999`.

<!-- no documentation in the engine source -->
## GetMicroseconds(date_time)

The microsecond within the second of `Val`.

<!-- no documentation in the engine source -->
## GetNanoseconds(date_time)

The nanosecond within the second of `Val`. A tick is 100 nanoseconds, so this is
always a multiple of 100 — the finest resolution a `date_time` can express.

<!-- no documentation in the engine source -->
## GetDayOfWeek

Total and cheap — a division of the tick count by the ticks per day and a
remainder modulo seven, with no calendar arithmetic, because tick zero
falls on a Monday. It cannot fail.

The answer describes the value's UTC date. Two `date_time` values a few
hours apart can land on different weekdays here while being the same local
day for a player, and vice versa.

<!-- no documentation in the engine source -->
## GetMonthOfYear

The enum form of the month, where `GetMonth` gives the same information as
an `int` from 1 to 12. Reach for this one when branching: `case` over the
twelve `month_of_year` values is checked for exhaustiveness, whereas a
chain of integer comparisons is not.

Like the other accessors it reads the value's UTC date fields and cannot
fail.

<!-- no documentation in the engine source -->
## time_span

A signed duration, stored as a count of 100-nanosecond ticks — a length of
time, not a point on the calendar. Where `date_time` is bounded by the
years 1 to 9999, a `time_span` has no valid range beyond its 64-bit tick
field (the source explicitly notes that there is no `ValidateTimeSpan`
because there is nothing to validate), which works out to roughly plus or
minus 29,000 years. Negative spans are ordinary and are exactly what
subtracting a later `date_time` from an earlier one gives you.

The type carries a full set of operators: `+` and `-` between spans, unary
negation, `*` and `/` by a `float`, and the comparisons `Less`, `Greater`,
`LessEqual` and `GreaterEqual`. Mixed arithmetic connects the two types —
`date_time - date_time` produces a `time_span`, while `date_time +
time_span` and `date_time - time_span` produce a `date_time`.

Two edges are worth knowing. Scaling by a `float` rounds halves away from
zero, and if the product leaves 64-bit range it raises an overflow runtime
error and yields zero rather than saturating. Dividing by zero raises a
division-by-zero runtime error and then saturates to the maximum tick
count with the sign of the numerator.

<!-- no documentation in the engine source -->
## time_span.Ticks

The entire state of a `time_span`: one tick is 100 nanoseconds, so there
are 10,000,000 to the second and 864,000,000,000 to the day. It is signed,
and unlike the fields of `date_parts` it is `<public>`, so you can both
read it and build a span with an archetype:
`time_span{Ticks := 5 * 10000000}` is five seconds.

That matters because `CreateTimeSpan` bottoms out at whole milliseconds —
setting `Ticks` directly is the only way to express a microsecond or a
single tick. It is also the exact route for comparing or scaling spans,
sidestepping the floating-point rounding that `*` and `/` go through.

<!-- no documentation in the engine source -->
## CreateTimeSpan

Cannot fail. The five components are simply scaled and summed, so they
need not be in their "natural" ranges: 90 minutes is accepted and equals
one hour thirty, and any component may be negative, so mixed signs cancel
against each other.

Resolution stops at the millisecond. Internally `Milliseconds` is
converted to nanoseconds and then divided down to ticks, so there is no
argument here that can name a microsecond — build the span from `Ticks`
for that. The arguments are Verse `int`s but are narrowed to 32-bit on the
way into the engine, and `Milliseconds` is scaled by a million before that
narrowing happens, so keep it inside roughly plus or minus two thousand
and the remaining components inside 32-bit range; larger magnitudes wrap
silently, and an absurd total trips an engine assertion in a development
build.

<!-- no documentation in the engine source -->
## ToString(time_span)

The format is not the one the engine's own comment claims. A span renders
as a sign followed by `hh:mm:ss.fff`, or `d.hh:mm:ss.fff` when the day
component is non-zero — colons inside the time, a dot before the
fractional seconds, and the day count unpadded. Ninety seconds gives
`+00:01:30.000`; a negative day and two hours gives `-1.02:00:00.000`.

The sign is always present, `+` or `-`, and is factored out front: each
component is printed as an absolute value, so a negative span shows no
internal minus signs. Output is truncated at the millisecond, so
sub-millisecond ticks are invisible and this is not a round-trippable
representation.

<!-- engine text:
Returns a string representation of the time span in the following format: yyyy.mm.dd-hh.mm.ss.
-->
## GetDays

The whole days in the span, truncated toward zero, and negative for a
negative span. Because days is the coarsest component there is nothing
larger to reduce it against, so this returns the same value as
`GetTotalDays` — the two differ only in that `GetTotalDays` routes through
a floating-point intermediate. Every other `Get`/`GetTotal` pair in the
type does diverge.

<!-- no documentation in the engine source -->
## GetHours(time_span)

The hours component within the day, so 0 to 23 in magnitude, not the total
number of hours: a 50-hour span reports 2 here and 50 from
`GetTotalHours`. The remainder follows the sign of the span, so a negative
span yields values from 0 down to -23.

<!-- no documentation in the engine source -->
## GetMinutes(time_span)

The minutes component within the hour, 0 to 59 in magnitude, and signed
with the span. A span of 90 minutes reports 30; ask `GetTotalMinutes` if
you wanted 90.

<!-- no documentation in the engine source -->
## GetSeconds(time_span)

The seconds component within the minute, 0 to 59 in magnitude and signed
with the span. Anything below a second is left to the fractional
accessors; use `GetTotalSeconds` for the span as a whole.

<!-- no documentation in the engine source -->
## GetMilliseconds(time_span)

The fractional second at millisecond resolution: 0 to 999 in magnitude,
signed with the span. It is neither a total nor a leftover — it is the
sub-second remainder rounded down to whole milliseconds, which is the same
fraction that `GetMicroseconds` and `GetNanoseconds` report at finer
scales.

<!-- no documentation in the engine source -->
## GetMicroseconds(time_span)

Easy to misread. This is the whole fractional second expressed in
microseconds, 0 to 999999 in magnitude — not the microseconds left over
after `GetMilliseconds`. For a span of 1.5 seconds, `GetMilliseconds`
returns 500 and this returns 500000: they overlap rather than nest, so
adding them together double-counts the same half second.

<!-- no documentation in the engine source -->
## GetNanoseconds(time_span)

The same fractional second again, now in nanoseconds, up to 999999900 in
magnitude and signed with the span. It overlaps `GetMilliseconds` and
`GetMicroseconds` rather than extending them.

The resolution on offer is illusory: a tick is 100 nanoseconds, so this
value is always an exact multiple of 100 and its last two digits are
invariably zero. There is no way for a `time_span` to hold a finer
distinction.

<!-- no documentation in the engine source -->
## GetTotalDays

The entire span expressed in days, truncated toward zero — so 36 hours
gives 1, and -36 hours gives -1 rather than -2. It is computed as a
floating-point division and then truncated to an `int`, which means the
fractional day is silently dropped; there is no rounding.

Since days is the largest component, this agrees with `GetDays` for every
span. The distinction between the two only becomes meaningful further down
the scale.

<!-- no documentation in the engine source -->
## GetTotalHours

The entire span in hours, truncated toward zero: 90 minutes gives 1, -90
minutes gives -1. Contrast `GetHours`, which reports only the hours
component within the day and so never exceeds 23 in magnitude.

<!-- no documentation in the engine source -->
## GetTotalMinutes

The entire span in minutes, truncated toward zero, so 90 seconds gives 1
and any remainder is discarded. `GetMinutes` gives the 0-59 component
instead.

<!-- no documentation in the engine source -->
## GetTotalSeconds

The entire span in seconds, truncated toward zero — the usual choice when
you want a duration as a single number. Sub-second content is dropped
without rounding, so a span of 999 milliseconds reports 0. Every value in
the type's range converts exactly.

<!-- no documentation in the engine source -->
## GetTotalMilliseconds

The entire span in whole milliseconds, truncated toward zero; ticks below
a millisecond are dropped. This is exact across the full range of
`time_span`, because even a maximal span is comfortably within the
integers a `double` can represent without loss.

<!-- no documentation in the engine source -->
## GetTotalMicroseconds

The finest total available — there is no `GetTotalNanoseconds`, so for
anything below this multiply the `Ticks` field by 100 yourself. Truncated
toward zero, discarding the sub-microsecond remainder, which is at most 99
nanoseconds since a tick is 100.

This is also the one total where the floating-point intermediate bites.
The division is performed as a `double` before being truncated to an
`int`, and a `double` holds integers exactly only up to about 9e15
microseconds — roughly 285 years of span. Beyond that the low-order digits
are rounded, so very long spans lose microsecond fidelity here even though
`Ticks` still holds it precisely.

<!-- no documentation in the engine source -->
