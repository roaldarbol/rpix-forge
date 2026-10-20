# Writes conda-forge's variant config (from the conda-forge-pinning package) to
# variants/conda_build_config.yaml (the name rattler-build needs to read its
# "# [linux]" selectors), without its channel_sources and channel_targets:
# rattler-build won't combine channel_sources with -c, or with publish's --to.
import os
import pathlib
import re

source = pathlib.Path(os.environ["CONDA_PREFIX"]) / "conda_build_config.yaml"
target = pathlib.Path(__file__).parent.parent / "variants" / "conda_build_config.yaml"
dropped = ("channel_sources", "channel_targets")

kept, skipping = [], False
for line in source.read_text(encoding="utf-8").splitlines(keepends=True):
    # A top-level key starts a new block
    if re.match(r"[A-Za-z_]", line):
        skipping = line.split(":", 1)[0].strip() in dropped
    if not skipping:
        kept.append(line)

target.parent.mkdir(exist_ok=True)
target.write_text("".join(kept), encoding="utf-8")
print(f"Wrote {target.name} without {', '.join(dropped)}")
