[![Build Status](https://travis-ci.org/k-nuth/conan-gmp.svg?branch=master)](https://travis-ci.org/k-nuth/conan-gmp) [![Appveyor Status](https://ci.appveyor.com/api/projects/status/github/k-nuth/conan-gmp?branch=master&svg=true)](https://ci.appveyor.com/project/k-nuth/conan-gmp?branch=master) [![Build Status](https://api.cirrus-ci.com/github/k-nuth/conan-gmp.svg?branch=master)](https://cirrus-ci.com/github/k-nuth/conan-gmp)

# conan-gmp

[Conan.io](https://conan.io) package for GMP library. https://gmplib.org/

The packages generated with this **conanfile** can be found in [conan.io](https://conan.io/source/gmp/6.2.1/k-nuth/k-nuth).

## Build packages

Download conan client from [Conan.io](https://conan.io) and run:

    $ python build.py
    
## Upload packages to server

    $ conan upload gmp/6.2.1@kth/stable --all
    
## Reuse the packages

### Basic setup

    $ conan install gmp/6.2.1@kth/stable
    
### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*
    
    [requires]
    gmp/6.2.1@kth/stable

    [options]
    gmp:shared=false # true
    
    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:</small></span>

    conan install . 

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.
