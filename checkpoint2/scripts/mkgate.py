#!/usr/bin/env python3
import sys,os
d=sys.argv[1]; hp=d+"/spp_dev_gated.h"; cp=d+"/spp_dev_gated.cc"
h=open(hp).read(); c=open(cp).read()
if "GATE_ON" in h: sys.exit("already patched")
F=[]
def S(t,o,n,l):
    if t.count(o)!=1: F.append(l+" x%d"%t.count(o)); return t
    return t.replace(o,n)
h=S(h,"#ifndef SPP_H\n#define SPP_H","#ifndef SPP_GATED_H\n#define SPP_GATED_H","guard")
h=S(h,"  using prefetcher::prefetcher;","""  constexpr static bool GATE_ON = true;
  constexpr static uint32_t GATE_LEVELS = 3;
  constexpr static uint64_t GATE_EPOCH_DEFAULT = 16384;
  constexpr static uint64_t GATE_MIN_EVIDENCE_DEFAULT = 256;
  constexpr static uint64_t GATE_WASTE_HIGH_DEFAULT = 500;
  constexpr static uint64_t GATE_WASTE_LOW_DEFAULT = 100;
  constexpr static uint64_t GATE_REPROBE_DEFAULT = 64;
  constexpr static uint32_t GATE_CAP_DEFAULT = 3;
  struct GATE_STATE {
    uint32_t level = 0;
    uint64_t accesses = 0, ep_fills = 0, ep_useful = 0, quiet_epochs = 0;
    uint64_t tot_fills = 0, tot_useful = 0, epochs = 0;
    uint64_t sup_lookahead = 0, sup_all = 0, demoted = 0, issued = 0;
    uint64_t level_epochs[GATE_LEVELS + 1] = {};
    uint32_t max_level_seen = 0;
    uint64_t epoch = GATE_EPOCH_DEFAULT;
    uint64_t min_evidence = GATE_MIN_EVIDENCE_DEFAULT;
    uint64_t waste_high = GATE_WASTE_HIGH_DEFAULT;
    uint64_t waste_low = GATE_WASTE_LOW_DEFAULT;
    uint64_t reprobe = GATE_REPROBE_DEFAULT;
    uint32_t cap = GATE_CAP_DEFAULT;
  };
  GATE_STATE GATE;
  void gate_configure();
  void gate_end_of_epoch();

  using prefetcher::prefetcher;""","decl")
c=S(c,"#include <cassert>\n#include <iostream>","#include <cassert>\n#include <cstdlib>\n#include <iostream>","inc")
c=S(c,"  // pass pointers\n  ST._parent = this;","  if constexpr (GATE_ON)\n    gate_configure();\n\n  // pass pointers\n  ST._parent = this;","cfg")
c=S(c,"  GHR.global_accuracy = GHR.pf_issued ? ((100 * GHR.pf_useful) / GHR.pf_issued) : 0;","""  GHR.global_accuracy = GHR.pf_issued ? ((100 * GHR.pf_useful) / GHR.pf_issued) : 0;

  if constexpr (GATE_ON) {
    if (useful_prefetch) { GATE.ep_useful++; GATE.tot_useful++; }
    if (++GATE.accesses >= GATE.epoch) gate_end_of_epoch();
  }""","acct")
c=S(c,"  uint8_t do_lookahead = 0;","  uint8_t do_lookahead = 0;\n  uint32_t gate_la_iter = 0;","la")
c=S(c,"""          if (FILTER.check(pf_addr, ((confidence_q[i] >= FILL_THRESHOLD) ? spp_dev_gated::SPP_L2C_PREFETCH : spp_dev_gated::SPP_LLC_PREFETCH))) {
            prefetch_line(pf_addr, (confidence_q[i] >= FILL_THRESHOLD), 0); // Use addr (not base_addr) to obey the same physical page boundary

            if (confidence_q[i] >= FILL_THRESHOLD) {""","""          bool want_l2 = (confidence_q[i] >= FILL_THRESHOLD);
          bool gate_skip = false;
          if constexpr (GATE_ON) {
            if (GATE.level >= 3) { gate_skip = true; GATE.sup_all++; }
            else if (GATE.level >= 1 && gate_la_iter > 0) { gate_skip = true; GATE.sup_lookahead++; }
            else if (GATE.level >= 2 && want_l2) { want_l2 = false; GATE.demoted++; }
          }
          if (!gate_skip && FILTER.check(pf_addr, (want_l2 ? spp_dev_gated::SPP_L2C_PREFETCH : spp_dev_gated::SPP_LLC_PREFETCH))) {
            prefetch_line(pf_addr, want_l2, 0);
            GATE.issued++;

            if (want_l2) {""","issue")
