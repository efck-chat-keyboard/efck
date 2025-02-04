%global app_name    efck-chat-keyboard
%global module_name efck

Name:		%{app_name}
Version:	%{app_version}
Release:	1%{?dist}
Summary:	Emoji filter / Unicode chat keyboard
License:	AGPLv3
URL:		https://efck-chat-keyboard.github.io
BugURL:		https://github.com/efck-chat-keyboard/efck

BuildArch:	noarch
BuildRequires:	python3-devel

%global _description %{expand:
A Qt GUI utility that pops up a dialog with tabs for:
emoji filtering / selection, text to Unicode transformation,
GIF meme selection etc. (extensible).
Upon activation, it 'pastes' your selection into the previously active
(focused) window, such as a web browser or a desktop chat app or similar.}

%description %_description

%py_provides python3-%{module_name}

Requires:	(python3-pyqt6 or python3-qt5)
Requires:	google-noto-emoji-color-fonts
Recommends:	xdotool if xorg-x11-server-Xorg
Recommends:	ydotool
Recommends:	python3dist(unicodedata2)

%prep
%autosetup -n %{app_name}-%{app_version}

%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files efck+auto
install -Dm644 -t %{buildroot}%{_datadir}/applications/ packaging/debian/*.desktop
install -Dm644 -t %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/ packaging/debian/*.svg

%files -n %{app_name} -f %{pyproject_files}
%doc README.md
%license LICENSE.txt
%{_bindir}/%{app_name}
%{_datadir}/applications/*
%{_datadir}/icons/hicolor/scalable/apps/*

%changelog
* Fri Sep 30 2022 Jaka Hudoklin <jaka@x-truder.net> - 1.0rc1-1
- initial package
