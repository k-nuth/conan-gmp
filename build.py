import platform
from conan.packager import ConanMultiPackager
import os
import cpuid
import copy

if __name__ == "__main__":

    print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
    print(cpuid.cpu_vendor())
    print(cpuid.cpu_name())
    print(cpuid.cpu_microarchitecture())
    print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')

    builder = ConanMultiPackager(username="bitprim", channel="stable",
                                 remotes="https://api.bintray.com/conan/bitprim/bitprim")
    builder.add_common_builds(shared_option_name="gmp:shared", pure_c=True)
    builder.password = os.getenv("CONAN_PASSWORD")

    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        if settings["build_type"] == "Release" \
                and settings["arch"] == "x86_64" \
                and not ("gmp:shared" in options and options["gmp:shared"]):
            
            opt1 = copy.deepcopy(options)
            opt2 = copy.deepcopy(options)

            opt1["gmp:microarchitecture"] = "x86_64"
            opt1["gmp:microarchitecture"] = ''.join(cpuid.cpu_microarchitecture())

            print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
            print(options)
            print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
            print(opt1)
            print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
            print(opt2)

            filtered_builds.append([settings, opt1, env_vars, build_requires])
            filtered_builds.append([settings, opt2, env_vars, build_requires])

    builder.builds = filtered_builds

    builder.run()
