/**
 * k6 Load Test: Scoliosis Brace Coach API
 *
 * Tests the application under load to identify performance bottlenecks
 * and verify stability under concurrent usage.
 *
 * Prerequisites: Install k6 - https://k6.io/docs/get-started/installation/
 * Run: k6 run tests/load/k6_api_load.js
 *
 * Scenarios:
 * 1. Homepage load (constant 10 VUs for 30s)
 * 2. API endpoint stress test (ramp 1-50 VUs over 2m)
 * 3. Upload + analysis pipeline (constant 5 VUs for 1m)
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// ---------------------------------------------------------------------------
// Custom metrics
// ---------------------------------------------------------------------------
const uploadSuccessRate = new Rate('upload_success_rate');
const apiResponseTime = new Trend('api_response_time');
const errorCount = new Counter('errors');

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------
const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:5000';

export const options = {
  scenarios: {
    // Scenario 1: Steady-state homepage traffic
    homepage_load: {
      executor: 'constant-vus',
      vus: 10,
      duration: '30s',
      exec: 'testHomepage',
      startTime: '0s',
    },

    // Scenario 2: API stress test (ramp up)
    api_stress: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 20 },
        { duration: '1m', target: 20 },
        { duration: '30s', target: 50 },
        { duration: '1m', target: 50 },
        { duration: '30s', target: 0 },
      ],
      exec: 'testAPIEndpoints',
      startTime: '35s',
    },

    // Scenario 3: Upload pipeline (limited concurrency)
    upload_pipeline: {
      executor: 'constant-vus',
      vus: 5,
      duration: '1m',
      exec: 'testUploadPipeline',
      startTime: '0s',
    },
  },

  thresholds: {
    http_req_duration: ['p(95)<3000', 'p(99)<5000'],  // 95th < 3s, 99th < 5s
    http_req_failed: ['rate<0.1'],                      // < 10% failure rate
    upload_success_rate: ['rate>0.8'],                  // > 80% upload success
  },
};

// ---------------------------------------------------------------------------
// Scenario 1: Homepage Load
// ---------------------------------------------------------------------------
export function testHomepage() {
  group('Homepage', () => {
    const res = http.get(`${BASE_URL}/`);
    check(res, {
      'homepage status 200': (r) => r.status === 200,
      'homepage has content': (r) => r.body.includes('Scoliosis Brace Coach'),
      'homepage response time < 1s': (r) => r.timings.duration < 1000,
    });
    apiResponseTime.add(res.timings.duration);
    if (res.status !== 200) errorCount.add(1);
  });

  sleep(Math.random() * 2 + 1);  // 1-3s think time
}

// ---------------------------------------------------------------------------
// Scenario 2: API Endpoint Stress Test
// ---------------------------------------------------------------------------
export function testAPIEndpoints() {
  group('API Endpoints', () => {
    // Test trends endpoint
    let res = http.get(`${BASE_URL}/api/trends`);
    check(res, {
      'trends status 200': (r) => r.status === 200,
      'trends has JSON': (r) => {
        try { JSON.parse(r.body); return true; } catch { return false; }
      },
    });
    apiResponseTime.add(res.timings.duration);

    // Test progression report
    res = http.get(`${BASE_URL}/api/progression-report`);
    check(res, {
      'progression status 200': (r) => r.status === 200,
    });
    apiResponseTime.add(res.timings.duration);

    // Test pressure evaluate
    const payload = JSON.stringify({
      upper_support: 50,
      middle_pressure: 60,
      lower_support: 45,
      skin_temp: 34.5,
    });
    const params = { headers: { 'Content-Type': 'application/json' } };
    res = http.post(`${BASE_URL}/api/pressure/evaluate`, payload, params);
    check(res, {
      'pressure evaluate status 200': (r) => r.status === 200,
      'pressure has score': (r) => {
        try { return JSON.parse(r.body).score !== undefined; } catch { return false; }
      },
    });
    apiResponseTime.add(res.timings.duration);

    // Test PDF report
    res = http.get(`${BASE_URL}/api/pdf-report`);
    check(res, {
      'pdf status 200': (r) => r.status === 200,
      'pdf is binary': (r) => r.headers['Content-Type'] === 'application/pdf',
    });
    apiResponseTime.add(res.timings.duration);
  });

  sleep(Math.random() * 3 + 1);  // 1-4s think time
}

// ---------------------------------------------------------------------------
// Scenario 3: Upload Pipeline
// ---------------------------------------------------------------------------
export function testUploadPipeline() {
  group('Upload Pipeline', () => {
    // Create a minimal JPEG payload (smallest valid JPEG)
    const payload = http.file(
      open(`${BASE_URL.replace('http://127.0.0.1:5000', '')}/test_image.jpg`, 'b') ||
      new Uint8Array([0xFF, 0xD8, 0xFF, 0xE0]),  // fallback minimal JPEG header
      'test.jpg',
      { type: 'image/jpeg' }
    );

    const formData = {
      media: payload,
      mode: 'standing_no_brace',
      age_group: 'under15',
    };

    const res = http.post(`${BASE_URL}/upload`, formData);
    const success = res.status === 200 && res.body.includes('job_id');
    uploadSuccessRate.add(success);

    if (success) {
      const jobId = JSON.parse(res.body).job_id;

      // Poll for completion (max 30 seconds)
      let completed = false;
      for (let i = 0; i < 30; i++) {
        sleep(1);
        const statusRes = http.get(`${BASE_URL}/status/${jobId}`);
        if (statusRes.status === 200) {
          const status = JSON.parse(statusRes.body);
          if (status.status === 'done' || status.status === 'error') {
            completed = true;
            check(statusRes, {
              'analysis completed': (r) => {
                const s = JSON.parse(r.body);
                return s.status === 'done' || s.status === 'error';
              },
            });
            break;
          }
        }
      }

      if (!completed) {
        errorCount.add(1);
        console.error(`Upload ${jobId} did not complete within 30s`);
      }
    } else {
      errorCount.add(1);
    }
  });

  sleep(Math.random() * 2 + 1);
}

// ---------------------------------------------------------------------------
// Summary handler
// ---------------------------------------------------------------------------
export function handleSummary(data) {
  return {
    'tests/load/load_test_results.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
