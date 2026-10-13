"""Build the tested namespace-key candidate, then restore upstream source."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKOUT = ROOT / '.local-review/kube-burner-native'
source = CHECKOUT / 'pkg/measurements/netpol_latency.go'
original = source.read_bytes()
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=CHECKOUT,text=True).strip() == '28f74ab467b212cb77e53881c7d34973f5b99a8d'
assert not subprocess.check_output(['git','diff','--','pkg/measurements/netpol_latency.go'],cwd=CHECKOUT)
try:
    subprocess.run(['git','apply',str(ROOT/'analysis/native-namespace-fix.patch')],cwd=CHECKOUT,check=True)
    subprocess.run(['docker','run','--rm','--network','none','--memory','4g','--cpus','2','-e','CGO_ENABLED=0',
       '-v','segmentation-go-modcache:/go/pkg/mod','-v','segmentation-go-buildcache:/root/.cache/go-build',
       '-v',f'{CHECKOUT}:/work','-w','/work',
       'golang@sha256:8bee1901f1e530bfb4a7850aa7a479d17ae3a18beb6e09064ed54cfd245b7191',
       'go','build','-p','2','-o','/work/kube-burner-fixed','./cmd/kube-burner'],check=True,timeout=300)
finally:
    source.write_bytes(original)
