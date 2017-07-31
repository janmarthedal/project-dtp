from __future__ import unicode_literals

from pipeline.conf import settings
from pipeline.compilers import SubProcessCompiler


class TypescriptCompiler(SubProcessCompiler):
    output_extension = 'js'

    def match_file(self, filename):
        return filename.endswith('.ts')

    def compile_file(self, infile, outfile, outdated=False, force=False):
        if not outdated and not force:
            return  # File doesn't need to be recompiled
        command = (
            settings.PIPELINE_TYPESCRIPT_BINARY,
            settings.PIPELINE_TYPESCRIPT_ARGUMENTS,
            '-out',
            outfile,
            infile,
        )
        return self.execute_command(command)
