# **********************************************************************
#
# Copyright (c) 2003-2013 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************

top_srcdir	= ..

include $(top_srcdir)/config/Make.rules

ifneq ($(findstring MINGW,$(UNAME)),)
    SUBDIRS		= IceUtil \
			  Slice \
			  slice2cpp \
			  slice2rb \
			  Ice
else
    SUBDIRS		= IceUtil \
			  Slice \
			  slice2cpp \
			  slice2freeze \
			  slice2py \
			  Ice \
			  Freeze
endif

.PHONY: $(EVERYTHING) $(SUBDIRS)

#
# Dependencies for 'all' target when using -jx
#

Slice: IceUtil

slice2cpp slice2cs slice2freeze slice2freezej slice2java slice2php slice2py slice2rb slice2html: Slice

Ice: slice2cpp

IceXML IceSSL Freeze FreezeScript IceBox Glacier2Lib IcePatch2Lib IceStormLib IceGridLib: Ice

Freeze: slice2freeze

FreezeScript IceDB: Freeze

Glacier2 IceGridLib: Glacier2Lib

IcePatch2: IcePatch2Lib

IceStorm: IceBox IceDB IceGridLib

IceGrid: IceGridLib IceStorm IcePatch2Lib IceDB


all:: $(SUBDIRS)

$(SUBDIRS):
	@echo "making all in $@"
	@$(MAKE) all --directory=$@

$(EVERYTHING_EXCEPT_ALL)::
	@for subdir in $(SUBDIRS); \
        do \
            if test -d $$subdir ; \
            then \
                echo "making $@ in $$subdir"; \
                ( cd $$subdir && $(MAKE) $@ ) || exit 1; \
            fi; \
        done

