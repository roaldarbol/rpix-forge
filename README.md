# rpix-forge

Conda packages that [rpix](https://github.com/roaldarbol/rpix) projects need in VS Code and Positron, until they're on
conda-forge. Built with [rattler-build](https://rattler.build) against conda-forge's R and published to
[https://prefix.dev/roaldarbol/rpix-forge](https://prefix.dev/roaldarbol/rpix-forge).

```sh
pixi workspace channel add https://prefix.dev/roaldarbol/rpix-forge
pixi add r-rpix r-sess r-jgd
```

Keep conda-forge first in `pixi.toml`'s channels:

```toml
channels = ["conda-forge", "https://prefix.dev/roaldarbol/rpix-forge"]
```

Pixi takes each package from the first channel that has it, so everything else comes from conda-forge, and once one of
these packages is on conda-forge, it comes from there.

## Packages

| Recipe | Version | Source | On conda-forge |
| --- | --- | --- | --- |
| `r-rpix` | 0.9.0 | [rpix](https://github.com/roaldarbol/rpix) tag `v0.9.0` | [staged-recipes#35133](https://github.com/conda-forge/staged-recipes/pull/35133) |
| `r-sess` | 3.2.0 | [vscode-R](https://github.com/REditorSupport/vscode-R) tag `v3.2.0`, `sess/` | [staged-recipes#35105](https://github.com/conda-forge/staged-recipes/pull/35105) |
| `r-jgd` | 0.2.1 | CRAN | [staged-recipes#35104](https://github.com/conda-forge/staged-recipes/pull/35104) |

- **r-rpix:** rpix itself, so it's in `pixi.lock` like any other package rather than installed separately.
- **r-sess:** the package VS Code's R extension uses to talk to R. The extension only uses an installed sess with exactly
  its own bundled source revision, so this one has to match the vscode-R release people use. `stamp_sess.R` recomputes
  that revision from the release tarball (it's the same as the extension's: `git-tree:25da801…` for 3.2.0). With it,
  the extension doesn't ask to install its own copy, and nothing has to compile sess's dependencies.
- **r-jgd:** the plot device the R extension prefers (also for R Interactive). Compiled, so it's built for each
  platform and for each R conda-forge builds for (4.4 and 4.5).

The recipes are the ones submitted to conda-forge, with sess at the current vscode-R release.

## How CI works

One workflow, no per-recipe matrix, no change detection:

- Every run calls `rattler-build` with `--skip-existing=all` over the recipes, and conda-forge's variant config
  (`conda-forge-pinning`). Anything already published (same version and build number) is skipped.
- The `linux-64` job builds **all** recipes (it owns the `noarch` ones, `r-rpix` and `r-sess`); the `osx-64`,
  `osx-arm64` and `win-64` jobs build only `r-jgd` (the `build-arch` task in `pixi.toml`).
- Pull requests only build (`build` / `build-arch` tasks); pushes to `main` and manual `workflow_dispatch` runs use
  `rattler-build publish` (`publish` / `publish-arch` tasks), which builds, uploads and indexes in one step,
  authenticating with OIDC trusted publishing.
- After publishing, a smoke test installs the three packages from the channel on every platform and loads them.

`pixi run build-local` builds everything from conda-forge alone, e.g. before the channel exists.

## Updating a package

1. In the recipe, update `context.version` and `source.sha256`, or bump `build.number` for a rebuild.
2. For `r-sess`: follow vscode-R's releases. A new release of the extension means a new sess, and the extension won't
   use an older one.
3. Open a PR: CI builds what changed.
4. Once a package is on conda-forge, delete its recipe here.
