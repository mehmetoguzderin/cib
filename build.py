#!/usr/bin/env python3

import argparse, os, subprocess, sys

llvmBuildType = 'Release'
llvmNo86BuildType = 'Release'
llvmBrowserBuildType = 'Release'
fastcompBuildType = 'RelWithDebInfo'
binaryenBuildType = 'RelWithDebInfo'
optimizerBuildType = 'RelWithDebInfo'
appBuildType = 'Debug'

root = os.path.dirname(os.path.abspath(__file__)) + '/'
cmakeInstall = root + 'install/cmake/'
llvmBuild = root + 'build/llvm-' + llvmBuildType + '/'
llvmInstall = root + 'install/llvm-' + llvmBuildType + '/'
llvmNo86Build = root + 'build/llvm-no86-' + llvmNo86BuildType + '/'
llvmNo86Install = root + 'install/llvm-no86-' + llvmNo86BuildType + '/'
llvmBrowserBuild = root + 'build/llvm-browser-' + llvmBrowserBuildType + '/'
llvmBrowserInstall = root + 'install/llvm-browser-' + llvmBrowserBuildType + '/'
fastcompBuild = root + 'build/fastcomp-' + fastcompBuildType + '/'
fastcompInstall = root + 'install/fastcomp-' + fastcompBuildType + '/'
binaryenBuild = root + 'build/binaryen-' + binaryenBuildType + '/'
binaryenInstall = root + 'install/binaryen-' + binaryenBuildType + '/'
wabtInstall = root + 'repos/wabt/bin/'
optimizerBuild = root + 'build/optimizer-' + optimizerBuildType + '/'
appsBrowserBuild = root + 'build/apps-browser-' + appBuildType + '/'

llvmBrowserTargets = [
    'clangAnalysis',
    'clangAST',
    'clangBasic',
    'clangCodeGen',
    'clangDriver',
    'clangEdit',
    'clangFormat',
    'clangFrontend',
    'clangLex',
    'clangParse',
    'clangRewrite',
    'clangSema',
    'clangSerialization',
    'clangToolingCore',
    'LLVMAnalysis',
    'LLVMAsmParser',
    'LLVMAsmPrinter',
    'LLVMBinaryFormat',
    'LLVMBitReader',
    'LLVMBitWriter',
    'LLVMCodeGen',
    'LLVMCore',
    'LLVMCoroutines',
    'LLVMCoverage',
    'LLVMDebugInfoCodeView',
    'LLVMGlobalISel',
    'LLVMInstCombine',
    'LLVMInstrumentation',
    'LLVMipo',
    'LLVMIRReader',
    'LLVMLinker',
    'LLVMLTO',
    'LLVMMC',
    'LLVMMCDisassembler',
    'LLVMMCParser',
    'LLVMObjCARCOpts',
    'LLVMObject',
    'LLVMOption',
    'LLVMPasses',
    'LLVMProfileData',
    'LLVMScalarOpts',
    'LLVMSelectionDAG',
    'LLVMSupport',
    'LLVMTarget',
    'LLVMTransformUtils',
    'LLVMVectorize',
    'LLVMWebAssemblyAsmPrinter',
    'LLVMWebAssemblyCodeGen',
    'LLVMWebAssemblyDesc',
    'LLVMWebAssemblyInfo',
]

cores = subprocess.check_output("grep 'processor' /proc/cpuinfo | wc -l", shell=True).decode('utf-8').strip()
parallel = '-j ' + cores

os.environ["PATH"] = os.pathsep.join([
    root + 'repos/emscripten',
    cmakeInstall + 'bin',
    llvmInstall + 'bin',
    wabtInstall,
    binaryenInstall + 'bin',
    os.environ["PATH"],
])
os.environ['BINARYEN'] = binaryenInstall
os.environ['EMSCRIPTEN_NATIVE_OPTIMIZER'] = optimizerBuild + 'optimizer'

def run(args):
    print('build.py:', args)
    if subprocess.call(args, shell=True):
        print('build.py: exiting because of error')
        sys.exit()

def getOutput(args):
    print('build.py:', args)
    result = subprocess.run(args, shell=True, stdout=subprocess.PIPE)
    if result.returncode:
        print('build.py: exiting because of error')
        sys.exit()
    print(result.stdout.decode("utf-8"), end='')
    return result.stdout

