#!/usr/bin/env python3
"""Make an instrumented copy of the author's verify.cpp that reports the accepted-leaf ledger.

Additions (nothing else changes; the stock binary is the fidelity check and its counts must match
certificate/cpp_verification.json exactly):
  * acceptBasic(): classify the accepted box by its maximum gap width (bucket = bit length), and
    accumulate the exact volume (__int128) per bucket, plus the count;
  * at the end, print one JSON line "KLEDGER {"buckets":[[bucket,count,volume_low,volume_high]],...}"
    and, if KDUMP is set, write every accepted box with max width >= KDW to that file.

Usage: python3 patch_dump.py <verify.cpp> <out.cpp> && build with the same flags.
"""
import sys
from pathlib import Path

src = Path(sys.argv[1]).read_text()

ACCEPT = """    void acceptBasic() noexcept {
        ++statistics_.leaves;
        ++statistics_.basic;
    }"""
NEW_ACCEPT = """    void acceptBasic() noexcept {
        ++statistics_.leaves;
        ++statistics_.basic;
        ledgerRecord(box_);
    }

  public:
    // --- instrumented ledger (added; search semantics untouched) ---
    struct Bucket { std::uint64_t count{}; unsigned __int128 volume{}; };
    static constexpr std::size_t kBucketCount{24U};
    std::array<Bucket, kBucketCount> ledger{};
    std::FILE* dumpFile{nullptr};
    std::size_t dumpMinWidth{1U};

    void ledgerRecord(const Box& box) noexcept {
        Grid width{0};
        for (std::size_t gap = 0U; gap < kGapCount; ++gap) {
            width = std::max(width, box.upper[gap] - box.lower[gap]);
        }
        std::size_t bucket{0U};
        for (Grid w{width}; w > 0U; w >>= 1U) { ++bucket; }
        if (bucket >= kBucketCount) { bucket = kBucketCount - 1U; }
        unsigned __int128 volume{1U};
        for (std::size_t gap = 0U; gap < kGapCount; ++gap) {
            volume *= (box.upper[gap] - box.lower[gap]);
        }
        ++ledger[bucket].count;
        ledger[bucket].volume += volume;
        if ((dumpFile != nullptr) && (width >= dumpMinWidth)) {
            for (std::size_t gap = 0U; gap < kGapCount; ++gap) {
                std::fprintf(dumpFile, "%llu ", static_cast<unsigned long long>(box.lower[gap]));
            }
            for (std::size_t gap = 0U; gap < kGapCount; ++gap) {
                std::fprintf(dumpFile, "%llu%c", static_cast<unsigned long long>(box.upper[gap]),
                             (gap + 1U == kGapCount) ? '\\n' : ' ');
            }
        }
    }

  private:
    Box box_{};"""
assert ACCEPT in src, "acceptBasic body not found"
src = src.replace(ACCEPT, NEW_ACCEPT)

# keep a copy of the box being examined, so acceptBasic can record it
OLD_LOOP = """            Box box{stack_[stackSize]};
            ++statistics_.nodes;"""
NEW_LOOP = """            Box box{stack_[stackSize]};
            box_ = box;
            ++statistics_.nodes;"""
assert OLD_LOOP in src
src = src.replace(OLD_LOOP, NEW_LOOP)

# report the ledger before the statistics line
OLD_OUT = """    writeStatistics(std::cout, "PASS_COB_CONTINUUM", search.statistics());"""
NEW_OUT = """    writeStatistics(std::cout, "PASS_COB_CONTINUUM", search.statistics());
    {
        std::cout << "KLEDGER {\\"buckets\\":[";
        for (std::size_t bucket = 0U; bucket < BoxSearch::kBucketCount; ++bucket) {
            if (bucket > 0U) { std::cout << ','; }
            const unsigned __int128 v{search.ledger[bucket].volume};
            const unsigned long long low{static_cast<unsigned long long>(v % 10000000000000000000ULL)};
            const unsigned long long high{static_cast<unsigned long long>(v / 10000000000000000000ULL)};
            std::cout << "[" << bucket << ',' << search.ledger[bucket].count << ',' << high << ','
                      << low << ']';
        }
        std::cout << "]}\\n";
    }"""
assert OLD_OUT in src
src = src.replace(OLD_OUT, NEW_OUT)

# open the dump file / read KDW before the search runs
OLD_RUN = """    const std::expected<void, Error> outcome{search.run()};"""
NEW_RUN = """    const char* const dumpPath{std::getenv("KDUMP")};
    if (dumpPath != nullptr) {
        search.dumpFile = std::fopen(dumpPath, "w");
        if (search.dumpFile == nullptr) { std::cerr << "verify: cannot open KDUMP\\n"; return ExitCode::InputError; }
        const char* const dw{std::getenv("KDW")};
        search.dumpMinWidth = (dw != nullptr) ? static_cast<std::size_t>(std::stoull(dw)) : 1U;
    }
    const std::expected<void, Error> outcome{search.run()};
    if (search.dumpFile != nullptr) { std::fclose(search.dumpFile); }"""
assert OLD_RUN in src
src = src.replace(OLD_RUN, NEW_RUN)

src = src.replace("#include <cstdint>", "#include <cstdint>\n#include <cstdio>\n#include <cstdlib>")

Path(sys.argv[2]).write_text(src)
print("wrote", sys.argv[2])
