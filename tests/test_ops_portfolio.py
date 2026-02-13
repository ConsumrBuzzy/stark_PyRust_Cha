import asyncio

from src.ops.portfolio import PortfolioMonitor


def test_portfolio_summary_and_report(tmp_path):
    monitor = PortfolioMonitor()
    summary = asyncio.run(monitor.generate_portfolio_summary())
    report = monitor.format_markdown_report(summary)
    assert summary.total_usd_value >= 0
    assert "Portfolio Summary" in report
    report_path = tmp_path / "report.md"
    report_path.write_text(report, encoding="utf-8")
    assert report_path.exists()
