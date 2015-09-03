"""Generate and work with PEP 425 Compatibility Tags."""

import sys

try:
    import sysconfig
except ImportError:  # pragma nocover
    # Python < 2.7
    import distutils.sysconfig as sysconfig
import distutils.util


def get_abbr_impl():
    """Return abbreviated implementation name."""
    if hasattr(sys, 'pypy_version_info'):
        pyimpl = 'pp'
    elif sys.platform.startswith('java'):
        pyimpl = 'jy'
    elif sys.platform == 'cli':
        pyimpl = 'ip'
    else:
        pyimpl = 'cp'
    return pyimpl


def get_impl_ver():
    """Return implementation version."""
    impl_ver = sysconfig.get_config_var("py_version_nodot")
    if not impl_ver or get_abbr_impl() == 'pp':
        impl_ver = ''.join(map(str, get_impl_version_info()))
    return impl_ver


def get_impl_version_info():
    """Return sys.version_info-like tuple for use in decrementing the minor
    version."""
    if get_abbr_impl() == 'pp':
        # as per https://github.com/pypa/pip/issues/2882
        return (sys.version_info[0], sys.pypy_version_info.major,
                sys.pypy_version_info.minor)
    else:
        return sys.version_info[0], sys.version_info[1]


def get_abi_tag():
    """Return the ABI tag based on SOABI (if available) or emulate SOABI
    (CPython 2, PyPy)."""
    soabi = sysconfig.get_config_var('SOABI')
    impl = get_abbr_impl()
    if not soabi and impl in ('cp', 'pp'):
        d = 'd' if hasattr(sys, 'pydebug') and sys.pydebug else ''
        m = 'm' if impl == 'cp' else ''
        u = 'u' if sys.maxunicode == 0x10ffff else ''
        abi = '%s%s%s%s%s' % (impl, get_impl_ver(), d, m, u)
    elif soabi and soabi.startswith('cpython-'):
        abi = 'cp' + soabi.split('-')[1]
    elif soabi:
        abi = soabi.replace('.', '_').replace('-', '_')
    else:
        abi = None
    return abi


def get_platform():
    """Return our platform name 'win32', 'linux_x86_64'"""
    # XXX remove distutils dependency
    return distutils.util.get_platform().replace('.', '_').replace('-', '_')


def get_supported(versions=None):
    """Return a list of supported tags for each version specified in
    `versions`.

    :param versions: a list of string versions, of the form ["33", "32"], 
        or None. The first version will be assumed to support our ABI.
    """
    supported = []
    
    # Versions must be given with respect to the preference
    if versions is None:
        versions = []
        version_info = get_impl_version_info()
        major = version_info[:-1]
        # Support all previous minor Python versions.
        for minor in range(version_info[-1], -1, -1):
            versions.append(''.join(map(str, major + (minor,))))
            
    impl = get_abbr_impl()
    
    abis = []

    abi = get_abi_tag()
    if abi:
        abis[0:0] = [abi]
 
    abi3s = set()
    import imp
    for suffix in imp.get_suffixes():
        if suffix[0].startswith('.abi'):
            abi3s.add(suffix[0].split('.', 2)[1])

    abis.extend(sorted(list(abi3s)))

    abis.append('none')

    arch = get_platform()
    
    # Current version, current API (built specifically for our Python):
    for abi in abis:
        supported.append(('%s%s' % (impl, versions[0]), abi, arch))
            
    # No abi / arch, but requires our implementation:
    for i, version in enumerate(versions):
        supported.append(('%s%s' % (impl, version), 'none', 'any'))
        if i == 0:
            # Tagged specifically as being cross-version compatible 
            # (with just the major version specified)
            supported.append(('%s%s' % (impl, versions[0][0]), 'none', 'any')) 
    
    # Major Python version + platform; e.g. binaries not using the Python API
    supported.append(('py%s' % (versions[0][0]), 'none', arch))

    # No abi / arch, generic Python
    for i, version in enumerate(versions):
        supported.append(('py%s' % (version,), 'none', 'any'))
        if i == 0:
            supported.append(('py%s' % (version[0]), 'none', 'any'))
        
    return supported
