Client

[Error] Failed to load resource: the server responded with a status of 500 () (reviews, line 0)
[Error] Failed to create comprehensive review: – Error: Server error. Please try again later. — BcmEhWWP.js:1:880
Error: Server error. Please try again later. — BcmEhWWP.js:1:880
	(anonymous function) (BcmEhWWP.js:1:4878)
[Error] Review submission failed: – Error: Server error. Please try again later. — BcmEhWWP.js:1:880
Error: Server error. Please try again later. — BcmEhWWP.js:1:880
	(anonymous function) (12.VYNEC06b.js:1:20549)
[Error] Error details: – {message: "Server error. Please try again later.", status: undefined, response: undefined, …}
{message: "Server error. Please try again later.", status: undefined, response: undefined, data: Object}Object
	(anonymous function) (12.VYNEC06b.js:1:21642)

render

2025-08-18T02:04:25.278359736Z INFO:routes.reviews:Creating review with data: freight_forwarder_id=7120060b-dd84-44eb-bdab-123f531641a3, city=Frankfurt am Main, country=Germany
2025-08-18T02:04:25.278395557Z INFO:routes.reviews:Using city=Frankfurt am Main, country=Germany from location, dummy branch_id=364e0dd7-a311-4d51-a833-e036dd16bdd0
2025-08-18T02:04:25.27854544Z INFO:routes.reviews:Review object created successfully: <database.models.Review object at 0x70e7965d3e10>
2025-08-18T02:04:25.296530077Z INFO:routes.reviews:Review added to session and flushed, ID: 61796c5f-fa9c-4ef9-83b8-8768f3e15d01
2025-08-18T02:04:25.402115623Z INFO:routes.reviews:Category scores created successfully for review 61796c5f-fa9c-4ef9-83b8-8768f3e15d01 with category and score fields set
2025-08-18T02:04:25.443549149Z INFO:routes.reviews:Review committed successfully: 61796c5f-fa9c-4ef9-83b8-8768f3e15d01
2025-08-18T02:04:25.446519243Z INFO:     182.19.225.177:0 - "POST /api/reviews/ HTTP/1.1" 500 Internal Server Error
2025-08-18T02:07:41.216246975Z INFO:     182.19.225.177:0 - "GET /api/users/me HTTP/1.1" 401 Unauthorized
2025-08-18T02:07:44.09341292Z ==> Detected service running on port 10000
2025-08-18T02:07:44.489996659Z ==> Docs on specifying a port: https://render.com/docs/web-services#port-binding
2025-08-18T02:12:41.306109867Z INFO:     182.19.225.177:0 - "OPTIONS /api/users/me HTTP/1.1" 200 OK
2025-08-18T02:12:41.336858358Z INFO:     182.19.225.177:0 - "GET /api/users/me HTTP/1.1" 401 Unauthorized
2025-08-18T02:14:17.560868401Z ==> Deploying...
2025-08-18T02:14:38.680792766Z ==> Your service is live 🎉
2025-08-18T02:14:38.861514673Z ==> 
2025-08-18T02:14:39.03773895Z ==> ///////////////////////////////////////////////////////////
2025-08-18T02:14:39.214250688Z ==> 
2025-08-18T02:14:39.393929895Z ==> Available at your primary URL https://logiscorebe.onrender.com
2025-08-18T02:14:39.567625143Z ==> 
2025-08-18T02:14:39.744963181Z ==> ///////////////////////////////////////////////////////////
2025-08-18T02:14:40.170320839Z INFO:     35.197.118.178:0 - "GET / HTTP/1.1" 200 OK
2025-08-18T02:15:12.797373838Z INFO:     182.19.225.177:0 - "GET /api/locations/?page=1&page_size=1000 HTTP/1.1" 200 OK
2025-08-18T02:15:12.840782065Z INFO:     182.19.225.177:0 - "OPTIONS /api/reviews/questions HTTP/1.1" 200 OK
2025-08-18T02:15:12.883654Z INFO:     182.19.225.177:0 - "GET /api/reviews/questions HTTP/1.1" 200 OK
2025-08-18T02:15:22.665186621Z INFO:     182.19.225.177:0 - "OPTIONS /api/locations/?q=fran&page=1&page_size=1000 HTTP/1.1" 200 OK
2025-08-18T02:15:22.705098805Z INFO:routes.locations:GET /api/locations called with q=fran, page=1, page_size=1000, region=None, country=None
2025-08-18T02:15:22.705121676Z INFO:routes.locations:Database session: True
2025-08-18T02:15:22.705276569Z INFO:routes.locations:Original query: 'fran', Normalized: 'fran'
2025-08-18T02:15:23.341932132Z INFO:routes.locations:Returning 1000 locations from page 1 of 10 (total: 9418)
2025-08-18T02:15:23.359501952Z INFO:     182.19.225.177:0 - "OPTIONS /api/locations/?q=frank&page=1&page_size=1000 HTTP/1.1" 200 OK
2025-08-18T02:15:23.362146925Z INFO:     182.19.225.177:0 - "GET /api/locations/?q=fran&page=1&page_size=1000 HTTP/1.1" 200 OK
2025-08-18T02:15:23.38747376Z INFO:routes.locations:GET /api/locations called with q=frank, page=1, page_size=1000, region=None, country=None
2025-08-18T02:15:23.387503191Z INFO:routes.locations:Database session: True
2025-08-18T02:15:23.387516061Z INFO:routes.locations:Original query: 'frank', Normalized: 'frank'
2025-08-18T02:15:24.579092374Z INFO:routes.locations:Returning 154 locations from page 1 of 1 (total: 154)
2025-08-18T02:15:24.584766659Z INFO:     182.19.225.177:0 - "GET /api/locations/?q=frank&page=1&page_size=1000 HTTP/1.1" 200 OK
2025-08-18T02:15:38.331470664Z INFO:     Shutting down
2025-08-18T02:15:38.431958246Z INFO:     Waiting for application shutdown.
2025-08-18T02:15:38.432077669Z INFO:     Application shutdown complete.
2025-08-18T02:15:38.43217603Z INFO:     Finished server process [48]
2025-08-18T02:16:21.091724509Z INFO:     182.19.225.177:0 - "OPTIONS /api/reviews/ HTTP/1.1" 200 OK
2025-08-18T02:16:21.133484197Z INFO:routes.reviews:Validating location_id: 4901WRIO5033 (type: <class 'str'>)
2025-08-18T02:16:21.137636186Z INFO:routes.reviews:Location found: UUID=4901WRIO5033, Location=Alzenau in Unterfranken, Bavaria, Germany, City=Alzenau in Unterfranken, Country=Germany
2025-08-18T02:16:21.137657317Z INFO:routes.reviews:Creating review with data: freight_forwarder_id=7120060b-dd84-44eb-bdab-123f531641a3, city=Alzenau in Unterfranken, country=Germany
2025-08-18T02:16:21.137712828Z INFO:routes.reviews:Using city=Alzenau in Unterfranken, country=Germany from location, dummy branch_id=459eb5fa-1e1b-434a-b4b6-274e7d4dc249
2025-08-18T02:16:21.137894063Z INFO:routes.reviews:Review object created successfully: <database.models.Review object at 0x74eb3df705a0>
2025-08-18T02:16:21.151758944Z INFO:routes.reviews:Review added to session and flushed, ID: ded3cdea-3d74-4e45-9335-337b9bdc1074
2025-08-18T02:16:21.258251028Z INFO:routes.reviews:Category scores created successfully for review ded3cdea-3d74-4e45-9335-337b9bdc1074 with category and score fields set
2025-08-18T02:16:21.296489112Z INFO:routes.reviews:Review committed successfully: ded3cdea-3d74-4e45-9335-337b9bdc1074
2025-08-18T02:16:21.299649857Z INFO:     182.19.225.177:0 - "POST /api/reviews/ HTTP/1.1" 500 Internal Server Error
