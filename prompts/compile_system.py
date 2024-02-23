#!/usr/bin/env python3

import re
from pathlib import Path
import sys

CWD = Path(__file__).parent

filename = "system.md"
if len(sys.argv) > 1:
    filename = sys.argv[1]


def build_template(prompt_template: str):
    arguments = re.findall(r"{{(.*?)}}", prompt_template, flags=re.DOTALL)
    prompts = {
        argument: build_template(CWD.joinpath(f"{argument.lower()}.md").read_text())
        for argument in arguments
    }

    return re.sub(
        r"{{(.*?)}}", lambda x: prompts[x.group(1)], prompt_template, flags=re.DOTALL
    ).removesuffix("\n")


system = CWD.joinpath(filename).read_text()
system = build_template(system)
CWD.joinpath("_compiled_system.md").write_text(system)
