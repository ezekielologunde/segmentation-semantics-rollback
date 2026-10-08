import pathlib,subprocess,json,hashlib,time
R=pathlib.Path(__file__).resolve().parents[1]
image=subprocess.check_output(['docker','image','inspect','segmentation-feasibility:v0','--format','{{.Id}}'],text=True).strip()
for backend in ['iptables-legacy','iptables-nft']:
 O=R/'analysis'/('feasibility-'+backend+'-v2');O.mkdir(exist_ok=False)
 files=[pathlib.Path(__file__),R/'src/rollback_probe_v2.py',R/'protocol/feasibility-v2.md']
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 (O/'freeze.json').write_text(json.dumps(dict(image=image,sha256={str(p.relative_to(R)):sha(p) for p in files}),indent=2))
 cmd=['docker','run','--rm','--network','none','--cap-drop','ALL','--cap-add','NET_ADMIN','--cap-add','NET_RAW','--cpus','1','--memory','256m','--mount',f'type=bind,source={R/"src/rollback_probe_v2.py"},target=/probe.py,readonly','--mount',f'type=bind,source={O},target=/out',image,'python3','/probe.py',backend]
 t=time.monotonic()
 with (O/'execution.log').open('w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=120)
 (O/'receipt.json').write_text(json.dumps(dict(exit_code=p.returncode,seconds=time.monotonic()-t,command=cmd),indent=2))
 (O/'manifest.json').write_text(json.dumps({f.name:sha(f) for f in O.iterdir() if f.is_file()},indent=2));print(backend,p.returncode)
