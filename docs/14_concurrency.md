# Concurrency

Concurrency is a fundamental aspect of Verse, allowing you to control
time flow as naturally as you control program flow. Unlike traditional
programming languages that bolt on concurrency as an afterthought,
Verse integrates time flow control directly into the language through
dedicated expressions and effects.

Game development inherently requires managing multiple simultaneous
activities. Think about a typical game scene: NPCs patrol their routes
while particle effects play, UI elements animate as cooldown timers
count down, and background music fades between tracks. All these
activities happen concurrently, overlapping in time. Verse recognizes
this reality and provides first-class language constructs to express
these parallel behaviors naturally.

The language achieves this through a combination of structured and
unstructured concurrency primitives, all built on the concept of async
expressions that can suspend and resume across multiple simulation
updates. This approach makes concurrent programming feel as natural as
writing sequential code, while avoiding the traditional pitfalls of
thread-based concurrency like data races and deadlocks.

## Core Concepts

### Immediate vs Async Expressions

Every expression falls into one of two categories: immediate or
async. Understanding this distinction is crucial for working with
Verse's concurrency model.

Immediate expressions evaluate with no delay, completing entirely
within the current simulation update or frame. These include most
basic operations you'd expect to happen instantly: arithmetic
calculations, variable access, simple function calls, and data
structure manipulation. When you write `X := 5 + 3`, the addition
happens immediately, the assignment completes instantly, and execution
moves to the next statement without any possibility of interruption.

Async expressions, on the other hand, have the possibility of taking
time to evaluate, potentially spanning multiple simulation
updates. They represent operations that inherently take time in the
game world: animations playing out, timers counting down, network
requests completing, or simply waiting for the next frame. An async
expression might complete immediately if its conditions are already
met, or it might suspend execution, allowing other code to run while
it waits for the right moment to resume.

### Simulation Updates

A simulation update represents one tick of the game's simulation,
typically corresponding to a frame being rendered. Most games target
30 or 60 updates per second, creating the smooth motion players
expect. Each update processes input, updates game logic, runs physics
simulations, and prepares the next frame for rendering.

In networked games, the relationship between simulation updates and
rendering becomes more complex. Multiple simulation updates might
occur before rendering to maintain synchronization with the server, or
updates might be interpolated to smooth out network latency. Verse's
concurrency model abstracts these complexities, allowing you to think
in terms of logical time flow rather than platform-specific timing
details.

Async expressions naturally align with this update cycle. When an
async expression suspends, it yields control back to the game engine,
which continues processing other tasks and rendering frames. The
suspended expression resumes in a future update when its conditions
are met, seamlessly continuing from where it left off. This
cooperative model ensures that long-running operations don't block the
game's responsiveness.

### The `suspends` Effect

Concurrent operations require the `<suspends>` effect specifier (see
[Effects](13_effects.md)). Functions marked with `<suspends>` can use
concurrency expressions, call other suspending functions, and
cooperatively yield execution:

<!--versetest
MyAsyncFunction()<suspends>:void =
    Sleep(1.0)
    Print("One second later!")

MyImmediateFunction():void =
    Print("This happens immediately")
<#
-->
<!-- 01 -->
```verse
# Function marked with suspends can use async expressions
MyAsyncFunction()<suspends>:void =
    Sleep(1.0)  # Pause execution
    Print("One second later!")

# Regular functions cannot use async expressions
MyImmediateFunction():void =
    # Sleep(1.0)  # ERROR: Cannot use Sleep without suspends
    Print("This happens immediately")
```
<!-- #> -->

The `<suspends>` effect propagates through the call chain—any function
calling a suspending function must itself be marked `<suspends>`.

## Structured Concurrency

Structured concurrency represents one of Verse's most elegant design
decisions. Rather than spawning threads or tasks that live
independently and require manual lifecycle management, structured
concurrency expressions have lifespans naturally bound to their
enclosing scope. When you enter a structured concurrency block, you
know that all concurrent operations within it will be properly managed
and cleaned up when the block exits, preventing resource leaks and
making code easier to reason about.

This approach mirrors how we think about sequential code. Just as a
block of sequential statements has a clear beginning and end,
structured concurrent operations have a defined lifetime. You can nest
them, compose them, and reason about them using the same mental model
you use for regular code blocks.

### Effect Requirements

All structured concurrency expressions (`sync`, `race`, `rush`, and
`branch`) require the `<suspends>` effect. You cannot use these
constructs in immediate (non-suspending) functions:

<!--versetest
Operation1<public>()<suspends>:void = {}
Operation2<public>()<suspends>:void = {}
-->
<!-- 02 -->
```verse
# Valid: structured concurrency in suspends function
ProcessConcurrently()<suspends>:void =
    sync:
        Operation1()
        Operation2()

# Invalid: cannot use sync without suspends
# ProcessImmediate():void =
#     sync:  # ERROR: sync requires suspends
#         Operation1()
```

### The sync Expression

The `sync` expression embodies the simplest concurrent pattern: doing
multiple things at once and waiting for all of them to finish. When
you have independent operations that can benefit from parallel
execution, `sync` provides a clean way to express this parallelism
while maintaining deterministic behavior.

<!--versetest
AsyncOperation1()<suspends>:int=1
AsyncOperation2()<suspends>:int=1
AsyncOperation3()<suspends>:int=1
F()<suspends>:void={
Results := sync:
    AsyncOperation1()
    AsyncOperation2()
    AsyncOperation3()
Print("All operations complete with results: {Results(0)} {Results(1)} {Results(2)}")
}
<#
-->
<!-- 04 -->
```verse
# All expressions start simultaneously and must all complete
Results := sync:
    AsyncOperation1()  # Returns value1
    AsyncOperation2()  # Returns value2
    AsyncOperation3()  # Returns value3

Print("All operations complete with results: {Results(0)} {Results(1)} {Results(2)}")
```
<!-- #> -->

Inside a `sync` block, all subexpressions begin execution at
essentially the same moment. The sync expression then waits patiently
for every single subexpression to complete, regardless of how long
each takes individually. If one operation finishes in milliseconds
while another takes several seconds, sync continues waiting until that
last operation completes. Only then does execution continue past the
sync block.

The beauty of sync lies in its predictability. You always get results
from all subexpressions, always in the same order you wrote them,
packaged neatly in a tuple. This makes sync perfect for scenarios
where you need multiple pieces of data or need to ensure multiple
systems are ready before proceeding. Loading game assets in parallel,
initializing multiple subsystems simultaneously, or gathering data
from multiple sources all benefit from sync's all-or-nothing approach.

Consider a more sophisticated example that demonstrates sync's composability:

<!--versetest
LoadTexture()<suspends>:void={}
ApplyTexture()<suspends>:void={}
LoadSound()<suspends>:void={}
PlaySound()<suspends>:void={}
LoadModel():void={}
ProcessData(:int,:int,:int):void={}
FetchDataA()<suspends>:int=1
FetchDataB()<suspends>:int=1
FetchDataC():int=1
F()<suspends>:void={
sync:
    block:  # Task 1 - sequential operations
        LoadTexture()
        ApplyTexture()
    block:  # Task 2 - parallel to task 1
        LoadSound()
        PlaySound()
    LoadModel()  # Task 3 - parallel to tasks 1 and 2
ProcessData(sync:
    FetchDataA()
    FetchDataB()
    FetchDataC()
)
}
<#
-->
<!-- 05 -->
```verse
# Nested blocks for complex operations
sync:
    block:  # Task 1 - sequential operations
        LoadTexture()
        ApplyTexture()
    block:  # Task 2 - parallel to task 1
        LoadSound()
        PlaySound()
    LoadModel()  # Task 3 - parallel to tasks 1 and 2

# Using sync results directly as function arguments
ProcessData(sync:
    FetchDataA()
    FetchDataB()
    FetchDataC()
)
```
<!--versetest
#>
-->

