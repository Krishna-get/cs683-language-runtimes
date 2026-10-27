#!/bin/bash
cd ~/cs683
$PIN_ROOT/pin -t ~/ChampSim/tracer/pin/obj-intel64/champsim_tracer.so -o traces/long_cll.champsimtrace \
  -app_thread 0 -start_symbol champsim_roi_begin -stop_symbol champsim_roi_end -t 40000000 -- bin/linked_list 80
./finish.sh long_cll cll
