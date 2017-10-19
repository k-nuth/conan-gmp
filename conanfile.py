from conans import ConanFile
import os #, shutil
from conans.tools import download, unzip #, replace_in_file, check_md5
# from conans import CMake
# from conans import tools
import cpuid

class BitprimGmpConan(ConanFile):
    name = "gmp"
    version = "6.1.2"
    url = "https://github.com/bitprim/bitprim-conan-gmp"
    ZIP_FOLDER_NAME = "gmp-%s" % version
    
    # generators = "cmake"
    generators = "txt"

    settings =  "os", "compiler", "arch", "build_type"
    build_policy = "missing"

    options = {"shared": [True, False],
               "disable_assembly": [True, False],
               "enable_fat": [True, False],
               "enable_cxx": [True, False],
               "disable-fft": [True, False],
               "enable-assert": [True, False],
               "microarchitecture": "ANY" #["x86_64", "haswell", "ivybridge", "sandybridge", "bulldozer", ...]
            #    "host": "ANY" #["auto", "generic", "haswell", "ivybridge", "sandybridge", ...]
              }

    default_options = "shared=False",  \
                      "disable_assembly=False",  \
                      "enable_fat=False", \
                      "enable_cxx=True",  \
                      "disable-fft=False",  \
                      "enable-assert=False", \
                      "microarchitecture=_DUMMY_"
                    #   "host=generic"

                    #   "microarchitecture=x86_64"
    requires = "m4/1.4.18@bitprim/stable"

    # def config_options(self):
    #     self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-* def config_options(self):")
    #     # print(self.options)
    #     # self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-*")
    #     # print(self.default_options)
    #     # self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-*")
    #     self.output.warn("*** microarchitecture: %s" % (self.options.microarchitecture,))
    #     # del self.options.microarchitecture
    #     # self.output.warn("*** microarchitecture: %s" % (self.options.microarchitecture,))
    #     print(cpuid.cpu_microarchitecture())

    def configure(self):
        self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-* def configure(self):")
        # print(self.options)
        # self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-*")
        # print(self.default_options)
        # self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-*")
        self.output.warn("*** microarchitecture: %s" % (self.options.microarchitecture,))

        if self.options.microarchitecture == "_DUMMY_":
            self.options.microarchitecture = "%s%s" % cpuid.cpu_microarchitecture()

        self.output.warn("*** microarchitecture: %s" % (self.options.microarchitecture,))

    def source(self):
        self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-* def source(self):")
        print(self.options)
        self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-*")
        print(self.default_options)
        self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-*")
        self.output.warn("*** microarchitecture: %s" % (self.options.microarchitecture,))

        # https://gmplib.org/download/gmp/gmp-6.1.2.tar.bz2
        zip_name = "gmp-%s.tar.bz2" % self.version
        download("http://gmplib.org/download/gmp/%s" % zip_name, zip_name)
        # download("http://gnu.uberglobalmirror.com/gmp/%s" % zip_name, zip_name)

        # check_md5(zip_name, "4c175f86e11eb32d8bf9872ca3a8e11d") #TODO
        unzip(zip_name)
        os.unlink(zip_name)

    # def config(self):
    #     pass
    #     # del self.settings.compiler.libcxx



    def _generic_env_configure_vars(self, verbose=False):
        """Reusable in any lib with configure!!"""
        command = ""
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            libs = 'LIBS="%s"' % " ".join(["-l%s" % lib for lib in self.deps_cpp_info.libs])
            ldflags = 'LDFLAGS="%s"' % " ".join(["-L%s" % lib for lib in self.deps_cpp_info.lib_paths])
            archflag = "-m32" if self.settings.arch == "x86" else ""
            cflags = 'CFLAGS="-fPIC %s %s"' % (archflag, " ".join(self.deps_cpp_info.cflags))
            cpp_flags = 'CPPFLAGS="-fPIC %s %s"' % (archflag, " ".join(self.deps_cpp_info.cppflags))
            command = "env %s %s %s %s" % (libs, ldflags, cflags, cpp_flags)
        elif self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            cl_args = " ".join(['/I"%s"' % lib for lib in self.deps_cpp_info.include_paths])
            lib_paths= ";".join(['"%s"' % lib for lib in self.deps_cpp_info.lib_paths])
            command = "SET LIB=%s;%%LIB%% && SET CL=%s" % (lib_paths, cl_args)
            if verbose:
                command += " && SET LINK=/VERBOSE"
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            libs = 'LIBS="%s"' % " ".join(["-l%s" % lib for lib in self.deps_cpp_info.libs])
            ldflags = 'LDFLAGS="%s"' % " ".join(["-L%s" % lib for lib in self.deps_cpp_info.lib_paths])
            archflag = "-m32" if self.settings.arch == "x86" else ""
            cflags = 'CFLAGS="-fPIC %s %s"' % (archflag, " ".join(self.deps_cpp_info.cflags))
            cpp_flags = 'CPPFLAGS="-fPIC %s %s"' % (archflag, " ".join(self.deps_cpp_info.cppflags))
            command = "env %s %s %s %s" % (libs, ldflags, cflags, cpp_flags)

        return command

    def _determine_host(self):
        if self.settings.os == "Macos":
            # nehalem-apple-darwin15.6.0
            os_part = 'apple-darwin'
        elif self.settings.os == "Linux":
            os_part = 'pc-linux-gnu'

        complete_host = "%s-%s" % (self.options.microarchitecture, os_part)
        host_string = " --build=%s --host=%s" % (complete_host, complete_host)
        return host_string


    # def determine_microarch(self):
    #     # precondition: self.options.host != 'auto'
        
    #     if self.options.host == 'generic':
    #         return (True, 'x86_64')
    #     elif self.options.host == 'haswell':
    #         return (True, self.options.host)
    #     elif self.options.host == 'ivybridge':
    #         return (True, self.options.host)
    #     elif self.options.host == 'sandybridge':
    #         return (True, self.options.host)

    #     return (False, None)

    # def determine_host(self):
    #     if self.options.host == 'auto':
    #         host_string = ""
    #     else:
    #         if self.settings.os == "Macos":
    #             # nehalem-apple-darwin15.6.0
    #             os_part = 'apple-darwin'
    #         elif self.settings.os == "Linux":
    #             os_part = 'pc-linux-gnu'

    #         predef, microarch_part = self.determine_microarch()

    #         if not predef:
    #             complete_host = self.options.host
    #             # microarch_part = " --build=%s --host=%s" % (self.options.host, self.options.host)
    #         else:
    #             complete_host = "%s-%s" % (microarch_part, os_part)

    #         host_string = " --build=%s --host=%s" % (complete_host, complete_host)

    #     return host_string


    #     # if self.options.host == 'generic':
    #     #     if self.settings.os == "Macos":
    #     #         # nehalem-apple-darwin15.6.0
    #     #         host_string = " --build=x86_64-apple-darwin --host=x86_64-apple-darwin"
    #     #     elif self.settings.os == "Linux":
    #     #         host_string = " --build=x86_64-pc-linux-gnu --host=x86_64-pc-linux-gnu"
    #     # elif self.options.host == 'auto':
    #     #     host_string = ""
    #     # elif self.options.host == 'haswell':
    #     #     host_string = " --build=haswell-pc-linux-gnu --host=haswell-pc-linux-gnu"
    #     # elif self.options.host == 'ivy':
    #     #     host_string = " --build=ivybridge-pc-linux-gnu --host=ivybridge-pc-linux-gnu"
    #     # elif self.options.host == 'sandy':
    #     #     host_string = " --build=sandybridge-pc-linux-gnu --host=sandybridge-pc-linux-gnu"
    #     # else:
    #     #     host_string = " --build=%s --host=%s" % (self.options.host, self.options.host)

    def build(self):
        self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-* def build(self):")
        print(self.options)
        self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-*")
        print(self.default_options)
        self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-*")
        self.output.warn("*** microarchitecture: %s" % (self.options.microarchitecture,))

        old_path = os.environ['PATH']
        os.environ['PATH'] = os.environ['PATH'] + ':' + os.getcwd()

        config_options_string = ""

        for option_name in self.options.values.fields:
            if option_name != 'microarchitecture':
                activated = getattr(self.options, option_name)
                if activated:
                    self.output.info("Activated option! %s" % option_name)
                    config_options_string += " --%s" % option_name.replace("_", "-")

        self.output.warn("*** Detected OS: %s" % (self.settings.os))

        if self.settings.os == "Macos":
            config_options_string += " --with-pic"


        host_string = self._determine_host()
        self.output.warn(host_string)

        disable_assembly = "--disable-assembly" if self.settings.arch == "x86" else ""

        # ./configure --build=x86_64-pc-linux-gnu --host=x86_64-pc-linux-gnu --program-prefix= --disable-dependency-tracking --enable-cxx
        # WARN: cd gmp-6.1.2 && env LIBS="" LDFLAGS="" CFLAGS="-fPIC  " CPPFLAGS="-fPIC  " ./configure --with-pic --enable-static --enable-shared  --enable-cxx
        # WARN: cd gmp-6.1.2 && env LIBS="" LDFLAGS="" CFLAGS="-fPIC  " CPPFLAGS="-fPIC  " ./configure  --build=x86_64-pc-linux-gnu --host=x86_64-pc-linux-gnu --with-pic --enable-static --enable-shared  --enable-cxx --host 

        configure_command = "cd %s && %s ./configure %s --with-pic --enable-static --enable-shared %s %s" % (self.ZIP_FOLDER_NAME, self._generic_env_configure_vars(), host_string, config_options_string, disable_assembly)
        self.output.warn(configure_command)
        self.run(configure_command)

        # if self.settings.os == "Linux" or self.settings.os == "Macos":
        if self.settings.os != "Windows":
            self.run("cd %s && make" % self.ZIP_FOLDER_NAME)
        else:
            # self.run("dir C:\MinGw\bin\")
            self.run("cd %s && C:/MinGw/bin/make" % self.ZIP_FOLDER_NAME)

        os.environ['PATH'] = old_path

    def imports(self):
        self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-* def imports(self):")
        self.copy("m4", dst=".", src="bin")

    def package(self):
        self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-* def package(self):")
        self.copy("*.h", "include", "%s" % (self.ZIP_FOLDER_NAME), keep_path=True)
        if self.options.shared:
            self.copy(pattern="*.so*", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            self.copy(pattern="*.dll*", dst="bin", src=self.ZIP_FOLDER_NAME, keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", src="%s" % self.ZIP_FOLDER_NAME, keep_path=False)

        self.copy(pattern="*.lib", dst="lib", src="%s" % self.ZIP_FOLDER_NAME, keep_path=False)
        
    def package_info(self):
        self.output.warn("-*-*-*-*-*-*-*-*-*-*-*-* def package_info(self):")
        self.cpp_info.libs = ['gmp']


