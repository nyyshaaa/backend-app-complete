import http from 'k6/http';
import { check, group, sleep } from 'k6';

// Open the file in the init stage (global scope)
const testFile = open('../assets/test-profile-avatar.jpeg', 'image/jpeg');

export const options = {
  vus: 10,            // virtual users
  duration: '10s',     // test length
  thresholds: {
    'http_req_duration{step:upload}': ['p(90)<1000'],
  },
}; 

const API_ROOT  = 'http://127.0.0.1:8000/api/v1'; 

// Add token while testing
const JWT = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImVtYWlsIjoiZnJvc3RAZHJlYW1lci5jb20iLCJ1c2VyX2lkIjo1MDA0N30sImV4cCI6MTc1MTM5MTM5OSwianRpIjoiOTE2NTE0YTEtZjdlYy00MjE3LTkxZmQtYzRhZmQxNTg5Y2QwIiwicmVmcmVzaCI6ZmFsc2V9.Ymd7rVa80hy7RnO86hxfRnCvJ04DN3urR8fVwxOdgtI';


export default function () {
  group('Pattern A: Queue Upload Flow via server', () => {
   
    // Step 1: upload to Cloudinary
    let form = {
      file: http.file(testFile),  // Use the pre-loaded file
    };
    let params = {
        headers: {
          Authorization: JWT,
        },
        tags: { step: 'upload' },
      };

    let uploadRes = http.post(`${API_ROOT}/uploads-queue/`, form,params);
    check(uploadRes, { 
      'status is 200': (r) => r.status === 200,
      'response has upload_id': (r) => r.json('upload_id') !== undefined,
     });

  });

  // small pause to avoid overwhelming
  sleep(0.1);
}
