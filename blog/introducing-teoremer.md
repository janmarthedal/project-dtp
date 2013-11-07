If you distill any book or article on some mathematical subject, then what you are left with is usually a lot of notation, definitions, algorithms, theorems, lemmas, corollaries, and proofs. *teoremer* is a collection of such mathematical items.

The items are split into the following main types:
  * **Definition** (also used for notation and algorithm).
  * **Theorem** (also used for axiom, lemma, corollary, proposition).
  * **Proof** (of varying rigor).

Each item is given a unique name and can refer to other items. This leads to a network of mathematical items with dependencies between them (a directed graph where the nodes are the math items and the edges are the references).

Associated with each definition is a number of categories, which specifies the terms being defined. A category is an ordered list of tags that provides a name and a context to a certain term or concept. For instance, a definition with the category `[analysis/operator/normal]` defines the term `normal` in the context of `operator` in the context of `analysis`. Categories are used to distinguish equally named terms within different contexts, e.g., `[analysis/operator/normal]` and `[geometry/vector/normal]`.

Once a math item (which lives up to the guidelines) is published, it can never be changed or edited in any way. Not ever. This prevents users from (accidentially) making true statements false. This also ensures that once you link to an item, you know exactly what you link to.

A theorem can have any number of proofs and a given category can have many definitions. A rating/point system will ensure that a user can easily find the 'best' item.

It is recommended that any item links to all the prerequisites it may have in terms of other items. But that means that if you wish to write a theorem that refers to the real numbers, you first have to find a satisfactory definition of the real numbers. What if none exists?
