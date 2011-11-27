%global debug_package %{nil}

%define run_tests               0
%define ship_tests              0
%define major                   8
%define minor                   0       
%define majmin                  %{major}.%{minor}
%define micro                   0
%define eclipse_base            %{_libdir}/eclipse
%define build_id		201106081058


# All arches line up except i386 -> x86
%ifarch %{ix86}
%define eclipse_arch    x86
%else
%define eclipse_arch   %{_arch}
%endif

Summary:        Eclipse C/C++ Development Tools (CDT) plugin
Name:           eclipse-cdt
Version:        %{majmin}.%{micro}
Release:        4
Epoch:		1
License:        EPL and CPL
Group:          Development/Java
URL:            http://www.eclipse.org/cdt
Requires:       eclipse-platform


# The following tarball was generated using the included fetch-cdt.sh
# script.  Note that the optional c99 and upc parsers plus the optional
# xlc support features have been removed.

Source0: %{name}-fetched-src-v201106081058.tar.bz2
Source4: fetch-cdt.sh

Source1: %{name}-fetched-src-autotools-dd3a8b8286575cba53fa95fff290fb708f843edd.tar.gz
Source14: make-autotools-tarball.sh

Source2: %{name}-fetched-src-libhover-dd3a8b8286575cba53fa95fff290fb708f843edd.tar.gz
Source15: make-libhover-tarball.sh

## The following tarball was generated thusly:
##
## mkdir temp && cd temp
## cvs -d:pserver:anonymous@dev.eclipse.org:/cvsroot/tools export -r CPPUnit_20061102 \
##   org.eclipse.cdt-cppunit/org.eclipse.cdt.cppunit \
##   org.eclipse.cdt-cppunit/org.eclipse.cdt.cppunit-feature
## cd org.eclipse.cdt-cppunit
## tar -czvf eclipse-cdt-cppunit-20061102.tar.gz org.eclipse.cdt.cppunit*
#
#Source2: %{name}-cppunit-20061102.tar.gz

# Script to run the tests in Xvnc
Source5: %{name}-runtests.sh

# Libhover docs to place locally
Source7: libstdc++-v3.libhover

# Autotools docs to place locally
Source8: acmacros-2.13.xml
Source9: acmacros-2.59.xml
Source10: acmacros-2.61.xml
Source11: ammacros-1.4-p6.xml
Source12: ammacros-1.9.5.xml
Source13: ammacros-1.9.6.xml

# Remove extraneous shared license statements that point to non-existent
# feature and were meant to be deleted.
Patch12: %{name}-remove-shared-license.patch

# Add XML -> HTML generation after running tests
Patch13: %{name}-testaggregation.patch

# Following are patches to build libhover libstdcxx plug-in and to supply
# binary libhover data directly in the plug-in itself.
Patch14: %{name}-libhover-local-libstdcxx.patch
Patch15: %{name}-libhover-libstdcxx.patch

# Patches for ppc64
# https://bugs.eclipse.org/bugs/show_bug.cgi?id=272380

# Add LDFLAGS to Makefile for .so
# https://bugs.eclipse.org/bugs/show_bug.cgi?id=272364
Patch16: %{name}-ppc64-add_ldflags.patch

# Add define of _XOPEN_SOURCE so that ptsname header is included
# https://bugs.eclipse.org/bugs/show_bug.cgi?id=272370
Patch17: %{name}-ppc64-add_xopen_source-include.patch

# Following is a patch to autotools to supply macro hover docs locally
# in the plugin.
Patch19: %{name}-autotools-local.patch

BuildRequires: eclipse-pde >= 1:3.7.0
BuildRequires: eclipse-rse >= 3.2
BuildRequires:  java-devel >= 1.4.2
BuildRequires: objectweb-asm >= 3.2
BuildRequires: lpg-java-compat
%if %{run_tests}
BuildRequires:  vnc-server
BuildRequires:  w3m
%endif

Requires:       gdb make gcc-c++ autoconf automake libtool
Requires:       eclipse-platform >= 1:3.7.0
Requires:	eclipse-rse >= 3.2
Requires:	objectweb-asm >= 3.2

ExclusiveArch: %{ix86} x86_64 ppc ia64 ppc64
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

%description
Eclipse features and plugins that are useful for C and C++ development.