### The race Expression

Where `sync` embodies cooperation, `race` represents competition. The
race expression starts multiple async operations simultaneously, but
only cares about the first one to cross the finish line. As soon as
one subexpression completes, race immediately cancels all the others
and continues with the winner's result. This winner-takes-all
semantics makes race perfect for timeout patterns, fallback
mechanisms, and any situation where you want the fastest possible
response.

<!--versetest
SlowOperation()<suspends>:int=0
FastOperation()<suspends>   :int=0
MediumOperation()<suspends>   :int=0
F()<suspends>:void={
Winner := race:
    SlowOperation()
    FastOperation()
    MediumOperation()

Print("Winner result: {Winner}")
}
<#
-->
<!-- 06 -->
```verse
# First to complete wins, others are canceled
Winner := race:
    SlowOperation()     # Takes 5 seconds
    FastOperation()     # Takes 1 second - wins!
    MediumOperation()   # Takes 3 seconds

Print("Winner result: {Winner}")  # Prints FastOperation's result
```
<!-- #> -->

The power of race becomes apparent when you consider real game
scenarios. Imagine querying multiple servers for data, where you want
to use whichever responds first. Or implementing a player action with
a timeout, where either the player completes the action or time runs
out. Race elegantly expresses these patterns without complex state
management or manual cancellation logic.

Cancellation in race is immediate and thorough. The moment a winner
emerges, all losing subexpressions receive a cancellation signal and
begin cleanup. This isn't just an optimization; it's crucial for
resource management and preventing unwanted side effects from
operations that are no longer needed.

**Type handling in race:**

The type system handles race elegantly. Since only one subexpression's
result will be returned, the result type of a race is the most
specific common supertype of all the subexpressions. This ensures type
safety while maintaining flexibility in what kinds of operations you
can race against each other:

<!--versetest
base_class := class:
    Value:int

derived_a := class(base_class):
    Name:string = "A"

derived_b := class(base_class):
    Name:string = "B"

GetA()<suspends>:derived_a = derived_a{Value := 1}
GetB()<suspends>:derived_b = derived_b{Value := 2}

F()<suspends>:void={
Result:base_class = race:
    GetA()
    GetB()
SameTypeResult:int = race:
    block:
        Sleep(1.0)
        42
    block:
        Sleep(2.0)
        100
}
<#
-->
<!-- 07 -->
```verse
base_class := class:
    Value:int

derived_a := class(base_class):
    Name:string = "A"

derived_b := class(base_class):
    Name:string = "B"

GetA()<suspends>:derived_a = derived_a{Value := 1}
GetB()<suspends>:derived_b = derived_b{Value := 2}

# Result type is base_class (common supertype)
Result:base_class = race:
    GetA()  # Returns derived_a
    GetB()  # Returns derived_b
# Result is base_class, can hold either derived type

# If all expressions return the same type, that's the result type
SameTypeResult:int = race:
    block:
        Sleep(1.0)
        42
    block:
        Sleep(2.0)
        100
# Result type is int
```
<!-- #> -->

A pattern involves adding identifiers to determine which subexpression won:

<!--versetest
SlowOperation()<suspends>:int=0
FastOperation()  <suspends> :int=0
InfiniteOperation()  <suspends> :int=0
F()<suspends>:void={
WinnerID := race:
    block:
        SlowOperation()
        1
    block:
        FastOperation()
        2
    block:
        loop:
            InfiniteOperation()
        3

case(WinnerID):
    1 => Print("Slow operation won somehow!")
    2 => Print("Fast operation won as expected")
    _ => Print("Impossible!")
}
<#
-->
<!-- 08 -->
```verse
# Adding identifiers to determine which expression won
WinnerID := race:
    block:
        SlowOperation()
        1  # Return 1 if this wins
    block:
        FastOperation()
        2  # Return 2 if this wins
    block:
        loop:
            InfiniteOperation()
        3  # Never returns

case(WinnerID):
    1 => Print("Slow operation won somehow!")
    2 => Print("Fast operation won as expected")
    _ => Print("Impossible!")
```
<!-- #> -->

### The rush Expression

The `rush` expression occupies a unique middle ground between `sync`
and `race`. Like race, it completes as soon as the first subexpression
finishes. Unlike race, it doesn't cancel the losers. This creates an
interesting pattern where you can start multiple operations, proceed
as soon as one provides a result, while allowing the others to
continue their work in the background.

<!--versetest
LongBackgroundTask()<suspends>:int=0
QuickCheck() <suspends>  :int=0
MediumTask() <suspends>  :int=0
F()<suspends>:void={
FirstResult := rush:
    LongBackgroundTask()
    QuickCheck()
    MediumTask()

Print("First result: {FirstResult}")
}
<#
-->
<!-- 09 -->
```verse
# First to complete allows continuation, others keep running
FirstResult := rush:
    LongBackgroundTask()   # Continues after rush completes
    QuickCheck()          # Finishes first
    MediumTask()          # Also continues after rush

Print("First result: {FirstResult}")
# LongBackgroundTask and MediumTask are still running!
```
<!-- #> -->

Rush shines in scenarios where you want to be responsive while still
completing all operations eventually. Consider preloading game assets:
you might start loading multiple levels simultaneously, begin gameplay
as soon as the current level loads, while continuing to cache the
other levels in the background. Or think about achievement checking,
where you want to notify the player as soon as one achievement unlocks
while continuing to check for others.

The non-canceling nature of rush requires careful consideration. Those
background tasks continue consuming resources and performing their
operations even after rush completes. They'll keep running until they
naturally complete or until their enclosing async context ends. This
makes rush powerful but also potentially dangerous if misused with
operations that might never complete or that consume significant
resources.

There's an important technical restriction to be aware of: rush cannot
be used directly in the body of iteration expressions like `loop` or
`for`. The interaction between rush's background tasks and iteration
could lead to resource accumulation. If you need rush-like behavior in
a loop, wrap it in an async function and call that function from your
iteration.

### The branch Expression

The `branch` expression represents fire-and-forget concurrency within
a structured context. When you encounter a branch, it immediately
starts executing its body as a background task and then, without any
pause or hesitation, continues with the next expression. There's no
waiting, no result collection, just a task spinning off to do its work
while the main flow proceeds unimpeded.

<!--versetest
AsyncOperation1()<computes><suspends>:int=0
ImmediateOperation()<computes> :int=0
AsyncOperation2() <suspends><computes>  :int=0
F()<suspends>:void={
branch:
    AsyncOperation1()
    ImmediateOperation()
    AsyncOperation2()
}
<#
-->
<!-- 10 -->
```verse
branch:
    # This block runs independently
    AsyncOperation1()
    ImmediateOperation()
    AsyncOperation2()

# Execution continues immediately here
Print("Branch started, continuing main flow")
# Branch block is still running in background
```
<!-- #> -->


Branch excels at handling side effects that shouldn't interrupt the
main game flow. Think about logging player actions to analytics,
triggering particle effects that play out over time, or starting
background music that fades in gradually. These operations need to
happen, but there's no reason to make the player wait for them to
complete. Branch lets you express this "start it and move on" pattern
directly.

