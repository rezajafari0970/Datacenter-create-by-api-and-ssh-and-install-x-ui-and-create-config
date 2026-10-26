"""Reproduce the patched core from immutable upstream archives and tracked patches."""
import gzip, hashlib, json, os, pathlib, shutil, subprocess, tarfile, urllib.request, zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORK = pathlib.Path(os.environ['RUNNER_TEMP']) / 'dob-finalmask-core'
WORK.mkdir()
SRC = WORK / 'source'
SRC.mkdir()
VERSION = 'dob-fm-0.2.4'
UPSTREAMS = {
    'xray': ('https://codeload.github.com/XTLS/Xray-core/tar.gz/701af60772cda123492f86e383e1fdba066614a9', '300e2b5450aef6b980b7fad6e5901ec567059c8ed5d7dd661ba152765eaee4a2'),
    'reality': ('https://proxy.golang.org/github.com/xtls/reality/@v/v0.0.0-20260908062103-8cdf7bf9c7f0.zip', '388de1507e023377a12b928d066692eeaa30bbe5d13ccf321a8fe9c2f4d0be5a'),
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(args, cwd=SRC, env=None):
    subprocess.run(args, cwd=cwd, env=env, check=True)

for name, (url, expected) in UPSTREAMS.items():
    archive = WORK / (name + '.archive')
    with urllib.request.urlopen(url, timeout=60) as response:
        archive.write_bytes(response.read())
    assert digest(archive) == expected, name + ' source checksum'
with tarfile.open(WORK / 'xray.archive') as archive:
    for member in archive.getmembers():
        parts = member.name.split('/', 1)
        if len(parts) != 2 or not parts[1]:
            continue
        member.name = parts[1]
        archive.extract(member, SRC, filter='data')
reality = SRC / 'third_party/reality'
reality.mkdir(parents=True)
with zipfile.ZipFile(WORK / 'reality.archive') as archive:
    for name in archive.namelist():
        if name.endswith('/'):
            continue
        relative = pathlib.PurePosixPath(name.split('@', 1)[1].split('/', 1)[1])
        assert not relative.is_absolute() and '..' not in relative.parts
        dest = reality / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(archive.read(name))
assert digest(SRC / 'LICENSE') == '1f256ecad192880510e84ad60474eab7589218784b9a50bc7ceee34c2b91f1d5'
assert digest(reality / 'LICENSE') == '7c1bcfe5b0a8009ffae73984bad8e3b5f6bc562f67d6d67bafb600a3b8c08c5e'
patchdir = ROOT / 'ops/runtime-build'
run(['git', 'apply', '--check', str(patchdir / 'xray.patch')])
run(['git', 'apply', str(patchdir / 'xray.patch')])
run(['patch', '--batch', '-p1', '-i', str(patchdir / 'reality.patch')], cwd=reality)
run(['go', 'test', '-race', '-count=3', './common/protocol/http', './transport/internet/headers/http', './proxy/trojan', './transport/internet/finalmask/fragment', './transport/internet/tls', './transport/internet/websocket'])
run(['go', 'test', '-race', '-count=3', '-run', 'TestDOB|TestFallback|TestHandshake', './...'], cwd=reality)
run(['go', 'vet', './common/protocol/http', './transport/internet/headers/http', './proxy/trojan'])
result = {'version': VERSION, 'source_commit': os.environ['GITHUB_SHA'], 'upstreams': UPSTREAMS, 'patch_sha256': {name:digest(patchdir / (name + '.patch')) for name in UPSTREAMS}, 'assets': {}}
for arch, name in [('amd64', 'xray'), ('arm64', 'xray-arm64')]:
    binary = WORK / name
    run(['go', 'build', '-trimpath', '-buildvcs=false', '-ldflags=-s -w -buildid= -X github.com/xtls/xray-core/core.build=' + VERSION, '-o', str(binary), './main'], env=dict(os.environ, CGO_ENABLED='0', GOOS='linux', GOARCH=arch))
    if arch == 'amd64':
        caps = json.loads(subprocess.check_output([str(binary), 'dob-capabilities']))
        assert caps['schema'] == 1 and caps['reality_fallback_max_connections'] == 512
        for capability in ['websocket_graceful_close', 'tls_certificate_snapshot', 'reality_fallback_bounded', 'reality_handshake_deadline', 'reality_finalmask_fragment', 'fragmented_http_sniffing', 'fragmented_http_header', 'fragmented_trojan_auth']:
            assert caps[capability] is True, capability
        result['capabilities'] = caps
    compressed = ROOT / (name + '.gz')
    with binary.open('rb') as source, compressed.open('wb') as output:
        with gzip.GzipFile(filename='', fileobj=output, mode='wb', mtime=0, compresslevel=9) as target:
            shutil.copyfileobj(source, target)
    result['assets'][name] = {'sha256': digest(binary), 'gzip_sha256': digest(compressed), 'size': binary.stat().st_size, 'gzip_size': compressed.stat().st_size}
(ROOT / 'runtime-build.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
