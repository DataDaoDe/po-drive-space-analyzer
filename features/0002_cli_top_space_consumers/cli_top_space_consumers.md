# Feature 0002 — CLI: Top Space Consumers

```latex
\section{Feature 0002: CLI Top Space Consumers}

\subsection{Overview}

This feature introduces a command-line interface (CLI) command that allows a user to identify the largest consumers of disk space within a specified filesystem path. The command analyzes the immediate children of a directory, computes their effective sizes, and displays the largest entries in decreasing order.

The feature constitutes the first user-facing capability of the Drive Space Analyzer system and provides a minimal mechanism for diagnosing disk usage on a machine.

\subsection{Command Definition}

The command introduced by this feature is

\begin{verbatim}
dsa top <path> [--limit N]
\end{verbatim}

where \texttt{path} denotes a filesystem path and \(N\) is an optional positive integer limiting the number of displayed results. If \(N\) is not provided, the implementation uses a fixed default.

\subsection{Filesystem Model}

Let \(\mathcal{O}\) denote the set of filesystem objects considered by the analysis. Objects may include files, directories, and other filesystem entities.

For any directory \(D\), define the set of its immediate children

\[
C(D) = \{x \in \mathcal{O} \mid x \text{ is directly contained in } D\}.
\]

The command operates on the elements of \(C(D)\).

\subsection{Recursive File Reachability}

For a directory \(x\), define the set

\[
A(x)
\]

to be the set of all descendant files of \(x\). Formally,

\[
A(x) = \{f \in \mathcal{O} \mid f \text{ is a file reachable from } x \text{ by recursive traversal}\}.
\]

\subsection{Partial Size Semantics}

Filesystem traversal may encounter permission failures or other errors that prevent the complete analysis of a directory. Consequently, the size function must allow unknown values.

Define the size codomain

\[
\mathcal{S} = \mathbb{N} \cup \{\bot\},
\]

where \(\bot\) represents an unknown size resulting from incomplete traversal.

\subsection{Size Function}

Define the size function

\[
S : \mathcal{O} \rightarrow \mathcal{S}.
\]

If \(x\) is a file and its metadata is accessible,

\[
S(x) = \mathrm{file\_size}(x),
\]

where \(\mathrm{file\_size}(x)\) denotes the file size in bytes.

If \(x\) is a directory and all children can be analyzed, define recursively

\[
S(x) = \sum_{y \in C(x)} S(y).
\]

If any child of \(x\) cannot be analyzed, then

\[
S(x) = \bot.
\]

Thus directory sizes are defined structurally over the directory tree whenever traversal succeeds, and otherwise become unknown.

\begin{proposition}
If a directory \(x\) is fully traversable, then \(S(x)\) equals the sum of the sizes of all descendant files contained within \(x\).
\end{proposition}

\begin{proof}
Proceed by structural induction on the directory tree rooted at \(x\). If all children of \(x\) are files, the claim follows immediately from the definition. Otherwise, for each child directory \(y \in C(x)\), the induction hypothesis implies that \(S(y)\) equals the sum of the sizes of all descendant files of \(y\). Summing over all immediate children of \(x\) therefore yields the sum of the sizes of all descendant files of \(x\).
\end{proof}

\subsection{Ranking}

Let \(D\) be the directory supplied to the command. The result set is constructed from the elements of \(C(D)\).

Define a ranking key

\[
K(x) = (\sigma(x), T(x), N(x)),
\]

where

\[
\sigma(x) =
\begin{cases}
-S(x) & \text{if } S(x) \in \mathbb{N} \\
+\infty & \text{if } S(x) = \bot
\end{cases}
\]

and

\begin{itemize}
\item \(T(x)\) is a fixed rank for the object type,
\item \(N(x)\) is the normalized entry name.
\end{itemize}

The ranked sequence

\[
R(D)
\]

is obtained by sorting the elements of \(C(D)\) in ascending lexicographic order according to \(K(x)\).

This ordering ensures that entries with larger sizes appear earlier, entries with unknown size appear last, and ties are broken deterministically by type and name.

\subsection{Result Selection}

Let \(N\) denote the limit parameter of the command.

The output sequence is the prefix

\[
R_N(D)
\]

defined by

\[
R_N(D) = (r_1, r_2, \dots, r_N)
\]

where \(r_i\) denotes the \(i\)-th element of \(R(D)\).

\subsection{Output Representation}

The command renders the result set as a textual table containing the size, object type, and name of each entry. Sizes are formatted using human-readable units such as bytes, kilobytes, megabytes, or gigabytes.

An example output is

\begin{verbatim}
Path: /Users/john

Largest entries
  45.2 GB  dir   Movies
  18.7 GB  dir   Library
  12.1 GB  dir   Downloads
   8.4 GB  file  archive.zip
   5.9 GB  file  video.mp4
\end{verbatim}

If the size of an entry is unknown due to traversal failure, it is rendered as

\begin{verbatim}
unknown
\end{verbatim}

in the size column.

\subsection{Determinism}

Let \(F\) denote the state of the filesystem and \(P\) the command parameters. Because the ranking relation is defined by a total ordering over \(K(x)\), the command is deterministic: for fixed \(F\) and \(P\), repeated executions produce identical output and ordering.

\subsection{Complexity}

Let

\[
n = |C(D)|
\]

be the number of immediate children of the analyzed directory, and let

\[
m
\]

denote the total number of files contained within descendant directories of those children.

Traversal requires visiting each file exactly once and therefore has time complexity

\[
O(m).
\]

Sorting the immediate children requires

\[
O(n \log n).
\]

In typical workloads the traversal cost dominates the sorting cost.

\subsection{Scope}

This feature provides only a minimal disk usage diagnostic command. It does not implement recursive tree visualization, duplicate detection, file deletion, filesystem snapshot analysis, or interactive navigation. These capabilities are introduced by later features of the system.
```