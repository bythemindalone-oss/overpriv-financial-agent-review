# Rendering-only corpus derivative

Original data/corpus_traps.json remains unchanged. This derivative adds domain_desc from the canonical base-task domain metadata to each of18 trap tasks. No request,tool description,gold,label,selection,or result is changed. This is a current reproducible schema repair,not historical evidence of the original fixing commit.

Use the original input when replaying recorded evidence. Use this documented derivative only to prepare exact prompt schemas for future rendering tests. Original versus derivative hashes must both be recorded; historical provenance trap hashes are not overwritten.
