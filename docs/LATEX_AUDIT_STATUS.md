# LaTeX submission audit status

The first reproducible manuscript build reached `pdflatex` and failed because the Ubuntu TeX install did not include `IEEEtran.cls`. The audit workflow is updated to install `texlive-publishers`, which provides the IEEEtran class on Debian/Ubuntu TeX Live packaging. A paper-path trigger is included so the corrected workflow can be exercised on pull request synchronization.

This is production validation only; no scientific protocol, thresholds, policy logic, numerical results, or manuscript claims are changed.
