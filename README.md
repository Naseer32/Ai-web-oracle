# AI Web Oracle

A standalone GenLayer Intelligent Contract: given a claim and a URL, it
fetches the page and returns a validator-consensus verdict on whether the
page supports the claim. No escrow, no domain-specific logic — a small,
general-purpose oracle other dapps and contracts can call directly.

See the docstring at the top of `ai_web_oracle.py` for the full design
rationale. In short, it demonstrates six core GenLayer patterns in one
compact contract: safe web fetching, structured LLM output, decision-only
consensus (`gl.vm.run_nondet_unsafe`), prompt-injection defenses, typed
on-chain storage, and expected-vs-external error classification.

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
- Deployed contract (Studionet): `0xC3D746bAA978a2D7A8eeC72290f8e551c4D9e2F2`
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
    `https://docs.genlayer.com` → verdict `true`, confidence `high`.
  - **False case** (id 2): claim "This page is a recipe for chocolate
    cake" on the same URL → verdict `false`, confidence `high`, tx
    `0x365fa7639c1cd7ad5203719b9ed923ddfb9e827dd3cf51d6bbe619b57b8c69c5`.
  - **Unreachable case** (id 3): a nonexistent domain → verdict `false`,
    confidence `low`, no crash, tx
    `0x325509dd7685fa9babc78cde52c4bcc82c323425d5d2890c4b8e5e21726ef6c4`.
  - **Bonus — unreachable independent of claim wording** (id 4): the
    same "developer documentation" claim pointed at the nonexistent
    domain still correctly resolves to `verdict: false, confidence:
    low` rather than defaulting to true, tx
    `0xc43b48bf024bef9681f0c26a5ed055d473ba7c67f1a35c7000ecc043c73555be`.
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
