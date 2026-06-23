import os
import shutil
from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    @property
    def bin_suffix(self):
        if self.settings.os == "Windows":
            return ".exe"

        return ""

    @property
    def file_io(self):
        return {
            "c": {
                "compiler": "CC",
                "src": os.path.join(self.source_folder, "hello.c"),
                "bin": os.path.join(self.build_folder, f"hello_c{self.bin_suffix}"),
            },
            "cpp": {
                "compiler": "CXX",
                "src": os.path.join(self.source_folder, "hello.cpp"),
                "bin": os.path.join(self.build_folder, f"hello_cpp{self.bin_suffix}"),
            },
        }

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

        runenv = VirtualRunEnv(self)
        runenv.generate()

    def build(self):
        buildenv = VirtualBuildEnv(self)
        env = buildenv.vars()

        for language, files in self.file_io.items():
            self.output.info(f"Testing build using {language} compiler")

            compiler = env.get(files['compiler'])
            self.run(f"echo {files['compiler']}: {compiler}", env="buildenv")
            self.run(f"{compiler} --version", env="buildenv")
            self.run(f"{compiler} -dumpversion", env="buildenv")

            # Confirm files can be compiled
            self.run(
                f"{compiler} {files['src']} -o {files['bin']}",
                env="conanbuild",
            )
            self.output.info(f"Successfully built {files['bin']}")

    def test(self):
        def chmod_plus_x(name):
            if os.name == "posix":
                os.chmod(name, os.stat(name).st_mode | 0o111)

        for language, files in self.file_io.items():
            self.output.info(f"Testing application built using {language} compiler")
            if not cross_building(self):
                chmod_plus_x(f"{files['bin']}")

                if self.settings.os == "Linux":
                    if shutil.which("readelf"):
                        self.run(f"readelf -l {files['bin']}", env="conanrun")
                    else:
                        self.output.info(
                            "readelf is not on the PATH. Skipping readelf test."
                        )

                if self.settings.os == "Macos":
                    if shutil.which("otool"):
                        self.run(f"otool -L {files['bin']}", env="conanrun")
                    else:
                        self.output.info(
                            "otool is not on the PATH. Skipping otool test."
                        )

                self.run(f"{files['bin']}", env="conanrun")
