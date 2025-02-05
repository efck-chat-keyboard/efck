%global app_name    efck-chat-keyboard
%global module_name efck

%global version 1.0git

Name:		%{module_name}
Version:	%{version}
Release:	1%{?dist}
Summary:	Emoji filter / Unicode chat keyboard
License:	AGPLv3
URL:		https://efck-chat-keyboard.github.io
BugURL:		https://github.com/efck-chat-keyboard/efck

Source0:     %{pypi_source efck}
Source1:     https://github.com/efck-chat-keyboard/efck/archive/v%{version}/%{module_name}-v%{version}.tar.gz

%description %{expand:
A Qt GUI utility that pops up a dialog with tabs for:
emoji filtering / selection, text to Unicode transformation,
GIF meme selection etc. (extensible).
Upon activation, it 'pastes' your selection into the previously active
(focused) window, such as a web browser or a desktop chat app or similar.}

BuildArch:	noarch
BuildRequires:	python3-devel
# Dependency on Fedora, required in other distros
BuildRequires: pyproject-rpm-macros
# For %check section
BuildRequires: xorg-x11-server-Xvfb
BuildRequires: python3-pyqt6
BuildRequires: python3-unicodedata2

Requires:	(python3-pyqt6 or python3-qt5)
Requires:	google-noto-emoji-color-fonts
Recommends:	xdotool if xorg-x11-server-Xorg
Recommends:	ydotool
Recommends:	python3dist(unicodedata2)
Provides:	%{module_name}

%py_provides python3-%{module_name}

%generate_buildrequires
%pyproject_buildrequires -r requirements.txt

%prep
%autosetup -n %{module_name}-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files efck +auto
install -Dm644 -t %{buildroot}%{_datadir}/applications/ packaging/debian/%{app_name}.desktop
install -Dm644 -t %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/ packaging/debian/%{app_name}.svg

%files -n %{module_name} -f %{pyproject_files}
%doc README.md
%license LICENSE.txt
%{python3_sitelib}/%{module_name}/
%{python3_sitelib}/%{module_name}-%{version}.dist-info/
%{_bindir}/%{module_name}
%{_datadir}/applications/*
%{_datadir}/icons/hicolor/scalable/apps/*

%check
%pyproject_check_import
xvfb-run -a -- %{_bindir}/%{module_name} --help

%changelog
* Fri Sep 30 2022 Maintainer <see-contact-details-on-project-website@example.org> - 1.0
- initial package