%package parsers
Summary:        Eclipse C/C++ Development Tools (CDT) SDK plugin
Group:          Development/Other
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       lpg-java-compat

%description parsers
Optional language-variant parsers for the CDT.

%package sdk
Summary:        Eclipse C/C++ Development Tools (CDT) SDK plugin
Group:          Development/Other
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description sdk
Source for Eclipse CDT for use within Eclipse.

%if %{ship_tests}
%package tests
Summary:        Test suite for Eclipse C/C++ Development Tools (CDT)
Group:          Development/Other
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       vnc-server

%description tests
Test suite for Eclipse C/C++ Development Tools (CDT).
%endif

%prep
%setup -q -c 

pushd "org.eclipse.cdt.releng"

pushd results/plugins
%patch13 -p0
popd

pushd results/features
%patch12 -p0
popd

# Only build the sdk
offset=0; 
for line in $(grep -no "value=.*platform" build.xml); do
  linenum=$(echo "$line" | cut -d : -f 1)
  sed --in-place -e "$(expr $linenum - 1 - $offset ),$(expr $linenum + 1 - $offset)d" build.xml 
  offset=$(expr $offset + 3) 
done
# Only build for the platform on which we're building
sed --in-place -e "s:linux.gtk.x86/:linux.gtk.%{eclipse_arch}/:g" build.xml
pushd sdk
sed --in-place -e "74,82d" build.properties
sed --in-place -e "s:configs=\\\:configs=linux,gtk,%{eclipse_arch}:" build.properties
popd
pushd master
sed --in-place -e "81,89d" build.properties
sed --in-place -e "s:configs= \\\:configs=linux,gtk,%{eclipse_arch}:" build.properties
popd
pushd platform
sed --in-place -e "74,82d" build.properties
sed --in-place -e "s:configs=.*\\\:configs=linux,gtk,%{eclipse_arch}:" build.properties
popd

# build.xml assumes we build all configs, but we only build one so update 
# build.xml directory reference to be accurate.
sed --in-place -e "s:linux.gtk.x86/:linux.gtk.%{eclipse_arch}/:g" build.xml

popd

## Autotools stuff
mkdir autotools
pushd autotools
tar -xzf %{SOURCE1}
%patch19 -p0
pushd org.eclipse.linuxtools.cdt.autotools.core
mkdir macros
pushd macros
cp %{SOURCE8} .
cp %{SOURCE9} .
cp %{SOURCE10} .
cp %{SOURCE11} .
cp %{SOURCE12} .
cp %{SOURCE13} .
popd
popd
popd

## Libhover stuff
mkdir libhover
pushd libhover
tar -xzf %{SOURCE2}
# newlib libhover is an optional feature...remove it from CDT base
rm -rf org.eclipse.linuxtools.cdt.libhover.newlib
rm -rf org.eclipse.linuxtools.cdt.libhover.newlib-feature
%patch14 -p0
%patch15 -p0
pushd org.eclipse.linuxtools.cdt.libhover.libstdcxx
mkdir data
pushd data
cp %{SOURCE7} .
popd
popd
popd


# Upstream CVS includes random .so files.  Let's remove them now.
# We actually remove the entire "os" directory since otherwise
# we wind up with some empty directories that we don't want.
#rm -r org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.linux/os

mv org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.tests/resources/testlib/x86/so.g/libtestlib_g.so \
  org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.tests/resources/testlib/x86/so.g/libtestlib_g.BAK
find -name \*.so | xargs rm -rf
mv org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.tests/resources/testlib/x86/so.g/libtestlib_g.BAK \
  org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.tests/resources/testlib/x86/so.g/libtestlib_g.so

%ifarch ppc64
pushd org.eclipse.cdt.releng/results/plugins
echo "fragmentName.linux.%{eclipse_arch} = C/C++ Development Tools Core for Linux (%{eclipse_arch})" \
  >> org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core/plugin.properties
cp -rp org.eclipse.cdt.core.linux.{x86,%{eclipse_arch}}
cd org.eclipse.cdt.core.linux.%{eclipse_arch}
sed -i "s/x86/%{eclipse_arch}/" META-INF/MANIFEST.MF
mv os/linux/{x86,%{eclipse_arch}}
cd ../org.eclipse.cdt.core.linux
%patch16 -p0
%patch17 -p0
popd
%endif

