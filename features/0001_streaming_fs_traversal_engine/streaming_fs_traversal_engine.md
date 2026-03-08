# Streaming Filesystem Traversal

```latex
\section*{Feature 1: Streaming Filesystem Traversal as an Event Algebra}

\subsection*{1. Purpose}

The traversal engine defines the canonical observational primitive of the system. 
Given a root path, it produces a structured, streaming representation of the 
reachable portion of the filesystem. All higher-level analyses --- including 
directory aggregation, heuristics, profiling, visualization, and diffing --- 
are defined as transformations of this event stream.

The traversal is required to be memory-bounded, configurable in ordering, 
deterministic when requested, and extensible without altering its formal semantics. 
It constitutes the foundational mechanism upon which all subsequent components are built.

\subsection*{2. Formal Model}

Let the filesystem under traversal configuration $T$ be modeled as a directed graph
\[
\mathcal{G}_T = (V, E),
\]
where:
\begin{itemize}
    \item $V$ is the set of discoverable filesystem nodes under configuration $T$,
    \item $E \subseteq V \times V$ represents parent-to-child containment,
    \item $r \in V$ is the designated root node.
\end{itemize}

The traversal does not construct $\mathcal{G}_T$ explicitly. Instead, it defines 
a total order over the subset of $V$ reachable from $r$, emitting events in a 
structured sequence.

\subsection*{3. Event Algebra}

The traversal produces a finite sequence
\[
E = (e_1, e_2, \dots, e_n),
\]
where each $e_i$ belongs to the event type $\mathsf{FsEvent}$ defined as:
\[
\mathsf{FsEvent} ::= 
\begin{cases}
\mathsf{EnterDir}(p, m), \\
\mathsf{File}(p, m), \\
\mathsf{ExitDir}(p), \\
\mathsf{Skipped}(p, \rho), \\
\mathsf{Error}(p, \varepsilon).
\end{cases}
\]

Here:
\begin{itemize}
    \item $p$ is a path identifier,
    \item $m$ is a metadata record,
    \item $\rho$ is a structured skip explanation,
    \item $\varepsilon$ is an error value.
\end{itemize}

Directory entry and exit events form matched pairs; file events are terminal; 
skipped and error events record explicit non-structural classifications.

\subsection*{4. Structural Invariants}

\paragraph{Bracket Well-Formedness.}
For every directory path $d$, the sequence contains at most one pair
\[
\mathsf{EnterDir}(d, \cdot), \quad \mathsf{ExitDir}(d),
\]
and these events are properly nested. Formally, if
\[
\mathsf{EnterDir}(d_1)
\]
precedes
\[
\mathsf{EnterDir}(d_2),
\]
and $d_2$ is encountered while $d_1$ remains open, then
\[
\mathsf{ExitDir}(d_2)
\]
must precede
\[
\mathsf{ExitDir}(d_1).
\]

Thus the event stream forms a well-parenthesized word over directory nodes. 
This property guarantees that directory-local aggregation can be computed 
using a finite stack.

\paragraph{Coverage.}
Every node $v$ reachable from $r$ under configuration $T$ must produce 
exactly one of the following classifications:
\begin{itemize}
    \item a directory bracket pair,
    \item a file event,
    \item a skipped event,
    \item an error event.
\end{itemize}
No reachable node may be omitted without explicit classification.

\paragraph{Uniqueness.}
Each path identifier is emitted at most once in structural position. 
If symlink-following is enabled, the traversal must guard against cycles. 
Uniqueness may therefore be defined lexically (path-based) or structurally 
(device/inode-based), depending on configuration.

\subsection*{5. Metadata Contract}

Each structural event carries a metadata record $m$ containing, at minimum:
\begin{itemize}
    \item node type,
    \item logical size,
    \item allocated size (if supported),
    \item platform flags sufficient to interpret classification policies.
\end{itemize}

Metadata acquisition must preserve the streaming constraint. 
Extended metadata may be supported, but structural semantics must remain invariant.

\subsection*{6. Ordering Policy}

For each directory node $d$, let $C(d)$ denote its set of immediate children. 
An ordering function
\[
\pi_d : C(d) \to \mathbb{N}
\]
determines emission order.

Three policies are supported:
\begin{itemize}
    \item Deterministic ordering, defined by a canonical comparator.
    \item OS ordering, defined by native enumeration.
    \item Custom ordering, defined by a user-specified key function.
\end{itemize}

Deterministic ordering guarantees identical event sequences across runs 
under a stable filesystem state. OS ordering provides maximal performance 
without ordering guarantees.

\subsection*{7. Bundle Semantics (macOS)}

A platform predicate
\[
\mathsf{isBundle} : \mathsf{Path} \to \{\top, \bot\}
\]
may reclassify directory nodes as terminal units when bundle treatment is enabled. 
If $\mathsf{isBundle}(d) = \top$, then $d$ is emitted as a file event and 
no structural descent occurs beneath it.

This rule modifies graph expansion while preserving structural invariants.

\subsection*{8. Complexity Guarantees}

Let $N$ denote the number of reachable nodes and $D$ the maximum directory depth.

\[
\text{Time} = O(N) \quad \text{(excluding optional sorting cost)},
\]
\[
\text{Memory} = O(D).
\]

The traversal engine must not allocate memory proportional to $N$. 
Transient buffering for ordering is permitted but bounded by the maximum 
number of children in a single directory.

\subsection*{9. Extension Boundary}

The traversal engine is purely observational. It performs classification 
and structured enumeration but no aggregation or interpretation beyond 
what is necessary to maintain invariants. All higher-order semantics 
are defined externally as transformations over the event stream.

```