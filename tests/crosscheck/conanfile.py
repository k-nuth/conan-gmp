from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import io
import os


class CrosscheckConan(ConanFile):
    """Runs a fixed sequence of integer operations against the package and
    compares the digest of the results with expected.txt, which is the same
    for every target. Under Emscripten the program runs on Node.js."""
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        binary = os.path.join(self.cpp.build.bindirs[0], "crosscheck")
        if self.settings.os == "Emscripten":
            command = f'node "{binary}.js"'
        elif can_run(self):
            command = f'"{binary}"'
        else:
            self.output.warning("The digest was not checked: this target cannot run here.")
            return
        output = io.StringIO()
        self.run(command, stdout=output, env="conanrun")
        digest = output.getvalue().strip().splitlines()[-1]
        with open(os.path.join(self.source_folder, "expected.txt")) as expected_file:
            expected = expected_file.read().strip()
        if digest != expected:
            raise ConanException(f"GMP computed a different result: digest {digest}, expected {expected}")
        self.output.info(f"Digest {digest} matches.")
