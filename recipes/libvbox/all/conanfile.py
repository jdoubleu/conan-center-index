import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import apply_conandata_patches, get, rmdir


# TODO: Linux XPCOM
class LibVBoxConan(ConanFile):
    name = "libvbox"
    license = "LGPL-2.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zrax/libvbox"
    description = "C++ wrapper for VirtualBox COM APIs"
    topics = ("libvbox", "virtualbox", "virtualboxsdk", "COM")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
    }

    generators = "CMakeDeps"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def source(self):
        get(self, **self.conan_data["vbox_sdk"][self.version], destination="_sdk", strip_root=True)
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        # CMAKE_FIND_PACKAGE_PREFER_CONFIG interferes with VirtualBoxSDK_DIR
        tc.blocks.remove("find_paths")
        tc.variables["VirtualBoxSDK_DIR"] = os.path.join(self.source_folder, "_sdk").replace("\\", "/")
        tc.variables["VirtualBoxSDK_VERSION"] = self.version
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["vbox"]
        self.cpp_info.set_property("cmake_file_name", "libvbox")
        self.cpp_info.set_property("cmake_target_name", "libvbox::libvbox")

        if self.settings.os == 'Windows':
            self.cpp_info.system_libs.extend(['Uuid', 'Ole32', 'OleAut32'])
        if self.settings.os == 'Linux':
            self.cpp_info.system_libs.extend(['dl', 'pthread'])
