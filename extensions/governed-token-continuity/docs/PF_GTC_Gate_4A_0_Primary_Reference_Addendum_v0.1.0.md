# PF-GTC Gate 4A-0 Primary Reference Addendum

**Artifact ID:** `PF-GTC-G4A0-REF-ADDENDUM-20260721-001`  
**Version:** `0.1.0`  
**Status:** `COMPLETE_FOR_GATE_4A_0_REVIEW`

Only official or primary project documentation is admitted.

| Subject | Primary reference | Gate 4A-0 use |
|---|---|---|
| Git linked worktrees | https://git-scm.com/docs/git-worktree.html | Disposable linked-worktree creation, listing, removal, pruning, and repair |
| uv command contract | https://docs.astral.sh/uv/reference/cli/ | `--frozen`, `--offline`, and `--no-python-downloads` semantics |
| uv locking and syncing | https://docs.astral.sh/uv/concepts/projects/sync/ | Lockfile as source of truth and frozen synchronization |
| uv Python control | https://docs.astral.sh/uv/concepts/python-versions/ | Disable automatic Python downloads |
| Python 3.13 | https://docs.python.org/3.13/ | Accepted runtime documentation root |
| Python virtual environments | https://docs.python.org/3.13/library/venv.html | Isolated environment creation |
| Python subprocess | https://docs.python.org/3.13/library/subprocess.html | Bounded child processes and stream separation |
| Python socket | https://docs.python.org/3.13/library/socket.html | Network-denial target surface |
| Python audit hooks | https://docs.python.org/3.13/library/sys.html#sys.addaudithook | Runtime audit-event observation |
| tiktoken | https://github.com/openai/tiktoken | Tokenizer implementation and encoding registration |
| cl100k declaration | https://github.com/openai/tiktoken/blob/main/tiktoken_ext/openai_public.py | Official asset URL and expected hash declaration |
| cl100k asset | https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken | Required controlled tokenizer asset |
| Accepted platform | `PF_GTC_Gate_4_Controlled_Good_Build_Plan_v0.1.1` | WSL2/Linux x86_64 and Python 3.13.5 candidate |

## Control notes

- Required environment proof: `uv sync --frozen --offline --no-python-downloads`.
- Automatic Python downloads are prohibited.
- No HTTP server, provider endpoint, hosted service, or external telemetry backend is admitted.
- The tokenizer asset must match SHA-256 `223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7`.
