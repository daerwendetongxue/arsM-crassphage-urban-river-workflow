# arsM/crAssphage Pipeline Lessons

These rules come from the Yamuna River pilot and should be followed in future runs.

1. Do not save full crAssphage alignments as BAM just to count reads.
   Use streamed counting: `bowtie2 --no-unal ... | samtools view -c -`.

2. Keep large-data cleanup strict.
   Delete SRA/raw FASTQ after clean FASTQ exists, delete clean FASTQ after assembly succeeds,
   and delete failed assembly temporary folders immediately.

3. Prefer full assembly after giving WSL enough memory.
   The first full MEGAHIT failed with exit code `-9` because WSL had only about 7.7GB.
   WSL is now configured with a 12GB memory limit and 12GB swap. Downsampling is only a fallback.

4. Mark downsampled outputs clearly.
   Do not mix downsampled assembly tables with full-sample assembly tables.

5. Use tabular `seqkit stats` output.
   Prefer `seqkit stats -a -T ...` so tables are easy to parse.

6. Avoid interrupting production commands with pipes like `| head`.
   This can leave empty or partial output files.

7. Parse HMMER domtblout fields carefully.
   Use full E-value `$7`, domain conditional E-value `$12`, and domain independent E-value `$13`.
   Do not compare score `$14` to an E-value cutoff.

8. Treat a single crAssphage genome as a narrow sewage marker.
   Zero mapping to NC_024711.1 does not prove no sewage signal. Later expand to a broader crAss-like reference set.

9. Avoid repeated Windows background launches for WSL jobs.
   Prefer one WSL-side runner with log/PID monitoring. Windows may not reliably report background WSL PIDs and can produce confusing system prompts.

10. Keep `.wslconfig` minimal.
    The `pageReporting=true` line triggered a WSL configuration warning on this machine.
    Use only stable settings unless there is a clear need: `memory`, `processors`, `swap`, and `localhostForwarding`.

11. Default future runs should use sample-level streaming cleanup, not river-level FASTQ retention.
    For large river batches, run each sample through download, FASTQ conversion, QC, crAssphage counting,
    assembly, gene prediction, HMM screening, and candidate extraction; then delete SRA/raw FASTQ/clean FASTQ
    and full assembly files before starting the next sample. After all samples yield small candidate files,
    build the river-level arsM catalog, then re-download/re-clean one sample at a time for final abundance
    mapping to the shared catalog. This costs extra time/network but prevents multiple samples of raw reads
    from occupying the disk at once. Use `/mnt/f/As/scripts/run_river_streaming_twopass.sh` as the default runner.

12. Do not call `log()` directly inside a redirected table-writing block.
    Redirect progress logs to stderr inside such blocks, otherwise progress lines contaminate TSV tables.

13. MEGAHIT memory should leave real headroom.
    On this 16GB Windows machine with WSL capped at 12GB, `--memory 0.85` drove WSL into heavy swap.
    Use `MEGAHIT_MEMORY=0.70` by default for full river runs unless the user explicitly accepts reduced desktop responsiveness.

14. If MEGAHIT still swaps heavily at `k-min=41`, keep all reads but simplify assembly.
    Use `MEGAHIT_K_MIN=61`, `MEGAHIT_THREADS=6`, and `MEGAHIT_MEMORY=0.60` before considering downsampling.

15. On this machine, `MEGAHIT_K_MIN=61`, `MEGAHIT_THREADS=6`, `MEGAHIT_MEMORY=0.60` still pushed Windows available memory below 1GB.
    For unattended full-river runs, use `MEGAHIT_K_MIN=91`, `MEGAHIT_THREADS=4`, and `MEGAHIT_MEMORY=0.45`.
    This is still full-read assembly, but it is a resource-adjusted assembly and should be reported as such.

16. WSL memory should not be capped at 12GB on this 16GB laptop for unattended MEGAHIT.
    The VM can leave Windows with less than 1GB available even when Linux is not swapping.
    Use `.wslconfig` memory=9GB and swap=8GB for this project unless the user explicitly prioritizes speed over desktop responsiveness.

17. If MEGAHIT fails with `std::bad_alloc` in `seq2sdbg`, lowering memory alone is not enough.
    Reduce graph complexity while keeping full reads: use `MEGAHIT_K_MIN=121`, `MEGAHIT_MIN_COUNT=3`, and `MEGAHIT_NO_MERCY=1`.
    Report this as resource-adjusted full-read assembly.

18. Avoid awk ternary expressions in portable runner scripts on this WSL environment.
    `awk 'END{print NR>0?NR-1:0}'` failed here. Use explicit `if/else` blocks instead.

19. Detect MUSCLE v5 broadly.
    This environment reports `muscle 5.3...`, not `MUSCLE v5`; v5 needs `-align/-output`, while older MUSCLE uses `-in/-out`.

20. Watch WSL file cache after large FASTQ/assembly scans.
    WSL may show most memory as `buff/cache` while Windows available memory falls below 1GB.
    If the active process is not memory-heavy, run `sync; echo 3 > /proc/sys/vm/drop_caches` in WSL to reduce desktop impact.

21. Use MUSCLE v5 `-super5` for large raw candidate alignments.
    With 667 arsM candidates, `muscle -align` entered a very slow consistency step.
    For more than about 500 raw candidates, use `muscle -super5 input.fa -output output.afa` and report it as a fast screening alignment.

22. Avoid C-drive temporary files for this project.
    Keep generated scripts, figures, logs, and project outputs under `F:\As` or `D:\codex`.
    For Windows-side helper scripts, set `TEMP` and `TMP` to `F:\As\tmp`.
    For WSL river runs, set `TMPDIR` and `XDG_CACHE_HOME` under the current river project work directory.

23. Do not rely only on a Windows PID to supervise WSL bioinformatics jobs.
    A Windows-side `wsl.exe` process can exit or become stale while the Linux-side workflow is still active.
    Supervisors should poll WSL process names plus the river `status/DONE.txt` marker before deciding whether to
    continue, stop, or launch the next river.

24. Support both paired-end and single-end SRA/FASTQ layouts.
    Some runs in the river set, for example `SRR26856457`, are reported as paired-end in metadata but yield a single
    FASTQ file from `fasterq-dump` or ENA. Pipeline stages must switch between Bowtie2 `-1/-2` and `-U`, and between
    MEGAHIT paired input and `-r` single-read input based on actual files.

25. Prefer ENA FASTQ download before SRA conversion when available.
    ENA `.fastq.gz` avoids the high temporary disk use of SRA plus expanded FASTQ. Query ENA with retry logic, download
    via `aria2c`, and fall back to SRA only if ENA has no usable FASTQ link or download fails.