The relationship between a branch and its enclosing scope maintains
the structured concurrency guarantee. While the branch task runs
independently, it's still tied to the lifetime of its parent async
context. If that parent context completes, either naturally or through
cancellation, the branch task is automatically canceled too. This
prevents orphaned tasks from accumulating and consuming resources
indefinitely.

Like rush, branch faces restrictions with iteration expressions. You
cannot use branch directly inside a loop or for body, as this could
lead to an unbounded number of background tasks. The workaround
remains the same: encapsulate the branch in an async function and call
that function from your iteration.

## Unstructured Concurrency

### The spawn Expression

While structured concurrency handles most concurrent programming needs
elegantly, sometimes you need to break free from the hierarchical task
structure. The `spawn` expression is Verse's single concession to
unstructured concurrency, allowing you to start an async operation
that lives independently of its creating scope. Think of spawn as an
emergency escape hatch—powerful when needed, but not your first choice
for typical concurrent patterns.

<!--versetest
LongRunningTask()  <suspends> :int=0
-->
<!-- 11 -->
```verse
# spawn returns a task(t) object you can control
BackgroundTask:task(int) = spawn{LongRunningTask()}

# Or fire-and-forget without capturing the task
spawn{LongRunningTask()}
Print("Spawned task continues even after this scope exits")
```

What makes spawn unique is its ability to work anywhere. Unlike all
the structured concurrency expressions that require an async context,
spawn works in immediate functions, class constructors, module
initialization—anywhere you can write code. This universality comes
with responsibility. The task you spawn becomes a free agent,
continuing its work regardless of what happens to the code that
created it. There's no automatic cleanup, no parent-child
relationship, just an independent task pursuing its goal.

The spawned function must have the `<suspends>` effect. You **cannot**
spawn functions with the `<decides>` effect:

<!--versetest-->
<!-- 12 -->
```verse
AsyncWork()<suspends>:void =
    Sleep(1.0)
    Print("Background work complete")

FailableWork()<decides>:void =
    false?  # Might fail

# Valid: spawning suspends function
spawn{AsyncWork()}

# Invalid: cannot spawn decides function
# spawn{FailableWork()}  # ERROR: spawn requires suspends, not decides
```

This restriction exists because spawned tasks run independently
without a parent to handle their failure. Since `<suspends>` and
`<decides>` cannot be combined on the same function, and spawn needs
`<suspends>`, functions with `<decides>` cannot be spawned. If you
need to spawn failable work, wrap it in a suspends function that
handles the failure internally:

<!--versetest
FailableWork<public>()<computes><decides>:void = {}
-->
<!-- 13 -->
```verse
SafeFailableWork()<suspends>:void =
    if (FailableWork[]):
        Print("Work succeeded")
    else:
        Print("Work failed, but handled gracefully")

spawn{SafeFailableWork()}  # Valid - failure handled inside
```

The syntax deliberately constrains spawn to launching a single
function call. You can't spawn a block of code with multiple
operations; you're limited to spawning one async function. This
constraint encourages you to think carefully about what you're
spawning and encapsulate complex operations properly in functions
rather than creating ad-hoc background tasks.

Spawn finds its place in specific architectural patterns. Global
background services that monitor game state throughout the entire
session, cleanup tasks that must complete even if the triggering
context ends, or integration points where immediate code needs to
trigger async operations—these scenarios justify reaching for spawn
over the structured alternatives.

The contrast with branch illuminates the design philosophy. Branch
gives you structured concurrency's safety within an async context,
allowing multiple expressions in its body while maintaining
parent-child relationships. Spawn trades these safeguards for the
flexibility to work anywhere, but restricts you to a single function
call. Each has its place, and choosing between them depends on whether
you need structure or freedom.

**Working with spawned tasks:**

The `spawn` expression returns a `task(t)` object where `t` is the
return type of the spawned function. This task object provides methods
to control and query the spawned operation—you can cancel it, wait for
it to complete, or check its current state. While spawn creates
independent tasks that don't require management, having access to the
task object gives you the power to intervene when needed. See the "The
task(t) Type" section below for complete details on task objects and
their capabilities.

## The task(t) Type

The `task(t)` type represents a handle to an executing async
operation, where `t` is the return type of the operation. While Verse
creates tasks automatically behind the scenes for all async
expressions, only `spawn` gives you direct access to a task object
that you can control and query.

<!--versetest-->
<!-- 14 -->
```verse
# spawn returns task(t) where t is the return type
BackgroundWork()<suspends>:int =
    Sleep(2.0)
    42

MyTask:task(int) = spawn{BackgroundWork()}
# MyTask is a handle to the spawned operation
```

Task objects provide a rich interface for managing async operations:
you can cancel them, wait for their completion, and query their
current state. This control is essential for implementing robust
concurrent systems where you need to coordinate multiple independent
operations.


A task moves through several distinct states during its lifetime:

**Active**: The task is currently running or suspended, but has not
yet finished. It's still doing work or waiting to resume.

**Completed**: The task finished successfully and returned a
result. Once completed, a task never changes state again. (Terminal state)

**Canceled**: The task was canceled before it could complete. This is
a terminal state — canceled tasks cannot resume.

**Settled**: A task is settled if it has reached either the Completed
or Canceled state. Settled tasks are no longer executing. (Terminal state)

**Uninterrupted**: A task is uninterrupted if it completed
successfully without being canceled. This is equivalent to the
Completed state. (alias)

**Interrupted**: A task is interrupted if it was canceled. This is
equivalent to the Canceled state. (alias)

### Task.Cancel()

!!! note "Unreleased Feature"
    The Cancel() method has not be released at this time.
	
The `Cancel()` method requests cancellation of a task. This is a safe
operation that can be called on any task in any state:

<!--versetest
BackgroundWork()<transacts><suspends>:void={Sleep(1.0)}
F()<suspends>:void= {
LongTask:task(void) = spawn{BackgroundWork()}
LongTask.Cancel()
LongTask.Cancel()
}
<#
-->
<!-- 16 -->
```verse
LongTask:task(void) = spawn{BackgroundWork()}

# Request cancellation
LongTask.Cancel()

# Safe to call multiple times
LongTask.Cancel()  # No error

# Safe to call on completed tasks (has no effect)
```
<!-- #> -->

Cancellation is cooperative—the task doesn't stop
immediately. Instead, it receives a cancellation signal that is
checked at the next suspension point. The task then unwinds
gracefully, allowing cleanup code to run. See "Suspension Points and
Cancellation" below for details on when cancellation takes effect.

Calling `Cancel()` on an already completed task is safe and has no
effect. This means you can cancel tasks without worrying about race
conditions between completion and cancellation.

### Task.Await()

The `Await()` method suspends the calling context until the task
completes, then returns the task's result:

<!--versetest
BackgroundWork()<computes><suspends>:int=42
F()<suspends>:void={
ComputeTask:task(int) = spawn{BackgroundWork()}
Result:int = ComputeTask.Await()
Print("Task returned: {Result}")
}
<#
-->
<!-- 17 -->
```verse
ComputeTask:task(int) = spawn{BackgroundWork()}

# Wait for task to complete and get result
Result:int = ComputeTask.Await()
Print("Task returned: {Result}")
```
<!-- #> -->

**Key behaviors of Await():**

- **Blocks until completion**: If the task is still running, `Await()`
  suspends until it finishes
- **Returns immediately if complete**: If the task already finished,
  `Await()` returns the cached result instantly (Sticky)
