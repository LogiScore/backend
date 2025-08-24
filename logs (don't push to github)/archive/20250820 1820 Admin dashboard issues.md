Admin dashboard issues

client:

API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/dashboard", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
API Error Response: 
Object { status: 500, statusText: "", errorText: `{"detail":"Failed to get recent activity: (psycopg2.errors.UndefinedColumn) column disputes.reason does not exist\\nLINE 1: ...id, disputes.reported_by AS disputes_reported_by, disputes.r...\\n                                                             ^\\n\\n[SQL: SELECT disputes.id AS disputes_id, disputes.review_id AS disputes_review_id, disputes.reported_by AS disputes_reported_by, disputes.reason AS disputes_reason, disputes.description AS disputes_description, disputes.status AS disputes_status, disputes.admin_notes AS disputes_admin_notes, disputes.resolved_at AS disputes_resolved_at, disputes.created_at AS disputes_created_at, disputes.updated_at AS disputes_updated_at \\nFROM disputes ORDER BY disputes.created_at DESC \\n LIMIT %(param_1)s]\\n[parameters: {'param_1': 10}]\\n(Background on this error at: https://sqlalche.me/e/20/f405)"}`, headers: {…} }
pqEgUiUM.js:1:463
Failed to get recent activity: Error: Server error. Please try again later.
    request Immutable
pqEgUiUM.js:1:28335
Failed to load recent activity: Error: Failed to load recent activity. Please try again later.
    getRecentActivity Immutable
3.mK6QSeLX.js:1:29225
API Error Response: 
Object { status: 500, statusText: "", errorText: `{"detail":"Failed to get dashboard stats: (psycopg2.errors.UndefinedColumn) column disputes.reason does not exist\\nLINE 2: ...id, disputes.reported_by AS disputes_reported_by, disputes.r...\\n                                                             ^\\n\\n[SQL: SELECT count(*) AS count_1 \\nFROM (SELECT disputes.id AS disputes_id, disputes.review_id AS disputes_review_id, disputes.reported_by AS disputes_reported_by, disputes.reason AS disputes_reason, disputes.description AS disputes_description, disputes.status AS disputes_status, disputes.admin_notes AS disputes_admin_notes, disputes.resolved_at AS disputes_resolved_at, disputes.created_at AS disputes_created_at, disputes.updated_at AS disputes_updated_at \\nFROM disputes \\nWHERE disputes.status = %(status_1)s) AS anon_1]\\n[parameters: {'status_1': 'open'}]\\n(Background on this error at: https://sqlalche.me/e/20/f405)"}`, headers: {…} }
pqEgUiUM.js:1:463
Failed to get dashboard stats: Error: Server error. Please try again later.
    request Immutable
pqEgUiUM.js:1:24440
Failed to load dashboard stats: Error: Failed to load dashboard statistics. Please try again later.
    getDashboardStats Immutable
3.mK6QSeLX.js:1:26575
Dashboard Error: Failed to load dashboard statistics. Please try again later. 3.mK6QSeLX.js:1:26795
Loading reviews data for admin user 3.mK6QSeLX.js:1:33906
Loading reviews with token: eyJhbGciOiJIUzI1NiIs... 3.mK6QSeLX.js:1:27443
API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/reviews?", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
Loading reviews with token: eyJhbGciOiJIUzI1NiIs... 3.mK6QSeLX.js:1:27443
API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/reviews?", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
API Error Response: 
Object { status: 500, statusText: "", errorText: `{"detail":"Failed to get reviews: 'Review' object has no attribute 'branch'"}`, headers: {…} }
pqEgUiUM.js:1:463
Failed to get reviews: Error: Server error. Please try again later.
    request Immutable
pqEgUiUM.js:1:25303
Failed to load reviews: Error: Failed to load reviews. Please try again later.
    getAdminReviews Immutable
3.mK6QSeLX.js:1:27577
API Error Response: 
Object { status: 500, statusText: "", errorText: `{"detail":"Failed to get reviews: 'Review' object has no attribute 'branch'"}`, headers: {…} }
pqEgUiUM.js:1:463
Failed to get reviews: Error: Server error. Please try again later.
    request Immutable
pqEgUiUM.js:1:25303
Failed to load reviews: Error: Failed to load reviews. Please try again later.
    getAdminReviews Immutable
3.mK6QSeLX.js:1:27577
Loading companies data for admin user 3.mK6QSeLX.js:1:34202
Loading companies with token: eyJhbGciOiJIUzI1NiIs... 3.mK6QSeLX.js:1:28389
API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/companies?", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
Loading companies with token: eyJhbGciOiJIUzI1NiIs... 3.mK6QSeLX.js:1:28389
API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/companies?", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
API Success Response: 
Object { status: 200, statusText: "", headers: {…} }
pqEgUiUM.js:1:1038
API Success Response: 
Object { status: 200, statusText: "", headers: {…} }
pqEgUiUM.js:1:1038
Loading users data for admin user 3.mK6QSeLX.js:1:33762
Loading users with token: eyJhbGciOiJIUzI1NiIs... 3.mK6QSeLX.js:1:26971
API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/users?", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
Loading users with token: eyJhbGciOiJIUzI1NiIs... 3.mK6QSeLX.js:1:26971
API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/users?", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
Loading users with token: eyJhbGciOiJIUzI1NiIs... 3.mK6QSeLX.js:1:26971
API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/users?", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
API Success Response: 
Object { status: 200, statusText: "", headers: {…} }
pqEgUiUM.js:1:1038
API Success Response: 
Object { status: 200, statusText: "", headers: {…} }
pqEgUiUM.js:1:1038
API Success Response: 
Object { status: 200, statusText: "", headers: {…} }
pqEgUiUM.js:1:1038
Loading analytics data for admin user 3.mK6QSeLX.js:1:34352
API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/analytics", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
API Success Response: 
Object { status: 200, statusText: "", headers: {…} }
pqEgUiUM.js:1:1038
Auto-refreshing dashboard data... 3.mK6QSeLX.js:1:24632
API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/analytics", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
API Success Response: 
Object { status: 200, statusText: "", headers: {…} }
pqEgUiUM.js:1:1038
Loading users data for admin user 3.mK6QSeLX.js:1:33762
Loading users with token: eyJhbGciOiJIUzI1NiIs... 3.mK6QSeLX.js:1:26971
API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/users?", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
Loading users with token: eyJhbGciOiJIUzI1NiIs... 3.mK6QSeLX.js:1:26971
API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/users?", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
Loading users with token: eyJhbGciOiJIUzI1NiIs... 3.mK6QSeLX.js:1:26971
API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/users?", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
API Success Response: 
Object { status: 200, statusText: "", headers: {…} }
pqEgUiUM.js:1:1038
API Success Response: 
Object { status: 200, statusText: "", headers: {…} }
pqEgUiUM.js:1:1038
API Success Response: 
Object { status: 200, statusText: "", headers: {…} }
pqEgUiUM.js:1:1038
Loading dashboard data for admin user 3.mK6QSeLX.js:1:33539
Testing authentication token... 3.mK6QSeLX.js:1:25285
Token length: 165 3.mK6QSeLX.js:1:25332
Token preview: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjM... 3.mK6QSeLX.js:1:25379
Loading recent activity with token: eyJhbGciOiJIUzI1NiIs... 3.mK6QSeLX.js:1:29084
Calling admin recent activity with token: eyJhbGciOiJIUzI1NiIs... pqEgUiUM.js:1:28143
API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/recent-activity", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
Auth test response status: 200 3.mK6QSeLX.js:1:25595
Auth test response headers: 
Object { "access-control-allow-credentials": "true", "access-control-allow-origin": "*", "access-control-expose-headers": "*", "alt-svc": 'h3=":443"; ma=86400', "cf-cache-status": "DYNAMIC", "cf-ray": "97212db4ace1cded-SIN", "content-encoding": "br", "content-length": "62", "content-type": "application/json", date: "Wed, 20 Aug 2025 10:24:00 GMT", … }
3.mK6QSeLX.js:1:25646
✅ Token is valid 3.mK6QSeLX.js:1:25735
Loading dashboard stats with valid token: eyJhbGciOiJIUzI1NiIs... 3.mK6QSeLX.js:1:26167
Calling admin dashboard with token: eyJhbGciOiJIUzI1NiIs... pqEgUiUM.js:1:24260
API Request: 
Object { url: "https://logiscorebe.onrender.com/admin/dashboard", method: "GET", headers: {…}, body: undefined }
pqEgUiUM.js:1:186
API Error Response: 
Object { status: 500, statusText: "", errorText: `{"detail":"Failed to get recent activity: (psycopg2.errors.UndefinedColumn) column disputes.reason does not exist\\nLINE 1: ...id, disputes.reported_by AS disputes_reported_by, disputes.r...\\n                                                             ^\\n\\n[SQL: SELECT disputes.id AS disputes_id, disputes.review_id AS disputes_review_id, disputes.reported_by AS disputes_reported_by, disputes.reason AS disputes_reason, disputes.description AS disputes_description, disputes.status AS disputes_status, disputes.admin_notes AS disputes_admin_notes, disputes.resolved_at AS disputes_resolved_at, disputes.created_at AS disputes_created_at, disputes.updated_at AS disputes_updated_at \\nFROM disputes ORDER BY disputes.created_at DESC \\n LIMIT %(param_1)s]\\n[parameters: {'param_1': 10}]\\n(Background on this error at: https://sqlalche.me/e/20/f405)"}`, headers: {…} }
pqEgUiUM.js:1:463
Failed to get recent activity: Error: Server error. Please try again later.
    request Immutable
pqEgUiUM.js:1:28335
Failed to load recent activity: Error: Failed to load recent activity. Please try again later.
    getRecentActivity Immutable
3.mK6QSeLX.js:1:29225
API Error Response: 
Object { status: 500, statusText: "", errorText: `{"detail":"Failed to get dashboard stats: (psycopg2.errors.UndefinedColumn) column disputes.reason does not exist\\nLINE 2: ...id, disputes.reported_by AS disputes_reported_by, disputes.r...\\n                                                             ^\\n\\n[SQL: SELECT count(*) AS count_1 \\nFROM (SELECT disputes.id AS disputes_id, disputes.review_id AS disputes_review_id, disputes.reported_by AS disputes_reported_by, disputes.reason AS disputes_reason, disputes.description AS disputes_description, disputes.status AS disputes_status, disputes.admin_notes AS disputes_admin_notes, disputes.resolved_at AS disputes_resolved_at, disputes.created_at AS disputes_created_at, disputes.updated_at AS disputes_updated_at \\nFROM disputes \\nWHERE disputes.status = %(status_1)s) AS anon_1]\\n[parameters: {'status_1': 'open'}]\\n(Background on this error at: https://sqlalche.me/e/20/f405)"}`, headers: {…} }
pqEgUiUM.js:1:463
Failed to get dashboard stats: Error: Server error. Please try again later.
    request Immutable
pqEgUiUM.js:1:24440
Failed to load dashboard stats: Error: Failed to load dashboard statistics. Please try again later.
    getDashboardStats Immutable
3.mK6QSeLX.js:1:26575
Dashboard Error: Failed to load dashboard statistics. Please try again later. 3.mK6QSeLX.js:1:26795

​Render

INFO:     203.116.163.124:0 - "GET /admin/dashboard HTTP/1.1" 500 Internal Server Error



