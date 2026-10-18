# Transport close and TLS certificate repair (dob-fm-0.2.3)

Xray Linux amd64 and arm64; original compatible Sanaei Fragment panel retained.

WebSocket preserves bytes returned with frame EOF and treats normal close code 1000 as stream EOF; abnormal close errors remain errors. TLS reload and OCSP refresh publish immutable atomic certificate snapshots, keeping concurrent handshakes and source configuration unchanged. The following prior REALITY protections are retained.
Unauthenticated fallback forwarding uses 16 KiB copy buffers per direction, a shared 60-second idle timer, and at most 512 simultaneous fallback connections per process. Excess invalid fallbacks are closed without consuming forwarding slots. Expired or refused unauthenticated TCP connections abort their send queues; authenticated transport is excluded. Active one-way transfer and TCP half-close responses remain supported. Rate-limit waiting is interruptible when fallback expires. A separate 60-second handshake deadline interrupts stalled reads and writes; it is cancelled when authenticated transport or fallback takes ownership. Authenticated forwarding never starts the fallback idle timer.

Complete modified sources, upstream commits, dependency lockfiles, patches and licenses are included. Xray is MPL-2.0; REALITY retains its upstream BSD notices; Sanaei is GPL-3.0. Keep all notices. The panel binary and source archive are unchanged from dob-fm-0.1.0.

Build using Go 1.27.1:

```sh
tar -xzf xray-source.tar.gz
tar -xzf reality-source.tar.gz
(cd xray/third_party/reality && go test -race ./...)
(cd xray && CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -trimpath -ldflags '-s -w -X github.com/xtls/xray-core/core.build=dob-fm-0.2.3' -o ../xray ./main)
```

For arm64, change GOARCH to arm64. For the unchanged panel, extract sanaei-source.tar.gz, run npm ci and npm run build in sanaei/frontend, then go build -trimpath -ldflags '-s -w' in sanaei. Install only using the journaled configuration-validation, identity-preservation and rollback procedure. Existing listener settings and client identities must remain unchanged.
