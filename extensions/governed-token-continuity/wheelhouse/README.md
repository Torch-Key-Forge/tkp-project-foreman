# PF-GTC Gate 4A-0 Wheelhouse

The accepted Gate 3 custody packet contains eight publisher-direct Linux wheels for the pinned top-level tools. They are preserved in the canonical Gate 4A-0 closure archive in Google Drive.

This Git branch does not claim a complete wheelhouse. The complete direct and transitive artifact set is still required before the following command can pass:

```text
uv sync --frozen --offline --no-python-downloads
```

No `uv.lock` is committed because a truthful lock and offline-sync proof have not yet been produced from a complete held artifact set. Locally reconstructed wheels may not be substituted for publisher artifacts without a separately accepted exception.