repos = [
    ('repos/llvm', 'git@github.com:tbfleming/cib-llvm.git', 'git@github.com:llvm-mirror/llvm.git', True, 'master', 'cib'),
    ('repos/llvm/tools/clang', 'git@github.com:tbfleming/cib-clang.git', 'git@github.com:llvm-mirror/clang.git', True, 'master', 'master'),
    ('repos/llvm/tools/lld', 'git@github.com:tbfleming/cib-lld.git', 'git@github.com:llvm-mirror/lld.git', True, 'master', 'master'),
    # ('repos/fastcomp', 'git@github.com:tbfleming/cib-emscripten-fastcomp.git', 'git@github.com:kripken/emscripten-fastcomp.git', True, 'incoming', 'incoming'),
    # ('repos/fastcomp/tools/clang', 'git@github.com:tbfleming/cib-emscripten-fastcomp-clang.git', 'git@github.com:kripken/emscripten-fastcomp-clang.git', True, 'incoming', 'incoming'),
    ('repos/emscripten', 'git@github.com:tbfleming/cib-emscripten.git', 'git@github.com:kripken/emscripten.git', True, 'incoming', 'cib'),
    ('repos/wabt', 'git@github.com:WebAssembly/wabt.git', 'git@github.com:WebAssembly/wabt.git', False, 'master', 'master'),
    ('repos/binaryen', 'git@github.com:tbfleming/cib-binaryen.git', 'git@github.com:WebAssembly/binaryen.git', True, 'master', 'cib'),
]

def clone():
    for (path, url, upstream, isPushable, upstreamBranch, branch) in repos:
        if os.path.isdir(path):
            continue
        dir = os.path.dirname(path)
        base = os.path.basename(path)
        run('mkdir -p ' + dir)
        run('cd ' + dir + ' && git clone ' + url + ' ' + base)
        run('cd ' + path + ' && git remote add upstream ' + upstream)
        run('cd ' + path + ' && git checkout ' + branch)

def status():
    for (path, url, upstream, isPushable, upstreamBranch, branch) in repos:
        print('****************')
        run('cd ' + path + ' && git status')
    print('****************')

def pull():
    for (path, url, upstream, isPushable, upstreamBranch, branch) in repos:
        if getOutput('cd ' + path + ' && git status --porcelain --untracked-files=no'):
            print('build.py: skip', path)
        else:
            run('cd ' + path + ' && git pull --no-edit')

def merge():
    for (path, url, upstream, isPushable, upstreamBranch, branch) in repos:
        if getOutput('cd ' + path + ' && git status --porcelain --untracked-files=no'):
            print('build.py: skip', path)
        else:
            run('cd ' + path + ' && git fetch upstream && git merge --no-edit upstream/' + upstreamBranch)

def push():
    for (path, url, upstream, isPushable, upstreamBranch, branch) in repos:
        if isPushable:
            if getOutput('cd ' + path + ' && git status --porcelain --untracked-files=no'):
                print('build.py: skip', path)
            else:
                run('cd ' + path + ' && git push')

def cmake():
    if not os.path.exists('download/cmake-3.10.1.tar.gz'):
        run('mkdir -p download')
        run('cd download && wget https://cmake.org/files/v3.10/cmake-3.10.1.tar.gz')
    if not os.path.exists('build/cmake-3.10.1'):
        run('mkdir -p build')
        run('cd build && tar xf ../download/cmake-3.10.1.tar.gz')
        run('cd build/cmake-3.10.1 && ./bootstrap --prefix=' + cmakeInstall + ' --parallel=' + cores)
        run('cd build/cmake-3.10.1 && make ' + parallel)
        run('cd build/cmake-3.10.1 && make install ' + parallel)

def llvm():
    if not os.path.isdir(llvmBuild):
        run('mkdir -p ' + llvmBuild)
        run('cd ' + llvmBuild + ' && time -p cmake -G "Ninja"' +
            ' -DCMAKE_INSTALL_PREFIX=' + llvmInstall +
            ' -DCMAKE_BUILD_TYPE=' + llvmBuildType +
            ' -DLLVM_TARGETS_TO_BUILD=X86' +
            ' -DLLVM_EXPERIMENTAL_TARGETS_TO_BUILD=WebAssembly' +
            ' ' + root + 'repos/llvm')
    run('cd ' + llvmBuild + ' && time -p ninja')
    if not os.path.isdir(llvmInstall):
        run('mkdir -p ' + llvmInstall)
        run('cd ' + llvmBuild + ' && time -p ninja ' + parallel + ' install')

