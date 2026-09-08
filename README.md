# AI Web Oracle

A standalone GenLayer Intelligent Contract: given a claim and a URL, it
fetches the page and returns a validator-consensus verdict on whether the
page supports the claim. No escrow, no domain-specific logic — a small,
general-purpose oracle other dapps and contracts can call directly.

See the docstring at the top of `ai_web_oracle.py` for the full design
rationale. In short, it demonstrates seven core GenLayer patterns in one
compact contract: safe web fetching, structured LLM output, decision-only
consensus (`gl.vm.run_nondet_unsafe`), prompt-injection defenses, typed
on-chain storage, expected-vs-external error classification, and
deterministic result-schema normalization (see "Schema enforcement fix"
below).

## Schema enforcement fix

An earlier version stored the LLM's verdict with `bool(result["verdict"])`.
Because any non-empty string is truthy in Python, a raw LLM output of
`{"verdict": "false", ...}` was stored as `verdict: true` — the opposite of
what validators had just agreed on. This is now fixed with a
`normalize_result()` helper applied in **both** the validator consensus
path (`validator_fn`) and immediately before constructing the stored
`Verification` record, so the two can never diverge. `normalize_result()`
also enforces `confidence` to be exactly `"high"`, `"medium"`, or `"low"`,
with deterministic fallbacks (`false` / `"low"`) for anything unparseable.
See `PR_DESCRIPTION.md` for the full rationale and test notes.

## Testing in GenLayer Studio (mobile-friendly, no local setup)

1. Open [GenLayer Studio](https://studio.genlayer.com) and paste in
   `ai_web_oracle.py` as a new contract.
2. Deploy it (Studio → Deploy).
3. Call `verify_claim` a few times to see both outcomes:
   - **True case**: pick a real, stable page and a claim it clearly
     supports — e.g. `url="https://docs.genlayer.com"`,
     `claim="This site is GenLayer's developer documentation"`.
   - **False case**: same URL, a claim it clearly does not support —
     e.g. `claim="This page is a recipe for chocolate cake"`.
   - **Unreachable case**: a broken URL, e.g.
     `url="https://this-domain-does-not-exist-12345.example"` — should
     resolve to `verdict: false, confidence: "low"` without the
     transaction failing.
4. Call `get_verification(id)` for each to confirm the stored verdict,
   confidence, and reasoning.
5. Confirm validators actually reached independent consensus (not just
   one leader's opinion) by checking the transaction's validator votes
   in Studio's node logs / trace view.

## Submitting to the GenLayer Foundation Portal ("Projects")

Package the same way as a Projects submission:
- Push `ai_web_oracle.py` (and this README) to a public GitHub repo.
- Deployed contract (Studionet): `0x5F5717adadB46E91D2E492ed5D84675ACe3eA603`
  (redeployed after the schema-enforcement fix above; supersedes the
  earlier address `0xC3D746bAA978a2D7A8eeC72290f8e551c4D9e2F2`)
- In the Portal submission notes, link the repo and these finalized Studio transactions covering the true/false/unreachable cases, and be upfront about why they're Studio rather than testnet:

  > Testnet deployment (TestnetAsimov/Bradbury) was blocked by the
  > faucet's 0.01 ETH mainnet requirement, which this wallet doesn't
  > currently hold. Evidence below is from GenLayer Studio instead,
  > including cross-model validator agreement — Studio's validator set
  > across these transactions spanned gpt-5.4, gemma, gemini, mistral,
  > glm, deepseek, gpt-oss, and sonnet, independently reaching the same
  > verdict each time, which demonstrates genuine judgment rather than
  > one model's idiosyncrasy.

  - **True case** (id 1): claim "developer documentation" on
    `https://docs.genlayer.com` → verdict `true`, confidence `high`, tx
    `0x034c06194ba459077ee70a8db0fe90c9871a4ed2029868a83f1101f3de7a3d88`.
  - **False case** (id 2): claim "This page is a recipe for chocolate
    cake" on the same URL → verdict `false`, confidence `high`, tx
    `0xf61d731eb43120b8b86980e70e2488bd53185e88c98b648cd15cc4d2c0efdaad`.
  - **Unreachable case** (id 3): a nonexistent domain → verdict `false`,
    confidence `low`, no crash, tx
    `0x0325b2b0beaa18ba2b9d2e45b2321d3a166e88a721b0a3201fc8d65b01fe5759`.
  - **Bonus — unreachable independent of claim wording** (id 4): a
    claim asserting the page confirms production-readiness, pointed at
    a nonexistent domain, still correctly resolves to `verdict: false,
    confidence: low` rather than defaulting to true, tx
    `0xfbfe5d6615ed10365288687a49e3fca668d961ff0977e47b88023cd2bd5aa78c`.
- Call out explicitly that it's a standalone, reusable primitive (not
  part of a larger dapp) and point reviewers at the docstring's
  "Patterns Demonstrated" list — that's the educational value the
  submission is being judged on.

## Suggested progression before final submission

Localnet or Studio first → TestnetAsimov to confirm real validator
infra handles it → TestnetBradbury for the transactions you'll cite as
evidence, since that's the network real LLM workloads run on. (For
this submission, testnet deployment is pending faucet access — see
notes above.)
