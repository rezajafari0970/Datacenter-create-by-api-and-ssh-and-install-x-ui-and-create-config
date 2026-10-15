# Verified XHTTP / REALITY Fragment runtime

Version dob-fm-0.1.0. Linux amd64. Native panel base 3.8.5; Xray base 26.10.10.

The Xray patch forwards Fragment half-close operations to its wrapped connection without bypassing masking. The panel preserves only Fragment masks when the installed core reports that capability. Stock-core guards remain in place. Browser Dialer is not enabled for REALITY.

Complete modified project sources, patches, upstream licenses, source commits and SHA-256 receipts are included. Xray is MPL-2.0; 3x-ui is GPL-3.0; retain upstream notices. The source archives include dependency manifests and lockfiles.

Build using Go 1.27.1, GCC and Node >=24:

```sh
tar -xzf xray-source.tar.gz
tar -xzf sanaei-source.tar.gz
(cd xray && go build -trimpath -ldflags '-s -w -X github.com/xtls/xray-core/core.build=dob-fm-0.1.0' -o ../xray ./main)
(cd sanaei/frontend && npm ci && npm run build)
(cd sanaei && go build -trimpath -ldflags '-s -w' -o ../x-ui .)
```

Only install with the bot's journaled installer, configuration checks, backups and digest verification. No migration of existing listener settings is part of this runtime.