%build
export JAVA_HOME=%{java_home}
export PATH=%{java_bin}:/usr/bin:$PATH

# See comments in the script to understand this.
/bin/sh -x %{eclipse_base}/buildscripts/copy-platform SDK \
  %{eclipse_base} xmlrpc codec httpclient lang rse
ln -sf %{_javadir}/lpgjavaruntime-1.1.0.jar SDK/plugins/net.sourceforge.lpg.lpgjavaruntime_1.1.0.jar
SDK=$(cd SDK >/dev/null && pwd)

# Eclipse may try to write to the home directory.
mkdir home
homedir=$(cd home > /dev/null && pwd)

pushd org.eclipse.cdt.releng/results/plugins/org.eclipse.cdt.core.linux/library
make JAVA_HOME="%{java_home}" ARCH=%{eclipse_arch} CC='gcc -D_GNU_SOURCE'
popd

PDEBUILDVERSION=$(ls %{eclipse_base}/dropins/sdk/plugins \
  | grep org.eclipse.pde.build_ | \
  sed 's/org.eclipse.pde.build_//')
PDEDIR=%{eclipse_base}/dropins/sdk/plugins/org.eclipse.pde.build_$PDEBUILDVERSION


LAUNCHERJAR=$(ls %{eclipse_base}/plugins \
  | grep org.eclipse.equinox.launcher_)
LAUNCHER=%{eclipse_base}/plugins/$LAUNCHERJAR

# Call eclipse headless to process CDT releng build scripts
pushd org.eclipse.cdt.releng 
java -jar $LAUNCHER \
     -Duser.home=$homedir                        \
     -DbuildId=%{build_id} \
     -DbranchVersion=%{version} \
     -DforceContextQualifier=%{build_id} \
     -XX:CompileCommand="exclude,org/eclipse/core/internal/dtree/DataTreeNode,forwardDeltaWith" \
     -XX:CompileCommand="exclude,org/eclipse/jdt/internal/compiler/lookup/ParameterizedMethodBinding,<init>" \
     -XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/dom/parser/cpp/semantics/CPPTemplates,instantiateTemplate" \
     -XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/pdom/dom/cpp/PDOMCPPLinkage,addBinding" \
     org.eclipse.core.launcher.Main             \
    -application org.eclipse.ant.core.antRunner \
    -DbuildId=%{build_id} \
    -DbranchVersion=%{version} \
    -DforceContextQualifier=%{build_id} \
    -DjavacFailOnError=true \
    -DdontUnzip=true \
    -DbaseLocation=$SDK \
    -Dpde.build.scripts=$PDEDIR/scripts \
    -DdontFetchAnything=true \
    -DskipFetch=true \
     zips
popd

## Autotools has dependencies on CDT so we must add these to the SDK directory
unzip -o org.eclipse.cdt.releng/results/I.%{build_id}/cdt-master-%{version}-%{build_id}.zip -d $SDK

## Autotools build
pushd autotools
java -jar $LAUNCHER \
     -Duser.home=$homedir                        \
     -XX:CompileCommand="exclude,org/eclipse/core/internal/dtree/DataTreeNode,forwardDeltaWith" \
     -XX:CompileCommand="exclude,org/eclipse/jdt/internal/compiler/lookup/ParameterizedMethodBinding,<init>" \
     -XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/dom/parser/cpp/semantics/CPPTemplates,instantiateTemplate" \
     -XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/pdom/dom/cpp/PDOMCPPLinkage,addBinding" \
     org.eclipse.core.launcher.Main             \
     -application org.eclipse.ant.core.antRunner \
     -DjavacSource=1.5 \
     -DjavacTarget=1.5 \
     -Duser.home=$homedir                        \
     -Dtype=feature                                    \
     -Did=org.eclipse.linuxtools.cdt.autotools \
     -DsourceDirectory=$(pwd)                          \
     -DbaseLocation=$SDK                               \
     -Dbuilder=$PDEDIR/templates/package-build  \
     -f $PDEDIR/scripts/build.xml 
popd

