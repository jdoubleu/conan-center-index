from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.0.9"

class ClangConan(ConanFile):
    name = "clang"
    description = "C/C++ compiler from the LLVM project"
    license = "Apache-2.0"
    url = "https://github.com/llvm/llvm-project/tree/main/clang"
    homepage = "https://clang.llvm.org/get_started.html"
    topics = ("c", "c++", "compiler", "llvm")
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "targets": ["ANY"],
        "lldb": [True, False],
        "lld": [True, False],
        "libcxx": [True, False],
    }
    options_description = {
        "targets": "Platforms that Clang should support (available targets can bee seen here https://llvm.org/docs/CMake.html#llvm-related-variables)",
        "lldb": "Build and provide the LLDB debugger as well",
        "lld": "Build and provide the LLD linker as well",
        "libcxx": "Build libc++ and provide it"
    }
    default_options = {
        "targets": "X86;AArch64;ARM;RISCV",
        "lldb": True,
        "lld": False,
        "libcxx": False,
    }

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        check_min_cppstd(self, 17)

        # TODO: check targets?

    def layout(self):
        cmake_layout(self, src_folder="llvm")
        self.no_copy_source = True

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination="..", strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.cache_variables["LLVM_ENABLE_PROJECTS"] = "clang"
        if self.options.lldb:
            tc.cache_variables["LLVM_ENABLE_PROJECTS"] += ";lldb"
        if self.options.lld:
            tc.cache_variables["LLVM_ENABLE_PROJECTS"] += ";lld"

        tc.cache_variables["LLVM_TARGETS_TO_BUILD"] = self.options.targets

        if self.options.libcxx:
            tc.cache_variables["LLVM_ENABLE_RUNTIMES"] = "libcxx;libcxxabi;libunwind"

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "libexec"))
        rmdir(self, os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")

        # TODO: Windows clang-cl?
        cc = os.path.join(bindir, f"clang")
        self.output.info("Creating CC env var with: " + cc)
        self.buildenv_info.define("CC", cc)

        cxx = os.path.join(bindir, f"clang++")
        self.output.info("Creating CXX env var with: " + cxx)
        self.buildenv_info.define("CXX", cxx)

        ar = os.path.join(bindir, f"llvm-ar")
        self.output.info("Creating AR env var with: " + ar)
        self.buildenv_info.define("AR", ar)

        ranlib = os.path.join(bindir, f"llvm-ranlib")
        self.output.info("Creating RANLIB env var with: " + ranlib)
        self.buildenv_info.define("RANLIB", ranlib)

        if self.options.lld:
            ld = os.path.join(bindir, f"llvm-lld")
            self.output.info("Creating LD env var with: " + ld)
            self.buildenv_info.define("LD", ld)

        # TODO: libcxx
