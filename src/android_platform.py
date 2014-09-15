from platform import Platform, Toolchain
from subprocess import call
import amigo_config
import os


class AndroidPlatform(Platform):
    def __init__(self, name, arch, ndk_path, sdk_version, toolchain_version, toolchain_install_path):
        super(AndroidPlatform, self).__init__(name, arch, ndk_path)
        self.__sdk_version = sdk_version
        self.__toolchain_version = toolchain_version
        self.__toolchain_install_path = toolchain_install_path
        self.__toolchain_generated = False

        toolchain_bin = os.path.join(toolchain_install_path, "bin/" + self.name())
        self._set_default_flags('CC', toolchain_bin + "-" + self.default_flags('CC'))
        self._set_default_flags('CXX', toolchain_bin + "-" + self.default_flags('CXX'))
        self._set_default_flags('LD', toolchain_bin + "-ld")
        self._set_default_flags('CPP', toolchain_bin + "-cpp")
        self._set_default_flags('AR', toolchain_bin + "-ar")
        self._set_default_flags('AS', toolchain_bin + "-as")
        self._set_default_flags('NM', toolchain_bin + "-nm")
        self._set_default_flags('STRIP', toolchain_bin + "-strip")
        self._set_default_flags('CXXCPP', toolchain_bin + "-cpp")
        self._set_default_flags('RANLIB', toolchain_bin + "-ranlib")

        self.append_default_flags(Platform.CONFIG_FLAGS,
                                  " --host=" + arch + "-android-linux" +
                                  " --target=" + self.name())
        self.append_default_flags('LDFLAGS',
                                  " -fPIC -Wl," +
                                  "-rpath-link=" + self.sysroot() + "/usr/lib" +
                                  " -L" + self.sysroot() + "/usr/lib -L" + self.gcc_libs())
        self.append_default_flags('CFLAGS', " -pipe -isysroot " + self.sysroot())
        self.append_default_flags('CXXFLAGS', " -pipe -isysroot " + self.sysroot())

    def configure(self, install_dir, env_vars=None, configure="", deps=None):
        if not self.__toolchain_generated:
            self.__generate_toolchain()
        super(AndroidPlatform, self).configure(install_dir, env_vars, configure, deps)

    def sdk_version(self):
        return self.__sdk_version

    def sysroot(self):
        return os.path.join(self.__toolchain_install_path, "sysroot")

    def gcc_libs(self):
        return os.path.join(self.__toolchain_install_path, "lib/gcc/" + self.name() + "/" + self.__toolchain_version)

    def __generate_toolchain(self):
        builder = os.path.join(self.sdk_path(), "build/tools/make-standalone-toolchain.sh")
        platform = '--platform=android-' + self.sdk_version()
        install_dir = "--install-dir=" + self.__toolchain_install_path
        toolchain = "--toolchain=" + self.name() + "-" + self.__toolchain_version
        system = "--system=" + self.env().system()
        llvm = ''
        if 'clang' in self.default_flags('CC'):
            llvm = '--llvm_version=3.4'
        cxx11 = ''
        if amigo_config.CXX11:
            cxx11 = '--stl=libc++'
        call_str = builder + " " + platform + " " + install_dir + " " + toolchain + " " + system + " " + llvm + " " + cxx11
        if amigo_config.VERBOSE:
            print call_str
        call([call_str], shell=True)
        self.__toolchain_generated = True
