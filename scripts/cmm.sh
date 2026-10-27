#!/bin/bash
cd ~/cs683
$PIN_ROOT/pin -t ~/ChampSim/tracer/pin/obj-intel64/champsim_tracer.so -o traces/long_cmm.champsimtrace \
  -app_thread 0 -start_symbol champsim_roi_begin -stop_symbol champsim_roi_end -t 40000000 -- bin/matrix_mult_512_v2
./finish.sh long_cmm cmm
