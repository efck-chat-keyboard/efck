VERSION := $(shell \
	curl 'https://api.github.com/repos/efck-chat-keyboard/efck/releases/latest' | \
	grep -oP '(?<=tag_name": "v)[^"]+' )
.PHONY: prepare srpm rpm


prepare:
	dnf -y install rpmdevtools rpm-build
	sed -Ei "s/^(%global version ).*/\1$(VERSION)/" $(spec)
	spectool -g -R $(spec)

srpm: prepare
	rpmbuild -bs --define "_srcrpmdir $(outdir)" $(spec)

rpm: prepare
	rpmbuild -bb --define "_rpmdir $(outdir)" $(spec)
