import http from 'k6/http';

let access_token="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImVtYWlsIjoiZnJvc3RAZHJlYW1lci5jb20iLCJ1c2VyX2lkIjo1MDA0N30sImV4cCI6MTc0NjYxODM5NywianRpIjoiYjQ5OWQ1ODEtYzE4Ny00ODBjLTlmZjYtZmI4MjU1MDQzYmRmIiwicmVmcmVzaCI6ZmFsc2V9.4lnyxXdo8OUXjmoC0ZbHAVZWCAhj7k2QTLli52MWbTQ"

export let options = {
  scenarios: {
    seq: {
      executor: 'shared-iterations',
      vus: 1,
      iterations: 200,
      maxDuration: '30s',
    },
    // light: {
    //   executor: 'constant-vus',
    //   vus: 5,            // 5 concurrent users
    //   duration: '30s',
    // }
  },

  // Fail if 95% of requests take longer than 50 ms
  thresholds: {
    http_req_duration: ['p(95)<50'],
  },

  // Show these stats in the summary
  summaryTrendStats: ['min', 'med', 'avg', 'max', 'p(90)', 'p(95)', 'p(99)'],

  // Keep connections alive (true by default)
  noConnectionReuse: false,

  // Don’t waste time reading body data you don’t need
  discardResponseBodies: true,
};

export default function () {
  const url = `http://localhost:8000/api/v1/frosties/50145?cb=${__ITER}`;
  const params = { headers: { 'Cache-Control': 'no-cache' , "Authorization":access_token}};
  http.get(url, params);
}

// current product details
// {
//   "id": 50145,
//   "user_id": 50047,
//   "title": "firefly lantern",
//   "description": null,
//   "qty": 200,
//   "created_at": "2025-05-03T20:38:14.019253",
//   "updated_at": "2025-05-03T20:38:14.019262",
//   "price": "100000.00"
// }

//2nd product 
// {
//   "id": 50197,
//   "user_id": 50047,
//   "title": "flying frozen lights",
//   "description": null,
//   "qty": 100,
//   "created_at": "2025-05-07T17:51:56.848300",
//   "updated_at": "2025-05-07T17:51:56.848309",
//   "price": "1000.00"
// }
