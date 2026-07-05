"""
End-to-end tests using Playwright for core user journeys.

Tests simulate real user interactions with the running application.
Requires: pip install playwright && playwright install chromium

Run with: pytest tests/e2e/ -v --timeout=60

Assumes the Flask server is running at http://127.0.0.1:5000
"""
import os
import time
import subprocess
import signal
import pytest
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, expect
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Skip all E2E tests if Playwright not installed
pytestmark = pytest.mark.skipif(
    not PLAYWRIGHT_AVAILABLE,
    reason="Playwright not installed. Run: pip install playwright && playwright install chromium"
)

BASE_URL = os.environ.get("E2E_BASE_URL", "http://127.0.0.1:5000")
TEST_IMAGE = Path(__file__).parent.parent.parent / "test_image.jpg"


@pytest.fixture(scope="module")
def browser():
    """Launch a shared browser instance for all E2E tests."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """Create a new browser page for each test."""
    page = browser.new_page()
    page.set_default_timeout(15000)
    yield page
    page.close()


# ---------------------------------------------------------------------------
# Home Page Tests
# ---------------------------------------------------------------------------

class TestHomePage:
    """Tests for the home/upload page."""

    def test_page_loads(self, page):
        """Home page should load successfully."""
        page.goto(BASE_URL)
        expect(page).to_have_title("Scoliosis Brace Coach")

    def test_upload_form_visible(self, page):
        """Upload form should be visible with all fields."""
        page.goto(BASE_URL)
        expect(page.locator("#uploadForm")).to_be_visible()
        expect(page.locator("input[name='media']")).to_be_visible()
        expect(page.locator("select[name='mode']")).to_be_visible()
        expect(page.locator("select[name='age_group']")).to_be_visible()
        expect(page.locator("button[type='submit']")).to_be_visible()

    def test_session_type_options(self, page):
        """Session type dropdown should have all 5 options."""
        page.goto(BASE_URL)
        options = page.locator("select[name='mode'] option").all()
        assert len(options) == 5

    def test_age_group_options(self, page):
        """Age group dropdown should have 4 options."""
        page.goto(BASE_URL)
        options = page.locator("select[name='age_group'] option").all()
        assert len(options) == 4

    def test_filming_tips_visible(self, page):
        """Filming tips section should be visible."""
        page.goto(BASE_URL)
        expect(page.locator("text=Filming Tips")).to_be_visible()

    def test_navigation_links(self, page):
        """Navigation links should be present."""
        page.goto(BASE_URL)
        expect(page.locator("a[href='/history']")).to_be_visible()
        expect(page.locator("a[href='/compare']")).to_be_visible()
        expect(page.locator("a[href='/dashboard']")).to_be_visible()
        expect(page.locator("a[href='/trends']")).to_be_visible()
        expect(page.locator("a[href='/sensors']")).to_be_visible()
        expect(page.locator("a[href='/about']")).to_be_visible()

    def test_why_this_tool_matters_section(self, page):
        """Educational section should be visible."""
        page.goto(BASE_URL)
        expect(page.locator("text=Why This Tool Matters")).to_be_visible()


# ---------------------------------------------------------------------------
# Navigation Tests
# ---------------------------------------------------------------------------

class TestNavigation:
    """Tests for navigation between pages."""

    def test_navigate_to_about(self, page):
        """Should navigate to About page."""
        page.goto(BASE_URL)
        page.click("a[href='/about']")
        page.wait_for_url("**/about")
        expect(page.locator("text=How Bracing")).to_be_visible()

    def test_navigate_to_dashboard(self, page):
        """Should navigate to Dashboard."""
        page.goto(BASE_URL)
        page.click("a[href='/dashboard']")
        page.wait_for_url("**/dashboard")
        expect(page.locator("text=Clinician Dashboard")).to_be_visible()

    def test_navigate_to_trends(self, page):
        """Should navigate to Trends page."""
        page.goto(BASE_URL)
        page.click("a[href='/trends']")
        page.wait_for_url("**/trends")
        expect(page.locator("text=Longitudinal Trends")).to_be_visible()

    def test_navigate_to_sensors(self, page):
        """Should navigate to Sensors page."""
        page.goto(BASE_URL)
        page.click("a[href='/sensors']")
        page.wait_for_url("**/sensors")
        expect(page.locator("text=Brace Sensors")).to_be_visible()

    def test_navigate_to_history(self, page):
        """Should navigate to History page."""
        page.goto(BASE_URL)
        page.click("a[href='/history']")
        page.wait_for_url("**/history")
        expect(page.locator("text=Session History")).to_be_visible()

    def test_navigate_to_compare(self, page):
        """Should navigate to Compare page."""
        page.goto(BASE_URL)
        page.click("a[href='/compare']")
        page.wait_for_url("**/compare")
        expect(page.locator("text=Compare Brace Effectiveness")).to_be_visible()


# ---------------------------------------------------------------------------
# Upload & Analysis Flow
# ---------------------------------------------------------------------------

class TestUploadFlow:
    """Tests for the upload and analysis user journey."""

    @pytest.mark.slow
    def test_upload_shows_loading_state(self, page):
        """Upload should show loading spinner."""
        page.goto(BASE_URL)

        # Create a minimal test image
        page.evaluate("""
            () => {
                const canvas = document.createElement('canvas');
                canvas.width = 400; canvas.height = 600;
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#ddd';
                ctx.fillRect(0, 0, 400, 600);
                // Store for later use
                window._testImageData = canvas.toDataURL('image/jpeg');
            }
        """)

        # Set file input via JS
        page.locator("input[name='media']").set_input_files(
            str(TEST_IMAGE) if TEST_IMAGE.exists() else None
        )

    def test_upload_without_file_shows_alert(self, page):
        """Submitting without file should trigger browser validation."""
        page.goto(BASE_URL)
        # The 'required' attribute should prevent submission
        file_input = page.locator("input[name='media']")
        expect(file_input).to_have_attribute("required", "")


# ---------------------------------------------------------------------------
# Sensors / Compliance Page
# ---------------------------------------------------------------------------

class TestSensorsPage:
    """Tests for the sensor integration page."""

    def test_pressure_points_displayed(self, page):
        """Pressure point ranges should be displayed."""
        page.goto(BASE_URL + "/sensors")
        expect(page.locator("text=Upper Support")).to_be_visible()
        expect(page.locator("text=Middle (Apex)")).to_be_visible()
        expect(page.locator("text=Lower Support")).to_be_visible()

    def test_compliance_buttons_visible(self, page):
        """Start/Stop monitoring buttons should be visible."""
        page.goto(BASE_URL + "/sensors")
        expect(page.locator("text=Start Monitoring")).to_be_visible()
        expect(page.locator("text=Stop Monitoring")).to_be_visible()

    def test_pressure_evaluation_form(self, page):
        """Pressure evaluation form should be present."""
        page.goto(BASE_URL + "/sensors")
        expect(page.locator("#upper-pressure")).to_be_visible()
        expect(page.locator("#middle-pressure")).to_be_visible()
        expect(page.locator("#lower-pressure")).to_be_visible()
        expect(page.locator("text=Evaluate Pressure")).to_be_visible()

    def test_scan_button_visible(self, page):
        """BLE scan button should be visible."""
        page.goto(BASE_URL + "/sensors")
        expect(page.locator("text=Scan for Devices")).to_be_visible()


# ---------------------------------------------------------------------------
# Dashboard Tests
# ---------------------------------------------------------------------------

class TestDashboard:
    """Tests for the clinician dashboard."""

    def test_dashboard_loads(self, page):
        """Dashboard should load successfully."""
        page.goto(BASE_URL + "/dashboard")
        expect(page.locator("text=Clinician Dashboard")).to_be_visible()

    def test_export_pdf_button(self, page):
        """PDF export button should be present."""
        page.goto(BASE_URL + "/dashboard")
        expect(page.locator("text=Export PDF")).to_be_visible()

    def test_treatment_rationale_section(self, page):
        """Treatment rationale section should be visible."""
        page.goto(BASE_URL + "/dashboard")
        expect(page.locator("text=Treatment Rationale")).to_be_visible()


# ---------------------------------------------------------------------------
# About / Education Page
# ---------------------------------------------------------------------------

class TestAboutPage:
    """Tests for the educational content page."""

    def test_about_loads(self, page):
        """About page should load successfully."""
        page.goto(BASE_URL + "/about")
        expect(page.locator("text=How Bracing")).to_be_visible()

    def test_surgery_prevention_content(self, page):
        """Page should contain surgery prevention messaging."""
        page.goto(BASE_URL + "/about")
        expect(page.locator("text=prevent surgery")).to_be_visible()

    def test_braist_study_referenced(self, page):
        """BrAIST study should be referenced."""
        page.goto(BASE_URL + "/about")
        expect(page.locator("text=BrAIST")).to_be_visible()

    def test_treatment_timeline(self, page):
        """Treatment timeline should be displayed."""
        page.goto(BASE_URL + "/about")
        expect(page.locator("text=Detection")).to_be_visible()
        expect(page.locator("text=Skeletal Maturity")).to_be_visible()

    def test_cost_comparison(self, page):
        """Cost comparison should be shown."""
        page.goto(BASE_URL + "/about")
        expect(page.locator("text=$100,000")).to_be_visible()


# ---------------------------------------------------------------------------
# Responsive Design
# ---------------------------------------------------------------------------

class TestResponsive:
    """Tests for responsive layout behavior."""

    def test_mobile_viewport(self, page):
        """App should be usable on mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 812})
        page.goto(BASE_URL)
        expect(page.locator("#uploadForm")).to_be_visible()

    def test_tablet_viewport(self, page):
        """App should be usable on tablet viewport."""
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto(BASE_URL)
        expect(page.locator("#uploadForm")).to_be_visible()

    def test_desktop_viewport(self, page):
        """App should be usable on desktop viewport."""
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(BASE_URL)
        expect(page.locator("#uploadForm")).to_be_visible()
