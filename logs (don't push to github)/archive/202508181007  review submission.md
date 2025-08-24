Client

[Log] Submitting review with data: – {freight_forwarder_id: "3e7beb0c-38f3-4f51-b16a-35dd369d431d", branch_id: "6f7b0c2d-0000-0000-0000-000000000000", selectedBranch: "6f7b0c2d-0000-0000-0000-000000000000", …} (12.Cz_wU8WQ.js, line 1)
{freight_forwarder_id: "3e7beb0c-38f3-4f51-b16a-35dd369d431d", branch_id: "6f7b0c2d-0000-0000-0000-000000000000", selectedBranch: "6f7b0c2d-0000-0000-0000-000000000000", selectedBranchDisplay: "Shanghai"}Object
[Log] Branch ID validation: – {branch_id: "6f7b0c2d-0000-0000-0000-000000000000", isUUID: true, length: 36} (12.Cz_wU8WQ.js, line 1)
[Log] Creating comprehensive review with data: – {freight_forwarder_id: "3e7beb0c-38f3-4f51-b16a-35dd369d431d", branch_id: "6f7b0c2d-0000-0000-0000-000000000000", is_anonymous: false, …} (gJt0NGzN.js, line 1)
{freight_forwarder_id: "3e7beb0c-38f3-4f51-b16a-35dd369d431d", branch_id: "6f7b0c2d-0000-0000-0000-000000000000", is_anonymous: false, review_weight: 1, category_ratings: Array, …}Object
[Log] Request endpoint: – "/api/reviews/" (gJt0NGzN.js, line 1)
[Log] Request method: – "POST" (gJt0NGzN.js, line 1)
[Log] Request headers: – {Authorization: "Bearer eyJhbGciOiJIUzI1NiIs...", Content-Type: "application/json"} (gJt0NGzN.js, line 1)
[Log] API Request: – {url: "https://logiscorebe.onrender.com/api/reviews/", method: "POST", headers: {Authorization: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdW…4OTl9.Iyw_QkyB-Zt_2T10yirTRmu6ySg9YvuEhUg-WS5CScY", Content-Type: "application/json"}, …} (gJt0NGzN.js, line 1)
{url: "https://logiscorebe.onrender.com/api/reviews/", method: "POST", headers: {Authorization: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdW…4OTl9.Iyw_QkyB-Zt_2T10yirTRmu6ySg9YvuEhUg-WS5CScY", Content-Type: "application/json"}, body: "{\"freight_forwarder_id\":\"3e7beb0c-38f3-4f51-b16a-3…regate_rating\":2.88125,\"weighted_rating\":2.88125}"}Object
[Error] Failed to load resource: the server responded with a status of 500 () (reviews, line 0)
[Log] API Error Response: – {status: 500, statusText: "", errorText: "{\"detail\":\"Failed to create review: (psycopg2.erro…n this error at: https://sqlalche.me/e/20/f405)\"}", …} (gJt0NGzN.js, line 1)
{status: 500, statusText: "", errorText: "{\"detail\":\"Failed to create review: (psycopg2.erro…n this error at: https://sqlalche.me/e/20/f405)\"}", headers: Object}Object
[Error] Failed to create comprehensive review: – Error: Server error. Please try again later. — gJt0NGzN.js:1:880
Error: Server error. Please try again later. — gJt0NGzN.js:1:880
	(anonymous function) (gJt0NGzN.js:1:4204)
[Error] Review submission failed: – Error: Server error. Please try again later. — gJt0NGzN.js:1:880
Error: Server error. Please try again later. — gJt0NGzN.js:1:880
	(anonymous function) (12.Cz_wU8WQ.js:1:18409)
[Error] Error details: – {message: "Server error. Please try again later.", status: undefined, response: undefined, …}
{message: "Server error. Please try again later.", status: undefined, response: undefined, data: Object}Object
	(anonymous function) (12.Cz_wU8WQ.js:1:19061)

vercel error

AUG 15 16:07:04.48
GET
404
logiscore.net
/.well-known/cf-custom-hostname-challenge/8eee4d5c-c483-4b58-8d73-8d5a7af01326
2
Not found: /.well-known/cf-custom-hostname-challenge/8eee4d5c-c483-4b58-8d73-8d5a7af01326
AUG 15 16:07:04.44
GET
404
logiscore.net
/.well-known/cf-custom-hostname-challenge/8eee4d5c-c483-4b58-8d73-8d5a7af01326
2
Not found: /.well-known/cf-custom-hostname-challenge/8eee4d5c-c483-4b58-8d73-8d5a7af01326
AUG 15 16:07:04.36
GET
404
logiscore.net
/.well-known/cf-custom-hostname-challenge/8eee4d5c-c483-4b58-8d73-8d5a7af01326
2
Not found: /.well-known/cf-custom-hostname-challenge/8eee4d5c-c483-4b58-8d73-8d5a7af01326
AUG 15 16:06:29.46
GET
200
logiscore.net
/search
Layout loaded with cache buster: { timestamp: 1755243114390, id: 'build-1755243114390', version: 'v1755243114', hash: 'hash-ulp6tpu9vsl', forceRebuild: true, noCache: true }
AUG 15 16:02:31.82
GET
404
logiscore.net
/favicon.ico
2
Not found: /favicon.ico
AUG 15 16:02:29.32
GET
200
logiscore.net
/
Layout loaded with cache buster: { timestamp: 1755243114390, id: 'build-1755243114390', version: 'v1755243114', hash: 'hash-ulp6tpu9vsl', forceRebuild: true, noCache: true }
AUG 15 16:02:27.43
GET
404
logiscore.net
/.well-known/cf-custom-hostname-challenge/cb2f6d2f-8f1b-410f-9ec8-12ffa2a5d165
2
Not found: /.well-known/cf-custom-hostname-challenge/cb2f6d2f-8f1b-410f-9ec8-12ffa2a5d165
AUG 15 16:02:26.83
GET
404
logiscore.net
/.well-known/cf-custom-hostname-challenge/cb2f6d2f-8f1b-410f-9ec8-12ffa2a5d165
2
Not found: /.well-known/cf-custom-hostname-challenge/cb2f6d2f-8f1b-410f-9ec8-12ffa2a5d165
AUG 15 16:02:02.22
GET
404
logiscore.net
/favicon.ico
2
Not found: /favicon.ico
AUG 15 16:02:01.30
GET
200
logiscore.net
/
Layout loaded with cache buster: { timestamp: 1755243114390, id: 'build-1755243114390', version: 'v1755243114', hash: 'hash-ulp6tpu9vsl', forceRebuild: true, noCache: true }
AUG 15 16:01:23.67
GET
200
logiscore.net
/
Layout loaded with cache buster: { timestamp: 1755243114390, id: 'build-1755243114390', version: 'v1755243114', hash: 'hash-ulp6tpu9vsl', forceRebuild: true, noCache: true }
AUG 15 16:01:23.13
GET
200
logiscore.net
/
Layout loaded with cache buster: { timestamp: 1755243114390, id: 'build-1755243114390', version: 'v1755243114', hash: 'hash-ulp6tpu9vsl', forceRebuild: true, noCache: true }
AUG 15 16:00:44.85
GET
404
logiscore.net
/.well-known/cf-custom-hostname-challenge/8eee4d5c-c483-4b58-8d73-8d5a7af01326
2
Not found: /.well-known/cf-custom-hostname-challenge/8eee4d5c-c483-4b58-8d73-8d5a7af01326

render

INFO:     182.19.225.177:0 - "OPTIONS /api/users/me HTTP/1.1" 200 OK
INFO:     182.19.225.177:0 - "GET /api/users/me HTTP/1.1" 200 OK
INFO:     182.19.225.177:0 - "OPTIONS /api/reviews/ HTTP/1.1" 200 OK
INFO:     182.19.225.177:0 - "POST /api/reviews/ HTTP/1.1" 500 Internal Server Error
INFO:     182.19.225.177:0 - "OPTIONS /api/users/me HTTP/1.1" 200 OK
INFO:     182.19.225.177:0 - "GET /api/users/me HTTP/1.1" 401 Unauthorized