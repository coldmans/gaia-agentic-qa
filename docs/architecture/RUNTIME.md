# Runtime architecture

## Ownership boundary

GAIA does not own browser rendering or Playwright's actionability rules. It
owns the QA runtime around that browser layer:

- translate a natural-language goal into one next action;
- bind actions to refs from the current role-tree snapshot;
- preserve action results and state changes in a run ledger;
- recover from stale or non-actionable refs without hiding the error;
- independently verify completion;
- emit benchmark artifacts and reason codes.

## Multi-call context ledger

One run spans several model calls. The ledger keeps them coherent without
pretending the model has durable memory.

```text
Actor prompt
  + current role tree
  + recent action/result digest
  + state-change evidence
  + bounded text evidence
  + current goal phase

Action result
  -> success/failure
  -> reason code
  -> ref and target
  -> URL/DOM/value change
  -> optional screenshot evidence

Judge prompt
  + actor completion claim
  + current DOM evidence
  + expected signals
  + recent state change
  + bounded run history
```

The actor proposes; the browser executes; the judge decides whether the
evidence is sufficient. A success result therefore has a traceable chain from
goal to current page state.

## Recovery policy

Recovery is error-specific. A stale ref triggers a fresh snapshot and remap. A
pointer interceptor remains an actionability failure, so the agent can reveal
or dismiss the covering surface rather than repeatedly clicking the same ref.
CAPTCHA and account gates stop as blocked user action.

## Packaged browser adapter

The repository ships a pinned, prebuilt adapter bundle as Python package data.
The full upstream source tree is not vendored. npm dependencies are locked and
installed locally on first use. The original MIT license is preserved beside
the bundle.