def fastcomp():
    if not os.path.isdir(fastcompBuild):
        run('mkdir -p ' + fastcompBuild)
        run('cd ' + fastcompBuild + ' && time -p cmake -G "Ninja"' +
            ' -DCMAKE_INSTALL_PREFIX=' + fastcompInstall +
            ' -DCMAKE_BUILD_TYPE=' + fastcompBuildType +
            ' "-DLLVM_TARGETS_TO_BUILD=X86;JSBackend"' +
            ' -DLLVM_INCLUDE_EXAMPLES=OFF' +
            ' -DLLVM_INCLUDE_TESTS=OFF' +
            ' -DCLANG_INCLUDE_TESTS=OFF' +
            ' -DLLVM_ENABLE_ASSERTIONS=ON' +
            ' ' + root + 'repos/fastcomp')
    run('cd ' + fastcompBuild + ' && time -p ninja')
    if not os.path.isdir(fastcompInstall):
        run('mkdir -p ' + fastcompInstall)
        run('cd ' + fastcompBuild + ' && time -p ninja ' + parallel + ' install')

def llvmNo86():
    if not os.path.isdir(llvmNo86Build):
        run('mkdir -p ' + llvmNo86Build)
        run('cd ' + llvmNo86Build + ' && time -p cmake -G "Ninja"' +
            ' -DCMAKE_INSTALL_PREFIX=' + llvmNo86Install +
            ' -DCMAKE_BUILD_TYPE=' + llvmNo86BuildType +
            ' -DLLVM_TARGETS_TO_BUILD=' +
            ' -DLLVM_EXPERIMENTAL_TARGETS_TO_BUILD=WebAssembly' +
            ' ' + root + 'repos/llvm')
    run('cd ' + llvmNo86Build + ' && time -p ninja')
    if not os.path.isdir(llvmNo86Install):
        run('mkdir -p ' + llvmNo86Install)
        run('cd ' + llvmNo86Build + ' && time -p ninja ' + parallel + ' install')

def wabt():
    if not os.path.isdir(wabtInstall):
        run('cd repos/wabt && time make clang-release-no-tests ' + parallel)

def binaryen():
    if not os.path.isdir(binaryenBuild):
        run('mkdir -p ' + binaryenBuild)
        run('cd ' + binaryenBuild + ' && time -p cmake -G "Ninja"' +
            ' -DCMAKE_INSTALL_PREFIX=' + binaryenInstall +
            ' -DCMAKE_BUILD_TYPE=' + binaryenBuildType +
            ' ' + root + 'repos/binaryen')
    run('cd ' + binaryenBuild + ' && time -p ninja')
    if not os.path.isdir(binaryenInstall):
        run('mkdir -p ' + binaryenInstall)
        run('cd ' + binaryenBuild + ' && time -p ninja ' + parallel + ' install')

def emscripten():
    configFile = os.path.expanduser('~') + '/.emscripten'
    if not os.path.isdir(optimizerBuild):
        run('mkdir -p ' + optimizerBuild)
        run('cd ' + optimizerBuild + ' && time -p cmake -G "Ninja"' +
            ' -DCMAKE_BUILD_TYPE=' + optimizerBuildType +
            ' ' + root + 'repos/emscripten/tools/optimizer')
    run('cd ' + optimizerBuild + ' && time -p ninja ' + parallel)
    if not os.path.exists(configFile):
        run('em++')
        with open(configFile, "a") as file:
            file.write("\nBINARYEN_ROOT='" + binaryenInstall + "'\n")
        run('mkdir -p build/dummy')
        run('cd build/dummy && em++ ../../src/say-hello.cpp -o say-hello.html')