c=S(c,"  } while (LOOKAHEAD_ON && do_lookahead);","    gate_la_iter++;\n  } while (LOOKAHEAD_ON && do_lookahead);","lainc")
c=S(c,"  if constexpr (FILTER_ON) {\n    if constexpr (SPP_DEBUG_PRINT) {\n      std::cout << std::endl;\n    }\n    FILTER.check(evicted_addr, spp_dev_gated::L2C_EVICT);","  if constexpr (GATE_ON) {\n    if (prefetch) { GATE.ep_fills++; GATE.tot_fills++; }\n  }\n\n  if constexpr (FILTER_ON) {\n    if constexpr (SPP_DEBUG_PRINT) {\n      std::cout << std::endl;\n    }\n    FILTER.check(evicted_addr, spp_dev_gated::L2C_EVICT);","fill")
c=S(c,"void spp_dev_gated::prefetcher_final_stats() {}","""namespace {
uint64_t genv(const char* n, uint64_t d)
{
  const char* v = std::getenv(n);
  if (v == nullptr || *v == '\\0') return d;
  char* e = nullptr;
  unsigned long long p = std::strtoull(v, &e, 10);
  return (e == v) ? d : static_cast<uint64_t>(p);
}
}

void spp_dev_gated::gate_configure()
{
  GATE.epoch = genv("SPP_GATE_EPOCH", GATE_EPOCH_DEFAULT);
  GATE.min_evidence = genv("SPP_GATE_MIN_EVIDENCE", GATE_MIN_EVIDENCE_DEFAULT);
  GATE.waste_high = genv("SPP_GATE_WASTE_HIGH", GATE_WASTE_HIGH_DEFAULT);
  GATE.waste_low = genv("SPP_GATE_WASTE_LOW", GATE_WASTE_LOW_DEFAULT);
  GATE.reprobe = genv("SPP_GATE_REPROBE", GATE_REPROBE_DEFAULT);
  uint64_t rc = genv("SPP_GATE_CAP", GATE_CAP_DEFAULT);
  GATE.cap = static_cast<uint32_t>(rc > GATE_LEVELS ? GATE_LEVELS : rc);
  if (GATE.epoch == 0) GATE.epoch = GATE_EPOCH_DEFAULT;
  std::cout << "SPP-GATE config epoch=" << GATE.epoch << " min_evidence=" << GATE.min_evidence << " waste_high=" << GATE.waste_high
            << " waste_low=" << GATE.waste_low << " reprobe=" << GATE.reprobe << " cap=" << GATE.cap << std::endl;
}

void spp_dev_gated::gate_end_of_epoch()
{
  GATE.epochs++;
  GATE.level_epochs[GATE.level <= GATE_LEVELS ? GATE.level : GATE_LEVELS]++;
  if (GATE.ep_fills >= GATE.min_evidence) {
    uint64_t waste = GATE.ep_fills / (1 + GATE.ep_useful);
    if (waste > GATE.waste_high && GATE.level < GATE.cap) GATE.level++;
    else if (waste < GATE.waste_low && GATE.level > 0) GATE.level--;
    GATE.quiet_epochs = 0;
  } else if (GATE.level > 0) {
    if (++GATE.quiet_epochs >= GATE.reprobe) { GATE.level--; GATE.quiet_epochs = 0; }
  }
  if (GATE.level > GATE.max_level_seen) GATE.max_level_seen = GATE.level;
  GATE.accesses = 0; GATE.ep_fills = 0; GATE.ep_useful = 0;
}

void spp_dev_gated::prefetcher_final_stats()
{
  std::cout << std::endl << "SPP-GATE stats" << std::endl;
  std::cout << "SPP-GATE cfg waste_high: " << GATE.waste_high << std::endl;
  std::cout << "SPP-GATE cfg cap: " << GATE.cap << std::endl;
  std::cout << "SPP-GATE epochs: " << GATE.epochs << std::endl;
  std::cout << "SPP-GATE final level: " << GATE.level << std::endl;
  std::cout << "SPP-GATE max level seen: " << GATE.max_level_seen << std::endl;
  for (uint32_t l = 0; l <= GATE_LEVELS; l++)
    std::cout << "SPP-GATE epochs at level " << l << ": " << GATE.level_epochs[l] << std::endl;
  std::cout << "SPP-GATE prefetches issued: " << GATE.issued << std::endl;
  std::cout << "SPP-GATE suppressed lookahead: " << GATE.sup_lookahead << std::endl;
  std::cout << "SPP-GATE suppressed all: " << GATE.sup_all << std::endl;
  std::cout << "SPP-GATE demoted to LLC: " << GATE.demoted << std::endl;
  std::cout << "SPP-GATE prefetch fills: " << GATE.tot_fills << std::endl;
  std::cout << "SPP-GATE useful prefetch hits: " << GATE.tot_useful << std::endl;
  std::cout << "SPP-GATE lifetime waste ratio: " << (GATE.tot_fills / (1 + GATE.tot_useful)) << std::endl;
}""","stats")
if F: sys.exit("FAILED: "+", ".join(F))
open(hp,"w").write(h); open(cp,"w").write(c); print("gate applied OK")
