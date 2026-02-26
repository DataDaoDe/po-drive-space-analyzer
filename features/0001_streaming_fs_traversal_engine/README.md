Excellent. I will rewrite the feature in a more precise, restrained, and mathematically structured style.

---

# Feature 1

## Streaming Filesystem Traversal as a Deterministic Event Algebra

### 1. Purpose

The traversal engine defines the canonical method by which the system observes the filesystem. It produces a structured, streaming representation of the reachable portion of a directory tree rooted at a given path. All higher-level analyses—size aggregation, heuristics, profiling, visualization, and diffing—are defined purely as transformations of this event stream.

The traversal is designed to be:

* streaming and memory-bounded,
* deterministic when required,
* configurable for performance,
* extensible without altering its formal semantics.

This feature constitutes the foundational primitive of the system. 

---

### 2. Formal Model

Let the filesystem under a given configuration be modeled as a directed graph

[
\mathcal{G}_T = (V, E),
]

where:

* ( V ) is the set of discoverable filesystem nodes under traversal configuration ( T ),
* ( E \subseteq V \times V ) represents parent-to-child containment,
* ( r \in V ) is the designated root node.

The traversal does not construct ( \mathcal{G}_T ) explicitly. Instead, it defines a total ordering over a subset of ( V ) reachable from ( r ), emitting events in a structured sequence.

---

### 3. Event Algebra

The traversal produces a finite sequence

[
E = (e_1, e_2, \dots, e_n),
]

where each ( e_i ) belongs to the event type ( \mathsf{FsEvent} ), defined as:

[
\mathsf{FsEvent} ::=
\begin{cases}
\mathsf{EnterDir}(p, m), \
\mathsf{File}(p, m), \
\mathsf{ExitDir}(p), \
\mathsf{Skipped}(p, \rho), \
\mathsf{Error}(p, \varepsilon).
\end{cases}
]

Here:

* ( p ) is a path identifier,
* ( m ) is a metadata record,
* ( \rho ) is a structured skip explanation,
* ( \varepsilon ) is an error value.

This event system defines a bracketed traversal language. Directory entry and exit events form matched pairs; file events are terminal; skipped and error events record non-structural classifications.

---

### 4. Structural Invariants

The traversal must satisfy the following properties.

#### 4.1 Bracket Well-Formedness

For every directory path ( d ), the sequence contains at most one pair

[
\mathsf{EnterDir}(d, \cdot), \quad \mathsf{ExitDir}(d),
]

and these events are properly nested. Formally, if

[
\mathsf{EnterDir}(d_1)
]

precedes

[
\mathsf{EnterDir}(d_2),
]

and ( d_2 ) is encountered while ( d_1 ) remains open, then

[
\mathsf{ExitDir}(d_2)
]

must precede

[
\mathsf{ExitDir}(d_1).
]

Thus the event stream forms a well-parenthesized word over directory nodes. This property guarantees that directory-local aggregation can be computed using a finite stack.

#### 4.2 Coverage

Every node ( v ) reachable from ( r ) under configuration ( T ) must produce exactly one of the following classifications:

* a directory bracket pair,
* a file event,
* a skipped event,
* an error event.

No reachable node may be omitted without explicit classification.

#### 4.3 Uniqueness

Each path identifier is emitted at most once in structural position. The traversal must guard against cycles when symlink-following is enabled. The path identity policy therefore determines whether uniqueness is defined lexically (path-based) or structurally (device/inode-based).

---

### 5. Metadata Contract

Each structural event carries a metadata record ( m ) containing, at minimum:

* node type,
* logical size,
* allocated size (if supported),
* platform flags sufficient to interpret classification policies.

Metadata acquisition must not violate the streaming constraint. The traversal engine may offer minimal and extended metadata modes, but the structural event semantics remain invariant under either.

---

### 6. Ordering Policy

Traversal order is configurable.

For each directory node ( d ), let ( C(d) ) be its set of immediate children. An ordering function

[
\pi_d : C(d) \to \mathbb{N}
]

determines emission order.

Three policies are supported:

* Deterministic ordering, defined by a canonical comparator independent of OS enumeration.
* OS ordering, defined by native directory enumeration.
* Custom ordering, defined by a user-specified key function.

Deterministic ordering guarantees identical event sequences across runs under a stable filesystem state. OS ordering provides maximal performance without ordering guarantees.

The choice of ordering does not alter structural invariants, only event sequence permutation within sibling sets.

---

### 7. Bundle Semantics (macOS)

A platform predicate

[
\mathsf{isBundle} : \mathsf{Path} \to {\top, \bot}
]

may reclassify directory nodes as terminal units when bundle treatment is enabled. If ( \mathsf{isBundle}(d) = \top ), then ( d ) is emitted as a file event and no structural descent occurs beneath it.

This rule modifies graph expansion but preserves event algebra invariants. 

---

### 8. Complexity Guarantees

Let ( N ) denote the number of reachable nodes and ( D ) the maximum directory depth.

Time complexity is ( O(N) ), excluding optional sorting costs under deterministic or custom ordering. Memory complexity is ( O(D) ), reflecting only the active directory stack and, when required, transient child buffers for ordering.

The traversal engine must not allocate memory proportional to ( N ).

---

### 9. Extension Boundary

The traversal engine is purely observational. It performs classification and structured enumeration but no aggregation or interpretation beyond what is necessary to maintain invariants. All higher-order semantics—size accumulation, heuristics, domain-specific detection—are defined externally as pure consumers of the event stream.

---

If this articulation meets your standard of precision and tone, the next step is natural:

We formalize **Feature 2: Streaming Directory Size Aggregation as a Stack Homomorphism over the Event Algebra**.

Before proceeding:

Should directory aggregation compute

[
(\text{logical size}, \text{allocated size})
]

as a two-component vector from the beginning, or restrict itself initially to logical size only?
