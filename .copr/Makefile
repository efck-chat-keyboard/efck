.PHONY: prepare srpm rpm

prepare:
	dnf -y install git rpmdevtools rpm-build
	spectool -g -R $(spec)

srpm: prepare
	v=$$(git describe --tags --abbrev=0); \
	rpmbuild -bs --define "app_version $$v" --define "_srcrpmdir $(outdir)" $(spec)

rpm: prepare
	v=$$(git describe --tags --abbrev=0); \
	rpmbuild -bb --define "app_version $$v" --define "_rpmdir $(outdir)" $(spec)