## Libhover build
pushd libhover
java -jar $LAUNCHER \
     -Duser.home=$homedir                        \
     -XX:CompileCommand="exclude,org/eclipse/core/internal/dtree/DataTreeNode,forwardDeltaWith" \
     -XX:CompileCommand="exclude,org/eclipse/jdt/internal/compiler/lookup/ParameterizedMethodBinding,<init>" \
     -XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/dom/parser/cpp/semantics/CPPTemplates,instantiateTemplate" \
     -XX:CompileCommand="exclude,org/eclipse/cdt/internal/core/pdom/dom/cpp/PDOMCPPLinkage,addBinding" \
     org.eclipse.core.launcher.Main             \
     -application org.eclipse.ant.core.antRunner \
     -Duser.home=$homedir                        \
     -Dtype=feature                                    \
     -Did=org.eclipse.linuxtools.cdt.libhover  \
     -DsourceDirectory=$(pwd)                          \
     -DbaseLocation=$SDK                               \
     -Dbuilder=$PDEDIR/templates/package-build  \
     -f $PDEDIR/scripts/build.xml 
popd

## Cppunit build
#pushd cppunit
#java -cp $SDK/startup.jar \
#     -Duser.home=$homedir                        \
#     org.eclipse.core.launcher.Main             \
#     -application org.eclipse.ant.core.antRunner       \
#     -Dtype=feature                                    \
#     -Did=org.eclipse.cdt.cppunit                      \
#     -DsourceDirectory=$(pwd)                          \
#     -DbaseLocation=$SDK                               \
#     -Dbuilder=$PDEDIR/templates/package-build  \
#     -f $PDEDIR/scripts/build.xml
#popd

%install
rm -rf ${RPM_BUILD_ROOT}

# Eclipse may try to write to the home directory.
mkdir -p home
homedir=$(cd home > /dev/null && pwd)

installDir=${RPM_BUILD_ROOT}/%{eclipse_base}/dropins/cdt
parsersInstallDir=${installDir}-parsers
sdkInstallDir=${installDir}-sdk
install -d -m755 $installDir
install -d -m755 $parsersInstallDir
install -d -m755 $sdkInstallDir

unzip -q -o org.eclipse.cdt.releng/results/I.%{build_id}/cdt-master-%{version}-%{build_id}.zip \
-d $installDir/eclipse

rm $installDir/eclipse/site.xml
rm $installDir/eclipse/pack.properties

