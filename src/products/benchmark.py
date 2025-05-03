import asyncio , time, httpx,os,statistics
from dotenv import load_dotenv

load_dotenv()

frost_id=50044


BASE_URL="http://127.0.0.1:8000/api/v1/frosties"
headers={"Authorization":"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImVtYWlsIjoiZnJvc3R5QGRyZWFtZXIuY29tIiwidXNlcl9pZCI6NTAwNDZ9LCJleHAiOjE3NDYyMzA4ODksImp0aSI6ImM5ZDJhNTczLTViMjEtNDE2NC05ZWU4LTMwYWExZDRkNzM0MSIsInJlZnJlc2giOmZhbHNlfQ.3mhr3lrblKnK97LZTqSYrqi4ipa1cej3dRy4rSLPWME"}


endpoints = {
    "post": {
        "method": "POST",
        "url": f"{BASE_URL}/",
        "headers": headers,
        "json":{
            "title":"Strawberry Choco Icecream",
            "qty":1000,
            "price":1000}
    },
    "get": {
        "method": "GET",
        "url": f"{BASE_URL}/{frost_id}",
        "headers": headers
    },
    "patch": {
        "method": "PATCH",
        "url": f"{BASE_URL}/{frost_id}",
        "headers": headers,
        # "json": {
        #     "url_link": new_post,
        #     "custom_slug": "prifile",
        #     "exp_date": None
        # },
    }
}


def stats_calc(res_times,endpoint,iterations):
    avg_time=sum(res_times)/len(res_times)
    min_time = min(res_times)
    max_time = max(res_times)
    median_time = statistics.median(res_times)
    p90 = statistics.quantiles(res_times, n=100)[89]  # 90th percentile approximation

    print(f"\nBenchmark Results for {endpoint}:")
    print(f"Requests run: {iterations}")
    print(f"Average response time: {avg_time:.4f} seconds")
    print(f"Median response time: {median_time:.4f} seconds")
    print(f"Minimum response time: {min_time:.4f} seconds")
    print(f"Maximum response time: {max_time:.4f} seconds")
    print(f"90th percentile response time: {p90:.4f} seconds\n")


async def benchmark(full_endpoint:dict,iterations:int=80,warmup:int=5):
    url=full_endpoint["url"]
    method=full_endpoint.get("method","GET")
    headers=full_endpoint.get("headers",{})
    payload=full_endpoint.get("json",None)

    async with httpx.AsyncClient() as client:
        for _ in range(warmup):
            if method.upper=="GET":
                await client.get(url,headers=headers,follow_redirects=False)
            elif method.upper=="POST":
                await client.post(url,headers=headers,json=payload)
            elif method.upper=="PATCH":
                await client.post(url,headers=headers)

        res_times=[]
        for i in range(iterations):
            start_time=time.perf_counter()
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, follow_redirects=False)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=payload)
            elif method.upper=="PATCH":
                response=await client.post(url,headers=headers)
            # print(response)
            end_time=time.perf_counter()
            process_time=end_time-start_time
            res_times.append(process_time)
            # print(f"Iteration {i+1}: {process_time:.4f} s")
        
    stats_calc(res_times,url,iterations)
    


async def main():

    for key,endpoint in endpoints.items():
        print(f"{key}:{endpoint['url']}")
    
    choice=input("Enter the endpoint key to benchmark: ").strip()
    if choice not in endpoints:
        print(f"Endpoint '{choice}' not found. Please try with valid key present before :")

    endpoint_to_test = endpoints[choice]
    
    print(f"Benchmarking endpoint '{choice}' with URL: {endpoint_to_test['url']}")
    await benchmark(endpoint_to_test,iterations=100)

if __name__ == "__main__":
    asyncio.run(main())