- **Can be called multiple times**: You can await the same task
  repeatedly, always getting the same result
- **Propagates cancellation**: If the awaited task was canceled,
  `Await()` propagates the cancellation to the caller

<!--versetest
ComputeValue<public>()<suspends>:int = 42
F()<suspends>:void={
MyTask:task(int) = spawn{ComputeValue()}
FirstResult := MyTask.Await()
SecondResult := MyTask.Await()
}
<#
-->
<!-- 18 -->
```verse
MyTask:task(int) = spawn{ComputeValue()}

# First await - waits for completion
FirstResult := MyTask.Await()

# Second await - returns cached result immediately
SecondResult := MyTask.Await()

# FirstResult = SecondResult
```
<!-- #> -->


### Common Task Patterns

**Canceling a task after timeout:**

<!--versetest
ProcessData()<suspends>:void={}
-->
<!-- 27 -->
```verse
StartTask()<suspends>:void =
    DataTask:task(void) = spawn{ProcessData()}

    race:
        block:
            DataTask.Await()
            Print("Task completed")
        block:
            Sleep(5.0)
            DataTask.Cancel()
            Print("Task timed out and was canceled")
```

**Waiting for multiple spawned tasks:**

<!--versetest
Task1()<suspends>:int=1
Task2()<suspends>:int=2
Task3()<suspends>:int=3
-->
<!-- 28 -->
```verse
RunMultipleTasks()<suspends>:void =
    T1 := spawn{Task1()}
    T2 := spawn{Task2()}
    T3 := spawn{Task3()}

    # Wait for all to complete
    Results := sync:
        T1.Await()
        T2.Await()
        T3.Await()

    Print("All tasks complete: {Results(0)}, {Results(1)}, {Results(2)}")
```


### Suspension Points and Cancellation

Task cancellation in Verse follows a cooperative model. Rather than
forcefully terminating tasks, which could leave resources in
inconsistent states, Verse sends cancellation signals that tasks check
at **suspension points**. When a task receives a cancellation signal,
it has the opportunity to clean up resources before terminating. This
cooperative approach prevents data corruption while ensuring
responsive cancellation.

Suspension points are the specific locations where async tasks can
pause and resume. These are the only places where:

- A task can be suspended to allow other tasks to run
- Cancellation signals are checked and processed
- The runtime can switch between concurrent tasks

Common suspension points include:

**Timing operations:**

<!--versetest
F()<suspends>:void=
    Sleep(1.0)
    NextTick() 
<#
-->
<!-- 30 -->
```verse
Sleep(1.0)  # Suspends for duration, checks cancellation when resuming
NextTick()  # Waits one simulation update, checks cancellation
```
<!-- #> -->

**Calling suspends functions:**

<!--versetest
SomeAsyncFunction<public>()<suspends>:void = {}
F()<suspends>:void={
Result := SomeAsyncFunction()
}
<#
-->
<!-- 32 -->
```verse
Result := SomeAsyncFunction()  # Suspension point at the call
```
<!-- #> -->

**Structured concurrency expressions:**

<!--versetest
Op1()<suspends>:void = {}
Op2()<suspends>:void = {}
M()<suspends>:void =
    sync:
        Op1()
        Op2()
<#
-->
<!-- 33 -->
```verse
sync:  # Suspension point when entering sync
    Op1()
    Op2()
# Suspension point when sync completes
```
<!-- #> -->

**Task operations:**

<!--versetest
ComputeValue<public>()<suspends>:int = 42
F()<suspends>:void={
MyTask:task(int) = spawn{ComputeValue()}
Result := MyTask.Await()
}
<#
-->
<!-- 34 -->
```verse
Result := MyTask.Await()  # Suspension point while waiting
```
<!-- #> -->

**Important:** Immediate code between suspension points runs without
interruption. If you write a long computation loop without any
suspension points, that task cannot be canceled until it reaches the
next suspension point:

<!--versetest
ComputeExpensiveOperation(:int):void={}
-->
<!-- 35  -->
```verse
# Cannot be canceled during the loop
LongComputation()<suspends>:void =
    for (I := 0..1000000):
        # No suspension points - runs to completion
        ComputeExpensiveOperation(I)
    Sleep(0.0)  # First cancellation check happens here!

# Can be canceled every iteration
ResponsiveComputation()<suspends>:void =
    for (I := 0..1000000):
        ComputeExpensiveOperation(I)
        Sleep(0.0)  # Cancellation checked every iteration
```

If you need to make long-running computations cancellable, insert
periodic suspension points using `Sleep(0.0)` or `NextTick()`, which
yield control without actual delay but allow cancellation checking.

Cancellation cascades through the task hierarchy. When a parent task
is canceled, all its child tasks receive cancellation signals
too. This cascading behavior maintains the invariant that child tasks
don't outlive their parents in structured concurrency, preventing
resource leaks and ensuring predictable cleanup. In a race expression,
for example, when the winner completes, the race task sends
cancellation signals to all losing subtasks, which then cascade to any
tasks those losers might have created.

## Cleanup and Resource Management

### The defer: Block

The `defer:` block provides guaranteed cleanup code execution when a
function scope exits, whether through normal completion, failure, or
cancellation. Deferred blocks always execute during stack unwinding,
making them the perfect tool for resource cleanup, logging, and
finalization.

<!--versetest
AcquireResource():int=42
ReleaseResource(:int):void={}
ProcessWithResource(:int)<suspends>:void={Sleep(1.0)}
-->
<!-- 36 -->
```verse
UseResourceSafely()<suspends>:void =
    Resource := AcquireResource()

    defer:
        # This ALWAYS runs when function exits
        ReleaseResource(Resource)
        Print("Resource released")

    ProcessWithResource(Resource)
    # defer block executes here on normal completion
```

**Key defer: behaviors:**

1. **Always executes on scope exit**: Whether the function returns normally, fails, or is canceled, the defer block runs
2. **Runs in reverse order**: Multiple defer blocks execute in LIFO
   order (last-in-first-out - most recent defer runs first)
3. **Captures current scope**: defer blocks close over variables from
   the enclosing scope
4. **Cannot be suspended**: defer blocks must execute immediately and
   cannot contain suspending operations

**Multiple defer blocks execute in reverse order:**

<!--versetest-->
<!-- 37 -->
```verse
Print("Start")

defer:
    Print("First defer (runs last)")

defer:
    Print("Second defer (runs second)")

defer:
    Print("Third defer (runs first)")

Print("End")

# Output:
# Start
# End
# Third defer (runs first)
# Second defer (runs second)
# First defer (runs last)
```

This reverse ordering mirrors the natural stacking of resource
acquisition—resources are released in the opposite order they were
acquired, preventing dependency issues.

**Common defer: patterns:**

**Resource cleanup:**

<!--versetest
OpenFile(:string):int=0
CloseFile(:int):void={}
ProcessFile(:int)<suspends>:void={}
-->
<!-- 38 -->
```verse
ProcessFileWithCleanup(Path:string)<suspends>:void =
    FileHandle := OpenFile(Path)

    defer:
        CloseFile(FileHandle)

    ProcessFile(FileHandle)
    # File always closed, even on cancellation
```

**State restoration:**

<!--versetest
SaveState():int=0
RestoreState(:int):void={}
ModifyState()<suspends>:void={}
-->
<!-- 39 -->
```verse
TemporarilyModifyState()<suspends>:void =
    OriginalState := SaveState()

    defer:
        RestoreState(OriginalState)

    ModifyState()
    # State restored to original value
```

