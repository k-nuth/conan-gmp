import platform
from conan.packager import ConanMultiPackager
import os

if __name__ == "__main__":
    builder = ConanMultiPackager(username="bitprim", channel="stable",
                                 remotes="https://api.bintray.com/conan/bitprim/bitprim")
    builder.add_common_builds(shared_option_name="gmp:shared", pure_c=True)
    builder.password = os.getenv("CONAN_PASSWORD")

    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        if settings["build_type"] == "Release" \
                and settings["arch"] == "x86_64" \
                and not ("gmp:shared" in options and options["gmp:shared"]):
            filtered_builds.append([settings, options, env_vars, build_requires])
    builder.builds = filtered_builds

    builder.run()
