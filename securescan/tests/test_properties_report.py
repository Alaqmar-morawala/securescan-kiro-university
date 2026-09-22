"""Property P2: severity ordering High > Medium > Low > Info preserved in reports."""

from hypothesis import given, settings
from hypothesis import strategies as st

from scanner.services import SEVERITY_RANK, order_findings


@given(
    findings=st.lists(
        st.fixed_dictionaries(
            {
                "name": st.text(min_size=1, max_size=30),
                "severity": st.sampled_from(["High", "Medium", "Low", "Info"]),
            }
        ),
        min_size=0,
        max_size=25,
    )
)
@settings(max_examples=150)
def test_severity_sort_invariant(findings):
    ordered = order_findings(findings)
    ranks = [SEVERITY_RANK[f["severity"]] for f in ordered]
    assert ranks == sorted(ranks, reverse=True)
    assert len(ordered) == len(findings)
