"""Run a preserved exact engine with a flushed JSON-lines audit log."""
from pathlib import Path
import importlib.util,sys
ROOT=Path(__file__).resolve().parent
engine_path=ROOT/'search-terminalbound.py'
if '--engine' in sys.argv:
    i=sys.argv.index('--engine');engine_path=ROOT/sys.argv[i+1];del sys.argv[i:i+2]
if '--output' in sys.argv:
    i=sys.argv.index('--output');output=Path(sys.argv[i+1]);del sys.argv[i:i+2]
    log=output.open('w',encoding='utf-8',buffering=1)
    class Tee:
        def __init__(self,original):self.original=original
        def write(self,s):log.write(s);log.flush();return self.original.write(s)
        def flush(self):log.flush();self.original.flush()
    sys.stdout=Tee(sys.stdout)
spec=importlib.util.spec_from_file_location('exact_engine',engine_path)
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
engine.main()