# Unpack all existing feature jars
for x in $installDir/eclipse/features/*.jar; do
  dirname=`echo $x | sed -e 's:\\(.*\\)\\.jar:\\1:g'`
  mkdir -p $dirname
  unzip -q $x -d $dirname
  rm $x
done 

# Autotools install
pushd autotools
unzip -qq -d $installDir build/rpmBuild/org.eclipse.linuxtools.cdt.autotools.zip
popd

# Libhover install
pushd libhover
unzip -qq -d $installDir build/rpmBuild/org.eclipse.linuxtools.cdt.libhover.zip
popd

# Move upc, xlc, and lrparser plugins/features to parsers install area.
mkdir -p $parsersInstallDir/eclipse/features $parsersInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*xlc* $parsersInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*xlc* $parsersInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*lrparser* $parsersInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*lrparser* $parsersInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*upc* $parsersInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*upc* $parsersInstallDir/eclipse/plugins
pushd $parsersInstallDir/eclipse/plugins
ln -s ../../../../../../share/java/lpgjavaruntime.jar net.sourceforge.lpg.lpgjavaruntime_1.1.0.jar
popd

mkdir -p $sdkInstallDir/eclipse/features $sdkInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*source* $sdkInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*source* $sdkInstallDir/eclipse/plugins
mv $installDir/eclipse/plugins/org.eclipse.cdt.doc.isv_* $sdkInstallDir/eclipse/plugins
mv $installDir/eclipse/features/*sdk* $sdkInstallDir/eclipse/features
mv $installDir/eclipse/plugins/*sdk* $sdkInstallDir/eclipse/plugins

rm -rf $installDir/eclipse/features/org.eclipse.cdt.master_*
rm -rf $installDir/eclipse/plugins/org.eclipse.ant.optional.junit_*
rm -rf $installDir/eclipse/plugins/org.eclipse.test_*
rm -rf $installDir/eclipse/plugins/net.sourceforge.*

## Cppunit install
#pushd cppunit
#unzip -qq -d $RPM_BUILD_ROOT%{eclipse_base}/dropins/cdt build/rpmBuild/org.eclipse.cdt.cppunit.zip
#popd

P2LAUNCHERJAR=$(ls %{eclipse_base}/plugins \
  | grep org.eclipse.equinox.launcher_)
P2LAUNCHER=%{eclipse_base}/plugins/$P2LAUNCHERJAR

# Generate p2 metadata for CDT
pushd $installDir/eclipse
java -jar $P2LAUNCHER \
-application \
org.eclipse.equinox.p2.publisher.EclipseGenerator \
-metadataRepository file:`pwd`/repo \
-artifactRepository file:`pwd`/repo \
-source `pwd` \
-root "Eclipse CDT" \
-rootVersion %{version} \
-flavor tooling \
-publishArtifacts \
-append \
-artifactRepositoryName "CDT" \
-metadataRepositoryName "CDT" \
-vmargs \
-Duser.home=$homedir

rm -rf repo
popd

# Generate p2 metadata for CDT Parsers
pushd $parsersInstallDir/eclipse
java -jar $P2LAUNCHER \
-application \
org.eclipse.equinox.p2.publisher.EclipseGenerator \
-metadataRepository file:`pwd`/repo \
-artifactRepository file:`pwd`/repo \
-source `pwd` \
-root "CDT Parsers" \
-rootVersion %{version} \
-flavor tooling \
-publishArtifacts \
-append \
-artifactRepositoryName "CDT Parsers" \
-metadataRepositoryName "CDT Parsers" \
-vmargs \
-Duser.home=$homedir

rm -rf repo
popd

# Generate p2 metadata for CDT SDK
pushd $sdkInstallDir/eclipse
java -jar $P2LAUNCHER \
-application \
org.eclipse.equinox.p2.publisher.EclipseGenerator \
-metadataRepository file:`pwd`/repo \
-artifactRepository file:`pwd`/repo \
-source `pwd` \
-root "Eclipse CDT SDK" \
-rootVersion %{version} \
-flavor tooling \
-publishArtifacts \
-append \
-artifactRepositoryName "CDT SDK" \
-metadataRepositoryName "CDT SDK" \
-vmargs \
-Duser.home=$homedir

rm -rf repo
popd

mkdir -p ${installDir}-tests/plugins
mkdir -p ${installDir}-tests/features
mv ${installDir}/eclipse/plugins/*test* \
  ${installDir}-tests/plugins
mv ${installDir}/eclipse/features/*test* \
  ${installDir}-tests/features
for x in ${installDir}-tests/plugins/*.jar; do
  dirname=`echo $x | sed -e 's:\\(.*\\)\\.jar:\\1:g'`
  mkdir -p $dirname
  unzip -q $x -d $dirname
  rm $x
done 
cp -p %{SOURCE5} ${installDir}-tests/runtests
chmod 755 ${installDir}-tests/runtests
%if ! %{ship_tests}
%if ! %{run_tests}
rm -rf ${installDir}-tests
%endif
%endif

%if %{run_tests}
%check
installDir=${RPM_BUILD_ROOT}/%{eclipse_base}/dropins/cdt
# Copy the SDK to simulate real system
rm -rf SDK.fortests
cp -rpL %{eclipse_base} SDK.fortests
# Remove any CDT or CDT tests we may have currently installed
rm -rf SDK.fortests/dropins/cdt*
cp -rpL $installDir SDK.fortests/dropins
# The libhover plugin offers lots of completions but these cause issues
# with some of the tests which expect only a few completions.  We should
# update the tests or something ...
rm -rf SDK.fortests/dropins/cdt/eclipse/plugins/org.eclipse.linuxtools.libhover.*
cp -rpL ${installDir}-tests SDK.fortests/dropins
# FIXME:  I'd like to simulate real life with something like this ...
#chown -R root:root SDK.fortests
SDK.fortests/dropins/cdt-tests/runtests -e $(pwd)/SDK.fortests
w3m -cols 120 -dump results-*/html/org.eclipse.cdt.testing.html
%if ! %{ship_tests}
rm -rf ${installDir}-tests
%endif
%endif

%clean 
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(-,root,root)
%{eclipse_base}/dropins/cdt

%files sdk
%defattr(-,root,root)
%{eclipse_base}/dropins/cdt-sdk

%files parsers
%defattr(-,root,root)
%{eclipse_base}/dropins/cdt-parsers

%if %{ship_tests}
%files tests
%defattr(-,root,root)
%{eclipse_base}/dropins/cdt-tests
%endif

