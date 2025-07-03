export const test_config = {
    TEST_TOKEN: __ENV.TEST_TOKEN 
  };


// cd to folder with benchmark file and run --
// k6 run --env TEST_TOKEN='Bearer ' benchmark.js