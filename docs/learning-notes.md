# Learning Notes

### Branches
Branches keep active work separated so experimental code or incomplete features do not break what is already working on `main`[cite: 5]. Working on dedicated branches makes it easy to test changes independently, open pull requests, and discard bad experiments without affecting the rest of the project[cite: 5].

### Atomic Commits
An atomic commit contains just one logical change along with its corresponding test or documentation update[cite: 5]. Sticking to small, self-contained commits makes git log readable, simplifies finding bugs using git bisect, and allows a single change to be reverted cleanly without undoing unrelated work[cite: 5].

### Pull Requests and Code Review
Pull requests act as a required checkpoint before anything gets merged into production[cite: 5]. They give peers a structured place to catch bugs, discuss design choices, and ensure automated test suites pass before new code touches the main branch[cite: 5].

### Merge Conflicts
Merge conflicts happen when two branches modify the exact same lines of a file and Git cannot determine on its own which version is correct[cite: 5]. Resolving them requires reading both sets of conflicting changes, deciding whether to keep one side or combine both, updating the file manually, and completing the merge with a clean commit[cite: 5].
