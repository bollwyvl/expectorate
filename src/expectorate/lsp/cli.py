import sys
from typing import Text

import click

from ..context import Context
from . import constants
from .conventions import CONVENTIONS


@click.group()
@click.pass_context
def lsp(ctx: Context):
    """ Tools for working with the Language Server Protocol
    """
    pass


@lsp.command()
@click.pass_context
@click.option("--lsp-spec-version", default=constants.LSP_SPEC_VERSION)
@click.option("--lsp-repo", default=constants.LSP_REPO)
@click.option("--lsp-committish", default=constants.LSP_COMMIT)
@click.option("--vlspn-repo", default=constants.VLSPN_REPO)
@click.option("--vlspn-committish", default=constants.VLSPN_COMMIT)
def generate(
    ctx: Context,
    lsp_spec_version: Text,
    lsp_repo: Text,
    lsp_committish: Text,
    vlspn_repo: Text,
    vlspn_committish: Text,
):
    """ generate JSON schema from markdown and typescript
    """
    from .generate import SpecGenerator

    lsp_spec = (
        CONVENTIONS.get(lsp_spec_version) or CONVENTIONS[constants.LSP_SPEC_VERSION]
    )

    assert lsp_spec, f"Couldn't find spec {lsp_spec_version}"
    assert ctx.obj.workdir, "Need a working directory"
    assert ctx.obj.output, "Need an output directory"
    assert ctx.obj.log, "Need a log"

    gen = SpecGenerator(
        log=ctx.obj.log,
        workdir=ctx.obj.workdir,
        output=ctx.obj.output,
        lsp_spec=lsp_spec,
        lsp_repo=lsp_repo,
        lsp_committish=lsp_committish,
        vlspn_repo=vlspn_repo,
        vlspn_committish=vlspn_committish,
    )
    sys.exit(gen.generate())


@lsp.command()
@click.pass_context
def validate(ctx: Context):
    """ test JSON schema by finding counterexamples
    """
    from .validate import SpecValidator

    assert ctx.obj.workdir and ctx.obj.workdir.is_dir(), "Need a working directory"
    assert ctx.obj.output and ctx.obj.output.is_dir(), "Need an output directory"
    assert ctx.obj.log, "Need a log"

    validator = SpecValidator(
        log=ctx.obj.log, workdir=ctx.obj.workdir, output=ctx.obj.output,
    )
    sys.exit(validator.validate())