**Logging and debugging:**

<!--versetest
Operation()<suspends>:void={}
-->
<!-- 40 -->
```verse
TrackedOperation()<suspends>:void =
    Print("Operation starting")

    defer:
        Print("Operation finished (or canceled)")

    Operation()
```

**defer: with cancellation:**

When a task is canceled, defer blocks execute as the stack unwinds from the cancellation point:

<!--versetest
Setup():void={}
Teardown():void={}
LongOperation()<suspends>:void={loop{NextTick()}}
-->
<!-- 42 -->
```verse
CancellableWork()<suspends>:void =
    Setup()

    defer:
        Teardown()
        Print("Cleanup after cancellation")

    # If this task is canceled, defer runs during unwinding
    LongOperation()
```

defer blocks **cannot** contain suspending operations. This ensures
cleanup happens immediately without delay:

<!--versetest
ValidDefer()<suspends>:void =
    defer:
        Print("Cleanup happens immediately")
    Sleep(1.0)
<#
-->
<!-- 44 -->
```verse
# ERROR: Cannot use suspending operations in defer
BadDefer()<suspends>:void =
    defer:
        Sleep(1.0)  # ERROR: defer blocks cannot suspend
        NextTick()  # ERROR: defer blocks cannot suspend
```
<!-- #> -->

This restriction is essential—if defer blocks could suspend, cleanup
could be delayed indefinitely, defeating their purpose as guaranteed
finalization.

**defer: scope:**

defer blocks belong to their enclosing function scope and execute when that function exits:

<!--verse -->
<!-- 45 -->
```verse
HelperFunction():void =
    defer:
        Print("Helper defer")
    Print("In helper")

OuterFunction()<suspends>:void =
    defer:
        Print("Outer defer")

    HelperFunction()  # Helper's defer runs immediately after HelperFunction returns
    Print("After helper")

    # Output:
    # Helper defer
    # After helper
    # Outer defer
```

Each function has its own defer stack. When a function returns, only
its defer blocks execute, not those of calling functions.

## Timing Functions

The fundamental timing function that suspends execution for a specified duration:

<!--versetest
M()<suspends>:void =
    Sleep(1.0)

    Sleep(0.0)
<#
-->
<!-- 46 -->
```verse
# Suspend for 1 second
Sleep(1.0)

# Suspend for one frame (smallest possible delay)
Sleep(0.0)
```
<!-- #> -->

The `Sleep(0.0)` pattern deserves special attention. While it doesn't
add actual delay, it serves two critical purposes:

1. **Creates a suspension point** for cancellation checking
2. **Yields control** to other concurrent tasks, preventing one task from monopolizing execution

This makes `Sleep(0.0)` essential for responsive concurrent code:

<!--versetest
ProcessFrame():void={}
ExpensiveOperation(:int):void={}
-->
<!-- 47 -->
```verse
# Without Sleep(0.0) - cannot be cancelled during loop
UnresponsiveLoop()<suspends>:void =
    for (I := 0..10000):
        ExpensiveOperation(I)
    # Cancellation only checked after all iterations

# With Sleep(0.0) - responsive to cancellation
ResponsiveLoop()<suspends>:void =
    for (I := 0..10000):
        ExpensiveOperation(I)
        Sleep(0.0)  # Yields and checks cancellation each iteration
```

**Best practice:** Insert `Sleep(0.0)` in long-running loops to ensure
tasks remain responsive to cancellation and share execution time
fairly with other concurrent operations.

### NextTick()

!!! note "Unreleased Feature"
    NextTick() have not yet been released. 

The `NextTick()` function suspends execution until the next simulation
update (tick). Unlike `Sleep(0.0)` which yields control and may resume
in the same tick if no other work is pending, `NextTick()` guarantees
that at least one simulation update will occur before resuming:

<!--versetest
M()<suspends>:void =
    NextTick()

    NextTick()
    NextTick()
    NextTick()
<#
-->
<!-- 48 -->
```verse
# Wait for exactly one simulation tick
NextTick()

# Multiple ticks
NextTick()  # Wait 1 tick
NextTick()  # Wait another tick
NextTick()  # Wait a third tick
```
<!-- #> -->

`NextTick()` is essential for game logic that needs to be synchronized with simulation updates:

<!--versetest
ProcessGameLogic():void={}
UpdatePhysics():void={}
CheckCollisions():void={}
PerformAction():void={}

GameLoop()<suspends>:void =
    loop:
        ProcessGameLogic()
        UpdatePhysics()
        CheckCollisions()
        NextTick()

DelayByTicks(TickCount:int)<suspends>:void =
    for (I := 1..TickCount):
        NextTick()

# Test the delay function
TestDelay()<suspends>:void =
    DelayByTicks(5)
    PerformAction()
<#
-->
<!-- 49 -->
```verse
# Process game logic every tick
GameLoop()<suspends>:void =
    loop:
        ProcessGameLogic()
        UpdatePhysics()
        CheckCollisions()
        NextTick()  # Wait for next simulation update

# Delay action by specific number of ticks
DelayByTicks(TickCount:int)<suspends>:void =
    for (I := 1..TickCount):
        NextTick()

# Wait 5 ticks before executing action
DelayByTicks(5)
PerformAction()
```
<!-- #> -->

**Sleep(0.0) vs NextTick():**

| Feature   | Sleep(0.0)              | NextTick() |
|---------  |------------             |------------|
| Timing    | May resume in same tick | Always waits for next tick |
| Use case  | Yield for cancellation checks | Synchronize with simulation updates |
| Guarantee | Creates suspension point | Guarantees tick boundary |

Both create suspension points for cancellation, but `NextTick()`
provides stronger timing guarantees when you need to align with the
simulation clock.

<!--versetest
ProcessFrame()<computes>:logic=false
-->
<!-- 50 -->
```verse
# Common patterns
LoopWithDelay()<suspends>:void =
    loop:
        ProcessFrame()
        Sleep(0.033)  # ~30 FPS

TickBasedLoop()<suspends>:void =
    loop:
        if (ProcessFrame()=false): 
             break
        NextTick()  # Once per simulation tick	
```

Timing Patterns are:

<!--versetest
DoAction():void={}
UpdateLogic()<computes>:void={}
Float(:int)<computes>:float=0.0
SetPosition(:float):void={}
-->
<!-- 51 -->
```verse
# Delayed action
PerformDelayedAction()<suspends>:void =
    Sleep(2.0)  # Wait 2 seconds
    DoAction()

# Periodic execution
PeriodicUpdate()<suspends>:void =
    loop:
        UpdateLogic()
        Sleep(1.0)  # Update every second

# Animation timing
AnimateMovement(Start:float,End:float)<suspends>:void =
    for (T := 0..10):
        SetPosition(Lerp(Start, End, Float(T)/10.0))
        Sleep(0.0)  # One frame
```

### Getting Current Time: GetSecondsSinceEpoch

The `GetSecondsSinceEpoch()` function returns the current Unix
timestamp—the number of seconds elapsed since January 1, 1970,
00:00:00 UTC. This function is essential for timestamping events,
measuring durations, and synchronizing with external systems that use
Unix time.

<!--versetest
LogEvent(Message:string):void =
    Timestamp := GetSecondsSinceEpoch()
    Print("[{Timestamp}] {Message}")