def llvmBrowser():
    if not os.path.isdir(llvmBrowserBuild):
        run('mkdir -p ' + llvmBrowserBuild)
        run('cd ' + llvmBrowserBuild + ' && ' +
            'time -p emcmake cmake -G "Ninja"' +
            ' -DCMAKE_INSTALL_PREFIX=' + llvmBrowserInstall + '' +
            ' -DCMAKE_BUILD_TYPE=' + llvmBrowserBuildType +
            ' -DLLVM_TARGETS_TO_BUILD=' +
            ' -DLLVM_EXPERIMENTAL_TARGETS_TO_BUILD=WebAssembly' +
            ' -DLLVM_BUILD_TOOLS=OFF' +
            ' -DLLVM_ENABLE_THREADS=OFF' +
            ' -DLLVM_BUILD_LLVM_DYLIB=OFF' +
            ' -DLLVM_INCLUDE_TESTS=OFF' +
            ' -DLLVM_TABLEGEN=' + llvmInstall + 'bin/llvm-tblgen' +
            ' -DCLANG_TABLEGEN=' + llvmBuild + 'bin/clang-tblgen' +
            ' ' + root + 'repos/llvm')
    run('cd ' + llvmBrowserBuild + ' && time -p ninja ' + parallel + ' ' + ' '.join(llvmBrowserTargets))

def dist():
    if not os.path.exists('download/monaco-editor-0.10.1.tgz'):
        run('mkdir -p download')
        run('cd download && wget https://registry.npmjs.org/monaco-editor/-/monaco-editor-0.10.1.tgz')
    if not os.path.exists('download/monaco-editor-0.10.1'):
        run('mkdir -p download/monaco-editor-0.10.1')
        run('cd download/monaco-editor-0.10.1 && tar -xf ../monaco-editor-0.10.1.tgz')
    run('mkdir -p dist/monaco-editor')
    run('cp -au download/monaco-editor-0.10.1/package/LICENSE dist/monaco-editor')
    run('cp -au download/monaco-editor-0.10.1/package/README.md dist/monaco-editor')
    run('cp -au download/monaco-editor-0.10.1/package/ThirdPartyNotices.txt dist/monaco-editor')
    run('cp -auv download/monaco-editor-0.10.1/package/min dist/monaco-editor')
    if not os.path.exists('download/split.js-1.3.5.tgz'):
        run('cd download && wget https://registry.npmjs.org/split.js/-/split.js-1.3.5.tgz')
    if not os.path.exists('download/Split.js-1.3.5'):
        run('mkdir -p download/Split.js-1.3.5')
        run('cd download/Split.js-1.3.5 && tar -xf ../split.js-1.3.5.tgz')
    run('mkdir -p dist/split.js')
    run('cp -au download/Split.js-1.3.5/package/LICENSE.txt dist/split.js')
    run('cp -au download/Split.js-1.3.5/package/AUTHORS.md dist/split.js')
    run('cp -au download/Split.js-1.3.5/package/README.md dist/split.js')
    run('cp -au download/Split.js-1.3.5/package/split.min.js dist/split.js')
    run('cp -auv download/Split.js-1.3.5/package/grips dist/split.js')
    run('cp -au src/clang.html src/process.js src/process-manager.js src/process-clang-format.js dist')
    run('cp -au src/process-clang.js src/process-runtime.js dist')

def app(name, prepBuildDir=None):
    if not os.path.isdir(appsBrowserBuild):
        run('mkdir -p ' + appsBrowserBuild)
        run('cd ' + appsBrowserBuild + ' &&' +
            ' emcmake cmake -G "Ninja"' +
            ' -DCMAKE_BUILD_TYPE=' + appBuildType +
            ' -DLLVM_BUILD=' + llvmBrowserBuild +
            ' -DEMSCRIPTEN=on'
            ' ../../src')
    if prepBuildDir:
        prepBuildDir()
    run('cd ' + appsBrowserBuild + ' && time -p ninja ' + name)
    if not os.path.isdir('dist'):
        run('mkdir -p dist')

def appClangFormat():
    app('clang-format')
    run('cp -au ' + appsBrowserBuild + 'clang-format.js ' + appsBrowserBuild + 'clang-format.wasm dist')

def appClang():
    def prepBuildDir():
        run('mkdir -p ' + appsBrowserBuild + 'usr/lib/libcxxabi ' + appsBrowserBuild + 'usr/lib/libc/musl/arch/emscripten')
        run('cp -auv repos/emscripten/system/include ' + appsBrowserBuild + 'usr')
        run('cp -auv repos/emscripten/system/lib/libcxxabi/include ' + appsBrowserBuild + 'usr/lib/libcxxabi')
        run('cp -auv repos/emscripten/system/lib/libc/musl/arch/emscripten ' + appsBrowserBuild + 'usr/lib/libc/musl/arch')
    app('clang', prepBuildDir)
    run('cp -au ' + appsBrowserBuild + 'clang.js ' + appsBrowserBuild + 'clang.wasm ' + appsBrowserBuild + 'clang.data dist')

