#!/bin/bash

set -e
set -x

if [[ "$(uname -s)" == 'Darwin' ]]; then
    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi
    pyenv activate conan
fi

python -c "exec(\"import cpuid\\nprint(cpuid.cpu_microarchitecture())\")" || true

python build.py
