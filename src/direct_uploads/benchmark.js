import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { test_config } from '../test_config.js';

// Open the file in the init stage (global scope)
const testFile = open('../assets/test-profile-avatar.jpeg', 'image/jpeg');

export const options = {
  vus: 10,            // virtual users
  duration: '10s',     // test length
  thresholds: {
    // Latency percentiles
    'http_req_duration{step:signature}': ['p(50)<100', 'p(95)<200'],
    'http_req_duration{step:upload}': [
      'p(50)<800',   // p50 under 800ms
      'p(90)<1000',  // p90 under 1000ms
      'p(95)<1200',  // p95 under 1200ms
      'p(99)<2000',  // p99 under 2000ms
    ],
    // Failure rate threshold
    'http_req_failed{step:upload}': ['rate<0.05'], // less than 5% failures
  },
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(50)', 'p(90)', 'p(95)', 'p(99)'],
}; 

const API_ROOT  = 'http://127.0.0.1:8000/api/v1'; 
// const CLOUD_URL = ''; // will be filled per-iteration
// Add token while testing
const JWT=test_config.TEST_TOKEN;
// const FILE_PATH = './test-profile-avatar.jpg';

export default function () {
  group('Pattern A: Direct Upload Flow', () => {
    // Step 1: fetch signature
    let sigRes = http.get(`${API_ROOT}/uploads-direct/avatar-signature`, {
      
      tags: { step: 'signature' }
    });
    check(sigRes, { 'got signature': (r) => r.status === 200 });
    const sig = sigRes.json();

    // Step 2: upload to Cloudinary
    let form = {
      file: http.file(testFile),  // Use the pre-loaded file
      api_key: sig.api_key,
      signature: sig.signature,
      timestamp: sig.timestamp,
      folder:    sig.folder,
      public_id: sig.public_id,
      overwrite: 'true',
      invalidate: 'true',
      eager: sig.eager.join(','),
    };
    let uploadRes = http.post(sig.upload_url, form, {
      tags: { step: 'upload' }
    });
    check(uploadRes, { 'uploaded to Cloudinary': (r) => r.status === 200,
      'response has url': (r) => {
        const url = r.json('url');
        return typeof url === 'string' && url.length > 0;
      },
    });
    

  });

  // small pause to avoid overwhelming
  sleep(0.1);
}
