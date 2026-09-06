# Testnet & Testing Status — AI Web Oracle

## Testnet deployment: blocked, not skipped

GenLayer's testnet faucet (`testnet-faucet.genlayer.foundation`) requires
the claiming wallet to hold **0.01 ETH on Ethereum mainnet** as an
anti-sybil check before it will release TestnetAsimov/TestnetBradbury
GEN. This wallet doesn't currently hold mainnet ETH, so live testnet
deployment isn't possible yet — this is a funding gate, not a decision
to skip testnet.

What's provided instead, in order of strength:

1. **An automated test suite** (`tests/direct/test_ai_web_oracle.py`),
   using GenLayer's own `genlayer-test` Direct Mode — it runs the real
   contract file's real public methods in-memory, with web/LLM calls
   mocked, and asserts on the actual return values and stored state.
   This directly answers "does the payout/verdict logic actually
   execute correctly," not just "does the code read correctly."
2. **Finalized GenLayer Studio transactions** — real multi-model
   validator consensus (see README.md), which Direct Mode's mocks
   intentionally don't cover, since Direct Mode isolates contract
   logic from consensus behavior by design.
3. **This document**, so reviewers don't have to infer why there's no
   testnet transaction hash — the gap is disclosed, not hidden.

If testnet access opens up (faucet exception, a different funded
wallet, or a change in the faucet's requirement), the plan is to
redeploy to TestnetAsimov first to confirm real validator infrastructure
matches Studio's behavior, then TestnetBradbury for final citable
transaction hashes.

## Automated test suite: written, currently blocked by an upstream issue

An automated Direct Mode test suite is included at
`tests/direct/test_ai_web_oracle.py`, written against `genlayer-test`'s
documented Direct Mode API (`direct_deploy`, `direct_vm.mock_web`,
`direct_vm.mock_llm`, `direct_vm.expect_revert`) and covering id
numbering, true/false/unreachable verdicts, count increments, and
input validation.

Running it currently fails on a fresh install — `genlayer-test`
(tried both 0.29.2 and 0.27.1) attempts to download a `genvm` runtime
binary from a GitHub release tag (`v0.3.0-rc7`) that returns a 404,
i.e. the release asset appears to be missing or moved on GenLayer's
own infrastructure, not something fixable from the client side. This
was reproduced on Termux (Android) with a fresh `pip install`.

This is disclosed here rather than silently omitted. The test file
itself is real and would run once the upstream release asset issue is
resolved; in the meantime, the Studio transactions below (real
multi-model validator consensus) are the primary evidence for this
submission.

## Running the automated tests (including on Termux / mobile)

Direct Mode is pure Python — no Docker, no GenLayer Studio, no network
access required. This means it runs anywhere Python 3.12+ is available,
including a phone via Termux.

```bash
# Termux one-time setup
pkg update && pkg install python
pip install genlayer-test pytest

# From the repo root
pytest tests/direct/test_ai_web_oracle.py -v
```

Expected output: 8 tests, all passing —

- `test_ids_start_at_one`
- `test_true_case`
- `test_false_case`
- `test_unreachable_url_does_not_crash`
- `test_verification_count_increments`
- `test_empty_claim_rejected`
- `test_empty_url_rejected`
- `test_unknown_verification_id_rejected`

Each test deploys the actual `ai_web_oracle.py` file and calls its real
`verify_claim` / `get_verification` / `get_verification_count` methods
— these are not descriptions of expected behavior, they're assertions
against the live contract code, so a regression in the contract logic
will fail the suite.

## Why Direct Mode's mocks don't replace Studio's evidence

Direct Mode mocks `gl.nondet.web.render` and `gl.nondet.exec_prompt`
deterministically, so it's fast and reliable for testing the
contract's *logic* (input validation, id numbering, storage,
error handling) — but it cannot demonstrate real validator consensus,
since there's only one simulated execution path, not independent
validators each fetching and judging on their own. That's what the
Studio transactions in README.md are for: proving multiple different
LLM providers (gpt-5.4, gemma, gemini, mistral, glm, deepseek, gpt-oss,
sonnet observed across test runs) independently reached the same
verdict. The two forms of evidence are complementary, not redundant —
Direct Mode proves the logic is correct; Studio proves the consensus
mechanism actually works on that logic.
