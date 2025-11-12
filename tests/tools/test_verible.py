import pytest
from pathlib import Path
from siliconcompiler import Flowgraph, Project
from siliconcompiler.tools.verible import lint


@pytest.mark.eda
@pytest.mark.quick
@pytest.mark.timeout(300)
def test_verible_lint(gcd_design):
    data_dir = Path(__file__).parent / "data"
    proj = Project(gcd_design)
    proj.add_fileset("rtl")
    proj.set("option", "nodisplay", True)
    proj.set("option", "clean", True)
    proj.set("option", "jobname", "test_verible_lint")

    flow = Flowgraph("testflow")
    flow.node("lint", lint.VeribleLintTask())
    proj.set_flow(flow)

    lint.VeribleLintTask().find_task(proj).set(
        "var",
        "waivers",
        [data_dir / "verible/waivers.txt"],
    )

    lint.VeribleLintTask().find_task(proj).set(
        "var",
        "rules",
        [data_dir / "verible/rules.txt"],
    )

    proj.run()


@pytest.mark.eda
@pytest.mark.quick
@pytest.mark.timeout(300)
def test_verible_lint_slurm(gcd_design):
    data_dir = Path(__file__).parent / "data"
    proj = Project(gcd_design)
    proj.add_fileset("rtl")
    proj.set("option", "nodisplay", True)
    proj.set("option", "clean", True)
    proj.set("option", "jobname", "test_verible_lint_slurm")

    proj.set("option", "scheduler", "name", "slurm")

    flow = Flowgraph("testflow")
    flow.node("lint", lint.VeribleLintTask())
    proj.set_flow(flow)

    lint.VeribleLintTask().find_task(proj).set(
        "var",
        "waivers",
        [data_dir / "verible/waivers.txt"],
    )

    lint.VeribleLintTask().find_task(proj).set(
        "var",
        "rules",
        [data_dir / "verible/rules.txt"],
    )

    proj.run()



if __name__ == "__main__":
    pytest.main(["-v", __file__ + "::test_verible_lint"])
