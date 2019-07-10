import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.client.tools.oss import get_gnu_triplet

class DebianDependencyConan(ConanFile):
    name = "libuuid1"
    version = "2.27.1"
    build_version = "6ubuntu3.7" 
    homepage = "https://packages.ubuntu.com/xenial-updates/libuuid1"
    # dev_url = https://packages.ubuntu.com/xenial-updates/uuid-dev
    description = "The libuuid library generates and parses 128-bit Universally Unique IDs (UUIDs). A UUID is an identifier that is unique within the space of all such identifiers across both space and time. It can be used for multiple purposes, from tagging objects with an extremely short lifetime to reliably identifying very persistent objects across a network."
    url = "https://github.com/jens-totemic/conan-libuuid1"    
    license = "BSD-3-clause"
    settings = "os", "arch"

    def translate_arch(self):
        arch_string = str(self.settings.arch)
        # ubuntu does not have v7 specific libraries
        if (arch_string) == "armv7hf":
            return "armhf"
        elif (arch_string) == "armv8":
            return "arm64"
        elif (arch_string) == "x86_64":
            return "amd64"
        return arch_string
        
    def _download_extract_deb(self, url, sha256):
        filename = "./download.deb"
        deb_data_file = "data.tar.xz"
        tools.download(url, filename)
        tools.check_sha256(filename, sha256)
        # extract the payload from the debian file
        self.run("ar -x %s %s" % (filename, deb_data_file))
        os.unlink(filename)
        tools.unzip(deb_data_file)
        os.unlink(deb_data_file)

    def triplet_name(self):
        # we only need the autotool class to generate the host variable
        autotools = AutoToolsBuildEnvironment(self)

        # construct path using platform name, e.g. usr/lib/arm-linux-gnueabihf/pkgconfig
        # if not cross-compiling it will be false. In that case, construct the name by hand
        return autotools.host or get_gnu_triplet(str(self.settings.os), str(self.settings.arch), self.settings.get_safe("compiler"))
        
    def build(self):
        if self.settings.os == "Linux":
            if self.settings.arch == "x86_64":
                # https://packages.ubuntu.com/xenial-updates/amd64/libuuid1/download
                sha_lib = "0069b9fe2ac138b980db186d88369e40d68570ab31925c19f9beabe1eb3af79e"
                # https://packages.ubuntu.com/xenial-updates/amd64/uuid-dev/download
                sha_dev = "a9d5d94c8181fcafa7464fb3298a36ece0ff64f1df7d599fe7258fa91dc23d62"
                
                url_lib = ("http://us.archive.ubuntu.com/ubuntu/pool/main/u/util-linux/libuuid1_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, self.translate_arch()))
                url_dev = ("http://us.archive.ubuntu.com/ubuntu/pool/main/u/util-linux/uuid-dev_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, self.translate_arch()))
            elif self.settings.arch == "armv8":
                # https://packages.ubuntu.com/xenial-updates/arm64/libuuid1/download
                sha_lib = "1d886309c5b24257e5cc6ba0aa27085b01fc4702049b780e01fef2dce52b0c70"
                # https://packages.ubuntu.com/xenial-updates/arm64/uuid-dev/download
                sha_dev = "8086d900b015b4be3a78c43c4a8a41954998a8d978e42c4d82b513468d8dc6a4"
                
                url_lib = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/u/util-linux/libuuid1_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, self.translate_arch()))
                url_dev = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/u/util-linux/uuid-dev_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, self.translate_arch()))
            else: # armv7hf
                # https://packages.ubuntu.com/xenial-updates/armhf/libuuid1/download
                sha_lib = "029dfbd95f619bdaf54a663dd5a92a5ec1d45447deeb81383e338c7aed5741b6"
                # https://packages.ubuntu.com/xenial-updates/armhf/uuid-dev/download
                sha_dev = "3b6ffd5b606ede5d0f3d9c4284bfd5a75a3cbc45bfd7aa008ac943f0b0c97912"
                
                url_lib = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/u/util-linux/libuuid1_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, self.translate_arch()))
                url_dev = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/u/util-linux/uuid-dev_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, self.translate_arch()))
            self._download_extract_deb(url_lib, sha_lib)
            self._download_extract_deb(url_dev, sha_dev)
            # remove libuuid.so which is an absolute link to /lib/arm-linux-gnueabihf/libuuid.so.1.3.0
            libuuid_so_path = "usr/lib/%s/libuuid.so" % self.triplet_name()
            os.remove(libuuid_so_path)
            os.symlink("libuuid.so.1.3.0", libuuid_so_path)
        else:
            self.output.info("Nothing to be done for this OS")

    def package(self):
        self.copy(pattern="*", dst="lib", src="lib/" + self.triplet_name(), symlinks=True)
        self.copy(pattern="*", dst="lib", src="usr/lib/" + self.triplet_name(), symlinks=True)
        self.copy(pattern="*", dst="include", src="usr/include", symlinks=True)
        self.copy(pattern="copyright", src="usr/share/doc/" + self.name, symlinks=True)

    def copy_cleaned(self, source, prefix_remove, dest):
        for e in source:
            if (e.startswith(prefix_remove)):
                entry = e[len(prefix_remove):]
                if len(entry) > 0 and not entry in dest:
                    dest.append(entry)

    def package_info(self):
        # pkgpath = "usr/lib/%s/pkgconfig" % self.triplet_name()
        pkgpath =  "lib/pkgconfig"
        pkgconfigpath = os.path.join(self.package_folder, pkgpath)
        if self.settings.os == "Linux":
            self.output.info("package info file: " + pkgconfigpath)
            with tools.environment_append({'PKG_CONFIG_PATH': pkgconfigpath}):
                pkg_config = tools.PkgConfig("uuid", variables={ "prefix" : self.package_folder } )

                #self.copy_cleaned(pkg_config.libs_only_L, "-L", self.cpp_info.lib_paths)
                self.output.info("lib_paths %s" % self.cpp_info.lib_paths)

                # exclude all libraries from dependencies here, they are separately included
                self.copy_cleaned(pkg_config.libs_only_l, "-l", self.cpp_info.libs)
                self.output.info("libs: %s" % self.cpp_info.libs)

                #self.copy_cleaned(pkg_config.cflags_only_I, "-I", self.cpp_info.include_paths)
                self.output.info("include_paths: %s" % self.cpp_info.include_paths)
