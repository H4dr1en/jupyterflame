import subprocess
import os
import getopt

from tempfile import TemporaryDirectory
from io import StringIO

from IPython.display import HTML
from IPython.core.magics.execution import ExecutionMagics
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
from IPython.utils.ipstruct import Struct
from IPython.core import page

try:
    import cProfile as profile
    import pstats
except ImportError:
    # profile isn't bundled by default in Debian for license reasons
    try:
        import profile, pstats
    except ImportError:
        profile = pstats = None


def extract_flamegraph_params(params, ):    

    prun_params = "l:rs:T:qD:"

    FLAMEGRAPH_ARGS = [
        "title=",
        "subtitle=",
        "width=",     
        "height=",
        "minwidth=",
        "fonttype=", 
        "fontsize=",
        "countname=",
        "nametype=", 
        "colors=",
        "bgcolors=",
        "hash",
        "cp",
        "reverse",
        "inverted",
        "flamechart",
        "negate",
        "notes="
    ]

    # Get all parameters
    flame_opts, args = getopt.getopt(params.split(), prun_params, FLAMEGRAPH_ARGS)    

    # Build list of prun characters to exclude
    prun_params = [o for o in prun_params if o != ':']

    # prun options 
    prun_opts = [ (opt, val) for opt, val in flame_opts if opt[1] in prun_params]

    # Flame options
    flame_opts_san = []
    for opt, val in flame_opts:
        if opt[1] not in prun_params:
            flame_opts_san.append(opt)
            if val != "":
                flame_opts_san.append(val)

    return flame_opts_san, prun_opts, "".join(args)

        
@magics_class
class FlameClass(ExecutionMagics):  
    
    @line_cell_magic
    def flame(self, parameter_s='', cell=None):  

        flame_opts_san, prun_opts, args = extract_flamegraph_params(parameter_s)

        with TemporaryDirectory() as d:

            temp_prof = None

            # Get user location for storing prof file
            for opt, val in prun_opts:
                if opt == "-D":
                    temp_prof = val
                    break

            # Define temporary file for stats by default  
            if temp_prof is None:
                temp_prof = os.path.join(d, "temp_prof.prof")
                prun_opts.append(("-D", temp_prof))

            # rebuild string of user options
            prun_opts_san = " ".join(opt + " " + val for (opt, val) in prun_opts)

            temp_prof_pl = os.path.join(d, "temp_prof_pl.prof")
            temp_svg = os.path.join(d, "temp_svg.svg")
            
            self.prun(f"{prun_opts_san} {args}", cell)
            
            with open(temp_prof_pl, "w", encoding="utf-8") as f:
                subprocess.run(["flameprof", "--format=log",  temp_prof], stdout=f)

                print(["perl", "flamegraph.pl", temp_prof_pl]+flame_opts_san)
                
            with open(temp_svg, "w") as f:
                subprocess.run(["perl", "flamegraph.pl", temp_prof_pl]+flame_opts_san, stdout=f)
                
            return HTML(temp_svg)
        
    
    def _run_with_profiler(self, code, opts, namespace):
        """
        Run `code` with profiler.  Used by ``%prun`` and ``%run -p``.

        Parameters
        ----------
        code : str
            Code to be executed.
        opts : Struct
            Options parsed by `self.parse_options`.
        namespace : dict
            A dictionary for Python namespace (e.g., `self.shell.user_ns`).

        """

        # Fill default values for unspecified options:
        opts.merge(Struct(D=[''], l=[], s=['time'], T=['']))

        prof = profile.Profile()
        try:
            prof = prof.runctx(code, namespace, namespace)
            sys_exit = ''
        except SystemExit:
            sys_exit = """*** SystemExit exception caught in code being profiled."""

        stats = pstats.Stats(prof).strip_dirs().sort_stats(*opts.s)

        lims = opts.l
        if lims:
            lims = []  # rebuild lims with ints/floats/strings
            for lim in opts.l:
                try:
                    lims.append(int(lim))
                except ValueError:
                    try:
                        lims.append(float(lim))
                    except ValueError:
                        lims.append(lim)

        # Trap output.
        stdout_trap = StringIO()
        stats_stream = stats.stream
        try:
            stats.stream = stdout_trap
            stats.print_stats(*lims)
        finally:
            stats.stream = stats_stream

        output = stdout_trap.getvalue()
        output = output.rstrip()

        if 'q' not in opts:
            page.page(output)
        print(sys_exit, end=' ')

        dump_file = opts.D[0]
        text_file = opts.T[0]
        if dump_file:
            prof.dump_stats(dump_file)
        if text_file:
            with open(text_file, 'w') as pfile:
                pfile.write(output)

        if 'r' in opts:
            return stats
        else:
            return None