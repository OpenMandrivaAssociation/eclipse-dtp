%global eclipse_base     %{_libdir}/eclipse
%global eclipse_dropin   %{_datadir}/eclipse/dropins

Name:      eclipse-dtp
Version:   1.8.2
Release:   1
Summary:   Eclipse Data Tools Platform
Group:     Development/Java
License:   EPL
URL:       http://www.eclipse.org/datatools/

# source tarball and the script used to generate it from upstream's source control
# script usage:
# $ sh get-dtp.sh
Source0:   dtp-%{version}.tar.gz
Source1:   get-dtp.sh

# Build with Java 6 SQL interfaces
Patch0:    %{name}-java6.patch

# remove duplicate plugin from sqltools features (it's actually built in the
# connectivity feature)
Patch1:    %{name}-remove-duplicate-plugin.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:        noarch

BuildRequires:    java-devel 
BuildRequires:    jpackage-utils
BuildRequires:    eclipse-pde >= 0:3.4.2
BuildRequires:    eclipse-emf
BuildRequires:    eclipse-gef
BuildRequires:    wsdl4j >= 1.5.2-6.6
BuildRequires:    xerces-j2 >= 2.7.1-10.3
BuildRequires:    xml-commons-resolver >= 1.1-2.15
BuildRequires:    xalan-j2 >= 2.7.0-7.5
BuildRequires:    xml-commons-apis >= 1.3.04-1.4
BuildRequires:    lpg-java-compat = 1.1.0

Requires:         java 
Requires:         jpackage-utils
Requires:         eclipse-platform >= 1:3.4.2
Requires:         eclipse-emf
Requires:         eclipse-gef
Requires:         wsdl4j >= 1.5.2-6.6
Requires:         xerces-j2 >= 2.7.1-10.3
Requires:         xml-commons-resolver >= 1.1-2.15
Requires:         xalan-j2 >= 2.7.0-7.5
Requires:         xml-commons-apis >= 1.3.04-1.4
Requires:         lpg-java-compat = 1.1.0

%description
The Eclipse Data Tools Platform provides extensible frameworks and exemplary 
tools, enabling a diverse set of plug-in offerings specific to particular 
data-centric technologies and supported by the DTP ecosystem.

%prep
%setup -q -n dtp-%{version}

# apply patches
pushd org.eclipse.datatools.connectivity.sqm.core
%patch0 -p0
popd
%patch1 -p0

sed -i -e "s|2.9.0.qualifier|0.0.0|g" org.eclipse.datatools.enablement.oda.feature/feature.xml

# make sure upstream hasn't snuck in any jars we don't know about
JARS=""
for j in `find -name "*.jar"`; do
  if [ ! -L $j ]; then
    JARS="$JARS $j"
  fi
done
if [ ! -z "$JARS" ]; then
   echo "These jars should be deleted and symlinked to system jars: $JARS"
   exit 1
fi

mkdir orbitDeps
pushd orbitDeps
ln -s %{_javadir}/xerces-j2.jar org.apache.xerces_2.9.0.jar
ln -s %{_javadir}/xalan-j2-serializer.jar org.apache.xml.serializer_2.7.1.jar
ln -s %{_javadir}/xml-commons-resolver.jar org.apache.xml.resolver_1.2.0.jar
ln -s %{_javadir}/xml-commons-apis.jar javax.xml_1.3.4.jar
ln -s %{_javadir}/wsdl4j.jar javax.wsdl_1.5.0.jar
ln -s %{_javadir}/lpgjavaruntime.jar net.sourceforge.lpg.lpgjavaruntime_1.1.0.jar
popd

%build
# Note: Use date from the cvs tag as the context qualifier.
OPTIONS="-DjavacTarget=1.5 -DjavacSource=1.5 -DforceContextQualifier=v201102060800"

# build all features except for documentation and SDK features TODO: build everything
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.datatools.modelbase.feature \
  -d "emf gef" -o `pwd`/orbitDeps -a "$OPTIONS"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.datatools.connectivity.feature \
  -d "emf gef" -o `pwd`/orbitDeps -a "$OPTIONS"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.datatools.sqldevtools.feature \
  -d "emf gef" -o `pwd`/orbitDeps -a "$OPTIONS"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.datatools.enablement.feature \
  -d "emf gef" -o `pwd`/orbitDeps -a "$OPTIONS"

%install
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{eclipse_dropin}
unzip -q -d %{buildroot}%{eclipse_dropin}/dtp-modelbase build/rpmBuild/org.eclipse.datatools.modelbase.feature.zip
unzip -q -d %{buildroot}%{eclipse_dropin}/dtp-connectivity build/rpmBuild/org.eclipse.datatools.connectivity.feature.zip
unzip -q -d %{buildroot}%{eclipse_dropin}/dtp-sqldevtools build/rpmBuild/org.eclipse.datatools.sqldevtools.feature.zip
unzip -q -d %{buildroot}%{eclipse_dropin}/dtp-enablement build/rpmBuild/org.eclipse.datatools.enablement.feature.zip

# use system bundles
pushd %{buildroot}%{eclipse_dropin}/dtp-enablement/eclipse/plugins
rm org.apache.xerces_*.jar
ln -s ../../../../../java/xerces-j2.jar org.apache.xerces_2.9.0.jar
rm org.apache.xml.serializer_*.jar
ln -s ../../../../../java/xalan-j2-serializer.jar org.apache.xml.serializer_2.7.1.jar
rm org.apache.xml.resolver_*.jar
ln -s ../../../../../java/xml-commons-resolver.jar org.apache.xml.resolver_1.2.0.jar
rm javax.xml_*.jar
ln -s ../../../../../java/xml-commons-apis.jar javax.xml_1.3.4.jar
rm javax.wsdl_*.jar
ln -s ../../../../../java/wsdl4j.jar javax.wsdl_1.5.0.jar
popd
pushd %{buildroot}%{eclipse_dropin}/dtp-sqldevtools/eclipse/plugins
rm net.sourceforge.lpg.lpgjavaruntime_*.jar
ln -s ../../../../../java/lpgjavaruntime.jar net.sourceforge.lpg.lpgjavaruntime_1.1.0.jar
popd

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{eclipse_dropin}/dtp-modelbase
%{eclipse_dropin}/dtp-connectivity
%{eclipse_dropin}/dtp-sqldevtools
%{eclipse_dropin}/dtp-enablement
%doc org.eclipse.datatools.sdk-all.feature/rootfiles/*