<#
-->
<!-- 52 -->
```verse
# Get current timestamp
CurrentTime := GetSecondsSinceEpoch()
# Returns something like 1716411409.0 (May 22, 2024)

# Log an event with timestamp
LogEvent(Message:string):void =
    Timestamp := GetSecondsSinceEpoch()
    Print("[{Timestamp}] {Message}")
```
<!-- #> -->

**Critical transactional behavior:**

Within a single transaction, `GetSecondsSinceEpoch()` returns the
**same value** every time it's called. This ensures deterministic
behavior and prevents time-related race conditions:

<!--versetest
DoExpensiveWork()<transacts>:void = {}
PerformDatabaseUpdates()<transacts>:void = {}

MeasureTransactionTime()<transacts>:void =
    StartTime := GetSecondsSinceEpoch()

    DoExpensiveWork()
    PerformDatabaseUpdates()

    EndTime := GetSecondsSinceEpoch()

    Duration := EndTime - StartTime
<#
-->
<!-- 53 -->
```verse
MeasureTransactionTime()<transacts>:void =
    StartTime := GetSecondsSinceEpoch()

    # Perform complex operations
    DoExpensiveWork()
    PerformDatabaseUpdates()

    EndTime := GetSecondsSinceEpoch()

    # StartTime = EndTime!
    # Time is "frozen" within the transaction
    Duration := EndTime - StartTime  # Always 0.0
```
<!-- #> -->

This transactional consistency is intentional—it prevents
non-deterministic behavior where transaction retry could produce
different results due to time progression. If the transaction fails
and is retried, all calls to `GetSecondsSinceEpoch()` in the retried
attempt will return a new consistent timestamp.

**Measuring elapsed time across transactions:**

To measure actual elapsed time, take timestamps in separate transactions:

<!--versetest
game_timer := class:
    var StartTime:float = 0.0

    Start()<transacts>:void =
        set StartTime = GetSecondsSinceEpoch()

    GetElapsed()<transacts>:float =
        CurrentTime := GetSecondsSinceEpoch()
        CurrentTime - StartTime

assert:
   Timer := game_timer{}
   Timer.Start()
   ElapsedSeconds := Timer.GetElapsed()
<#
-->
<!-- 54 -->
```verse
game_timer := class:
    var StartTime:float = 0.0

    Start()<transacts>:void =
        set StartTime = GetSecondsSinceEpoch()

    GetElapsed()<transacts>:float =
        CurrentTime := GetSecondsSinceEpoch()
        CurrentTime - StartTime

Timer := game_timer{}
Timer.Start()

# Later, in a different transaction
ElapsedSeconds := Timer.GetElapsed()
# ElapsedSeconds reflects actual time passed
```
<!-- #> -->

**Use cases:**

**Event logging and debugging:**

<!--versetest
logger := class:
    var EventLog:[]tuple(float, string) = array{}

    Log(Message:string)<transacts>:void =
        Timestamp := GetSecondsSinceEpoch()
        set EventLog = EventLog + array{(Timestamp, Message)}

    GetRecentEvents(LastSeconds:float)<transacts>:[]string =
        Now := GetSecondsSinceEpoch()
        Cutoff := Now - LastSeconds
        for (Entry : EventLog, Entry(0) >= Cutoff):
            Entry(1)
<#
-->
<!-- 55 -->
```verse
logger := class:
    var EventLog:[]tuple(float, string) = array{}

    Log(Message:string)<transacts>:void =
        Timestamp := GetSecondsSinceEpoch()
        set EventLog = EventLog + array{(Timestamp, Message)}

    GetRecentEvents(LastSeconds:float)<transacts>:[]string =
        Now := GetSecondsSinceEpoch()
        Cutoff := Now - LastSeconds
        for ((Time, Message) : EventLog, Time >= Cutoff):
            Message
```
<!-- #> -->

**Session tracking:**
<!--versetest-->
<!-- 56 -->
```verse
player_session := class:
    LoginTime:float

MakeSession()<transacts>:player_session =
    player_session{LoginTime := GetSecondsSinceEpoch()}

GetSessionDuration(S:player_session)<transacts>:float =
    GetSecondsSinceEpoch() - S.LoginTime
```

**Rate limiting:**

<!--versetest
PerformAction():void={}
ShowCooldownMessage():void={}
rate_limiter := class:
    var LastAction:float = 0.0
    Cooldown:float = 5.0

    CanAct()<transacts><decides>:void =
        Now := GetSecondsSinceEpoch()
        TimeSinceLastAction := Now - LastAction
        TimeSinceLastAction >= Cooldown
        set LastAction = Now

assert:
   Limiter := rate_limiter{}
   if (Limiter.CanAct[]):
       PerformAction()
   else:
       ShowCooldownMessage()
<#
-->
<!-- 57 -->
```verse
rate_limiter := class:
    var LastAction:float = 0.0
    Cooldown:float = 5.0  # 5 second cooldown

    CanAct()<transacts><decides>:void =
        Now := GetSecondsSinceEpoch()
        TimeSinceLastAction := Now - LastAction
        TimeSinceLastAction >= Cooldown
        set LastAction = Now

Limiter := rate_limiter{}

if (Limiter.CanAct[]):
    PerformAction()
else:
    ShowCooldownMessage()
```
<!-- #> -->

**Absolute timestamps for external systems:**

When interfacing with external systems, databases, or APIs that use Unix timestamps:

<!--versetest
MyPlayerID:string = "player123"
SendToAnalytics<public>(EventType:string, Timestamp:float, PlayerID:string):void = {}
FetchServerTime():float = 1716411409.0

M():void =
    SendToAnalytics("player_action", GetSecondsSinceEpoch(), MyPlayerID)

    ServerTime := FetchServerTime()
    LocalTime := GetSecondsSinceEpoch()
    ClockSkew := LocalTime - ServerTime
<#
-->
<!-- 58 -->
```verse
# Timestamp for external analytics
AnalyticsEvent := map{
    "event_type" => "player_action",
    "timestamp" => GetSecondsSinceEpoch(),
    "player_id" => MyPlayerID
}
SendToAnalytics(AnalyticsEvent)

# Comparing with server timestamps
ServerTime := FetchServerTime()
LocalTime := GetSecondsSinceEpoch()
ClockSkew := LocalTime - ServerTime
```
<!-- #> -->

**Important notes:**

- Returns `float` representing seconds (may have fractional parts for millisecond precision)
- Located in `/Verse.org/Verse` module—use `using { /Verse.org/Verse }` to access
- Not affected by `Sleep()` or other suspension—measures real-world time
- Consistent within transactions for determinism
- Each new transaction gets a fresh timestamp

**Combining with Sleep for time-based logic:**

<!--versetest
PerformAction<public>()<suspends>:void = {}
-->
<!-- 59 -->
```verse
# Wait until a specific time
WaitUntil(TargetTime:float)<suspends>:void =
    loop:
        if (GetSecondsSinceEpoch() >= TargetTime) then:
            break
        Sleep(0.1)  # Check every 100ms

# Schedule an action for the future
ScheduleDelayedAction(DelaySeconds:float)<suspends>:void =
    TargetTime := GetSecondsSinceEpoch() + DelaySeconds
    WaitUntil(TargetTime)
    PerformAction()
```

Note that the transactional consistency means you cannot use
`GetSecondsSinceEpoch()` to measure time within a single
transaction. For measuring execution time of operations that don't
span transactions, use profiling tools or external timing mechanisms.

## Events and Synchronization

Events provide synchronization primitives for coordinating between
concurrent tasks. They implement producer-consumer and observer
patterns, allowing tasks to signal each other and wait for specific
conditions. Events bridge the gap between independent concurrent
operations, enabling communication without shared mutable state.