def appClangNative():
    if not os.path.isdir('build/apps-native'):
        run('mkdir -p build/apps-native')
        run('cd build/apps-native &&' +
            ' CXX=' + root + 'install/llvm-Release/' + 'bin/clang++' +
            ' CXXFLAGS=-DLIB_PREFIX=' + root + 'repos/emscripten/system/' +
            ' cmake -G "Ninja"' +
            ' -DCMAKE_BUILD_TYPE=Debug' +
            ' -DLLVM_BUILD=' + llvmNo86Build +
            ' -DCMAKE_CXX_STANDARD_LIBRARIES="-lpthread -lncurses -ltinfo -lz"' +
            ' ../../src')
    run('cd build/apps-native && time -p ninja -v clang')
    #run('cd build/apps-native && ./clang')
    #run('cd build/apps-native && gdb -q -ex run --args ./clang')

def appRuntime():
    app('runtime')
    run('cp -au ' + appsBrowserBuild + 'runtime.js ' + appsBrowserBuild + 'runtime.wasm dist')

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--all', action='store_true', help="Do everything marked with (*)")
parser.add_argument('-B', '--bash', action='store_true', help="Run bash with environment set up")
parser.add_argument('-f', '--format', action='store_true', help="Format sources")
parser.add_argument('-c', '--clone', action='store_true', help="(*) Clone repos. Doesn't touch ones which already exist.")
parser.add_argument('-s', '--status', action='store_true', help="git status")
parser.add_argument('--pull', action='store_true', help="git pull")
parser.add_argument('--merge', action='store_true', help="git merge upstream")
parser.add_argument('--push', action='store_true', help="git push")
parser.add_argument('--cmake', action='store_true', help="Build cmake if not already built")
parser.add_argument('-l', '--llvm', action='store_true', help="(*) Build llvm if not already built")
parser.add_argument('--no86', action='store_true', help="Build llvm without X86 if not already built")
parser.add_argument('--fastcomp', action='store_true', help="Build fastcomp if not already built")
parser.add_argument('--wabt', action='store_true', help="Build wabt if not already built")
parser.add_argument('-y', '--binaryen', action='store_true', help="(*) Build binaryen if not already built")
parser.add_argument('-e', '--emscripten', action='store_true', help="(*) Prepare emscripten by compiling say-hello.cpp")
parser.add_argument('-b', '--llvm-browser', action='store_true', help="(*) Build llvm in-browser components")
parser.add_argument('-1', '--app-1', action='store_true', help="Build app 1: clang-format")
parser.add_argument('-2', '--app-2', action='store_true', help="Build app 2: clang")
parser.add_argument('-n', '--app-n', action='store_true', help="Build app 2: clang, native")
parser.add_argument('-3', '--app-3', action='store_true', help="Build app 3: runtime")
args = parser.parse_args()

haveArg = False
for k,v in vars(args).items():
    if v:
        haveArg = True
if not haveArg:
    print('build.py: Tell me what to do. -a does almost everything. -h shows options.')

if args.bash:
    run('bash')
if args.format:
    run('clang-format -i src/*.cpp')
    run('chmod a-x src/*.cpp src/*.js src/*.html src/*.txt')
if args.clone or args.all:
    clone()
if args.status:
    status()
if args.pull:
    pull()
if args.merge:
    merge()
if args.push:
    push()
if args.cmake:
    cmake()
if args.llvm or args.all:
    llvm()
if args.no86:
    llvmNo86()
if args.fastcomp:
    fastcomp()
if args.wabt:
    wabt()
if args.binaryen or args.all:
    binaryen()
if args.emscripten or args.all:
    emscripten()
if args.llvm_browser or args.all:
    llvmBrowser()
if args.app_1 or args.app_2 or args.app_3:
    dist()
if args.app_1:
    appClangFormat()
if args.app_2:
    appClang()
if args.app_n:
    appClangNative()
if args.app_3:
    appRuntime()
