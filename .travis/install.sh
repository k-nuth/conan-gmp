#!/bin/bash

set -e
set -x

if [[ "$(uname -s)" == 'Darwin' ]]; then
    brew update || brew update
    brew outdated pyenv || brew upgrade pyenv
    brew install pyenv-virtualenv
    brew install cmake || true

    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi

    pyenv install 3.7.1
    pyenv virtualenv  3.7.1 conan
    pyenv rehash
    pyenv activate conan
fi

pip install conan --upgrade
pip install conan_package_tools

# python -c "exec(\"import cpuid\\nprint(cpuid.cpu_microarchitecture())\")" || true
pip install cpuid --upgrade
# python -c "exec(\"import cpuid\\nprint(cpuid.cpu_microarchitecture())\")" || true

conan user

if [[ "$(uname -s)" == 'Darwin' ]]; then
    conan install m4/1.4.18@ --build=m4
fi
