# clean-code rules brief

You apply the clean-code skill's rules to the diff. Read the "While writing: the bright lines" section of the skill's
`SKILL.md` first. A project's `AGENTS.md` / `CLAUDE.md` can change or switch off a rule; theirs wins.

1. **check.py output.** It's a regex tool and can misfire. Give each line a verdict: real, or a false alarm with the
   reason.
2. **Parameters.** A new function with 4+ parameters is a finding. An existing one the diff touches is a suggestion
   only. Signatures a framework dictates (Express's `(err, req, res, next)`) are exempt.
3. **Pass-throughs.** check.py flags private ones. For each exported function whose body only forwards, decide: the
   official entry point to a layer or module (controller → service, a module's public function in front of its
   internals) is fine; forwarding within the same layer is a finding.
4. **Same names elsewhere** (from check.py): open both. The same thing → a finding (reuse it). Clearly different, like
   each file's own private constant → nothing. Unsure → a "Potential duplicate" finding with `Confidence: unsure`.
5. **Judgment rules, for every changed function:** wrappers the regex missed (class methods, multi-line forwarders),
   premature extraction (a helper used once or twice that isn't a complex step), memoization without one of the three
   allowed reasons or with an untrue reason comment, mixed responsibilities, speculative code (options, flags,
   factories for one use), unreadable conditions, comments that restate the code, edits the task didn't need.

Report in the format of [finding.md](finding.md), naming the rule in each title. Done when every check.py line has a
verdict and every changed function was checked against step 5.
