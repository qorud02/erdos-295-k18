"""Apply the exact quadratic impossibility check before expensive prime tests."""
from pathlib import Path
import importlib.util
from fractions import Fraction
spec=importlib.util.spec_from_file_location('terminal_backend',Path(__file__).with_name('search-terminalbound.py'))
terminal=importlib.util.module_from_spec(spec);spec.loader.exec_module(terminal)
math=terminal.math
json=terminal.json

class Search(terminal.Search):
    def dfs(self,d,t,a,b,primes,prefix):
        if t==2 and a>0 and b>0 and a*a>4*b:
            delta=a*a-4*b
            s=math.isqrt(delta)
            if s*s<delta:s+=1
            if (a-s)//2<max(d,b//a+1):
                self.stats['nodes']+=1
                self.stats['quadratic_early_prunes']=self.stats.get('quadratic_early_prunes',0)+1
                if self.stats['nodes']&1023==0:
                    self.prefix=prefix;self.tick()
                return None
        return super().dfs(d,t,a,b,primes,prefix)

def main():
    terminal.Fraction=Fraction
    terminal.strong.Fraction=Fraction
    terminal.strong._base.Fraction=Fraction
    terminal.strong._base.Search=Search
    terminal.strong._base.main()

if __name__=='__main__':main()
