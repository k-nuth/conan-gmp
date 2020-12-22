import platform
from cpt.packager import ConanMultiPackager
import os
import cpuid
import copy

print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
print(cpuid.cpu_microarchitecture())
print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")

def handle_microarchs(opt_name, microarchs, filtered_builds, settings, options, env_vars, build_requires):
    print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
    print(microarchs)
    print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
    microarchs = list(set(microarchs))
    print(microarchs)
    print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")

    for ma in microarchs:
        opts_copy = copy.deepcopy(options)
        opts_copy[opt_name] = ma
        filtered_builds.append([settings, opts_copy, env_vars, build_requires])

if __name__ == "__main__":
    builder = ConanMultiPackager(username="kth", channel="stable"
                                 , remotes="https://api.bintray.com/conan/k-nuth/kth")
    builder.add_common_builds(shared_option_name="gmp:shared", pure_c=True)
    builder.password = os.getenv("CONAN_PASSWORD")

    print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
    print(len(builder.items))
    print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")

    filtered_builds = []
    # for settings, options, env_vars, build_requires in builder.builds:
    for settings, options, env_vars, build_requires, reference in builder.items:
        if settings["build_type"] == "Release" \
                and settings["arch"] == "x86_64" \
                and not ("gmp:shared" in options and options["gmp:shared"]):
            
        #     marchs = ["x86_64", ''.join(cpuid.cpu_microarchitecture()), "haswell", "skylake", "ivybridge", "sandybridge"]
            marchs = ["x86_64", ''.join(cpuid.cpu_microarchitecture()), "haswell", "skylake"]
            handle_microarchs("gmp:microarchitecture", marchs, filtered_builds, settings, options, env_vars, build_requires)

    builder.builds = filtered_builds

    builder.run()
