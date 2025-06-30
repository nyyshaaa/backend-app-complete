import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { parseHTML } from 'k6/html';

// Open the file in the init stage (global scope)
const testFile = open('./test-profile-avatar.jpeg', 'image/jpeg');

export const options = {
  vus: 10,            // virtual users
  duration: '10s',     // test length
  thresholds: {
    'http_req_duration{step:signature}': ['p(90)<200'],
    'http_req_duration{step:upload}': ['p(90)<1000'],
  },
};

const API_ROOT  = 'http://127.0.0.1:8000/api/v1'; 
// const CLOUD_URL = ''; // will be filled per-iteration
// Add token while testing
const JWT       = 'Bearer ';
// const FILE_PATH = './test-profile-avatar.jpg';

export default function () {
  group('Pattern A: Direct Upload Flow', () => {
    // Step 1: fetch signature
    let sigRes = http.get(`${API_ROOT}/uploads-direct/avatar-signature`, {
      headers: { Authorization: JWT },
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
    check(uploadRes, { 'uploaded to Cloudinary': (r) => r.status === 200 });

  });

  // small pause to avoid overwhelming
  sleep(0.1);
}