### Basic Events

The `event(t)` type creates a communication channel where producers
signal values and consumers await them. Each signal delivers one value
to each awaiting task:

<!--versetest
ProcessValue(:int):void={}
F()<suspends>:void={
GameEvent := event(int){}

ProducerTask()<suspends>:void =
    Sleep(1.0)
    GameEvent.Signal(42)

ConsumerTask()<suspends>:void =
    Value := GameEvent.Await()
    ProcessValue(Value)

sync:
    ProducerTask()
    ConsumerTask()
}
<#
-->
<!-- 60 -->
```verse
# Create an event channel for integers
GameEvent := event(int){}

# Producer: signals values to the event
ProducerTask()<suspends>:void =
    Sleep(1.0)
    GameEvent.Signal(42)

# Consumer: awaits values from the event
ConsumerTask()<suspends>:void =
    Value := GameEvent.Await()
    ProcessValue(Value)

sync:
    ProducerTask()
    ConsumerTask()
```
<!-- #> -->

When `Await()` is called on an event, the calling task suspends until
another task calls `Signal()` with a value. The signaled value is
delivered to one waiting task, and execution resumes. If multiple
tasks await the same event, each `Signal()` wakes exactly one
awaiter—signals and awaits pair up one-to-one.

This one-to-one matching makes events perfect for task
coordination. Think of a player action system: the input handler
signals button presses while the gameplay system awaits them. Or
consider an AI pathfinding request: the game logic signals destination
requests while the pathfinding system awaits and processes them.

Events work naturally with structured concurrency. You can use them
within `sync` blocks to coordinate parallel operations, or combine
them with `race` to implement timeouts on event waiting:

<!--versetest
F()<suspends>:void={
GameEvent:event(int)=event(int){}
Result := race:
    block:
        Value := GameEvent.Await()
        option{Value}
    block:
        Sleep(5.0)
        false
}
<#
-->
<!-- 61 -->
```verse
# Wait for event with timeout
Result := race:
    block:
        Value := GameEvent.Await()
        option{Value}
    block:
        Sleep(5.0)
        false  # Timeout - no value received
```
<!-- #> -->

### Sticky Events

!!! note "Unreleased Feature"
    Sticky Events have not yet been released and is not currently available.

While basic events deliver each signal to exactly one awaiter,
`sticky_event(t)` remembers the last signaled value and delivers it to
all subsequent awaits until a new value is signaled:

<!--NoCompile-->
<!-- 62 -->
```verse
StateEvent := sticky_event(int){}

# Signal once
StateEvent.Signal(100)

# Multiple awaits all receive the same value
Value1 := StateEvent.Await()  # Gets 100
Value2 := StateEvent.Await()  # Gets 100 again
Value3 := StateEvent.Await()  # Still gets 100

# New signal updates the sticky value
StateEvent.Signal(200)
Value4 := StateEvent.Await()  # Gets 200
Value5 := StateEvent.Await()  # Also gets 200
```

Sticky events excel at representing state changes that multiple
consumers need to observe. Unlike basic events where each signal
disappears after one await, sticky events maintain the current
state. Consider a game phase system: when the phase changes from
"Lobby" to "Playing", every system that checks the phase should see
"Playing", not have one system consume the signal while others miss
it.

The sticky behavior creates a form of eventually consistent state. If
a task awaits a sticky event, it's guaranteed to see the most recent
signal, even if that signal occurred before the await. This makes
sticky events ideal for configuration updates, mode switches, or any
scenario where "what's the current state?" matters more than "what
just changed?".

### Subscribable Events

!!! note "Unreleased Feature"
    Subscribable Events have not yet been released and is not currently available.

The `subscribable_event` type implements the observer pattern,
allowing multiple handlers to react to each signal. Unlike events
where awaiting tasks explicitly wait, subscribable events let you
register callback functions that execute automatically when values are
signaled:

<!--NoCompile-->
<!-- 63 -->
```verse
LogScore(:int):void={}
UpdateUI(:int):void={}
CheckAchievements(:int):void={}

ScoreEvent := subscribable_event(int){}

# Subscribe multiple handlers
Logger := ScoreEvent.Subscribe(LogScore)
UIUpdater := ScoreEvent.Subscribe(UpdateUI)
AchievementChecker := ScoreEvent.Subscribe(CheckAchievements)

# Signal invokes all subscribed handlers
ScoreEvent.Signal(1000)  # Calls LogScore(1000), UpdateUI(1000), CheckAchievements(1000)

# Unsubscribe to stop receiving signals
Logger.Cancel()
ScoreEvent.Signal(2000)  # Only calls UpdateUI and CheckAchievements
```

Each subscription returns a `cancelable` object that lets you
unsubscribe by calling `Cancel()`. Once canceled, that handler stops
receiving signals. This provides fine-grained control over handler
lifetimes, essential for systems that come and go during gameplay.

Subscribable events shine in broadcast scenarios where multiple
independent systems need to react to the same occurrence. When a
player scores points, the UI needs to update, the audio system needs
to play a sound, the achievement system needs to check for unlocks,
and the analytics system needs to log the event. With subscribable
events, each system registers its handler independently, and every
signal reaches all interested parties.

### The awaitable and signalable Interfaces

Events are built on two fundamental interfaces that you can use to create custom synchronization types:

<!--NoCompile-->
<!-- 64 -->
```verse
awaitable(t:type) := interface:
    Await()<suspends>:t

signalable(t:type) := interface:
    Signal(Value:t):void
```

The `awaitable` interface represents anything that can be waited on,
while `signalable` represents anything that can send signals. By
separating these capabilities, Verse enables precise control over who
can produce values versus who can consume them.

You can pass `awaitable` parameters to functions that should only read
from an event, preventing accidental signals:

<!--versetest
ProcessValue(:int):void={}
-->
<!-- 65 -->
```verse
# This function can only await, not signal
ConsumerFunction(Source:awaitable(int))<suspends>:void =
    Value := Source.Await()
    ProcessValue(Value)
    # Source.Signal(123)  # ERROR: awaitable doesn't have Signal

# This function can only signal, not await
ProducerFunction(Target:signalable(int)):void =
    Target.Signal(42)
    # Value := Target.Await()  # ERROR: signalable doesn't have Await
```

This separation creates clear interfaces for producer-consumer
relationships. A queue implementation might expose an `awaitable`
interface to consumers for reading and a `signalable` interface to
producers for writing, ensuring neither side can accidentally use the
wrong operation.

### Transactional Behavior

Event subscriptions participate in Verse's transactional system. If a
transaction containing a `Subscribe()` call fails and rolls back, the
subscription never takes effect:

<!--NoCompile-->
<!-- 66 -->
```verse
Handler(:int):void={}

MyEvent := subscribable_event(int){}

# Subscription in a failing transaction
if:
    Sub := MyEvent.Subscribe(Handler)
    false?  # Transaction fails and rolls back

# Subscription was rolled back - handler not called
MyEvent.Signal(100)
```

Similarly, `Cancel()` operations are transactional. If you cancel a subscription within a transaction that later fails, the subscription remains active:

<!--NoCompile-->
<!-- 67 -->
```verse
Handler(:int):void={}

MyEvent := subscribable_event(int){}
Sub := MyEvent.Subscribe(Handler)

# Cancel in a failing transaction
if:
    Sub.Cancel()
    false?  # Transaction fails

# Cancel was rolled back - subscription still active
MyEvent.Signal(100)  # Handler still gets called
```

