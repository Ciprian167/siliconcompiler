from siliconcompiler import sc_open
from siliconcompiler import Task


class VeribleLintTask(Task):
    def __init__(self):
        super().__init__()

        self.add_parameter(
            "waivers",
            "[file]",
            "A list of waiver files.",
        )

        self.add_parameter(
            "rules",
            "[file]",
            "A list of lint rule files.",
        )

    def tool(self):
        return "verible"

    def task(self):
        return "lint"

    def setup(self):
        super().setup()

        self.set_exe("verible-verilog-lint", clobber=True)
        self.set_threads(1, clobber=True)
        self.add_regex("warnings", r"warning: ", clobber=True)
        self.add_regex("errors", r"error: ", clobber=True)

        self.add_required_key("option", "design")
        self.add_required_key("option", "fileset")
        if self.project.get("option", "alias"):
            self.add_required_key("option", "alias")

        for lib, fileset in self.project.get_filesets():
            if lib.has_idir(fileset):
                self.add_required_key(lib, "fileset", fileset, "idir")
            if lib.get("fileset", fileset, "define"):
                self.add_required_key(lib, "fileset", fileset, "define")
            if lib.has_file(fileset=fileset, filetype="systemverilog"):
                self.add_required_key(lib, "fileset", fileset, "file", "systemverilog")
            if lib.has_file(fileset=fileset, filetype="verilog"):
                self.add_required_key(lib, "fileset", fileset, "file", "verilog")

        if self.get("var", "waivers"):
            self.add_required_key("var", "waivers")

        if self.get("var", "rules"):
            self.add_required_key("var", "rules")

    def runtime_options(self):
        options = super().runtime_options()
        options.extend(
            [
                "--lint_fatal",
                "--parse_fatal",
            ]
        )

        rules = self.find_files("var", "rules")
        if rules:
            options.extend(["--rules_config", ",".join(rules)])

        waivers = self.find_files("var", "waivers")
        if waivers:
            options.extend(["--waiver_files", ",".join(waivers)])

        for lib, fileset in self.project.get_filesets():
            for value in lib.get_file(fileset=fileset, filetype="systemverilog"):
                options.append(value)
            for value in lib.get_file(fileset=fileset, filetype="verilog"):
                options.append(value)

        return options

    def post_process(self):
        with sc_open(f"{self.step}.log") as log:
            line_count = sum(1 for _ in log.readlines())
            self.record_metric("errors", line_count, f"{self.step}.log")
