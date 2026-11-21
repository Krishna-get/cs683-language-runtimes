#!/bin/bash
# Null-change control: clone spp_dev -> spp_dev_gated with NO logic change,
# build it, and prove it reproduces spp_dev bit-for-bit. Validates the
# toolchain before any mitigation code is written.
set -e
CS=~/ChampSim
cd $CS
rm -rf prefetcher/spp_dev_gated
cp -r prefetcher/spp_dev prefetcher/spp_dev_gated
cd prefetcher/spp_dev_gated
for f in *.cc *.h; do
  sed -i 's/spp_dev/spp_dev_gated/g' "$f"
  mv "$f" "$(echo $f | sed 's/spp_dev/spp_dev_gated/')"
done
cd $CS
sed 's/spp_dev/spp_dev_gated/g' configs/spp_dev_lru.json > configs/spp_dev_gated_lru.json
echo "--- config: configs/spp_dev_gated_lru.json"; cat configs/spp_dev_gated_lru.json
./config.sh configs/spp_dev_gated_lru.json
make -j$(nproc)
ls -la bin/champsim_spp_dev_gated_lru