This transactional integration ensures that event subscriptions
maintain consistency with other transactional operations. If you're
setting up a complex system where subscribing to events is part of a
larger initialization that might fail, the transaction system
guarantees that either all initialization succeeds or none of it does,
preventing partial setups that could cause subtle bugs.

### Event Patterns and Use Cases

**Request-Response:** Use basic events to implement request-response patterns between systems:

<!--versetest
FindPath(Start:int, Goal:int):void = {}

pathfinding_system := class:
    PathRequest:event(tuple(int, int)) = event(tuple(int, int)){}
    PathResponse:event(int) = event(int){}

    PathfindingService()<suspends>:void =
        loop:
            Request := PathRequest.Await()
            Start := Request(0)
            Goal := Request(1)
            FindPath(Start, Goal)
            PathResponse.Signal(42)

    RequestPath(Start:int, Goal:int)<suspends>:int =
        PathRequest.Signal((Start, Goal))
        PathResponse.Await()
<#
-->
<!-- 68 -->
```verse
PathRequest := event(tuple(int, int)){}  # (start, goal)
PathResponse := event(int){}             # path result

PathfindingService()<suspends>:void =
    loop:
        (Start, Goal) := PathRequest.Await()
        FindPath(Start, Goal)
        PathResponse.Signal(42)

RequestPath(Start:int, Goal:int)<suspends>:int =
    PathRequest.Signal((Start, Goal))
    PathResponse.Await()
```
<!-- #> -->

**State Broadcasting:** Use sticky events for state that multiple systems need to observe:

<!--NoCompile-->
<!-- 69 -->
```verse
PhaseChange := sticky_event(game_phase){}

# Systems await current phase without missing updates
UISystem()<suspends>:void =
    loop:
        Phase := PhaseChange.Await()
        UIUpdate(Phase)

AISystem()<suspends>:void =
    loop:
        Phase := PhaseChange.Await()
        AIUpdate(Phase)

AudioSystem()<suspends>:void =
    loop:
        Phase := PhaseChange.Await()
        AudioUpdate(Phase)
```

**Multi-System Notifications:** Use subscribable events when many
systems need to react to the same events:

<!--NoCompile-->
<!-- 70 -->
```verse
UpdateInventoryUI(:int):void={}
PlayPickupSound(:int):void={}
CheckCollectionAchievement(:int):void={}
LogItemPickup(:int):void={}

ItemPickedUp := subscribable_event(int){}

# Each system subscribes independently
InitializeSystems():void =
    ItemPickedUp.Subscribe(UpdateInventoryUI)
    ItemPickedUp.Subscribe(PlayPickupSound)
    ItemPickedUp.Subscribe(CheckCollectionAchievement)
    ItemPickedUp.Subscribe(LogItemPickup)

# Single signal reaches all systems
OnPlayerPickupItem(ItemID:int):void =
    ItemPickedUp.Signal(ItemID)
```

Events complement structured concurrency by providing communication
channels that outlive individual concurrent operations. While `sync`,
`race`, `rush`, and `branch` organize how tasks execute relative to
each other, events organize how tasks share information and coordinate
their actions.

## Common Patterns and Best Practices

Implement operations with timeouts using `race`:

<!--versetest
ActualOperation()<suspends>:void={}
-->
<!-- 71 -->
```verse
PerformWithTimeout()<suspends>:logic =
    race:
        block:
            ActualOperation()
            true  # Success
        block:
            Sleep(5.0)  # 5 second timeout
            false  # Timeout
```

Initialize multiple systems concurrently:

<!--versetest
LoadAssets()<suspends>:void={}
ConnectToServer()<suspends>:void={}
InitializeUI()<suspends>:void={}
PrepareAudio()<suspends>:void={}

InitializeGame()<suspends>:void =
    sync:
        LoadAssets()
        ConnectToServer()
        InitializeUI()
        PrepareAudio()
    Print("Game ready!")
<#
-->
<!-- 72 -->
```verse
InitializeGame()<suspends>:void =
    sync:
        LoadAssets()
        ConnectToServer()
        InitializeUI()
        PrepareAudio()
    Print("Game ready!")
```
<!-- #>-->

Start background tasks that don't block gameplay:

<!--versetest
MonitorPlayerStats()<suspends>:void={}
UpdateLeaderboards()<suspends>:void={}
ProcessAchievements()<suspends>:void={}
-->
<!-- 73 -->
```verse
StartBackgroundSystems()<suspends>:void =
    branch:
        MonitorPlayerStats()
    branch:
        UpdateLeaderboards()
    branch:
        ProcessAchievements()
    # Main game continues while background tasks run
```

Spawn entities with delays:

<!--versetest
enemy_class := class {     Spawn()<suspends>:void={} }
-->
<!-- 74 -->
```verse
SpawnWave(Enemies:[]enemy_class)<suspends>:void =
    for (Enemy : Enemies):
        spawn{Enemy.Spawn()}
        Sleep(0.5)  # Half second between spawns
```

## Limitations and Considerations

### Iteration Restrictions

The interaction between iteration and certain concurrency expressions
requires careful consideration. Rush and branch cannot be used
directly inside loop or for bodies, a restriction that prevents
unbounded task accumulation. When you write a loop that might execute
hundreds or thousands of times, allowing rush or branch directly would
create that many background tasks, potentially overwhelming the
system.

<!--versetest
Operation1()<suspends>:void = {}
Operation2()<suspends>:void = {}

ProcessWithRush(I:int)<suspends>:void =
    rush:
        Operation1()
        Operation2()

M()<suspends>:void =
    for (I := 0..10):
        ProcessWithRush(I)
<#
-->
<!-- 76 -->
```verse
# Not allowed
for (I := 0..10):
    rush:  # ERROR: Cannot use rush in loop
        Operation1()
        Operation2()

# Workaround - wrap in function
ProcessWithRush(I:int)<suspends>:void =
    rush:
        Operation1()
        Operation2()

for (I := 0..10):
    ProcessWithRush(I)  # OK
```
<!-- #> -->

This restriction forces you to be intentional about creating
background tasks in iterations. By wrapping the concurrent operation
in a function, you acknowledge the task creation and make it explicit
in your code structure. This small friction prevents accidental
resource exhaustion while maintaining the flexibility to use these
patterns when genuinely needed.

### Abstraction Over Implementation

Verse deliberately abstracts away the underlying threading and
scheduling mechanisms. You won't find thread creation APIs,
thread-local storage, or explicit synchronization primitives like
mutexes or semaphores. This isn't a limitation but a design
philosophy. By working with higher-level task abstractions, Verse
eliminates entire categories of bugs—no data races, no deadlocks from
incorrect lock ordering, no forgotten unlock calls.

The concurrency model is cooperative rather than preemptive. Tasks
voluntarily yield control at suspension points rather than being
forcibly interrupted by a scheduler. This cooperative nature makes
reasoning about concurrent code easier since you know exactly where
task switches can occur. It also integrates naturally with game
engines' frame-based execution models, where predictable timing is
crucial.

### Effect Interactions

The effect system that makes Verse's concurrency safe also introduces
some restrictions. The `decides` effect, which marks functions that
can fail, cannot be combined with the `suspends` effect. This
separation keeps the failure model and the concurrency model
orthogonal, preventing complex interactions that would be difficult to
reason about. Transactional operations and certain device-specific
operations may also have restrictions when used in concurrent
contexts, ensuring that operations that must be atomic remain so.
