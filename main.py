import os
import subprocess
import sys
from pathlib import Path
import typer
import re
import time

app = typer.Typer()

script_path = Path(__file__).resolve().parent


@app.command()
def build(target: str, workspace: str, extra: str, file_content_display: bool = False, raw: bool = False):
    target = Path(target)
    workspace = Path(workspace)

    # compile
    args = [script_path.joinpath('spcomp.exe'), target, extra]

    print(f'   {typer.style("Compiling", bold=True, fg=typer.colors.BRIGHT_GREEN)} {target.name} ({target})')

    start = time.time()

    result = subprocess.run(
        args, stdout=subprocess.PIPE).stdout.decode('utf-8')

    # print raw result from sourcepawn compile
    if raw:
        print(result)
    else:
        success = False

        # collect all notes
        notes = []
        for line in result.split('\r\n')[4:]:
            if line.startswith('Code size:'):
                success = True
                break
            notes.append(line)

        # print notes pretty
        for note in notes:
            m = re.match(r'^(.*)\((.+)\)\s:\s(.+)\s(\d+):(.*)$', note)
            if m:
                file, line, kind, code, msg = m.groups()

                if not success and kind not in ['error', 'fatal error']:
                    continue

                if kind in ['error', 'fatal error']:
                    kind = typer.style(f'{kind}[{code}]', fg=typer.colors.BRIGHT_RED, bold=True)
                elif kind == 'warning':
                    kind = typer.style(f'{kind}', fg=typer.colors.BRIGHT_YELLOW, bold=True)

                # print kind and msg
                print(kind + typer.style(f':{msg}', fg=typer.colors.BRIGHT_WHITE, bold=True))

                w = ' ' * len(line)

                # print file path and line
                print(
                    f'{w}{typer.style("-->", fg=typer.colors.BRIGHT_CYAN, bold=True)} {Path(file).relative_to(workspace)}:{line}')

                # print line content
                if file_content_display:
                    all_lines = open(Path(file), encoding='utf-8').readlines()
                    c = typer.style(' |', bold=True, fg=typer.colors.BRIGHT_CYAN)
                    print(
                        f'{w}{c}\n{typer.style(line, bold=True, fg=typer.colors.BRIGHT_CYAN)}{c} {all_lines[int(line) - 1].rstrip()}\n{w}{c}\n')

        if success:
            end = time.time()
            if len(notes):
                print(
                    f'{typer.style("warning", fg=typer.colors.BRIGHT_YELLOW, bold=True)}{typer.style(":", fg=typer.colors.BRIGHT_WHITE, bold=True)} `{target.name}` generated {len(notes)} warning')

            print(f'    {typer.style("Finished", bold=True, fg=typer.colors.BRIGHT_GREEN)} in %.2fs' % (end - start))
        else:
            print(
                f'{typer.style("error", fg=typer.colors.BRIGHT_RED, bold=True)}{typer.style(":", fg=typer.colors.BRIGHT_WHITE, bold=True)} could not compile `{target.name}` due to previous error')


if __name__ == "__main__":
    app()
