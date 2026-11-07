.DEFAULT_GOAL := all
.PHONY: all full nrf52811-aesl nrf52811-aesl-bootloader nrf52811-aesl-unsigned nrf52811-aesl-bootloader-unsigned nrf52811-aesl-ota print-build-profile
# Both public entries compile without keys or signing. Makefile.signed selects
# signature-required Recovery. Official packaging uses private Makefile.private.
INKTAG_NRF_REQUIRE_SIGNED_DFU ?= 0
ifneq ($(INKTAG_NRF_REQUIRE_SIGNED_DFU),0)
ifneq ($(INKTAG_NRF_REQUIRE_SIGNED_DFU),1)
$(error INKTAG_NRF_REQUIRE_SIGNED_DFU must be 0 or 1)
endif
endif
override NRF_SIGNATURE_PROFILE := $(if $(filter 1,$(INKTAG_NRF_REQUIRE_SIGNED_DFU)),required,optional)
NRF_BUILD_ROOT ?= $(if $(BUILD_DIR),$(BUILD_DIR),.cache/build/nordic/nrf52811_aesl)
NRF_OUTPUT_ROOT ?= $(if $(OUTPUT_DIR),$(OUTPUT_DIR),_build/nordic/nrf52811_aesl)
override NRF_PROFILE_BUILD_DIR := $(NRF_BUILD_ROOT)/$(NRF_SIGNATURE_PROFILE)
override NRF_PROFILE_OUTPUT_DIR := $(NRF_OUTPUT_ROOT)/$(NRF_SIGNATURE_PROFILE)
override NRF_RECOVERY_ARGS := INKTAG_NRF_REQUIRE_SIGNED_DFU=$(INKTAG_NRF_REQUIRE_SIGNED_DFU) BUILD_DIR="$(NRF_PROFILE_BUILD_DIR)/bootloader" OUTPUT_DIR="$(NRF_PROFILE_OUTPUT_DIR)/bootloader"
ifneq ($(filter nrf52811-aesl-ota,$(MAKECMDGOALS)),)
ifneq ($(INKTAG_NRF_REQUIRE_SIGNED_DFU),0)
$(error Unsigned OTA packaging requires the optional Makefile entry)
endif
endif
all: nrf52811-aesl
full:
	python3 build.py --profile $(NRF_SIGNATURE_PROFILE) $(if $(SDK_ROOT),--sdk-root "$(SDK_ROOT)") $(if $(TOOLCHAIN_PATH),--toolchain-path "$(TOOLCHAIN_PATH)") --build-root "$(NRF_BUILD_ROOT)" --output-root "$(NRF_OUTPUT_ROOT)" $(if $(SIGNED_OTA),--signed-ota "$(SIGNED_OTA)")
nrf52811-aesl:
	$(MAKE) -f firmware/ports/nordic/nrf52811/Makefile all BUILD_DIR="$(NRF_PROFILE_BUILD_DIR)" OUTPUT_DIR="$(NRF_PROFILE_OUTPUT_DIR)"
	$(MAKE) -f firmware/ports/nordic/nrf52811/bootloader/Makefile all $(NRF_RECOVERY_ARGS)
nrf52811-aesl-bootloader:
	$(MAKE) -f firmware/ports/nordic/nrf52811/bootloader/Makefile all $(NRF_RECOVERY_ARGS)
nrf52811-aesl-unsigned: nrf52811-aesl
nrf52811-aesl-bootloader-unsigned: nrf52811-aesl-bootloader
nrf52811-aesl-ota: nrf52811-aesl
	python3 tools/ota/package-nrf52811.py --app "$(NRF_PROFILE_OUTPUT_DIR)/InkTag-nrf52811_aesl.bin" --output "$(NRF_PROFILE_OUTPUT_DIR)/InkTag-nrf52811_aesl-ota-unsigned.zip"
print-build-profile:
	@printf '%s\n' 'profile=$(NRF_SIGNATURE_PROFILE)' 'signatureRequired=$(INKTAG_NRF_REQUIRE_SIGNED_DFU)' 'build=$(NRF_PROFILE_BUILD_DIR)' 'output=$(NRF_PROFILE_OUTPUT_DIR)' 'signing=no'
